# scripts/

Executable utility code invoked by the agent or by widgets in the same
skill. Choose Python or JS by context (see `codex-skill-project-architecture`).

## Python

Initialize with `pyproject.toml` and follow `codex-python-architecture`,
`codex-python-tooling`, and applicable `lex-python-*`. Suggested layout:

```
scripts/
├── pyproject.toml
└── src/
    └── module/
        ├── __init__.py
        └── ...
```

## JavaScript

Initialize with `package.json` and a TypeScript setup when possible
(`lex-frontend-typing`). Suggested layout:

```
scripts/
├── package.json
├── tsconfig.json
└── src/
    └── ...
```

The consuming project's build step freezes dependencies and copies runnable artifacts
into `.build/{slug}/scripts/`.
