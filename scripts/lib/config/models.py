"""pydantic v2 models for adk config v5.

ID convention: ``"kind:id"`` strings. Kinds:
    user, org, workspace, team, repo, service, channel, dashboard,
    datadog_app, statsig_project, mixpanel_project, snowflake_table,
    jira_project, confluence_space.

The loader (loader.py) validates that every cross-reference id resolves to a
known entity. Within models, references are plain strings — type-narrowing
happens at bundle-construction time.
"""

from __future__ import annotations

import re
from typing import Annotated, Literal, Optional

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

# ---------------------------------------------------------------------------
# Common base — strict (forbid extra fields)
# ---------------------------------------------------------------------------


class _Strict(BaseModel):
    """Forbid unknown fields. Catches typos at load time."""
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


_ID_RE = re.compile(r"^[a-z_]+:[A-Za-z0-9._\-/]+$")


def _ensure_id(kind: str):
    """Return a field validator that enforces ``<kind>:<rest>`` shape."""
    prefix = kind + ":"

    def _check(v: str) -> str:
        if not isinstance(v, str) or not v.startswith(prefix):
            raise ValueError(f"expected id starting with {prefix!r}, got {v!r}")
        if not _ID_RE.match(v):
            raise ValueError(f"malformed id {v!r}")
        return v
    return _check


def _ensure_any_id(v: str) -> str:
    if not isinstance(v, str) or not _ID_RE.match(v):
        raise ValueError(f"malformed id {v!r}; expected '<kind>:<id>'")
    return v


# Annotated id types — use these as field types to get auto-validation
WorkspaceId  = Annotated[str, AfterValidator(_ensure_id("workspace"))]
TeamId       = Annotated[str, AfterValidator(_ensure_id("team"))]
RepoId       = Annotated[str, AfterValidator(_ensure_id("repo"))]
ServiceId    = Annotated[str, AfterValidator(_ensure_id("service"))]
ChannelId    = Annotated[str, AfterValidator(_ensure_id("channel"))]
DashboardId  = Annotated[str, AfterValidator(_ensure_id("dashboard"))]
DatadogAppId = Annotated[str, AfterValidator(_ensure_id("datadog_app"))]
StatsigProjectId  = Annotated[str, AfterValidator(_ensure_id("statsig_project"))]
MixpanelProjectId = Annotated[str, AfterValidator(_ensure_id("mixpanel_project"))]
SnowflakeTableId  = Annotated[str, AfterValidator(_ensure_id("snowflake_table"))]
JiraProjectId     = Annotated[str, AfterValidator(_ensure_id("jira_project"))]
ConfluenceSpaceId = Annotated[str, AfterValidator(_ensure_id("confluence_space"))]
AnyEntityId       = Annotated[str, AfterValidator(_ensure_any_id)]


# ---------------------------------------------------------------------------
# Identity / org / bot
# ---------------------------------------------------------------------------


class User(_Strict):
    email: str
    first_name: str = Field(..., min_length=1)
    last_name: Optional[str] = None
    github_login: Optional[str] = None
    slack_user_id: Optional[str] = None
    bitbucket_username: Optional[str] = None


class Org(_Strict):
    name: str
    display_name: Optional[str] = None
    primary_workspace: str
    protected_branches: list[str] = ["main", "master", "release/*", "prod/*"]


class BotIdentity(_Strict):
    """Bot persona used when adk posts to Slack / GitHub / etc.

    The footer + name templates support ``{first_name}`` interpolation.
    Either ``icon_url`` or ``icon_emoji`` should be set (icon_url takes
    precedence if both are given).
    """
    icon_url: Optional[str] = None
    icon_emoji: Optional[str] = ":robot_face:"
    name_template: str = "{first_name}'s Automation"
    footer_template: str = "Sent by {first_name}'s Automation Setup"


# ---------------------------------------------------------------------------
# Defaults (per-skill knobs)
# ---------------------------------------------------------------------------


class QuestionFirstDefaults(_Strict):
    silent: bool = False


class ImplementDefaults(_Strict):
    scope: Literal["vertical-slice", "full", "spike"] = "vertical-slice"


class ReviewDefaults(_Strict):
    severity_bar: Literal["blocker", "critical", "should", "may", "nit"] = "should"


class InvestigateDefaults(_Strict):
    cross_source_required: bool = True
    confidence_threshold: Literal["low", "medium", "high"] = "medium"


