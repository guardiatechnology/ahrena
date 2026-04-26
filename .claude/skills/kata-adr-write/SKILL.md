---
name: kata-adr-write
description: "{Title}. Production of an individual ADR in simplified MADR format under docs/adr/"
---

# Kata: Write an Architecture Decision Record (ADR)

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Production of an individual ADR in simplified MADR format under `docs/adr/`

## Workflow

```
Progress:
- [ ] 1. Detect the next sequential number
- [ ] 2. Generate the title slug
- [ ] 3. Compose content in MADR format
- [ ] 4. Persist to docs/adr/
- [ ] 5. Return reference to the caller
```

### Step 1: Detect the next sequential number

1. List files under `docs/adr/` matching `ADR-{n}-*.md`.
2. Extract the highest existing `n` (e.g., `ADR-007-*.md` → `7`).
3. Next number = highest + 1 (e.g., `8`).
4. If `docs/adr/` does not exist, create the directory and start at `1`.
5. Format with 3-digit zero-padding (`ADR-001`, `ADR-023`, `ADR-125`).

### Step 2: Generate the title slug

1. Convert the title to lowercase.
2. Replace spaces with hyphens.
3. Remove non-alphanumeric characters (except hyphens).
4. Limit to ~60 characters.

**Example:** `"Use FastAPI routers for module separation"` → `use-fastapi-routers-for-module-separation`

**Final filename:** `docs/adr/ADR-{n}-{slug}.md` (e.g., `docs/adr/ADR-008-use-fastapi-routers-for-module-separation.md`)

### Step 3: Compose content in MADR format

```markdown
# ADR-{n}: {Title}

- **Status:** {proposed | accepted | deprecated | superseded by ADR-XXX}
- **Date:** {YYYY-MM-DD}
- **Issue:** #{issue-number}  (omit if not applicable)

## Context

{problem or force that motivated the decision — 1-3 paragraphs}

## Decision

{the decision made, in active voice — 1-2 paragraphs}

## Consequences

### Positive

- {benefit 1}
- {benefit 2}

### Negative

- {cost or trade-off 1}
- {cost or trade-off 2}

### Neutral

- {change that is neither clearly benefit nor cost, but relevant}

## Alternatives Considered

- **{Alternative A}:** {brief description}. Rejected because {rationale}.
- **{Alternative B}:** {brief description}. Rejected because {rationale}.
```

**Content rules:**
- **Context** describes the problem, not the solution. Must be understandable by someone reading in 2 years.
- **Decision** is declarative and imperative ("We adopt X", "We use Y").
- **Consequences** includes costs — an ADR without Negative is suspicious.
- **Alternatives** needs at least 1; "do nothing" is a valid alternative.
- If the decision is linked to an issue, include `**Issue:** #{n}` with a clickable link.

### Step 4: Persist to `docs/adr/`

1. Create `docs/adr/` if it does not exist.
2. Write the file at `docs/adr/ADR-{n}-{slug}.md`.
3. If the file already exists (unlikely, since n is sequential), stop and report an error.

### Step 5: Return reference to the caller

Return:
- Relative path: `docs/adr/ADR-{n}-{slug}.md`
- Number: `ADR-{n}`
- Status: `proposed` (or the informed status)

This reference is used by `kata-architecture-brief` to include in the architecture document and by `warrior-athena` to present at Gate 1.

## Status Transitions

After creation with status `proposed`, the ADR may transition to:

| New Status | When | Action |
|---|---|---|
| `accepted` | After human approval at Gate 1 | Edit the ADR, change `Status:` |
| `deprecated` | Decision is no longer relevant but was not replaced | Edit, change `Status:` and add a note explaining |
| `superseded by ADR-XXX` | Replaced by another ADR | Edit, change `Status:`; the new ADR references this one in its `Context` |

**Important:** ADRs are **append-only in spirit** — once `accepted`, the historical content is preserved. Changes are made by creating a new ADR that supersedes the previous.

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| ADR file | Markdown MADR | `docs/adr/ADR-{n}-{slug}.md` |
| Reference to caller | Text: path + number + status | Return |

## Restrictions

- **Sequential numbering is inviolable:** never reuse numbers; gaps indicate removed ADRs (which should not happen — see "Important" above).
- **Simplified MADR:** strictly follow the structure above; do not add optional sections without justification.
- **At least 1 alternative:** an ADR with no alternatives is suspicious (means the decision was made without considering options).
- **Fixed destination:** `docs/adr/` per `lex-issue-driven` — never `.ahrena/` or another path.
- **Do not edit `accepted` ADRs except for status transition:** decision changes become a new ADR (`superseded by`).
