"""
PURPOSE: Failure policy — retry / stop / escalate.
CALLED BY: agent.py
ABSTRACTION LEVEL: policy
RCA: retry storms → tighten decide() here
"""

from __future__ import annotations


def classify(error: Exception) -> str:
    msg = str(error).lower()
    if "not_found" in msg:
        return "not_found"
    if "timeout" in msg or "temporarily" in msg:
        return "transient"
    if "evidence" in msg or "required" in msg:
        return "bad_args"
    return "unknown"


def decide(error: Exception, attempt: int) -> dict:
    kind = classify(error)
    if kind == "transient" and attempt < 2:
        return {"action": "retry", "reason": kind}
    if kind == "not_found":
        return {"action": "stop", "reason": kind}  # do not retry same id
    if kind == "bad_args" and attempt < 2:
        return {"action": "repair_once", "reason": kind}
    return {"action": "escalate", "reason": kind}
