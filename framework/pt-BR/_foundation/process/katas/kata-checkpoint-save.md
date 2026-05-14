# Kata: Salvar Checkpoint de Sessão

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Salvamento sob demanda + fim de sessão, conforme `lex-checkpoint`

## Objetivo

Coletar Session focus, Active plans, Open threads e Notes do contexto atual da sessão e gravar `.checkpoint` na raiz do workspace, respeitando o schema canônico (4 seções). Sobrescreve qualquer schema antigo silenciosamente.

## Quando Usar

- Quando o usuário invoca `cry-checkpoint` (gatilho explícito)
- Ao encerrar a sessão SE houve mudança de contexto (novo Session focus, novo Active plan, novo Open thread, novas Notes)
- Quando agente detecta que está prestes a fechar a janela e há contexto não persistido

NÃO usar:
- Após cada activity automática (a granularidade vive no plano)
- Para registrar conteúdo já presente no plano (duplicaria `lex-agent-planning`)
- Em sessões puramente operacionais sem threads paralelas (não há contexto a preservar fora do plano)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Session focus | Sim | 1-3 frases descrevendo o foco geral da janela de trabalho |
| Active plans | Não | Lista de `(plan-id, 1-line context)` dos planos ativos na sessão; pode estar vazia |
| Open threads | Não | Lista de threads paralelas pendentes; pode estar vazia |
| Notes | Não | Texto livre — links, lembretes, snippets; pode estar vazio |
| Workspace root | Sim | Diretório onde gravar `.checkpoint` (default: `pwd`) |

Pelo menos um entre Session focus, Active plans, Open threads ou Notes deve ter conteúdo. Checkpoint vazio não é gravado — `kata-checkpoint-save` retorna `nothing-to-save`.

## Workflow

```
Progresso:
- [ ] 1. Coletar contexto da sessão
- [ ] 2. Validar conteúdo (não duplicar plano)
- [ ] 3. Renderizar schema canônico
- [ ] 4. Gravar .checkpoint
- [ ] 5. Confirmar ao usuário
```

### Passo 1: Coletar contexto da sessão

1. Capturar **Session focus** do contexto ativo ou pedir ao usuário em 1-3 frases.
2. Listar **Active plans** — para cada plano em uso na sessão, gerar entrada `\`plan-{M}-{slug}\` — 1-line context ≤ 80 chars`. Inferir do contexto ou consultar `plan-*.md` ativos (status `in-progress`) no provider cache (`.claude/plans/` para Claude Code; `.cursor/plans/` para Cursor).
3. Coletar **Open threads** — perguntar ao usuário ou extrair do histórico recente da conversa decisões pendentes que não viraram plano.
4. Coletar **Notes** — texto livre adicional. Pode ser vazio.

### Passo 2: Validar conteúdo (não duplicar plano)

Antes de gravar, verificar:

