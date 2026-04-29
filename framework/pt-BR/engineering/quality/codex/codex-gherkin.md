# Codex: Gherkin no Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Engenharia — Qualidade. Subset de Gherkin adotado, layout de arquivos, tags e padrões concretos para `07-bdd-scenarios.md` e `*.feature`.

## Visão Geral

Este Codex é o **manual operacional do Gherkin** no Guardia. Define exatamente quais palavras-chave usamos, onde os arquivos vivem, como são taggeados e quais padrões aplicar para cada tipo de cenário. Junto com `lex-bdd-gherkin-format`, é o que `warrior-themis` consulta linha a linha ao escrever cenários.

## Contexto

- **Domínio:** sintaxe Gherkin aplicada à Fase 8 do fluxo Issue-Driven.
- **Público-alvo:** `warrior-themis`, autores e revisores de `07-bdd-scenarios.md` ou `*.feature`.
- **Atualização:** quando padrões de cenário se mostram repetitivos (oportunidade de novo template), quando linters detectam novos anti-patterns frequentes, quando a stack de testes muda de forma a afetar convenção de nomeação.

## Conteúdo

### 1. Subset adotado

Usamos um subset enxuto. Tudo fora desta lista **não é aceito** em revisão:

| Adotado | Uso |
|---|---|
| `Feature:` (`Funcionalidade:`) | Cabeçalho do bloco; nome em frase nominal |
| `Background:` (`Contexto:`) | Pré-condição de negócio compartilhada |
| `Scenario:` (`Cenário:`) | Comportamento concreto |
| `Scenario Outline:` (`Esquema do Cenário:`) + `Examples:` (`Exemplos:`) | Cenário paramétrico |
| `Given` (`Dado`) / `When` (`Quando`) / `Then` (`Então`) | Passos principais |
| `And` (`E`) / `But` (`Mas`) | Continuação do passo anterior |
| Doc strings `"""..."""` | Apenas quando o passo precisa de texto longo (ex.: mensagem que o cliente recebe) |
| Data tables `| col | col |` | Apenas para dados de exemplo paramétricos |
| Tags `@AC-{N}`, `@happy-path`, etc. | Rastreabilidade e taxonomia |
| Comentários `# ...` | Para id `SCN-{N}` quando não for parte do título |

| Excluído | Por que |
|---|---|
| `Rule:` | Introduz hierarquia que não usamos; resolva agrupamento via Feature ou tags |
| `*` como passo livre | Reduz clareza do papel do passo (Given/When/Then) |
| Custom keywords / extensões | Cada plugin acoplaria a um runner — proibido por `lex-bdd-no-framework-coupling` |

### 2. Layout dos arquivos

**Padrão (preferido):** consolidado em `07-bdd-scenarios.md`.

```
docs/
└── issues/
    └── issue-42/
        ├── 01-brief.md
        ├── 02-requirements.md
        ├── 03-architecture.md
        ├── 07-bdd-scenarios.md      ← consolidado
        └── 08-bdd-validation-report.md
```

**Volume justifica split:** quando há > 3 Features ou > 30 cenários no mesmo issue, separar:

```
docs/issues/issue-42/
├── 07-bdd-scenarios.md              ← índice + frontmatter
└── scenarios/
    ├── transfer-scheduling.feature
    ├── transfer-cancellation.feature
    └── transfer-execution.feature
```

O `07-bdd-scenarios.md` neste caso contém só o frontmatter e a lista de arquivos `.feature`.

### 3. Frontmatter de `07-bdd-scenarios.md`

YAML obrigatório no topo do arquivo, declarando origem e cobertura:

```yaml
---
issue: 42
repo: guardiafinance/ahrena
generated_at: "2026-04-29T14:00:00Z"
generated_by: warrior-themis
sources:
  github_issue: "guardiafinance/ahrena#42"
  notion_pages:
    - "https://www.notion.so/page-id-1"
  flow_artifacts:
    - docs/issues/issue-42/01-brief.md
    - docs/issues/issue-42/02-requirements.md
    - docs/issues/issue-42/03-architecture.md
ac_coverage:
  - ac: AC-1
    scenarios: [SCN-1]
  - ac: AC-2
    scenarios: [SCN-2, SCN-3]
  - ac: AC-3
    scenarios: [SCN-4, SCN-5, SCN-6]
---
```

Caminhos sob `src/`, `app/`, `lib/`, `tests/` em `sources` invalidam o artefato (per `lex-bdd-spec-only-sources`).

### 4. Idioma do bloco Gherkin

Primeira linha do bloco Gherkin (após o frontmatter):

```gherkin
# language: pt-BR
```

Obrigatório quando o idioma não é `en`. Consistente dentro do mesmo arquivo. Idiomas suportados: `pt-BR`, `es`, `en`. Para projetos multi-time, `en` é o padrão pragmático.

### 5. Taxonomia de tags

| Categoria | Tags | Quantidade por cenário |
|---|---|---|
| AC | `@AC-1`, `@AC-2`, ... | **≥ 1** (obrigatória) |
| Tipo | `@happy-path` \| `@alternative` \| `@edge` \| `@error` \| `@nfr` | **exatamente 1** (obrigatória) |
| Área (opcional) | `@backend`, `@frontend`, `@mobile`, `@api`, `@worker` | 0..1 |
| Prioridade (opcional) | `@critical`, `@regression`, `@smoke` | 0..1 |

