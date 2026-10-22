# Template & data flow (cheat sheet)

Clone `fde-agent-template/`. Fill stubs; don’t invent a new layout every time.

## Essential template

```
fde-agent-template/
├── main.py
├── agent.py
├── model_client.py
├── skill_router.py          # shortlist ONE skill
├── tools/                   # package (not tools.py — avoids clash)
│   ├── __init__.py          # schemas() + dispatch()
│   └── schemas/*.json       # what the model sees
├── services.py
├── repositories.py
├── memory.py
├── healing.py
├── prompts/system.md
├── skills/
│   ├── _template.md
│   └── investigate_shortage.md   # demo skill
├── schemas/                 # Job / Evidence / ToolRun shapes
├── fixtures/inventory.json
├── config.example.yaml
├── .env.example
├── requirements.txt
└── evals/cases.jsonl
```

## Data flow

```
main
  → agent.run
      → repositories.load + memory.load
      → skill_router.select_skill  → at most ONE skill.md
      → prompts/system.md (+ skill body if matched)
      → tools.schemas()            → from tools/schemas/*.json
      → model_client.chat(messages, tools)
      → tools.dispatch → services / repositories
      → healing.decide on errors
      → memory.save + repositories.save
```

## Who calls whom

| File | Called by | Calls |
|------|-----------|--------|
| `main.py` | you | `agent`, (dry) `skill_router`, `tools` |
| `agent.py` | `main` | router, model, tools, memory, repos, healing |
| `skill_router.py` | `agent` | reads `skills/*.md` |
| `tools/` | `agent` | `services`, `repositories` |
| `services.py` | `tools` | fixtures / APIs |
| `repositories.py` | `agent`, `tools` | store |
| `memory.py` | `agent` | repos (optional) |
| `healing.py` | `agent` | — |

**Rule:** never send all skills. Tool JSON ≠ skill markdown.

Patterns menu: `docs/04-architecture-patterns.md`
