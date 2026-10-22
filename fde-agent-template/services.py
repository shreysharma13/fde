"""
PURPOSE: External/fake side effects. No agent logic.
CALLED BY: tools package handlers
CALLS: fixtures/inventory.json (fake ERP)
WHEN INVOKED: Inside a tool handler
ABSTRACTION LEVEL: I/O
RCA: wrong qty / not_found → here or fixtures/inventory.json
"""

from __future__ import annotations

import json
from pathlib import Path

_FIXTURE = Path(__file__).parent / "fixtures" / "inventory.json"


def get_inventory(part_id: str) -> dict:
    data = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    row = data.get(part_id)
    if row is None:
        # not_found → healing should NOT retry-storm
        raise KeyError(f"not_found:part_id={part_id}")
    return {"part_id": part_id, "qty": row["qty"], "unit": row["unit"], "location": row["location"]}
