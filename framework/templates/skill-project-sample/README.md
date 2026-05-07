# Skill Project Template

This directory is the **template** consumed by `kata-init-skill` to
scaffold a new skill project under `skills/{slug}/`. It is **not** a
working skill on its own — `kata-init-skill` copies this tree, replaces
placeholders enclosed by `__...__`, validates the slug against the
Anthropic Agent Skills spec, and writes the result to the destination
controlled by `paths.skills_root` in `.ahrena/.directives` (default
`skills/`).

For the rules that govern the resulting project, see
`lex-skill-project-structure`. For the architecture of each
subdirectory, see `codex-skill-project-architecture`. For the spec of
the final SKILL.md, see `codex-skill-anthropic-agent-skills`.

## Placeholders

| Placeholder | Meaning |
|-------------|---------|
| `__SLUG__` | Project slug — kebab-case, 1-64 chars, matches the directory name |
| `__BCP47__` | Language code (`pt-BR`, `es`, `en`) declared in `metadata.language` |
| `__HUMAN_TITLE__` | Human-readable title for the SKILL.md `# Heading` |
| `__ONE_SENTENCE_DESCRIPTION_INCLUDING_WHEN_TO_USE__` | Frontmatter `description`; must include both **what** and **when** |
| `__LICENSE_OR_REFERENCE__` | License identifier (`Apache-2.0`, `MIT`) or reference to a bundled license file |

## Tree

```
skill-project-sample/
├── SKILL.md                  # frontmatter + body
├── skill.config.json         # local config (not packaged)
├── .skill-manifest.json      # skeleton; build fills hashes/refs
├── README.md                 # this file (NOT copied to the project)
├── references/
│   └── REFERENCE.md
├── scripts/
│   ├── README.md
│   └── .gitkeep
├── tools/
│   ├── mcp.config.json
│   ├── README.md
│   └── handlers/
│       └── .gitkeep
└── widgets/
    ├── package.json
    ├── tsconfig.json
    ├── manifest.json
    ├── README.md
    └── src/
        └── .gitkeep
```

`README.md` at the root is **not** copied to the destination — it
documents the template itself for framework maintainers.
