# Lexis: Tags de Sessão

> **Prefixo:** `lex-` | **Tipo:** Lei Inviolável | **Escopo:** Tags semânticas anexadas a cada sessão Claude Code, expostas ao humano no statusline, no sidebar da extensão VSCode e no digest de planos do Eunomia

## Lei

> **Toda sessão Claude Code que adere a `session_tracking.tags.enabled` DEVE carregar no máximo 3 tags no seu arquivo de heartbeat: exatamente um `kind` (1ª slot, retirado do vocabulário controlado em `session_tracking.tags.kinds`) e 0–2 `topics` (livres, em letra minúscula, kebab-case, ≤ 20 caracteres cada). As tags DEVEM viver no objeto `tags` de `.ahrena/workflow/sessions/<session-id>.json` conforme `codex-session-tracking` §9. Inventar um `kind` fora do vocabulário configurado, exceder 3 slots, ou persistir tags em qualquer outro local que não o heartbeat JSON é PROIBIDO.**

## Cobertura

- **Aplica-se a:** toda sessão Claude Code rodando em um repositório com `session_tracking.enabled: true` e `session_tracking.tags.enabled: true` em `.ahrena/.directives`.
- **Agentes vinculados:** todo agente que escreve um heartbeat (`kata-session-heartbeat`), sugere tags (`kata-session-tag-suggest`) ou aceita override do usuário (`cry-tags`). Os consumidores de superfície (script do statusline, extensão ahrena-vscode, digest do Eunomia) leem, mas não escrevem.
- **Exceções:** sessões rodando fora do Claude Code (sem `CLAUDE_CODE_SESSION_ID`) pulam as tags silenciosamente junto com o heartbeat. Sessões em repositórios sem o bloco `tags` em `.directives` mantêm heartbeats sem `tags` — compatível com versões anteriores.

## Regras

### 1. Modelo de slots

O objeto `tags` tem exatamente duas chaves:

```json
"tags": {
  "kind": "tech-task",
  "topics": ["reconciliation", "api"]
}
```

- `kind` (slot 1): string única, obrigatória quando `tags` está presente, retirada de `session_tracking.tags.kinds` em `.directives`.
- `topics` (slots 2–3): array de 0 a 2 strings, livres, recomendado em letra minúscula kebab-case, cada uma ≤ 20 caracteres.

Arrays planos (`"tags": ["tech-task", "reconciliation", "api"]`), estruturas aninhadas, ou chaves extras são PROIBIDAS.

### 2. Vocabulário controlado para `kind`

`kind` DEVE corresponder exatamente a um dos valores em `session_tracking.tags.kinds`. O vocabulário padrão cobre as intenções comuns do fluxo Issue-Driven: `tech-task`, `bug`, `spike`, `user-story`, `epic`, `chore`, `design`, `review`, `exploration`, `release`.

Um projeto PODE estender a lista no seu próprio `.ahrena/.directives`, mas adições passam por PR para manter o vocabulário pequeno e agregável no digest do Eunomia.

### 3. `topics` livres

`topics` não são validados contra nenhuma lista. Forma recomendada: letra minúscula, kebab-case (`reconciliation-engine`, `pix-integration`). O agente DEVERIA avisar quando um topic está em maiúscula, contém espaços, ou ultrapassa 20 caracteres, mas NÃO DEVE rejeitar — a correção fica com o usuário via `cry-tags set`.

### 4. Heartbeat como única fonte da verdade

Tags DEVEM ser persistidas apenas no heartbeat JSON em `.ahrena/workflow/sessions/<session-id>.json`. Duplicar tags no front-matter do plan, no corpo da Issue, no corpo do PR, em mensagens de commit, ou em qualquer outro local é PROIBIDO — cada leitor (statusline, extensão, digest) lê o heartbeat diretamente. A seção "Session Trace" do PR (construída por `kata-pr-prepare`) PODE incluir tags como informação derivada dos heartbeats que agrega, mas o heartbeat continua sendo o canônico.

### 5. Sugestão automática é silenciosa com nota de visibilidade

