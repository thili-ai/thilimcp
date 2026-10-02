"""Keys-free quickstart: list the shop server's tools/resources/prompt, run a known-answer call,
and show a crash-shaped failure degrade into a structured error instead of a stack trace.

Run: python examples/quickstart.py
"""
import asyncio

from thilimcp import build_server, call, connect, list_everything, read_json_resource


async def main():
    mcp_server = build_server("shop.db", reseed=True)

    async with connect(mcp_server) as mcp_client:
        print("offers:", await list_everything(mcp_client))

        order = await call(mcp_client, "get_order", order_id=123)
        print("order #123:", order)

        catalog = await read_json_resource(mcp_client, "shop://products")
        print("catalog size:", len(catalog))

        result = await mcp_client.call_tool("get_order", {"order_id": 999999})
        print("missing order -> is_error:", result.is_error, "| message:", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
