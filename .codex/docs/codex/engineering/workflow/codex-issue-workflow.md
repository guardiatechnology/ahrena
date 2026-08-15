# Codex: Fluxo Issue-Driven Development

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Estrutura, fases, gates e artefatos do fluxo de desenvolvimento orientado por issues orquestrado por `warrior-athena`

## Conteúdo

### As 7 fases do fluxo

| # | Fase | Kata principal | Saída |
|:-:|---|---|---|
| 1 | Análise da issue | `kata-issue-analysis` | `.ahrena/issues/{n}/01-brief.md` |
| 2 | Elicitação de requisitos | `kata-requirements-brief` | `.ahrena/issues/{n}/02-requirements.md` |
| 3 | Design arquitetural | `kata-architecture-brief` (+ `kata-adr-write` se aplicável) | `.ahrena/issues/{n}/03-architecture.md` + `docs/adr/ADR-*` |
| 4 | Implementação | delega a `warrior-apollo` → `kata-python-implement` (Python) | código + testes com marcação `AC-N` |
| 5 | Revisão de segurança | `kata-security-review` | `.ahrena/issues/{n}/05-security-review.md` |
| 6 | Gate de qualidade | `kata-quality-gate` | `.ahrena/issues/{n}/06-quality-report.md` |
| 7 | Preparação do PR | `kata-pr-prepare` | URL do PR no GitHub |

### Os 2 gates

**Gate 1 — Aprovação de Escopo** (entre Fase 3 e Fase 4)

- Executado por: `warrior-athena`
- Apresenta ao humano: brief + ACs + arquitetura + ADRs propostos
- Critério de passagem: aprovação explícita humana
- Se falhar: fluxo encerrado ou retorna a Fase 1/2/3 com feedback

**Gate 2 — Qualidade de Implementação** (entre Fase 6 e Fase 7)

- Executado por: `kata-quality-gate`
- 7 verificações; resultado é `go` (todas ✅ ou `unverifiable` onde não aplicável), `no-go` (qualquer ❌), ou `go-with-caveats` (>2 `unverifiable`, humano decide):

| # | Verificação | Como |
|:-:|---|---|
| 1 | Rastreabilidade AC ↔ teste (bidirecional) | Markers canônicos por stack (pytest marker, JS `@ac` tag); regex só como fallback |
| 2 | Scope creep check | `git diff` vs. componentes declarados na Fase 3 |
| 3 | Best practices (Lexis aplicáveis por stack) | Python/Frontend/IaC Lexis; convenções cross-stack |
| 4 | Testes executados | `pytest` / `yarn test` / comando específico do stack |
| 5 | Cobertura | `pytest --cov` ≥ `quality.coverage_threshold` em `.directives` |
| 6 | Tipos | `mypy --strict` / `tsc --noEmit` sem erros novos |
| 7 | Performance budget | Lighthouse/bundle (Frontend); benchmark p99 (Backend); Infracost (IaC) |

- Se falhar: retorna a Fase 4 (Apollo) com relatório detalhado; humano pode optar por ampliar ACs (nova iteração do Gate 1) se o problema for scope creep justificável.

### Best practices verificadas no Gate 2

| Lexis | Verificação |
|---|---|
| `lex-python-typing` | `mypy --strict` sem erros |
| `lex-python-testing` | Todas as funções públicas têm teste |
| `lex-python-security` | Sem credenciais hardcoded; inputs validados |
| `lex-python-immutability` | Sem mutação em estruturas compartilhadas |
| `lex-python-error-handling` | Sem `except: pass` ou swallowing silencioso |
| `lex-conventional-commits` | Commits no formato `type(scope): message` |

### Estrutura de documentação em `docs/`

```
docs/
├── adr/
│   ├── ADR-001-use-event-sourcing-for-ledger.md
│   ├── ADR-002-migrate-to-fastapi.md
│   └── ...
└── issues/
    └── issue-{n}/
        ├── 01-brief.md
        ├── 02-requirements.md
        ├── 03-architecture.md
        ├── 05-security-review.md
        └── 06-quality-report.md
```

### Estado efêmero em `.ahrena/workflow/`

```
.ahrena/workflow/issue-{n}/
└── checkpoint.md       # Contexto de handoff entre fases
```

### Convenção de rastreabilidade AC ↔ teste

Cada AC da Fase 2 é numerado (`AC-1`, `AC-2`, ...). Cada teste novo na Fase 4 **deve** referenciar o(s) AC(s) que cobre, em uma das formas:

**Forma 1 — nome do teste:**
```python
def test_create_refund_returns_201_AC_1():
    ...
```

**Forma 2 — docstring:**
```python
def test_refund_idempotency():
    """AC-2: chamadas repetidas com mesmo Idempotency-Key retornam o mesmo resultado."""
    ...
```

**Forma 3 — marker pytest:**
```python
@pytest.mark.ac("AC-3")
def test_refund_audit_log():
    ...
```

O `kata-quality-gate` usa regex para extrair as referências e cruza com a lista de ACs. Não há coerção automática — é responsabilidade do implementador (Apollo ou outro warrior) marcar corretamente.

### Formato de ADR (MADR simplificado)

```markdown
# ADR-{n}: {Título curto}

- **Status:** proposed | accepted | deprecated | superseded by ADR-XXX
- **Date:** {YYYY-MM-DD}
- **Issue:** #{issue-number}

## Decision

{a decisão tomada, em voz ativa}

## Consequences

### Positive
- ...

### Negative
- ...

### Neutral
- ...

## Alternatives Considered

- **{Alternativa A}:** rejeitada porque ...
- **{Alternativa B}:** rejeitada porque ...
```

**Numeração:** `ADR-{n}` é sequencial global em `docs/adr/`. O `kata-adr-write` detecta o próximo número listando os arquivos existentes.

### Quando gerar ADR (checklist)

| Situação | Gerar ADR? |
|---|:-:|
| Nova escolha tecnológica (framework, library) | ✅ Sim |
| Deviação de padrão existente no codebase | ✅ Sim |
| Trade-off significativo entre alternativas | ✅ Sim |
| Decisão que afeta múltiplos componentes | ✅ Sim |
| Decisão que afeta contrato externo (API, evento) | ✅ Sim |
| Fix pontual de bug sem mudança de padrão | ❌ Não |
| Refactor localizado seguindo padrão existente | ❌ Não |
| Adição de endpoint seguindo padrão do codebase | ❌ Não |

### Delegação a warriors especialistas

`warrior-athena` **não implementa** as fases 4 (código) nem 3 (quando envolve API/eventos). Em vez disso, delega:

| Situação | Delega a | Via |
|---|---|---|
| Feature envolve API REST | `warrior-daedalus` | `kata-api-design-oas` |
| Feature envolve eventos (CloudEvents) | `warrior-kronos` | `kata-events-doc` |
| Feature envolve infraestrutura AWS | `warrior-atlas` | `kata-aws-design` |
| Implementação em Python | `warrior-apollo` | `kata-python-implement` |
| Implementação em Frontend | `warrior-hephaestus` | `kata-frontend-implement` |

O handoff ocorre via `.ahrena/workflow/issue-{n}/checkpoint.md` — Athena grava o contexto necessário, invoca o warrior especialista, e retoma a orquestração após a conclusão.

### Mapeamento de entrada da cry

A `/cry-implement-issue` aceita como argumentos:

```
/cry-implement-issue <issue-number> [<owner>/<repo>]
```

- `<issue-number>` (obrigatório): número da issue no GitHub.
- `<owner>/<repo>` (opcional): repositório de destino; padrão é o repo do projeto atual (detectado via git remote).