class DocumentDefaults(_Strict):
    audience: Literal["engineer", "pm", "exec", "mixed"] = "engineer"
    tone: str = "calm-technical"


class SyncDefaults(_Strict):
    idempotency: Literal["match-by-id-then-title", "match-by-id-only"] = (
        "match-by-id-then-title"
    )


class Defaults(_Strict):
    protected_branches: list[str] = ["main", "master", "release/*", "prod/*"]
    question_first: QuestionFirstDefaults = QuestionFirstDefaults()
    package_manager_priority: list[str] = ["yarn", "npm", "gradle"]
    test_before_push: bool = True
    adk_implement: ImplementDefaults = Field(
        default_factory=ImplementDefaults, alias="adk-implement"
    )
    adk_review: ReviewDefaults = Field(
        default_factory=ReviewDefaults, alias="adk-review"
    )
    adk_investigate: InvestigateDefaults = Field(
        default_factory=InvestigateDefaults, alias="adk-investigate"
    )
    adk_document: DocumentDefaults = Field(
        default_factory=DocumentDefaults, alias="adk-document"
    )
    adk_sync: SyncDefaults = Field(default_factory=SyncDefaults, alias="adk-sync")


class CoreConfig(_Strict):
    schema_version: int = 5
    user: User
    org: Org
    bot: BotIdentity
    defaults: Defaults = Field(default_factory=Defaults)


# ---------------------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------------------


class Workspace(_Strict):
    id: WorkspaceId
    name: str
    role: Literal["work", "personal"]
    email: Optional[str] = None
    github_org: Optional[str] = None
    bitbucket_workspace: Optional[str] = None
    workspace_root: str
    protected_branches: list[str] = []


class WorkspacesFile(_Strict):
    workspaces: list[Workspace]


# ---------------------------------------------------------------------------
# Team
# ---------------------------------------------------------------------------


class TeamMember(_Strict):
    name: str
    email: Optional[str] = None
    github_login: Optional[str] = None
    slack_user_id: Optional[str] = None
    role: Optional[str] = None   # "lead", "ic", "manager", ...


class Team(_Strict):
    id: TeamId
    name: str
    parent: Optional[TeamId] = None
    aliases: dict[str, str] = Field(
        default_factory=dict,
        description="Per-tool name aliases. Keys: datadog, jira, github_team, "
                    "bitbucket_group, pagerduty, slack_handle. Values are the "
                    "tool-side identifier.",
    )
    description: Optional[str] = None
    members: list[TeamMember] = []
    owns_channels: list[ChannelId] = []
    owns_repos: list[RepoId] = []



class TeamsFile(_Strict):
    teams: list[Team]


# ---------------------------------------------------------------------------
# Repo
# ---------------------------------------------------------------------------


class RepoCommands(_Strict):
    """Repo-native commands. All optional; absent means "skill should ask"."""
    build: Optional[str] = None
    dev: Optional[str] = None
    test: Optional[str] = None
    typecheck: Optional[str] = None
    lint: Optional[str] = None
    e2e: Optional[str] = None
    format: Optional[str] = None


class RepoModule(_Strict):
    """A sub-component of a monorepo (e.g. one Gradle module)."""
    name: str
    role: Optional[str] = None
    service: Optional[str] = None   # service:<id> if this module deploys as a service
    downstreams: list[str] = []     # arbitrary tags or service ids


class Repo(_Strict):
    id: RepoId
    host: Literal["github", "bitbucket"]
    org: str                              # github org / bitbucket workspace
    name: str                             # repo slug
    workspace: WorkspaceId
    team: TeamId
    path: str                             # local checkout path (may use ~)
    primary_language: str
    secondary_languages: list[str] = []
    framework: Optional[str] = None
    package_manager: Optional[str] = None
    base_branch: str = "main"
    role_summary: Optional[str] = None
    commands: RepoCommands = Field(default_factory=RepoCommands)
    services: list[ServiceId] = []
    statsig_project: Optional[StatsigProjectId] = None
    mixpanel_project: Optional[MixpanelProjectId] = None
    downstream_repos: list[RepoId] = []
    modules: list[RepoModule] = []          # for monorepos
    notes: Optional[str] = None


class ReposFile(_Strict):
    repos: list[Repo]


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class ServiceSLO(_Strict):
    p95_ms: Optional[int] = None
    p99_ms: Optional[int] = None
    error_rate_pct: Optional[float] = None
    notes: Optional[str] = None


