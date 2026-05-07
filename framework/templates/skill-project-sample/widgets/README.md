# widgets/

React components rendered by the consuming agent in the chat surface
(Ahrena convention — not part of the Anthropic Agent Skills spec).

Architecture follows `codex-frontend-architecture` integrally — layers,
state management, accessibility (`lex-frontend-accessibility`), security
(`lex-frontend-security`), typing (`lex-frontend-typing`), testing
(`lex-frontend-testing`), and design system (`lex-design-system-library`)
when rendered inside Guardia surfaces.

Manifest schema, props, events, and the widget ↔ script binding land in
`codex-skill-tools-and-widgets` (PR 2 of the external skills work). The
PR 1 scaffold ships an empty `manifest.json` and a `src/.gitkeep`.

## Suggested layout when adding components

```
widgets/
├── package.json
├── tsconfig.json
├── manifest.json
└── src/
    ├── components/         # presentational primitives
    ├── features/           # feature blocks composed of components
    └── index.tsx           # entry registered in manifest.json
```
