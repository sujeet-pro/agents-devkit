# Java Backend Review Guidelines

These guidelines apply to **Java backend** projects, with a focus on Spring Boot
applications. They supplement the general guidelines with Java-specific rules for
enterprise application development.

---

## 1. Spring Boot Patterns

- **Use constructor injection** over field injection. Field injection (`@Autowired`
  on fields) hides dependencies, prevents immutability, and makes testing harder.
  ```java
  // Good
  @Service
  public class OrderService {
      private final OrderRepository orderRepo;
      private final PaymentGateway paymentGateway;

      public OrderService(OrderRepository orderRepo, PaymentGateway paymentGateway) {
          this.orderRepo = orderRepo;
          this.paymentGateway = paymentGateway;
      }
  }

  // Bad
  @Service
  public class OrderService {
      @Autowired
      private OrderRepository orderRepo;
  }
  ```
- **Use `@ConfigurationProperties`** for application configuration instead of
  scattered `@Value` annotations. This provides type safety, validation, and
  documentation.
- **Profiles**: Use Spring profiles (`@Profile`, `application-{profile}.yml`) for
  environment-specific configuration. Do not use `if (env == "prod")` checks in
  application code.
- **Bean scoping**: Default singleton scope is correct for most services. Use
  `@Scope("prototype")` only when each injection site needs a new instance. Never
  use `@Scope("request")` or `@Scope("session")` without understanding the
  implications for thread safety.
- **Auto-configuration**: When creating shared libraries, use Spring Boot
  auto-configuration (`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`)
  so consumers get beans registered automatically.
- **Avoid `@PostConstruct` for complex logic.** Use `ApplicationRunner` or
  `CommandLineRunner` for startup tasks that depend on the full application context.
- **Circular dependencies** are a design smell. If Spring reports a circular
  dependency, refactor the code to break the cycle. Do not use `@Lazy` as a
  workaround without understanding the root cause.

## 2. Exception Handling

- **Use a global exception handler** (`@RestControllerAdvice` + `@ExceptionHandler`)
  to convert exceptions into consistent HTTP error responses. Do not handle
  exceptions individually in every controller method.
  ```java
  @RestControllerAdvice
  public class GlobalExceptionHandler {
      @ExceptionHandler(EntityNotFoundException.class)
      public ResponseEntity<ErrorResponse> handleNotFound(EntityNotFoundException ex) {
          return ResponseEntity.status(404)
              .body(new ErrorResponse("NOT_FOUND", ex.getMessage()));
      }
  }
  ```
- **Define domain-specific exceptions.** Create exception classes for each error
  category (e.g., `OrderNotFoundException`, `InsufficientInventoryException`,
  `PaymentDeclinedException`). Do not throw raw `RuntimeException` or
  `IllegalStateException` for business logic errors.
- **Exception hierarchy**: Organize exceptions into a hierarchy:
  - `BusinessException` (base for recoverable business errors)
  - `TechnicalException` (base for infrastructure/system errors)
  - Specific exceptions extend the appropriate base
- **Never catch `Exception` or `Throwable`** except at the outermost boundary
  (global handler, scheduled task runner). Catch specific exception types.
- **Include context in exceptions.** The exception message should contain enough
  information to identify what went wrong without looking at logs:
  ```java
  throw new OrderNotFoundException(
      "Order not found: orderId=" + orderId + ", customerId=" + customerId
  );
  ```
- **Do not use exceptions for control flow.** Throwing and catching exceptions is
  expensive. For expected cases (e.g., "user not found" in a lookup), return
  `Optional<T>` or a result type.

## 3. Logging Best Practices

- **Use SLF4J** as the logging facade. Do not use `System.out.println()`,
  `java.util.logging`, or direct Log4j/Logback calls.
- **Log levels**:
  - `ERROR`: Something broke and requires immediate attention (failed payment,
    data corruption, unrecoverable state)
  - `WARN`: Something unexpected happened but the system handled it (retry
    succeeded, fallback triggered, deprecated API used)
  - `INFO`: Significant business events (order placed, user registered, job
    completed)
  - `DEBUG`: Detailed technical information for troubleshooting (method entry/exit,
    intermediate values, SQL queries)
  - `TRACE`: Extremely detailed debugging (raw payloads, protocol-level data)
- **Structured logging**: Use key-value pairs for machine-parseable logs:
  ```java
  log.info("Order placed: orderId={}, customerId={}, total={}",
      order.getId(), order.getCustomerId(), order.getTotal());
  ```
- **No sensitive data in logs.** Never log passwords, tokens, credit card numbers,
  SSNs, or full request/response bodies that may contain PII. Mask or redact.
- **Correlation IDs**: Include a request/correlation ID in all log entries for a
  given request. Use MDC (Mapped Diagnostic Context) for this.
