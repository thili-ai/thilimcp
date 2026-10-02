"""The product catalog, as a resource — not a tool.

A naive first pass exposes the catalog as a tool the model has to call with a guessed query. In
practice three plausible guesses ("all", "*", "everything") return zero results and only an empty
string works — a silent failure, not an obvious one. The catalog rarely changes and needs no
argument to be useful, which is exactly what makes it a resource: something the model can just
read, not something it has to invoke correctly.
"""
import json
import sqlite3

from mcp.server.mcpserver import MCPServer


def register_resources(mcp_server: MCPServer, conn: sqlite3.Connection) -> None:
    @mcp_server.resource("shop://products", name="product_catalog", mime_type="application/json")
    def product_catalog() -> str:
        """The full product catalog, read-only."""
        rows = conn.execute("SELECT * FROM products").fetchall()
        return json.dumps([dict(r) for r in rows])
