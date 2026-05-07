# tools/

MCP tools bundled with this skill (Ahrena convention — not part of the
Anthropic Agent Skills spec). Detailed conventions land in
`codex-skill-tools-and-widgets` (PR 2 of the external skills work).

## Layout

```
tools/
├── mcp.config.json     # registry of tools shipped with the skill
└── handlers/
    └── ...             # implementations (Python or JS)
```

Handler implementations follow the same Lexis as code in `scripts/`
(typing, testing, security, error handling). See
`codex-skill-project-architecture` § "Reuso de codex e Lexis durante a
autoria" for the full mapping.
