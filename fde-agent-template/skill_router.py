"""
PURPOSE: Shortlist ONE skill (or none) before the model call. Never dump all skills.
CALLED BY: agent.py
CALLS: reads skills/*.md (skips _template.md)
WHEN INVOKED: Once per run, before building messages.
ABSTRACTION LEVEL: policy (routing)
DO NOT PUT HERE: tool schemas, LLM calls, HTTP.
SECTIONS: parse frontmatter → match → return skill body
APPROACH IN USE: keywords (see docs/04 for alternatives)
PSEUDOCODE:
  skills = load_all_with_triggers()
  matches = [s for s in skills if any(t in user_msg.lower() for t in s.triggers)]
  return matches[0] if len(matches)==1 else (None if 0 else first/best)
RCA: wrong skill loaded → triggers in skill frontmatter or this matcher.
"""

from __future__ import annotations

import re
from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "skills"


def _parse_skill(path: Path) -> dict | None:
    """Read YAML frontmatter + body. Returns {id, triggers, body, path}."""
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        return None
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return None
    fm, body = parts[1], parts[2].strip()
    skill_id = None
    triggers: list[str] = []
    for line in fm.splitlines():
        line = line.strip()
        if line.startswith("id:"):
            skill_id = line.split(":", 1)[1].strip()
        elif line.startswith("- "):
            triggers.append(line[2:].strip().strip('"').strip("'"))
    if not skill_id:
        skill_id = path.stem
    return {"id": skill_id, "triggers": triggers, "body": body, "path": str(path)}


def list_skills() -> list[dict]:
    out = []
    for path in sorted(SKILLS_DIR.glob("*.md")):
        if path.name.startswith("_"):
            continue
        parsed = _parse_skill(path)
        if parsed:
            out.append(parsed)
    return out


def select_skill(
    user_msg: str,
    *,
    explicit_id: str | None = None,
    sticky_id: str | None = None,
    mode: str = "keywords",
) -> dict | None:
    """
    mode:
      keywords — match triggers in user_msg (default)
      explicit — must pass explicit_id
      sticky   — prefer sticky_id from session, else keywords
    Returns skill dict or None. At most one skill.
    """
    skills = {s["id"]: s for s in list_skills()}

    if mode == "explicit":
        return skills.get(explicit_id) if explicit_id else None

    if mode == "sticky" and sticky_id and sticky_id in skills:
        return skills[sticky_id]

    # keywords (also fallback for sticky miss)
    msg = user_msg.lower()
    matches = []
    for s in skills.values():
        if any(t.lower() in msg for t in s["triggers"]):
            matches.append(s)

    if not matches:
        return None
    # If several match, prefer longest trigger hit (more specific)
    def score(s: dict) -> int:
        return max((len(t) for t in s["triggers"] if t.lower() in msg), default=0)

    matches.sort(key=score, reverse=True)
    return matches[0]


def skill_as_system_message(skill: dict | None) -> dict | None:
    """Format for messages[] — only call if select_skill returned something."""
    if not skill:
        return None
    return {
        "role": "system",
        "content": f"## Active skill: {skill['id']}\n\n{skill['body']}",
    }
