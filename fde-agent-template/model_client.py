"""
PURPOSE: Thin LLM I/O. Pass messages + tool schemas; return text and/or tool_calls.
CALLED BY: agent.py
ABSTRACTION LEVEL: I/O
NOTE: Without OPENAI_API_KEY this raises — fine for reading the harness offline.
"""

from __future__ import annotations

import json
import os


def chat(messages: list, tools_list: list | None = None) -> dict:
    """
    Returns:
      {content, tool_calls: [{id, name, arguments}], raw_assistant?}
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing — copy .env.example to .env")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    kwargs = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        "messages": messages,
    }
    if tools_list:
        kwargs["tools"] = tools_list

    resp = client.chat.completions.create(**kwargs)
    msg = resp.choices[0].message
    tool_calls = []
    if msg.tool_calls:
        for tc in msg.tool_calls:
            tool_calls.append(
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments or "{}"),
                }
            )
    raw = {
        "role": "assistant",
        "content": msg.content,
        "tool_calls": msg.tool_calls,  # may be SDK objects; agent mainly uses tool_calls list
    }
    return {"content": msg.content, "tool_calls": tool_calls, "raw_assistant": {
        "role": "assistant",
        "content": msg.content or "",
        "tool_calls": [
            {
                "id": t["id"],
                "type": "function",
                "function": {
                    "name": t["name"],
                    "arguments": json.dumps(t["arguments"]),
                },
            }
            for t in tool_calls
        ] or None,
    }}
