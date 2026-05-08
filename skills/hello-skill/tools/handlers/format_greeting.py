"""MCP tool handler: formats a greeting using a configurable separator.

Documental smoke for plan-010 PR 2 — registered in tools/mcp.config.json as
the `format_greeting` tool, referenced by the Hello widget binding.
"""

from typing import Any


def run(input: dict[str, Any]) -> dict[str, str]:
    name = str(input.get("name", "world"))
    return {"greeting": f"Hello, {name}!"}
