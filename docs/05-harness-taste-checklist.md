# Harness taste checklist — how to actually check

This is not “I can see X.” Each item is: **do this → look for that → pass if → fail if**.

**Harness** = prompt + tools + skills + memory + state + retries around the model.

Work in the interview repo root. Prefer ripgrep/`rg`; if missing use IDE search.

---

## 0. Map the repo (do this first, 5–10 min)

### 0.1 Find the agent loop

**Do:**
```bash
rg -n "tool_calls|toolCalls|max_turns|maxTurns|while .*turn" --glob '!node_modules' --glob '!.git'
rg -n "chat\.completions|generateText|openai|anthropic" --glob '!node_modules'
```

**Look for:** A function that (1) calls the model, (2) checks for tool calls, (3) runs tools, (4) loops.

**Pass:** One clear `run` / `agent` / `loop` function you can open.  
**Fail:** Model calls scattered with no loop, or loop with no tool handling.

**Write down path:** ______________________

### 0.2 Find the system prompt

**Do:**
```bash
rg -n "SYSTEM_PROMPT|systemPrompt|system_prompt|role:\s*[\"']system" --glob '!node_modules'
rg -n "You are " -g '*.md' -g '*.ts' -g '*.py' -g '*.txt'
ls prompts 2>/dev/null; ls src/prompts 2>/dev/null
```

**Pass:** One primary file/constant loaded into `role: system`.  
**Fail:** Prompt only hard-coded inline in 5 places, or no system message at all.

**Write down path:** ______________________

### 0.3 Find tool schemas (what the model sees)

**Do:**
```bash
rg -n "\"type\":\s*\"function\"|type:\s*[\"']function[\"']|parameters:\s*\{|tool_definitions|tools:\s*\[" --glob '!node_modules'
ls tools/schemas 2>/dev/null
```

**Pass:** List of `{ name, description, parameters }` (JSON or TS objects) passed into the model API.  
**Fail:** No schemas — model never gets tools.

**Write down path:** ______________________

### 0.4 Find tool handlers (code that runs)

**Do:**
```bash
rg -n "dispatch|HANDLERS|executeTool|case ['\"].*['\"]:|tools\[name\]" --glob '!node_modules'
```

**Pass:** `name → function` map or switch that runs real code.  
**Fail:** Schemas exist but no handler (or handlers empty stubs only with no plan).

**Write down path:** ______________________

### 0.5 Find memory / DB / Convex state

**Do:**
```bash
rg -n "convex|mutation|useQuery|repository|sessionId|session_id|memory\.|saveMemory|loadMemory" --glob '!node_modules'
ls convex 2>/dev/null
```

**Pass:** You know where jobs/messages/facts are stored (Convex table, DB, file, or RAM).  
**Fail:** You cannot tell if anything survives past one response.

**Write down path:** ______________________

### 0.6 Find healing / retries

**Do:**
```bash
rg -n "retry|backoff|maxRetries|heal|escalate|not_found|transient" --glob '!node_modules'
```

**Pass:** Dedicated policy function **or** clear retry with a numeric cap.  
**Fail:** No matches, or only the word “retry” inside the prompt with no code.

**Write down path (or “NONE”):** ______________________

### 0.7 Find entry point

**Do:**
```bash
rg -n "if __name__|createServer|app\.(post|get)|webhook|export default function" -g 'main.*' -g '**/api/**' -g '**/route.ts'
cat README.md 2>/dev/null | head -80
```

**Pass:** README or `main`/API route shows how to send one message.  
**Fail:** No way to invoke the agent documented or obvious.

---

## 1. System prompt — how to check

**Open** the file from 0.2.

### 1.1 Single source

**Do:** Search the prompt’s first unique sentence across the repo.
```bash
rg -n "FIRST_FIVE_WORDS_OF_PROMPT" --glob '!node_modules'
```
**Pass:** Appears in 1–2 places (definition + loader).  
**Fail:** Copied into many files with different versions.

### 1.2 Length

