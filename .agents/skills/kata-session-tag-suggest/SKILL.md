---
name: kata-session-tag-suggest
description: "Sugerir Tags de Sessão a partir do Primeiro Prompt. Inferir um objeto tags válido (1 kind + até 2 topics) a partir do primeiro prompt do usuário e do contexto do plano ativo"
---

# Kata: Sugerir Tags de Sessão a partir do Primeiro Prompt

> **Prefixo:** `kata-` | **Tipo:** Habilidade Repetível | **Escopo:** Inferir um objeto `tags` válido (1 kind + até 2 topics) a partir do primeiro prompt do usuário e do contexto do plano ativo

## Entradas

| Entrada | Obrigatório | Descrição |
|---|:---:|---|
| `user_prompt` | Sim | Texto do primeiro prompt do usuário na sessão (cru, sem pré-processamento). |
| `plan_front_matter` | Não | Front-matter YAML do plano ativo (`.claude/plans/plan-{M}-{slug}.md` quando houver). Fornece slug + status como sinais adicionais de inferência. |
| `branch_name` | Não | Nome da branch atual (ex.: `feat/321-session-tags-foundation`). O prefixo do tipo (`feat`, `fix`, etc.) é um sinal forte para `kind`. |
| `kinds_vocabulary` | Sim | Lista de valores de `kind` permitidos, lida de `session_tracking.tags.kinds` em `.ahrena/.directives`. |

## Fluxo

```
Progresso:
- [ ] 1. Ler kinds_vocabulary de .ahrena/.directives
- [ ] 2. Derivar kind do prefixo da branch + verbos do prompt + slug do plano
- [ ] 3. Derivar topics dos substantivos do prompt + slug do plano + pistas de escopo
- [ ] 4. Validar contra lex-session-tags (kind no vocabulário, topics ≤ 2)
- [ ] 5. Emitir o objeto {kind, topics} como saída estruturada
```

### Etapa 1 — Ler vocabulário

```bash
KINDS=$(yq '.session_tracking.tags.kinds' .ahrena/.directives)
```

Se `session_tracking.tags.kinds` está ausente ou vazio, sai com código 1 — a sugestão não pode ser feita sem um vocabulário.

### Etapa 2 — Derivar `kind`

O agente escolhe um valor de `kinds_vocabulary` usando esta escada de sinais (primeira correspondência vence):

| Sinal | Mapeia para `kind` |
|---|---|
| Prefixo `feat/` + prompt menciona uma nova capacidade | `user-story` (quando a Issue parent é uma User Story) ou `tech-task` (quando é uma Tech Task) |
| Prefixo `fix/` + prompt menciona bug, erro, regressão | `bug` |
| Prefixo `chore/`, `ci/`, `build/`, `docs/`, `style/`, `refactor/` | `chore` |
| Prompt menciona "design", "wireframe", "mockup", "API design" | `design` |
| Prompt menciona "review", "audit", "check", "approve" + ref a PR/Issue | `review` |
| Prompt menciona "explore", "investigate", "spike", "PoC", "research" | `spike` (ou `exploration` quando não há entregável time-boxed) |
| Prompt menciona "release", "tag", "publish", "version bump" | `release` |
| Prompt é uma pergunta ou ponta aberta | `exploration` |
| Nenhum sinal dispara | `tech-task` (padrão seguro para o framework) |

Quando múltiplos sinais disparam, o **prefixo da branch** vence — ele reflete o escopo commitado, não a conversa.

### Etapa 3 — Derivar `topics`

Escolher até 2 topics nesta ordem de preferência:

1. **Slug do plano** sem o número inicial: `321-session-tags-foundation` → `session-tags-foundation` → `session-tags` (mantido) + `foundation` (mantido).
2. **Substantivo de domínio** do prompt: identifica o substantivo de domínio mais concreto (ex.: "reconciliation", "pix", "fiscal", "auth"). Letra minúscula, kebab-case.
3. **Repo/componente** de `cwd` quando o prompt é genérico.

Truncar para ≤ 20 caracteres cada. Pular topics muito genéricos (`feature`, `code`, `system`, `change`).

### Etapa 4 — Validar

Aplicar as verificações de precondição do HARD-GATE de `lex-session-tags`:

- `kind` ∈ `kinds_vocabulary`
- `topics` é um array de 0 a 2 strings
- Total ≤ 3 slots
- Formato de objeto `{kind, topics: [...]}` (sem array plano, sem chaves extras)

Quando a validação falha, recorrer a `{"kind": "tech-task", "topics": []}` e emitir um aviso no stderr — a escrita do heartbeat é não-bloqueante.

### Etapa 5 — Emitir saída estruturada

Imprimir uma única linha JSON no stdout:

```json
{"kind":"tech-task","topics":["session-tags","foundation"]}
```

O chamador encaminha isso diretamente para `kata-session-heartbeat --set-tags` ou renderiza a nota de visibilidade `tagged: [tech-task] [session-tags] [foundation]` na resposta do agente.

## Saídas

| Saída | Formato | Destino |
|---|---|---|
| Sugestão de tags | Linha JSON única | stdout |
| Aviso (quando há fallback) | Texto de uma linha | stderr |

## Restrições

- **Sem persistência.** A kata nunca toca no arquivo de heartbeat. Escrever é trabalho do chamador.
- **Sem prompt interativo.** A inferência é silenciosa; a confirmação do usuário vive na nota de visibilidade + `cry-tags set`.
- **Sem re-sugestão em um heartbeat com tags existentes.** O chamador DEVE verificar `tags == null` antes de invocar; caso contrário esta kata é um no-op (código de saída 0, stdout vazio).
- **Sem invenção de `kind`.** Recorrer a um valor padrão é aceitável; inventar um novo valor de vocabulário não é.
