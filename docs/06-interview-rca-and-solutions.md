# Morsa interview — problems → RCA → where → fix

Use when something breaks in **their shared repo** (or yours).  
Interview focus: harness taste — system prompt, tools, skills, long-horizon memory, self-healing (Convex + OpenAI).

**How to read each row**

| Field | Meaning |
|-------|---------|
| Problem | What you observe |
| RCA | Likely root cause |
| Where | File / layer to open first |
| Fix | What good taste looks like |

Related: `03-navigation-and-rca.md`, `05-harness-taste-checklist.md`.

---

## A. Nothing runs / setup

### A1. Repo won’t start
| | |
|--|--|
| **Problem** | `npm`/`pnpm`/`pip` fails; Convex not linked; env missing |
| **RCA** | Missing deps, wrong Node/Python, no `.env`, Convex not initialized |
| **Where** | `README`, `package.json` / `requirements.txt`, `.env.example`, `convex/` |
| **Fix** | Follow their README exactly. Copy env example. Create Convex account/project. Don’t invent a second stack. Ask once if blocked on credentials. |

### A2. OpenAI key errors
| | |
|--|--|
| **Problem** | 401 / missing API key |
| **RCA** | Key not in env; wrong var name; key not passed into client |
| **Where** | `.env`, model client module, Convex env dashboard |
| **Fix** | Use the key they give; match their env var name (`OPENAI_API_KEY` etc.). Don’t hardcode the key in source. |

### A3. Convex deploy / schema push fails
| | |
|--|--|
| **Problem** | Schema reject, auth error, functions won’t sync |
| **RCA** | Invalid schema, not logged in, wrong project |
| **Where** | `convex/schema.ts`, Convex CLI output |
| **Fix** | Fix schema types; `npx convex dev` as they document; don’t fight the platform — adapt to their patterns. |

---

## B. Agent loop / orchestration

### B1. Agent never answers
| | |
|--|--|
| **Problem** | Hangs or returns empty |
| **RCA** | Loop waiting on tools forever; no stop when model returns text; max turns missing; swallowed exception |
| **Where** | Agent / runner loop |
| **Fix** | Cap turns. Stop when there are **no** `tool_calls`. Surface errors to the UI/logs. |

### B2. Agent loops forever calling tools
| | |
|--|--|
| **Problem** | Same tool again and again |
| **RCA** | No max turns; tool result not fed back; prompt says “keep going”; healing retries forever |
| **Where** | Agent loop, healing/retry, system prompt |
| **Fix** | `max_turns`. Append tool results correctly. Healing: cap retries. Prompt: stop when blocked. |

### B3. Tool results ignored
| | |
|--|--|
| **Problem** | Model asks for same info again / invents numbers after a tool ran |
| **RCA** | Tool message not appended; wrong role/`tool_call_id`; result truncated/empty |
| **Where** | Agent loop message assembly, model client |
| **Fix** | After each tool: append proper tool message with matching id + full structured result. |

### B4. Parallel tool calls blow up
| | |
|--|--|
| **Problem** | Crash when model returns multiple tools |
| **RCA** | Code assumes one tool_call |
| **Where** | Agent loop |
| **Fix** | Iterate all `tool_calls`; append all results before next model call (or document serial-only and enforce). |

---

## C. System prompt taste

### C1. Agent ignores rules
| | |
|--|--|
| **Problem** | Invents stock, closes without proof, ignores “ask human” |
| **RCA** | Prompt vague; rules buried; no code gate |
| **Where** | System prompt **and** close/write tool handlers |
| **Fix** | Short hard rules in prompt. **Also** enforce in code (`close_task` requires evidence enum). Taste = prompt + code. |

### C2. Prompt too long / confused behavior
| | |
|--|--|
| **Problem** | Inconsistent, misses instructions |
| **RCA** | Novel-length prompt; workflows + tools + memory policy all dumped in system |
| **Where** | System prompt, skills |
| **Fix** | Slim system prompt. Move workflows to **one** skill. Tools stay in schemas. |

### C3. Prompt duplicates tool schemas
| | |
|--|--|
| **Problem** | Drift: prompt says one thing, schema another |
| **RCA** | Schemas pasted into markdown |
| **Where** | Prompt vs `tools` schemas |
| **Fix** | Single source of truth = tool schema files. Prompt only says “use tools; don’t invent.” |

