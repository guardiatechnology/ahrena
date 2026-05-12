# Kata: Elicitação de Requisitos (perspectiva PO)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Fase 2 do fluxo Issue-Driven — transformação do brief da Fase 1 em lista numerada de critérios de aceitação, DoD e out-of-scope

## Objetivo

Adotando a perspectiva de Product Owner, converter o brief produzido na Fase 1 em um documento de requisitos contendo: lista numerada de critérios de aceitação (ACs), Definition of Done (DoD), itens fora de escopo declarados explicitamente, e perguntas pendentes para o usuário. Os ACs numerados formam a base da rastreabilidade AC ↔ teste exigida pelo Gate 2 (conforme `lex-issue-driven`).

## Quando Usar

- Fase 2 do fluxo orquestrado por `warrior-athena`, após conclusão da Fase 1 (`kata-issue-analysis`)
- Quando é necessário formalizar critérios mensuráveis a partir de uma descrição genérica de feature/bugfix

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Brief da Fase 1 | Sim | `.issues/{n}/01-brief.md` |
| Confirmações do usuário | Não | Respostas a perguntas pendentes identificadas no brief (via interação) |

## Workflow

```
Progresso:
- [ ] 1. Ler o brief da Fase 1
- [ ] 2. Identificar atores, entidades e comportamentos
- [ ] 3. Formular ACs no padrão Given/When/Then
- [ ] 4. Resolver desconhecidos com perguntas ao usuário
- [ ] 5. Definir DoD e out-of-scope
- [ ] 6. Persistir em .issues/{n}/02-requirements.md
- [ ] 7. Atualizar checkpoint
```

### Passo 1: Ler o brief da Fase 1

1. Ler `.issues/{n}/01-brief.md`.
2. Se não existir, informar que a Fase 1 não foi executada e encerrar.
3. Focar nas seções: Problema, Contexto adicional, Tipo de trabalho, Riscos e desconhecidos.

### Passo 2: Identificar atores, entidades e comportamentos

1. Listar atores envolvidos (ex.: cliente, sistema de pagamento, backoffice).
2. Listar entidades afetadas (ex.: Refund, Payment, AuditLog).
3. Listar comportamentos esperados (ex.: "criar refund", "auditar tentativa", "notificar cliente").
4. Registrar os três grupos internamente para usar no Passo 3.

### Passo 3: Formular ACs no padrão Given/When/Then

Para cada comportamento identificado, formular um ou mais ACs no formato:

```
AC-{N}: {título curto}
  Dado que {precondição observável}
  Quando {ação ou evento}
  Então {resultado observável e mensurável}
```

**Regras para ACs:**
- Cada AC deve ser **testável** — se não há como escrever um teste, reescrever.
- Cada AC deve cobrir **um comportamento**, não múltiplos.
- ACs numerados sequencialmente a partir de `AC-1`, sem saltos.
- Cobrir casos felizes, casos de erro relevantes e bordas (ex.: idempotência, concorrência quando aplicável).

### Passo 4: Resolver desconhecidos com perguntas ao usuário

1. Para cada item em "Riscos e desconhecidos" do brief, formular pergunta objetiva ao usuário.
2. Perguntas em lote (até 5 por rodada) para não cansar o usuário.
3. Registrar respostas recebidas; se o usuário não puder responder agora, marcar o AC correspondente como `PENDENTE` e incluir na seção "Perguntas Pendentes" do documento final.
4. Não inventar respostas — se algo fica pendente, fica explicitamente pendente.

### Passo 5: Definir DoD e out-of-scope

1. **Definition of Done** — checklist objetivo:
   - Todos os ACs com teste correspondente (rastreabilidade `AC-N`)
   - Gate 2 aprovado
   - Documentação em `.issues/{n}/` completa
   - ADR(s) criados se houve decisão arquitetural relevante
   - PR aprovado por pelo menos 1 revisor

2. **Out of scope** — lista explícita do que **não** será feito nesta iteração:
   - Extrair do brief e da interação com o usuário
   - Cada item out-of-scope deve ter justificativa ou link para issue futura

### Passo 6: Persistir em `.issues/{n}/02-requirements.md`

Estrutura do documento:

```markdown
# Requisitos — Issue #{n}: {título}

- **Referência:** [Brief da Fase 1](./01-brief.md)
- **Data:** {YYYY-MM-DD}

## Critérios de Aceitação

### AC-1: {título curto}

- **Dado** {precondição}
- **Quando** {ação}
- **Então** {resultado}

### AC-2: {título curto}

...

## Definition of Done

- [ ] Todos os ACs acima têm pelo menos um teste com marcação `AC-N`
- [ ] Gate 2 (`kata-quality-gate`) aprovado
- [ ] Documentação completa em `.issues/{n}/`
- [ ] ADR(s) criados se aplicável em `docs/adr/`
- [ ] PR aprovado por pelo menos 1 revisor

## Out of Scope

- **{Item 1}:** {justificativa ou link para issue futura}
- **{Item 2}:** {justificativa ou link para issue futura}

## Perguntas Pendentes

- [ ] {Pergunta 1} — aguardando resposta de @{usuário}
- [ ] {Pergunta 2} — aguardando resposta de @{usuário}

## Próxima fase

Fase 3: design arquitetural (`kata-architecture-brief`).
```

### Passo 7: Atualizar checkpoint

1. Atualizar `.ahrena/workflow/issue-{n}/checkpoint.md` com:
   - fase concluída: 2
   - próxima fase: 3
   - referência: `.issues/{n}/02-requirements.md`
   - número total de ACs
   - perguntas pendentes (se houver)
2. Informar ao `warrior-athena`.

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Documento de requisitos | Markdown com ACs numerados | `.issues/{n}/02-requirements.md` |
| Checkpoint atualizado | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |
| Perguntas ao usuário (se houver) | Texto estruturado | Resposta ao orquestrador |

## Restrições

- **ACs devem ser testáveis:** não aceitar ACs vagos ("o sistema deve ser rápido"); sempre com métrica observável.
- **Numeração contínua:** `AC-1`, `AC-2`, `AC-3`... sem saltos; ACs removidos ficam como `AC-N: (removido — ver nota)` para preservar numeração em iterações.
- **Sem inferência de requisitos não documentados:** se não está no brief nem foi confirmado pelo usuário, fica em "Perguntas Pendentes".
- **Destino fixo:** `.issues/{n}/02-requirements.md` (conforme `lex-issue-driven`).

## Referências

- `lex-issue-driven` — leis do fluxo
- `codex-issue-workflow` — estrutura do fluxo e convenção de rastreabilidade
- `kata-issue-analysis` — kata predecessor (Fase 1)
- `kata-architecture-brief` — kata sucessor (Fase 3)
