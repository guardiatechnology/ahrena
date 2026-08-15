# Codex: Code Design and Clean Code

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Design, readability, and refactoring decisions across stacks

## Overview

This Codex turns Clean Code into decision criteria. It does not prescribe a universal aesthetic; it helps balance intent, cohesion, coupling, simplicity, evolution, and operational risk.

## Context

- **Domain:** internal software design and safe refactoring
- **Audience:** agents and people who implement or review code
- **Update:** when analyzers, canonical architecture, or the Ahrena patterns dictionary changes

## Content

### Principles

1. **Intent before brevity:** readers should understand the business decision without reconstructing accidental details.
2. **Cohesion before size:** a smaller unit can worsen design if it separates related data and behavior.
3. **Evidence-backed abstraction:** extract for real variation, stable policy, or semantic repetition, not a mechanical count.
4. **SOLID as diagnosis:** use the principles to frame risks, not as a checklist for adding interfaces.
5. **Protected change:** refactoring preserves behavior and begins with executable evidence.

### Decision Questions

| Signal | Question | Preferred response |
|---|---|---|
| Long function | Does it have more than one business reason to change? | Separate by observable responsibility |
| Duplication | Do copies represent the same rule and change together? | Extract; otherwise tolerate distinct semantics |
| New interface | Is there a second consumer or evidence-backed variation? | Create only with evidence |
| Many parameters | Do they form a domain concept? | Value Object or Parameter Object with invariants |
| Growing conditional | Are branches replaceable policies? | Strategy/polymorphism, not for one stable simple case |
| External dependency | Does the external model leak into the domain? | Adapter or Anti-Corruption Layer |

### Smells Are Hypotheses

A smell starts an investigation; it does not prove a defect. Before choosing a pattern, record the observed problem, change pressure, simple option, structural option, trade-offs, and reversal criterion. Always include **when not to use it**.

### Safe Refactoring

1. Capture current behavior with characterization tests when it is not protected.
2. Establish a baseline for tests, static analysis, and relevant performance.
3. Make one transformation at a time and run the smallest reliable checks.
4. Preserve public contracts, data, telemetry, and failure semantics.
5. Separate behavior changes from structural reorganization when that improves reviewability.

### Current Decisions

| Decision | Status | Consequence |
|---|---|---|
| Objective limits live in `lex-clean-code` | Confirmed | This Codex keeps contextual trade-offs |
| Patterns require `use_when`, `avoid_when`, and trade-offs | Ahrena v2 proposal | Prevents cargo cult and prepares the queryable dictionary |

### Technical Constraints

- Do not introduce a pattern without naming the problem and when it should be avoided or removed.
- Do not change contracts, schemas, or error semantics under the label of refactoring.
- Do not use coverage, complexity, or size alone as proof of quality.
- Do not place sensitive information in comments, names, tests, or telemetry.

## Glossary

| Term | Definition |
|---|---|
| Change pressure | Evidence that an area changes for different or recurring reasons |
| Smell | A signal worth investigating, not a definitive diagnosis |
| False abstraction | Structural sharing between concepts with different semantics |

## References

- `lex-clean-code`, `lex-dry`, `lex-no-silent-tech-debt`, `kata-safe-refactoring`
