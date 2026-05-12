# Kata: Desenhar Plano de Testes

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Desenho de plano de testes para uma feature — distribui ACs pelos níveis certos, define cobertura esperada, identifica riscos e gaps

## Objetivo

Dada uma feature com requisitos (ACs numerados) e arquitetura (componentes afetados), produzir um **plano de testes estruturado** que mapeia cada AC aos níveis apropriados (unit, integration, E2E), identifica cenários de erro e borda, e documenta gaps conhecidos. O plano serve como entrada para Apollo/Hephaestus implementarem testes com rastreabilidade, e como input para o Gate 2 validar cobertura.

## Quando Usar

- Fase 2.5 (opcional) do fluxo Issue-Driven, quando a feature é complexa o suficiente para beneficiar de plano explícito antes da implementação
- Invocada por `warrior-hera` diretamente ou delegada por `warrior-athena` em features tier-1
- Também aplicável fora do fluxo Issue-Driven para auditar cobertura de feature existente

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Requisitos (ACs) | Sim | `.issues/{n}/02-requirements.md` ou lista equivalente |
| Arquitetura | Sim | Lista de componentes afetados (fase 3 do fluxo Issue-Driven) |
| Stack | Sim | Linguagens, frameworks detectados |
| Criticidade | Não | Tier (1/2/3/4); default 2 |

## Workflow

```
Progresso:
- [ ] 1. Mapear ACs aos níveis de teste apropriados
- [ ] 2. Identificar cenários além do caso feliz
- [ ] 3. Identificar fronteiras e riscos
- [ ] 4. Definir cobertura-alvo por componente
- [ ] 5. Listar ferramentas e fixtures necessárias
- [ ] 6. Persistir em .issues/{n}/02b-test-plan.md
- [ ] 7. Atualizar checkpoint
```

### Passo 1: Mapear ACs aos níveis

Para cada AC:

1. Identificar **tipo de comportamento**: lógica pura? persistência? UI? integração externa?
2. Atribuir nível primário conforme decision tree em `codex-test-strategy`:
   - Lógica pura → **Unit**
   - Persistência / integração real → **Integration**
   - Contrato externo / fluxo multi-endpoint → **E2E API**
   - Jornada de usuário crítica → **E2E UI**
3. Decidir se AC também merece cobertura em nível adjacente (ex.: AC do repositório tem unit do domain + integration do repo).

Produzir tabela:

| AC | Comportamento | Nível primário | Nível adjacente | Justificativa |
|---|---|---|---|---|
| AC-1 | Criar refund via POST /v1/refunds | Integration | E2E API | Cruza service + repository + DB real |
| AC-2 | Idempotência via Idempotency-Key | Integration | Unit (hash key) | — |
| AC-3 | Refund após 30 dias retorna 422 | Unit (domain) | Integration | Regra pura de negócio + integração prova HTTP |

### Passo 2: Cenários além do caso feliz

Para cada AC, **obrigatório** identificar:

- **Erros conhecidos**: inputs inválidos, precondições não atendidas
- **Bordas**: limites (amount = 0, amount = máximo), concorrência (duplo submit)
- **Idempotência / replay**: repetir a operação produz mesmo resultado?
- **Falhas de dependência**: BD fora, API externa 500, timeout

Cenários extras viram **testes adicionais** (não duplicam ACs, estendem-nos).

### Passo 3: Fronteiras e riscos

Listar explicitamente:

- **Fronteiras externas** que serão mockadas: quais? como? contratos atualizados?
- **Datos sensíveis** em fixtures: mascarar/redact; nunca dados reais de clientes.
- **Custos reais** de E2E (ex.: Stripe sandbox gera token real → limpeza necessária).
- **Tempo de execução estimado**: somar por nível; se passar budget (`codex-test-strategy`), escalar para humano.

### Passo 4: Cobertura-alvo

Por criticidade:

| Tier | Cobertura mínima | Mutation score | Comentário |
|---|---:|---:|---|
| Tier 1 (receita, segurança crítica) | 90% | >70% | Investimento justificado |
| Tier 2 (importante) | 80% | — | Default |
| Tier 3 | 70% | — | Cobertura básica |
| Tier 4 (interno) | 60% | — | Só caminho feliz + erros óbvios |

Ajustar `quality.coverage_threshold` em `.ahrena/.directives` se diferente do default 80%.

### Passo 5: Ferramentas e fixtures

- **Ferramentas por nível**: conforme `codex-test-strategy`
- **Fixtures reutilizáveis**: identificar factories novas necessárias
- **Containers**: listar imagens Docker (Postgres, Redis, LocalStack para AWS)
- **Dados de teste**: datasets necessários; onde ficam (fixtures/, seeds/)

### Passo 6: Persistir o plano

Estrutura em `.issues/{n}/02b-test-plan.md`:

```markdown
# Plano de Testes — Issue #{n}: {título}

- **Referências:** [Requisitos](./02-requirements.md) · [Arquitetura](./03-architecture.md)
- **Criticidade (tier):** 2
- **Cobertura-alvo:** 80%

## Mapeamento AC → Níveis

| AC | Nível primário | Nível adjacente | Justificativa |
|---|---|---|---|

## Cenários adicionais

### AC-1
- Erros: amount negativo, payment_id inexistente, pagamento já reembolsado
- Bordas: refund igual ao valor original; refund 1 centavo menos
- Idempotência: 2x mesmo Idempotency-Key → 1 refund
- Falhas: BD timeout, evento não publica

## Fronteiras mockadas

- Stripe: sandbox quando disponível, contract test vs Pact
- SNS: real em staging; moto/localstack em integration

## Recursos necessários

- Container: `postgres:16`
- Fixtures novas: `RefundFactory`, `PaymentWithCaptureFactory`
- Dataset: nenhum novo (reusa fixtures globais)

## Riscos e gaps

- E2E UI não coberto nesta iteração (sem UI de refund para cliente final ainda)
- Mutation testing: rodar em ciclo offline mensal (não no CI de cada PR)
```

### Passo 7: Atualizar checkpoint

Adicionar entrada no `.ahrena/workflow/issue-{n}/checkpoint.md`:

```yaml
test_plan:
  artifact: .issues/{n}/02b-test-plan.md
  total_acs_mapped: 5
  coverage_target: 80
  tier: 2
```

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Plano de testes estruturado | Markdown | `.issues/{n}/02b-test-plan.md` |
| Mapeamento AC → níveis | Tabela no plano | — |
| Lista de fixtures/containers | Seção no plano | — |

## Restrições

- **Não escreve testes**: esta kata planeja; escrita real é de Apollo/Hephaestus.
- **Plano vinculante para Gate 2**: se o plano define Integration para AC-1, o Gate 2 verifica que existe integration test para AC-1.
- **Tier declarado explicitamente**: se omitido, Gate 2 assume tier 2 (80% cobertura).
- **Destino fixo**: `.issues/{n}/02b-test-plan.md` (seguindo convenção de `lex-issue-driven`).

## Referências

- `lex-test-pyramid`, `lex-test-isolation`
- `codex-test-strategy`
- `warrior-hera`
- `kata-quality-gate` — consome o plano no Gate 2
- `lex-issue-driven`