Quando `session_tracking.tags.auto_suggest: true` e o heartbeat da sessão atual não tem objeto `tags`, o agente invoca `kata-session-tag-suggest` no primeiro turno do usuário, escreve as tags inferidas via `kata-session-heartbeat`, e emite uma nota de visibilidade de uma linha na mesma resposta (formato: `tagged: [kind] [topic1] [topic2]`). O usuário mantém controle total via `/cry-tags set`, `/cry-tags clear` ou `/cry-tags --auto-suggest` para inferir novamente.

Re-executar a auto-sugestão quando `tags` já está presente é PROIBIDO — as tags têm escopo de sessão e apenas o usuário as limpa.

### 6. Compatibilidade com versões anteriores

Heartbeats escritos antes das tags existirem (sem chave `tags`) permanecem válidos. Cada leitor DEVE tratar o campo `tags` como opcional e renderizar graciosamente quando ausente (ex.: o statusline mostra `main ahrena` sem chip; a linha do digest omite a coluna de tags para essa sessão).

```
<HARD-GATE>
Todo agente NÃO DEVE escrever um heartbeat de sessão contendo `tags`
sem satisfazer TODAS as precondições:

  (a) `session_tracking.tags.enabled: true` em `.ahrena/.directives`
  (b) `tags.kind` é uma string retirada de `session_tracking.tags.kinds`
  (c) `tags.topics` é um array de 0 a 2 strings
  (d) Total de slots usados ≤ 3 (1 kind + até 2 topics)
  (e) O formato é o objeto `{kind, topics: [...]}` —
      arrays planos ou chaves extras são rejeitados
  (f) O destino é `.ahrena/workflow/sessions/<id>.json`
      (sem duplicação no front-matter do plan, no corpo da
      Issue/PR, ou em mensagens de commit)

Esta regra aplica-se a TODA sessão Claude Code, independentemente de:
  - tamanho percebido ("é só uma tag")
  - urgência ("o usuário quer ver agora")
  - confiança do time ("já validamos o kind")
  - confiança da inferência ("tenho certeza de que é um bug")

Exceção declarada única: sessões rodando fora do Claude Code
(sem `CLAUDE_CODE_SESSION_ID`) pulam o heartbeat e as tags
silenciosamente, sem erro e sem persistência fallback.
</HARD-GATE>
```

## Exemplos

### Correto

```json
{
  "session_id": "85846253-4edf-443d-b294-187ef287d1bb",
  "plan_id": "321",
  "branch": "feat/321-session-tags-foundation",
  "tags": {
    "kind": "tech-task",
    "topics": ["session-tracking", "framework"]
  },
  "last_heartbeat": "2026-05-28T04:10:00Z"
}
```

```
Usuário: /cry-tags set bug reconciliation api
Agente: tags atualizadas → [bug] [reconciliation] [api]
```

### Incorreto

```json
"tags": ["tech-task", "reconciliation", "api"]
```
Array plano — viola a regra 1.

```json
"tags": {"kind": "documentation", "topics": []}
```
`documentation` não está na lista padrão de `kinds`; ou adicione ao `.directives` do projeto (via PR) ou escolha do vocabulário controlado.

```json
"tags": {"kind": "tech-task", "topics": ["a","b","c"]}
```
Três topics — excede o limite de 2 slots. Total seria 4 (1 kind + 3 topics).

## Validação Automatizada

- **Ferramenta:** validador de JSON schema na escrita do heartbeat (`kata-session-heartbeat`); `cry-tags` rejeita `kind` fora do vocabulário com erro de uma linha listando o vocabulário configurado; o digest do Eunomia lê `tags` de forma defensiva e ignora entradas malformadas.
- **Quando:** toda escrita de heartbeat; toda invocação de `/cry-tags set`; tick do loop PM do Eunomia.
- **Métrica:** 0 heartbeats com `tags.kind` fora de `session_tracking.tags.kinds`; 0 heartbeats com mais de 3 slots de tags; 0 tags persistidas fora do heartbeat JSON.
