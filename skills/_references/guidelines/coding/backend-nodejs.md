# Node.js Backend Review Guidelines

These guidelines apply to **Node.js backend** projects, covering Express, Fastify,
and NestJS applications. They supplement the general guidelines with Node.js-specific
rules for building reliable, maintainable, and performant server-side JavaScript/TypeScript
services.

---

## 1. Async Patterns

- **Use `async`/`await` over raw promises and callbacks.** Async/await produces
  readable, debuggable code with proper stack traces:
  ```typescript
  // Good
  async function getOrder(orderId: string): Promise<Order> {
      const order = await orderRepo.findById(orderId);
      if (!order) throw new OrderNotFoundError(orderId);
      const enriched = await enrichWithCustomerData(order);
      return enriched;
  }

  // Bad: nested promise chains
  function getOrder(orderId: string): Promise<Order> {
      return orderRepo.findById(orderId)
          .then(order => {
              if (!order) throw new OrderNotFoundError(orderId);
              return enrichWithCustomerData(order);
          })
          .then(enriched => enriched);
  }
  ```
- **Handle unhandled rejections.** Register a global handler in your application
  entry point. In production, log the error and shut down gracefully:
  ```typescript
  process.on("unhandledRejection", (reason, promise) => {
      logger.fatal({ reason, promise }, "Unhandled promise rejection -- shutting down");
      process.exit(1);
  });
  ```
- **Use `Promise.allSettled`** when running independent async operations where
  individual failures should not abort the batch:
  ```typescript
  const results = await Promise.allSettled(
      orders.map(order => processOrder(order))
  );

  const failures = results.filter(r => r.status === "rejected");
  if (failures.length > 0) {
      logger.warn({ failureCount: failures.length }, "Some orders failed to process");
  }
  ```
- **Avoid `async void` functions.** Exceptions thrown in `async void` (or async
  functions called without `await`) become unhandled rejections. Always `await`
  async calls or attach `.catch()`.
- **Use `AbortController` for cancellation** of long-running operations, HTTP
  requests via `fetch`, and database queries that support it:
  ```typescript
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);

  try {
      const response = await fetch(url, { signal: controller.signal });
      return await response.json();
  } finally {
      clearTimeout(timeout);
  }
  ```

