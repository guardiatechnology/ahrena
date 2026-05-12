# Codex: Component UI — Next.js App e Widgets Exportáveis

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — convenções internas do diretório `components/ui/`

## Visão Geral

`components/ui/` hospeda a interface humana do bounded context. Tipicamente um app Next.js que serve a UI primária e, quando aplicável, exporta widgets embarcáveis via `tsup` para serem consumidos por outros frontends Guardia. Consome `@guardia/design-system` per `lex-design-system-library` — primitivas próprias são proibidas. Este codex detalha estrutura interna, dual-build (app + widgets) e a fronteira com `components/api/`.

## Contexto

- **Domínio:** UI do bounded context (Next.js app + widgets exportados)
- **Público-alvo:** engenheiros frontend, Hephaestus quando delega UI
- **Atualização:** mudança de versão major Next.js, novo padrão de widget bundling, ADR de fronteira

## Stack canônico

| Camada | Ferramenta | Notas |
|--------|------------|-------|
| Framework | Next.js (App Router) | SSR/SSG conforme necessidade da view |
| Bundler de widgets | `tsup` | Output ESM + CJS, types incluídos |
| Design System | `@guardia/design-system` | Obrigatório per `lex-design-system-library` |
| Tipagem | TypeScript strict | per `lex-frontend-typing` |
| Estado | React hooks; Zustand quando necessário | Evitar Redux/state managers pesados |
| Testes | Vitest + React Testing Library; Playwright para E2E | per `lex-frontend-testing` |
| Estilo | Tokens do design system; Tailwind apenas via tokens | per `lex-brand-colors`, `lex-brand-typography` |

Convenções frontend transversais: `codex-frontend-architecture`.

## Estrutura interna

```
components/ui/
├── package.json
├── tsup.config.ts
├── next.config.mjs
├── tsconfig.json
├── src/
│   ├── app/                     # Next.js App Router (rotas)
│   ├── pages/                   # (se Pages Router em legado; preferir app/)
│   ├── widgets/                 # Componentes exportáveis via tsup
│   │   ├── {widget-name}/
│   │   │   ├── index.tsx
│   │   │   └── types.ts
│   │   └── index.ts             # Barrel de exports
│   ├── features/                # UI específica do bounded context (não exportada)
│   ├── lib/
│   │   ├── api.ts               # Cliente HTTP para components/api/
│   │   └── auth.ts              # Helpers de auth
│   └── styles/                  # Apenas tokens; sem estilos hardcoded
└── tests/
```

`widgets/` exporta componentes consumíveis por outros frontends. `features/` é privado ao bounded context. `app/` consome ambos.

## Padrões essenciais

1. **Consumo do design system obrigatório.** Per `lex-design-system-library` — botões, inputs, modais, layout primitives vêm de `@guardia/design-system`. Reimplementar é proibido.
2. **Acessibilidade WCAG 2.1 AA.** Per `lex-frontend-accessibility` — semântica nativa, atributos ARIA quando necessário, contraste e foco testáveis.
3. **Cliente API tipado.** `src/lib/api.ts` gera tipos a partir do `openapi.yaml` em `docs/{context}/oas/` (codegen no build). Componentes consomem o cliente tipado.
4. **Widgets stateless por contrato.** Widgets exportáveis aceitam tudo via props; estado/data fetching responsabilidade do consumer. Permite reuse seguro.
5. **Dual build com tsup.** `next build` para o app; `tsup --watch` durante dev de widget; `tsup` em CI para gerar package consumível.
6. **Voice e brand consistentes.** Per `lex-brand-voice`, `lex-brand-colors`, `lex-brand-typography`, `lex-brand-logo` — sem buzzwords, paleta oficial, Poppins + Roboto fallback.

## Fronteira com outros components

| Pode | Não pode |
|------|----------|
| Chamar `components/api/` via HTTP (cliente tipado) | Acessar DB do bounded context direto |
| Exportar widgets para outros frontends Guardia | Hospedar lógica de negócio (move para `api/` ou consumer) |
| Disparar fluxos via `api/` (POST/PATCH/DELETE) | Chamar `components/jobs/` direto — sempre via `api/` ou eventos |
| Consumir tokens de `@guardia/design-system` | Hardcoded cores, fontes ou espaçamentos fora dos tokens |

## Anti-padrões

| Anti-padrão | Caminho correto |
|-------------|-----------------|
| Reimplementar Button/Input/Modal localmente | Consumir de `@guardia/design-system` |
| Cores em hex inline (`color: '#4F186D'`) | Tokens do design system per `lex-brand-colors` |
| Cliente HTTP escrito à mão para `components/api/` | Gerar tipos do `openapi.yaml`; cliente em `src/lib/api.ts` |
| Widget com estado interno acoplado a uma feature | Stateless; props in, callbacks out |
| Lighthouse score baixo (perf/a11y) sem ADR | Rodar Lighthouse em CI; bloquear regressões |

## Referências

- `codex-component-architecture` — fronteiras gerais entre components
- `codex-frontend-architecture` — convenções frontend transversais
- `lex-design-system-library`, `codex-design-system`, `codex-design-system-components` — consumo do design system
- `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-testing`, `lex-frontend-security`
- `lex-brand-voice`, `lex-brand-colors`, `lex-brand-typography`, `lex-brand-logo`
- `lex-ai-first-experience` — quando UI integra com agentes do bounded context
- `lex-feature-design-docs`, `codex-feature-design-docs` — `docs/{context}/oas/openapi.yaml` como contrato com `components/api/`
- `references.component_template_repo.url` em `.ahrena/.directives`
