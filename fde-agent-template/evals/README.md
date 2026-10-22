# Evals

`cases.jsonl` — one JSON object per line.

| Field | Meaning |
|-------|---------|
| `id` | Case name |
| `input` | User / plant message |
| `expect` | What good harness behavior looks like |

Skip keys starting with `_` (docs lines).

Run later: loop cases → `agent.run` → assert `expect` (tool called, no retry storm, etc.).
