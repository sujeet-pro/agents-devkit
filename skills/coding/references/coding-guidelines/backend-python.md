# Python Backend Review Guidelines

These guidelines apply to **Python backend** projects, covering FastAPI, Django,
and Flask applications. They supplement the general guidelines with Python-specific
rules for building reliable, maintainable, and performant backend services.

---

## 1. Type Hints

- **Use type hints on all function signatures.** Every function should have type
  annotations for all parameters and the return type.
  ```python
  # Good
  def get_user(user_id: int) -> User | None:
      ...

  # Bad
  def get_user(user_id):
      ...
  ```
- **Use modern syntax** (Python 3.10+): `int | None` instead of `Optional[int]`,
  `list[str]` instead of `List[str]`, `dict[str, int]` instead of `Dict[str, int]`.
  For older Python support, use `from __future__ import annotations`.
- **TypedDict for dictionaries with known shapes**:
  ```python
  class UserResponse(TypedDict):
      id: int
      name: str
      email: str
  ```
- **Pydantic models for validation** (FastAPI):
  ```python
  class CreateUserRequest(BaseModel):
      name: str = Field(min_length=1, max_length=100)
      email: EmailStr
      age: int = Field(ge=0, le=150)
  ```
- **Avoid `Any`** except at boundaries where the type is genuinely unknown (e.g.,
  JSON parsing before validation). Use `object` or `Unknown` patterns instead.
- **Run a type checker** (mypy, pyright, or pytype) in CI. The PR should not
  introduce new type errors.
- **Protocol classes** for duck typing:
  ```python
  from typing import Protocol

  class Repository(Protocol):
      def get(self, id: int) -> Model | None: ...
      def save(self, model: Model) -> Model: ...
  ```

## 2. Error Handling

- **Use specific exception types.** Define domain exceptions rather than raising
  bare `Exception` or `ValueError`.
  ```python
  class OrderNotFoundError(Exception):
      def __init__(self, order_id: int):
          self.order_id = order_id
          super().__init__(f"Order not found: {order_id}")

  class InsufficientInventoryError(Exception):
      def __init__(self, product_id: int, requested: int, available: int):
          self.product_id = product_id
          self.requested = requested
          self.available = available
          super().__init__(
              f"Insufficient inventory for product {product_id}: "
              f"requested={requested}, available={available}"
          )
  ```
- **Global exception handlers**:
  - FastAPI: Use `@app.exception_handler(SomeError)` or middleware
  - Django: Use `MIDDLEWARE` with a custom exception handler or DRF's
    `exception_handler` setting
  - Flask: Use `@app.errorhandler(SomeError)`
- **Never use bare `except:`** or `except Exception:` without re-raising or
  logging. This silently swallows errors and makes debugging impossible.
  ```python
  # Bad
  try:
      process_order(order)
  except Exception:
      pass

  # Acceptable (log and re-raise or handle specifically)
  try:
      process_order(order)
  except OrderProcessingError as e:
      logger.error("Failed to process order: %s", e, exc_info=True)
      raise
  ```
- **Use `else` and `finally` correctly**:
  - `else`: Runs when no exception was raised (keep happy-path code here)
  - `finally`: Runs always (cleanup code)
- **Context managers** for resource cleanup:
  ```python
  async with aiohttp.ClientSession() as session:
      response = await session.get(url)
  ```
- **Error responses must be structured** (not just a string):
  ```json
  {
    "error": "INSUFFICIENT_INVENTORY",
    "message": "Not enough stock for product 42",
    "details": { "product_id": 42, "requested": 10, "available": 3 }
  }
  ```

## 3. Logging

- **Use the `logging` module** with named loggers, not `print()`.
  ```python
  import logging

  logger = logging.getLogger(__name__)

  logger.info("Order placed: order_id=%s, customer_id=%s", order.id, customer.id)
  ```
- **Log levels** (same as Java guidelines):
  - `ERROR`: Unrecoverable failures requiring attention
  - `WARNING`: Unexpected but handled situations
  - `INFO`: Significant business events
  - `DEBUG`: Technical details for troubleshooting
- **Structured logging**: Use `structlog` or `python-json-logger` for
  machine-parseable logs in production:
  ```python
  logger.info("order_placed", order_id=order.id, total=order.total)
  ```
- **No f-strings in log calls.** Use `%s` formatting to avoid string interpolation
  when the log level is disabled:
  ```python
  # Good (lazy evaluation)
  logger.debug("Processing item: id=%s", item.id)
  # Bad (always evaluated)
  logger.debug(f"Processing item: id={item.id}")
  ```
- **No sensitive data in logs.** Never log passwords, tokens, PII, or full request
  bodies that may contain sensitive data.
