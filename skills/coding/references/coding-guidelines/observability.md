# Observability Review Guidelines

These guidelines apply to **observability engineering** across all backend services,
covering structured logging, distributed tracing, metrics, alerting, dashboards, and
health checks. They supplement the general guidelines with rules for building systems
that are transparent, diagnosable, and operable in production.

---

## 1. Structured Logging

- **Emit all logs as JSON.** Structured logs are machine-parseable, queryable, and
  compatible with every major log aggregation platform (Elasticsearch, Datadog,
  Splunk, CloudWatch Logs Insights). Never rely on regex-parsed plain text in
  production:
  ```json
  {
      "timestamp": "2025-03-15T14:23:01.442Z",
      "level": "info",
      "message": "Order placed successfully",
      "service": "order-api",
      "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
      "spanId": "00f067aa0ba902b7",
      "orderId": "ord-8a3f",
      "customerId": "cust-12b4",
      "total": 142.50,
      "itemCount": 3,
      "durationMs": 87
  }
  ```
- **Correlation IDs are mandatory.** Every request entering the system must receive
  a unique identifier (typically a UUID or W3C Trace Context `traceparent`). This ID
  must propagate through all downstream service calls, message queue publications,
  and background job dispatches:
  - Extract from `X-Request-Id` or `traceparent` header at the edge.
  - Generate a new ID if none is present.
  - Attach the ID to every log entry, every outgoing HTTP header, every message
    envelope, and every database query comment.
  - Use language-native context propagation: `AsyncLocalStorage` (Node.js),
    `CoroutineContext` (Kotlin), `contextvars` (Python), `Context` (Go),
    `MDC` (Java/SLF4J).
- **Log levels must be semantically correct:**

  | Level | Use For | Example |
  |-------|---------|---------|
  | `error` | Failures that require human investigation | Database connection failure, payment gateway 5xx |
  | `warn` | Degraded behavior that self-recovers | Circuit breaker opened, retry succeeded on attempt 3 |
  | `info` | Significant business events | Order placed, user registered, deployment completed |
  | `debug` | Diagnostic detail for active troubleshooting | SQL query text, cache hit/miss, request/response payloads |

- **Never log secrets.** Scrub or redact PII, tokens, passwords, API keys, and
  credit card numbers before they reach the logger. Use allowlists (log only known-safe
  fields) rather than denylists (try to catch every secret pattern).
- **Include contextual fields, not interpolated strings.** Log `{ userId: "u-123", action: "login" }`,
  not `"User u-123 performed login"`. Structured fields enable filtering and
  aggregation; interpolated strings do not.
- **Rate-limit noisy log paths.** A tight loop emitting thousands of identical log
  entries per second degrades log infrastructure and masks other signals. Use
  sampling or deduplication for high-frequency events.

