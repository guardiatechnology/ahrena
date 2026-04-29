# Codex: Behavior-Driven Development no Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Engenharia — Qualidade. Princípios e prática de BDD aplicados na Fase 8 do fluxo Issue-Driven.

## Visão Geral

Este Codex é a referência operacional para **validação comportamental** de features no Guardia. Consultado por `warrior-themis` ao desenhar cenários, por `warrior-athena` ao decidir delegação, e por revisores de PR no Gate 3.

BDD aqui não é metodologia de planejamento nem framework de teste — é um **mecanismo de validação black-box** que protege contra "construímos a coisa errada", complementando a rastreabilidade AC↔teste já exigida por `lex-issue-driven`.

## Contexto

- **Domínio:** validação comportamental pós-implementação (Fase 8 do fluxo Issue-Driven).
- **Público-alvo:** `warrior-themis`, `warrior-athena`, `warrior-hera`, revisores que abrem ou aprovam PRs.
- **Atualização:** quando a taxonomia de cenários se mostra insuficiente, quando novos tipos de fonte são adotados (ex.: especificação em Figma), ou quando padrões anti-pattern se repetem em revisões.

## Conteúdo

### 1. Por que BDD no Guardia

A rastreabilidade AC↔teste obrigada por `lex-issue-driven` Regra 3 garante que cada AC tem teste e cada teste tem AC. Mas não garante que **o teste valida o comportamento certo**: um AC ambíguo pode receber um teste que passa sem demonstrar a regra de negócio.

BDD fecha essa fresta:

| Sem BDD | Com BDD |
|---|---|
| AC: "deve validar saldo" → teste: `assert response.status_code == 422` | AC: "deve validar saldo" → SCN-1: "dado saldo X, quando solicita Y > X, então recusa por saldo insuficiente" → teste valida a regra de negócio observável |

A diferença é simples: **cenário descreve comportamento; teste valida cenário**. Se o cenário foi escrito sem olhar o código (`lex-bdd-spec-only-sources`), divergência entre pedido e entrega aparece no mapeamento.

### 2. Hierarquia de fontes

`warrior-themis` consulta as fontes nesta ordem (sempre cega para `src/`):

```
1. docs/issues/issue-{n}/02-requirements.md   ← ACs numerados
2. docs/issues/issue-{n}/01-brief.md          ← contexto da Issue
3. GitHub Issue #{n}                          ← título, corpo, comentários
4. Páginas Notion referenciadas               ← especificação detalhada
5. docs/issues/issue-{n}/03-architecture.md   ← restrições, contratos
6. ADRs em docs/adr/                          ← quando referenciados
```

Se essas fontes não bastam, **a Issue está incompleta** — o agente para e devolve à origem (per `lex-bdd-spec-only-sources` Regra 4). Nunca recorre ao código como atalho.

### 3. Three Amigos no nosso contexto

O ritual clássico (PM + Dev + QA em sala) é assíncrono e distribuído aqui:

| Papel | Quem | Onde conversa |
|---|---|---|
| PM (autor do pedido) | autor da Issue | corpo da Issue + páginas Notion |
| Tech Lead (viabilidade) | autor de `03-architecture.md` | comentários do `03-architecture.md` e da Issue |
| Validador (cenários) | `warrior-themis` | `07-bdd-scenarios.md` + comentários na Issue para ambiguidades |

Quando um cenário não consegue ser escrito a partir das fontes, `warrior-themis` abre comentário na Issue listando as ambiguidades. PM e Tech Lead respondem; o cenário é escrito quando as três vozes convergem por escrito. Sem reunião síncrona — a evidência fica no histórico.

### 4. Taxonomia de cenários

Cada cenário tem **uma** tag de tipo. Use esta tabela como guia:

| Tag | Quando | Regra de cobertura |
|---|---|---|
| `@happy-path` | Caminho principal: tudo de input válido, fluxo de sucesso | **Toda AC** precisa de pelo menos 1 |
| `@alternative` | Caminho de sucesso alternativo (mesma intenção, branch diferente) | Quando a AC menciona "ou", "se já existe", "quando o usuário tem perfil X" |
| `@edge` | Limites, fronteiras, dados extremos válidos | ACs com limites numéricos, ranges, datas, tamanhos máximos |
| `@error` | Falha esperada com tratamento definido | ACs com requisito negativo explícito ("recusa quando", "rejeita se") |
| `@nfr` | Requisito não-funcional observável (latência, idempotência, disponibilidade) | Quando NFRs são parte do AC ou do `03-architecture.md` |

**Mínimo aceitável por AC:** 1 happy-path + (1 error se há requisito negativo) + (1 edge se há fronteira numérica/temporal). Cobertura completa exige todos os tipos aplicáveis.

### 5. De AC para SCN

Padrão para transformar AC numerado em cenários:

```
AC-3: O sistema deve recusar agendamento de transferência
       quando o saldo disponível é menor que o valor solicitado,
       informando o motivo ao cliente.
```

Quebra em comportamentos observáveis:

