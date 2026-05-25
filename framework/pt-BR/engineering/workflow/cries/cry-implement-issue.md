# Cry: Implementar Issue (Issue-Driven Development)

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Ponto de entrada do fluxo Issue-Driven Development — invoca `warrior-athena` para conduzir a issue do GitHub pelas 7 fases até a criação do PR

## Descrição

Este comando aciona o fluxo completo de desenvolvimento orientado por issue: desde a leitura da issue no GitHub até a criação do PR revisável, passando por requisitos, arquitetura, Gate 1 de escopo, implementação (delegada), segurança, Gate 2 de qualidade e preparação do PR. O orquestrador é o **Warrior Athena**, que coordena todos os Katas do clade `engineering/workflow/` e delega a especialistas (Apollo, Daedalus, Kronos) quando apropriado.

## Uso

```
/cry-implement-issue <número da issue> [<owner>/<repo>]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `número da issue` | Sim | Número da issue no GitHub | `42` |
| `<owner>/<repo>` | Não | Repositório de destino; padrão: repo atual (via git remote) | `guardiatechnology/ahrena` |

## Pré-requisitos

- `github` listado em `mcp.servers` em `.ahrena/.directives`
- `notion` listado em `mcp.servers` (opcional — enriquece com contexto Notion quando disponível)
- Variáveis de ambiente: `GITHUB_PAT` (obrigatório) e `NOTION_API_KEY` (opcional)
- Issue existente no repositório indicado

## O que o Comando Faz

Invoca **warrior-athena** para conduzir as 7 fases do fluxo:

1. **Fase 1 — Análise da Issue** (`kata-issue-analysis`): lê a issue no GitHub e busca contexto no Notion → `.ahrena/issues/{n}/01-brief.md`
2. **Fase 2 — Requisitos** (`kata-requirements-brief`): elicita ACs numerados com perspectiva PO → `.ahrena/issues/{n}/02-requirements.md`
3. **Fase 3 — Arquitetura** (`kata-architecture-brief`): mapeia componentes, delega design de API/eventos a Daedalus/Kronos se aplicável, invoca `kata-adr-write` para decisões relevantes → `.ahrena/issues/{n}/03-architecture.md` + ADRs em `docs/adr/`
4. **Gate 1 — Aprovação de Escopo:** Athena apresenta artefatos ao humano e aguarda aprovação explícita
5. **Fase 4 — Implementação:** Athena delega a `warrior-apollo` (ou warrior do stack) via `kata-python-implement`; testes marcam `AC-N` para rastreabilidade
6. **Fase 5 — Revisão de Segurança** (`kata-security-review`): OWASP + CVE scan → `.ahrena/issues/{n}/05-security-review.md`
7. **Fase 6 — Gate 2 Qualidade** (`kata-quality-gate`): 6 checks (rastreabilidade AC↔teste, scope creep, best practices, testes, cobertura, tipos) → `.ahrena/issues/{n}/06-quality-report.md`; `no-go` retorna à Fase 4
8. **Fase 7 — Preparar PR** (`kata-pr-prepare`): cria branch + push + PR via GitHub MCP; transiciona ADRs `proposed → accepted`

## Prompt Template

```
Contexto:
- Issue: #{{número da issue}}
- Repositório: {{<owner>/<repo>}} (ou detectado via git remote)

Tarefa:
Atue como **warrior-athena** e conduza o fluxo Issue-Driven Development completo para a issue #{{número da issue}}.

Execute as 7 fases em ordem estrita conforme `codex-issue-workflow`:

1. **Fase 1:** kata-issue-analysis — leia a issue via GitHub MCP e busque contexto via Notion MCP; produza o brief em .ahrena/issues/{n}/01-brief.md.

2. **Fase 2:** kata-requirements-brief — elicite critérios de aceitação numerados (AC-1, AC-2, ...); faça perguntas de clarificação ao usuário se necessário; produza 02-requirements.md.

3. **Fase 3:** kata-architecture-brief — mapeie componentes afetados; delegue a warrior-daedalus (API) ou warrior-kronos (eventos) quando aplicável; invoque kata-adr-write para decisões arquiteturais relevantes; produza 03-architecture.md + ADRs em docs/adr/.

4. **Gate 1:** Apresente brief + ACs + arquitetura + ADRs propostos ao usuário e **aguarde aprovação explícita** antes de prosseguir.

5. **Fase 4:** Delegue a warrior-apollo (ou equivalente) para implementar. Cada teste deve referenciar `AC-N` conforme convenção em codex-issue-workflow.

6. **Fase 5:** kata-security-review — revise o diff contra OWASP Top 10 e CVE scan.

7. **Fase 6:** kata-quality-gate — execute os 6 checks. `no-go` retorna à Fase 4; `go` avança.

8. **Fase 7:** kata-pr-prepare — crie branch, push dos arquivos e PR via GitHub MCP; transicione ADRs proposed → accepted; entregue URL do PR.

Respeite rigorosamente lex-issue-driven: sem pular gates, com rastreabilidade AC↔teste, com ADRs para decisões relevantes, com documentação em docs/.
```

## Exemplo de Invocação

**Input:**

```
/cry-implement-issue 42 guardiatechnology/ahrena
```

**Output esperado (fluxo sequencial com pausas para humano):**

- Athena lê issue #42, produz `.ahrena/issues/42/01-brief.md`
- Athena faz perguntas de clarificação ao usuário (se necessário)
- Athena produz `02-requirements.md` com 5 ACs
- Athena produz `03-architecture.md` + cria `docs/adr/-*.md`
- **Gate 1:** Athena apresenta resumo; usuário aprova
- Apollo implementa; cada teste marca o AC correspondente
- `kata-security-review` aprova (0 achados críticos)
- `kata-quality-gate`: 6 checks ✅ → `go`
- Athena cria PR e informa URL: `https://github.com/guardiatechnology/ahrena/pull/123`

## Restrições

- **Gate 1 é inviolável:** o comando não avança para implementação sem aprovação humana explícita
- **Gate 2 é inviolável:** o comando não cria PR se o Gate 2 resultou em `no-go`
- **Apenas issues existentes:** o comando recusa se a issue não existe ou está vazia (conforme `lex-issue-driven`)
- **Documentação em `docs/`:** todos os artefatos públicos do fluxo ficam em `.ahrena/issues/{n}/` e `docs/adr/`
- **Comando orquestra, não implementa:** o próprio comando não escreve código nem contratos — delega a Katas e warriors especialistas

## Cries e Warriors Associados

- **warrior-athena** — Orquestradora, invocada por este Cry
- **warrior-apollo** — Delegada na Fase 4 para implementação Python
- **warrior-daedalus** — Delegada na Fase 3 para design de API
- **warrior-kronos** — Delegada na Fase 3 para design de eventos
- **cry-api-design**, **cry-event-storm**, **cry-python-implement** — Cries relacionados (fluxos isolados; este Cry os orquestra num fluxo unificado partindo da issue)

## Referências

- `warrior-athena` — orquestradora do fluxo
- `lex-issue-driven` — leis invioláveis
- `codex-issue-workflow` — estrutura completa do fluxo
- `engineering/workflow/README.md` — guia narrativo para humanos
