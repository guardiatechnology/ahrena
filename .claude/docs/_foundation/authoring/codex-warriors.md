# Codex: How to Write Good Warriors

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Creation of Warriors (specialized agents)

## Content

### Principles

1. **Clear identity:** A Warrior MUST have a name, role, and persona that distinguish it. Identity is not cosmetic — it anchors the expected behavior.
2. **Bounded scope:** What a Warrior "Does" is as important as what it "Does Not Do". Vague responsibilities lead to overlap and conflict between Warriors.
3. **Explicit consultation:** Every Warrior MUST declare which Lexis it follows, which Codex it consults, and which Katas it executes. Without this, behavior is unpredictable.
4. **Defined escalation:** A Warrior MUST know when to stop and request human help. Autonomy without limits is a risk.

### Anatomy of a Good Warrior

| Section | Purpose | Quality Criteria |
|---------|---------|-----------------|
| **Identity** | Name, role, domain, and persona | Memorable names; persona that informs the tone |
| **Mission** | Core purpose in 1-2 sentences | Specific and actionable |
| **Responsibilities** | Does / Does Not Do | Balanced and unambiguous lists |
| **Consultation** | Lexis, Codex, and Katas referenced | Tables with identifier and description |
| **Behavior** | Tone, action flow, escalation | Concrete and verifiable |
| **Interaction Example** | Real usage scenario | User input + Warrior response |

### Identity Design

A Warrior's identity guides its behavior:

| Element | Function | Guideline |
|---------|----------|-----------|
| **Name** | Identification and memorability | Mythological, historical, or symbolic names that evoke the role |
| **Role** | What it does in professional terms | Clear title (e.g., "Software Architect", "Specialist Translator") |
| **Domain** | Where it operates | Specific area (e.g., "architectural decisions and code quality") |
| **Persona** | How it behaves | 2-3 adjectives that define the tone (e.g., "methodical, rigorous, focused on trade-offs") |

### Responsibility Design

The "Does" / "Does Not Do" section defines the Warrior's boundary:

**Good "Does":**
- Drafts ADRs with trade-off analysis
- Reviews PRs with a focus on architecture

**Bad "Does":**
- Helps with code (too vague)
- Does everything related to backend (infinite scope)

**Good "Does Not Do":**
- Does not make product decisions (that is the PM's role)
- Does not deploy to production (that is DevOps)

**Bad "Does Not Do":**
- Does not do bad things (obvious and useless)

### Consultation Chain Design

Every Warrior declares three reference tables:

1. **Lexis** — the laws it obeys (always `lex-directives` + others)
2. **Codex** — the manuals it consults to make decisions
3. **Katas** — the procedures it executes

The chain MUST be complete: if the Warrior performs a task, there MUST be a corresponding Kata. If it makes decisions about a domain, there MUST be a corresponding Codex.

### Escalation Design

Escalation criteria define when the Warrior stops and requests help:

| Type | Example |
|------|---------|
| High impact | "Decision affects more than 3 modules" |
| Financial cost | "Trade-off involves significant cost" |
| Rule conflict | "Conflict between Lexis and business requirement" |
| Uncertainty | "Insufficient information to make a decision" |

### Standards and Conventions

| Aspect | Standard | Example |
|--------|----------|---------|
| Naming | `warrior-{kebab-case-name}` | `warrior-spartacus` |
| Warrior name | Memorable proper noun | Hermes, Spartacus, Athena |
| Mission | Maximum 2 sentences in blockquote | > "Ensure that every architectural decision is documented..." |
| Interaction example | Real user input + structured response | Demonstrates the tone and flow of the Warrior |

### Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Generic Warrior | "Code assistant" — no identity | Define specific role, domain, and persona |
| Unlimited scope | Does everything, specializes in nothing | Use "Does Not Do" to set boundaries |
| No consultation chain | Unpredictable behavior | Declare Lexis, Codex, and Katas explicitly |
| No escalation | Warrior decides things it should not | Define clear criteria for when to stop |
| Decorative persona | Mythological name with no connection to the role | Choose a name that evokes the specialty |

### Warrior vs Generic Agent — When to Create

| Situation | Answer | Why |
|-----------|--------|-----|
| Recurring task with ongoing scope | Warrior | Needs identity and persistent context |
| One-off task executed by any agent | Kata | A procedure is sufficient |
| Multiple agents with the same specialty | Warrior | Avoids reconfiguring context every time |
| Domain with specific tone and behavior | Warrior | The persona ensures consistency |

### Technical Constraints

- Every Warrior MUST include **at least one Lexis** in the consultation chain (`lex-directives` at minimum)
- The **Interaction Example** section MUST contain a complete scenario (user input + structured Warrior response)
- The file name MUST use the prefix defined in `naming.prefixes.warriors` (consult `.ahrena/.directives`) and kebab-case: `{prefix}-{name}.md`
- The structure MUST follow the official template: consult `paths.samples.warriors` in `.directives` (e.g. `templates/warrior-sample.md`)
- The **Mission** MUST be a blockquote citation (1–2 sentences)
