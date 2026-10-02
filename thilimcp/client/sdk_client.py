"""A deterministic MCP client — no LLM involved. Calls a tool it already knows the name and
arguments for, the way every conformance check and every lesson before "connect a real client"
does. Useful on its own for scripts, tests, and grading; `claude_bridge.py` is the layer that lets
a model decide what to call instead.
"""
from typing import Any

from mcp.client import Client
from mcp.server.mcpserver import MCPServer


async def list_everything(mcp_client: Client) -> dict[str, list[str]]:
    """Names only — tools, resources, and prompts the server currently offers."""
    tools = (await mcp_client.list_tools()).tools
    resources = (await mcp_client.list_resources()).resources
    prompts = (await mcp_client.list_prompts()).prompts
    return {
        "tools": [t.name for t in tools],
        "resources": [r.uri for r in resources],
        "prompts": [p.name for p in prompts],
    }


async def call(mcp_client: Client, tool_name: str, **kwargs: Any) -> Any:
    """Call a tool and return its structured result (raises if the call itself errors).

    A dict-returning tool's `structured_content` IS that dict; a list-returning tool's is wrapped
    as `{"result": [...]}` (structured content must be a JSON object) — this returns whichever
    shape the tool actually produced, unwrapped no further, matching what each tool's own schema
    promises.
    """
    result = await mcp_client.call_tool(tool_name, kwargs)
    if result.is_error:
        raise RuntimeError(result.content[0].text)
    return result.structured_content if result.structured_content is not None else result.content[0].text


async def read_json_resource(mcp_client: Client, uri: str) -> Any:
    """Read a resource and parse it as JSON — the shape `product_catalog` returns."""
    import json

    result = await mcp_client.read_resource(uri)
    return json.loads(result.contents[0].text)


def connect(target: MCPServer | str):
    """`async with connect(mcp_server) as mcp_client:` — works in-process or over a URL/stdio."""
    return Client(target)
