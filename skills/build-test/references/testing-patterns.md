# Testing patterns — practical templates

Concrete templates for the most common testing situations. Pick the one that matches your stack and adapt; the SHAPE is what matters.

## Table of contents

1. Test structure (Arrange-Act-Assert)
2. Test naming
3. Common assertions
4. Mocking at boundaries
5. React / component (Testing Library)
6. API / integration (supertest)
7. End-to-end (Playwright)
8. Anti-patterns

## 1. Test structure (Arrange-Act-Assert)

```ts
test('user can be created with valid email and password', () => {
  // Arrange
  const repo = new InMemoryUserRepository();
  const service = new UserService(repo);

  // Act
  const result = service.create({ email: 'user@example.com', password: 'p@ssw0rd-very-long' });

  // Assert
  expect(result.ok).toBe(true);
  expect(repo.count()).toBe(1);
});
```

Visually separated. One concept per test. If the assert section has unrelated checks, split the test.

## 2. Test naming

Convention: describe the **behavior** in the test name. Three rough patterns work:

```
test('returns 422 when email is missing', ...)
test('createUser_missingEmail_returns422', ...)
test('createUser › when email is missing › returns 422', ...)
```

Avoid: `test('createUser')`, `test('it works')`, `test('happy path')`.

## 3. Common assertions

```ts
expect(result).toBe(value);                         // primitive identity
expect(result).toEqual({ a: 1, b: 2 });             // deep equality
expect(result).toMatchObject({ a: 1 });             // subset match
expect(result).toBeNull();                          // null
expect(result).toBeUndefined();                     // undefined
expect(result).toContain('substring');              // string / array contains
expect(fn).toThrow(/permission denied/i);           // throws matching regex
expect(promise).resolves.toBe(value);               // async resolves
expect(promise).rejects.toThrow(/timeout/);         // async rejects
```

## 4. Mocking at boundaries

Mock at **architectural boundaries** (HTTP, DB, time, randomness, env), not in the middle of business logic.

```ts
// Time
beforeAll(() => vi.useFakeTimers().setSystemTime(new Date('2025-01-15T00:00:00Z')));
afterAll(() => vi.useRealTimers());

// Network (msw is preferred over jest.mock for HTTP)
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
const server = setupServer(
  http.get('https://api.example.com/v1/me', () => HttpResponse.json({ id: 'user_1' }))
);
beforeAll(() => server.listen());
afterAll(() => server.close());
afterEach(() => server.resetHandlers());

// Randomness
vi.spyOn(globalThis.crypto, 'randomUUID').mockReturnValue('00000000-0000-0000-0000-000000000001');

// Environment
vi.stubEnv('NODE_ENV', 'test');
```

## 5. React / component (Testing Library)

```tsx
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('login form submits with valid credentials', async () => {
  const onSubmit = vi.fn();
  render(<LoginForm onSubmit={onSubmit} />);

  await userEvent.type(screen.getByLabelText(/email/i), 'user@example.com');
  await userEvent.type(screen.getByLabelText(/password/i), 'correct-horse-battery-staple');
  await userEvent.click(screen.getByRole('button', { name: /log in/i }));

  expect(onSubmit).toHaveBeenCalledWith({
    email: 'user@example.com',
    password: 'correct-horse-battery-staple',
  });
});
```

Rules:

- Query by **role** > **label** > **text** > **test id** (last resort).
- Use `userEvent` over `fireEvent` for realistic interactions.
- Assert what the user sees, not the React internals.

## 6. API / integration (supertest)

```ts
import request from 'supertest';
import { createApp } from '../src/app';

describe('POST /api/users', () => {
  const app = createApp({ db: 'in-memory' });

  test('returns 201 with the created user on valid input', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({ email: 'a@b.com', password: 'long-enough-password' });
    expect(res.status).toBe(201);
    expect(res.body).toMatchObject({ email: 'a@b.com' });
    expect(res.body).not.toHaveProperty('password');
  });

  test('returns 422 with VALIDATION_ERROR on missing email', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({ password: 'long-enough-password' });
    expect(res.status).toBe(422);
    expect(res.body.error.code).toBe('VALIDATION_ERROR');
  });

  test('returns 401 without an auth token on protected route', async () => {
    const res = await request(app).get('/api/me');
    expect(res.status).toBe(401);
  });
});
```

## 7. End-to-end (Playwright)

```ts
import { test, expect } from '@playwright/test';

test('user signs up and lands on the dashboard', async ({ page }) => {
  await page.goto('/signup');
  await page.getByLabel(/email/i).fill('e2e@example.com');
  await page.getByLabel(/password/i).fill('correct-horse-battery-staple');
  await page.getByRole('button', { name: /create account/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByRole('heading', { name: /welcome/i })).toBeVisible();
});
```

E2E rules:

- Test the user journey, not every code path.
- Use `getByRole` / `getByLabel` for resilience.
- Web-first assertions (`await expect(...)`) — they auto-retry until timeout.
- Run against a known-state seeded environment.

## 8. Test anti-patterns

- Tests that change state in the database without cleanup → use transactions or per-test fixtures.
- Tests that share mutable module state → reset in `beforeEach`.
- Tests with sleep / setTimeout to "wait for things" → use fake timers or web-first assertions.
- "Test that does N things" → N tests instead.
- Snapshot tests for behavior → assert behavior explicitly, snapshots only for shape.
- Tests that test the mock → reach for an integration test or a real impl.
- Coverage chasing (tests that touch lines but don't assert) → behavior coverage > line coverage.
