# Kanban

**Directive:** `kanban`

**Syntax:**

```
kanban
    column1[To Do]
        task1[Task description]
        task2[Another task]
    column2[In Progress]
        task3[Active work]
    column3[Done]
        task4[Completed item]
```

**Example:**

```
%% Diagram: Sprint Board
%% Type: kanban
kanban
    todo[To Do]
        t1[Setup CI pipeline]
        t2[Write API docs]
        t3[Add rate limiting]
    progress[In Progress]
        t4[Auth service refactor]
        t5[Database migration]
    review[In Review]
        t6[Fix pagination bug]
    done[Done]
        t7[Add health check endpoint]
        t8[Update dependencies]
```
