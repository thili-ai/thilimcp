"""Run the shop server over streamable-HTTP — for a remote client.

The transport is a constructor/method-call detail (`host`/`port` go to `.run(...)`, not
`MCPServer(...)`), never a change to tool logic — the exact same `build_server()` as
transport_stdio.py. Run directly: `python -m thilimcp.server.transport_http`.
"""
from . import build_server

mcp_server = build_server()

if __name__ == "__main__":
    mcp_server.run("streamable-http", host="127.0.0.1", port=8000)