**Do:** `wc -l` / `wc -w` on the prompt file, or scroll it.

| Result | Verdict |
|--------|---------|
| ~under 150–200 lines / readable in 2 min | Pass |
| Multi-page, many workflows | Fail — too fat |
| One line “helpful assistant” | Fail — too empty |

### 1.3 Required ideas present

**Do:** In the prompt file, search (Cmd/Ctrl+F) for these ideas (wording can differ):

| Search for | Pass if you find |
|------------|------------------|
| invent / guess / fabricate | Rule against inventing facts |
| tool | When to use tools |
| human / escalate / approve / ask | Stop and ask human |
| never / must not / do not | Hard rules section |

**Fail if:** None of these appear.

### 1.4 Tool JSON not pasted into prompt

**Do:** In the prompt, search for `"parameters"` or `"type": "object"` or long JSON blocks.

**Pass:** No full tool schemas in the prompt.  
**Fail:** OpenAI tool JSON pasted into the system prompt.

### 1.5 Secrets

**Do:**
```bash
rg -n "sk-|api[_-]?key\s*=\s*['\"][^'\"]+['\"]" -g '*prompt*' -g '*.md'
```
**Pass:** No real keys.  
**Fail:** Any live secret in prompt files.

---

## 2. Tool schemas — how to check

**Open** every tool definition from 0.3 (or list files in `tools/schemas/`).

### 2.1 Each tool has the three fields

**Do:** For each tool, verify these keys exist: `name` (or `function.name`), `description`, `parameters`.

**Pass:** All three present.  
**Fail:** Name only, or description empty.

### 2.2 Name quality

**Do:** Write every tool name in a list.

**Pass examples:** `get_inventory`, `create_task`, `close_task`, `send_supplier_chase`.  
**Fail examples:** `do`, `run`, `query`, `handle`, `action`, `do_stuff`, `process`.

**Rule of thumb:** name = verb + noun. If you can’t tell what it writes/reads from the name alone → fail.

### 2.3 Description quality (read out loud)

**Do:** For each description, answer three questions yourself:

1. What does it do?  
2. When should the model use it?  
3. When should it **not** use it?

**Pass:** All three answerable from the text.  
**Fail:** Description is only “Gets data” / “Updates the system.”

### 2.4 Parameters quality

**Do:** Open `parameters.properties` for each tool.

**Check:**
- [ ] Important fields are in `required` (e.g. `part_id` for get_inventory).
- [ ] Closed choices use `enum` (e.g. evidence types).
- [ ] No single required field named only `data` / `payload` / `input` typed as empty object — unless there is a strong reason.

**Pass:** Specific fields.  
**Fail:** `payload: {}` does everything.

### 2.5 Count tools sent in one turn

**Do:** Find where schemas are passed to the model (in agent/model client). Count the array length.

| Count | Verdict |
|------|---------|
| 1–10 | Usually fine |
| 10–20 | OK if descriptions are sharp |
| 20+ with no subsetting | Weak — expect wrong tool choice |

### 2.6 Schemas actually passed to the API

**Do:** In model client / agent, find the OpenAI/Anthropic call.

**Pass:** You see `tools=` / `tools:` argument set from your schema list.  
**Fail:** Schemas defined in a file but never passed into the call (dead code).

---

## 3. Tool handlers — how to check

**Open** dispatch from 0.4.

### 3.1 Router exists

**Do:** Confirm there is a map or switch: tool name string → function.

**Pass:** `HANDLERS["create_task"](...)` or equivalent.  
**Fail:** Model tool name strings never appear in handler code.

### 3.2 Return shape

**Do:** Read what a handler returns. Or add a temporary log if you’re allowed to run.

**Pass:** Returns a dict/object (`{ ok, ... }` or clear fields).  
**Fail:** Only `print`, or returns `None` with side effects undocumented.

### 3.3 Create returns an id

**Do:** Open any `create_*` handler.

**Pass:** Response includes `id` / `task_id` / `_id`.  
**Fail:** Creates in DB but returns `{ ok: true }` only — model can’t refer to it later.

