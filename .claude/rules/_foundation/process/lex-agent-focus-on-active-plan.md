# Lexis: Agent Focus on the Active Plan

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Agent behavior when a Plan sub-issue is in `status: development` and the current session is the declared owner

## Law

> **When a Plan sub-issue is in `status: development` and the current session is the declared owner (assignee), the agent MUST decline user requests for unrelated work until the Plan transitions to `status: to review`. The decline MUST mention the active Plan (number, current status, ETA to `to review` when known) and offer the user the explicit alternative: treat the request as (a) a tangential finding to the current Plan, (b) a new Plan sub-issue under the same parent Issue, (c) a new parent Issue, or (d) a declared critical blocker.**

## Coverage

- **Applies to:** every agent session operating on a Plan sub-issue in `status: development` with assignee equal to the current session identifier (human or agent)
- **Bound agents:** `warrior-athena` (primary orchestrator), `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`, `warrior-claudionor`, and any warrior in execution during an active Plan
- **Declared exceptions:** three and only three — (a) declared critical blocker (CI broken on `main`, declared P0 incident, critical security); (b) direct question about the active Plan (clarification, status query, next step); (c) scope adjustment of the active Plan itself (expand, contract, replan)

<HARD-GATE>
Every agent MUST NOT start work unrelated to the active Plan when there
is a Plan sub-issue in `status: development` with the current session
as the declared assignee.

Mandatory preconditions to accept the request:
  (a) The request is directly related to the active Plan's declared scope
  (b) Or it falls under one of the 3 declared exceptions (critical blocker, question about the Plan, scope adjustment of the Plan)
  (c) And the agent explicitly declares which exception applies before proceeding
  (d) And the agent commits to resuming the Plan after handling the exception

This rule applies to EVERY session with an active Plan, regardless of:
  - "it's quick, just one little thing"
  - "while you're at it, could you also..."
  - "wait, before continuing..."
  - "oh, I forgot to ask you one thing before"

Declared exceptions (3, exhaustive):
  - Declared critical blocker (CI broken on `main`, P0 incident, critical security)
  - Direct question about the active Plan (clarification, status, next step)
  - Scope adjustment of the active Plan itself (expand, contract, replan)
</HARD-GATE>

## Decline Protocol

Upon receiving an unrelated request during an active Plan, the agent MUST:

1. Identify the active Plan: sub-issue number, title, status, ETA to `to review` when known
2. State the decline directly: "There is an active Plan in `status: development` (Plan #{N}: {title}); I cannot start unrelated work until `to review`."
3. Present the user with four discrete options:
   - **(a)** The request is a tangential finding to the active Plan → apply `lex-no-silent-tech-debt` (Tangential Finding Protocol)
   - **(b)** It is a new Plan sub-issue under the same parent Issue → register and handle after `to review`
   - **(c)** It is a new parent Issue (new capability) → register and handle after `to review`
   - **(d)** It is a declared critical blocker → handle now, resume Plan upon completion
4. Wait for the user's choice before any action
5. Resume the active Plan after handling the exception (when applicable), with an explicit checkpoint of the resumption point

## Examples

### Correct

```
User: Before continuing, can you review this other repo here?
Agent: There is an active Plan: #163 (codify 3 Lexis HARD-GATE rules),
       in `status: development`, ETA to `to review` ~10min.
       I cannot start work on another repo now. Do you prefer:
       (a) Register as a new Plan under parent #140 and handle after this PR?
       (b) Open a new parent Issue if it is a separate capability?
       (c) Declare as a critical blocker (broken CI / P0)?
       (d) Wait for `to review` (~10min)?
User: (a)
Agent: Ok, registered. Resuming #163.
```

```
User: Wait, is this Plan really going to touch file X?
Agent: [Exception (b): direct question about the active Plan]
       Yes, file X is part of the declared scope because {reason}.
       Continuing the implementation.
```

### Incorrect

```
User: Before continuing, could you also update this Lex here?
Agent: Sure, let me do that first.                  # FORBIDDEN — silent context switch
       [edits unrelated file, contaminates PR diff]
```

```
User: While at it, fix this other bug too
Agent: [silently expands scope without recording]    # FORBIDDEN — silent scope creep
```

## Automated Validation

- **Tool:** agent self-check before accepting any new instruction during an active Plan; Argos audit during PR review detecting files modified outside the Plan's declared scope (compares PR diff with scope in the sub-issue body)
- **When:** on every new instruction received during a Plan in `status: development`; PR review by Argos
- **Metric:** 0 PRs with files modified outside the Plan's declared scope; 100% of unrelated requests declined with explicit reference to the active Plan
