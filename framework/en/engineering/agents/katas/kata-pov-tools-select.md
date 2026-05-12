# Kata: Select PoV Tools

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Engineering — Agents (pre-operational stage): select the minimum subset of Anthropic tools to feed the primary use case

## Objective

Produce `docs/{context}/agents-pov/{agent}/tools.md` with the minimum subset of Anthropic tools (web search, code execution, file write) required for the PoV's primary use case. Zero custom MCP, zero specialized ML, zero tooling outside the native Anthropic ecosystem. Apply Directive 03 of `lex-agent-construction-directives` (Concrete Tools) in PoV context: search + simple execution suffice to prove value; sophistication stays for Mêtis.

## When to Use

- After `kata-pov-scope-define` (overview ready)
- As a step parallel to `kata-pov-system-prompt` (no strong dependency)
- When a prompt capability depends on tooling not declared in `tools.md` (reactivates this kata)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| `docs/{context}/agents-pov/{agent}/pov.md` | Yes | Defines the primary use case |
| `codex-skill-tools-and-widgets` | Yes | Ahrena convention for `tools/` and widgets inside Skills |
| `codex-skill-anthropic-agent-skills` | Yes | Anthropic spec for tools declared in SKILL.md |

## Workflow

```
Progress:
- [ ] 1. Read pov.md and list required capabilities
- [ ] 2. Map capabilities → native Anthropic tools
- [ ] 3. Refuse out-of-scope tooling
- [ ] 4. Document minimum parameters and examples
- [ ] 5. Persist tools.md
```

### Step 1: Read pov.md and list required capabilities

1. Read `docs/{context}/agents-pov/{agent}/pov.md`.
2. For each capability implied by the primary use case, list the concrete operation (e.g., "search ERP entries" → CSV file read; "validate reconciliation" → Python script execution).

### Step 2: Map capabilities → native Anthropic tools

Allowed catalog in PoV:

| Anthropic tool | When to use |
|---|---|
| `web_search` | When the PoV needs public information (regulation, FX, rates) |
| `str_replace_editor` / file write | When it needs to read/edit project files |
| `code execution` (Anthropic sandbox) | When it needs to run Python to validate a business rule |
| `bash` (sandbox) | When it needs to orchestrate idempotent shell commands |

For each item from Step 1's list, point to exactly 1 tool in the catalog. If none cover, **re-scope the use case** (back to `kata-pov-scope-define`) — do not attempt custom.

### Step 3: Refuse out-of-scope tooling

Vetoed in PoV:

- Custom MCP servers (official MCP servers listed in `.ahrena/.directives::mcp.servers` are OK — Anthropic authorship is not required, as long as they are declared and respect `lex-mcp` Rule 5 on transport preference order)
- Trained ML libraries (transformers, scikit-learn) — stays for `warrior-apollo-agents` (plan-013) when Mêtis designs production
- Integration with a **paid** external API without a public sandbox
- Persistent cross-session cache — Directive 02 in PoV is short-term only

If the primary use case **requires** something from the vetoed list, it is a strong signal that the PoV is premature: document the gap in `pov.md::Out of scope` and proceed without the tool.

### Step 4: Document minimum parameters and examples

For each selected tool, document:

- Operation (verb + object)
- Minimum required parameters
- Real invocation example (not fictional)
- Limit (e.g., "web_search ≤ 3 calls per turn")

### Step 5: Persist tools.md

Write `docs/{context}/agents-pov/{agent}/tools.md` with sections: Required capabilities, Capability→tool mapping, Selected tools (one section per tool), Refused tools (with justification), Per-turn limits.

### Final Validation

- [ ] Every primary-use-case capability has a mapped tool
- [ ] Zero custom MCP
- [ ] Zero ML library
- [ ] Real invocation examples (not invented)
- [ ] Per-turn limits declared

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| `tools.md` | Markdown | `docs/{context}/agents-pov/{agent}/tools.md` |

## Execution Example

### Input (pov.md, excerpt)

```
Primary use case: suggest bank-statement-to-ledger-entry pairing by value + date + description.
```

### Output (tools.md, excerpt)

```markdown
## Required capabilities

1. Read bank statement (CSV/OFX) from the project
2. Read ledger entries (CSV exported from the ERP)
3. Run comparison logic (string similarity)

## Capability → tool mapping

| Capability | Anthropic tool |
|---|---|
| Read statement + entries | str_replace_editor (read) |
| Run similarity | code execution (Python sandbox) |

## Selected tools

### str_replace_editor (read)

- Operation: file read
- Minimum parameters: `command=view, path=<file>`
- Example: read of `inputs/statement-2026-04.csv`
- Limit: ≤ 5 reads per turn

### code execution (Python sandbox)

- Operation: run string comparison
- Parameters: `code=<python>`, with `rapidfuzz` allowed as a lightweight dependency
- Example: `compare("Rent payment", "RENT REF MAR/26") -> 0.82`
- Limit: ≤ 1 execution per turn (expensive)

## Refused tools

- Custom MCP for ERP: gap declared in pov.md::Out of scope
- Trained NER model: premature for PoV
```

## Restrictions

- **Never** introduce custom MCP in PoV. If needed, it signals the use case has already moved past the pre-operational stage.
- **Never** declare a tool without a real invocation example.
- **Never** more than 3 tools per PoV. More than that signals a scope that is too broad.

---

**Model:** This Kata applies Directive 03 (`lex-agent-construction-directives`) at pre-operational rigor. Sophisticated tooling stays for Mêtis (plan-032) when the agent is promoted.
