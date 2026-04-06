# Class Diagram

**Directive:** `classDiagram`

**Syntax:**

```
classDiagram
    class ClassName {
        +String publicField
        -int privateField
        #List~String~ protectedField
        +publicMethod() ReturnType
        -privateMethod(param: Type) void
        #protectedMethod()* void
        +staticMethod()$ Type
    }

    %% Relationships
    ClassA <|-- ClassB : inherits
    ClassA *-- ClassC : composition
    ClassA o-- ClassD : aggregation
    ClassA --> ClassE : association
    ClassA ..> ClassF : dependency
    ClassA ..|> InterfaceG : implements
    ClassA "1" --> "*" ClassH : multiplicity

    %% Notes
    note for ClassName "This is a note"

    %% Namespace
    namespace Domain {
        class Entity
        class ValueObject
    }
```

**Example:**

```
%% Diagram: Repository Pattern
%% Type: class
classDiagram
    class Repository~T~ {
        <<interface>>
        +findById(id: string) T
        +findAll() List~T~
        +save(entity: T) void
        +delete(id: string) void
    }

    class UserRepository {
        -db: Database
        +findById(id: string) User
        +findAll() List~User~
        +save(user: User) void
        +delete(id: string) void
        +findByEmail(email: string) User
    }

    class User {
        +String id
        +String email
        +String name
        -String passwordHash
        +verifyPassword(password: string) bool
    }

    Repository~T~ <|.. UserRepository : implements
    UserRepository --> User : manages
```
