# Codex: Planejamento de Tarefas por Agentes

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Criação, manutenção e ciclo de vida de planos de tarefas por agentes no contexto Ahrena

## Visão Geral

Este Codex é o manual canônico de planejamento de tarefas por agentes. Complementa `lex-agent-planning` (a Lei) com templates, exemplos de preenchimento, regras de numeração, boas práticas e diretrizes para casos-limite. Todo agente que cria planos DEVE consultar este Codex.

## Contexto

- **Domínio:** disciplina de execução de tarefas por agentes AI
- **Público-alvo:** todos os agentes (Claude, Cursor, warriors, katas) e revisores humanos
- **Atualização:** quando o template ou as convenções mudam (ADR recomendado para mudanças no front-matter)

---

## 1. Resolução do path de planos

O agente resolve o diretório de planos na seguinte ordem:

```
1. Ler .ahrena/.directives
2. Se paths.plans existir → usar esse valor (ex.: ".plans/")
3. Caso contrário → usar padrão por agente:
   - Claude Code (CLI, VSCode, Desktop, claude.ai) → .claude/plans/
   - Cursor                                         → .cursor/plans/
   - Agente desconhecido                            → .plans/
```

Exemplo de override no projeto:
```yaml
# .ahrena/.directives
paths:
  root: ".ahrena/"
  plans: ".plans/"    # override: todos os agentes usam .plans/
```

---

## 2. Convenção de nomeação de arquivos

```
plan-{NNN}-{slug}.md
```

| Campo | Regra |
|---|---|
| `{NNN}` | Número sequencial de 3 dígitos (001, 002, …). Incrementar a partir do maior número existente no diretório. Sem lacunas quando possível; se houver lacuna (plano abandonado), não reutilizar o número |
| `{slug}` | kebab-case, máximo 60 caracteres, resumo da tarefa |

Exemplos:
- `plan-001-complete-feature-design-docs.md`
- `plan-002-create-warrior-hecate.md`
- `plan-003-update-discovery-warriors.md`

---

## 3. Template completo do plano

```markdown
---
plan_id: "001"
title: "complete-feature-design-docs"
status: pending
agent: claude
issue: "guardiafinance/ahrena#42"
created_at: "2026-05-02T14:30:00Z"
updated_at: "2026-05-02T14:30:00Z"
---

# Plano: Complete Feature Design Docs — atualizar cries e katas

## Objetivo

Concluir a migração dos artefatos de design de feature para a estrutura canônica
`docs/{context}/{categoria}/` definida por `lex-feature-design-docs`. Os warriors e katas
já foram atualizados; faltam os Cries (entry points do usuário) e 2 katas com referências residuais.

## Escopo

Arquivos a modificar:
- `framework/pt-BR/engineering/platform/cries/cry-api-design.md`
- `framework/pt-BR/engineering/platform/cries/cry-event-storm.md`
- `framework/pt-BR/engineering/platform/cries/cry-feature-design.md`
- `framework/pt-BR/engineering/platform/cries/cry-full-design.md`
- `framework/pt-BR/engineering/platform/katas/kata-api-design-review.md`
- `framework/pt-BR/engineering/platform/katas/kata-api-design-doc.md`
- Equivalentes em `framework/en/` e `framework/es/`
- `.cursor/skills/` e `.cursor/commands/` correspondentes

Total: ~18 arquivos.

## Etapas

- [ ] 1. Abrir issue no GitHub para rastrear este trabalho
- [ ] 2. Criar branch `feat/{N}-complete-feature-design-docs`
- [ ] 3. Atualizar `cry-api-design.md` (pt-BR, en, es)
- [ ] 4. Atualizar `cry-event-storm.md` (pt-BR, en, es)
- [ ] 5. Atualizar `cry-feature-design.md` (pt-BR, en, es)
- [ ] 6. Atualizar `cry-full-design.md` (pt-BR, en, es)
- [ ] 7. Atualizar `kata-api-design-review.md` (pt-BR, en, es)
- [ ] 8. Corrigir `kata-api-design-doc.md` (pt-BR, en, es)
- [ ] 9. Atualizar `.cursor/commands/` e `.cursor/skills/` afetados
- [ ] 10. Commitar todos os artefatos anteriores (feature-design-docs novos + cries + katas)
- [ ] 11. Abrir PR referenciando a issue

## Dependências

- Trabalho anterior (uncommitted): `lex-feature-design-docs`, `codex-feature-design-docs`, `kata-feature-design-docs` + warriors + katas já atualizados

## Riscos

- en/es de cries precisam de tradução consistente — usar versões pt-BR como fonte de verdade
- cry-feature-design tem mais referências (paths.domain + paths.oas + paths.events) — verificar todas
```

---

## 4. Estados do ciclo de vida

| Status | Quando usar | Quem atualiza |
|---|---|---|
| `pending` | Plano criado, aguarda confirmação do usuário ou início | Agente ao criar |
| `in-progress` | Execução iniciada | Agente ao começar a primeira etapa |
| `done` | Todas as etapas marcadas com `[x]` | Agente ao concluir |
| `abandoned` | Tarefa cancelada antes de concluir | Agente com nota de motivo |
| `archived` | PR mergeado, plano não precisa mais de atenção ativa | Agente após merge |

---

## 5. Quando um plano é obrigatório (e quando não é)

### Obrigatório

- Tarefa com 2+ etapas encadeadas
- Qualquer operação que toque 2+ arquivos
- Toda invocação de warrior ou cry (por definição multi-etapa)
- Qualquer tarefa que produza artefatos permanentes (arquivos, commits, PRs, posts)

### Não obrigatório (etapa única trivial)

- Editar um único arquivo com instrução direta e precisa
- Ler/consultar arquivos sem escrita
- Executar um único comando isolado sem efeito colateral permanente
- Responder uma pergunta factual

### Zona cinzenta — usar plano por precaução

- Tarefa aparentemente simples que pode se ramificar (ex.: "corrigir o bug" sem saber o escopo)
- Operação irreversível mesmo que de etapa única (ex.: deletar arquivos)

---

## 6. Relação entre planos e outros artefatos

```
Issue GitHub
    └── Plan (plano da tarefa)
            ├── ADR (se decisão arquitetural relevante)
            └── Checkpoint (estado de sessão — .checkpoint)
```

- Um plano **referencia** uma issue, mas não a substitui
- Um plano pode **gerar** um ADR quando uma decisão de impacto é identificada durante a execução
- O **checkpoint** captura onde o agente parou na sessão; o plano captura o que o agente pretende fazer

---

## 7. Boas práticas

1. **Escrever o plano antes de saber tudo.** O objetivo é tornar a intenção visível, não produzir documentação perfeita. Um plano impreciso que evolui é melhor que nenhum plano.
2. **Manter etapas atômicas.** Cada etapa deve ser verificável: feita ou não feita. Evitar etapas vagas como "cuidar da parte de events".
3. **Atualizar em tempo real.** Marcar `[x]` à medida que cada etapa conclui, não ao final de tudo.
4. **Não criar planos fantasmas.** Se a tarefa for cancelada antes de começar, marcar `abandoned` com motivo — não deletar o arquivo.
5. **Commitar o plano.** O plano é parte do trabalho; deve ir no mesmo PR que os artefatos que descreve.

---

## Referências

- `lex-agent-planning` — Lei correspondente
- `kata-plan-task` — Procedimento operacional para criar e manter planos
- `lex-checkpoint` — Rastreamento de estado de sessão
- `lex-issue-driven` — Fluxo Issue-Driven do Athena