---

## D. Tools & descriptions

### D1. Model never calls tools
| | |
|--|--|
| **Problem** | Answers from imagination |
| **RCA** | Tools not passed to API; descriptions say nothing; prompt doesn’t push tools for facts |
| **Where** | Model client (`tools=`), tool schemas, system prompt |
| **Fix** | Pass schemas every turn. Description: when to use. Prompt: don’t guess facts. |

### D2. Model calls the wrong tool
| | |
|--|--|
| **Problem** | `close_task` instead of `create_task`, etc. |
| **RCA** | Vague names (`update`, `handle`); overlapping descriptions; too many tools visible |
| **Where** | Tool schema **descriptions** and names |
| **Fix** | Specific names. “When to use / when not.” Skill subset if catalog is large. |

### D3. Bad arguments / JSON parse errors
| | |
|--|--|
| **Problem** | Handler crashes on args |
| **RCA** | Weak parameter schema; no enum; no validation in handler |
| **Where** | Tool `parameters`, dispatch/handler |
| **Fix** | Tighten JSON schema (required, enum). Validate in code. Healing: `bad_args` → repair once then stop. |

### D4. Mega-tool / god function
| | |
|--|--|
| **Problem** | Unreliable, unsafe |
| **RCA** | `do_action(payload)` design |
| **Where** | Tool definitions |
| **Fix** | Split into specific tools. Interview signal: propose the split and why. |

### D5. Tool succeeds but state wrong
| | |
|--|--|
| **Problem** | “Created” but no row / wrong session |
| **RCA** | Handler didn’t write DB; missing `sessionId`; write to wrong table |
| **Where** | Tool handler, Convex mutation, repositories |
| **Fix** | Mutation must write. Thread session/job id. Return new id in tool result. |

### D6. Duplicate creates on retry
| | |
|--|--|
| **Problem** | Two tasks for one shortage |
| **RCA** | Retrying a write tool with no idempotency key |
| **Where** | Healing + create handler |
| **Fix** | Don’t retry creates blindly. Idempotency key (client token) or check existing open job first. |

---

## E. Skills

### E1. Wrong skill loaded
| | |
|--|--|
| **Problem** | Shortage message gets quoting skill |
| **RCA** | Overlapping triggers; no tie-break; sticky skill stuck |
| **Where** | Skill router, skill frontmatter triggers, session sticky id |
| **Fix** | More specific triggers. Tie-break (longest match). Clear sticky on topic change or new intent. |

### E2. No skill loaded when one should
| | |
|--|--|
| **Problem** | Generic weak behavior |
| **RCA** | Triggers don’t match wording; skill file missing frontmatter; router skipped |
| **Where** | Skill markdown triggers, `select_skill` call in agent |
| **Fix** | Add real phrases from the eval/case. Confirm agent calls router before model. |

### E3. All skills dumped into context
| | |
|--|--|
| **Problem** | Confusion, cost, wrong steps |
| **RCA** | No shortlist — concatenate all skill files |
| **Where** | Agent message builder |
| **Fix** | Load **at most one** skill. Say this out loud in the interview — it’s taste. |

### E4. Skill fights system prompt
| | |
|--|--|
| **Problem** | Contradictory instructions |
| **RCA** | Skill restates/overrides hard rules |
| **Where** | System prompt vs skill body |
| **Fix** | System = global hard rules. Skill = steps for one workflow only. |

---

## F. Long-horizon memory & durable state

### F1. Forgets task id next turn
| | |
|--|--|
| **Problem** | “What task?” after it just created one |
| **RCA** | Id only in chat; not saved; memory not loaded next turn |
| **Where** | Repositories/Convex tables, memory load/save, agent |
| **Fix** | Persist job in DB. On load, inject open job ids/facts. Don’t rely on chat alone. |

### F2. Forgets after refresh / restart
| | |
|--|--|
| **Problem** | Works in one process, gone later |
| **RCA** | In-memory only; Convex not written; wrong session id |
| **Where** | Store layer, session id from client |
| **Fix** | Write Convex/DB. Stable `sessionId` from UI. Label RAM stores as demo-only. |

