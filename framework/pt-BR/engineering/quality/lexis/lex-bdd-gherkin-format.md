# Lexis: Formato Gherkin Declarativo Obrigatório

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Engenharia — Qualidade. Formato e estilo de redação de todo cenário Gherkin produzido para validação BDD.

## Propósito

Cenário acoplado a seletor de UI vira obsoleto na próxima reestilização e deixa de descrever comportamento. Cenário com `status code 201` testa o protocolo, não a regra de negócio. BDD existe para proteger **intenção de comportamento** (linguagem ubíqua), não para duplicar testes de unidade ou contrato com prosa em torno.

Esta Lexis existe para que **um cenário sobreviva a refatorações de implementação** e **comunique inequivocamente o comportamento esperado a qualquer leitor de negócio ou de engenharia**.

## Lei

> **Todo cenário Gherkin produzido para validação BDD DEVE seguir Gherkin declarativo estrito: estruturado com `Feature`/`Background`/`Scenario`/`Scenario Outline` usando passos `Given`/`When`/`Then`/`And`; escrito em linguagem de negócio (linguagem ubíqua); livre de seletores de UI, status codes HTTP, nomes de função, nomes de tabela/coluna, caminhos de arquivo e qualquer outro detalhe de implementação. Cenários imperativos que narram cliques de UI ou artefatos técnicos são PROIBIDOS. Cada cenário DEVE ser independente (sem dependência de ordem de execução) e marcado com pelo menos uma tag de AC (`@AC-{N}`) e uma tag de tipo (`@happy-path` | `@alternative` | `@edge` | `@error` | `@nfr`).**

## Regras

### 1. Estrutura mandatória

Cada arquivo de cenários **DEVE** conter:

```gherkin
# language: pt-BR (ou en/es conforme idioma escolhido)
Funcionalidade: <título em linguagem de negócio>

  Contexto:
    Dado que <pré-condição compartilhada de negócio>

  @AC-1 @happy-path
  Cenário: SCN-1 <comportamento de negócio em uma frase>
    Dado que <estado inicial>
    Quando <ação de negócio>
    Então <resultado observável>

  @AC-2 @edge
  Esquema do Cenário: SCN-2 <variação parametrizada>
    Dado que o saldo é <saldo>
    Quando o usuário solicita <valor>
    Então o sistema responde com <resultado>

    Exemplos:
      | saldo | valor | resultado          |
      | 100   | 50    | aprovado           |
      | 100   | 200   | recusado por saldo |
```

A primeira linha **PODE** declarar o idioma do Gherkin (`# language: pt-BR`); na ausência, assume-se `en`.

### 2. Linguagem ubíqua, não técnica

Os passos descrevem **o que o negócio observa**, não como o sistema executa.

| Permitido (declarativo) | Proibido (imperativo/técnico) |
|---|---|
| "o cliente solicita um reembolso de R$ 50,00" | "POST /api/refunds com payload {amount: 5000}" |
| "o sistema rejeita o reembolso como duplicado" | "a resposta tem status code 409" |
| "o cliente recebe confirmação de que a transferência foi agendada" | "o e-mail é enviado pela função `send_email_async`" |
| "o saldo disponível é insuficiente" | "a coluna `available_balance` tem valor < amount" |
| "a operação é registrada no histórico do cliente" | "uma linha é inserida em `audit_log`" |

### 3. Padrões proibidos dentro de `Given`/`When`/`Then`

O lint **DEVE** rejeitar cenários contendo:

- Seletores CSS/XPath: `#id`, `.classe`, `input[name=...]`, `//div[...]`
- Verbos de UI: "clica", "preenche o campo", "aguarda o seletor", "rola até"
- Métodos HTTP e status: `POST`, `GET`, `PUT`, `DELETE`, `200`, `201`, `400`, `404`, `409`, `500`
- Nomes de função/método: `calcula_fee()`, `processPayment(...)`, qualquer identificador com parênteses
- Nomes de tabela/coluna em snake_case ou referência SQL: `SELECT ... FROM`, `INSERT INTO`, `UPDATE ... SET`
- Caminhos de arquivo ou módulo: `src/`, `app/`, `.py`, `.ts`, `.java`
- Headers HTTP, payloads JSON literais, bytes, hashes

### 4. Identificação e rastreabilidade

Cada `Scenario` ou `Scenario Outline` **DEVE**:

1. Ter um id único `SCN-{N}` no título (ou em comentário imediatamente acima).
2. Ter pelo menos uma tag `@AC-{N}` referenciando um critério de aceitação numerado em `02-requirements.md`.
3. Ter exatamente uma tag de tipo: `@happy-path`, `@alternative`, `@edge`, `@error` ou `@nfr`.