Tags vão em **uma linha imediatamente acima** do `Scenario:` ou `Scenario Outline:`. Tags na Feature aplicam-se a todos os cenários do arquivo (ex.: `@backend` no topo da Feature evita repetição).

### 6. Id `SCN-{N}` — onde colocar

**Preferido:** no título do cenário.

```gherkin
@AC-1 @happy-path
Scenario: SCN-1 Cliente agenda transferência válida
```

**Aceito:** em comentário imediatamente acima.

```gherkin
# SCN-1
@AC-1 @happy-path
Scenario: Cliente agenda transferência válida
```

Regras:

- Único dentro do arquivo.
- Estável: ao editar texto do cenário, o id permanece (mantém rastreabilidade ao teste).
- Numeração contígua não é obrigatória; `SCN-1`, `SCN-2`, `SCN-4` é aceito (`SCN-3` foi removido em revisão).

### 7. Uso de `Background`

`Background` declara **pré-condição de negócio** compartilhada por todos os cenários do arquivo.

**Bom:**

```gherkin
Background:
  Dado um cliente ativo com conta corrente na carteira "Operacional"
  E o cliente tem o perfil de aprovador habilitado
```

**Ruim:**

```gherkin
Background:
  Dado um banco de dados Postgres limpo
  E a fila de eventos foi purgada
  E o serviço foi reiniciado
```

Setup técnico vive no código de teste (fixture, container), não no cenário. Per `lex-bdd-gherkin-format` Regra 6.

### 8. `Scenario Outline` — quando usar

Use **somente** quando há ≥ 3 variações paramétricas do mesmo trio Given/When/Then.

**Bom:**

```gherkin
@AC-2 @edge
Esquema do Cenário: SCN-3 Limites de saldo no agendamento
  Dado que o saldo disponível é R$ <saldo>
  Quando o cliente solicita uma transferência de R$ <valor>
  Então o sistema responde com <resultado>

  Exemplos:
    | saldo  | valor  | resultado                |
    | 100,00 | 50,00  | aprovação                |
    | 100,00 | 100,00 | aprovação                |
    | 100,00 | 100,01 | recusa por saldo         |
    | 100,00 | 0,00   | recusa por valor inválido |
```

**Ruim:** 1 ou 2 exemplos em outline (use cenários separados; outline com 1-2 linhas é overhead sem ganho).

Cabeçalhos da tabela de Examples em snake_case curtos. Valores monetários com formato consistente (R$ X,XX em pt-BR; $ X.XX em en).

### 9. Convenções de nomenclatura

| Elemento | Padrão | Exemplo |
|---|---|---|
| Feature | Frase nominal capitalizada | `Funcionalidade: Agendamento de transferência` |
| Scenario | `SCN-{N} <frase verbal em terceira pessoa>` | `Scenario: SCN-1 Cliente agenda transferência válida` |
| Steps | Terceira pessoa, voz ativa, presente | `Quando o cliente agenda uma transferência` (não "Você agenda...") |
| Doc string | Aspas triplas, indentação consistente | dentro do `Then` quando precisa citar mensagem literal |
| Tag | `@kebab-case` ou `@AC-{N}` | `@happy-path`, `@AC-3` |

### 10. Padrões comuns

#### 10.1 Cenário negativo (`@error`)

Mesmo `Given` do happy-path, `When` alterado, `Then` oposto:

```gherkin
@AC-3 @error
Cenário: SCN-4 Cliente tenta agendar sem saldo
  Dado que o saldo disponível é R$ 50,00
  Quando o cliente tenta agendar uma transferência de R$ 100,00
  Então o sistema recusa o agendamento por saldo insuficiente
  E nenhuma transferência é registrada
```

#### 10.2 Cenário de fronteira (`@edge`)

`Given` no valor exato da fronteira:

```gherkin
@AC-3 @edge
Cenário: SCN-5 Saldo igual ao valor mais a taxa
  Dado que o saldo disponível é R$ 100,00
  E a taxa de transferência é R$ 1,00
  Quando o cliente tenta agendar uma transferência de R$ 100,00
  Então o sistema recusa o agendamento por saldo insuficiente
```

#### 10.3 Cenário NFR (`@nfr`)

Comportamento observável de orçamento, latência, idempotência:

```gherkin
@AC-4 @nfr
Cenário: SCN-6 Resposta dentro do orçamento de latência
  Dado um cliente ativo
  Quando o cliente solicita o saldo disponível
  Então a resposta é entregue em até 1 segundo
```

#### 10.4 Idempotência (`@nfr`)

```gherkin
@AC-5 @nfr
Cenário: SCN-7 Reenvio do mesmo agendamento não duplica
  Dado um cliente que já agendou a transferência X
  Quando o cliente reenvia exatamente o mesmo agendamento X
  Então o sistema retorna o mesmo agendamento previamente registrado
  E nenhuma transferência adicional é criada
```

