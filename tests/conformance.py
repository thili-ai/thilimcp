"""Tool list, resource list, and a fixed set of known-answer tool calls against the seeded shop.

Run with: `pytest tests/conformance.py -q` (or any pytest discovery).
"""
import tempfile
from pathlib import Path

import pytest

from thilimcp import build_server
from thilimcp.client import sdk_client


@pytest.fixture
def mcp_server():
    db_path = str(Path(tempfile.mkdtemp()) / "shop.db")
    return build_server(db_path, reseed=True)


async def test_lists_every_primitive(mcp_server):
    async with sdk_client.connect(mcp_server) as mcp_client:
        names = await sdk_client.list_everything(mcp_client)
    assert set(names["tools"]) == {
        "get_order", "search_products", "list_customer_orders", "get_order_items",
    }
    assert "shop://products" in names["resources"]
    assert "summarize_customer_history" in names["prompts"]


async def test_known_order_123_exists(mcp_server):
    async with sdk_client.connect(mcp_server) as mcp_client:
        order = await sdk_client.call(mcp_client, "get_order", order_id=123)
    assert order["id"] == 123


async def test_order_items_links_order_to_product_category(mcp_server):
    async with sdk_client.connect(mcp_server) as mcp_client:
        items = await sdk_client.call(mcp_client, "get_order_items", order_id=79)
    assert len(items["result"]) == 1
    assert items["result"][0]["category"] == "electronics"


async def test_order_items_missing_order_fails_honestly(mcp_server):
    async with sdk_client.connect(mcp_server) as mcp_client:
        result = await mcp_client.call_tool("get_order_items", {"order_id": 999999})
    assert result.is_error is True
    assert "999999" in result.content[0].text


async def test_priya_shah_has_three_orders(mcp_server):
    async with sdk_client.connect(mcp_server) as mcp_client:
        orders = await sdk_client.call(mcp_client, "list_customer_orders", customer_id=1)
    assert len(orders["result"]) >= 3


async def test_search_products_finds_a_real_match(mcp_server):
    async with sdk_client.connect(mcp_server) as mcp_client:
        hits = await sdk_client.call(mcp_client, "search_products", query="Wireless")
    assert len(hits["result"]) >= 1
    assert "Wireless" in hits["result"][0]["name"]


async def test_product_catalog_resource_has_thirty_items(mcp_server):
    async with sdk_client.connect(mcp_server) as mcp_client:
        catalog = await sdk_client.read_json_resource(mcp_client, "shop://products")
    assert len(catalog) == 30


async def test_missing_order_returns_structured_error_not_a_crash(mcp_server):
    async with sdk_client.connect(mcp_server) as mcp_client:
        result = await mcp_client.call_tool("get_order", {"order_id": 999999})
    assert result.is_error is True
    assert "999999" in result.content[0].text


async def test_malformed_argument_rejected_before_the_tool_runs(mcp_server):
    async with sdk_client.connect(mcp_server) as mcp_client:
        result = await mcp_client.call_tool("get_order", {"order_id": "not-a-number"})
    assert result.is_error is True
    assert "order_id" in result.content[0].text
