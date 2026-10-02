"""Bridge an MCP client to the Anthropic API directly — no framework in between.

This ~30-line loop is the entire mechanism Claude Desktop and Claude Code hide inside themselves:
list the server's tools, convert their schemas to Claude's `tools=[...]` format, let Claude decide
what to call, run that exact call through the real MCP client, hand the result back, repeat until
Claude has enough to answer in plain text.

Four layers, named: the LLM (the `messages.create` calls) only ever produces a *request* — the
agent/host runtime (this function's own `while` loop) is what reads that request and actually
calls `mcp_client.call_tool(...)`, the one line in this whole function with any side effect.
"""
from typing import Any

import anthropic
from mcp.client import Client

DEFAULT_MODEL = "claude-haiku-4-5-20251001"


async def mcp_tools_as_claude_tools(mcp_client: Client) -> list[dict[str, Any]]:
    """Convert the server's tool schemas into Claude's `tools=[...]` format — close enough to a
    direct transformation that there's barely a conversion step at all."""
    tools = (await mcp_client.list_tools()).tools
    return [
        {"name": t.name, "description": t.description, "input_schema": t.input_schema}
        for t in tools
    ]


async def ask(
    question: str,
    mcp_client: Client,
    claude_tools: list[dict[str, Any]],
    claude: anthropic.Anthropic | None = None,
    model: str = DEFAULT_MODEL,
) -> str:
    """Ask Claude a question with the server's tools attached; run any tool call it requests
    through the real MCP client and feed the result back, until it answers in plain text."""
    claude = claude or anthropic.Anthropic()
    messages = [{"role": "user", "content": question}]

    response = claude.messages.create(
        model=model, max_tokens=500, tools=claude_tools, messages=messages,
    )

    while response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            # The only line in this function that actually reaches the server/database — every
            # other line prepares input for Claude or reads a decision Claude already made.
            result = await mcp_client.call_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result.content[0].text,
                "is_error": result.is_error,
            })
        messages.append({"role": "user", "content": tool_results})
        response = claude.messages.create(
            model=model, max_tokens=500, tools=claude_tools, messages=messages,
        )

    return "".join(b.text for b in response.content if b.type == "text")
