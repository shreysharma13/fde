# Essential terms (cheat sheet)

Quick definitions for FDE + agent harness work (Morsa-flavored).

## Agent harness

| Term | Meaning |
|------|---------|
| **Harness** | Everything around the model: prompt, tools, memory, state, retries — not the model weights |
| **Agent loop** | Model thinks → may call tools → results come back → repeat until done or blocked |
| **System prompt** | Standing instructions every turn (`prompts/system.md`) |
| **Skill** | Scoped playbook for one workflow (`skills/*.md`) — when to use, steps, boundaries |
| **Tool** | A function the model can call, with a clear name, args, and return shape |
| **Tool description** | The schema/docs the model reads to decide *when* and *how* to call a tool |
| **Long-horizon memory** | Facts/state that survive many turns (usually DB + selective recall, not infinite chat) |
| **Self-healing** | On failure: retry, stop, alternate path, or escalate — leave system in a known state |
| **Eval case** | Scripted input + expected behavior (`evals/cases.jsonl`) |

## State & proof

| Term | Meaning |
|------|---------|
| **Source of truth** | System you trust for a field (ERP stock vs chat claim) |
| **Durable state** | Survives process restart (`repositories`) |
| **Session / job** | One ongoing piece of work the agent is driving |
| **Evidence / proof** | What counts as “done” (ERP receipt, photo) — not “ok done” in chat |
| **Escalation** | Hand off to a human or higher role when idle/blocked/out of policy |

## Manufacturing systems (what Morsa sits on)

| Term | Meaning |
|------|---------|
| **ERP** | Orders, POs, stock, commercial record |
| **MES** | What’s running on the line / job status |
| **WMS** | Warehouse inventory moves / locations |
| **WCS / WES** | Control / execution of automation on floor |
| **QMS / CMMS** | Quality / maintenance systems |
| **Shortage** | Material needed for a build isn’t available in time |
| **Expedite** | Chase a supplier / PO to pull a date in |
| **Replan** | Change what the line runs because reality moved |

## Morsa product loop (operating AI)

| Step | Question |
|------|----------|
| **Signal** | What changed? |
| **Context** | What does it belong to? (part, WO, customer, owner) |
| **Consequence** | What breaks downstream? |
| **Decision** | What’s next, and is it allowed? |
| **Execution** | Who/what acts where? |
| **Verification** | Did it actually happen? |

## Role

| Term | Meaning |
|------|---------|
| **FDE** | Forward Deployed Engineer — make the product work in a real customer environment; own outcome |
| **Pilot** | Narrow live rollout (one line / one workflow) before scale |
| **Approval boundary** | What the agent may do alone vs must ask a human |
