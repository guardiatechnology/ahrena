# Kata: Planejar Tarefa

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação e manutenção de planos de tarefa por agentes, conforme `lex-agent-planning`

## Objetivo

Criar ou atualizar o documento de plano de uma tarefa antes de sua execução, garantindo que objetivo, escopo, etapas e dependências estejam documentados e confirmados pelo usuário antes de qualquer ação irreversível começar. Este é o procedimento que **`warrior-eunomia` executa em modo top-level** (per plan-044) e que o agente da sessão segue como fallback enquanto Eunomia não estiver disponível.

Per `lex-agent-planning` HARD-GATE, o plano só pode ser apresentado em `status: todo` quando os 5 passos canônicos forem concluídos: (1) Issue aberta per `lex-issue-quality`; (2) Issue Type verificado per `lex-issue-type-verified`; (3) branch remota criada via `gh issue develop` e linkada à Issue; (4) worktree criado per `lex-git-worktrees`; (5) front-matter do plano atualizado com `issue:`, `branch:`, `worktree:`.

## Quando Usar

- No início de qualquer tarefa multi-etapa
- Antes de invocar warriors, katas em sequência, ou cries
- Antes de modificar múltiplos arquivos em uma única sessão
- Quando o usuário pede "faça X" e X tem mais de uma etapa discernível

## Inputs

| Entrada | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Descrição da tarefa | Sim | O que o agente precisa fazer (pode ser vaga — o kata clarifica) |
| Issue de referência | Não | `owner/repo#N` quando a tarefa origina de uma issue GitHub |
| Agent dir | Não | Padrão resolvido automaticamente; pode ser sobrescrito por `paths.plans` em `.directives` |

## Fluxo de Trabalho

```
Progresso:
- [ ] 1. Resolver path e nome do arquivo de plano
- [ ] 2. Verificar planos existentes
- [ ] 3. Rascunhar o plano
- [ ] 4. Apresentar ao usuário e confirmar
- [ ] 5. Gravar o arquivo de plano
- [ ] 6. Executar a tarefa atualizando o plano
- [ ] 7. Finalizar o plano
```

### Passo 1: Resolver path e nome do arquivo de plano

1. Ler `.ahrena/.directives` e verificar se `paths.plans` está definido
2. Se sim → usar esse valor como diretório base
3. Se não → usar padrão por agente:
   - Claude Code → `.claude/plans/`
   - Cursor → `.cursor/plans/`
   - Desconhecido → `.plans/`
4. Listar arquivos existentes no diretório (se existir) para determinar o próximo número sequencial
5. Compor o nome: `plan-{NNN}-{slug}.md` onde `{slug}` é o resumo da tarefa em kebab-case (máx. 60 chars)

### Passo 2: Verificar planos existentes

1. Se o diretório de planos não existir → criará no Passo 5
2. Se existir → listar planos com status `in-progress` ou `pending`:
   - Se houver plano `in-progress` para a mesma tarefa → perguntar ao usuário se quer retomar ou criar novo
   - Se retomar → carregar o plano existente e pular para o Passo 6

### Passo 3: Rascunhar o plano

Com base na descrição da tarefa:

1. Identificar o **objetivo** (por que esta tarefa existe — máx. 3 frases)
2. Listar todos os arquivos ou sistemas que serão afetados (**escopo**)
3. Decompor a tarefa em **etapas atômicas** e verificáveis (cada etapa = uma ação concluível)
4. Identificar **dependências** (outros planos, issues, decisões pendentes)
5. Listar **riscos** conhecidos (o que pode dar errado; se nenhum, escrever "Nenhum identificado")

### Passo 4: Apresentar ao usuário e confirmar

Apresentar o rascunho do plano com a pergunta:

> "Este é o plano para a tarefa. Quer ajustar alguma coisa antes de eu começar?"

Aguardar resposta. Incorporar ajustes se solicitado. **Não iniciar execução antes da confirmação.**

### Passo 5: Gravar o arquivo de plano

