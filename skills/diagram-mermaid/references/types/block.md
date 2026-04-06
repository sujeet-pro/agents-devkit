# Block Diagram

**Directive:** `block-beta`

**Syntax:**

```
block-beta
    columns 3

    a["Block A"]:2 b["Block B"]
    c["Block C"] d["Block D"] e["Block E"]

    a --> c
    b --> d

    block:group1
        columns 2
        f["Inner F"] g["Inner G"]
    end
```

**Example:**

```
%% Diagram: Deployment Architecture
%% Type: block
block-beta
    columns 3

    block:cdn["CDN Layer"]
        columns 1
        cf["CloudFront"]
    end

    block:compute["Compute"]
        columns 2
        ecs1["ECS Task 1"] ecs2["ECS Task 2"]
    end

    block:data["Data"]
        columns 2
        rds["RDS PostgreSQL"] redis["ElastiCache"]
    end

    cf --> ecs1
    cf --> ecs2
    ecs1 --> rds
    ecs2 --> rds
    ecs1 --> redis
    ecs2 --> redis
```