- **Request correlation**: Include a request ID in all log entries. Use middleware
  to generate/propagate correlation IDs.

## 4. API Design

### FastAPI
- **Use Pydantic models** for request/response bodies. Never accept or return
  raw `dict`.
- **Dependency injection**: Use FastAPI's `Depends()` for database sessions, auth,
  and shared logic. Do not create global mutable state.
- **Path operation ordering**: Define routes from most specific to least specific
  to avoid parameter conflicts.
- **Response models**: Always specify `response_model` to control serialization
  and documentation:
  ```python
  @router.get("/users/{user_id}", response_model=UserResponse)
  async def get_user(user_id: int) -> UserResponse:
      ...
  ```
- **Status codes**: Use appropriate HTTP status codes (same as Java guidelines).

### Django / Django REST Framework
- **Use serializers** for request validation and response formatting. Never return
  raw `QuerySet` or model instances directly.
- **ViewSets and Routers** for standard CRUD operations. Use `@action` for
  non-standard actions.
- **Permissions**: Use DRF permission classes (`IsAuthenticated`,
  `IsAdminUser`, custom) on every view. Default to restrictive permissions.
- **Pagination**: Configure default pagination in settings. All list endpoints
  must be paginated.

### Flask
- **Use Marshmallow or Pydantic** for request validation. Do not manually parse
  `request.json` without validation.
- **Blueprints**: Organize routes into Blueprints by domain/feature.
- **Error handlers**: Register global error handlers for common HTTP errors.

### All Frameworks
- **API versioning**: Version APIs in the URL path or header.
- **Pagination**: All list endpoints must support pagination.
- **Filtering and sorting**: Use query parameters for filtering and sorting. Validate
  filter fields against an allowlist.

## 5. Database Patterns

- **Use an ORM** (SQLAlchemy, Django ORM, Tortoise) for standard queries. Use raw
  SQL only for performance-critical queries that cannot be expressed efficiently
  in the ORM.
- **Migrations**: Use Alembic (SQLAlchemy) or Django migrations. Never modify the
  database schema manually in production.
- **N+1 queries**: Watch for lazy-loaded relationships accessed in loops. Use eager
  loading (`joinedload`, `selectinload` in SQLAlchemy;
  `select_related`, `prefetch_related` in Django).
  ```python
  # Bad: N+1
  orders = session.query(Order).all()
  for order in orders:
      print(order.items)  # triggers a query per order!

  # Good: eager load
  orders = session.query(Order).options(joinedload(Order.items)).all()
  ```
- **Connection pooling**: Configure connection pool size appropriately. Use
  `pool_size`, `max_overflow`, and `pool_timeout` in SQLAlchemy. In Django,
  use `CONN_MAX_AGE` or `django-db-connection-pool`.
- **Transactions**: Use context managers for explicit transactions:
  ```python
  async with session.begin():
      session.add(order)
      session.add(payment)
  ```
- **Indexing**: When adding new query patterns, verify that appropriate indexes
  exist. Add migration to create indexes for frequently filtered/sorted columns.

## 6. Security

- **Authentication**: Use established libraries (python-jose for JWT,
  authlib for OAuth2, django-allauth for Django). Do not implement JWT
  verification manually.
- **Password hashing**: Use bcrypt or argon2 via `passlib`. Never use MD5, SHA-1,
  or SHA-256 for passwords (they are too fast).
- **SQL injection**: Always use parameterized queries. Never use f-strings or
  `.format()` to build SQL:
  ```python
  # Good
  cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
  # Bad
  cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
  ```
- **Input validation**: Validate all external input at the boundary (Pydantic
  models, Django forms/serializers). Do not trust `request.json` without
  validation.
- **CORS**: Configure CORS explicitly. Do not allow `*` origins in production.
- **Secrets**: Use environment variables or a secrets manager. Never hardcode
  secrets in Python files or configuration.
- **Dependency vulnerabilities**: Run `pip-audit` or `safety check` in CI.
- **Rate limiting**: Use libraries like `slowapi` (FastAPI) or
  `django-ratelimit` to protect endpoints.

## 7. Testing

- **Use pytest** as the test framework. It is more flexible and readable than
  `unittest`.
- **Test organization**:
  ```
  tests/
    unit/
      test_order_service.py
      test_payment_gateway.py
    integration/
      test_order_api.py
      test_database.py
    conftest.py  # shared fixtures
  ```
- **Fixtures**: Use `pytest` fixtures for test setup/teardown. Use `conftest.py`
  for shared fixtures.
  ```python
  @pytest.fixture
  def order_service(mock_repo, mock_gateway):
      return OrderService(repo=mock_repo, gateway=mock_gateway)
  ```
- **Async tests**: Use `pytest-asyncio` for testing async code:
  ```python
  @pytest.mark.asyncio
  async def test_get_user():
      user = await get_user(1)
      assert user.name == "Alice"
  ```
