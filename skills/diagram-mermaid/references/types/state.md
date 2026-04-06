# State Diagram

**Directive:** `stateDiagram-v2`

**Syntax:**

```
stateDiagram-v2
    [*] --> State1
    State1 --> State2 : event
    State2 --> [*]

    State1 : Entry action
    State1 : Do activity
    State1 : Exit action

    state "Long Name" as s1

    state fork_state <<fork>>
    state join_state <<join>>

    state if_state <<choice>>
    [*] --> if_state
    if_state --> State1 : condition 1
    if_state --> State2 : condition 2

    state CompositeState {
        [*] --> SubState1
        SubState1 --> SubState2
    }

    state ConcurrentState {
        [*] --> A
        --
        [*] --> B
    }

    note right of State1 : Note text
```

**Example:**

```
%% Diagram: Order Lifecycle
%% Type: state
stateDiagram-v2
    [*] --> draft : Create Order

    state "Order Processing" as processing {
        draft --> pending_payment : Submit
        pending_payment --> paid : Payment Received
        paid --> preparing : Start Preparation

        state payment_check <<choice>>
        pending_payment --> payment_check : Check Payment
        payment_check --> paid : Success
        payment_check --> payment_failed : Declined

        payment_failed --> pending_payment : Retry
        payment_failed --> cancelled : Max retries
    }

    preparing --> shipped : Ship Order
    shipped --> delivered : Confirm Delivery
    delivered --> [*]

    cancelled --> [*]

    note right of shipped : Tracking number assigned
```