### F3. Context too large / slow / confused
| | |
|--|--|
| **Problem** | Truncation, high cost, lost instructions |
| **RCA** | Full transcript + all tool dumps every turn |
| **Where** | Memory loader |
| **Fix** | Window last N messages + selected facts. Compact old turns. Never embed secrets. |

### F4. Stale or wrong facts
| | |
|--|--|
| **Problem** | Acts on outdated “PO delayed Friday” |
| **RCA** | No overwrite; guesses stored as facts; no TTL |
| **Where** | Memory write path |
| **Fix** | Store only confirmed facts. Newer overrides older. Optional expiry. Escalate conflicts. |

### F5. Mixed sessions / data leak between users
| | |
|--|--|
| **Problem** | Sees another chat’s jobs |
| **RCA** | Missing or shared session key |
| **Where** | Session id plumbing, queries |
| **Fix** | Scope all reads/writes by session (and org if multi-tenant). |

### F6. “Memory” is only embeddings junk
| | |
|--|--|
| **Problem** | Irrelevant recalls |
| **RCA** | Vectored everything including tool noise |
| **Where** | Ingest pipeline |
| **Fix** | Durable jobs in tables. Vectors only for notes that need fuzzy search. Prefer entity keys (po_id, part_id). |

---

## G. Self-healing

### G1. Retry storm
| | |
|--|--|
| **Problem** | Same failing tool 20× |
| **RCA** | Blind retry; prompt “keep trying”; no classify |
| **Where** | Healing / retry helper, agent catch block |
| **Fix** | Classify: transient → retry ≤2; `not_found` → stop; else escalate. Log each attempt. |

### G2. Gives up with no state
| | |
|--|--|
| **Problem** | Silent fail; user thinks it worked |
| **RCA** | Exception swallowed; no blocked status |
| **Where** | Agent error path, job status updates |
| **Fix** | Mark job `blocked`. Return clear error + healing reason. |

### G3. Retries a write after partial success
| | |
|--|--|
| **Problem** | Duplicates / double email |
| **RCA** | Treating write errors as transient without idempotency |
| **Where** | Healing policy for write tools |
| **Fix** | Different policy for reads vs writes. Idempotent mutations. |

### G4. Model “heals” by inventing success
| | |
|--|--|
| **Problem** | Says done though tool failed |
| **RCA** | Failure not shown in tool message; prompt allows guessing |
| **Where** | Tool result payload, system prompt |
| **Fix** | Tool message includes `{ ok: false, error }`. Prompt: never invent success. |

---

## H. Verification / “done” (Morsa-shaped)

### H1. Closes on “ok done” in chat
| | |
|--|--|
| **Problem** | Job closed with no proof |
| **RCA** | No evidence requirement; prompt-only rule |
| **Where** | `close_*` schema + handler |
| **Fix** | Require `evidence_type` + `evidence_ref`. Handler rejects empty. |

### H2. Wrong evidence accepted
| | |
|--|--|
| **Problem** | Random string closes job |
| **RCA** | No enum / no format check |
| **Where** | Schema enum, handler validation |
| **Fix** | Enum (`erp_receipt`, `photo_url`). Validate non-empty ref. |

---

## I. Convex-specific (likely in their repo)

### I1. Client can’t read new data
| | |
|--|--|
| **Problem** | UI stale after tool write |
| **RCA** | Wrote outside Convex; query not reactive; wrong query args |
| **Where** | Mutations vs actions, React hooks / `useQuery` |
| **Fix** | Prefer Convex mutation for state. Match query args to session. |

### I2. Action timeout / long OpenAI call
| | |
|--|--|
| **Problem** | Convex action times out |
| **RCA** | Too much work in one action; unbounded loop |
| **Where** | Convex action that calls OpenAI |
| **Fix** | Cap turns. Split work. Don’t hold action open forever. |

### I3. Schema doesn’t match writes
| | |
|--|--|
| **Problem** | Insert fails / fields undefined |
| **RCA** | Code writes fields not in `schema.ts` |
| **Where** | `convex/schema.ts`, mutations |
| **Fix** | Align fields. Migrate thoughtfully. |

### I4. Running OpenAI inside wrong place
| | |
|--|--|
| **Problem** | Can’t use fetch/secrets as expected |
| **RCA** | LLM call in a query (queries must be pure) |
| **Where** | Convex query vs action/mutation |
| **Fix** | LLM + external HTTP in **actions** (or their documented pattern). Queries read only. |

