# Lexis: Planejamento Obrigatório para Tarefas de Agentes

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Toda tarefa multi-etapa iniciada por qualquer agente ou subagente (Claude, Cursor, IDEs, warriors, katas, cries)

## Propósito

Agentes que executam sem planejamento prévio produzem resultados parciais, deixam arquivos em estados inconsistentes e forçam o usuário a reconstruir contexto manualmente. Esta Lexis elimina esse padrão exigindo que todo agente documente seu plano antes de executar, tornando intenção, escopo e sequência auditáveis por humanos e por outros agentes.

## Lei

> **Todo agente DEVE criar um documento de plano em `./{agent_dir}/plans/plan-{NNN}-{slug}.md` (ou no path definido em `paths.plans` de `.ahrena/.directives`) ANTES de iniciar qualquer tarefa que envolva 2 ou mais etapas, afete múltiplos arquivos, ou produza artefatos permanentes. O plano DEVE ser apresentado ao usuário para confirmação antes da execução começar. Iniciar execução multi-etapa sem plano documentado e confirmado é PROIBIDO.**

## Abrangência

- **Aplica-se a:** Claude Code (CLI, VSCode, Desktop, claude.ai/code), Cursor, qualquer AI agent ou subagente que invoque katas, warriors ou cries no contexto Ahrena
- **Agentes vinculados:** todos, sem exceção de papel
- **Exceções permitidas:** operações triviais de etapa única (editar um único arquivo com instrução direta, consulta de leitura pura, comando isolado sem efeito colateral permanente)

## Resolução do path do plano (precedência)

| Prioridade | Fonte | Valor |
|:---:|---|---|
| 1 | `paths.plans` em `.ahrena/.directives` | Override de projeto — substitui todo o restante |
| 2 | Padrão por agente | `.claude/plans/` para Claude Code; `.cursor/plans/` para Cursor; `.plans/` para agente desconhecido |

Nome do arquivo: `plan-{NNN}-{slug}.md` onde `{NNN}` é sequencial por diretório (001, 002, …), sem lacunas.

## Estrutura mínima obrigatória do plano

```markdown
---
plan_id: "{NNN}"
title: "{slug}"
status: pending | in-progress | done | archived | abandoned
agent: claude | cursor | unknown
issue: "{owner/repo#N}"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
---

# Plano: {título legível}

## Objetivo
{Por que esta tarefa está sendo feita — 1 a 3 frases}

## Escopo
{O que será modificado: arquivos, sistemas, artefatos afetados}

## Etapas
- [ ] Etapa 1
- [ ] Etapa 2
...

## Dependências
{Planos ou issues de que esta tarefa depende; "Nenhuma" se não houver}

## Riscos
{Riscos conhecidos e mitigações; "Nenhum identificado" se não houver}
```

## Ciclo de vida do plano

```
pending → in-progress → done
                     ↘ abandoned
done → archived
```

- O agente DEVE atualizar `status` no front-matter ao iniciar (`in-progress`) e ao concluir (`done`)
- Etapas DEVEM ser marcadas com `[x]` conforme concluídas
- Planos `done` ou `abandoned` DEVEM ser movidos para `archived` após o PR correspondente ser mergeado
- Planos DEVEM ser commitados junto com o trabalho que descrevem (não são efêmeros como `.checkpoint`)

## Relação com outros artefatos

- **Issue GitHub:** um plano referencia uma issue; uma issue pode ter múltiplos planos (ex.: design, implementação, testes)
- **Checkpoint (`.checkpoint`):** o checkpoint rastreia estado de sessão; o plano rastreia intenção e progresso estruturado — são complementares, não excludentes
- **ADR:** quando um plano identifica uma decisão arquitetural relevante, um ADR DEVE ser aberto conforme `lex-issue-driven`

## Exemplos

### Correto

```
Tarefa: atualizar 4 cries e 2 katas para nova estrutura de paths
→ Agente cria .claude/plans/plan-001-complete-feature-design-docs.md
→ Apresenta ao usuário: objetivo, 12 arquivos a editar, sequência
→ Usuário confirma
→ Agente executa marcando etapas, atualiza status para done
→ Plano commitado junto com as edições
```

### Incorreto

```
Tarefa: atualizar 4 cries e 2 katas
→ Agente começa editando cry-api-design.md diretamente sem criar plano
→ ❌ Viola lex-agent-planning — execução multi-etapa sem plano documentado
```

## Validação Automatizada

- **Ferramenta:** verificação pelo agente antes de qualquer execução multi-etapa; `kata-plan-task` como ponto de entrada canônico
- **Momento:** antes de qualquer execução de tarefa multi-etapa — sem exceção
- **Métrica:** 0 tarefas multi-etapa executadas sem plano documentado em `{agent_dir}/plans/`

## Referências

- `codex-agent-planning` — manual com template completo, exemplos e boas práticas
- `kata-plan-task` — procedimento operacional para criar e manter planos
- `lex-checkpoint` — rastreamento de estado de sessão (complementar)
- `lex-issue-driven` — fluxo de desenvolvimento dirigido por issues