- **Do not use string concatenation in log calls.** Use parameterized messages to
  avoid the cost of string building when the log level is disabled:
  ```java
  // Good
  log.debug("Processing item: id={}", item.getId());
  // Bad
  log.debug("Processing item: id=" + item.getId());
  ```

## 4. API Design (REST)

- **Use proper HTTP methods**: GET for reads, POST for creation, PUT for full
  replacement, PATCH for partial update, DELETE for removal. Do not use POST for
  everything.
- **Resource naming**: Use nouns, not verbs. Use plural forms.
  - Good: `GET /api/v1/orders`, `POST /api/v1/orders`
  - Bad: `GET /api/v1/getOrders`, `POST /api/v1/createOrder`
- **API versioning**: Version APIs in the URL path (`/api/v1/`, `/api/v2/`).
  Maintain backward compatibility within a version.
- **HTTP status codes**:
  - `200` OK (successful GET, PUT, PATCH)
  - `201` Created (successful POST that creates a resource)
  - `204` No Content (successful DELETE)
  - `400` Bad Request (validation failure)
  - `401` Unauthorized (missing/invalid authentication)
  - `403` Forbidden (authenticated but not authorized)
  - `404` Not Found
  - `409` Conflict (duplicate resource, concurrent modification)
  - `422` Unprocessable Entity (semantic validation failure)
  - `500` Internal Server Error (unexpected server failure)
- **Request validation**: Use Bean Validation annotations (`@NotNull`, `@Size`,
  `@Pattern`, `@Valid`) on request DTOs. Return structured validation errors:
  ```json
  {
    "error": "VALIDATION_FAILED",
    "details": [
      { "field": "email", "message": "must be a valid email address" },
      { "field": "name", "message": "must not be blank" }
    ]
  }
  ```
- **Pagination**: All list endpoints must support pagination. Use page/size or
  cursor-based pagination. Return total count and next/previous links.
- **DTOs**: Use dedicated request/response DTOs. Never expose JPA entities directly
  in API responses (this leaks internal database structure and creates N+1 queries).

## 5. Database Access Patterns

- **Use Spring Data JPA repositories** for standard CRUD. Use custom repository
  implementations for complex queries.
- **N+1 queries**: Watch for lazy-loaded collections accessed in loops. Use
  `@EntityGraph`, `JOIN FETCH`, or `@BatchSize` to prevent N+1.
  ```java
  // Bad: triggers N+1 when iterating orders and accessing items
  List<Order> orders = orderRepo.findAll();
  orders.forEach(o -> o.getItems().size()); // N additional queries!

  // Good: eager fetch in the query
  @Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.status = :status")
  List<Order> findByStatusWithItems(@Param("status") OrderStatus status);
  ```
- **Transactions**:
  - Use `@Transactional` on service methods, not on repository or controller methods
  - Use `@Transactional(readOnly = true)` for read-only operations (enables DB
    optimizations)
  - Keep transactions short -- do not perform external API calls, file I/O, or
    heavy computation inside a transaction
  - Understand transaction propagation (`REQUIRED`, `REQUIRES_NEW`,
    `NOT_SUPPORTED`) and use them intentionally
- **Migration management**: Use Flyway or Liquibase for database schema changes.
  Never modify the database schema manually or via JPA `ddl-auto` in production.
- **Indexes**: When adding new queries, verify that appropriate database indexes
  exist. A missing index on a frequently queried column causes full table scans.
- **Optimistic locking**: Use `@Version` for entities that may be updated
  concurrently. Handle `OptimisticLockException` gracefully (retry or inform user).

## 6. Security

- **Authentication**: Use Spring Security with a standard mechanism (JWT, OAuth2,
  session). Do not implement custom authentication.
- **Authorization**: Use method-level security (`@PreAuthorize`,
  `@RolesAllowed`) or URL-based security in `SecurityFilterChain`. Verify that
  every endpoint has appropriate authorization.
- **CORS**: Configure CORS explicitly in `SecurityFilterChain`. Do not use
  `@CrossOrigin("*")` on individual controllers.
- **Input sanitization**: Even with Bean Validation, sanitize inputs that will be
  used in SQL queries (use parameterized queries), HTML output (escape), or system
  commands (avoid; use structured APIs).
- **Dependency vulnerabilities**: Run `mvn dependency:check` or OWASP Dependency
  Check in CI. Flag PRs that introduce dependencies with known CVEs.
- **Secrets management**: Use environment variables, Spring Cloud Config, AWS
  Secrets Manager, or HashiCorp Vault. Never hardcode secrets in
  `application.properties`.
- **Rate limiting**: Protect public-facing APIs with rate limiting (Resilience4j,
  Spring Cloud Gateway, or API gateway).
