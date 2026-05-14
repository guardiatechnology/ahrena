# Lexis: Sem Dívida Técnica Silenciosa

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Comentários e seções deixadas em código ou documentação durante a execução de um Plan ativo

## Propósito

Comentários `# TODO`, `# FIXME`, `# XXX`, `# follow-up`, `# later`, `# revisit` e seções de documentação do tipo `## TODO`, `## Follow-up`, `## Out of scope (to revisit)` são marcadores de dívida técnica silenciosa: eles registram que algo ficou para depois, mas não conectam aquele "depois" a uma Issue ou Plan rastreável. O resultado é entropia: a dívida acumula, ninguém é responsável e o usuário descobre semanas depois quando o débito vira incidente.

O framework Ahrena trata cada achado tangencial como **decisão deliberada**: o agente PAUSA, leva ao humano e oferece três caminhos explícitos — expandir o Plan atual, abrir um Plan novo sob o mesmo parent Issue, ou abrir uma Issue nova de capability. Nenhum desses caminhos é "deixar um TODO".

## Lei

> **Durante a execução de um Plan ativo (status `development`), commitar código com comentários `# TODO`, `// TODO`, `# FIXME`, `# XXX`, `# follow-up`, `# later`, `# revisit` (ou variantes equivalentes em outras linguagens) OU commitar documentação com seções `## TODO`, `## Follow-up`, `## Out of scope (to revisit)`, sem que esses marcadores referenciem uma Issue ou Plan rastreável (formato `# TODO(#NNN): ...` ou equivalente), é FORBIDDEN. Achados tangenciais identificados durante a execução DEVEM ser surfaceados ao humano com três opções explícitas: (a) expandir o escopo do Plan atual, (b) abrir Plan sub-issue novo sob o mesmo parent Issue, (c) abrir Issue parent nova de capability.**

## Abrangência

- **Aplica-se a:** todo código de aplicação (Python, TypeScript/JavaScript, Go, Swift, Kotlin, Dart) e toda documentação (Markdown sob `docs/`, `README.md`, comentários estruturados em código) commitada via um Plan em `status: development`
- **Agentes vinculados:** `warrior-athena`, `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`, `warrior-claudionor`, e qualquer warrior que execute código durante um Plan ativo
- **Exceções declaradas:** (i) comentários `# WHY: ...` que explicam decisão não-óbvia (lineage, não dívida); (ii) `pytest.mark.xfail(reason="bug:#N")` com número de Issue rastreável; (iii) blocos `<!-- not-flushed -->` em provider cache (`.claude/plans/`, `.cursor/plans/`) — scratch transitório, não canônico

## Aplicabilidade Prospectiva

Esta Lex aplica-se prospectivamente: comentários `# TODO`/`# FIXME`/`# follow-up` existentes em código histórico de projetos que adotaram Ahrena antes desta Lex **não** são bloqueados retroativamente. O lint detecta apenas marcadores adicionados ou modificados no diff do PR corrente. Migração de dívida histórica é trabalho de Plan dedicado, surfaceado quando relevante para o escopo do Plan corrente.

<HARD-GATE>
Todo agente NÃO DEVE commitar código ou documentação contendo
marcadores `# TODO`, `// TODO`, `# FIXME`, `# XXX`, `# follow-up`,
`# later`, `# revisit`, `## TODO`, `## Follow-up`, `## Out of scope`
sem referência a Issue ou Plan rastreável.

Pré-condições obrigatórias para commitar tais marcadores:
  (a) O marcador referencia uma Issue/Plan rastreável (ex: `# TODO(#NNN): descrição`)
  (b) Ou o achado foi surfaceado ao humano com 3 opções explícitas (expandir Plan, abrir Plan novo, abrir Issue nova)
  (c) E o humano confirmou a decisão por escrito (resposta na sessão ou comment na Issue)

Esta regra se aplica a TODO Plan em `status: development`, independentemente de:
  - "é só uma linha"
  - "o usuário não pediu mas vai precisar"
  - "é dívida técnica, não feature"
  - "é só um comentário, ninguém lê TODOs"

Exceções declaradas (não silenciosas):
  - Comentários `# WHY: ...` explicando decisão não-óbvia (lineage)
  - `pytest.mark.xfail(reason="bug:#N")` com Issue number rastreável
  - Blocos `<!-- not-flushed -->` em provider cache de plan
  - Marcadores pré-existentes no código histórico, fora do diff do PR atual
</HARD-GATE>

## Protocolo de Achado Tangencial

Ao identificar um achado fora do escopo declarado do Plan atual durante a execução, o agente DEVE:

1. PAUSAR a implementação corrente
2. Apresentar ao humano: descrição do achado, escopo afetado, custo estimado de tratar agora vs. depois
3. Oferecer três opções discretas:
   - **(a) Expandir o Plan atual** — se trivial e diretamente relacionado ao escopo corrente; requer atualizar o corpo da sub-issue Plan
   - **(b) Abrir novo Plan sub-issue** — se material mas separável, ainda sob o mesmo parent Issue (User Story / Bug / Tech Task)
   - **(c) Abrir nova Issue parent** — se constitui capability nova, não derivada do parent Issue atual
4. Registrar a decisão do humano na Issue/Plan correspondente antes de retomar
5. Nunca aceitar implicitamente como TODO silencioso

## Exemplos

### Correto

```python
# WHY: integer arithmetic on cents avoids floating-point error in money math
fee_cents = int(amount_cents * Decimal("0.015"))

# TODO(#172): switch to bank-specific fee table once spec arrives
return fee_cents
```

```python
@pytest.mark.xfail(reason="bug:#185 — race condition in retry path")
def test_concurrent_retries(): ...
```

### Incorreto

```python
# TODO: handle edge case later                    # FORBIDDEN — sem #N rastreável
def parse_value(raw: str) -> int:
    return int(raw)

# FIXME: this is broken for negative numbers      # FORBIDDEN — silencioso
def calc(x): return x * 2

# XXX: refactor when we have time                 # FORBIDDEN — silencioso
```

```markdown
## Out of scope (to revisit)                      <!-- FORBIDDEN — sem Issue/Plan -->
- Migration of legacy plans under docs/
- Cleanup of orphan worktrees
```

## Validação Automatizada

- **Ferramenta:** ripgrep pre-commit hook executando `rg -n '(^|\s)(# |// |## )(TODO|FIXME|XXX|follow-up|later|revisit)(?!\(#\d+\))'` no diff staged; extensão de `kata-quality-gate` (Check 4 ou check novo) que aplica o mesmo padrão ao diff do PR
- **Momento:** pre-commit local + Gate 2 do fluxo Issue-Driven em todo PR
- **Métrica:** 0 marcadores de dívida silenciosa adicionados/modificados no diff do PR; 100% dos achados tangenciais durante execução surfaceados ao humano com 3 opções explícitas
