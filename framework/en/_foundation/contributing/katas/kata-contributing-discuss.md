# Kata: Open discussion on GitHub Discussions

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Create discussion in the origin repository (Golden Circle; GitHub MCP when available)

## Objective

This Kata defines the standardized procedure for opening a discussion on the origin repository's GitHub Discussions, following the **Golden Circle** (WHAT, WHY, HOW). There is no .md template — the content is structured around these three axes. Creating the discussion **MUST prioritize GitHub MCP** when available; fallback to manual creation or `gh` CLI.

## When to Use

- When the user wants to propose an idea or significant change before opening an issue/PR
- When invoked by cry-new-discuss or by cry-contribute with discuss action
- Per codex-contributing: discuss first, then issue/PR

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| WHAT | Yes | What is proposed: idea, feature, or change in one clear phrase |
| WHY | Yes | Why it matters: impact, problem it solves, value |
| HOW | No | How it could be done: suggested approach, technical or process options |

## Workflow

```
Progress:
- [ ] 1. Collect WHAT, WHY, HOW (with the user)
- [ ] 2. Draft the discussion body (Golden Circle)
- [ ] 3. Create discussion via GitHub MCP (or provide manual steps)
- [ ] 4. Final verification
```

### Step 1: Collect WHAT, WHY, HOW

1. Ask or infer from context: **WHAT** (objective summary), **WHY** (motivation and benefit), **HOW** (optional — implementation or process suggestion).
2. If the user already provides text, structure it into the three axes.

### Step 2: Draft the discussion body

1. Build the body in Markdown with clear sections: **WHAT**, **WHY**, **HOW** (if any).
2. Include suggested category: usually "Ideas" (per codex-contributing).
3. Discussion title: phrase that summarizes WHAT.

### Step 3: Create discussion via GitHub MCP

1. **Preferred:** Use GitHub MCP if the server exposes discussion creation (e.g., discussions tool). Indicate server and parameters (owner, repo, category, title, body).
2. **Fallback:** If MCP is unavailable or there is no discussions tool: present the ready title and body to the user; instruct them to open manually: repository GitHub → Discussions → New discussion (Ideas category); or use `gh` CLI if supported.

### Step 4: Final verification

- [ ] The discussion was created (or the content was delivered for manual opening)
- [ ] The text follows the Golden Circle (WHAT, WHY, HOW)
- [ ] The discussion link or instructions were presented to the user

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Discussion | GitHub Discussion | Origin repository (Ideas category) |
| Discussion URL or instructions | Link / text | Presented to the user |

## Constraints

- There is no .md template in the framework for discussion; content is free-form within the Golden Circle.
- Always structure the proposal as WHAT, WHY, and (when applicable) HOW.
- If creation via MCP is not possible, do not invent a `gh` command for discussions — provide manual steps and the ready title + body.

## References

- `codex-contributing` — Guardia contribution flow (discuss first; Ideas category)
- Golden Circle — WHAT, WHY, HOW
- GitHub MCP (when available for discussion creation)
- cry-new-discuss, cry-contribute — Shortcuts that invoke this Kata