### 3.4 Unknown tool

**Do:** Read dispatch default branch.

**Pass:** Explicit error for unknown name.  
**Fail:** Crash or silent no-op.

### 3.5 Writes hit the store

**Do:** From a write handler, jump to the function it calls (mutation/repo). Confirm insert/update.

**Pass:** Clear write to Convex/DB.  
**Fail:** Handler returns fake success without writing.

---

## 4. Skills — how to check

### 4.1 Find skills

**Do:**
```bash
ls skills 2>/dev/null; ls agent/skills 2>/dev/null
rg -n "skill|playbook|workflow" -g '*.md' --glob '!node_modules' | head -40
```

### 4.2 Are they separate files?

**Pass:** One workflow ≈ one file.  
**Fail:** All workflows pasted only inside the system prompt with no modules.

### 4.3 How many skills go to the model?

**Do:** Find code that reads skill files and builds messages.
```bash
rg -n "skills/|readFile.*skill|selectSkill|select_skill|loadSkill" --glob '!node_modules'
```

**Then read that function and ask:** does it append **one** skill or **loop all** skills into messages?

| Behavior | Verdict |
|----------|---------|
| Select one (or none), then append | Pass |
| `for skill in all: messages.push(skill)` | Fail |

### 4.4 Matching criteria visible?

**Do:** Read the selector. Note the mode:

| What you see in code | Pattern |
|----------------------|---------|
| `triggers` / `includes(keyword)` | Keywords |
| `skillId` argument required | Explicit |
| `session.skill` reused | Sticky |
| Extra model call to classify | Router model |

**Pass:** You can explain the rule in one sentence.  
**Fail:** Skills load randomly / always / never with no rule.

### 4.5 Skill file contents

**Open one skill.** Check for sections (headings or clear paragraphs):

- [ ] When to use  
- [ ] Steps  
- [ ] Tools to use  
- [ ] Ask human / boundaries  
- [ ] Done = evidence  

**Pass:** At least when-to-use + steps + tools.  
**Fail:** Empty or only a title.

---

## 5. Agent loop — how to check

**Open** the loop from 0.1.

### 5.1 Order of operations

**Do:** Read top to bottom. Tick:

- [ ] Load prompt / memory / state  
- [ ] Call model with messages + tools  
- [ ] If tool_calls → dispatch  
- [ ] Append tool results to messages  
- [ ] Loop or return  

**Pass:** That order exists.  
**Fail:** Tools run but results never appended; or model called once with no loop though tools are expected.

### 5.2 Max turns

**Do:**
```bash
rg -n "max_turns|maxTurns|MAX_STEPS|for .* in range\(|Array\.from\(\{ length" --glob '!node_modules'
```

**Pass:** Numeric cap (e.g. 8). Write the number: ___.  
**Fail:** `while (true)` with no break condition except model silence — and even then risky if model always calls tools.

### 5.3 Stop condition

**Do:** Find what happens when `tool_calls` is empty/missing.

**Pass:** Return final assistant text / end run.  
**Fail:** Continues looping anyway.

### 5.4 Tool message format

**Do:** Find where tool output is pushed into `messages`.

**Pass:** Role is `tool` (or provider equivalent) and `tool_call_id` matches.  
**Fail:** Tool output appended as `user` with no id — model may ignore or mis-bind.

---

## 6. Long-horizon memory — how to check

### 6.1 Is there durable state at all?

**Do:** From 0.5, open the store. Ask: if I restart the server, does a created task still exist?

| Storage | How to verify |
|---------|----------------|
| Convex | Table in `schema.ts` + mutation insert; restart app, query still returns row |
| SQL/file | Same idea |
| Module-level `dict` / array | **Not** durable — demo only |

**Pass for “long-horizon claim”:** Durable store for jobs/facts.  
**Fail:** Only `messages` array in RAM.

### 6.2 What gets written?

**Do:** Find `save` / `insert` / `mutation` after tools.
```bash
rg -n "insert\(|createJob|save\(|facts\.push|memory\.save" --glob '!node_modules'
```

