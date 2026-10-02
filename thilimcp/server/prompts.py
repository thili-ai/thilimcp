"""One parameterized prompt template — a third primitive, distinct from a tool or a resource.

A prompt template doesn't execute anything and doesn't return data on its own; it hands back text
the caller can send to an LLM. This is the MCP server offering a piece of its own domain expertise
("here's how to ask about a customer's order history well") rather than a capability or a fact.
"""
from mcp.server.mcpserver import MCPServer


def register_prompts(mcp_server: MCPServer) -> None:
    @mcp_server.prompt()
    def summarize_customer_history(customer_id: int) -> str:
        """A reusable prompt: summarize one customer's order history."""
        return (
            f"Summarize the order history for customer {customer_id}: their total orders, "
            f"how many were returned, and any patterns worth flagging."
        )
