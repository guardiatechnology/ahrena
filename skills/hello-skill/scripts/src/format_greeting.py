"""Smoke script: formats a greeting message.

Documental smoke for plan-010 PR 2 — exercises the binding from the Hello
widget (widgets/manifest.json) to a Python script. Real execution depends on
kata-skill-dev-server / kata-build-skill being implemented operationally.
"""

from typing import Any


def run(input: dict[str, Any]) -> dict[str, str]:
    name = str(input.get("name", "world"))
    greeting = str(input.get("greeting", "Hello"))
    return {"message": f"{greeting}, {name}!"}