```
SCN-3.1 @AC-3 @error
  Saldo insuficiente para o valor exato → recusa com motivo

SCN-3.2 @AC-3 @edge
  Saldo igual ao valor (incluindo taxa) → recusa por borda

SCN-3.3 @AC-3 @happy-path
  Saldo suficiente → aceita (cobre o "deve recusar" pelo contraste)
```

Use o eixo do template de Issue (Why/What/How) como bússola: o **What** vira o `When` do cenário; o **How** observável vira o `Then`; o **Why** geralmente fica como contexto na descrição da Feature.

### 6. Linguagem ubíqua

Cenários que tocam domínio core (transferência, conciliação, lançamento contábil, evento contábil) **DEVEM** usar os termos do modelo de domínio produzido por `warrior-theseus` ou pelo Event Storm (`kata-event-storm`). Termos divergentes em cenários geram drift entre design e implementação.

| Bom | Ruim |
|---|---|
| "o cliente agenda uma transferência" | "o usuário cria um registro de transferência" |
| "a conciliação é aprovada" | "o status do reconcile vira 'approved'" |
| "o lançamento contábil é estornado" | "a entrada do ledger é deletada" |

Quando o termo do domínio ainda não existe, **o cenário cria uma dúvida explícita** na Issue (per Three Amigos) antes de inventar nomenclatura.

### 7. Definition of Done do conjunto de cenários

`07-bdd-scenarios.md` está pronto quando:

1. **Toda AC tem ≥ 1 cenário** (cobertura básica).
2. **Toda AC com requisito negativo tem ≥ 1 `@error`**.
3. **Toda AC com fronteira numérica/temporal tem ≥ 1 `@edge`**.
4. **Frontmatter declara apenas fontes permitidas** (per `lex-bdd-spec-only-sources` Regra 3).
5. **Lint de formato passa** (per `lex-bdd-gherkin-format` validação).
6. **Ids `SCN-{N}` únicos** dentro do arquivo.
7. **Sem ambiguidades pendentes** — comentários na Issue resolvidos ou cenários removidos.

### 8. Anti-patterns

| Anti-pattern | Por que é ruim | Sintoma |
|---|---|---|
| Cenário imperativo ("clica em ...", "POST /api/...") | Acopla a UI/protocolo, envelhece mal | `lex-bdd-gherkin-format` lint rejeita |
| Cenário por tela | Cobre layout, não comportamento | Várias telas com mesmo cenário rodando — Background é o lugar certo |
| Cenário por função | Já existe teste unitário; cenário não acrescenta | SCN cita nome de função |
| Boilerplate de "logado" no Given de todo cenário | Repetição que mascara o `When` real | Mover para `Background` |
| `Then` sem resultado observável | Cenário não testa nada | `Then a operação acontece` (sem efeito declarado) |
| Cenário com ordem implícita ("após SCN-1, ...") | Quebra independência exigida por `lex-bdd-gherkin-format` Regra 5 | Refatorar com Background ou Given explícito |

### 9. Relação com `kata-test-plan-design`

Cenário e teste são **complementares**:

| Artefato | Pergunta que responde |
|---|---|
| Cenário (BDD) | "**Qual** comportamento o sistema deve ter?" |
| Plano de testes | "**Em qual nível** validamos cada comportamento?" |
| Teste implementado | "**Como** o validamos no código de teste?" |

Um SCN pode mapear para 1 teste (caminho simples), 2 testes (unit + integração), ou N testes (unit + integração + E2E quando jornada crítica). `kata-bdd-validate-implementation` produz o mapa em `08-bdd-validation-report.md`.

### 10. Glossário

| Termo | Definição no Guardia |
|---|---|
| **Feature** | Bloco Gherkin que agrupa cenários de uma funcionalidade ou epic |
| **Background** | Pré-condição compartilhada entre cenários da mesma Feature, em linguagem de negócio |
| **Scenario** | Comportamento observável; um caso concreto Given/When/Then |
| **Scenario Outline + Examples** | Cenário paramétrico; uma estrutura, vários exemplos em tabela |
| **SCN-{N}** | Identificador único do cenário, usado para rastrear ↔ teste |
| **Linguagem ubíqua** | Vocabulário do domínio compartilhado entre negócio, design e engenharia |
| **Three Amigos** | PM + Tech Lead + Validador conversando sobre cada cenário (assíncrono no Guardia) |
| **Black-box validation** | Validação que ignora como o sistema é construído, só observa o que ele faz |

## Referências

- `lex-bdd-spec-only-sources` — fontes permitidas para derivar cenários
- `lex-bdd-gherkin-format` — formato Gherkin obrigatório
- `lex-bdd-no-framework-coupling` — implementação dos testes sem step-runner
- `codex-gherkin` — manual do Gherkin adotado
- `codex-test-strategy` — escolha de níveis de teste
- `kata-bdd-scenarios-design` — produção do `07-bdd-scenarios.md`
- `kata-bdd-validate-implementation` — produção do `08-bdd-validation-report.md`
- `warrior-themis` — agente da Fase 8
- `lex-issue-driven` — fluxo que precede a Fase 8
- [North, "Introducing BDD" (2006)](https://dannorth.net/introducing-bdd/)
