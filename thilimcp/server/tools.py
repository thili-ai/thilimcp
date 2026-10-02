"""The shop's three tools — actions with arguments the model must supply correctly.

`get_order` and `list_customer_orders` need an id the model has to already have or ask for;
`search_products` needs a real query, which is exactly why the product catalog itself is a
*resource* (see resources.py), not a fourth tool here — "give me everything" is reading, not acting.
"""
import sqlite3
from typing import Any

from mcp.server.mcpserver import MCPServer

from .errors import not_found


def register_tools(mcp_server: MCPServer, conn: sqlite3.Connection) -> None:
    @mcp_server.tool()
    def get_order(order_id: int) -> dict[str, Any]:
        """Look up one order by its id."""
        row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if row is None:
            raise not_found("order", order_id)
        return dict(row)

    @mcp_server.tool()
    def search_products(query: str) -> list[dict[str, Any]]:
        """Search the product catalog by name. An empty or overly broad query returns few or no
        results on purpose — browsing the whole catalog is the product_catalog resource's job."""
        rows = conn.execute("SELECT * FROM products WHERE name LIKE ?", (f"%{query}%",)).fetchall()
        return [dict(r) for r in rows]

    @mcp_server.tool()
    def list_customer_orders(customer_id: int) -> list[dict[str, Any]]:
        """List every order placed by one customer, most recent first."""
        rows = conn.execute(
            "SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC", (customer_id,)
        ).fetchall()
        return [dict(r) for r in rows]
