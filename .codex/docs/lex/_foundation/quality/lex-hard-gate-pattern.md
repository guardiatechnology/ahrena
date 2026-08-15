# Lexis: Padrão HARD-GATE para Bloqueios em Lexis

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Sintaxe de bloqueios textuais em Lexis do framework Ahrena

## Lei

> **Toda Lexis que exige bloqueio de fluxo — ação proibida com pré-condições inegociáveis — DEVE conter um bloco `<HARD-GATE>` literal explicitando sujeito, ação, pré-condições, escopo, anti-pretextos e exceções. Lexis que declaram "MUST" textual sem este bloco, quando houver bloqueio efetivo, são consideradas incompletas e DEVEM ser revisadas para incluí-lo.**

## Regras

### 1. Quando aplicar HARD-GATE

Aplique quando a Lexis:

- Bloqueia ação concreta (criar issue, mergear PR, iniciar rollout, deployar agente)
- Tem pré-condições verificáveis programaticamente ou por checklist
- Não admite exceções implícitas ou negociáveis caso a caso

NÃO aplique quando a Lexis:

- Define apenas convenção (nomenclatura, casing) — basta o `MUST` textual
- Tem múltiplas exceções legítimas e contextuais sem checklist único
- Descreve atributo qualitativo sem ação concreta de bloqueio

### 2. Sintaxe canônica

```
<HARD-GATE>
{Sujeito} NÃO MAY {ação proibida no infinitivo} {alvo da ação}
sem que {pré-condição mínima inicial}.

Pré-condições obrigatórias:
  (a) {condição 1 — específica e verificável}
  (b) {condição 2 — específica e verificável}
  (c) {condição 3 — específica e verificável}
  ...

Esta regra se aplica a {escopo: TODA feature / agentes da plataforma / etc.},
independentemente de:
  - {anti-pretexto 1 — ex: tamanho percebido}
  - {anti-pretexto 2 — ex: urgência declarada}
  - {anti-pretexto 3 — ex: confiança do time}

Exceção {única / declarada}: {descrição literal ou "Nenhuma"}.
</HARD-GATE>
```

Os 6 elementos (sujeito, ação, pré-condições, escopo, anti-pretextos, exceção) são **obrigatórios**. Omitir qualquer um produz bloqueio fraco.

### 3. Posicionamento

O bloco `<HARD-GATE>` DEVE estar:

- Dentro de bloco de código fenced, com tag `HARD-GATE` literal nas linhas de abertura e fechamento
- Na **mesma seção** que define os critérios verificados — não em apêndice ou nota de rodapé

O posicionamento dentro do arquivo depende do tipo de artefato:

- **Em uma Lexis** — após a seção `Lei` (ou seção `Regras` quando houver), e antes de `Exemplos`
- **Em um Warrior** — após a seção que define as pré-condições verificadas (ex: `Autenticação`, `Ferramental`, `Inputs`) e antes da seção de comportamento operacional (ex: `Comportamento`, `Fluxo`, `Fases`)

### 4. Anti-pretextos

A lista `independentemente de` enumera 2 a 4 racionalizações comuns que humanos invocam para pular a lei. Forçá-las no texto torna o pretexto explícito e mais difícil de usar.

Exemplos canônicos de anti-pretextos:

- "tamanho percebido ('isso é trivial')"
- "urgência ('é incêndio')"
- "quem solicitou ('o CEO pediu')"
- "confiança do time ('já testamos muito')"
- "pressão de prazo"
- "tempo apertado de release"

### 5. Exceções declaradas

Quando houver exceção legítima, ela DEVE estar dentro do bloco `<HARD-GATE>` com:

- Tag explícita (ex: `incident:p0`, `prototype/*`, `sandbox`)
- Compensação retroativa quando aplicável (ex: "DoR retroativo em até 5 dias")
- Justificativa que **não** seja pretexto disfarçado

Exceções implícitas ou negociáveis caso a caso são FORBIDDEN no bloco. Se a Lexis admite múltiplas exceções não enumeráveis, ela não é candidata a HARD-GATE — é Lexis declarativa convencional.

### 6. Aplicabilidade plurilíngue

Lexis traduzidas (per [lex-framework-language](framework/pt-BR/_foundation/i18n/lexis/lex-framework-language.md)) DEVEM ter o bloco `<HARD-GATE>` traduzido **em todos os idiomas em `language.i18n`**, mantendo equivalência estrutural — mesmas pré-condições, mesmos anti-pretextos, mesmas exceções.

A tag `<HARD-GATE>` em si **não é traduzida** — é literal nos 3 idiomas. Apenas o conteúdo dentro do bloco é localizado.

## Exemplos

### Correto

Lexis aplicando HARD-GATE textual completo:

```markdown
## Lei

> Toda issue de feature MUST atender DoR canônico antes de existir.

<HARD-GATE>
warrior-athena NÃO MAY iniciar fluxo Issue-Driven sem que
kata-dor-validate retorne ✅ em TODOS os 9 critérios.

Pré-condições obrigatórias:
  (a) Discovery referenciada (docs/discovery/{topic}/insights.md)
  (b) PRD em docs/product/{feature}/prd.md aprovado
  (c) Capability Spec em docs/product/{feature}/capability-spec.md aprovado
  (d) Pacote técnico aprovado por Mômos
  (e) Wireframes aprovados quando UI
  (f) ACs numeradas presentes
  (g) Métricas leading + lagging declaradas
  (h) Dependências mapeadas
  (i) Busca anti-duplicação executada

Esta regra se aplica a TODA feature, independentemente de:
  - tamanho percebido ("isso é trivial")
  - urgência ("é incêndio")
  - quem solicitou ("o CEO pediu")

Exceção única: hotfix com label `incident:p0` — exige
DoR retroativo em até 5 dias.
</HARD-GATE>
```

### Incorreto

Bloqueio implícito sem sintaxe canônica:

```markdown
## Lei

> Toda issue de feature MUST atender DoR antes de existir.
> warrior-athena recusa issues incompletas.
```

Problemas:
- "recusa issues incompletas" é vago — não enumera as pré-condições
- Não declara escopo ("TODA feature" vs. subconjunto)
- Não enumera anti-pretextos
- Não declara exceções

Resultado: humanos invocam "este caso é diferente"; agentes interpretam ambiguamente.

## Validação Automatizada

- **Ferramenta:** revisão de PR humana enquanto linter dedicado não existe; futuramente `kata-design-validation` aplicado por warrior-momos parametrizado para tipo `lexis` deve verificar a presença e conformidade do bloco
- **Momento:** PR review de toda Lexis nova ou modificada
- **Métrica:** 100% das Lexis com cláusula de bloqueio têm bloco `<HARD-GATE>` correspondente nas 3 línguas (`language.i18n`)
