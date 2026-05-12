# Kata: Curate PoV Context Pack

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Agents (pre-operational stage): curate few-shot examples + domain negative examples to feed the PoV's context

## Objective

Produce `docs/{context}/agents-pov/{agent}/context-pack.md` with 3-5 real few-shot examples and 2-3 curated negative examples (anti-patterns observed in a basic LLM for the domain). Apply Directive 06 of `lex-agent-construction-directives` (Rich Context) in PoV context. The context-pack is the **asset that feeds `--from-pov`** when the agent matures: Mêtis uses these examples as a starting point for the production context-pack.

## When to Use

- After `kata-pov-scope-define` (overview ready)
- After `kata-pov-system-prompt` (to align tone and example format)
- When a round of PoV operation reveals new anti-patterns to curate

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `docs/{context}/agents-pov/{agent}/pov.md` | Yes | Primary use case |
| `docs/{context}/agents-pov/{agent}/system-prompt.md` | Yes | Expected output format |
| Domain knowledge | Yes | Customer domain knowledge (interviews, docs, samples) |
| `--inputs-dir <path>` | No | Directory with anonymized real data to inspire examples |

## Workflow

```
Progress:
- [ ] 1. Read overview + system-prompt
- [ ] 2. Collect 3-5 representative real inputs
- [ ] 3. Write positive few-shot examples (input → ideal answer)
- [ ] 4. Identify 2-3 anti-patterns and write negative examples
- [ ] 5. Anonymize PII (lex-data-retention)
- [ ] 6. Persist context-pack.md
```

### Step 1: Read overview + system-prompt

1. Read both files.
2. Note: primary use case, expected output format, prompt restrictions.

### Step 2: Collect 3-5 representative real inputs

1. Cover the **use-case space**: easy case, medium case, ambiguous case. Not 5 versions of the same scenario.
2. If `--inputs-dir` was passed, list and select; otherwise ask the user for 3-5 real inputs. **Without real inputs, the kata aborts** — an invented context-pack is a direct violation of Directive 06.

### Step 3: Write positive few-shot examples

For each selected input:

- **Input block:** literal data (anonymized)
- **Ideal answer:** what the agent **should** produce, in the format declared in `system-prompt.md`

Examples follow the `<input> → <output>` template consistent with the prompt's output style. Avoid over-engineering: the ideal answer is what the customer would accept, not a perfectionist ideal.

### Step 4: Identify 2-3 anti-patterns and write negative examples

Typical anti-patterns in a basic LLM for the domain:

- **Hallucination:** invents an ID/value missing from the input
- **Over-confidence:** says "high confidence" when data is insufficient
- **Out-of-scope drift:** answers about a secondary, undeclared use case
- **Format breakage:** breaks the format declared in the prompt

For each anti-pattern, write:

- **Input block:** the case that triggered the error
- **❌ Undesired answer:** what the basic LLM produced
- **✅ Correct answer:** what it should have produced (same structure as the positive few-shot examples)

### Step 5: Anonymize PII

Apply `lex-data-retention`:

- Remove or mask: tax IDs, e-mail, phone, full name, address
- Keep: input structure (fields, patterns), quantitative values (with light obfuscation if sensitive)
- Mark each example with `# Origin: anonymized from customer data on <date>` for traceability

### Step 6: Persist context-pack.md

Write `docs/{context}/agents-pov/{agent}/context-pack.md` with sections: Positive few-shot examples (3-5), Anti-patterns (2-3), Anonymization notes, Quality criteria applied.

### Final Validation

- [ ] 3 to 5 positive few-shot examples covering representative cases
- [ ] 2 to 3 anti-patterns with `❌` and `✅`
- [ ] Zero PII (tax IDs, full name, e-mail)
- [ ] Examples derived from real inputs (not fictional)
- [ ] Few-shot output format is consistent with `system-prompt.md`

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| `context-pack.md` | Markdown | `docs/{context}/agents-pov/{agent}/context-pack.md` |

## Execution Example

### Output (context-pack.md, excerpt)

```markdown
## Positive few-shot examples

### Example 1 (easy case)

**Input:**
- Statement: TX-001 | 2026-04-01 | $ 1,200.00 | "Rent ref 04/26"
- Entries:
  - L-100 | 2026-04-01 | $ 1,200.00 | "PAY RENT APR/26"
  - L-101 | 2026-04-02 | $ 350.00 | "INTERNET"

**Ideal answer:**
TX-001 ↔ L-100 | confidence: high | basis: value + date + similar description

### Example 2 (medium case — divergent description)
...

## Anti-patterns

### Anti-pattern A: ID hallucination

**Input:**
- Statement: TX-007 | 2026-04-15 | $ 500.00 | "PIX 12345"
- Entries: (empty for that window)

**❌ Undesired answer:**
TX-007 ↔ L-999 | confidence: high
(L-999 does not exist in the entries — hallucination.)

**✅ Correct answer:**
TX-007 ↔ no candidate | confidence: n/a | note: manual review required.
```

## Restrictions

- **Never** a context-pack with invented examples — Directive 06 requires real data.
- **Never** PII in the final file — `lex-data-retention` applies.
- **Never** fewer than 3 or more than 5 positive few-shot examples. The band encodes the trade-off between coverage and noise.
- **Always** mark each example's origin (anonymization date stamp) to trace retrofit.

---

**Model:** This Kata applies Directive 06 (`lex-agent-construction-directives`). The context-pack is the most transferable asset to Mêtis via `--from-pov`.
