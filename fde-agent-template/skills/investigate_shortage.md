---
id: investigate_shortage
triggers:
  - shortage
  - short on
  - short of
  - no material
  - only has
  - not enough
  - out of stock
  - material risk
---

# Skill: investigate_shortage

## When to use
Someone reports that material for a line/build is low, late, missing, or only lasts until a date.
Examples: "Line 2 only has valves until Wednesday", "short on VALVE-9", "no material for pump build".

## Goal
Turn the signal into an owned expedite (or material-risk) task, optionally check stock with a tool, and never close without proof that material moved.

## Steps
1. Extract what you can: part name/id, line, and time risk ("until Wednesday").
2. If `part_id` is known or strongly implied and stock is uncertain, call `get_inventory`.
3. Call `create_task` with:
   - `title` — short, e.g. "Expedite VALVE-9 for Line 2"
   - `owner` — usually `purchasing` (or who they named)
   - `due_at` — a concrete date (use the risk date if given)
   - `part_id` — if known
4. Tell the user the `task_id`, owner, and due date.
5. Do **not** call `close_task` in this first response unless they already provided evidence (`erp_receipt` id or `photo_url`).

## Tools to prefer
| Tool | Use when |
|------|----------|
| `get_inventory` | You have a part id and need on-hand qty |
| `create_task` | Almost always for a new shortage signal |
| `close_task` | Only later, with evidence that material arrived / was received |

## Boundaries — ask a human
- Changing tomorrow's production sequence / replan
- Promising a new date to a customer
- Approving a substitute part/material
- Choosing between two expensive expedite options

## Done when (evidence)
Task may close only via `close_task` with:
- `evidence_type`: `erp_receipt` **or** `photo_url`
- `evidence_ref`: real receipt id or URL — never invented
