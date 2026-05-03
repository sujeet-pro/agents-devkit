---
# ~/.config/adk/review.md
# Review conventions. Used by adk-review:* and adk-review:audit-*.

severity_bar:
  blocker:
    - secret_in_diff
    - sql_injection
    - auth_bypass
    - data_loss_risk
    - protected_branch_force_push
  critical:
    - n_plus_one_query
    - unbounded_loop
    - silent_exception_swallow
    - missing_authz_check
  should_have:
    - missing_test_for_new_branch
    - hardcoded_value_should_be_config
    - inconsistent_naming_with_repo
ignore_in_repos:
  acme/legacy-monolith:
    - style_consistency
    - test_coverage_threshold
auto_post_comments_to_pr: true        # only honored under --auto
post_only_blockers_under_auto: false  # if true, only Blocker/Critical posted under --auto
comment_template_overrides:
  # path -> template snippet (rare); see review-pr/references/pr-review-comment-format.md
---

# Notes

- Severity ladder: Blocker > Critical > Should Have > May Have > Nitpick > Question.
- Type axis: Issue / Suggestion / Praise / Question / Nitpick.
- Severity drives summary inclusion (Blockers + Critical listed; rest counted only) and verdict (any Blocker → request-changes).
- The `ignore_in_repos` map suppresses noise on legacy repos where certain checks are too noisy to be useful.
