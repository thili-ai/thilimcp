"""Run the shop server over stdio — for a local client (e.g. another process on this machine).

Nothing about the server logic changes for this transport; see transport_http.py. Run directly:
`python -m thilimcp.server.transport_stdio`.
"""
from . import build_server

mcp_server = build_server()

if __name__ == "__main__":
    mcp_server.run("stdio")
