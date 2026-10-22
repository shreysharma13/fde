# Navigation & RCA (cheat sheet)

When something breaks or a task lands, open the right file first.

## Interview-style situations → file

| Situation | Open first | Then |
|-----------|------------|------|
| Bad taste (vague prompt / tools) | `prompts/system.md`, `tools/schemas/*.json` | `skills/` |
| Long-horizon memory | `memory.py`, `repositories.py` | `agent.py` load/save points |
| Skills + tool descriptions | `skills/`, `skill_router.py`, `tools/schemas/` | `prompts/system.md` |
| Self-healing | `healing.py` | `agent.py` error branch |
| End-to-end demo / “does it run?” | `main.py` | follow data flow; check `evals/cases.jsonl` |

## Symptom → file

| Symptom | Likely file |
|---------|-------------|
| Wrong tone / ignores rules | `prompts/system.md` |
| Calls wrong tool or bad args | `tools/schemas/*.json` |
| Wrong skill loaded | `skill_router.py` + skill frontmatter `triggers` |
| Forgets earlier decisions | `memory.py` / `repositories.py` |
| Retries forever / spam | `healing.py` |
| External/API data wrong or fail | `services.py` |
| Lost after restart | `repositories.py` |
| Workflow steps unclear | `skills/*.md` |
| Loop never starts / never stops | `agent.py` |
| Webhook/CLI wiring | `main.py` |
| Eval failed, need expected behavior | `evals/cases.jsonl` |

## How to walk the codebase (60 seconds)

1. Start at `main.py` — how does a request enter?
2. Jump to `agent.run` — what’s the loop order?
3. Check what gets loaded: memory, repos, system prompt, skill.
4. See `tools.dispatch` — which side effects exist?
5. See `healing` — what happens on failure?
6. Confirm what gets saved before return.

## DO / DON’T when editing

| DO | DON’T |
|----|--------|
| Fix tool schemas in `tools/schemas/` | Bury HTTP/API calls inside `agent.py` |
| Put standing rules in `system.md` | Paste huge prompts into tool code |
| Put one workflow in one skill file | One mega-skill for the whole plant |
| Persist jobs in `repositories` | Rely only on chat history |
| Encode retry policy in `healing` | Blind `while True: retry` in the model prompt |
