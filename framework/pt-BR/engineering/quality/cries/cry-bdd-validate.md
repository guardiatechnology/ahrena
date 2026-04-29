# Cry: Validar BDD (Fase 8)

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Engenharia — Qualidade. Atalho que invoca `warrior-themis` para executar a Fase 8 do fluxo Issue-Driven (desenho de cenários + validação contra a implementação) e devolver a decisão `go | no-go` do Gate 3.

## Descrição

Aciona a Fase 8 completa para uma Issue: `warrior-themis` produz `07-bdd-scenarios.md` (cego para código) e em seguida `08-bdd-validation-report.md` (com leitura de testes), encerrando com decisão `go | no-go` para o Gate 3 do `kata-quality-gate`.

Este Cry é um-para-um com `warrior-themis` (per `lex-pilars` Regra 5: Cry → 1 Warrior ou 1 Kata). O Warrior internamente orquestra `kata-bdd-scenarios-design` e `kata-bdd-validate-implementation`.

## Uso

```
/cry-bdd-validate <número da issue> [<owner>/<repo>]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `número da issue` | Sim | Número da issue no GitHub | `42` |
| `<owner>/<repo>` | Não | Repositório de destino; padrão: detectado via `git remote` | `guardiafinance/ahrena` |

## Pré-requisitos

- `github` listado em `mcp.servers` em `.ahrena/.directives` (per `lex-mcp`)
- `notion` em `mcp.servers` quando a Issue referencia páginas Notion
- Variáveis de ambiente: `GITHUB_PAT` (obrigatório), `NOTION_API_KEY` (quando aplicável)
- Fases 1-3 do fluxo Issue-Driven concluídas: `01-brief.md`, `02-requirements.md`, `03-architecture.md` em `docs/issues/issue-{n}/`
- **Recomendado:** Gate 2 com decisão `go` (`06-quality-report.md`); se ausente ou `no-go`, o Cry alerta e pede confirmação antes de prosseguir

## O que o Comando Faz

1. Lê `.ahrena/.directives`.
2. Verifica pré-requisitos (artefatos das Fases 1-3 e estado do Gate 2).
3. Invoca **warrior-themis** com o número da issue e o repositório.
4. `warrior-themis` executa `kata-bdd-scenarios-design` (Fase 8.1) — cego para código:
   - Lê fontes permitidas (Issue, Notion, artefatos de fluxo)
   - Produz `docs/issues/issue-{n}/07-bdd-scenarios.md`
5. `warrior-themis` executa `kata-bdd-validate-implementation` (Fase 8.2) — com leitura de testes:
   - Mapeia cada `SCN-{N}` para testes existentes
   - Verifica acoplamento a step-runner BDD nos manifestos
   - Produz `docs/issues/issue-{n}/08-bdd-validation-report.md`
6. Reporta a decisão `go | no-go` do Gate 3 e, quando `no-go`, lista próximas ações com responsável e nível.

## Prompt Template

```
Contexto:
- Issue: #{{número da issue}}
- Repositório: {{<owner>/<repo>}} (ou detectado via git remote)

Tarefa:
Atue como warrior-themis e conduza a Fase 8 do fluxo Issue-Driven para a issue
#{{número da issue}}, encerrando com a decisão go | no-go para o Gate 3.

Execute em ordem estrita:

1. Verifique pré-condições: artefatos das Fases 1-3 presentes em docs/issues/issue-{n}/.
2. Verifique o estado do Gate 2 (06-quality-report.md). Se ausente ou no-go, alerte e pergunte se deve prosseguir.
3. Fase 8.1 — kata-bdd-scenarios-design:
   - Leia exclusivamente fontes permitidas (per lex-bdd-spec-only-sources).
   - Produza 07-bdd-scenarios.md com frontmatter declarando fontes e cobertura por AC.
   - Aplique formato declarativo (per lex-bdd-gherkin-format) e auto-lint via regex de codex-gherkin.
4. Fase 8.2 — kata-bdd-validate-implementation:
   - Indexe testes do repositório por referência SCN-{N}.
   - Verifique manifestos contra a lista proibida de step-runners (lex-bdd-no-framework-coupling).
   - Produza 08-bdd-validation-report.md com classificação (covered | partial | missing).
   - Emita decisão go | no-go.
5. Atualize o checkpoint em .ahrena/workflow/issue-{n}/checkpoint.md.
6. Reporte ao usuário: decisão, contagens (covered/partial/missing) e tabela de próximas ações.

Respeite rigorosamente as Lexis BDD: cego para código na Fase 8.1, formato Gherkin
declarativo, sem step-runner, rastreabilidade SCN-{N} obrigatória.
```

## Exemplo de Invocação

**Input:**

```
/cry-bdd-validate 42 guardiafinance/ahrena
```

**Output esperado:**

```
Phase 8 — Issue #42

Phase 8.1 (scenarios design, blind to code):
✓ 07-bdd-scenarios.md produced (6 scenarios, 4 ACs covered)

Phase 8.2 (test mapping):
✓ 08-bdd-validation-report.md produced
  - covered: 4
  - partial: 1 (SCN-5 @nfr at unit level)
  - missing: 1 (SCN-6 @nfr idempotency)
  - framework coupling: clean

Gate 3 decision: NO-GO

Next actions:
| Gap   | Action                                  | Owner          | Level       |
| SCN-5 | Add integration test measuring latency  | warrior-apollo | integration |
| SCN-6 | Create idempotency test                 | warrior-apollo | integration |

Checkpoint atualizado.
```

## Restrições

- **Não pula o Gate 2:** se Gate 2 deu `no-go` ou está ausente, o Cry alerta e pede confirmação antes de prosseguir (a Fase 8 faz mais sentido após o Gate 2 fechar).
- **Não implementa testes:** quando há gap, o Cry retorna `no-go` com ações sugeridas — a implementação dos testes faltantes é delegada em iteração subsequente.
- **Output canônico:** `07-bdd-scenarios.md` e `08-bdd-validation-report.md` em `docs/issues/issue-{n}/`; nunca em outro caminho.
- **Sem invenção:** se a Issue está incompleta para alguma AC, o Cry retorna com ACs marcadas `BLOCKED` e devolve à origem (não consulta código para preencher).

## Diferença de Kata

| Aspecto | Cry `cry-bdd-validate` | Katas `kata-bdd-*` |
|---|---|---|
| **Natureza** | Atalho de invocação | Procedimento detalhado |
| **Escopo** | Aciona `warrior-themis` | Executados pelo Warrior |
| **Complexidade** | Baixa (uma frase) | Alta (dezenas de passos) |

## Cries e Warriors Associados

- **warrior-themis** — Warrior invocado por este Cry; orquestra os Katas de Fase 8
- **warrior-athena** — Quando este Cry é parte do fluxo Issue-Driven completo (`/cry-implement-issue`), Athena delega a Fase 8 e este Cry pode ser invocado isoladamente como atalho fora do fluxo
- **warrior-apollo / warrior-hephaestus / warrior-iris** — Recebem ações de gap quando o resultado é `no-go`

## Referências

- `warrior-themis` — agente invocado
- `kata-bdd-scenarios-design` — Fase 8.1
- `kata-bdd-validate-implementation` — Fase 8.2
- `lex-bdd-spec-only-sources`, `lex-bdd-gherkin-format`, `lex-bdd-no-framework-coupling` — leis do BDD
- `lex-issue-driven` — fluxo Issue-Driven (Fase 8 e Gate 3)
- `codex-bdd`, `codex-gherkin` — manuais de referência
