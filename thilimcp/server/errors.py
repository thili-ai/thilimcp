"""The shop's error contract.

A tool's failure is part of what it promises its caller, exactly as much as its success is.

- A malformed argument (wrong type, missing field) is caught automatically by the tool's own
  schema, before the function body ever runs — nothing to write here.
- An "expected" business-logic failure (an id that doesn't exist, a state that doesn't allow this)
  should be raised as `ToolError`, not a plain exception. `ToolError`'s message is treated as safe
  to pass through to the caller, because the tool's author chose the words.
- Anything else — a bug, an unhandled edge case — should be left as a plain exception on purpose.
  The server converts it to a generic, detail-free message and logs the real traceback on its own
  side; that's deliberate, not a gap to work around.
"""
from mcp.server.mcpserver.exceptions import ToolError

__all__ = ["ToolError", "not_found"]


def not_found(resource: str, identifier: object) -> ToolError:
    """A consistently-worded ToolError for "no such <resource> with id <identifier>"."""
    return ToolError(f"no {resource} with id {identifier}")