- **Session focus** NÃO contém `## Steps`, `## Decisões fechadas`, `## Riscos` (esses vivem no plano)
- **Active plans** entries têm formato canônico (\`plan-{M}-{slug}\` — descrição) e ≤ 80 chars
- **Open threads** NÃO contém steps detalhados de uma task (se contém, mover para o plano correspondente antes de gravar)
- **Notes** NÃO contém artifacts produced (lista de arquivos modificados — `git diff` cobre)

Se validação detectar duplicação, apresentar ao usuário e oferecer:
- Mover conteúdo duplicado para o plano apropriado antes de gravar
- Ignorar e gravar como está (com warning explícito)

### Passo 3: Renderizar schema canônico

Montar conteúdo do arquivo:

```markdown
# Session checkpoint

- **Last update:** {YYYY-MM-DDTHH:MM:SSZ — UTC ISO 8601}
- **Session id:** {session_id ou commit short SHA do HEAD}

## Session focus

{conteúdo coletado no Passo 1}

## Active plans

{lista; se vazia, omitir bullets e deixar a seção com texto "Nenhum plano ativo registrado."}

## Open threads

{lista; se vazia, omitir bullets e deixar a seção com texto "Nenhuma thread aberta."}

## Notes

{texto livre; se vazio, omitir e deixar a seção com texto "—"}
```

Seções vazias são preservadas (cabeçalho mantido) com placeholder textual — schema é canônico, não opcional.

### Passo 4: Gravar `.checkpoint`

1. Caminho final: `{workspace_root}/.checkpoint`
2. Escrita atômica: gravar em `.checkpoint.tmp` e `mv` para `.checkpoint` (evita corromper em caso de interrupção)
3. Encoding UTF-8, line endings LF
4. Sobrescrita silenciosa de qualquer schema antigo presente
5. Validar `.gitignore` contém `.checkpoint` (per `lex-checkpoint` rule 4); se não, alertar usuário (mas gravar mesmo assim)

### Passo 5: Confirmar ao usuário

```
✅ Checkpoint salvo em `.checkpoint`:
   - Session focus: {primeira frase, max 100 chars}
   - Active plans: {N}
   - Open threads: {N}
   - Notes: {presente | vazio}
```

### Passo 6: Validação Final

- [ ] `.checkpoint` existe na raiz do workspace
- [ ] Primeira linha é `# Session checkpoint` (não `# Checkpoint`)
- [ ] As 4 seções (Session focus, Active plans, Open threads, Notes) estão presentes
- [ ] Não há seções proibidas (Activity, Status, Progress, Decisions made, Next steps, Artifacts produced)
- [ ] `.gitignore` cobre `.checkpoint`
- [ ] Confirmação foi mostrada ao usuário

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `.checkpoint` | Markdown UTF-8 com schema canônico | Raiz do workspace |
| Status (`saved`, `nothing-to-save`, `validation-warning`, `gitignore-missing`) | Enum interno | Contexto da sessão |
| Confirmação ao usuário | Texto markdown | Terminal/IDE |

## Exemplo de Execução

### Input

```
Session focus: "Reposicionando lex-checkpoint em paralelo com revisão de plan-026."
Active plans:
  - plan-026 (commit-readiness-observer; aguardando ajuste)
  - plan-040 (reposicionamento do .checkpoint; em redação)
Open threads:
  - Avaliar absorção de "Risks da sessão" em lex-agent-planning
  - Decidir clade dos Brand-related cries
Notes: "Link discussão kata-quality-gate: https://..."
Workspace: /Users/dev/workspace/guardia/tooling/ahrena
```

### Output (`.checkpoint`)

```markdown
# Session checkpoint

- **Last update:** 2026-05-10T01:55:00Z
- **Session id:** abc1234

## Session focus

Reposicionando lex-checkpoint em paralelo com revisão de plan-026.

## Active plans

- `plan-026` — commit-readiness-observer; aguardando ajuste
- `plan-040` — reposicionamento do `.checkpoint`; em redação

## Open threads

- Avaliar absorção de "Risks da sessão" em lex-agent-planning
- Decidir clade dos Brand-related cries

## Notes

Link discussão kata-quality-gate: https://...
```

### Confirmação

```
✅ Checkpoint salvo em `.checkpoint`:
   - Session focus: Reposicionando lex-checkpoint em paralelo com revisão de plan-026.
   - Active plans: 2
   - Open threads: 2
   - Notes: presente
```

## Restrições

- NÃO grava conteúdo que duplica plano (Activity, Steps, Artifacts produced)
- NÃO trata schema antigo — sobrescreve silenciosamente
- NÃO emite save vazio — checkpoint sem conteúdo retorna `nothing-to-save`
- NÃO grava se workspace é read-only ou se permissões impedem (alerta usuário)
- Escrita é atômica (tmp + mv) — interrupção mid-save não corrompe
- NÃO comita `.checkpoint` — fica gitignored per `lex-checkpoint` rule 4
