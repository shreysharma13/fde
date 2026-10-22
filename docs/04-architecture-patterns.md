# Architecture patterns (when to use what)

Short menu of design choices in this harness. Default = what’s coded now.

## Skills → model

| Pattern | How | Use when | Avoid when |
|---------|-----|----------|------------|
| **Keywords** (default) | Match `triggers` in skill frontmatter | Few skills, clear phrases | Ambiguous chat, many overlapping triggers |
| **Explicit** | Caller passes `skill=id` | Webhooks, evals, known workflow | Free-form user chat only |
| **Sticky** | Reuse session’s last skill | Multi-turn jobs | First message / topic change |
| **Router model** | Tiny classify call → skill id | Many skills, messy language | Cost/latency sensitive pilots |
| **Send all skills** | Dump every file into context | Never (almost) | Always — confuses the model |

**Rule:** at most **one** skill body per turn.

## Tools → model

| Pattern | How | Use when |
|---------|-----|----------|
| **All schemas** (default) | `tools.schemas()` | Small tool set (≤10) |
| **Skill subset** | `tools.schemas(names for skill)` | Many tools; reduce wrong calls |
| **Schemas in JSON files** (here) | `tools/schemas/*.json` loaded in code | Edit descriptions without touching handlers |
| **Schemas inline in Python** | Dicts in code | Tiny prototypes only |
| **One mega-tool** | `do_anything(payload)` | Never — kills taste |

## Memory / state

| Pattern | How | Use when |
|---------|-----|----------|
| **DB = source of truth** | `repositories` (jobs, traces) | Anything that must survive restart |
| **Selective memory** | `memory` keeps short facts/msgs | Long-horizon without context blowup |
| **Chat-only memory** | Stuff all history in messages | Demos only — not production |
| **Summarize then store** | LLM compresses → fact list | Very long threads |

## Healing

| Pattern | How | Use when |
|---------|-----|----------|
| **Classify → policy** (here) | transient retry; not_found stop; else escalate | Always prefer this |
| **Blind retry N times** | Same call in a loop | Never for 404 / bad args |
| **Model self-repair only** | “try again” in prompt | Weak alone — pair with `healing.py` |

## Entry / deploy

| Pattern | How | Use when |
|---------|-----|----------|
| **CLI `main.py`** | Args → `agent.run` | Local/interview |
| **Webhook** | HTTP → same `agent.run` | WhatsApp/Teams later |
| **Same agent, swap repos** | In-memory → Convex | Interview → real deploy |

## Layout choices

| Choice | Here | Alternative |
|--------|------|-------------|
| Tools as package | `tools/` + `schemas/*.json` | Single `tools.py` (fine until JSON files exist) |
| Skills as markdown | `skills/*.md` + frontmatter | Skills as Python classes |
| Config | `config.example.yaml` | Env-only flags |

## Interview taste defaults

1. Keywords skill shortlist (one skill)  
2. JSON tool schemas with sharp descriptions  
3. Durable jobs in repositories  
4. Classify errors in healing  
5. Don’t send all skills / one mega-tool  
