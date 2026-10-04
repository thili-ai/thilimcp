"""The shop's tools — actions with arguments the model must supply correctly.

`get_order` and `list_customer_orders` need an id the model has to already have or ask for;
`search_products` needs a real query, which is exactly why the product catalog itself is a
*resource* (see resources.py), not a fourth tool here — "give me everything" is reading, not acting.

`get_order_items` was added after the Learn Fast "Build an MCP Server" course shipped — its first
consumer (that course's own lessons) never needed an order's line items, only the order itself.
`lfagentinfra-lfa2a`'s Order Agent does: answering "is this order still returnable" needs to know
which product category an order actually contains, and nothing else here exposes that link.

`price_cents` and `tax_rate_percent` were added to `get_order_items`'s own output later still, for
`lfagentinfra-lforchestrate`'s Refund Agent — it needs a real amount to refund, and this tool
already had everything else about a line item. The tool computes nothing; it exposes the facts
`products` already held, same as every earlier addition here.
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

    @mcp_server.tool()
    def get_order_items(order_id: int) -> list[dict[str, Any]]:
        """List one order's line items: product name, category, return window, unit price in
        cents, tax rate, and quantity. An order can span more than one category — this returns
        every item, not a single summarized answer."""
        if conn.execute("SELECT 1 FROM orders WHERE id = ?", (order_id,)).fetchone() is None:
            raise not_found("order", order_id)
        rows = conn.execute(
            "SELECT p.id AS product_id, p.name, p.category, p.return_window_days, "
            "p.price_cents, p.tax_rate_percent, oi.quantity "
            "FROM order_items oi JOIN products p ON p.id = oi.product_id "
            "WHERE oi.order_id = ?", (order_id,),
        ).fetchall()
        return [dict(r) for r in rows]
