"""pr_pipeline — pipelined per-stage scheduler for /adk-pr-review.

Six stages (import / sync / index / review / validate / post), each with its
own semaphore so different PRs can be at different stages concurrently while
the bottleneck stage (index, default 1) stays slot-limited.

Entry point:
  from pr_pipeline.scheduler import run, Semaphores
  from pr_pipeline.state import PRState
"""