class Service(_Strict):
    id: ServiceId
    name: str
    team: TeamId
    repo: Optional[RepoId] = None
    module: Optional[str] = None           # name of repo module if monorepo
    runtime: Optional[str] = None          # next.js | spring-boot | aws-lambda | ...
    kube_deployment: Optional[str] = None
    health_endpoint: Optional[str] = None
    datadog_app: Optional[DatadogAppId] = None      # APM
    datadog_rum_app: Optional[DatadogAppId] = None  # RUM
    alert_channels: list[ChannelId] = []   # must reference purpose=alerts channels
    deploy_channels: list[ChannelId] = []  # must reference purpose=release channels
    slo: Optional[ServiceSLO] = None
    downstreams: list[str] = []            # service:<id> or free strings (redis, opensearch)
    span_family: Optional[str] = None      # e.g. "trace.web.request.*"
    notes: Optional[str] = None


class ServicesFile(_Strict):
    services: list[Service]


# ---------------------------------------------------------------------------
# Channel (Slack)
# ---------------------------------------------------------------------------


ChannelPurpose = Literal[
    "alerts", "review", "release", "incident", "oncall",
    "discussion", "design-review", "help", "automation",
]


class Channel(_Strict):
    id: ChannelId
    handle: str                            # "#datadog-alerts-bff"
    slack_id: Optional[str] = None         # "C0A6AGBDNUR" once known
    workspace: str = "lastbrand"
    purpose: ChannelPurpose
    routes_alerts_for: list[ServiceId] = []   # services whose alerts land here
    routes_deploys_for: list[ServiceId] = []  # services whose deploys post here
    member_teams: list[TeamId] = []           # teams whose members are here
    owner_team: Optional[TeamId] = None
    no_auto_post: bool = False
    description: Optional[str] = None

    @field_validator("handle")
    @classmethod
    def _check_handle(cls, v):
        if not v.startswith("#"):
            raise ValueError(f"channel handle must start with # (got {v!r})")
        return v


class ChannelsFile(_Strict):
    channels: list[Channel]


# ---------------------------------------------------------------------------
# Datadog application (APM service or RUM app)
# ---------------------------------------------------------------------------


class DatadogQuery(_Strict):
    type: Literal["metrics", "apm", "spans", "logs", "rum"]
    query: str
    description: Optional[str] = None


class DatadogApp(_Strict):
    id: DatadogAppId
    name: str                              # the @service tag value
    type: Literal["apm", "rum"]
    team: Optional[TeamId] = None
    team_tag: Optional[str] = None         # the @team tag value used in monitors
    service: Optional[ServiceId] = None    # the service this app observes (1:1)
    rum_application_id: Optional[str] = None  # for type=rum
    common_queries: dict[str, DatadogQuery] = {}
    slo_thresholds: dict[str, int] = {}     # {"p95_ms": 800}
    aliases: list[str] = []                # other names referring to this app
    notes: Optional[str] = None


class DatadogAppsFile(_Strict):
    datadog_apps: list[DatadogApp]


# ---------------------------------------------------------------------------
# Dashboard (Datadog / Looker / Mixpanel)
# ---------------------------------------------------------------------------


class Dashboard(_Strict):
    id: DashboardId
    host: Literal["datadog", "looker", "mixpanel"]
    host_id: str                           # the host-side dashboard id
    name: str
    url: Optional[str] = None
    role: Optional[str] = None             # one-liner description
    team: Optional[TeamId] = None
    services: list[ServiceId] = []         # services this dashboard tracks
    is_primary: bool = False               # the primary dashboard for its services


class DashboardsFile(_Strict):
    dashboards: list[Dashboard]


# ---------------------------------------------------------------------------
# Statsig
# ---------------------------------------------------------------------------


class StatsigExperiment(_Strict):
    id: str                                # experiment id (statsig-side)
    surface: Optional[str] = None
    hypothesis: Optional[str] = None
    kind: Optional[str] = None             # "A/B", "A/A", ...
    id_type: Optional[str] = None          # "userID" | "customer_id"


class StatsigGateHygiene(_Strict):
    total_gates: Optional[int] = None
    temporary: Optional[int] = None
    stale: Optional[int] = None
    note: Optional[str] = None


class StatsigProject(_Strict):
    id: StatsigProjectId
    project_name: str
    workspace_id: Optional[str] = None
    repos: list[RepoId] = []               # repos that emit exposures
    bucket_string_format: str = "<experiment_id>_<bucket_name>"
    common_experiments: list[StatsigExperiment] = []
    common_gates: list[str] = []
    recent_decisions: list[str] = []
    gate_hygiene: Optional[StatsigGateHygiene] = None
    id_types: dict[str, str] = {}          # {"primary": "userID", "alternate": "customer_id"}