- **Audit logging**: Log security-relevant events (login, logout, permission
  changes, data access) to a dedicated audit log.

## 7. Testing

- **Unit tests** (JUnit 5 + Mockito):
  - Test service layer business logic with mocked dependencies
  - Test utility/helper methods directly
  - Aim for >80% line coverage on service classes
- **Integration tests** (`@SpringBootTest`, `@DataJpaTest`, `@WebMvcTest`):
  - Test repository queries against a real database (H2 or Testcontainers)
  - Test controller request handling with `MockMvc` or `WebTestClient`
  - Test security configuration (authorized/unauthorized access)
  - Test external service integration with WireMock or similar
- **Test naming**: Use descriptive names that document behavior:
  ```java
  @Test
  void placeOrder_withInsufficientInventory_throwsInsufficientInventoryException()
  ```
- **Test data**: Use test fixtures or builders (e.g., `OrderBuilder`) to create
  test data. Do not use production data in tests. Do not share mutable state
  between tests.
- **No `@SpringBootTest` for unit tests.** Loading the full application context is
  slow and unnecessary for testing a single class. Use `@ExtendWith(MockitoExtension.class)`.
- **Testcontainers** for integration tests that need a real database, message queue,
  or cache. Prefer Testcontainers over H2 for database tests because H2 has
  behavioral differences from PostgreSQL/MySQL.

## 8. Concurrency

- **Spring beans are singletons by default**, meaning they are shared across all
  request threads. Do not store request-scoped state in instance fields.
  ```java
  // DANGEROUS: shared mutable state
  @Service
  public class OrderService {
      private Order currentOrder; // accessed by multiple threads!
  }
  ```
- **Use thread-safe data structures** when sharing data (`ConcurrentHashMap`,
  `CopyOnWriteArrayList`, `AtomicReference`).
- **`@Async`**: Use `@Async` with a configured `TaskExecutor` for background tasks.
  Do not use raw `Thread` or `ExecutorService` in Spring applications.
- **`@Scheduled`**: For scheduled tasks, ensure they are idempotent and handle
  overlapping executions (use `@SchedulerLock` or similar).
- **CompletableFuture**: Use `CompletableFuture` for asynchronous orchestration.
  Always handle exceptions with `exceptionally()` or `handle()`.
- **Virtual threads** (Java 21+): If using Project Loom virtual threads, avoid
  `synchronized` blocks and `ThreadLocal` in I/O-heavy code paths.

## 9. Memory Management

- **Avoid holding large collections in memory.** Use streaming/pagination for large
  datasets:
  ```java
  // Good: streaming
  @Query("SELECT o FROM Order o WHERE o.status = :status")
  Stream<Order> streamByStatus(@Param("status") OrderStatus status);

  // Bad: loading everything
  List<Order> findByStatus(OrderStatus status); // what if there are 1M orders?
  ```
- **Close resources**: Use try-with-resources for `InputStream`, `Connection`,
  `ResultSet`, `EntityManager`, and any `AutoCloseable`.
- **Beware of `@Cacheable` without eviction.** Cached data grows indefinitely
  unless you configure a maximum size and TTL.
- **String handling**: For building large strings in loops, use `StringBuilder` or
  `StringJoiner`, not string concatenation.
- **Pagination for batch processing**: When processing large datasets, use
  paginated queries with a fixed batch size rather than loading everything at once.

## 10. Configuration Management

- **Externalize all configuration.** No hardcoded URLs, timeouts, feature flags,
  or magic numbers. Use `application.yml` / `application.properties` with
  `@ConfigurationProperties`.
- **Configuration validation**: Use `@Validated` on `@ConfigurationProperties`
  classes to fail fast on startup if required values are missing.
  ```java
  @Validated
  @ConfigurationProperties(prefix = "app.payment")
  public record PaymentConfig(
      @NotBlank String apiUrl,
      @NotBlank String apiKey,
      @Min(1) @Max(30) int timeoutSeconds
  ) {}
  ```
- **Profiles for environment-specific config**: Use
  `application-dev.yml`, `application-staging.yml`, `application-prod.yml`.
  The base `application.yml` should contain defaults.
- **Feature flags**: Use a feature flag system (LaunchDarkly, Unleash, or a simple
  config-based system) for gradual rollouts. Do not use environment checks
  (`if (isProd)`) to toggle features.
- **Timeouts**: Every external call (HTTP, database, cache) must have explicit
  timeouts configured. Default timeouts are often too generous (30+ seconds).
  Configure connection timeout, read timeout, and overall timeout separately.
- **Health checks**: Use Spring Boot Actuator health endpoints. Add custom health
  indicators for critical dependencies (database, cache, external APIs).
