# Kata: Artifact Self-Review

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Pre-human self-review of any artifact produced by an agent — Lexis, Codex, Kata, Warrior, Cry, PRD, Capability Spec, ADR, release plan, PLR, wireframes

## Objective

Before submitting any artifact for human review, the agent that produced the artifact MUST run this Kata to detect common defects: forgotten placeholders, internal contradictions, quantifiable ambiguities, scope drift, empty sections, vocabulary outside Guardia tone, divergence between multilingual versions.

Self-review reduces iteration with humans (fixes obvious defects before review) and strengthens the delivered output. Inspired by the Spec Self-Review pattern in the `brainstorming` skill of [obra/superpowers](https://github.com/obra/superpowers).

## When to Use

- Before submitting a new artifact (Lexis, Codex, Kata, Warrior, Cry) to `kata-push-to-framework` or human review
- Before closing PRD, Capability Spec, ADR
- Before closing release plan or PLR
- Before any orchestrator warrior delivers a package to a human Gate

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Artifact to review | Yes | Absolute or relative path to the Markdown file |
| Artifact type | Yes | One of: `lexis`, `codex`, `kata`, `warrior`, `cry`, `prd`, `capability-spec`, `adr`, `release-plan`, `plr`, `wireframe-lf`, `wireframe-hf`, `insights`, `other` |
| Reference template | No | Path to the corresponding sample when the type has a canonical template |

## Workflow

```
Progress:
- [ ] 1. Placeholder scan
- [ ] 2. Internal contradictions scan
- [ ] 3. Quantifiable ambiguities scan
- [ ] 4. Scope drift scan
- [ ] 5. Empty sections and incomplete structure scan
- [ ] 6. Tone and vocabulary scan
- [ ] 7. Multilingual equivalence verification (when applicable)
- [ ] 8. Consolidated report
```

### Step 1: Placeholder scan

Look for unfilled markers: `TBD`, `TODO`, `FIXME`, `XXX`, intentional template bracket text (`[Law Name]`, `[description]`), ellipses in declarative content, generic strings (`Lorem ipsum`, `placeholder`, `insert here`), empty headings.

For each finding: location (line), problematic content, action (fill / remove / convert to open question).

### Step 2: Internal contradictions scan

Verify consistency between sections:
- Law/Objective at the opening vs. Rules/Workflow in subsequent sections
- "Correct" and "Incorrect" examples aligned with the rules
- Inputs/outputs vs. Workflow — is each declared input consumed? is each output produced?
- Numbered criteria — does N in the Law match N in Automated Validation?

### Step 3: Quantifiable ambiguities scan

Identify vague statements: "many", "several", "fast", "simple", "complex", "reasonable", "high latency", "low cost".

For each: quantifiable alternative (e.g.: "many cases" → "≥80% of observed cases"; "fast" → "p99 ≤ 300ms"). Exception: ambiguity acceptable when the number will come in a later phase — document the postponement.

### Step 4: Scope drift scan

Verify that the artifact has not exceeded its scope:
- Lexis: addresses a single law? does not embed kata or codex?
- Capability Spec: follows the 8 rigid sections? does not invade technical design?
- Kata: describes ONE procedure?
- Warrior: orchestrates but does not execute?
- PRD: focuses on WHAT/WHY?

### Step 5: Empty sections and incomplete structure scan

Verify conformance with the canonical template (when exists):
- Are all mandatory sections present?
- Does each section have substantive content?
- Is the heading hierarchy correct?
- Is the frontmatter complete (when applicable to `.cursor/` or `.claude/`)?
- Do internal links resolve (not 404)?

### Step 6: Tone and vocabulary scan

Verify conformance with [lex-tone](framework/en/_foundation/quality/lexis/lex-tone.md) and — when public — [lex-brand-voice](framework/en/design/brand/lexis/lex-brand-voice.md):
- Forbidden buzzwords: "innovative", "disruptive", "transformative", "revolutionary", "fintech" (for Guardia)
- Correct RFC 2119 modal verbs: MUST/MUST NOT/SHOULD/MAY (en) or DEVE/NÃO DEVE/DEVERIA/PODE (pt-BR), DEBE/NO DEBE/DEBERÍA/PUEDE (es)
- Canonical terms preserved: Lexis, Codex, Katas, Warriors, Cries, Ahrena

### Step 7: Multilingual equivalence verification

When the artifact exists in multiple languages (per [lex-framework-language](framework/en/_foundation/i18n/lexis/lex-framework-language.md)):
- Same structure and order of sections
- Same number of numbered rules
- Tables with same number of rows
- Code blocks (HARD-GATE, examples) preserved without incorrect translation of tag/syntax
- Canonical terms preserved

### Step 8: Consolidated report

```markdown
# Self-Review Report — {artifact name}

> **Reviewer:** kata-artifact-self-review · **Date:** YYYY-MM-DD · **Type:** {type}
> **Result:** APPROVED | RETURNED FOR CORRECTION

## Findings by category

### 1. Placeholders
- (empty when 0 findings)
- {line N}: {description} → action: {recommendation}

### 2. Internal contradictions
### 3. Quantifiable ambiguities
### 4. Scope drift
### 5. Empty sections / structure
### 6. Tone and vocabulary
### 7. Multilingual equivalence

## Decision

- [ ] APPROVED — may submit for human review
- [ ] RETURNED — fix findings above and re-run this Kata
```

Submit artifact to human ONLY when the report indicates APPROVED.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Self-Review Report | Structured Markdown | inline (chat) or `docs/.review/{artifact}-{date}.md` |
| Decision APPROVED / RETURNED | Explicit boolean | part of the report |

## Execution Example

### Input

```
Artifact: framework/en/_foundation/quality/lexis/lex-hard-gate-pattern.md
Type: lexis
Template: framework/templates/lex-sample.md
```

### Output

```markdown
# Self-Review Report — lex-hard-gate-pattern.md

> **Reviewer:** kata-artifact-self-review · **Date:** 2026-04-30 · **Type:** lexis
> **Result:** APPROVED

## Findings by category

### 1. Placeholders
- (zero findings)

### 2. Internal contradictions
- (zero findings)

### 3. Quantifiable ambiguities
- (zero findings — declared metrics have verifiable criteria)

### 4. Scope drift
- (zero findings)

### 5. Empty sections / structure
- (zero findings — follows lex-sample.md)

### 6. Tone and vocabulary
- (zero findings — RFC 2119 correct; no buzzwords)

### 7. Multilingual equivalence
- (zero findings — pt-BR, en, es structurally equivalent)

## Decision

- [x] APPROVED — may submit for human review
```

## Restrictions

- This Kata **detects**, not **fixes** — correction is the responsibility of the agent that produced the artifact.
- Self-review **does not replace** human review — it is a pre-human phase, complementary.
- If the artifact fails multilingual equivalence, the agent MUST align all languages before submitting — do not submit partially.
- Whenever it returns RETURNED, the report MUST be preserved in `docs/.review/` for audit.
