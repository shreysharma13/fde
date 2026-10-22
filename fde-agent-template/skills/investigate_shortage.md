---
id: investigate_shortage
triggers:
  - shortage
  - short on
  - short of
  - no material
  - only has
  - not enough
---

<!--
PURPOSE: Demo skill — shortage → owned task → verify with evidence.
CALLED BY: skill_router → agent (only if shortlisted).
NOT sent every turn — only when triggers match.
-->

# Skill: investigate_shortage

## When to use
Material risk for a line/build mentioned in chat.

## Steps
1. Identify part if possible; call `get_inventory` if stock is uncertain.
2. Call `create_task` with owner (usually purchasing) and a due date.
3. Do not close until `close_task` has real evidence.

## Tools to prefer
- `get_inventory` — facts, not guesses
- `create_task` — ownership
- `close_task` — only with erp_receipt or photo_url

## Boundaries (ask human)
- Resequencing the line / customer promise date changes

## Done when (evidence)
- `erp_receipt` or `photo_url` on `close_task`