> **Reference**: [Node.js Async Hooks](https://nodejs.org/api/async_hooks.html),
> [MDN: async function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)

## 2. Error Handling

- **Define custom error classes** for domain errors. Include an error code, HTTP
  status, and contextual details:
  ```typescript
  class AppError extends Error {
      constructor(
          message: string,
          public readonly code: string,
          public readonly statusCode: number,
          public readonly details?: Record<string, unknown>,
      ) {
          super(message);
          this.name = this.constructor.name;
          Error.captureStackTrace(this, this.constructor);
      }
  }

  class OrderNotFoundError extends AppError {
      constructor(orderId: string) {
          super(`Order not found: ${orderId}`, "ORDER_NOT_FOUND", 404, { orderId });
      }
  }
  ```
- **Distinguish operational errors from programmer errors.**
  - **Operational errors** (network timeout, invalid input, file not found) are
    expected failure modes. Handle them with retries, fallbacks, or user-facing
    error messages.
  - **Programmer errors** (TypeError, ReferenceError, assertion failure) indicate
    bugs. Let them crash the process and fix the code.
- **Never catch and ignore.** Every `catch` block must log, rethrow, or handle
  the error. Silent swallowing makes debugging impossible:
  ```typescript
  // Bad
  try { await riskyOperation(); }
  catch (e) { /* ignore */ }

  // Good
  try { await riskyOperation(); }
  catch (e) {
      logger.error({ err: e, context: "riskyOperation" }, "Operation failed");
      throw e;
  }
  ```
- **Centralize error handling** in framework-specific middleware (see framework
  sections below). Individual route handlers should throw; the error middleware
  converts exceptions to HTTP responses.

> **Reference**: [Node.js Error Handling Best Practices](https://nodejs.org/api/errors.html),
> [Joyent Error Handling Guide](https://www.joyent.com/node-js/production/design/errors)

## 3. Express

- **Middleware order matters.** Register middleware in this order:
  1. Request parsing (`express.json()`, `express.urlencoded()`)
  2. Security (`helmet`, CORS, rate limiting)
  3. Logging / request ID
  4. Authentication / authorization
  5. Routes
  6. 404 handler
  7. Error-handling middleware (must be last)
- **Error-handling middleware** must have exactly four parameters `(err, req, res, next)`.
  Express uses the parameter count to distinguish error handlers:
  ```typescript
  app.use((err: AppError | Error, req: Request, res: Response, next: NextFunction) => {
      const statusCode = "statusCode" in err ? err.statusCode : 500;
      const code = "code" in err ? err.code : "INTERNAL_ERROR";

      logger.error({ err, method: req.method, url: req.url }, "Request failed");

      res.status(statusCode).json({
          error: { code, message: err.message },
      });
  });
  ```
- **Wrap async route handlers** to forward rejected promises to the error middleware.
  Express 4 does not handle async errors natively (Express 5 does):
  ```typescript
  const asyncHandler = (fn: RequestHandler): RequestHandler =>
      (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

  app.get("/orders/:id", asyncHandler(async (req, res) => {
      const order = await orderService.findById(req.params.id);
      if (!order) throw new OrderNotFoundError(req.params.id);
      res.json(order);
  }));
  ```
- **Use Router** for route grouping. Each domain area should have its own router
  file:
  ```typescript
  // routes/orders.ts
  const router = Router();
  router.get("/", asyncHandler(listOrders));
  router.post("/", asyncHandler(createOrder));
  router.get("/:id", asyncHandler(getOrder));
  export default router;

  // app.ts
  app.use("/api/v1/orders", ordersRouter);
  ```

> **Reference**: [Express.js Documentation](https://expressjs.com/),
> [Express Error Handling](https://expressjs.com/en/guide/error-handling.html)

## 4. Fastify

- **Use JSON Schema validation** for request bodies, query parameters, and response
  shapes. Fastify compiles schemas into fast validators and serializers:
  ```typescript
  fastify.post("/orders", {
      schema: {
          body: {
              type: "object",
              required: ["customerId", "items"],
              properties: {
                  customerId: { type: "string", format: "uuid" },
                  items: {
                      type: "array",
                      minItems: 1,
                      items: {
                          type: "object",
                          required: ["productId", "quantity"],
                          properties: {
                              productId: { type: "string" },
                              quantity: { type: "integer", minimum: 1 },
                          },
                      },
                  },
              },
          },
          response: {
              201: { $ref: "OrderResponse" },
          },
      },
      handler: async (request, reply) => {
          const order = await orderService.create(request.body);
          reply.code(201).send(order);
      },
  });
  ```
- **Use plugins for encapsulation.** Fastify's plugin system provides dependency
  isolation and lifecycle management:
  ```typescript
  async function orderPlugin(fastify: FastifyInstance) {
      const orderService = new OrderService(fastify.db);
      fastify.decorate("orderService", orderService);

      fastify.get("/orders", listOrdersHandler);
      fastify.post("/orders", createOrderHandler);
  }

  fastify.register(orderPlugin, { prefix: "/api/v1" });
  ```
- **Use `setErrorHandler`** for centralized error handling:
  ```typescript
  fastify.setErrorHandler((error, request, reply) => {
      request.log.error({ err: error }, "Request failed");
      const statusCode = error.statusCode ?? 500;
      reply.status(statusCode).send({
          error: { code: error.code ?? "INTERNAL_ERROR", message: error.message },
      });
  });
  ```
- **Type providers**: Use `@fastify/type-provider-typebox` or
  `@fastify/type-provider-zod` for end-to-end type safety between schemas and
  handler types.

> **Reference**: [Fastify Documentation](https://fastify.dev/docs/latest/),
> [Fastify Validation and Serialization](https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/)

## 5. NestJS

- **Module organization**: Each domain area should have its own module containing
  controllers, services, and repository providers. Keep modules cohesive:
  ```typescript
  @Module({
      imports: [TypeOrmModule.forFeature([OrderEntity])],
      controllers: [OrderController],
      providers: [OrderService, OrderMapper],
      exports: [OrderService],
  })
  export class OrderModule {}
  ```
- **Guards for authentication/authorization.** Do not check auth inside controllers;
  use guards:
  ```typescript
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles("admin")
  @Delete(":id")
  async deleteOrder(@Param("id") id: string): Promise<void> {
      await this.orderService.delete(id);
  }
  ```
- **Interceptors for cross-cutting concerns**: logging, response transformation,
  caching, timeout:
  ```typescript
  @Injectable()
  export class LoggingInterceptor implements NestInterceptor {
      intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
          const request = context.switchToHttp().getRequest();
          const start = Date.now();

          return next.handle().pipe(
              tap(() => {
                  const duration = Date.now() - start;
                  logger.info({ method: request.method, url: request.url, duration });
              }),
          );
      }
  }
  ```
- **Pipes for validation**: Use `ValidationPipe` globally with class-validator DTOs:
  ```typescript
  app.useGlobalPipes(new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
  }));
  ```
- **Exception filters** for consistent error responses. Create a global filter
  that maps domain exceptions to HTTP responses.

> **Reference**: [NestJS Documentation](https://docs.nestjs.com/),
> [NestJS Guards](https://docs.nestjs.com/guards),
> [NestJS Interceptors](https://docs.nestjs.com/interceptors)

## 6. Streaming and Backpressure

- **Use `pipeline()`** (from `node:stream/promises`) instead of `.pipe()` for
  stream composition. `pipeline` handles error propagation and cleanup automatically:
  ```typescript
  import { pipeline } from "node:stream/promises";

  async function processLargeFile(input: string, output: string) {
      await pipeline(
          createReadStream(input),
          new Transform({
              transform(chunk, encoding, callback) {
                  callback(null, processChunk(chunk));
              },
          }),
          createWriteStream(output),
      );
  }
  ```
- **Respect backpressure.** When producing data faster than a consumer can handle,
  check the return value of `.write()` and wait for the `drain` event:
  ```typescript
  async function writeRecords(stream: Writable, records: AsyncIterable<Record>) {
      for await (const record of records) {
          const canContinue = stream.write(JSON.stringify(record) + "\n");
          if (!canContinue) {
              await once(stream, "drain");
          }
      }
      stream.end();
  }
  ```
- **Streaming HTTP responses** for large payloads. Pipe database cursors or file
  reads directly to the response rather than buffering in memory:
  ```typescript
  app.get("/export", asyncHandler(async (req, res) => {
      res.setHeader("Content-Type", "application/ndjson");
      const cursor = orderRepo.streamAll();
      await pipeline(cursor, new JSONStringify(), res);
  }));
  ```

> **Reference**: [Node.js Stream API](https://nodejs.org/api/stream.html),
> [Node.js Backpressuring in Streams](https://nodejs.org/en/learn/modules/backpressuring-in-streams)

## 7. Worker Threads

- **Use worker threads for CPU-intensive work** that would block the event loop:
  image processing, cryptography, parsing large documents, heavy computation.
  Do not use them for I/O-bound tasks (use async I/O instead).
- **`SharedArrayBuffer` and `Atomics`** for zero-copy data sharing between threads.
  Use these for large datasets where serialization overhead is significant:
  ```typescript
  import { Worker, isMainThread, parentPort, workerData } from "node:worker_threads";

  if (isMainThread) {
      const sharedBuffer = new SharedArrayBuffer(1024 * 1024);
      const worker = new Worker(__filename, { workerData: { buffer: sharedBuffer } });
      worker.on("message", (result) => { /* handle result */ });
  } else {
      const { buffer } = workerData;
      const view = new Float64Array(buffer);
      // perform computation on shared data
      parentPort!.postMessage({ done: true });
  }
  ```
- **Use a worker pool** for repeated CPU-intensive tasks. Avoid creating a new
  worker for every request (thread creation has overhead). Libraries like
  `workerpool` or `piscina` manage pools for you.
- **Error handling**: Workers can crash independently. Always handle `error` and
  `exit` events on worker instances.

> **Reference**: [Node.js Worker Threads](https://nodejs.org/api/worker_threads.html),
> [Piscina Worker Pool](https://github.com/piscinajs/piscina)

## 8. Observability

- **Use structured logging with pino.** Pino is fast, produces JSON, and integrates
  with all major Node.js frameworks:
  ```typescript
  import pino from "pino";

  const logger = pino({
      level: process.env.LOG_LEVEL ?? "info",
      serializers: {
          err: pino.stdSerializers.err,
          req: pino.stdSerializers.req,
          res: pino.stdSerializers.res,
      },
  });

  // Log with context
  logger.info({ orderId, customerId, total }, "Order placed successfully");
  ```
- **Correlation IDs**: Generate a unique request ID at the edge (or extract from
  `X-Request-Id` header) and propagate it through all log entries and downstream
  calls. Use `AsyncLocalStorage` for implicit propagation:
  ```typescript
  import { AsyncLocalStorage } from "node:async_hooks";

  const requestContext = new AsyncLocalStorage<{ requestId: string }>();

  app.use((req, res, next) => {
      const requestId = req.headers["x-request-id"] ?? crypto.randomUUID();
      requestContext.run({ requestId }, () => next());
  });
  ```
- **OpenTelemetry integration**: Use `@opentelemetry/sdk-node` for automatic
  instrumentation of HTTP, database, and messaging frameworks. Add custom spans
  for business-critical operations.
- **Health endpoints**: Expose `/health/live` (is the process running?) and
  `/health/ready` (can it serve traffic?) for orchestrator probes.

> **Reference**: [Pino Logger](https://getpino.io/),
> [OpenTelemetry JS](https://opentelemetry.io/docs/languages/js/)

## 9. Security

- **Use `helmet`** to set security-related HTTP headers (CSP, HSTS, X-Frame-Options):
  ```typescript
  import helmet from "helmet";
  app.use(helmet());
  ```
- **Rate limiting**: Protect public endpoints with rate limiting. Use
  `@fastify/rate-limit` or `express-rate-limit`:
  ```typescript
  import rateLimit from "express-rate-limit";

  app.use("/api/", rateLimit({
      windowMs: 15 * 60 * 1000,  // 15 minutes
      max: 100,                   // 100 requests per window
      standardHeaders: true,
      legacyHeaders: false,
  }));
  ```
- **Input validation at the boundary.** Use `zod` or `joi` to validate and parse
  all external input before it enters business logic:
  ```typescript
  import { z } from "zod";

  const CreateOrderSchema = z.object({
      customerId: z.string().uuid(),
      items: z.array(z.object({
          productId: z.string(),
          quantity: z.number().int().positive(),
      })).min(1),
  });

  type CreateOrderInput = z.infer<typeof CreateOrderSchema>;
  ```
- **Parameterized queries only.** Never interpolate user input into SQL strings.
  Use parameterized queries or an ORM:
  ```typescript
  // Good
  await db.query("SELECT * FROM orders WHERE id = $1", [orderId]);

  // Bad: SQL injection vulnerability
  await db.query(`SELECT * FROM orders WHERE id = '${orderId}'`);
  ```
- **Dependency auditing**: Run `npm audit` in CI. Configure Dependabot or Snyk
  for automated vulnerability scanning.

> **Reference**: [Helmet.js](https://helmetjs.github.io/),
> [OWASP Node.js Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html)

## 10. Testing

- **Use the built-in test runner** (`node:test`) for new projects on Node.js 20+,
  or Jest/Vitest for existing codebases. Prefer Vitest for TypeScript projects due
  to faster execution and native ESM support.
- **Test HTTP endpoints** with `supertest` (Express) or `inject` (Fastify):
  ```typescript
  import request from "supertest";

  describe("POST /api/v1/orders", () => {
      it("returns 201 with valid input", async () => {
          const res = await request(app)
              .post("/api/v1/orders")
              .send({ customerId: "uuid-123", items: [{ productId: "p1", quantity: 2 }] })
              .expect(201);

          expect(res.body).toHaveProperty("id");
          expect(res.body.status).toBe("PENDING");
      });

      it("returns 400 with empty items array", async () => {
          await request(app)
              .post("/api/v1/orders")
              .send({ customerId: "uuid-123", items: [] })
              .expect(400);
      });
  });
  ```
- **Testcontainers** for integration tests with real databases:
  ```typescript
  import { PostgreSqlContainer } from "@testcontainers/postgresql";

  let container: StartedPostgreSqlContainer;

  beforeAll(async () => {
      container = await new PostgreSqlContainer("postgres:16-alpine").start();
      await runMigrations(container.getConnectionUri());
  }, 60_000);

  afterAll(async () => {
      await container.stop();
  });
  ```
- **Mock external services** with `nock` or `msw` (Mock Service Worker). Prefer MSW
  for its network-level interception and reusability across tests.
- **Avoid mocking the module system** (`jest.mock`). It couples tests to
  implementation details. Prefer dependency injection and test doubles.

> **Reference**: [Node.js Test Runner](https://nodejs.org/api/test.html),
> [Vitest Documentation](https://vitest.dev/),
> [Mock Service Worker](https://mswjs.io/)
