# Cry: Salvar Checkpoint de Sessão

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho do usuário para gravar `.checkpoint` sob demanda, conforme `lex-checkpoint`

## Descrição

Atalho do usuário que invoca `kata-checkpoint-save` para gravar o `.checkpoint` da sessão atual. Útil quando há contexto fora do plano (Open threads, Notes, hand-off entre múltiplos planos ativos) que vale preservar antes de pausar ou encerrar a janela.

Ler `.checkpoint` é responsabilidade automática do agente no início da sessão (via `kata-checkpoint-read`) — `cry-checkpoint` cobre apenas o gatilho de **escrita** sob demanda.

## Uso

```
/cry-checkpoint
```

Sem argumentos por padrão. O agente coleta contexto da sessão e grava.

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `--focus "<frase>"` | Não | Sobrescreve o Session focus inferido pelo agente | `--focus "Revisando plan-026"` |
| `--add-thread "<linha>"` | Não | Acrescenta uma Open thread ao checkpoint atual | `--add-thread "Avaliar X"` |
| `--note "<texto>"` | Não | Acrescenta texto às Notes | `--note "Link: https://..."` |
| `--dry-run` | Não | Mostra o conteúdo que seria gravado sem persistir | — |

Sem flags, o agente infere todos os campos do contexto da sessão.

## O que o Comando Faz

1. Invoca `kata-checkpoint-save`
2. O kata coleta Session focus, Active plans, Open threads e Notes do contexto da sessão
3. Valida que conteúdo não duplica plano
4. Grava `.checkpoint` na raiz do workspace com schema canônico
5. Apresenta confirmação ao usuário

## Prompt Template

```
Invocar kata-checkpoint-save com:

- Workspace root: {{pwd}}
- Session focus: {{--focus se fornecido, senão inferir do contexto da sessão}}
- Active plans: {{inferir dos planos com status: in-progress em .claude/plans/}}
- Open threads: {{coletar do contexto + adicionar --add-thread se fornecido}}
- Notes: {{coletar do contexto + acrescentar --note se fornecido}}
- Dry-run: {{--dry-run flag}}

Após gravação, apresentar confirmação ao usuário no formato:

✅ Checkpoint salvo em `.checkpoint`:
   - Session focus: {primeira frase, max 100 chars}
   - Active plans: {N}
   - Open threads: {N}
   - Notes: {presente | vazio}
```

## Exemplo de Invocação

**Input:**

```
/cry-checkpoint
```

**Output esperado:**

```
Coletando contexto da sessão...

Session focus: Reposicionando lex-checkpoint em paralelo com revisão de plan-026.
Active plans: plan-026, plan-040
Open threads:
  - Avaliar absorção de "Risks da sessão" em lex-agent-planning
  - Decidir clade dos Brand-related cries
Notes: Link discussão kata-quality-gate: https://...

✅ Checkpoint salvo em `.checkpoint`:
   - Session focus: Reposicionando lex-checkpoint em paralelo com revisão de plan-026.
   - Active plans: 2
   - Open threads: 2
   - Notes: presente
```

**Input com flags:**

```
/cry-checkpoint --add-thread "Validar com PM antes do PR" --note "Slack: #ahrena"
```

**Output:**

```
Acrescentando 1 thread e 1 note ao contexto.

✅ Checkpoint salvo em `.checkpoint`:
   - Session focus: {inferido}
   - Active plans: 2
   - Open threads: 3 (1 nova)
   - Notes: presente
```

## Restrições

- NÃO modifica planos (`.claude/plans/plan-*.md`) — `cry-checkpoint` cobre apenas `.checkpoint`
- NÃO grava conteúdo que duplica plano — kata-checkpoint-save valida e bloqueia
- Output respeita o tom Guardia (`lex-tone`, `lex-brand-voice`) — direto, sem buzzwords
- Não comita `.checkpoint` — segue gitignore per `lex-checkpoint` rule 4
- `--dry-run` mostra mas não grava

## Diferença de Kata

| Aspecto | `cry-checkpoint` | `kata-checkpoint-save` |
|---------|------------------|------------------------|
| **Natureza** | Atalho do usuário | Procedimento completo |
| **Invocação** | `/cry-checkpoint` (1 linha) | Chamado por `cry-checkpoint` ou por outros warriors |
| **Configura agente?** | Não | Sim — define gatilhos, validação, formato |
| **Output** | Gravação + confirmação | Gravação + status + confirmação |
