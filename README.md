# thilimcp

**A small, hackable MCP server.** A seeded e-commerce backend served over the **Model Context
Protocol** — tools, a resource, a parameterized prompt template, two transports, and a hand-rolled
bridge to a real LLM's tool-use loop. No framework hides the mechanism; every primitive is
registered with a plain decorator you can read top to bottom.

> ⚠️ Educational reference implementation, not production. Error handling, auth, and persistence
> are deliberately minimal — the point is to see every moving part of MCP, not to harden it.

## 📚 Built lesson-by-lesson in a Learn Fast course

`thilimcp` is the reference implementation for the **[Learn Fast](https://learnfast.thili.ai)
course "Build an MCP Server."** You don't import a framework — you build the server and the client
bridge yourself, from a model that can't call anything to one that completes a real multi-turn
task through a protocol-served backend.

| Lesson | You build | Files |
|---|---|---|
| 1 · The model-context problem | — (a plain-README baseline, no code to carry forward) | — |
| 2 · Stand up the shop | the seeded schema | `shop/schema.sql`, `shop/seed.py` |
| 3 · The first tool | `get_order` as an MCP tool | `server/tools.py` |
| 4 · Tool vs. resource | the product catalog, fixed as a resource | `server/resources.py` |
| 5 · A second tool and a prompt | `search_products`, `list_customer_orders`, a prompt template | `server/tools.py`, `server/prompts.py` |
| 6 · Transport | stdio, then streamable-HTTP, same tool logic | `server/transport_stdio.py`, `server/transport_http.py` |
| 7 · Connect a real client | the MCP-client ↔ Claude tool-use bridge | `client/sdk_client.py`, `client/claude_bridge.py` |
| 8 · The architecture you just built | — (names lesson 7's code; no new files) | — |
| 9 · Contracts and errors | `ToolError`, not a plain exception, for expected failures | `server/errors.py` |

Every lesson's server logic is the same `build_server()` — transport, resources, and error
handling layer on top of it without rewriting it.

## Quickstart (no API key)

```bash
pip install -e ".[dev]"
python examples/quickstart.py
pytest tests/conformance.py -q
```

```python
import asyncio
from thilimcp import build_server, connect, call

async def main():
    mcp_server = build_server("shop.db", reseed=True)
    async with connect(mcp_server) as mcp_client:
        print(await call(mcp_client, "get_order", order_id=123))

asyncio.run(main())
```

## Connecting a real model (needs `ANTHROPIC_API_KEY`)

```python
import asyncio
from thilimcp import build_server, connect, mcp_tools_as_claude_tools, ask

async def main():
    mcp_server = build_server("shop.db", reseed=True)
    async with connect(mcp_server) as mcp_client:
        claude_tools = await mcp_tools_as_claude_tools(mcp_client)
        answer = await ask("What's the status of order #123?", mcp_client, claude_tools)
        print(answer)

asyncio.run(main())
```

`ask()` is the exact loop Claude Desktop and Claude Code run internally every time they use an MCP
server — nothing hidden, ~30 lines, in `client/claude_bridge.py`.

## Why tool vs. resource matters

The product catalog is deliberately **not** a tool. A tool the model has to call with a guessed
query produces a sharp, silent failure: three plausible queries return zero results, and only an
empty string works. A resource needs no argument at all — the model just reads it. See
`server/resources.py` and lesson 4.

## Why errors are part of the contract

Raising a plain exception inside a tool doesn't crash the server once a real `Client` is in front
of it — the protocol layer catches it — but it does strip the real reason, leaving only a generic
`"Error executing tool ..."` message. `server/errors.py`'s `not_found()` raises `ToolError`
instead, which keeps the author's own words intact for the model to actually read. See lesson 9.

## License

MIT © 2026 thili.ai
