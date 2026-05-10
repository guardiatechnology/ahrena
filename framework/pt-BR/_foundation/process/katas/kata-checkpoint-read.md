# Kata: Ler Checkpoint de Sessão

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Início de sessão com agente IA, conforme `lex-checkpoint`

## Objetivo

Localizar `.checkpoint` na raiz do workspace, validar o schema, apresentar resumo ao usuário e perguntar se deseja retomar o contexto salvo. Quando o schema é antigo, emitir warning de deprecation e prosseguir como se não houvesse checkpoint.

## Quando Usar

- No início de cada sessão com agente IA, antes de qualquer outra atividade (gatilho automático per `lex-checkpoint` rule 1)
- Quando o usuário invoca explicitamente para revisar o contexto salvo
- Após `git pull` que possa ter trazido alterações no workspace (raro — `.checkpoint` é gitignored, mas paths configurados podem mudar)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Workspace root | Sim | Diretório onde procurar `.checkpoint` (default: `pwd` na inicialização da sessão) |
| Modo de apresentação | Não | `summary` (default — resumo curto) ou `full` (conteúdo completo do checkpoint) |

## Workflow

```
Progresso:
- [ ] 1. Localizar .checkpoint
- [ ] 2. Detectar schema (novo, antigo, ausente)
- [ ] 3. Apresentar ao usuário (resumo ou warning)
- [ ] 4. Capturar decisão (retomar, descartar, ignorar)
- [ ] 5. Aplicar decisão no contexto da sessão
```

### Passo 1: Localizar `.checkpoint`

1. Procurar `.checkpoint` na raiz do workspace (workspace = `pwd` ou diretório passado como input).
2. Se não existir: status `absent` → prosseguir para Passo 5 sem leitura.
3. Se existir: status `present` → prosseguir para Passo 2.

### Passo 2: Detectar schema

1. Ler primeira linha do arquivo:
   - `# Session checkpoint` → schema novo
   - `# Checkpoint` (sem "Session") → schema antigo
   - Outro conteúdo → schema desconhecido (tratar como antigo: warning + ignorar)
2. Para schema novo: validar presença de pelo menos `## Session focus` ou `## Active plans` ou `## Open threads` ou `## Notes`. Se nenhuma das 4 seções existir, downgrade para schema desconhecido.
3. Para schema antigo ou desconhecido: NÃO parsear conteúdo. Apenas registrar status para Passo 3.

### Passo 3: Apresentar ao usuário

**Caso schema novo:**

```
Encontrei um `.checkpoint` (schema atual):
  - Session focus: {primeira linha de Session focus, max 100 chars}
  - Active plans: {lista compacta de plan-IDs}
  - Open threads: {N itens}
  - Last update: {timestamp em formato relativo, ex: "há 2h"}

Deseja retomar este contexto ou iniciar uma nova janela?
```

Em modo `full`, apresentar o conteúdo completo das 4 seções.

**Caso schema antigo:**

```
⚠️  Encontrei um `.checkpoint` em schema antigo (pré-issue #73).
   O conteúdo será ignorado e sobrescrito na próxima invocação de
   `cry-checkpoint` ou ao encerrar a sessão.

   Para descartar agora: `rm .checkpoint`
   Para preservar como Notes: copie o conteúdo manualmente antes de salvar.

Prosseguindo como se não houvesse checkpoint.
```

NÃO oferecer opção de retomar — schema antigo não é parseável de forma segura.

**Caso ausente:**

Não emitir nada. Prosseguir silenciosamente. A ausência de `.checkpoint` é cenário válido (per `lex-checkpoint` rule 1.5).

### Passo 4: Capturar decisão (apenas para schema novo)

Aguardar resposta do usuário:

- **"retomar" / "yes" / "r"** → status `resume`; agente carrega contexto na memória da sessão e o disponibiliza para próximas decisões.
- **"nova" / "descartar" / "n"** → status `discard`; agente marca `.checkpoint` para sobrescrita na próxima invocação de save (não apaga ainda — usuário pode mudar de ideia).
- **"ignorar" / silêncio por timeout** → status `ignore`; agente prossegue sem aplicar contexto, mas NÃO marca para sobrescrita; checkpoint atual permanece intacto.

### Passo 5: Aplicar decisão

- `resume`: pôr Active plans, Open threads, Session focus no contexto ativo da sessão. Notes ficam disponíveis sob demanda mas não são automaticamente apresentadas.
- `discard`: limpar contexto da sessão, marcar `.checkpoint` para sobrescrita.
- `ignore`: prosseguir sem aplicar.
- `absent` / `schema antigo`: prosseguir sem aplicar.

### Passo 6: Validação Final

- [ ] Decisão do usuário foi capturada (ou inferida via timeout)
- [ ] Contexto da sessão reflete a decisão (resume = aplicado; outros = sem aplicação)
- [ ] Schema antigo emitiu warning visível ao usuário
- [ ] Checkpoint ausente NÃO emitiu warning (silencioso é correto)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Resumo do checkpoint apresentado ao usuário | Texto markdown | Terminal/IDE |
| Status da operação (`resume`, `discard`, `ignore`, `absent`, `deprecated_schema`) | Enum interno | Contexto da sessão |
| Contexto carregado (apenas se `resume`) | Estruturado (Session focus, Active plans, Open threads, Notes) | Memória da sessão |

## Exemplo de Execução

### Input

Workspace root: `/Users/dev/workspace/guardia/tooling/ahrena`
Modo: `summary` (default)

### Conteúdo de `.checkpoint`

```markdown
# Session checkpoint

- **Last update:** 2026-05-09T22:30:00Z
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

Link da discussão sobre kata-quality-gate: https://...
```

### Output

```
Encontrei um `.checkpoint` (schema atual):
  - Session focus: Reposicionando lex-checkpoint em paralelo com revisão de plan-026
  - Active plans: plan-026, plan-040
  - Open threads: 2 itens
  - Last update: há 2h

Deseja retomar este contexto ou iniciar uma nova janela?
```

## Restrições

- NÃO modifica `.checkpoint` em nenhum cenário (operação read-only)
- NÃO tenta parsear schema antigo — apenas detecta e emite warning
- NÃO falha se `.checkpoint` está ausente — ausência é cenário válido
- NÃO escreve em logs verbosos detalhes do conteúdo (Notes podem ter info sensível pessoal)
- Modo de apresentação respeita preferência declarada — não invadir o terminal com conteúdo completo se modo é `summary`