1. Criar o diretório se não existir
2. Gravar o arquivo com front-matter completo (`status: pending`) e o corpo do plano
3. Confirmar ao usuário: "Plano salvo em `{path}`. Iniciando execução."
4. Atualizar `status` para `in-progress` e `updated_at`

### Passo 6: Executar a tarefa atualizando o plano

Durante a execução:
- Marcar cada etapa com `[x]` ao concluí-la
- Atualizar `updated_at` a cada mudança de etapa
- Se uma nova etapa for descoberta durante a execução → adicioná-la ao plano antes de executá-la
- Se um bloqueio surgir → registrar no plano como nota e comunicar ao usuário

### Passo 7: Finalizar o plano

Quando todas as etapas estiverem `[x]`:
1. Atualizar `status` para `done`
2. Atualizar `updated_at`
3. Informar ao usuário: "Tarefa concluída. Plano em `{path}` marcado como `done`."
4. Lembrar ao usuário que o plano deve ser commitado junto com os artefatos produzidos
5. (Opcional) Sugerir invocar `cry-checkpoint` para atualizar `Active plans` no `.checkpoint` removendo este plano da lista, caso ele estivesse listado lá

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Arquivo de plano | Markdown com front-matter YAML | `{plans_dir}/plan-{NNN}-{slug}.md` |

## Exemplo de Execução

### Input

```
Tarefa: concluir migração de cries para lex-feature-design-docs
Issue: guardiafinance/ahrena#42
```

### Passo 1 — Path resolvido

```
Agente: Claude Code
Diretório: .claude/plans/
Próximo número: 001 (diretório vazio)
Arquivo: .claude/plans/plan-001-complete-feature-design-docs.md
```

### Passo 3 — Rascunho

```markdown
## Objetivo
Concluir a atualização dos Cries e katas que ainda referenciam paths.oas/paths.events/paths.domain
após a criação de lex-feature-design-docs. Os warriors e katas principais já foram atualizados;
faltam os entry points (Cries) e 2 katas com referências residuais.

## Escopo
- cry-api-design.md, cry-event-storm.md, cry-feature-design.md, cry-full-design.md (pt-BR, en, es)
- kata-api-design-review.md (pt-BR, en, es)
- kata-api-design-doc.md — corrigir referências a .directives (pt-BR, en, es)
- .cursor/commands/ correspondentes

## Etapas
- [ ] 1. Abrir issue GitHub para rastrear o trabalho
- [ ] 2. Criar branch feat/{N}-complete-feature-design-docs
- [ ] 3-6. Atualizar 4 cries (× 3 línguas)
- [ ] 7. Atualizar kata-api-design-review (× 3 línguas)
- [ ] 8. Corrigir kata-api-design-doc (× 3 línguas)
- [ ] 9. Atualizar .cursor/commands/ afetados
- [ ] 10. Commitar tudo (novos artefatos + cries + katas)
- [ ] 11. Abrir PR
```

### Passo 4 — Confirmação

```
Agente: "Este é o plano para completar a migração de feature-design-docs.
  Total: ~18 arquivos. Quer ajustar alguma coisa antes de eu começar?"
```

## Restrições

- **Nunca iniciar execução sem confirmação do usuário** no Passo 4
- **Nunca criar plano vazio** — se a descrição for insuficiente para decompor etapas, fazer perguntas de clarificação antes
- **Nunca deletar um plano** — planos cancelados viram `abandoned`, não são removidos
- **Nunca omitir o front-matter** — `plan_id`, `title`, `status`, `agent`, `created_at`, `updated_at` são obrigatórios; `issue` quando aplicável

## Referências

- `lex-agent-planning` — Lei
- `codex-agent-planning` — Manual com template completo e boas práticas
- `lex-checkpoint` — Scratchpad de **sessão** (delimitação clara: plano = task; checkpoint = sessão)
- `cry-checkpoint` — Atalho para registrar plan-id em `Active plans` quando múltiplos planos coexistem na sessão
- `lex-directives` — Leitura de `.ahrena/.directives`
