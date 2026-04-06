# XY Chart

**Directive:** `xychart-beta`

**Syntax:**

```
xychart-beta
    title "Chart Title"
    x-axis [label1, label2, label3]
    y-axis "Y Label" min --> max
    bar [val1, val2, val3]
    line [val1, val2, val3]
```

**Example:**

```
%% Diagram: API Response Times
%% Type: xy
xychart-beta
    title "API Latency by Endpoint (ms)"
    x-axis ["/users", "/orders", "/products", "/search", "/auth"]
    y-axis "P95 Latency (ms)" 0 --> 500
    bar [45, 120, 65, 350, 30]
    line [35, 90, 50, 280, 25]
```
