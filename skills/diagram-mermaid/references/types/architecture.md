# Architecture Diagram

**Directive:** `architecture-beta`

**Syntax:**

```
architecture-beta
    group api(cloud)[API Layer]

    service gateway(internet)[API Gateway] in api
    service auth(server)[Auth Service] in api
    service db(database)[PostgreSQL]

    gateway:R --> L:auth
    auth:B --> T:db
```

Icons: `cloud`, `database`, `disk`, `internet`, `server`.

**Example:**

```
%% Diagram: Microservices Architecture
%% Type: architecture
architecture-beta
    group frontend(cloud)[Frontend]
    group backend(cloud)[Backend Services]
    group data(cloud)[Data Layer]

    service cdn(internet)[CDN] in frontend
    service spa(server)[SPA] in frontend

    service gateway(internet)[API Gateway] in backend
    service users(server)[User Service] in backend
    service orders(server)[Order Service] in backend
    service notify(server)[Notification] in backend

    service postgres(database)[PostgreSQL] in data
    service redis(database)[Redis Cache] in data

    cdn:R --> L:spa
    spa:B --> T:gateway
    gateway:B --> T:users
    gateway:B --> T:orders
    gateway:B --> T:notify
    users:B --> T:postgres
    orders:B --> T:postgres
    users:R --> L:redis
```
