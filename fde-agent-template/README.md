# FDE agent template

Empty-slate harness with **real** tool JSON + demo skill + skill shortlist.

## Quick look (no API key)

```bash
cd fde-agent-template
python main.py --dry-route --msg "Line 2 only has valves until Wednesday"
```

Shows which skill was shortlisted and loads tool schemas from `tools/schemas/`.

## Full run

```bash
cp .env.example .env   # add OPENAI_API_KEY
pip install -r requirements.txt
python main.py --msg "Line 2 only has valves until Wednesday"
```

## Where taste lives

| Concern | Look at |
|---------|---------|
| System prompt | `prompts/system.md` |
| Skill shortlist | `skill_router.py` + `skills/*.md` frontmatter |
| Tool descriptions | `tools/schemas/*.json` |
| Dispatch | `tools/__init__.py` |
| Memory / durability | `memory.py`, `repositories.py` |
| Self-healing | `healing.py` |

Cheat sheets: repo `docs/` (01–04).
