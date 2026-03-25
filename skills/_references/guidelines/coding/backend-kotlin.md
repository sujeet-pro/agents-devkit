# Kotlin/JVM Backend Review Guidelines

These guidelines apply to **Kotlin backend** projects, covering Spring Boot and Ktor
applications. They supplement the general guidelines with Kotlin-specific rules for
building reliable, maintainable, and performant JVM backend services.

---

## 1. Coroutines and Structured Concurrency

- **Always use structured concurrency.** Every coroutine should be launched within a
  `CoroutineScope` that defines its lifetime. Never use `GlobalScope` in application code.
  ```kotlin
  // Good: scoped to the class lifecycle
  class OrderProcessor(private val scope: CoroutineScope) {
      fun processAsync(order: Order) = scope.launch {
          validate(order)
          charge(order)
          fulfill(order)
      }
  }

  // Bad: unscoped, no cancellation, no error propagation
  fun processAsync(order: Order) = GlobalScope.launch {
      // ...
  }
  ```
- **Understand cancellation.** Coroutines are cancellable by default. Use
  `ensureActive()` or check `isActive` in long-running loops. Wrap blocking calls
  with `withContext(Dispatchers.IO)` so cancellation remains responsive.
- **Use `supervisorScope`** when child failures should not cancel siblings. This is
  common in fan-out scenarios where independent tasks run in parallel:
  ```kotlin
  suspend fun processBatch(orders: List<Order>) = supervisorScope {
      orders.map { order ->
          async {
              try { process(order) }
              catch (e: Exception) { log.error("Failed: orderId={}", order.id, e) }
          }
      }.awaitAll()
  }
  ```
- **Use `flowOn` to shift dispatchers** for Flow producers. Never call `withContext`
  inside a `flow {}` builder; use `flowOn` at the collection site instead:
  ```kotlin
  // Good
  fun orders(): Flow<Order> = flow {
      repository.streamAll().collect { emit(it) }
  }.flowOn(Dispatchers.IO)

  // Bad: withContext inside flow builder violates Flow invariants
  fun orders(): Flow<Order> = flow {
      withContext(Dispatchers.IO) { /* ... */ }
  }
  ```
- **Prefer `Dispatchers.IO` for blocking I/O** (database calls, file reads, legacy
  blocking APIs). Use `Dispatchers.Default` for CPU-intensive computation. Never
  perform blocking calls on `Dispatchers.Main` or `Dispatchers.Unconfined`.
- **Exception handling**: Use `CoroutineExceptionHandler` at the scope level for
  fire-and-forget jobs launched with `launch`. For `async`, exceptions propagate
  through `await()` and should be caught at the call site.

