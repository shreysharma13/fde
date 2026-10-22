"""
PURPOSE: Load tool JSON schemas (what the model sees) + dispatch to handlers.
CALLED BY: agent.py
CALLS: services.py, repositories.py; reads tools/schemas/*.json
WHEN INVOKED: schemas() each model call; dispatch() on each tool_call
ABSTRACTION LEVEL: contracts (+ thin dispatch)
DO NOT PUT HERE: prompts, healing, OpenAI HTTP
RCA: bad tool choice → JSON under tools/schemas/. Handler fail → services/repos.

NOTE: This package replaces a root tools.py so `tools/schemas/` can live beside code.
"""

from __future__ import annotations

import json
from pathlib import Path

import repositories
import services

SCHEMAS_DIR = Path(__file__).parent / "schemas"


def schemas(names: list[str] | None = None) -> list[dict]:
    """
    Return OpenAI-style tool list.
    names=None → all schemas (default).
    names=[...] → subset (skill_subset mode — see docs/04).
    """
    out = []
    for path in sorted(SCHEMAS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        name = data["name"]
        if names is not None and name not in names:
            continue
        out.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": data["description"],
                    "parameters": data["parameters"],
                },
            }
        )
    return out


def _get_inventory(part_id: str) -> dict:
    return services.get_inventory(part_id)


def _create_task(
    title: str,
    owner: str,
    due_at: str,
    part_id: str | None = None,
    session_id: str = "default",
) -> dict:
    return repositories.create_job(
        session_id,
        title=title,
        owner=owner,
        due_at=due_at,
        part_id=part_id,
    )


def _close_task(
    task_id: str,
    evidence_type: str,
    evidence_ref: str,
    session_id: str = "default",
) -> dict:
    return repositories.close_job(
        session_id,
        task_id=task_id,
        evidence_type=evidence_type,
        evidence_ref=evidence_ref,
    )


HANDLERS = {
    "get_inventory": _get_inventory,
    "create_task": _create_task,
    "close_task": _close_task,
}


def dispatch(name: str, args: dict, *, session_id: str = "default") -> dict:
    """Run tool; always return a JSON-serializable dict."""
    if name not in HANDLERS:
        return {"ok": False, "error": f"unknown_tool:{name}"}
    fn = HANDLERS[name]
    if name in ("create_task", "close_task"):
        args = {**args, "session_id": session_id}
    try:
        result = fn(**args)
        repositories.add_tool_run(session_id, name, args, result, ok=True)
        return {"ok": True, **(result if isinstance(result, dict) else {"result": result})}
    except Exception as e:
        repositories.add_tool_run(
            session_id, name, args, {}, ok=False, error=str(e)
        )
        raise
