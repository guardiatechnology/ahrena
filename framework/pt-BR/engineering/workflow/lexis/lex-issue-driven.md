# Lexis: Desenvolvimento Orientado por Issue

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Fluxo de desenvolvimento de features e bugfixes orientado por issues do GitHub no framework Ahrena

## Propósito

Em projetos que adotam o fluxo Issue-Driven Development (orquestrado por `warrior-athena`), cada feature ou bugfix começa em uma issue do GitHub e atravessa fases obrigatórias de análise, design, implementação e validação. Sem regras firmes, esse fluxo perde integridade: gates são pulados, critérios de aceitação viram opcionais, decisões arquiteturais não ficam registradas, e a documentação produzida se espalha em locais inconsistentes.

Esta Lexis existe para garantir que **toda implementação tenha rastreabilidade desde a issue original até o PR final**, que **gates de qualidade não sejam contornados**, que **decisões arquiteturais relevantes sejam registradas como ADRs** e que **toda documentação produzida pelo fluxo fique estruturada em `docs/`**.

## Lei

> **Toda implementação conduzida por `warrior-athena` DEVE partir de uma issue existente, passar por ambos os Gates (Escopo e Qualidade), respeitar a rastreabilidade bidirecional entre critérios de aceitação e testes, registrar decisões arquiteturais relevantes como ADRs em `docs/adr/`, e produzir toda documentação pública do fluxo em `docs/issues/issue-{n}/`.**

## Regras

### 1. Issue obrigatória como ponto de partida

O agente **DEVE**:

1. Exigir uma referência de issue existente (`owner/repo#número` ou equivalente) antes de iniciar qualquer fase do fluxo.
2. Ler a issue via `kata-mcp-github-read` na Fase 1.
3. Se a issue não existir ou estiver vazia, informar ao usuário e encerrar — não criar a issue automaticamente nem inferir o escopo.

### 2. Gates não podem ser pulados

O agente **NÃO PODE**:

1. Avançar da Fase 3 para a Fase 4 sem aprovação explícita humana no Gate 1 (escopo).
2. Criar o PR na Fase 7 se o Gate 2 (qualidade) não resultou em `go`.
3. Marcar itens do Gate 2 como atendidos sem execução real da verificação (ex.: não pode declarar "testes passam" sem rodar `pytest`).

### 3. Rastreabilidade bidirecional AC ↔ teste

Para que o Gate 2 passe:

1. **Cada critério de aceitação** numerado na Fase 2 **DEVE** ter pelo menos um teste que o cobre.
2. **Cada teste novo** introduzido na Fase 4 **DEVE** estar ligado a pelo menos um AC via convenção `AC-{N}` no nome ou docstring do teste.
3. Testes novos sem AC correspondente são tratados como **scope creep** e bloqueiam o gate.

### 4. ADRs obrigatórios para decisões arquiteturais relevantes

O agente **DEVE** invocar `kata-adr-write` quando a Fase 3 identificar:

1. Nova escolha tecnológica (framework, biblioteca, padrão arquitetural).
2. Deviação de padrão existente no codebase.
3. Trade-off significativo entre alternativas.
4. Decisão que afeta múltiplos componentes ou contratos externos.

O ADR **DEVE** ser salvo em `docs/adr/ADR-{n}-{título-em-kebab}.md` no formato MADR simplificado.

### 5. Documentação em `docs/`

O agente **DEVE** estruturar toda documentação pública do fluxo em `docs/`:

1. `docs/issues/issue-{n}/01-brief.md` — análise da issue (Fase 1)
2. `docs/issues/issue-{n}/02-requirements.md` — ACs numerados (Fase 2)
3. `docs/issues/issue-{n}/03-architecture.md` — design (Fase 3)
4. `docs/issues/issue-{n}/05-security-review.md` — revisão de segurança (Fase 5)
5. `docs/issues/issue-{n}/06-quality-report.md` — relatório do Gate 2 (Fase 6)
6. `docs/adr/ADR-{n}-*.md` — ADRs quando aplicáveis

Estado efêmero de orquestração (checkpoint entre fases) pode ir em `.ahrena/workflow/issue-{n}/checkpoint.md`, **nunca** em `docs/`.

### 6. Scope creep é bloqueio, não aviso

O Gate 2 **DEVE** falhar se:

1. Arquivos modificados estão fora do escopo declarado na Fase 3.
2. Funções ou classes públicas novas não são justificadas por algum AC.

Quando detectado, o agente **DEVE** apresentar duas opções ao usuário:
- Ampliar os ACs (nova iteração do Gate 1) para cobrir o código adicional.
- Remover o código além do escopo do PR atual e abrir nova issue para ele.

## Abrangência

- **Aplica-se a:** qualquer invocação de `/cry-implement-issue` e qualquer atividade conduzida por `warrior-athena`.
- **Agentes vinculados:** `warrior-athena` (orquestrador) e todos os warriors/katas delegados durante o fluxo.
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Gate pulado:** PR criado sem o Gate 2 equivale a código não revisado em produção; bloqueia merge e exige reabertura do fluxo a partir da Fase 5.
2. **Rastreabilidade quebrada:** AC sem teste ou teste sem AC invalida o PR; requer correção antes de reabrir o Gate 2.
3. **ADR ausente:** decisão arquitetural sem ADR deixa a organização sem histórico de racional; ADR deve ser escrito retroativamente antes do merge.
4. **Documentação fora de `docs/`:** quebra o padrão de auditoria; arquivos devem ser movidos para a estrutura correta antes do merge.
5. **Scope creep não declarado:** código além do escopo é revertido ou justificado em nova iteração do Gate 1.

## Exemplos

### Correto

```
# Fluxo conduzido a partir de uma issue existente:
/cry-implement-issue 42 guardiafinance/ahrena

# Athena lê a issue #42, produz:
# docs/issues/issue-42/01-brief.md
# docs/issues/issue-42/02-requirements.md   (AC-1, AC-2, AC-3)
# docs/issues/issue-42/03-architecture.md
# docs/adr/ADR-007-use-fastapi-routers.md   (decisão relevante)

# Aguarda Gate 1 → humano aprova
# Apollo implementa: cada teste referencia AC-N
# Gate 2 executa 6 checks, todos ✅
# docs/issues/issue-42/06-quality-report.md registra o resultado
# PR criado com body referenciando os artefatos acima
```

### Incorreto

```
# ❌ Athena inicia o fluxo sem issue:
/cry-implement-issue "adicionar refund"

# ❌ Humano pede "pular Gate 1, já está ok":
# (Gate 1 é obrigatório — Athena deve recusar)

# ❌ Teste novo sem ligação a AC:
# def test_random_helper(): ...   (sem docstring AC-N)

# ❌ ADR salvo em local incorreto:
# .ahrena/workflow/issue-42/adr.md
# (o caminho correto é docs/adr/ADR-{n}-*.md)

# ❌ Modificação de arquivo fora do escopo declarado:
# (Gate 2 bloqueia; usuário decide entre ampliar AC ou abrir nova issue)
```

## Validação Automatizada

- **Ferramenta:** `kata-quality-gate` (Gate 2) executa a verificação de rastreabilidade, scope creep e best practices antes do PR; `scripts/validate.py` verifica a presença obrigatória de artefatos em `docs/issues/issue-{n}/` quando o fluxo é concluído.
- **Momento:** Gate 1 (antes da Fase 4), Gate 2 (antes da Fase 7).
- **Métrica:** 100% das issues passam por ambos os gates; 100% dos ACs têm pelo menos um teste; 0 testes sem AC correspondente; 100% das decisões arquiteturais relevantes têm ADR em `docs/adr/`.