> **Reference**: [The Twelve-Factor App -- Logs](https://12factor.net/logs),
> [OpenTelemetry Logging Data Model](https://opentelemetry.io/docs/specs/otel/logs/data-model/),
> [Pino Logger Best Practices](https://getpino.io/#/docs/best-practices)

## 2. Distributed Tracing

- **Instrument with OpenTelemetry.** OpenTelemetry is the industry-converged standard
  for traces, metrics, and logs. Use the OTel SDK for your language and the OTel
  Collector as the telemetry pipeline:
  ```
  Service → OTel SDK → OTel Collector → Backend (Jaeger, Tempo, Datadog, etc.)
  ```
- **Use W3C Trace Context** (`traceparent` / `tracestate` headers) for cross-service
  propagation. This is the W3C Recommendation (since 2020) and is supported by all
  major tracing vendors. Do not invent proprietary propagation formats:
  ```
  traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
  ```
- **Auto-instrument frameworks first.** OTel provides automatic instrumentation for
  HTTP servers, HTTP clients, database drivers, message queue clients, and gRPC.
  Enable these before adding manual instrumentation -- they cover 80% of the trace
  with zero application code.
- **Add custom spans for business-critical operations.** Auto-instrumentation covers
  infrastructure; manual spans cover domain logic:
  ```typescript
  const tracer = trace.getTracer("order-service");

  async function placeOrder(input: CreateOrderInput): Promise<Order> {
      return tracer.startActiveSpan("placeOrder", async (span) => {
          span.setAttribute("order.customer_id", input.customerId);
          span.setAttribute("order.item_count", input.items.length);
          try {
              const order = await processOrder(input);
              span.setAttribute("order.id", order.id);
              span.setStatus({ code: SpanStatusCode.OK });
              return order;
          } catch (error) {
              span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
              span.recordException(error);
              throw error;
          } finally {
              span.end();
          }
      });
  }
  ```
- **Set span attributes that support debugging.** Include domain identifiers
  (`order.id`, `customer.id`, `payment.transaction_id`), not just infrastructure
  metadata. Follow the [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
  for attribute naming.
- **Use sampling in production.** Tracing every request at 100% volume generates
  enormous data costs. Use head-based sampling (decide at the edge) or tail-based
  sampling (decide after the trace completes, keeping errors and slow traces):
  - **Always trace**: Errors (5xx), slow requests (> p95 latency), sampled percentage of
    healthy requests (1-10%).
  - **Tail-based sampling** via the OTel Collector `tailsamplingprocessor` is
    preferred for high-traffic services.

> **Reference**: [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/otel/),
> [W3C Trace Context](https://www.w3.org/TR/trace-context/),
> [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)

## 3. Metrics

- **Follow the RED method for request-driven services** (Tom Wilkie, 2018):
  - **R**ate: Requests per second.
  - **E**rrors: Failed requests per second (and error rate as a percentage).
  - **D**uration: Latency distribution (p50, p90, p95, p99).

  Every service that handles requests must emit these three metric families as a
  baseline. If a service does not have RED metrics, it is invisible in production.

- **Follow the USE method for infrastructure resources** (Brendan Gregg):
  - **U**tilization: Percentage of resource capacity consumed (CPU, memory, disk,
    connections).
  - **S**aturation: Work queued because the resource is fully utilized (queue depth,
    thread pool pending tasks).
  - **E**rrors: Resource-level error count (disk I/O errors, network packet drops,
    OOM kills).

  Apply USE to: CPU, memory, disk, network, database connection pools, thread pools,
  goroutine counts, and event loop lag.

- **Use histograms for latency, not averages.** Averages hide tail latency. Use
  histogram buckets or summary quantiles to capture the distribution. Prometheus
  histograms with appropriate bucket boundaries are the standard:
  ```
  http_request_duration_seconds_bucket{le="0.01"} 24054
  http_request_duration_seconds_bucket{le="0.025"} 33444
  http_request_duration_seconds_bucket{le="0.05"} 39123
  http_request_duration_seconds_bucket{le="0.1"} 41234
  http_request_duration_seconds_bucket{le="0.25"} 42000
  http_request_duration_seconds_bucket{le="+Inf"} 42100
  ```
- **Label metrics with care.** High-cardinality labels (user ID, request ID, full URL
  path) cause metric explosion. Use bounded labels: HTTP method, status code class
  (2xx, 4xx, 5xx), endpoint name (not path), service version:
  ```
  http_requests_total{method="POST", endpoint="/api/v1/orders", status="201"} 15420
  http_requests_total{method="POST", endpoint="/api/v1/orders", status="500"} 3
  ```
- **Emit business metrics alongside technical metrics.** Orders placed per minute,
  payments processed, search queries executed. These connect technical health to
  business outcomes and are often the first signal that something is wrong.
- **Use counters for totals, gauges for current values, histograms for distributions.**
  Do not use a gauge where a counter is appropriate (counters survive aggregation
  across instances; gauges do not).

> **Reference**: [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/),
> [RED Method (Tom Wilkie)](https://grafana.com/blog/2018/08/02/the-red-method-how-to-instrument-your-services/),
> [USE Method (Brendan Gregg)](https://www.brendangregg.com/usemethod.html),
> [Google SRE Book, Chapter 6: Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)

## 4. Alerting

- **Alert on symptoms, not causes.** Alert when the user experience is degraded
  (high error rate, high latency), not when an internal component is unhealthy
  (one pod restarting, CPU spike). Component health is a dashboard concern; user
  impact is an alerting concern.
- **Drive alerts from SLOs.** Define Service Level Objectives with error budgets
  and alert when the burn rate threatens the budget:
  - **SLO**: 99.9% of requests succeed within 500ms over a 30-day window.
  - **Error budget**: 0.1% of requests = ~43 minutes of downtime per 30 days.
  - **Fast burn alert**: Error rate is 14.4x the budget rate for 5 minutes (exhausts
    budget in ~2 hours). Page immediately.
  - **Slow burn alert**: Error rate is 6x the budget rate for 30 minutes (exhausts
    budget in ~5 hours). Ticket or Slack notification.

  This approach (from the Google SRE Workbook, Chapter 5) ensures you alert on
  conditions that actually threaten your commitments, not transient blips.

- **Every alert must have a runbook.** An alert without a runbook is a context-free
  page that wastes the on-call engineer's time. Link the runbook URL directly in the
  alert annotation.
- **Alert fatigue kills reliability.** If an alert fires more than once a week and
  the response is "ignore it" or "it resolved itself," the alert is broken. Either
  fix the underlying issue, tune the threshold, or delete the alert.
- **Use multi-window, multi-burn-rate alerting** to balance detection speed and
  false positive rate. The Google SRE Workbook recommends checking both a short
  window (5 min) and a long window (1 hour) before paging:
  ```yaml
  # Prometheus alerting rule example (multi-burn-rate)
  - alert: HighErrorRate
    expr: |
      (
        job:sli_errors:ratio_rate5m{job="order-api"} > (14.4 * 0.001)
        and
        job:sli_errors:ratio_rate1h{job="order-api"} > (14.4 * 0.001)
      )
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Order API error budget burn rate critical"
      runbook: "https://runbooks.internal/order-api/high-error-rate"
  ```
- **Classify alert severity consistently:**

  | Severity | Response | Example |
  |----------|----------|---------|
  | Critical (page) | Immediate human response required | SLO burn rate critical, data loss risk |
  | Warning (ticket) | Investigate within business hours | Slow burn rate, disk usage approaching threshold |
  | Info (dashboard) | No action required; situational awareness | Deployment completed, scaling event |

> **Reference**: [Google SRE Workbook, Chapter 5: Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/),
> [Google SRE Book, Chapter 6: Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/),
> [Prometheus Alerting Best Practices](https://prometheus.io/docs/practices/alerting/)

## 5. Dashboards

- **Build dashboards in layers:**
  - **Layer 1 -- Service overview**: RED metrics (rate, errors, duration) for every
    service. This is the first dashboard anyone opens during an incident.
  - **Layer 2 -- Component detail**: Database performance, cache hit rates, queue
    depths, connection pool utilization. Navigate here from Layer 1 when investigating
    a specific component.
  - **Layer 3 -- Debug**: Individual request traces, slow query logs, pod-level
    resource usage. Navigate here from Layer 2 for root cause analysis.
- **The Four Golden Signals** (Google SRE Book) should be visible on every Layer 1
  dashboard: latency, traffic, errors, saturation.
- **Time-align all panels.** When an operator drags the time range on one panel, all
  panels must update. Misaligned time windows cause incorrect correlations.
- **Include deployment markers.** Overlay deployment events on metric charts so
  operators can correlate behavior changes with releases.
- **Use consistent units and scales.** Latency in milliseconds (not mixed ms/s),
  data sizes in bytes/KiB/MiB (not mixed), percentages from 0-100 (not 0-1).
- **Dashboard-as-code.** Store dashboard definitions in version control (Grafana
  JSON, Terraform, Pulumi). Manual dashboard edits in the UI drift from the
  canonical definition and are lost during infrastructure rebuilds.

> **Reference**: [Google SRE Book, Chapter 6: Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/),
> [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/)

## 6. Health Checks

- **Implement two health endpoints:**
  - **Liveness** (`/health/live`): Is the process running and not deadlocked? This
    endpoint should return `200 OK` with minimal logic. Kubernetes uses this to
    decide whether to restart the container. A failed liveness probe causes a pod
    restart, so do NOT include dependency checks here -- a database outage should not
    cause cascading pod restarts.
  - **Readiness** (`/health/ready`): Can the service accept traffic? Check critical
    dependencies: database connectivity, cache connectivity, required configuration
    loaded. Kubernetes uses this to decide whether to route traffic to the pod. A
    failed readiness probe removes the pod from the load balancer but does not
    restart it.
- **Return structured health responses:**
  ```json
  {
      "status": "UP",
      "checks": {
          "database": { "status": "UP", "latencyMs": 2 },
          "cache": { "status": "UP", "latencyMs": 1 },
          "config": { "status": "UP" }
      }
  }
  ```
- **Set appropriate timeouts on health check dependencies.** A health check that
  waits 30 seconds for a database response will cause the orchestrator to believe
  the service is hung. Use aggressive timeouts (1-3 seconds) and treat a timeout
  as a failure.
- **Startup probes for slow-starting services.** If your service takes 30+ seconds
  to initialize (JVM warm-up, large cache load, schema migration), use Kubernetes
  startup probes to prevent premature liveness probe failures:
  ```yaml
  startupProbe:
    httpGet:
      path: /health/live
      port: 8080
    failureThreshold: 30
    periodSeconds: 10  # up to 300 seconds to start
  livenessProbe:
    httpGet:
      path: /health/live
      port: 8080
    periodSeconds: 10
    failureThreshold: 3
  readinessProbe:
    httpGet:
      path: /health/ready
      port: 8080
    periodSeconds: 5
    failureThreshold: 3
  ```
- **Do not expose sensitive information in health endpoints.** Health checks should
  not reveal database hostnames, internal IP addresses, or version numbers to
  unauthenticated callers. Protect detailed health responses behind authentication
  or limit them to internal network access.

> **Reference**: [Kubernetes Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/),
> [MicroProfile Health Specification](https://microprofile.io/specifications/microprofile-health/),
> [Spring Boot Actuator Health](https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html#actuator.endpoints.health)

## 7. Review Checklist

- [ ] All logs are structured JSON with timestamp, level, message, service name, and correlation ID
- [ ] Correlation IDs propagate across all service boundaries (HTTP, messaging, background jobs)
- [ ] Log levels are semantically correct (error/warn/info/debug)
- [ ] No secrets, PII, or tokens appear in log output
- [ ] Distributed tracing uses OpenTelemetry with W3C Trace Context propagation
- [ ] Auto-instrumentation is enabled for HTTP, database, and messaging frameworks
- [ ] Custom spans exist for business-critical operations with domain-specific attributes
- [ ] Trace sampling strategy is defined and appropriate for production traffic volume
- [ ] RED metrics (rate, errors, duration) are emitted for every request-handling service
- [ ] USE metrics (utilization, saturation, errors) are emitted for infrastructure resources
- [ ] Latency is measured with histograms, not averages
- [ ] Metric labels are bounded (no high-cardinality labels)
- [ ] Alerts are symptom-based and SLO-driven, not cause-based
- [ ] Every alert links to a runbook
- [ ] Multi-window, multi-burn-rate alerting is used for SLO-based alerts
- [ ] Dashboards follow the three-layer model (overview, component detail, debug)
- [ ] Dashboard definitions are stored in version control
- [ ] Liveness and readiness health endpoints are implemented with correct semantics
- [ ] Health check dependency timeouts are aggressive (1-3 seconds)
- [ ] Startup probes are configured for slow-starting services