class StatsigFile(_Strict):
    projects: list[StatsigProject]


# ---------------------------------------------------------------------------
# Mixpanel
# ---------------------------------------------------------------------------


class MixpanelFunnel(_Strict):
    id: str                                # mixpanel funnel id
    name: str
    role: Optional[str] = None


class MixpanelProject(_Strict):
    id: MixpanelProjectId
    project_id: str                        # mixpanel-side numeric id
    name: str                              # "Quince_Prod"
    workspace_id: Optional[str] = None
    role: str = "production"               # "production" | "staging" | "legacy"
    repos: list[RepoId] = []
    common_events: dict[str, list[str]] = {}     # category → events
    common_dashboards: list[DashboardId] = []
    common_funnels: list[MixpanelFunnel] = []
    identity: dict[str, str] = {}          # {"distinct_id_column": "$user_id", ...}
    common_event_properties: list[str] = []


class MixpanelFile(_Strict):
    projects: list[MixpanelProject]


# ---------------------------------------------------------------------------
# Snowflake
# ---------------------------------------------------------------------------


class SnowflakePIIRules(_Strict):
    block_substring: list[str] = []
    block_token_columns: list[str] = []


class SnowflakeTable(_Strict):
    id: SnowflakeTableId
    db: str
    db_schema: str = Field(..., alias="schema")
    name: str
    partition_filter: Optional[str] = None
    role: str
    use_case: str                          # "clickstream" | "orders" | "marketing" | ...
    pii_sensitive: bool = False
    notes: Optional[str] = None


class SnowflakeFile(_Strict):
    """Top-level snowflake.json5 — account-level config + table catalog."""
    account: str
    default_warehouse: str
    default_role: str
    default_database: str
    default_schema_search_path: list[str] = []
    pii_columns: SnowflakePIIRules = Field(default_factory=SnowflakePIIRules)
    conventions: list[str] = []
    tables: list[SnowflakeTable] = []


# ---------------------------------------------------------------------------
# Atlassian (Jira projects + Confluence spaces)
# ---------------------------------------------------------------------------


class JiraProject(_Strict):
    id: JiraProjectId
    key: str                               # "SF", "DS", "STORE"
    name: str
    team: Optional[TeamId] = None
    repos: list[RepoId] = []
    base_url: Optional[str] = None


class ConfluenceSpace(_Strict):
    id: ConfluenceSpaceId
    key: str
    name: str
    team: Optional[TeamId] = None
    documents_for: list[str] = []          # arbitrary entity ids (repo:* or service:*)


class AtlassianFile(_Strict):
    base_url: Optional[str] = None
    jira_projects: list[JiraProject] = []
    confluence_spaces: list[ConfluenceSpace] = []


# ---------------------------------------------------------------------------
# Connectors — auth + tool-global config only (no inventory)
# ---------------------------------------------------------------------------


class DatadogConnector(_Strict):
    site: str = "datadoghq.com"
    default_env: str = "prod"
    default_window: str = "last 1h"
    auth: dict[str, str] = Field(
        default_factory=lambda: {
            "api_key_env": "DATADOG_API_KEY_CRED",
            "app_key_env": "DATADOG_APP_KEY_CRED",
        },
    )
    clusters: list[str] = []
    environments: dict[str, list[str] | str] = {}


class SlackPRReviewReminder(_Strict):
    enabled: bool = True
    hours: int = 24
    tag_users: list[str] = ["author", "thread_starter"]
    message_template: str = (
        "PR review pending — please address the {pending_findings} open "
        "comments above. cc {author} {thread_starter}"
    )


class SlackPRReviewConfig(_Strict):
    """Subsection of slack connector: how `adk pr-scan` walks the workspace."""
    channels: list[str] = []               # ["#sf-web-pr-reviews", ...] — channel handles
    url_patterns: list[str] = []           # repo URL prefixes that count as PR links
    filter_mentioned_users: list[str] = []
    status_emoji: dict[str, Optional[str]] = {}
    scan_days_default: int = 30
    user_id: Optional[str] = None          # the user's Slack member ID
    reminder: SlackPRReviewReminder = Field(default_factory=SlackPRReviewReminder)
    channel_id_cache: dict[str, str] = {}  # handle → C-id


