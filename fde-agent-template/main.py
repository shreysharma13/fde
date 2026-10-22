"""
PURPOSE: Entry point. CLI today; webhook later.
CALLED BY: you
CALLS: agent.run, skill_router (demo print)
ABSTRACTION LEVEL: entry
EXAMPLE: python main.py --msg "Line 2 only has valves until Wednesday"
"""

from __future__ import annotations

import argparse
import json

import agent
import skill_router
import tools


def main() -> None:
    p = argparse.ArgumentParser(description="FDE agent template")
    p.add_argument("--msg", required=True, help="User / plant message")
    p.add_argument("--session", default="demo")
    p.add_argument("--skill-mode", default="keywords", choices=["keywords", "explicit", "sticky"])
    p.add_argument("--tools-mode", default="all_schemas", choices=["all_schemas", "skill_subset"])
    p.add_argument("--dry-route", action="store_true", help="Only show skill shortlist + tool schemas, no LLM")
    args = p.parse_args()

    if args.dry_route:
        skill = skill_router.select_skill(args.msg, mode=args.skill_mode)
        print("skill:", skill["id"] if skill else None)
        print("tools:", json.dumps(tools.schemas(), indent=2)[:800], "...")
        return

    result = agent.run(
        args.msg,
        args.session,
        skill_mode=args.skill_mode,
        tools_mode=args.tools_mode,
    )
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
