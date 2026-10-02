"""Build the shop MCP server — the same server every lesson's transport runs unchanged."""
import os
import sqlite3

from mcp.server.mcpserver import MCPServer

from ..shop.seed import seed_shop
from .prompts import register_prompts
from .resources import register_resources
from .tools import register_tools


def build_server(db_path: str = "shop.db", reseed: bool = False) -> MCPServer:
    """Open (seeding if needed) the shop database and register every tool, resource, and prompt.

    Tool logic never changes with transport — stdio and streamable-HTTP both call this same
    function and get back an identical server.
    """
    if reseed or not os.path.exists(db_path):
        seed_shop(db_path).close()

    # check_same_thread=False: MCPServer runs sync tool functions via anyio.to_thread, not the
    # connection's own thread, so the default sqlite3 thread-affinity check would crash every call.
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    mcp_server = MCPServer("shop")
    register_tools(mcp_server, conn)
    register_resources(mcp_server, conn)
    register_prompts(mcp_server)
    return mcp_server
