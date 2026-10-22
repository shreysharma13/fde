"""
PURPOSE: Compact context across turns (demo: last few messages + facts in repos).
CALLED BY: agent.py
CALLS: repositories (optional)
ABSTRACTION LEVEL: policy + data selection
STORE: short msgs / facts. NEVER: secrets, full tool JSON dumps as "memory"
"""

from __future__ import annotations

import repositories

_MAX_MSGS = 6
_BUF: dict[str, list] = {}


def load(session_id: str) -> list:
    msgs = list(_BUF.get(session_id, []))[-_MAX_MSGS:]
    facts = repositories.load(session_id).get("facts") or []
    if facts:
        msgs = [
            {
                "role": "system",
                "content": "Known facts:\n" + "\n".join(f"- {f}" for f in facts[-10:]),
            }
        ] + msgs
    return msgs


def save(session_id: str, new_messages: list) -> None:
    buf = _BUF.setdefault(session_id, [])
    buf.extend(new_messages)
    _BUF[session_id] = buf[-_MAX_MSGS:]
