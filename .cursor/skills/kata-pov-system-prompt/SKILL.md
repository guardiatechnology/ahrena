---
name: kata-pov-system-prompt
description: "Write PoV System Prompt. Engineering — Agents (pre-operational stage): write a PoV's minimum viable system prompt with an explicit stage: pre-operational declaration"
---

# Kata: Write PoV System Prompt

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Agents (pre-operational stage): write a PoV's minimum viable system prompt with an explicit `stage: pre-operational` declaration

## Workflow

```
Progress:
- [ ] 1. Read pov.md and extract persona/scope
- [ ] 2. Write Identity block (with stage: pre-operational)
- [ ] 3. Write Capabilities block (minimum viable)
- [ ] 4. Write Restrictions block (minimum viable)
- [ ] 5. Write Output style block (1-2 lines)
- [ ] 6. Validate minimal adversarial via kata-system-prompt-adversarial-validate
- [ ] 7. Persist system-prompt.md
```

### Step 1: Read pov.md and extract persona/scope

1. Read `docs/{context}/agents-pov/{agent}/pov.md`.
2. Extract: persona (1 sentence), primary use case, value metric, discontinuation criterion.
3. Confirm `pov.md` contains `stage: pre-operational`. If absent, return to `kata-pov-scope-define` (do not try to fix here).

### Step 2: Write Identity block

Minimum viable block of the 4 required by `lex-system-prompt`:

```
# Identity

You are {PoV name}, an assistant at the **pre-operational** stage focused on
{primary use case extracted from pov.md}.

stage: pre-operational
```

The `stage: pre-operational` line is **literal** and required — it is the hook that `kata-dooc-validate` (plan-032) will inspect at item 9.

### Step 3: Write Capabilities block

```
# Capabilities

You can:
- {capability 1, aligned with the primary use case}
- {capability 2, optional, still inside the scope}
```

Maximum 3 capabilities. More than that breaks Directive 05 (Restricted Scope).

### Step 4: Write Restrictions block

```
# Restrictions

You cannot:
- Execute actions outside the primary use case declared in pov.md
- Persist data beyond the current context window (no persistent memory)
- Override the discontinuation criterion or change the value metric
```

Additional restrictions come from `pov.md::Out of scope` (literal copy).

### Step 5: Write Output style block

```
# Style

Short, direct answers, in {language of `language.default`}. Cite context evidence
when applicable. Never make up data not received.
```

### Step 6: Validate minimal adversarial

Invoke `kata-system-prompt-adversarial-validate` in `--minimum-viable` mode:

- Reduced suite: trivial prompt injection, instruction exfiltration, basic jailbreak
- Full suite (5 OWASP controls) remains for when the agent is promoted to `operational-concrete`
- If it passes → proceed; if it fails → harden the corresponding restriction and re-run

### Step 7: Persist system-prompt.md

1. Write `docs/{context}/agents-pov/{agent}/system-prompt.md` with the 4 blocks.
2. At the file footer, annotate: `# Notes`, `kata-pov-system-prompt`, date, hash of the consumed `pov.md` (for traceability).

### Final Validation

- [ ] System prompt has the 4 blocks (Identity, Capabilities, Restrictions, Style)
- [ ] The `stage: pre-operational` line appears literally in the Identity block
- [ ] Minimal adversarial suite passes
- [ ] Restrictions copy the overview's `Out of scope` literally
- [ ] No remaining `{...}` placeholders

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| `system-prompt.md` | Markdown (system prompt) | `docs/{context}/agents-pov/{agent}/system-prompt.md` |

## Execution Example

### Input (pov.md, excerpt)

```
Persona: Assistant that suggests bank-statement-to-ledger-entry pairings.
stage: pre-operational
Value metric: % automatic reconciliation ≥ 60% in 4 weeks.
```

### Output (system-prompt.md, excerpt)

```
# Identity

You are the Reconciliation Assistant, at the pre-operational stage, focused on
suggesting pairings between bank statement transactions and ERP ledger entries
from the same time window.

stage: pre-operational

# Capabilities

You can:
- Suggest the most likely pairing by value + date + similar description
- Indicate confidence level (high / medium / low) per suggestion

# Restrictions

You cannot:
- Create ERP entries (suggest only)
- Reconcile across distinct accounts
- Detect fraud
- Persist data outside the current context window

# Style

Short, direct answers, in English. Cite the transaction ID and the entry ID.
Never make up data not received in the context.
```

## Restrictions

- **Never** omit `stage: pre-operational` — blocks DoOC.
- **Never** production templates (full OWASP controls, complex tools) — scope is minimum viable.
- **Never** more than 3 capabilities. Forcing reduction beats inflating.

---

**Model:** This Kata applies Directive 01 (`lex-agent-construction-directives`) at pre-operational rigor. Production templates belong to `kata-system-prompt-author` (Mêtis) — not to this kata.