**Pass:** Saves job id, status, owner, or explicit facts.  
**Fail:** No write path after `create_*`.

### 6.3 What gets loaded next turn?

**Do:** Find load before model call.
```bash
rg -n "load\(|getOpenJobs|listMessages|memory\.load" --glob '!node_modules'
```

**Pass:** Load injects open jobs / facts / recent messages into context.  
**Fail:** Every turn starts with empty history and empty DB read.

### 6.4 Practical test (if you can run)

1. Send: create a task / shortage message.  
2. Note returned `task_id`.  
3. New message in **same session**: “What’s the open task id?”  
4. **Pass:** Agent uses the real id. **Fail:** Doesn’t know / invents.

### 6.5 Restart test (if durable claimed)

1. Create task.  
2. Restart server / reload.  
3. Same session id.  
4. **Pass:** Task still queryable. **Fail:** Gone.

### 6.6 Context bloat check

**Do:** Read memory loader. Is there `slice(-N)`, `limit`, `take(10)`?

**Pass:** Cap on messages/facts.  
**Fail:** Append forever with no limit.

### 6.7 Secrets in memory?

**Do:**
```bash
rg -n "api_key|password|authorization" -g '*memory*' -g '*store*' 
```
**Pass:** Not stored as memory facts.  
**Fail:** Full headers/secrets persisted into memory tables.

---

## 7. Self-healing — how to check

### 7.1 Is policy in code?

**Do:** Open file from 0.6. If NONE → fail this section (prompt-only “retry” doesn’t count).

### 7.2 Classification exists?

**Do:** Look for branches on error type/message (`timeout`, `not_found`, `404`, `validation`).

**Pass:** Different actions for different errors.  
**Fail:** Every error → same `retry()`.

### 7.3 Cap

**Do:** Find numeric attempt limit.

**Pass:** e.g. `attempt < 2` or `maxRetries: 2`.  
**Fail:** Unlimited retries.

### 7.4 not_found behavior

**Do:** Trace what happens on missing entity (fake an unknown id if you can run).

**Pass:** Stops or escalates; does **not** call the same tool 10 times.  
**Fail:** Retry storm.

### 7.5 Failure visible to model/user?

**Do:** On failure, is `{ ok: false, error }` appended as tool result and/or job set to `blocked`?

**Pass:** Yes.  
**Fail:** Exception caught, empty success returned.

---

## 8. Verification / close — how to check

### 8.1 Find close/complete tool

**Do:**
```bash
rg -n "close_task|completeTask|markDone|evidence" --glob '!node_modules'
```

### 8.2 Evidence required?

**Do:** Open schema for that tool. Check `required` includes evidence fields. Open handler: does it throw if evidence missing?

**Pass:** Schema + handler both require proof.  
**Fail:** Either allows close with only a chat “done”.

### 8.3 Runtime test (if runnable)

Send: “Mark the task done” with no receipt/photo.  
**Pass:** Refuses / asks for evidence.  
**Fail:** Closes.

---

## 9. Approvals & safety — how to check

### 9.1 Boundaries written?

**Do:** Search prompt + skills for: `approve`, `human`, `do not replan`, `must ask`.

**Pass:** Explicit list of forbidden auto-actions.  
**Fail:** Nothing.

### 9.2 Dangerous tools gated?

**Do:** List write tools that email, pay, delete, change schedule. Check for approval tool or human flag.

**Pass:** Gate exists or tool not exposed.  
**Fail:** Open `replan_production` with no approval.

### 9.3 Args validated in code?

**Do:** In handlers, look for enum checks / zod / pydantic / manual `if evidence_type not in ...`.

**Pass:** Validation in code.  
**Fail:** Trust model JSON blindly.

---

## 10. Observability — how to check

### 10.1 Tool traces

**Do:**
```bash
rg -n "tool_run|toolRun|trace|log.*tool" --glob '!node_modules'
```

