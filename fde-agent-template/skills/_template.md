<!--
PURPOSE: One workflow playbook the agent loads when intent matches.
CALLED BY: agent.py (optional append after system prompt)
CALLS: nothing (instructs which tools to use)
WHEN INVOKED: When user/signal matches this skill (routing in agent.py)
ABSTRACTION LEVEL: policy
DO NOT PUT HERE: generic rules (system.md), tool schemas (tools.py), retry policy
SECTIONS TO FILL: when to use, steps, tools, boundaries, done = evidence
PSEUDOCODE: copy this file → rename investigate_shortage.md → fill sections
EXAMPLE skill: investigate_shortage — signal shortage → task → verify receipt
RCA: wrong workflow steps → here. Wrong tool contract → tools.py
-->

# Skill: NAME

## When to use
TODO: trigger phrases / signals

## Steps
1. TODO
2. TODO

## Tools to prefer
- TODO: tool_name — why

## Boundaries (ask human)
- TODO: e.g. replan line, substitute material

## Done when (evidence)
- TODO: e.g. erp_receipt | photo_url
