# Testing Review Guidelines

These guidelines apply to **testing practices** across all languages and frameworks.
They supplement the general guidelines with rules for building a reliable, fast,
and maintainable test suite that gives genuine confidence in production readiness.

---

## 1. Test Pyramid

- **Maintain a healthy test ratio**: many unit tests, fewer integration tests,
  fewest end-to-end tests. The exact ratio depends on the system, but a common
  starting point is:
  - **Unit tests**: ~70% of your test suite. Fast, isolated, high coverage.
  - **Integration tests**: ~20%. Test boundaries between components.
  - **End-to-end tests**: ~10%. Validate critical user journeys.
- **If your pyramid is inverted** (more E2E than unit tests), the suite will be
  slow, flaky, and expensive to maintain. Identify logic that can be tested in
  isolation and push it down the pyramid.
- **Do not treat the pyramid as dogma.** Some systems (e.g., a thin API layer over
  a database) benefit from more integration tests than unit tests. Let the
  architecture guide the ratio.

> **Reference**: [Martin Fowler -- Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html),
> [Google Testing Blog -- Test Sizes](https://testing.googleblog.com/2010/12/test-sizes.html)

## 2. Unit Tests

- **Isolate the unit under test.** A unit test should exercise a single function,
  method, or class with all external dependencies replaced by test doubles.
- **Test behavior, not implementation.** Verify what the code *does*, not how it
  does it. If you refactor the implementation and the behavior is unchanged, tests
  should still pass:
  ```typescript
  // Good: tests observable behavior
  test("calculateTotal applies 10% discount for orders over $100", () => {
      const order = createOrder({ items: [{ price: 120, quantity: 1 }] });
      expect(calculateTotal(order)).toBe(108);
  });

  // Bad: tests implementation details
  test("calculateTotal calls applyDiscount when subtotal > 100", () => {
      const spy = jest.spyOn(discountModule, "applyDiscount");
      calculateTotal(createOrder({ items: [{ price: 120, quantity: 1 }] }));
      expect(spy).toHaveBeenCalledWith(120, 0.1);
  });
  ```
- **Unit tests must be fast.** A single unit test should complete in milliseconds.
  If a unit test takes seconds, it is doing I/O or loading a framework context and
  should be reclassified as an integration test.
- **One assertion per logical concept.** Multiple `expect`/`assert` calls are fine
  if they verify different aspects of the same behavior. Avoid testing unrelated
  behaviors in a single test case.
- **Edge cases to always test**: null/undefined/empty input, boundary values (0, 1,
  max), type coercion surprises, error paths, and concurrent access when applicable.

> **Reference**: [Jest Documentation](https://jestjs.io/docs/getting-started),
> [pytest Documentation](https://docs.pytest.org/)

## 3. Integration Tests

- **Test at system boundaries.** Integration tests verify that your code works
  correctly with real external systems: databases, message queues, caches,
  file systems, and HTTP APIs.
- **Use Testcontainers** for database and infrastructure tests. Testcontainers
  spins up real instances in Docker, giving you high-fidelity tests without
  environment-specific setup:
  ```typescript
  // TypeScript with Testcontainers
  import { PostgreSqlContainer } from "@testcontainers/postgresql";

  let container: StartedPostgreSqlContainer;

  beforeAll(async () => {
      container = await new PostgreSqlContainer("postgres:16-alpine").start();
      db = createPool(container.getConnectionUri());
      await runMigrations(db);
  }, 60_000);
  ```
  ```java
  // Java with Testcontainers
  @Container
  static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");
  ```
  ```python
  # Python with testcontainers
  @pytest.fixture(scope="session")
  def postgres():
      with PostgresContainer("postgres:16-alpine") as pg:
          yield pg
  ```
- **Avoid in-memory substitutes** (H2 for PostgreSQL, embedded Redis) for
  integration tests. They have behavioral differences that mask real bugs.
- **Clean up test data** between tests. Use transaction rollback, truncation, or
  per-test database schemas to ensure test isolation.
- **External HTTP APIs**: Use WireMock, MSW (Mock Service Worker), or `nock` to
  simulate third-party API responses. Record real responses for initial setup, then
  maintain the recordings as fixtures.

> **Reference**: [Testcontainers](https://testcontainers.com/),
> [WireMock](https://wiremock.org/),
> [Mock Service Worker](https://mswjs.io/)

## 4. End-to-End Tests

- **Test critical user journeys**, not every permutation. E2E tests should cover
  the paths that generate revenue, prevent data loss, or have legal/compliance
  implications:
  - User registration and login
  - Core purchase/checkout flow
  - Payment processing
  - Data export
- **Minimize E2E test count.** Each E2E test is expensive to write, slow to run,
  and prone to flakiness. If a scenario can be covered by a lower-level test,
  test it there instead.
- **Avoid flakiness**:
  - Wait for elements/conditions explicitly, not with `sleep()`.
  - Use data-testid attributes for selectors, not CSS classes or text content.
  - Isolate test data (each test creates its own users, orders, etc.).
  - Retry flaky assertions with a bounded timeout.
  - Run E2E tests against a stable, dedicated environment.
- **Run E2E tests in CI** on every merge to the main branch. Run them on PRs only
  if they complete in under 10 minutes; otherwise run on a schedule.
- **Visual regression testing**: For UI applications, use screenshot comparison
  tools (Playwright snapshots, Percy, Chromatic) to catch unintended visual changes.

> **Reference**: [Playwright Documentation](https://playwright.dev/docs/intro),
> [Cypress Best Practices](https://docs.cypress.io/guides/references/best-practices),
> [Testing Library](https://testing-library.com/)

## 5. Mocking Strategy

- **Mock at system boundaries**, not within the system. Mock the database client,
  the HTTP client, the message queue producer. Do not mock internal classes or
  utility functions.
- **Prefer fakes over mocks** when feasible. A fake is a working in-memory
  implementation that behaves like the real thing:
  ```typescript
  // Fake: working in-memory implementation
  class InMemoryOrderRepository implements OrderRepository {
      private orders = new Map<string, Order>();

      async save(order: Order): Promise<Order> {
          this.orders.set(order.id, order);
          return order;
      }

      async findById(id: string): Promise<Order | null> {
          return this.orders.get(id) ?? null;
      }
  }

  // Mock: behavior specification (more brittle)
  const orderRepo = mock<OrderRepository>();
  when(orderRepo.save(any())).thenResolve(expectedOrder);
  ```
- **Avoid over-mocking.** If a test requires more than 3 mocks, it is a signal
  that the code under test has too many dependencies or the test is at the wrong
  level of the pyramid.
- **Verify interactions sparingly.** Check that a side effect occurred (email sent,
  event published) but do not verify the exact sequence of every internal method
  call. Over-verification makes tests brittle.
- **Reset mocks between tests.** Shared mock state across tests causes order-
  dependent failures that are painful to debug.

> **Reference**: [Martin Fowler -- Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html),
> [Testing Library Guiding Principles](https://testing-library.com/docs/guiding-principles)

## 6. Property-Based Testing

- **Use property-based testing for code with mathematical or structural properties**:
  serialization round-trips, parser/formatter pairs, sorting, encoding/decoding,
  and data transformations:
  ```typescript
  // fast-check (TypeScript)
  import fc from "fast-check";

  test("JSON serialize/deserialize round-trip", () => {
      fc.assert(fc.property(fc.object(), (obj) => {
          expect(JSON.parse(JSON.stringify(obj))).toEqual(obj);
      }));
  });
  ```
  ```python
  # Hypothesis (Python)
  from hypothesis import given
  from hypothesis import strategies as st

  @given(st.lists(st.integers()))
  def test_sort_is_idempotent(xs):
      assert sorted(sorted(xs)) == sorted(xs)
  ```
  ```kotlin
  // Kotest (Kotlin)
  checkAll(Arb.string()) { s ->
      decode(encode(s)) shouldBe s
  }
  ```
- **Define properties, not examples.** Instead of testing specific inputs and
  outputs, describe invariants that hold for all valid inputs:
  - Round-trip: `decode(encode(x)) == x`
  - Idempotency: `f(f(x)) == f(x)`
  - Monotonicity: `if x <= y then f(x) <= f(y)`
  - Preservation: `length(sort(xs)) == length(xs)`
- **Start with a small number of iterations** (100) during development and increase
  for CI (1000+). Configure a fixed seed for reproducibility.
- **Shrinking**: Property-based testing frameworks automatically shrink failing
  inputs to the minimal reproducing case. Use this to your advantage in bug reports.

> **Reference**: [fast-check Documentation](https://fast-check.dev/),
> [Hypothesis Documentation](https://hypothesis.readthedocs.io/),
> [Kotest Property Testing](https://kotest.io/docs/proptest/property-based-testing.html)

## 7. Test Data Management

- **Use factories (builders) over fixtures.** Factories create test data
  programmatically with sensible defaults and allow overriding only the fields
  relevant to the test:
  ```typescript
  // Factory with defaults
  function createOrder(overrides: Partial<Order> = {}): Order {
      return {
          id: randomUUID(),
          status: "pending",
          customerId: "customer-1",
          items: [{ productId: "product-1", quantity: 1, price: 10 }],
          createdAt: new Date(),
          ...overrides,
      };
  }

  // Usage: only specify what matters for this test
  const overdueOrder = createOrder({
      status: "pending",
      createdAt: daysAgo(30),
  });
  ```
- **Builder pattern** for complex objects with many interdependent fields:
  ```java
  Order order = new OrderBuilder()
      .withCustomer(testCustomer)
      .withItem("SKU-001", 2, Money.of(25, "USD"))
      .withItem("SKU-002", 1, Money.of(50, "USD"))
      .withDiscount(Discount.percentage(10))
      .build();
  ```
- **Avoid shared mutable test state.** Each test should create its own data. Shared
  fixtures lead to order-dependent tests and make it impossible to run tests in
  parallel.
- **Do not use production data in tests.** Generate synthetic data that covers
  your edge cases. Production data introduces privacy risks and unpredictable
  test behavior.

> **Reference**: [Factory Bot (Ruby)](https://github.com/thoughtbot/factory_bot),
> [Fishery (TypeScript)](https://github.com/thoughtbot/fishery)

## 8. Test Naming

- **Describe what happens under what conditions**, not what method you are calling:
  ```
  # Good
  "returns empty list when no orders match the filter"
  "rejects payment when card is expired"
  "sends notification email after order is confirmed"

  # Bad
  "test getOrders"
  "test processPayment error"
  "test sendEmail"
  ```
- **Use a consistent pattern** across the codebase. Common patterns:
  - `[action] [condition] [expected result]`: "placeOrder with insufficient inventory throws InsufficientInventoryException"
  - `should [behavior] when [condition]`: "should return 404 when order does not exist"
  - `given [context] when [action] then [result]`: Gherkin-style for BDD
- **Test names are documentation.** A developer reading the test file should
  understand the full behavior of the module without reading the implementation.

## 9. Code Coverage

- **Use 80% line coverage as a guideline, not a goal.** Coverage measures which
  lines were executed, not whether the logic is correct. 100% coverage with bad
  assertions is worse than 60% coverage with thorough assertions.
- **Focus coverage efforts on**:
  - Business logic and domain rules (aim for 90%+)
  - Error handling paths
  - Edge cases and boundary conditions
- **Do not measure coverage on**:
  - Generated code, type definitions, and configuration
  - Framework boilerplate (DI modules, route registration)
  - Trivial getters/setters and data classes
- **Enforce coverage in CI** as a gate on PRs. Do not let coverage decrease on
  changed files. Use tools that report coverage diff, not just absolute numbers.
- **Branch coverage** is more meaningful than line coverage. A line can be "covered"
  by the happy path while error branches are never tested.
- **Beware of coverage gaming.** Tests that execute code without asserting anything
  inflate coverage numbers while providing zero confidence. Every test must include
  meaningful assertions.

> **Reference**: [Istanbul/nyc](https://istanbul.js.org/),
> [JaCoCo](https://www.jacoco.org/jacoco/),
> [Coverage.py](https://coverage.readthedocs.io/)

## 10. Test Performance

- **Unit tests should complete in under 10 seconds** for the entire suite in a
  typical module. If they take longer, look for I/O, framework context loading,
  or excessive setup.
- **Parallelize tests** where possible. Most test runners support parallel execution.
  Ensure tests are independent (no shared mutable state) so they can run in any
  order.
- **Use test sharding** in CI for large suites. Split tests across multiple CI
  jobs to keep the total pipeline time under a target (e.g., 10 minutes).
- **Profile slow tests.** Most test runners can report test duration. Investigate
  any test that takes more than 1 second -- it is either doing too much or has a
  performance issue worth fixing.
- **Separate fast and slow tests.** Tag integration and E2E tests so developers can
  run only unit tests locally for fast feedback, while CI runs the full suite.