---

## J. Product / Morsa-shaped scenarios (they may use as stories)

### J1. Shortage message doesn’t create owned work
| | |
|--|--|
| **Problem** | Chat acknowledged, no task |
| **RCA** | No create tool / skill not loaded / model not instructed |
| **Where** | Skill, `create_task` tool, prompt |
| **Fix** | Skill steps + create tool with owner + due_at. Eval case for it. |

### J2. Inventory guessed
| | |
|--|--|
| **Problem** | Agent invents qty |
| **RCA** | No get_inventory tool or not forced |
| **Where** | Tool + prompt |
| **Fix** | Tool for stock. Prompt: never invent qty. |

### J3. Escalation never happens
| | |
|--|--|
| **Problem** | Idle work sits forever |
| **RCA** | No blocked/escalate path; no human gate tool |
| **Where** | Healing, job status, prompt boundaries |
| **Fix** | After N failures or out-of-policy → escalate / ask human; set `blocked`. |

### J4. Approval boundary violated
| | |
|--|--|
| **Problem** | Agent “replans the line” alone |
| **RCA** | No boundary in prompt/skills; no missing approval tool |
| **Where** | System prompt, skill boundaries, tools available |
| **Fix** | Explicit ask-human for replan/customer promise. Don’t expose an ungoverned replan tool. |

---

## K. Evals & demo pressure

### K1. Demo works once, fails on second phrasing
| | |
|--|--|
| **Problem** | Brittle triggers / prompt |
| **RCA** | Overfit to one sentence |
| **Where** | Skill triggers, evals |
| **Fix** | Add 2–3 phrasings to triggers + eval cases. |

### K2. Can’t prove taste quickly
| | |
|--|--|
| **Problem** | Interviewer asks “why is this good?” |
| **RCA** | No before/after; no eval |
| **Where** | Your narration + small eval case |
| **Fix** | Show: bad description → wrong tool; fixed description → right tool. Show healing table. |

### K3. AI assistant suggests a bad harness change
| | |
|--|--|
| **Problem** | Copilot wants mega-tool or dump-all-skills |
| **RCA** | Generic AI defaults ≠ harness taste |
| **Where** | Your judgment (AI is allowed — taste is the test) |
| **Fix** | Reject. Cite: one skill, sharp tools, classify retries, durable jobs. |

---

## L. Collaboration / interview process

### L1. Don’t understand their layout
| | |
|--|--|
| **Problem** | Lost in folders |
| **RCA** | Different names than our template |
| **Where** | Search for: `tools`, `prompt`, `memory`, `retry`, `schema` |
| **Fix** | Map their names → our layers (entry / loop / schemas / store / healing). Say the mapping out loud. |

### L2. Scope too big for time
| | |
|--|--|
| **Problem** | Trying to rebuild everything |
| **RCA** | No thin slice |
| **Where** | — |
| **Fix** | Pick one path: tighten 1 tool description + 1 healing rule + 1 memory save. Ship that. Explain next steps. |

### L3. Stuck on a platform detail
| | |
|--|--|
| **Problem** | Convex/API rabbit hole |
| **RCA** | Perfecting infra vs showing taste |
| **Where** | — |
| **Fix** | Stub with a clear TODO; implement the policy (prompt/tool/memory/heal) that shows judgment. |

---

## Quick index — symptom → section

| You see… | Go to |
|----------|--------|
| Won’t boot / key / Convex | A |
| Hang / infinite tools | B |
| Ignores rules / huge prompt | C |
| Wrong/missing tool calls | D |
| Wrong or all skills | E |
| Forgets / restart / huge context | F |
| Retry spam / silent fail | G |
| Closes without proof | H |
| Convex query/action/schema | I |
| Shortage / inventory / escalate story | J |
| Brittle demo / AI bad suggestion | K |
| Lost / too much scope | L |

---

## Script you can say while fixing

1. “I’m treating this as a harness issue in **[layer]**.”  
2. “RCA: **[one sentence]**.”  
3. “I’ll change **[file]** to **[specific fix]**.”  
4. “I won’t **[anti-pattern]** because …”  
5. “Eval I’d add: **[input → expect]**.”  
