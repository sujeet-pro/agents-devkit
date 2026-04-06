# Entity-Relationship Diagram

**Directive:** `erDiagram`

**Syntax:**

```
erDiagram
    ENTITY1 ||--o{ ENTITY2 : "relationship"

    %% Cardinality:
    %%   ||  exactly one
    %%   o|  zero or one
    %%   }|  one or more
    %%   }o  zero or more

    ENTITY {
        type name PK "comment"
        type name FK
        type name UK
    }
```

**Example:**

```
%% Diagram: E-Commerce Data Model
%% Type: er
erDiagram
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER {
        uuid id PK
        string email UK
        string name
        timestamp created_at
    }

    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        uuid id PK
        uuid customer_id FK
        decimal total
        enum status "pending|paid|shipped|delivered"
        timestamp ordered_at
    }

    ORDER_ITEM }o--|| PRODUCT : references
    ORDER_ITEM {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
        decimal unit_price
    }

    PRODUCT ||--o{ PRODUCT_VARIANT : "has variants"
    PRODUCT {
        uuid id PK
        string name
        text description
        uuid category_id FK
    }

    CATEGORY ||--o{ PRODUCT : categorizes
    CATEGORY {
        uuid id PK
        string name
        uuid parent_id FK "self-referential"
    }
```