> **Reference**: [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html),
> [Structured Concurrency](https://kotlinlang.org/docs/coroutines-basics.html#structured-concurrency)

## 2. Null Safety and Type System

- **Avoid platform types.** When calling Java code that lacks nullability annotations,
  explicitly declare the Kotlin type as nullable or non-nullable. Do not let the
  compiler infer platform types (`String!`):
  ```kotlin
  // Good: explicit about nullability from Java interop
  val name: String? = javaObject.getName()

  // Bad: platform type leaks into Kotlin code
  val name = javaObject.getName() // type is String! -- crash risk
  ```
- **Prefer sealed classes/interfaces for error modeling** over exceptions for expected
  failure modes. Reserve exceptions for truly exceptional situations:
  ```kotlin
  sealed interface PaymentResult {
      data class Success(val transactionId: String) : PaymentResult
      data class Declined(val reason: String) : PaymentResult
      data class NetworkError(val cause: Throwable) : PaymentResult
  }

  fun processPayment(order: Order): PaymentResult {
      // ...
  }
  ```
- **Use `require`, `check`, and `error`** for preconditions, state invariants, and
  unreachable code instead of throwing raw exceptions:
  ```kotlin
  fun withdraw(amount: BigDecimal) {
      require(amount > BigDecimal.ZERO) { "Amount must be positive: $amount" }
      check(balance >= amount) { "Insufficient balance: $balance < $amount" }
  }
  ```
- **Avoid `!!` (non-null assertion).** If you must use it, add a comment explaining
  why the value is guaranteed non-null. In most cases, use `?.let {}`,
  `?: return`, or `?: throw` with a descriptive message instead.
- **Use `value class`** (inline classes) for type-safe wrappers around primitives:
  ```kotlin
  @JvmInline
  value class OrderId(val value: Long)

  @JvmInline
  value class CustomerId(val value: Long)

  // Prevents accidentally passing a CustomerId where an OrderId is expected
  fun findOrder(id: OrderId): Order? = // ...
  ```

> **Reference**: [Kotlin Null Safety](https://kotlinlang.org/docs/null-safety.html),
> [Sealed Classes](https://kotlinlang.org/docs/sealed-classes.html)

## 3. Spring Boot with Kotlin

- **Use constructor injection** via Kotlin primary constructors. Spring automatically
  uses the primary constructor for injection:
  ```kotlin
  @Service
  class OrderService(
      private val orderRepo: OrderRepository,
      private val paymentGateway: PaymentGateway,
      private val clock: Clock,
  ) {
      // ...
  }
  ```
- **Use `@ConfigurationProperties` with data classes** for type-safe configuration.
  Requires `kotlin-kapt` or `kotlin-spring` plugin:
  ```kotlin
  @ConfigurationProperties(prefix = "app.payment")
  data class PaymentConfig(
      val apiUrl: String,
      val apiKey: String,
      val timeoutSeconds: Int = 10,
  )
  ```
- **WebFlux vs MVC decision**: Use Spring MVC with coroutines for most applications.
  This gives you a familiar programming model with non-blocking I/O when needed.
  Use WebFlux only when you need full reactive stream semantics (backpressure across
  network boundaries, complex stream transformations). Spring MVC supports
  `suspend fun` in controllers since Spring 6:
  ```kotlin
  @RestController
  @RequestMapping("/api/v1/orders")
  class OrderController(private val orderService: OrderService) {

      @GetMapping("/{id}")
      suspend fun getOrder(@PathVariable id: OrderId): OrderResponse {
          return orderService.findById(id)
              ?: throw ResponseStatusException(HttpStatus.NOT_FOUND)
      }
  }
  ```
- **Open classes for Spring proxies.** Apply the `kotlin-spring` (all-open) compiler
  plugin so that Spring can proxy `@Service`, `@Component`, `@Configuration`, and
  `@Transactional` classes without requiring `open` on every class.
- **Null-safe repository methods.** Use Kotlin return types to express nullability
  clearly in Spring Data repositories:
  ```kotlin
  interface OrderRepository : JpaRepository<Order, Long> {
      fun findByOrderId(orderId: OrderId): Order?  // nullable when not found
      fun findAllByStatus(status: OrderStatus): List<Order>  // empty list, not null
  }
  ```

> **Reference**: [Spring Framework Kotlin Support](https://docs.spring.io/spring-framework/reference/languages/kotlin.html),
> [Spring Boot Kotlin Guide](https://spring.io/guides/tutorials/spring-boot-kotlin)

## 4. Ktor

- **Use the routing DSL** for type-safe, readable route definitions:
  ```kotlin
  fun Application.configureRouting() {
      routing {
          route("/api/v1/orders") {
              get { call.respond(orderService.findAll()) }
              get("/{id}") {
                  val id = call.parameters["id"]?.toLongOrNull()
                      ?: return@get call.respond(HttpStatusCode.BadRequest)
                  val order = orderService.findById(OrderId(id))
                      ?: return@get call.respond(HttpStatusCode.NotFound)
                  call.respond(order)
              }
              post { /* ... */ }
          }
      }
  }
  ```
- **Use plugins for cross-cutting concerns**: authentication, content negotiation,
  CORS, rate limiting, compression, and logging should be installed as Ktor plugins,
  not implemented manually in routes.
- **Dependency injection**: Use Koin or Kodein for DI in Ktor applications. Prefer
  constructor injection in service classes. Keep the DI module declaration close to
  the application entry point:
  ```kotlin
  val appModule = module {
      single<OrderRepository> { PostgresOrderRepository(get()) }
      single { OrderService(get(), get()) }
  }

  fun main() {
      embeddedServer(Netty, port = 8080) {
          install(Koin) { modules(appModule) }
          configureRouting()
      }.start(wait = true)
  }
  ```
- **Status pages plugin** for consistent error handling:
  ```kotlin
  install(StatusPages) {
      exception<NotFoundException> { call, cause ->
          call.respond(HttpStatusCode.NotFound, ErrorResponse(cause.message))
      }
      exception<ValidationException> { call, cause ->
          call.respond(HttpStatusCode.BadRequest, ErrorResponse(cause.message))
      }
  }
  ```

> **Reference**: [Ktor Documentation](https://ktor.io/docs/welcome.html),
> [Koin for Ktor](https://insert-koin.io/docs/reference/koin-ktor/ktor)

## 5. Serialization

- **Prefer `kotlinx.serialization`** over Jackson for Kotlin-first projects. It
  is multiplatform, compile-time safe, and handles Kotlin types (data classes,
  sealed classes, value classes, default parameters) correctly out of the box:
  ```kotlin
  @Serializable
  data class OrderResponse(
      val id: Long,
      val status: OrderStatus,
      val items: List<OrderItem>,
      val createdAt: Instant,
  )

  @Serializable
  enum class OrderStatus { PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED }
  ```
- **When Jackson is required** (existing Spring Boot codebase, Java interop), use
  the `jackson-module-kotlin` module and register `KotlinModule()`. This handles
  data classes, default parameter values, and nullable types correctly.
- **Explicit serializers** for types not supported out of the box:
  ```kotlin
  @Serializable
  data class Event(
      val name: String,
      @Serializable(with = InstantSerializer::class)
      val timestamp: Instant,
  )
  ```
- **Do not expose internal models in API responses.** Use dedicated request/response
  DTOs annotated with `@Serializable`. Map between domain models and DTOs explicitly.

> **Reference**: [kotlinx.serialization Guide](https://github.com/Kotlin/kotlinx.serialization/blob/master/docs/serialization-guide.md),
> [Jackson Kotlin Module](https://github.com/FasterXML/jackson-module-kotlin)

## 6. Testing

- **MockK over Mockito** for Kotlin projects. MockK understands Kotlin features
  (coroutines, extension functions, top-level functions, value classes):
  ```kotlin
  @Test
  fun `placeOrder charges payment and persists order`() {
      val paymentGateway = mockk<PaymentGateway>()
      val orderRepo = mockk<OrderRepository>()

      coEvery { paymentGateway.charge(any()) } returns PaymentResult.Success("txn-123")
      coEvery { orderRepo.save(any()) } returnsArgument 0

      val service = OrderService(orderRepo, paymentGateway)
      runBlocking { service.placeOrder(testOrder) }

      coVerify(exactly = 1) { paymentGateway.charge(any()) }
      coVerify(exactly = 1) { orderRepo.save(match { it.status == CONFIRMED }) }
  }
  ```
- **Kotest for expressive assertions and property-based testing**:
  ```kotlin
  class OrderServiceTest : FunSpec({
      test("discount is never negative") {
          checkAll(Arb.positiveLong(), Arb.double(0.0, 1.0)) { price, rate ->
              calculateDiscount(price, rate) shouldBeGreaterThanOrEqual 0
          }
      }
  })
  ```
- **Testcontainers** for integration tests with real infrastructure (PostgreSQL,
  Redis, Kafka). Prefer Testcontainers over H2 or embedded alternatives:
  ```kotlin
  @Testcontainers
  @SpringBootTest
  class OrderRepositoryTest {
      companion object {
          @Container
          val postgres = PostgreSQLContainer("postgres:16-alpine")

          @DynamicPropertySource
          @JvmStatic
          fun properties(registry: DynamicPropertyRegistry) {
              registry.add("spring.datasource.url", postgres::getJdbcUrl)
              registry.add("spring.datasource.username", postgres::getUsername)
              registry.add("spring.datasource.password", postgres::getPassword)
          }
      }
  }
  ```
- **Use `runTest`** from `kotlinx-coroutines-test` for testing suspend functions.
  It provides virtual time control and fails on uncaught exceptions:
  ```kotlin
  @Test
  fun `timeout triggers fallback`() = runTest {
      val service = OrderService(slowGateway, repo, testScope = this)
      val result = service.placeOrderWithTimeout(testOrder, timeout = 1.seconds)
      result shouldBe is<PaymentResult.NetworkError>()
  }
  ```

> **Reference**: [MockK Documentation](https://mockk.io/),
> [Kotest Documentation](https://kotest.io/),
> [Testcontainers for Kotlin](https://www.testcontainers.org/quickstart/junit5_quickstart/)

## 7. Gradle Build Configuration

- **Use convention plugins** (`buildSrc` or included build) to share build
  configuration across subprojects. Do not copy-paste plugin blocks and dependency
  declarations:
  ```kotlin
  // buildSrc/src/main/kotlin/kotlin-service-conventions.gradle.kts
  plugins {
      kotlin("jvm")
      kotlin("plugin.spring")
      kotlin("plugin.serialization")
      id("org.springframework.boot")
  }

  dependencies {
      implementation(platform("org.springframework.boot:spring-boot-dependencies:3.3.0"))
  }

  kotlin {
      jvmToolchain(21)
  }
  ```
- **Use version catalogs** (`libs.versions.toml`) for centralized dependency version
  management:
  ```toml
  [versions]
  kotlin = "2.0.0"
  spring-boot = "3.3.0"
  ktor = "2.3.12"
  kotest = "5.9.0"
  mockk = "1.13.11"

  [libraries]
  spring-boot-starter-web = { module = "org.springframework.boot:spring-boot-starter-web" }
  ktor-server-core = { module = "io.ktor:ktor-server-core", version.ref = "ktor" }
  kotest-runner = { module = "io.kotest:kotest-runner-junit5", version.ref = "kotest" }
  mockk = { module = "io.mockk:mockk", version.ref = "mockk" }
  ```
- **Kotlin compiler options**: Enable strict mode flags for better safety:
  ```kotlin
  kotlin {
      compilerOptions {
          allWarningsAsErrors = true
          freeCompilerArgs.addAll("-Xjsr305=strict")  // strict Java nullability
      }
  }
  ```
- **Use `kotlin-spring` and `kotlin-jpa` compiler plugins** when using Spring Boot
  with JPA. These open the necessary classes for proxying and generate no-arg
  constructors for entities.

> **Reference**: [Gradle Kotlin DSL](https://docs.gradle.org/current/userguide/kotlin_dsl.html),
> [Version Catalogs](https://docs.gradle.org/current/userguide/platforms.html#sub:version-catalog)

## 8. Kotlin Idioms and Code Style

- **Use data classes** for value objects and DTOs. They provide `equals`, `hashCode`,
  `toString`, `copy`, and destructuring automatically.
- **Use `when` exhaustively** on sealed types. The compiler enforces that all cases
  are handled:
  ```kotlin
  fun handle(result: PaymentResult): HttpResponse = when (result) {
      is PaymentResult.Success -> HttpResponse.ok(result.transactionId)
      is PaymentResult.Declined -> HttpResponse.unprocessable(result.reason)
      is PaymentResult.NetworkError -> HttpResponse.serviceUnavailable()
      // No else needed -- compiler enforces exhaustiveness
  }
  ```
- **Extension functions** for domain-specific operations. They improve readability
  without inheritance:
  ```kotlin
  fun Order.isOverdue(clock: Clock): Boolean =
      status == OrderStatus.PENDING && createdAt.isBefore(clock.instant().minus(24.hours))
  ```
- **Scope functions**: Use `let` for null-safe chaining, `apply` for object
  configuration, `also` for side effects, `run`/`with` for scoped computation.
  Do not chain more than two scope functions -- it becomes unreadable.
- **Prefer immutable data.** Use `val` over `var`, `List` over `MutableList`,
  `Map` over `MutableMap`. Mutability should be local to a function, never exposed
  in public APIs.
- **Avoid `lateinit`** for production code outside of framework-mandated injection
  points. Use lazy initialization or nullable types with explicit initialization.

> **Reference**: [Kotlin Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html),
> [Kotlin Idioms](https://kotlinlang.org/docs/idioms.html)
