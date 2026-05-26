"""ConfigBundle — loads every config file, cross-validates, exposes queries.

Usage::

    from scripts.lib.config import get_bundle
    bundle = get_bundle()                  # cached singleton
    bundle.user.first_name                  # → "Sujeet"
    bundle.repos.by_id("repo:ecomm-ssr")    # → Repo
    bundle.alerts_channels_for("service:quince-site")  # → list[Channel]

Reload after editing files::

    from scripts.lib.config import reset_bundle, get_bundle
    reset_bundle()
    bundle = get_bundle()

Tests can also pass an explicit config root::

    bundle = ConfigBundle.load(config_root=tmp_path)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional, TypeVar

from pydantic import BaseModel, ValidationError

from .io import read_json5, read_json5_or_none
from .models import (
    AtlassianFile, BitbucketConnector, Channel, ChannelsFile, CoreConfig,
    Dashboard, DashboardsFile, DatadogApp, DatadogAppsFile, DatadogConnector,
    GithubConnector, MixpanelConnector, MixpanelFile, MixpanelProject,
    RelationsFile, Repo, ReposFile, Service, ServicesFile, SlackConnector,
    SnowflakeConnector, SnowflakeFile, StatsigConnector, StatsigFile,
    StatsigProject, Team, TeamsFile, Workspace, WorkspacesFile,
)
from .paths import adk_config_home


class ConfigError(Exception):
    """Raised when a config file is missing, malformed, or fails cross-validation."""


T = TypeVar("T", bound=BaseModel)


# ---------------------------------------------------------------------------
# Catalog wrappers — small typed views over the entity lists
# ---------------------------------------------------------------------------


class _ByIdCatalog:
    """list[T] indexed by .id with helpful errors."""

    def __init__(self, items: list[Any], kind: str):
        self._items = items
        self._by_id = {x.id: x for x in items}
        self._kind = kind

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def all(self) -> list[Any]:
        return list(self._items)

    def by_id(self, id_: str) -> Any:
        try:
            return self._by_id[id_]
        except KeyError:
            raise ConfigError(
                f"unknown {self._kind} id: {id_!r}. Known: "
                f"{sorted(self._by_id)[:5]}{'...' if len(self._by_id) > 5 else ''}"
            )

    def by_id_or_none(self, id_: str) -> Any | None:
        return self._by_id.get(id_)

    def by_name(self, name: str) -> Any | None:
        """Best-effort lookup by .name (case-insensitive)."""
        name_lower = name.lower()
        for x in self._items:
            if getattr(x, "name", "").lower() == name_lower:
                return x
        return None

    def filter(self, **kwargs) -> list[Any]:
        out = []
        for x in self._items:
            if all(getattr(x, k, None) == v for k, v in kwargs.items()):
                out.append(x)
        return out


# ---------------------------------------------------------------------------
# Bundle
# ---------------------------------------------------------------------------


@dataclass
class _Connectors:
    datadog: DatadogConnector
    slack: SlackConnector
    statsig: StatsigConnector
    mixpanel: MixpanelConnector
    snowflake: SnowflakeConnector
    atlassian: dict       # AtlassianConnector + lists
    github: GithubConnector
    bitbucket: BitbucketConnector


@dataclass
class ConfigBundle:
    """Validated, cross-checked adk config — read-only at runtime."""

    core: CoreConfig
    workspaces: _ByIdCatalog       # of Workspace
    teams: _ByIdCatalog            # of Team
    repos: _ByIdCatalog            # of Repo
    services: _ByIdCatalog         # of Service
    channels: _ByIdCatalog         # of Channel
    dashboards: _ByIdCatalog       # of Dashboard
    datadog_apps: _ByIdCatalog     # of DatadogApp
    statsig_projects: _ByIdCatalog # of StatsigProject
    mixpanel_projects: _ByIdCatalog # of MixpanelProject
    snowflake: SnowflakeFile
    atlassian: AtlassianFile
    connectors: _Connectors
    relations: list                # list[Relation]
    config_root: Path = field(default_factory=adk_config_home)

    # -- shortcuts for the hot path --

    @property
    def user(self):
        return self.core.user

    @property
    def org(self):
        return self.core.org

    @property
    def bot(self):
        return self.core.bot

    @property
    def defaults(self):
        return self.core.defaults

    # -- graph queries --

    def team_for(self, *, repo_id: str | None = None,
                 service_id: str | None = None) -> Team | None:
        if repo_id:
            r = self.repos.by_id_or_none(repo_id)
            return self.teams.by_id_or_none(r.team) if r else None
        if service_id:
            s = self.services.by_id_or_none(service_id)
            return self.teams.by_id_or_none(s.team) if s else None
        return None

    def services_for_repo(self, repo_id: str) -> list[Service]:
        r = self.repos.by_id_or_none(repo_id)
        if not r:
            return []
        return [self.services.by_id(sid) for sid in r.services
                if self.services.by_id_or_none(sid)]

    def repo_for_service(self, service_id: str) -> Repo | None:
        s = self.services.by_id_or_none(service_id)
        if s and s.repo:
            return self.repos.by_id_or_none(s.repo)
        return None

    def alerts_channels_for(self, service_id: str) -> list[Channel]:
        s = self.services.by_id_or_none(service_id)
        if not s:
            return []
        return [self.channels.by_id(cid) for cid in s.alert_channels
                if self.channels.by_id_or_none(cid)]

    def channels_by_purpose(self, purpose: str) -> list[Channel]:
        return self.channels.filter(purpose=purpose)

    def datadog_app_for_service(self, service_id: str,
                                *, type: str = "apm") -> DatadogApp | None:
        s = self.services.by_id_or_none(service_id)
        if not s:
            return None
        ref = s.datadog_app if type == "apm" else s.datadog_rum_app
        return self.datadog_apps.by_id_or_none(ref) if ref else None

    def neighbors(self, entity_id: str) -> list[str]:
        """1-hop neighbors via relations.json5 + primary edges on entities."""
        out: set[str] = set()
        for r in self.relations:
            if r.from_ == entity_id:
                out.add(r.to)
            if r.to == entity_id:
                out.add(r.from_)
        # primary edges
        if entity_id.startswith("repo:"):
            r = self.repos.by_id_or_none(entity_id)
            if r:
                if r.team:
                    out.add(r.team)
                out.update(r.services)
                if r.statsig_project:
                    out.add(r.statsig_project)
                if r.mixpanel_project:
                    out.add(r.mixpanel_project)
        elif entity_id.startswith("service:"):
            s = self.services.by_id_or_none(entity_id)
            if s:
                if s.team:
                    out.add(s.team)
                if s.repo:
                    out.add(s.repo)
                if s.datadog_app:
                    out.add(s.datadog_app)
                if s.datadog_rum_app:
                    out.add(s.datadog_rum_app)
                out.update(s.alert_channels)
        elif entity_id.startswith("team:"):
            t = self.teams.by_id_or_none(entity_id)
            if t:
                if t.parent:
                    out.add(t.parent)
                out.update(t.owns_channels)
                out.update(t.owns_repos)
        return sorted(out)

    # -- bot helpers --

    def bot_footer(self) -> str:
        return self.bot.footer_template.format(first_name=self.user.first_name)

    def bot_name(self) -> str:
        return self.bot.name_template.format(first_name=self.user.first_name)

    # -- workspace helpers --

    def primary_workspace(self) -> Workspace:
        return self.workspaces.by_id(f"workspace:{self.core.org.primary_workspace}")

    def workspace_for_repo(self, repo_id: str) -> Workspace | None:
        r = self.repos.by_id_or_none(repo_id)
        if not r:
            return None
        return self.workspaces.by_id_or_none(r.workspace)

    # ---------------- loading ----------------

    @classmethod
    def load(cls, config_root: Path | None = None) -> "ConfigBundle":
        """Read every file under config_root and cross-validate."""
        root = config_root or adk_config_home()
        if not root.exists():
            raise ConfigError(f"config root does not exist: {root}")

        core = _load_required(root / "core.json5", CoreConfig)
        workspaces = _load_optional(root / "workspaces.json5",
                                    WorkspacesFile, "workspaces")
        teams = _load_optional(root / "teams.json5", TeamsFile, "teams")
        repos = _load_optional(root / "repos.json5", ReposFile, "repos")
        services = _load_optional(root / "services.json5",
                                  ServicesFile, "services")
        channels = _load_optional(root / "channels.json5",
                                  ChannelsFile, "channels")
        dashboards = _load_optional(root / "dashboards.json5",
                                    DashboardsFile, "dashboards")
        datadog_apps = _load_optional(root / "datadog-apps.json5",
                                      DatadogAppsFile, "datadog_apps")
        statsig_file = _load_optional(root / "statsig.json5",
                                      StatsigFile, "projects")
        mixpanel_file = _load_optional(root / "mixpanel.json5",
                                       MixpanelFile, "projects")
        snowflake = _load_required(root / "snowflake.json5", SnowflakeFile,
                                   allow_missing=True,
                                   missing_default=lambda: SnowflakeFile(
                                       account="", default_warehouse="",
                                       default_role="", default_database="",
                                   ))
        atlassian = _load_required(root / "atlassian.json5", AtlassianFile,
                                   allow_missing=True,
                                   missing_default=AtlassianFile)
        relations = _load_optional(root / "relations.json5",
                                   RelationsFile, "relations")

        # Connectors
        connectors = _Connectors(
            datadog=_load_required(root / "connectors/datadog.json5",
                                   DatadogConnector,
                                   allow_missing=True,
                                   missing_default=DatadogConnector),
            slack=_load_required(root / "connectors/slack.json5",
                                 SlackConnector,
                                 allow_missing=True,
                                 missing_default=SlackConnector),
            statsig=_load_required(root / "connectors/statsig.json5",
                                   StatsigConnector,
                                   allow_missing=True,
                                   missing_default=StatsigConnector),
            mixpanel=_load_required(root / "connectors/mixpanel.json5",
                                    MixpanelConnector,
                                    allow_missing=True,
                                    missing_default=MixpanelConnector),
            snowflake=_load_required(root / "connectors/snowflake.json5",
                                     SnowflakeConnector,
                                     allow_missing=True,
                                     missing_default=SnowflakeConnector),
            atlassian={},   # Atlassian connector merged with atlassian.json5
            github=_load_required(root / "connectors/github.json5",
                                  GithubConnector,
                                  allow_missing=True,
                                  missing_default=GithubConnector),
            bitbucket=_load_required(root / "connectors/bitbucket.json5",
                                     BitbucketConnector,
                                     allow_missing=True,
                                     missing_default=BitbucketConnector),
        )

        bundle = cls(
            core=core,
            workspaces=_ByIdCatalog(workspaces, "workspace"),
            teams=_ByIdCatalog(teams, "team"),
            repos=_ByIdCatalog(repos, "repo"),
            services=_ByIdCatalog(services, "service"),
            channels=_ByIdCatalog(channels, "channel"),
            dashboards=_ByIdCatalog(dashboards, "dashboard"),
            datadog_apps=_ByIdCatalog(datadog_apps, "datadog_app"),
            statsig_projects=_ByIdCatalog(statsig_file, "statsig_project"),
            mixpanel_projects=_ByIdCatalog(mixpanel_file, "mixpanel_project"),
            snowflake=snowflake,
            atlassian=atlassian,
            connectors=connectors,
            relations=relations,
            config_root=root,
        )
        bundle._cross_validate()
        return bundle

    # ---------------- cross-validation ----------------

    def _cross_validate(self) -> None:
        errors: list[str] = []

        def _check_ref(field_loc: str, target: str | None,
                       catalog: _ByIdCatalog, expected_kind: str):
            if target is None:
                return
            if not target.startswith(expected_kind + ":"):
                errors.append(
                    f"{field_loc}: expected {expected_kind}:* (got {target!r})"
                )
                return
            if catalog.by_id_or_none(target) is None:
                errors.append(
                    f"{field_loc}: unknown {expected_kind} {target!r}"
                )

        # workspaces
        primary_ws = f"workspace:{self.core.org.primary_workspace}"
        if self.workspaces.by_id_or_none(primary_ws) is None and len(self.workspaces):
            errors.append(
                f"core.org.primary_workspace: unknown workspace "
                f"{self.core.org.primary_workspace!r}"
            )

        # teams: parent must exist; no cycles
        for t in self.teams:
            _check_ref(f"teams[{t.id}].parent", t.parent, self.teams, "team")
            for ch in t.owns_channels:
                _check_ref(f"teams[{t.id}].owns_channels", ch,
                           self.channels, "channel")
            for r in t.owns_repos:
                _check_ref(f"teams[{t.id}].owns_repos", r, self.repos, "repo")
        for t in self.teams:
            if self._has_team_cycle(t.id):
                errors.append(f"teams[{t.id}]: cycle detected in parent chain")

        # repos
        for r in self.repos:
            _check_ref(f"repos[{r.id}].workspace", r.workspace,
                       self.workspaces, "workspace")
            _check_ref(f"repos[{r.id}].team", r.team, self.teams, "team")
            for sid in r.services:
                _check_ref(f"repos[{r.id}].services", sid,
                           self.services, "service")
            _check_ref(f"repos[{r.id}].statsig_project", r.statsig_project,
                       self.statsig_projects, "statsig_project")
            _check_ref(f"repos[{r.id}].mixpanel_project", r.mixpanel_project,
                       self.mixpanel_projects, "mixpanel_project")
            for ds in r.downstream_repos:
                _check_ref(f"repos[{r.id}].downstream_repos", ds,
                           self.repos, "repo")

        # services
        for s in self.services:
            _check_ref(f"services[{s.id}].team", s.team, self.teams, "team")
            _check_ref(f"services[{s.id}].repo", s.repo, self.repos, "repo")
            _check_ref(f"services[{s.id}].datadog_app", s.datadog_app,
                       self.datadog_apps, "datadog_app")
            _check_ref(f"services[{s.id}].datadog_rum_app", s.datadog_rum_app,
                       self.datadog_apps, "datadog_app")
            for cid in s.alert_channels:
                _check_ref(f"services[{s.id}].alert_channels", cid,
                           self.channels, "channel")
                ch = self.channels.by_id_or_none(cid)
                if ch and ch.purpose != "alerts":
                    errors.append(
                        f"services[{s.id}].alert_channels: {cid} has "
                        f"purpose={ch.purpose!r}, expected 'alerts'"
                    )
            for cid in s.deploy_channels:
                _check_ref(f"services[{s.id}].deploy_channels", cid,
                           self.channels, "channel")
                ch = self.channels.by_id_or_none(cid)
                if ch and ch.purpose != "release":
                    errors.append(
                        f"services[{s.id}].deploy_channels: {cid} has "
                        f"purpose={ch.purpose!r}, expected 'release'"
                    )

        # channels
        for c in self.channels:
            for sid in c.routes_alerts_for:
                _check_ref(f"channels[{c.id}].routes_alerts_for", sid,
                           self.services, "service")
            for sid in c.routes_deploys_for:
                _check_ref(f"channels[{c.id}].routes_deploys_for", sid,
                           self.services, "service")
            for tid in c.member_teams:
                _check_ref(f"channels[{c.id}].member_teams", tid,
                           self.teams, "team")
            _check_ref(f"channels[{c.id}].owner_team", c.owner_team,
                       self.teams, "team")

        # dashboards
        for d in self.dashboards:
            _check_ref(f"dashboards[{d.id}].team", d.team, self.teams, "team")
            for sid in d.services:
                _check_ref(f"dashboards[{d.id}].services", sid,
                           self.services, "service")

        # datadog apps
        for a in self.datadog_apps:
            _check_ref(f"datadog_apps[{a.id}].team", a.team, self.teams, "team")
            _check_ref(f"datadog_apps[{a.id}].service", a.service,
                       self.services, "service")

        # statsig / mixpanel
        for sp in self.statsig_projects:
            for rid in sp.repos:
                _check_ref(f"statsig.projects[{sp.id}].repos", rid,
                           self.repos, "repo")
        for mp in self.mixpanel_projects:
            for rid in mp.repos:
                _check_ref(f"mixpanel.projects[{mp.id}].repos", rid,
                           self.repos, "repo")

        # relations
        for i, rel in enumerate(self.relations):
            kind_from = rel.from_.split(":", 1)[0]
            kind_to = rel.to.split(":", 1)[0]
            for endpoint, val in (("from", rel.from_), ("to", rel.to)):
                cat = self._catalog_for(val.split(":", 1)[0])
                if cat is None:
                    continue   # unknown-kind endpoints are tolerated
                if cat.by_id_or_none(val) is None:
                    errors.append(
                        f"relations[{i}].{endpoint}: unknown entity {val!r}"
                    )

        if errors:
            msg = "config cross-validation failed:\n  - " + "\n  - ".join(errors)
            raise ConfigError(msg)

    def _catalog_for(self, kind: str) -> _ByIdCatalog | None:
        return {
            "team": self.teams,
            "repo": self.repos,
            "service": self.services,
            "channel": self.channels,
            "workspace": self.workspaces,
            "dashboard": self.dashboards,
            "datadog_app": self.datadog_apps,
            "statsig_project": self.statsig_projects,
            "mixpanel_project": self.mixpanel_projects,
        }.get(kind)

    def _has_team_cycle(self, start: str) -> bool:
        seen = {start}
        cur = self.teams.by_id_or_none(start)
        while cur and cur.parent:
            if cur.parent in seen:
                return True
            seen.add(cur.parent)
            cur = self.teams.by_id_or_none(cur.parent)
        return False


# ---------------------------------------------------------------------------
# File-loading helpers
# ---------------------------------------------------------------------------


def _format_validation_error(path: Path, err: ValidationError) -> str:
    lines = [f"{path}: schema validation failed:"]
    for e in err.errors():
        loc = ".".join(str(x) for x in e["loc"])
        lines.append(f"  - {loc}: {e['msg']} (got {e.get('input')!r})")
    return "\n".join(lines)


def _load_required(path: Path, model: type[T],
                   allow_missing: bool = False,
                   missing_default=None) -> T:
    if not path.exists():
        if allow_missing:
            return missing_default() if callable(missing_default) else missing_default
        raise ConfigError(
            f"required config file missing: {path}. "
            f"Run `adk setup --init` or copy from shared/templates/config-v5/."
        )
    data = read_json5(path)
    try:
        return model.model_validate(data)
    except ValidationError as e:
        raise ConfigError(_format_validation_error(path, e)) from e


def _load_optional(path: Path, file_model: type[BaseModel],
                   list_attr: str) -> list:
    """Load a file whose top level is ``{<list_attr>: [...]}``; return [] if absent."""
    if not path.exists():
        return []
    data = read_json5(path)
    try:
        wrapper = file_model.model_validate(data)
    except ValidationError as e:
        raise ConfigError(_format_validation_error(path, e)) from e
    return list(getattr(wrapper, list_attr))


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


_bundle: Optional[ConfigBundle] = None


def get_bundle() -> ConfigBundle:
    """Return the cached ConfigBundle, loading on first call."""
    global _bundle
    if _bundle is None:
        _bundle = ConfigBundle.load()
    return _bundle


def reset_bundle() -> None:
    """Clear the cache (for tests, or after editing config files)."""
    global _bundle
    _bundle = None


__all__ = ["ConfigBundle", "ConfigError", "get_bundle", "reset_bundle"]
