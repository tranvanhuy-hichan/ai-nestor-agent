"""Controls for built-in tools and connected MCP tools."""
from fastapi import APIRouter, HTTPException

from ..core import config
from ..services import mcp_client, tools

AUTO = True
router = APIRouter()
_TIMEOUT_TOOLS = {"exec", "exec_bg", "run_script"}


@router.get("/tool-policies")
def list_tool_policies():
    agent = config.load().agent
    registry = tools.TOOLS | mcp_client.manager.tool_defs()
    return [
        {
            "name": name,
            "risk": registry[name].risk if name in registry else "mcp",
            "timeout_supported": name in _TIMEOUT_TOOLS or (name in registry and registry[name].risk == "mcp"),
            "policy": agent.tool_policies.get(name, config.ToolPolicy()),
            "base_enabled": agent.tools_enabled.get(name, True),
        }
        for name in sorted(registry.keys() | agent.tool_policies.keys())
    ]


@router.put("/tool-policies/{name}")
async def save_tool_policy(name: str, policy: config.ToolPolicy):
    cfg = config.load()
    tool = tools.TOOLS.get(name) or mcp_client.manager.tool_defs().get(name)
    if tool is None and name not in cfg.agent.tool_policies:
        raise HTTPException(404, "Không có công cụ này")
    if policy.timeout is not None and name not in _TIMEOUT_TOOLS and tool is not None and tool.risk != "mcp":
        raise HTTPException(422, "Công cụ này dùng thời hạn cố định")
    if policy == config.ToolPolicy():
        cfg.agent.tool_policies.pop(name, None)
    else:
        cfg.agent.tool_policies[name] = policy
    config.save(cfg)
    return {"ok": True}