Esta tripla (id + AC + tipo) é o que `kata-bdd-validate-implementation` usa para mapear cenários aos testes.

### 5. Independência

Cenários do mesmo arquivo **NÃO PODEM** depender de ordem de execução. Cada cenário começa do estado declarado em `Background` mais seu próprio `Given`. Cenário que assume "depois do cenário anterior, ..." é violação.

### 6. `Background` só para pré-condição de negócio

`Background` **DEVE** declarar pré-condições compartilhadas em linguagem de negócio (ex.: "Dado um cliente ativo na carteira X"). Setup técnico (banco vazio, fila purgada, mock configurado) **NÃO PODE** aparecer em `Background` — pertence ao código de teste, não ao cenário.

### 7. Idioma do Gherkin

O idioma dos passos segue `language.default` em `.ahrena/.directives` para projetos cujo time fala esse idioma. Projetos multi-time **PODEM** escrever cenários em `en`. O idioma escolhido **DEVE** ser consistente dentro do mesmo arquivo `.feature` (ou `07-bdd-scenarios.md`).

## Abrangência

- **Aplica-se a:** todo arquivo `.feature` ou `07-bdd-scenarios.md` produzido na Fase 8 do fluxo Issue-Driven; também aplica-se a cenários BDD produzidos fora do fluxo (p. ex. discovery de domínio).
- **Agentes vinculados:** `warrior-themis` (produz), qualquer agente que edite cenários, `kata-bdd-scenarios-design`, `kata-bdd-validate-implementation`.
- **Exceções:** Nenhuma. Cenários que falhem o formato são regenerados, não corrigidos por patch.

## Consequências de Violação

1. **Bloqueio do Gate 3:** `kata-quality-gate` Check 8 falha quando o lint de cenários encontra padrões proibidos ou tags ausentes.
2. **Cenário descartado:** cenários imperativos são regenerados a partir das fontes de especificação (per `lex-bdd-spec-only-sources`), não consertados.
3. **Erosão de valor:** cenários acoplados a implementação envelhecem mal, viram dívida e treinam o time a ignorá-los — bloquear no gate previne que esse hábito se instale.

## Exemplos

### Correto

```gherkin
# language: pt-BR
Funcionalidade: Agendamento de transferência

  Contexto:
    Dado um cliente ativo com conta corrente na carteira "Operacional"

  @AC-1 @happy-path
  Cenário: SCN-1 Cliente agenda transferência válida
    Dado que o saldo disponível é R$ 1.000,00
    Quando o cliente agenda uma transferência de R$ 100,00 para amanhã
    Então a transferência é registrada como agendada
    E o cliente recebe confirmação com a data de execução prevista

  @AC-2 @error
  Cenário: SCN-2 Cliente tenta agendar transferência sem saldo
    Dado que o saldo disponível é R$ 50,00
    Quando o cliente tenta agendar uma transferência de R$ 100,00
    Então o sistema recusa o agendamento por saldo insuficiente
    E nenhuma transferência é registrada
```

### Incorreto

```gherkin
Funcionalidade: Agendamento de transferência

  Cenário: Sucesso
    Dado um POST em /api/transfers com {"amount": 10000, "scheduled_for": "2026-04-30"}
    Quando o usuário clica em #btn-confirm
    Então a resposta tem status code 201
    E a coluna status na tabela transfers é "scheduled"
```

Violações: status code, método HTTP, payload JSON, seletor de UI, nome de tabela e coluna, ausência de `@AC-{N}` e tag de tipo, ausência de id `SCN-{N}`, ausência de comportamento de negócio observável.

## Validação Automatizada

- **Ferramenta:** lint de cenários (regex set) que rejeita padrões proibidos enumerados na Regra 3; verificação obrigatória de tags `@AC-{N}` + tag de tipo em cada cenário; revisão manual no Gate 3 (`kata-quality-gate` Check 8).
- **Momento:** ao salvar `07-bdd-scenarios.md` no `kata-bdd-scenarios-design` e novamente no Gate 3 antes de `kata-pr-prepare`.
- **Métrica:** 0 cenários contendo padrões técnicos proibidos; 100% dos cenários com tag `@AC-{N}` e tag de tipo; 100% dos cenários com id `SCN-{N}` único.

## Referências

- `lex-bdd-spec-only-sources` — fontes permitidas para derivar os cenários
- `lex-bdd-no-framework-coupling` — implementação dos testes sem framework BDD
- `codex-bdd` — princípios de BDD no Guardia
- `codex-gherkin` — manual do Gherkin adotado no Guardia
- `kata-bdd-scenarios-design` — procedimento de produção dos cenários
