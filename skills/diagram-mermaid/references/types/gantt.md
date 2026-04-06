# Gantt Chart

**Directive:** `gantt`

**Syntax:**

```
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    axisFormat %b %d
    excludes weekends
    todayMarker stroke-width:3px,stroke:#0f0

    section Section Name
    Task Name           :id, start_date, duration
    Active Task         :active, id, start_date, duration
    Critical Task       :crit, id, start_date, duration
    Done Task           :done, id, start_date, duration
    Milestone           :milestone, id, start_date, 0d
    After dependency    :id, after other_id, duration
```

**Example:**

```
%% Diagram: Sprint Plan
%% Type: gantt
gantt
    title Q2 Sprint 4
    dateFormat YYYY-MM-DD
    axisFormat %b %d
    excludes weekends

    section Backend
    API redesign          :crit, api, 2025-04-07, 5d
    Database migration    :db, after api, 3d
    Integration tests     :test, after db, 2d

    section Frontend
    Component library     :comp, 2025-04-07, 4d
    Page refactor         :pages, after comp, 3d
    E2E tests             :e2e, after pages, 2d

    section DevOps
    CI pipeline update    :ci, 2025-04-07, 2d
    Staging deploy        :milestone, deploy, after test, 0d

    section QA
    Regression testing    :qa, after e2e, 3d
    Release               :milestone, release, after qa, 0d
```
