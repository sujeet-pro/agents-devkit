"""adk config v5 — schema-validated JSON5 config loader.

Public API:
    from scripts.lib.config import get_bundle, ConfigBundle

    bundle = get_bundle()
    bundle.user.first_name
    bundle.bot.footer_template
    bundle.repos.by_id("repo:ecomm-ssr")
    bundle.team_for(repo_id="repo:ecomm-ssr")
    bundle.alerts_channels_for(service_id="service:quince-site")

Files loaded from $ADK_CONFIG_HOME:
    core.json5, workspaces.json5, teams.json5, repos.json5, services.json5,
    channels.json5, dashboards.json5, tables.json5, statsig.json5,
    mixpanel.json5, snowflake.json5, relations.json5, connectors/*.json5

See plan.md and shared/config-schema.md for layout details.
"""

from .loader import ConfigBundle, ConfigError, get_bundle, reset_bundle
from .models import (
    AtlassianConnector, AtlassianFile, BitbucketConnector, BotIdentity,
    Channel, ChannelPurpose, ChannelsFile, ConfluenceSpace, CoreConfig,
    Dashboard, DashboardsFile, DatadogApp, DatadogAppsFile, DatadogConnector,
    DatadogQuery, Defaults, DocumentDefaults, GithubConnector,
    ImplementDefaults, InvestigateDefaults, JiraProject, MixpanelConnector,
    MixpanelFile, MixpanelFunnel, MixpanelProject, Org, QuestionFirstDefaults,
    Relation, RelationKind, RelationsFile, Repo, RepoCommands, RepoModule,
    ReposFile, ReviewDefaults, Service, ServiceSLO, ServicesFile,
    SlackConnector, SlackPRReviewConfig, SlackPRReviewReminder,
    SnowflakeConnector, SnowflakeFile, SnowflakePIIRules, SnowflakeTable,
    StatsigConnector, StatsigExperiment, StatsigFile, StatsigGateHygiene,
    StatsigProject, SyncDefaults, Team, TeamMember, TeamsFile, User,
    Workspace, WorkspacesFile,
)
from .io import comment_header, read_json5, read_json5_or_none, write_json5
from .paths import (
    adk_config_home, adk_data_home, adk_learning_home, adk_logs_home,
    adk_memory_home, adk_metadata_home, adk_repos_home, adk_skill_home,
    config_path, schema_dir,
)
from .cli_settings import (
    get_adk_cli, load_adk_cli,
    load_identity_cache, load_tui_prefs,
    save_identity_cache, save_tui_prefs,
)

__all__ = [
    # loader
    "ConfigBundle", "ConfigError", "get_bundle", "reset_bundle",
    # io
    "comment_header", "read_json5", "read_json5_or_none", "write_json5",
    # paths
    "adk_config_home", "adk_data_home", "adk_learning_home", "adk_logs_home",
    "adk_memory_home", "adk_metadata_home", "adk_repos_home",
    "adk_skill_home", "config_path", "schema_dir",
    # CLI settings + small caches
    "get_adk_cli", "load_adk_cli",
    "load_identity_cache", "save_identity_cache",
    "load_tui_prefs", "save_tui_prefs",
    # models — identity / core
    "User", "Org", "BotIdentity", "CoreConfig", "Defaults",
    "QuestionFirstDefaults", "ImplementDefaults", "ReviewDefaults",
    "InvestigateDefaults", "DocumentDefaults", "SyncDefaults",
    # models — workspaces / teams / repos / services / channels
    "Workspace", "WorkspacesFile",
    "Team", "TeamMember", "TeamsFile",
    "Repo", "RepoCommands", "RepoModule", "ReposFile",
    "Service", "ServiceSLO", "ServicesFile",
    "Channel", "ChannelPurpose", "ChannelsFile",
    # models — datadog / dashboards
    "DatadogApp", "DatadogAppsFile", "DatadogQuery",
    "Dashboard", "DashboardsFile",
    # models — statsig / mixpanel / snowflake
    "StatsigExperiment", "StatsigGateHygiene", "StatsigProject", "StatsigFile",
    "MixpanelFunnel", "MixpanelProject", "MixpanelFile",
    "SnowflakePIIRules", "SnowflakeTable", "SnowflakeFile",
    # models — atlassian
    "JiraProject", "ConfluenceSpace", "AtlassianFile",
    # models — connectors
    "AtlassianConnector", "BitbucketConnector", "DatadogConnector",
    "GithubConnector", "MixpanelConnector", "SlackConnector",
    "SlackPRReviewConfig", "SlackPRReviewReminder", "SnowflakeConnector",
    "StatsigConnector",
    # models — relations
    "Relation", "RelationKind", "RelationsFile",
]
