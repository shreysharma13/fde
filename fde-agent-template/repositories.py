"""
PURPOSE: Durable state (in-memory demo; swap for Convex/DB later).
CALLED BY: agent.py, tools handlers, memory.py
ABSTRACTION LEVEL: data
RCA: lost after restart → replace _STORE with real DB; shape in schemas/job.json
"""

from __future__ import annotations

import uuid
from typing import Any

# demo only — process memory
_STORE: dict[str, dict[str, Any]] = {}


def _session(session_id: str) -> dict:
    if session_id not in _STORE:
        _STORE[session_id] = {"jobs": {}, "tool_runs": [], "facts": [], "sticky_skill": None}
    return _STORE[session_id]


def load(session_id: str) -> dict:
    return _session(session_id)


def save(session_id: str, state: dict) -> None:
    _STORE[session_id] = state


def create_job(
    session_id: str,
    *,
    title: str,
    owner: str,
    due_at: str,
    part_id: str | None = None,
) -> dict:
    s = _session(session_id)
    job_id = f"T-{uuid.uuid4().hex[:6]}"
    job = {
        "id": job_id,
        "title": title,
        "owner": owner,
        "due_at": due_at,
        "part_id": part_id,
        "status": "open",
        "evidence_type": None,
        "evidence_ref": None,
    }
    s["jobs"][job_id] = job
    return job


def close_job(
    session_id: str,
    *,
    task_id: str,
    evidence_type: str,
    evidence_ref: str,
) -> dict:
    s = _session(session_id)
    job = s["jobs"].get(task_id)
    if not job:
        raise KeyError(f"not_found:task_id={task_id}")
    if evidence_type not in ("erp_receipt", "photo_url") or not evidence_ref:
        raise ValueError("evidence_required")
    job["status"] = "closed"
    job["evidence_type"] = evidence_type
    job["evidence_ref"] = evidence_ref
    return job


def add_tool_run(
    session_id: str,
    name: str,
    args: dict,
    result: dict,
    *,
    ok: bool,
    error: str | None = None,
) -> None:
    _session(session_id)["tool_runs"].append(
        {"name": name, "args": args, "result": result, "ok": ok, "error": error}
    )
