# Lexis: HARD-GATE Pattern for Blocks in Lexis

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Syntax of textual blocks in framework Ahrena Lexis

## Law

> **Every Lexis that requires flow block — forbidden action with non-negotiable preconditions — MUST contain a literal `<HARD-GATE>` block explicitly stating subject, action, preconditions, scope, counter-pretexts, and exceptions. Lexis that declare textual "MUST" without this block, when there is effective blocking, are considered incomplete and MUST be revised to include it.**

## Rules

### 1. When to apply HARD-GATE

Apply when the Lexis:

- Blocks concrete action (create issue, merge PR, start rollout, deploy agent)
- Has preconditions verifiable programmatically or by checklist
- Does not admit implicit or case-by-case negotiable exceptions

DO NOT apply when the Lexis:

- Defines only convention (naming, casing) — textual `MUST` is sufficient
- Has multiple legitimate and contextual exceptions without single checklist
- Describes qualitative attribute without concrete blocking action

### 2. Canonical syntax

```
<HARD-GATE>
{Subject} MUST NOT {forbidden action in infinitive} {target of action}
without {minimum initial precondition}.

Mandatory preconditions:
  (a) {condition 1 — specific and verifiable}
  (b) {condition 2 — specific and verifiable}
  (c) {condition 3 — specific and verifiable}
  ...

This rule applies to {scope: EVERY feature / platform agents / etc.},
regardless of:
  - {counter-pretext 1 — e.g.: perceived size}
  - {counter-pretext 2 — e.g.: declared urgency}
  - {counter-pretext 3 — e.g.: team confidence}

Exception {single / declared}: {literal description or "None"}.
</HARD-GATE>
```

The 6 elements (subject, action, preconditions, scope, counter-pretexts, exception) are **mandatory**. Omitting any of them produces weak blocking.

### 3. Positioning in the Lexis

The `<HARD-GATE>` block MUST be:

- **After** the `Law` section (or `Rules` section when present), and before `Examples`
- Inside a fenced code block, with literal `HARD-GATE` tag on opening and closing lines
- In the **same section** that defines the verified criteria — not in appendix or footnote

### 4. Counter-pretexts

The `regardless of` list enumerates 2 to 4 common rationalizations that humans invoke to skip the law. Forcing them into the text makes the pretext explicit and harder to use.

Canonical examples of counter-pretexts:

- "perceived size ('this is trivial')"
- "urgency ('it's a fire')"
- "who requested ('the CEO asked')"
- "team confidence ('we already tested a lot')"
- "deadline pressure"
- "tight release timing"

### 5. Declared exceptions

When a legitimate exception exists, it MUST be inside the `<HARD-GATE>` block with:

- Explicit tag (e.g.: `incident:p0`, `prototype/*`, `sandbox`)
- Retroactive compensation when applicable (e.g.: "retroactive DoR within 5 days")
- Justification that is **not** a disguised pretext

Implicit or case-by-case negotiable exceptions are FORBIDDEN in the block. If the Lexis admits multiple non-enumerable exceptions, it is not a HARD-GATE candidate — it is a conventional declarative Lexis.

### 6. Multilingual applicability

Translated Lexis (per [lex-framework-language](framework/en/_foundation/i18n/lexis/lex-framework-language.md)) MUST have the `<HARD-GATE>` block translated **in all languages in `language.i18n`**, maintaining structural equivalence — same preconditions, same counter-pretexts, same exceptions.

The `<HARD-GATE>` tag itself is **not translated** — it is literal in all 3 languages. Only the content inside the block is localized.

## Coverage

- **Applies to:** all Lexis of the framework Ahrena that block concrete action
- **Bound agents:** all agents that create or modify Lexis (human and AI), including Hécate when she exists
- **Exceptions:** declarative Lexis (without effective blocking) are out of scope; they may be refined in future revisions if blocking necessity is identified

## Examples

### Correct

Lexis applying complete textual HARD-GATE:

```markdown
## Law

> Every feature issue MUST meet canonical DoR before existing.

<HARD-GATE>
warrior-athena MUST NOT initiate Issue-Driven flow without
kata-dor-validate returning ✅ on ALL 9 criteria.

Mandatory preconditions:
  (a) Discovery referenced (docs/discovery/{topic}/insights.md)
  (b) PRD at docs/product/{feature}/prd.md approved
  (c) Capability Spec at docs/product/{feature}/capability-spec.md approved
  (d) Technical package approved by Mômos
  (e) Wireframes approved when UI
  (f) Numbered ACs present
  (g) Leading + lagging metrics declared
  (h) Dependencies mapped
  (i) Anti-duplication search executed

This rule applies to EVERY feature, regardless of:
  - perceived size ("this is trivial")
  - urgency ("it's a fire")
  - who requested ("the CEO asked")

Single exception: hotfix with label `incident:p0` — requires
retroactive DoR within 5 days.
</HARD-GATE>
```

### Incorrect

Implicit blocking without canonical syntax:

```markdown
## Law

> Every feature issue MUST meet DoR before existing.
> warrior-athena refuses incomplete issues.
```

Problems:
- "refuses incomplete issues" is vague — does not enumerate preconditions
- Does not declare scope ("EVERY feature" vs. subset)
- Does not enumerate counter-pretexts
- Does not declare exceptions

Result: humans invoke "this case is different"; agents interpret ambiguously.

## Automated Validation

- **Tool:** human PR review while dedicated linter does not exist; in the future `kata-design-validation` applied by warrior-momos parameterized for type `lexis` should verify presence and conformance of the block
- **Timing:** PR review of every new or modified Lexis
- **Metric:** 100% of Lexis with blocking clause have corresponding `<HARD-GATE>` block in the 3 languages (`language.i18n`)
