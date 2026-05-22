---
id: "rust-framework-support/ideas/002-rust-fundamentals-codex-bundle"
topic: "rust-framework-support"
problem: "O onboarding de engineers em Rust no contexto Guardia/agêntico não tem material curado; engineers experientes em outras stacks gastam tempo coletando referências do MIT Rust Book, Rustacean e materiais dispersos por conta própria, sem padrão interno consolidado."
hypothesis: "Se o framework oferecer um bundle de Codex pedagógicos (ownership/borrowing, string types, traits/generics, concurrency guarantees, testing/docs, error handling fundamentals, ffi safety) referenciados a fontes canônicas (MIT Rust Book, Rust for Rustaceans), o time-to-first-PR Rust por novo engineer cai pela metade — de cerca de 3 semanas para cerca de 1.5 semanas em 6 meses após release; baseline a confirmar com 3 entrevistas adicionais."
target_user: "Engineers transitioning para Rust no contexto agêntico Guardia, vindo de Python, TypeScript ou Go, sem experiência prévia com sistema de ownership"
success_metric: "Time-to-first-PR Rust por novo engineer — baseline a confirmar (estimativa atual ~3 semanas, via 3 entrevistas) → target 1.5 semanas em 6 meses após release; secundário: número de novos engineers Rust onboardados via framework por trimestre"
effort_estimate: "M (1-2 sprints — material existe na PR #2 (~1444 linhas); o trabalho é reformatação para template Codex Ahrena, checklist pedagógico, decisão entre referenciar livro vs reescrever, e overlap com Lexis da PR #1)"
linked_insights:
  - "rust-framework-support/insights/002-rust-mit-book-guides"
created_at: "2026-05-22T04:09:25Z"
updated_at: "2026-05-22T04:09:25Z"
---

# Idea: Bundle de Codex pedagógicos Rust para onboarding agêntico

## Síntese

A PR #2 codificou 16 arquivos (~1444 linhas) derivados do MIT Rust Book com viés didático — ownership, strings, traits/generics, concurrency, testing, error handling fundamentals, FFI. Promover esse material como bundle de Codex (manuais de referência) reduz o custo de onboarding de novos engineers Rust e dá ao framework uma camada pedagógica explícita, separada da camada de qualidade-de-produção tratada na Idea 001. A hipótese de redução de time-to-first-PR (~3 → ~1.5 semanas) é estimativa inicial que precisa de validação empírica antes de virar critério de release.

## Insights de origem

1. **rust-framework-support/insights/002-rust-mit-book-guides** — PR #2 propôs 3 Lexis fundamentais (ownership/borrowing, string types, ffi-safety) e 3 Codex (concurrency guarantees, testing/docs, traits/generics), com 4 arquivos sobrepostos à PR #1 (`library-must-define-error-type`, `no-assume-utf8-on-io`, `no-panic-in-production`, `no-regex-compilation-in-loops`).

## Próximos passos

- Decidir a tipologia de cada artefato pedagógico: o que é Codex (referência), o que é Lex (regra automatizável). Especificamente, `lex-rust-ownership-borrowing` proibindo `clone()`/`Rc` "sem justificativa" exige critério de revisão claro ou regra clippy/linter — caso contrário, é Codex
- Validar a baseline de time-to-first-PR Rust com 3 entrevistas a engineers que recentemente fizeram a transição (sem essa validação, a métrica de sucesso fica suspensa)
- Coordenar com a Idea 001: definir se a clade `engineering/rust/` divide em `fundamentals/` + `production/` ou se ambos os bundles coabitam no mesmo nível, e qual versão dos 4 arquivos conflitantes (com a PR #1) é canônica
- Decidir política de referenciar fontes externas: linkar capítulos do MIT Rust Book com permalink versionado vs reescrever conteúdo internamente — impacto direto no esforço de tri-tradução
- Avaliar se um checklist de onboarding (lista verificável de Codex a ler em ordem) deve acompanhar o bundle, ou se isso é responsabilidade de outro artefato Ahrena
