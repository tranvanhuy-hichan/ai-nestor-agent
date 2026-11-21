"""Services facade and dynamic module router for Nestor.

Supports backward-compatible imports from legacy paths (e.g. `from nestor.services import agent`,
`from nestor.services.agent import ...`, `from ..services import tools`) while organizing the codebase
into 8 clean domain subpackages:
- agent: Agent loop, prompt building, loop guard, compaction, checkpoints
- tools: Core tool registry and domain tools (browser, docs, office, media, computer...)
- mcp: Model Context Protocol client, catalog, registry, OAuth
- skills: Skills system, ClawHub, curator, authoring
- channels: Chat channels (Telegram, Zalo, Teams, pairing)
- memory: Knowledge base, memory index, vectorstore, embeddings
- system: Sessions, jobs, kanban, scheduler, auth, audit, providers, workfiles
- office: Office documents, CV, habits, exam shuffle, deliverable quality
"""
from __future__ import annotations

import sys
import types
from importlib import import_module
from typing import Any

MODULE_ROUTING: dict[str, str] = {
    # agent
    "agent": "nestor.services.agent",
    "chat_runner": "nestor.services.agent.chat_runner",
    "loop_guard": "nestor.services.agent.loop_guard",
    "truncation": "nestor.services.agent.truncation",
    "compaction": "nestor.services.agent.compaction",
    "checkpoints": "nestor.services.agent.checkpoints",
    "commands": "nestor.services.agent.commands",
    "limits": "nestor.services.agent.limits",
    "tokens": "nestor.services.agent.tokens",
    "brief": "nestor.services.agent.brief",
    "distill": "nestor.services.agent.distill",
    "api_run": "nestor.services.agent.api_run",
    # tools
    "tools": "nestor.services.tools",
    "tools_agents": "nestor.services.tools.tools_agents",
    "tools_browser": "nestor.services.tools.tools_browser",
    "tools_computer": "nestor.services.tools.tools_computer",
    "tools_cv": "nestor.services.tools.tools_cv",
    "tools_docs": "nestor.services.tools.tools_docs",
    "tools_kb": "nestor.services.tools.tools_kb",
    "tools_media": "nestor.services.tools.tools_media",
    "tools_memory": "nestor.services.tools.tools_memory",
    "tools_office": "nestor.services.tools.tools_office",
    "tools_pages": "nestor.services.tools.tools_pages",
    "tools_plan": "nestor.services.tools.tools_plan",
    "tools_quality": "nestor.services.tools.tools_quality",
    "tools_reconcile": "nestor.services.tools.tools_reconcile",
    # mcp
    "mcp": "nestor.services.mcp",
    "mcp_client": "nestor.services.mcp.mcp_client",
    "mcp_catalog": "nestor.services.mcp.mcp_catalog",
    "mcp_oauth": "nestor.services.mcp.mcp_oauth",
    "mcp_probe": "nestor.services.mcp.mcp_probe",
    "mcp_registry": "nestor.services.mcp.mcp_registry",
    # skills
    "skills": "nestor.services.skills",
    "skill_curator": "nestor.services.skills.skill_curator",
    "skill_picks": "nestor.services.skills.skill_picks",
    "clawhub": "nestor.services.skills.clawhub",
    "hub_install": "nestor.services.skills.hub_install",
    # channels
    "channels": "nestor.services.channels",
    "telegram_channel": "nestor.services.channels.telegram_channel",
    "zalo_channel": "nestor.services.channels.zalo_channel",
    "teams": "nestor.services.channels.teams",
    "pairing": "nestor.services.channels.pairing",
    # memory
    "memory": "nestor.services.memory",
    "knowledge": "nestor.services.memory.knowledge",
    "memory_index": "nestor.services.memory.memory_index",
    "vectorstore": "nestor.services.memory.vectorstore",
    "embeddings": "nestor.services.memory.embeddings",
    # system
    "system": "nestor.services.system",
    "sessions": "nestor.services.system.sessions",
    "jobs": "nestor.services.system.jobs",
    "kanban": "nestor.services.system.kanban",
    "scheduler": "nestor.services.system.scheduler",
    "backup": "nestor.services.system.backup",
    "auth": "nestor.services.system.auth",
    "audit": "nestor.services.system.audit",
    "heartbeat": "nestor.services.system.heartbeat",
    "hooks": "nestor.services.system.hooks",
    "notifications": "nestor.services.system.notifications",
    "plans": "nestor.services.system.plans",
    "providers": "nestor.services.system.providers",
    "cli_provider": "nestor.services.system.cli_provider",
    "rules": "nestor.services.system.rules",
    "security": "nestor.services.system.security",
    "usage": "nestor.services.system.usage",
    "workfiles": "nestor.services.system.workfiles",
    "browser": "nestor.services.system.browser",
    "terminal_child": "nestor.services.system.terminal_child",
    "assistants": "nestor.services.system.assistants",
    # office
    "office": "nestor.services.office",
    "vanban": "nestor.services.office.vanban",
    "cv_content": "nestor.services.office.cv_content",
    "docx_blocks": "nestor.services.office.docx_blocks",
    "exam_shuffle": "nestor.services.office.exam_shuffle",
    "habits": "nestor.services.office.habits",
    "pages": "nestor.services.office.pages",
    "deliverable_quality": "nestor.services.office.deliverable_quality",
}

PACKAGES = {"agent", "tools", "mcp", "skills", "channels", "memory", "system", "office"}


class _LazyModule(types.ModuleType):
    def __init__(self, fullname: str, target: str):
        super().__init__(fullname)
        self._target = target
        self._real_mod = None

    def _load(self) -> types.ModuleType:
        if self._real_mod is None:
            mod = import_module(self._target)
            self._real_mod = mod
            self.__dict__.update(mod.__dict__)
            sys.modules[self.__name__] = mod
        return self._real_mod

    def __getattr__(self, name: str) -> Any:
        return getattr(self._load(), name)

    def __dir__(self) -> list[str]:
        return dir(self._load())


for short_name, target in MODULE_ROUTING.items():
    if short_name not in PACKAGES:
        fullname = f"nestor.services.{short_name}"
        if fullname not in sys.modules:
            sys.modules[fullname] = _LazyModule(fullname, target)


def __getattr__(name: str) -> Any:
    if name in MODULE_ROUTING:
        mod = import_module(MODULE_ROUTING[name])
        setattr(sys.modules[__name__], name, mod)
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(MODULE_ROUTING.keys()) + list(PACKAGES)
