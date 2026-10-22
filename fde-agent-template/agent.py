"""
PURPOSE: The harness loop. Load context → shortlist skill → model → tools → heal → save.
CALLED BY: main.py
CALLS: model_client, tools, memory, repositories, healing, skill_router; reads prompts/
WHEN INVOKED: Once per user message
ABSTRACTION LEVEL: orchestration
DO NOT PUT HERE: raw HTTP, SQL, prompt essay text
RCA: wrong skill → skill_router. wrong tool → tools/schemas. retry storm → healing.
"""

from __future__ import annotations

from pathlib import Path

import healing
import memory
import model_client
import repositories
import skill_router
import tools

PROMPTS = Path(__file__).parent / "prompts" / "system.md"

# Demo: which tools each skill may expose (skill_subset mode)
SKILL_TOOLS = {
    "investigate_shortage": ["get_inventory", "create_task", "close_task"],
}


def _system_prompt() -> str:
    return PROMPTS.read_text(encoding="utf-8")


def run(
    user_msg: str,
    session_id: str,
    *,
    skill_mode: str = "keywords",
    tools_mode: str = "all_schemas",
    explicit_skill: str | None = None,
    max_turns: int = 8,
) -> dict:
    state = repositories.load(session_id)
    mem_msgs = memory.load(session_id)

    # --- shortlist ONE skill (or none); never send all skill files ---
    skill = skill_router.select_skill(
        user_msg,
        explicit_id=explicit_skill,
        sticky_id=state.get("sticky_skill"),
        mode=skill_mode,
    )
    if skill:
        state["sticky_skill"] = skill["id"]
        repositories.save(session_id, state)

    messages: list[dict] = [
        {"role": "system", "content": _system_prompt()},
    ]
    skill_msg = skill_router.skill_as_system_message(skill)
    if skill_msg:
        messages.append(skill_msg)
    messages.extend(mem_msgs)
    messages.append({"role": "user", "content": user_msg})

    # --- which tool schemas to send ---
    if tools_mode == "skill_subset" and skill:
        tool_list = tools.schemas(SKILL_TOOLS.get(skill["id"]))
    else:
        tool_list = tools.schemas()  # all

    for _ in range(max_turns):
        reply = model_client.chat(messages, tool_list)
        tool_calls = reply.get("tool_calls") or []

        if not tool_calls:
            memory.save(session_id, [{"role": "assistant", "content": reply.get("content") or ""}])
            return {
                "content": reply.get("content"),
                "skill": skill["id"] if skill else None,
                "state": repositories.load(session_id),
            }

        messages.append(reply.get("raw_assistant") or {"role": "assistant", "tool_calls": tool_calls})

        for call in tool_calls:
            name = call["name"]
            args = call.get("arguments") or {}
            call_id = call.get("id", name)
            attempt = 0
            while True:
                attempt += 1
                try:
                    result = tools.dispatch(name, args, session_id=session_id)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": str(result),
                        }
                    )
                    break
                except Exception as e:
                    decision = healing.decide(e, attempt)
                    if decision["action"] == "retry":
                        continue
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": str({"ok": False, "healing": decision, "error": str(e)}),
                        }
                    )
                    if decision["action"] == "escalate":
                        return {
                            "content": None,
                            "blocked": True,
                            "healing": decision,
                            "skill": skill["id"] if skill else None,
                            "state": repositories.load(session_id),
                        }
                    break

    return {"content": None, "error": "max_turns", "skill": skill["id"] if skill else None}