- **Test client**: Use framework-provided test clients:
  - FastAPI: `TestClient(app)` or `httpx.AsyncClient`
  - Django: `Client()` or DRF's `APIClient()`
  - Flask: `app.test_client()`
- **Database tests**: Use transactions that roll back after each test, or use a
  test database. Consider Testcontainers for integration tests.
- **Mocking**: Use `unittest.mock.patch` or `pytest-mock`. Mock at boundaries
  (external APIs, database), not internal functions.
- **Coverage**: Aim for >80% on service/business logic. Use `pytest-cov`.

## 8. Code Style (PEP 8 and Tooling)

- **Follow PEP 8** for code style. Use an auto-formatter to enforce it.
- **Black** for formatting (or Ruff formatter). The PR should not introduce
  formatting changes mixed with logic changes -- format first, then change logic.
- **Ruff** for linting (replaces flake8, isort, pylint, and more). Configure in
  `pyproject.toml`.
- **isort** for import ordering (or Ruff's isort rules). Group imports:
  1. Standard library
  2. Third-party
  3. Local/project
- **Docstrings**: Use Google-style or NumPy-style docstrings consistently. Every
  public function, class, and module should have a docstring.
  ```python
  def calculate_total(items: list[LineItem], tax_rate: float) -> Decimal:
      """Calculate the total price including tax.

      Args:
          items: Line items in the order.
          tax_rate: Tax rate as a decimal (e.g., 0.08 for 8%).

      Returns:
          Total price including tax, rounded to 2 decimal places.

      Raises:
          ValueError: If tax_rate is negative.
      """
  ```
- **Line length**: 88 characters (Black default) or 120 characters. Be consistent
  with the project's configuration.
- **No star imports**: `from module import *` is forbidden. Always import specific
  names.

## 9. Dependency Management

- **Use `pyproject.toml`** as the single source of truth for project metadata and
  dependencies (PEP 621). Avoid `setup.py` and `setup.cfg` for new projects.
- **Pin dependencies** in lock files. Use `pip-tools` (`requirements.txt` +
  `requirements.in`), `poetry.lock`, `pdm.lock`, or `uv.lock`.
- **Separate dev dependencies** from production dependencies:
  ```toml
  [project]
  dependencies = ["fastapi>=0.100", "sqlalchemy>=2.0"]

  [project.optional-dependencies]
  dev = ["pytest>=7.0", "ruff>=0.1", "mypy>=1.0"]
  ```
- **Virtual environments**: Always use a virtual environment. Never install packages
  globally. Document the environment setup in the README.
- **Minimum Python version**: Declare the minimum Python version in `pyproject.toml`
  (`requires-python = ">=3.11"`). Test on the minimum version in CI.
- **Audit dependencies**: Run `pip-audit` in CI. Flag PRs that add dependencies
  with known vulnerabilities.
- **Prefer standard library** when possible. Do not add a dependency for something
  Python already provides (e.g., `json`, `pathlib`, `dataclasses`, `enum`).

## 10. Async Patterns

- **Use `async`/`await` consistently.** If the framework supports async (FastAPI,
  Starlette, Django 4.1+), use async for I/O-bound operations (database, HTTP,
  file I/O).
- **Do not mix sync and async.** Calling synchronous blocking code in an async
  function blocks the event loop. Use `asyncio.to_thread()` or
  `loop.run_in_executor()` for unavoidable blocking calls.
  ```python
  # Good: async all the way
  async def get_user(user_id: int) -> User:
      return await db.fetch_one("SELECT * FROM users WHERE id = $1", user_id)

  # Bad: sync call in async context
  async def get_user(user_id: int) -> User:
      return db.fetch_one_sync("SELECT * FROM users WHERE id = $1", user_id)  # blocks!
  ```
- **Concurrency with `asyncio.gather`**: Run independent I/O operations in parallel:
  ```python
  user, orders, notifications = await asyncio.gather(
      get_user(user_id),
      get_orders(user_id),
      get_notifications(user_id),
  )
  ```
- **Timeouts**: Use `asyncio.wait_for()` or `asyncio.timeout()` (Python 3.11+)
  for external calls. Never wait indefinitely.
- **Task cancellation**: Handle `asyncio.CancelledError` gracefully. Clean up
  resources when a task is cancelled.
- **Connection pooling**: Use async-compatible connection pools (asyncpg,
  aiohttp.ClientSession, httpx.AsyncClient). Create pools once at startup, not
  per request.
- **Background tasks**: Use framework-provided background task mechanisms
  (FastAPI `BackgroundTasks`, Celery, ARQ) rather than raw `asyncio.create_task()`
  for work that should survive request completion.