class SlackConnector(_Strict):
    workspace: str = "lastbrand"
    auth: dict[str, str] = Field(
        default_factory=lambda: {
            "bot_token_env": "SLACK_BOT_TOKEN_CRED",
            "user_token_env": "SLACK_USER_TOKEN_CRED",
        },
    )
    pr_reviews: SlackPRReviewConfig = Field(default_factory=SlackPRReviewConfig)


class StatsigConnector(_Strict):
    default_window: str = "last 7d"
    default_audit_window: str = "last 24h"
    auth: dict[str, str] = Field(
        default_factory=lambda: {
            "console_api_key_env": "STATSIG_CONSOLE_API_KEY_CRED",
            "server_sdk_key_env": "STATSIG_SERVER_SDK_KEY_CRED",
            "client_sdk_key_env": "STATSIG_CLIENT_SDK_KEY_CRED",
        },
    )
    environments: list[str] = ["development", "staging", "production"]


class MixpanelConnector(_Strict):
    default_window: str = "last 7d"
    default_project_id: Optional[str] = None
    auth: dict[str, str] = Field(default_factory=dict)


class SnowflakeConnector(_Strict):
    auth: dict[str, str] = Field(
        default_factory=lambda: {
            "account_env": "SNOWFLAKE_ACCOUNT",
            "user_env": "SNOWFLAKE_USER",
            "password_env": "SNOWFLAKE_PASSWORD_CRED",
        },
    )


class AtlassianConnector(_Strict):
    base_url: Optional[str] = None
    auth: dict[str, str] = Field(
        default_factory=lambda: {
            "token_env": "ATLASSIAN_API_TOKEN_CRED",
            "email_env": "ATLASSIAN_EMAIL",
        },
    )


class GithubConnector(_Strict):
    default_org: Optional[str] = None
    auth: dict[str, str] = Field(
        default_factory=lambda: {"token_env": "GH_PAT_CRED"},
    )


class BitbucketConnector(_Strict):
    default_workspace: Optional[str] = None
    auth: dict[str, str] = Field(
        default_factory=lambda: {
            "token_env": "BITBUCKET_TOKEN_CRED",
            "username_env": "BITBUCKET_USERNAME",
        },
    )


# ---------------------------------------------------------------------------
# Relations — cross-cutting graph edges
# ---------------------------------------------------------------------------


RelationKind = Literal[
    "owns", "parent_of", "hosts", "observed_by", "alerts_to",
    "uses_flags_from", "emits_events_to", "tracks", "documents",
    "used_for_use_case", "member_of", "chats_in", "deploys_to",
    "depends_on", "siblings_with",
]


class Relation(_Strict):
    from_: AnyEntityId = Field(..., alias="from")
    to: AnyEntityId
    kind: RelationKind
    notes: Optional[str] = None


class RelationsFile(_Strict):
    relations: list[Relation]


__all__ = [
    # base + helpers
    "User", "Org", "BotIdentity", "Defaults",
    "QuestionFirstDefaults", "ImplementDefaults", "ReviewDefaults",
    "InvestigateDefaults", "DocumentDefaults", "SyncDefaults",
    "CoreConfig",
    # workspaces / teams / repos / services / channels
    "Workspace", "WorkspacesFile",
    "TeamMember", "Team", "TeamsFile",
    "RepoCommands", "RepoModule", "Repo", "ReposFile",
    "ServiceSLO", "Service", "ServicesFile",
    "Channel", "ChannelPurpose", "ChannelsFile",
    # datadog / dashboards
    "DatadogQuery", "DatadogApp", "DatadogAppsFile",
    "Dashboard", "DashboardsFile",
    # statsig / mixpanel / snowflake
    "StatsigExperiment", "StatsigGateHygiene", "StatsigProject", "StatsigFile",
    "MixpanelFunnel", "MixpanelProject", "MixpanelFile",
    "SnowflakePIIRules", "SnowflakeTable", "SnowflakeFile",
    # atlassian
    "JiraProject", "ConfluenceSpace", "AtlassianFile",
    # connectors
    "DatadogConnector", "SlackConnector", "SlackPRReviewConfig",
    "SlackPRReviewReminder", "StatsigConnector", "MixpanelConnector",
    "SnowflakeConnector", "AtlassianConnector", "GithubConnector",
    "BitbucketConnector",
    # relations
    "Relation", "RelationKind", "RelationsFile",
]