### 11. Anti-patterns (referência cruzada)

Lista canônica de padrões proibidos: `lex-bdd-gherkin-format` Regra 3. Resumo dos mais frequentes:

- Seletores de UI: `#id`, `.classe`, `input[name=...]`
- Métodos HTTP / status codes: `POST /api/...`, `status code 201`
- Nomes de função: `calcula_fee()`, `processPayment(...)`
- Nomes de tabela / SQL: `SELECT ...`, `INSERT INTO refunds`
- Caminhos de arquivo: `src/`, `app/`, `.py`, `.ts`
- JSON literal, headers HTTP, hashes

### 12. Lint — regex do verificador

Conjunto base usado pelo lint (e por `warrior-themis` na auto-revisão):

```
# proibições
\b(POST|GET|PUT|DELETE|PATCH)\s+/        # método HTTP + path
\bstatus\s+code\s+\d+                    # status code numérico
\b\d{3}\b\s+(OK|Created|Bad Request)     # status nomeado
\b[a-z_][a-z0-9_]*\([^)]*\)              # nomes de função/método
SELECT\s+|INSERT\s+INTO|UPDATE\s+\w+\s+SET   # SQL
src/|app/|lib/|tests/|spec/              # caminhos de implementação
#[a-zA-Z][\w-]+|\.[a-zA-Z][\w-]+         # seletores CSS
input\[[^\]]+\]                          # seletor de atributo
\.(py|ts|tsx|js|jsx|java|go)\b           # extensão de arquivo

# obrigatórios (por cenário)
@AC-\d+                                  # ≥ 1
@(happy-path|alternative|edge|error|nfr) # exatamente 1
SCN-\d+                                  # único no arquivo
```

`warrior-themis` aplica este check antes de salvar `07-bdd-scenarios.md`. PR que falhe o lint é bloqueado pelo Gate 3 (`kata-quality-gate` Check 8).

### 13. Exemplo completo

```yaml
---
issue: 42
repo: guardiafinance/ahrena
generated_at: "2026-04-29T14:00:00Z"
generated_by: warrior-themis
sources:
  github_issue: "guardiafinance/ahrena#42"
  notion_pages:
    - "https://www.notion.so/transfer-spec"
  flow_artifacts:
    - docs/issues/issue-42/01-brief.md
    - docs/issues/issue-42/02-requirements.md
    - docs/issues/issue-42/03-architecture.md
ac_coverage:
  - ac: AC-1
    scenarios: [SCN-1]
  - ac: AC-2
    scenarios: [SCN-2]
  - ac: AC-3
    scenarios: [SCN-3, SCN-4]
  - ac: AC-4
    scenarios: [SCN-5]
---
```

```gherkin
# language: pt-BR
@backend
Funcionalidade: Agendamento de transferência

  Contexto:
    Dado um cliente ativo com conta corrente na carteira "Operacional"

  @AC-1 @happy-path
  Cenário: SCN-1 Cliente agenda transferência válida
    Dado que o saldo disponível é R$ 1.000,00
    Quando o cliente agenda uma transferência de R$ 100,00 para amanhã
    Então a transferência é registrada como agendada
    E o cliente recebe confirmação com a data de execução prevista

  @AC-2 @alternative
  Cenário: SCN-2 Cliente agenda usando perfil aprovador
    Dado que o cliente tem o perfil de aprovador habilitado
    E o saldo disponível é R$ 1.000,00
    Quando o cliente agenda uma transferência de R$ 100,00 com aprovação imediata
    Então a transferência é registrada como agendada e pré-aprovada

  @AC-3 @error
  Cenário: SCN-3 Cliente tenta agendar sem saldo
    Dado que o saldo disponível é R$ 50,00
    Quando o cliente tenta agendar uma transferência de R$ 100,00
    Então o sistema recusa o agendamento por saldo insuficiente
    E nenhuma transferência é registrada

  @AC-3 @edge
  Esquema do Cenário: SCN-4 Limites do saldo no agendamento
    Dado que o saldo disponível é R$ <saldo>
    Quando o cliente solicita uma transferência de R$ <valor>
    Então o sistema responde com <resultado>

    Exemplos:
      | saldo    | valor    | resultado                |
      | 100,00   | 100,00   | aprovação                |
      | 100,00   | 100,01   | recusa por saldo         |
      | 0,00     | 1,00     | recusa por saldo         |

  @AC-4 @nfr
  Cenário: SCN-5 Resposta dentro do orçamento de latência
    Dado um cliente ativo
    Quando o cliente solicita o saldo disponível
    Então a resposta é entregue em até 1 segundo
```

## Referências

- `lex-bdd-spec-only-sources` — fontes permitidas
- `lex-bdd-gherkin-format` — formato declarativo (lei aplicada por este Codex)
- `lex-bdd-no-framework-coupling` — sem step-runner
- `codex-bdd` — princípios de BDD no Guardia
- `kata-bdd-scenarios-design` — produção de cenários
- `kata-bdd-validate-implementation` — validação cenário↔teste
- [Cucumber: Gherkin Reference](https://cucumber.io/docs/gherkin/reference/)