**Pass:** Each tool call stored or logged with name, args, ok.  
**Fail:** No history — you can’t RCA.

### 10.2 Active skill logged?

**Do:** Search if selected skill id is logged or returned in response.

**Pass:** You can see `skill: investigate_shortage` in logs/result.  
**Fail:** Unknown which skill ran.

### 10.3 Can you answer “why tool X?”

**Do:** Mentally pick a past run. If you have traces + descriptions, you can RCA. If not → fail.

---

## 11. Evals — how to check

**Do:**
```bash
ls evals 2>/dev/null; ls tests 2>/dev/null
rg -n "expect|cases\.jsonl|toHaveBeenCalled|tool.*name" --glob '!node_modules' | head -30
```

**Pass:** At least a few cases with input + expected tool/behavior.  
**Fail:** No evals and no test for tool choice / no-retry / evidence.

**Minimum cases to look for (or add):**
1. Message should call `create_*`  
2. “Mark done” without proof should **not** close  
3. Unknown id should **not** retry forever  

---

## 12. Config & secrets — how to check

**Do:**
```bash
ls .env.example 2>/dev/null; ls .env.local.example 2>/dev/null
rg -n "process\.env|os\.getenv|OPENAI" --glob '!node_modules' | head -20
rg -n "sk-live|sk-proj" --glob '!node_modules' --glob '!.env*'
```

**Pass:** Env-based keys; example file without secrets; no sk- in tracked code.  
**Fail:** Key committed in source.

---

## 13. Architecture hygiene — how to check

**Do:** For one change (“edit tool description”), count files you must touch.

| Change | Should touch | Should NOT need to touch |
|--------|--------------|---------------------------|
| Tool description | schema JSON/TS | agent loop, healing |
| Retry policy | healing module | tool schemas |
| Shortage steps | one skill file | all prompts |
| Stock API URL | services | system prompt |

**Pass:** Change stays in the right layer.  
**Fail:** Editing a description requires rewriting the loop.

---

## 14. End-to-end “taste” drills (run these)

If the repo runs, do these four. If not, walk the code paths and predict.

| # | Input | How to check pass |
|---|--------|-------------------|
| 1 | Shortage-like message | Skill selected (log) + `create_task` (or equiv) called; job row exists with owner+due |
| 2 | “Check inventory for FAKE-PART” | `not_found` path; **≤1–2** attempts; no storm |
| 3 | “Mark it done” no proof | Close refused |
| 4 | Same session follow-up “what’s open?” | Real task id from store recalled |

---

## 15. Do’s and Don’ts (while fixing)

### Do
- Grep first, then open one spine file.
- Fix the **schema description** when the wrong tool is chosen.
- Put workflow steps in **one** skill; load **one** skill.
- Cap loops and retries with numbers you can point to.
- Persist job ids; load them next turn.
- Enforce evidence in **handler code**, not only in prose.
- Say your RCA out loud: “wrong layer is X, I’m changing Y.”

### Don’t
- Don’t dump all skills into the system message.
- Don’t add a mega-tool to “fix” routing.
- Don’t retry `not_found` in a loop.
- Don’t trust chat history as the database.
- Don’t close on “done” without evidence fields.
- Don’t paste secrets into prompts.
- Don’t accept AI suggestions that violate the above — AI is allowed, taste is the test.

---

## 16. Pattern cheat-sheet (identify which they used)

After 0.x mapping, circle one per row:

| Area | Options (pick what the code does) |
|------|-----------------------------------|
| Skill load | keywords / explicit / sticky / router model / **all dumped (bad)** |
| Tools sent | all schemas / skill subset / mega-tool (bad) |
| Memory | durable DB+selective / chat-only / unbounded dump (bad) |
| Healing | classify+cap / prompt-only / blind retry (bad) |
| Loop | capped while / graph / uncapped while (bad) |

---

## Related

- `06-interview-rca-and-solutions.md` — symptom → fix  
- `04-architecture-patterns.md` — when to use which pattern  
- `01-template-and-dataflow.md` — our template map  
