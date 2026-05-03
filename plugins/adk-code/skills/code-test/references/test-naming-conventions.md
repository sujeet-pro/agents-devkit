# `code-test` — test naming conventions

The test name IS the documentation of what behavior is being asserted. When the test fails, the name should tell the reader what's broken without reading the assertion.

## Behavior-named, not function-named

| Bad (function-named) | Good (behavior-named) |
| --- | --- |
| `it("calculateCheckout()")` | `it("returns 400 when the cart is empty at checkout")` |
| `it("validateEmail")` | `it("rejects emails without @ at validate-email")` |
| `it("UserService.create")` | `it("creates a user with default role 'member'")` |
| `it("test1")` (yes, this happens) | `it("rejects negative quantities at addToCart")` |
| `it("works")` | `it("returns the discount-adjusted total")` |
| `it("doesn't crash")` | `it("returns 500 with a structured error when the upstream API is unreachable")` |

The test name should answer: "What is the assertion?" in one sentence.

## Per-framework dialects

### Vitest / Jest (`describe` / `it`)

```ts
describe("checkout", () => {
  it("returns 400 when the cart is empty", () => { … });
  it("returns 200 with the discount-adjusted total when discount is applied", () => { … });
  it("returns 401 when the user is unauthenticated", () => { … });
});
```

### Vitest / Jest (`test`)

```ts
test("rejects expired discount codes", () => { … });
test("applies same-day codes until midnight", () => { … });
```

### node:test

```ts
import { test, describe, it } from 'node:test';

describe("checkout", () => {
  it("returns 400 when the cart is empty", () => { … });
});
```

### pytest

```python
def test_returns_400_when_cart_is_empty():
    …

def test_rejects_expired_discount_codes():
    …
```

(Snake_case is the Python convention; the BEHAVIOR is still encoded.)

### JUnit 5 (Kotlin / Java)

```kotlin
class CheckoutTests {
    @Test
    fun `returns 400 when the cart is empty`() { … }

    @Test
    fun `applies discount-adjusted total when discount code is valid`() { … }
}
```

(Kotlin's backtick syntax allows space-separated test names; use it.)

### JUnit (Java, no spaces)

```java
@Test
void returns400WhenCartIsEmpty() { … }

@Test
void appliesDiscountAdjustedTotalWhenCodeIsValid() { … }
```

### Go

```go
func TestReturns400WhenCartIsEmpty(t *testing.T) { … }
func TestAppliesDiscountAdjustedTotalWhenCodeIsValid(t *testing.T) { … }
```

### Rust

```rust
#[test]
fn returns_400_when_cart_is_empty() { … }

#[test]
fn applies_discount_adjusted_total_when_code_is_valid() { … }
```

### Ruby (RSpec)

```ruby
describe Checkout do
  it "returns 400 when the cart is empty" do … end
  it "applies the discount-adjusted total when the code is valid" do … end
end
```

## Behavior-name shape

A good behavior-name has 3 parts (in any order):

- **Action** (the verb the test asserts): "returns", "rejects", "throws", "logs", "increments", "applies", "sends".
- **Result** (the observable outcome): "400", "the discount-adjusted total", "ParseError", "to the audit log".
- **Condition** (when this happens): "when the cart is empty", "with no discount code", "if the user is unauthenticated".

Examples:

| Action | Result | Condition |
| --- | --- | --- |
| `returns` | `400` | `when the cart is empty at checkout` |
| `rejects` | `expired discount codes` | `at apply-discount` |
| `throws` | `ParseError` | `for malformed date strings` |
| `logs` | `WARN with the queue name` | `when enqueue fails` |

## Anti-patterns

- **`it("should return 400 …")`** — the "should" is fluff. `returns 400` is sharper.
- **`it("happy path")`** — happy path of WHAT?
- **`it("error case")`** — which error?
- **`it("test 1")`** / `it("test 2")`** — useless.
- **`it("works correctly")`** — what's "correctly"?
- **`it("does the thing")`** — what thing?
- **`it("returns true")`** — true under what condition? when?
- **`it("integration test")`** — that's the type, not the behavior.

## When the name is too long

If the behavior name runs >80 characters, you might be testing two things. Split:

- BAD: `it("returns 400 when the cart is empty AND logs the rejection AND increments the metric")`
- GOOD:
  - `it("returns 400 when the cart is empty at checkout")`
  - `it("logs an INFO when an empty cart is rejected at checkout")`
  - `it("increments the empty_cart_rejected metric on rejection")`

Each test asserts ONE behavior. Failures point at exactly one thing.

## Group with `describe` (or equivalent)

Use the outer `describe` for the unit / function being tested; the `it` is the behavior:

```ts
describe("applyDiscount", () => {
  describe("with a valid code", () => {
    it("returns the discount-adjusted total", () => { … });
  });

  describe("with an expired code", () => {
    it("returns the original total", () => { … });
    it("logs a WARN with the code value", () => { … });
  });
});
```

The outer-`describe` block names the SUT; the inner `describe` blocks group BY CONDITION; the `it` names the assertion.

## Snapshot tests

Snapshots get a name too — make it behavior-shaped:

| Bad | Good |
| --- | --- |
| `expect(x).toMatchSnapshot()` (auto-named) | `expect(x).toMatchSnapshot("checkout response with discount")` |
| `it("matches snapshot")` | `it("renders the checkout summary with the discount applied")` (then snapshot) |

The snapshot file is auto-named; the test wrapping it should still describe behavior.

## When the framework forces names

Some frameworks (older JUnit, some test.each variants) force a function-style name. In those cases:

- Use the closest-to-behavior style allowed.
- Add a comment above the test summarizing the behavior in plain English.

Don't fight the framework, but don't surrender to function-named tests either.
