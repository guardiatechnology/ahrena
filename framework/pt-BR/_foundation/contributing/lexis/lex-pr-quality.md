# Lexis: Requisitos de Qualidade do Pull Request

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrantável | **Escopo:** Todos os Pull Requests em repositórios Guardia

## Lei

> **Todo PR em um repositório Guardia DEVE: (1) espelhar todas as labels da issue associada; (2) ter exatamente uma label de tamanho (`size/XS` a `size/XXL`), aplicada automaticamente pelo GitHub Actions ou manualmente quando a automação ainda não estiver configurada; (3) aplicar labels específicos de PR quando aplicável (`breaking change 💥`, `security 🛡️`, `release ↗️`); (4) ser atribuído ao autor com `--assignee @me`; (5) ter reviewers solicitados a partir do `.github/CODEOWNERS` do repositório — automaticamente pelo GitHub quando a auto-request estiver habilitada, ou manualmente via `gh pr edit --add-reviewer` antes do merge; (6) quando o PR recebe comentários de review (humanos ou bots — Gemini, Argos, claude[bot], CodeRabbit, etc.) e fixes são aplicados, CADA comentário endereçado DEVE receber uma reply individual no thread original contendo o SHA do commit de fix + uma linha de justificativa, antes de re-pedir review ou marcar como pronto para merge. O repositório DEVE ter um arquivo `.github/CODEOWNERS` com pelo menos um owner default (`* @{team}`). PRs que não atendam a esses requisitos NÃO DEVEM receber merge.**

## Cobertura

- **Aplica-se a:** todos os Pull Requests em todos os repositórios Guardia.
- **Agentes vinculados:** desenvolvedores, agentes de IA (warrior-athena, warrior-apollo, warrior-hephaestus) que criam ou revisam PRs.
- **Exceções:** PRs automáticos do Dependabot e ferramentas de varredura de segurança, que seguem seu próprio fluxo. Toda outra exceção exige justificativa explícita no PR.

## Regras

### 1. Espelhamento de labels da issue

Ao criar um PR, o agente DEVE:

1. Obter todas as labels da issue associada.
2. Aplicar as mesmas labels ao PR.
3. Adicionar labels específicos de PR quando aplicável (ver Regra 3).

```bash
# Obter labels da issue associada
LABELS=$(gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO --json labels --jq '[.labels[].name] | join(",")')

# Espelhar no PR
gh pr edit $PR_NUMBER --repo $OWNER/$REPO --add-label "$LABELS"
```

### 2. Label de tamanho obrigatória

Todo PR DEVE ter exatamente uma label de tamanho (`size/XS`, `size/S`, `size/M`, `size/L`, `size/XL` ou `size/XXL`):

- **Quando o GitHub Actions está configurado:** a label é aplicada automaticamente ao criar ou atualizar o PR. Não aplicar manualmente.
- **Quando o GitHub Actions não está configurado ou ainda não executou:** o agente DEVE calcular o tamanho manualmente e aplicar a label antes de abrir o PR para revisão.

**Cálculo manual do tamanho:**

```bash
# Contar linhas alteradas em relação à branch base (ignorando arquivos gerados)
git diff main...HEAD --stat | tail -1
```

| Label | Linhas alteradas |
|-------|:----------------:|
| `size/XS` | 0–9 |
| `size/S` | 10–29 |
| `size/M` | 30–99 |
| `size/L` | 100–499 |
| `size/XL` | 500–999 |
| `size/XXL` | 1.000+ |

### 3. Labels específicos de PR

Aplicar adicionalmente quando aplicável:

| Label | Quando aplicar |
|-------|----------------|
| `breaking change 💥` | PR introduz mudança incompatível de API; requer incremento de versão major |
| `security 🛡️` | PR resolve uma vulnerabilidade de segurança |
| `release ↗️` | PR de release — somente mantenedores |

### 4. Atribuição ao autor

Todo PR DEVE ser atribuído ao autor:

```bash
gh pr create ... --assignee "@me"
# ou após a criação:
gh pr edit $PR_NUMBER --add-assignee "@me"
```

### 5. Reviewers via CODEOWNERS

Todo PR DEVE ter reviewers solicitados a partir do `.github/CODEOWNERS` do repositório:

1. **Pré-condição (configuração do repo):** o repositório DEVE ter `.github/CODEOWNERS` com pelo menos um owner default (`* @org/team`) e a configuração de Branch Protection com auto-request de review dos code owners habilitada.
2. **Quando a auto-request está habilitada:** o GitHub solicita automaticamente os reviewers do CODEOWNERS ao criar o PR. O agente DEVE verificar (`gh pr view $PR --json reviewRequests`) que pelo menos um reviewer foi solicitado.
3. **Quando não há reviewers solicitados após a criação:** o agente DEVE aplicar manualmente antes de marcar o PR como pronto:

```bash
# Verificar reviewers atuais
gh pr view $PR_NUMBER --json reviewRequests --jq '[.reviewRequests[].login]'

# Solicitar manualmente o team default do CODEOWNERS
gh pr edit $PR_NUMBER --add-reviewer "org/team"
```

PRs sem nenhum reviewer solicitado (após criação e fallback manual) NÃO DEVEM receber merge.

### 6. Pré-requisitos antes de criar o PR

O agente DEVE verificar, nesta ordem, antes de executar `gh pr create`:

1. Issue associada existe e está em conformidade com `lex-issue-quality`.
2. Branch segue o formato definido em `lex-git-branches`.
3. PR body inclui `Closes #N` ou `Refs #N` conforme `lex-issue-first`.
4. Repositório tem `.github/CODEOWNERS` configurado.

E verificar, **imediatamente após** `gh pr create`:

5. Labels da issue foram espelhadas.
6. Label de tamanho foi aplicada (manualmente se necessário).
7. Pelo menos um reviewer foi solicitado (auto via CODEOWNERS ou manual via `--add-reviewer`).
8. Label `status: <name>` aplicada (`status: to review` por padrão ao abrir o PR; per `lex-issue-status`).
9. Seção **"Session Trace"** presente no body do PR quando `session_tracking.enabled == true` em `.ahrena/.directives` e o branch tem heartbeat files associados (per `codex-session-tracking` §7). Construída por `kata-pr-prepare` agregando `.ahrena/workflow/sessions/*.json` filtrados pelo branch corrente. Em PRs dirigidos exclusivamente por humano (sem agente Claude Code), a seção pode ser `_(human-driven; no session trace)_`.

### 7. Resposta por thread a comentários de review endereçados

Quando o PR recebe comentários de review (humanos ou bots — `gemini-code-assist`, `warrior-argos`, `claude[bot]`, `coderabbitai`, etc.) e o autor (ou agente em seu nome) aplica fixes, CADA comentário endereçado pelo commit DEVE receber uma reply individual no thread original. Um único comentário top-level resumindo "apliquei N fixes" NÃO basta — bots de auto-resolve dependem da reply no thread para marcar como resolvido, e o reviewer humano precisa de fechamento por thread em PRs com mais de 5 comentários.

**Formato canônico da reply:**

```
Addressed in {SHA-curto}: {1-linha de justificativa explicando o que mudou e por quê}
```

**Mecanismo (GitHub CLI):**

```bash
# Listar PR review comments (resumo do review + comentários por linha de código)
gh api "repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments" --jq '.[] | {id, user: .user.login, body: .body, path, line}'

# Postar reply no thread original
gh api "repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments/$COMMENT_ID/replies" \
  -f body="Addressed in ${SHA}: ${RATIONALE}"
```

> **Escopo da Regra 7:** aplica-se a **PR review comments** — os retornados por `/pulls/{N}/comments` (resumo de review + comentários por linha de código). **Issue comments na aba *Conversation* do PR** (retornados por `/issues/{N}/comments`) NÃO são threaded e não têm endpoint `/replies`; ficam fora do escopo da Regra 7. Se um reviewer registra observações na aba Conversation, o autor responde com um issue comment livre (quote-and-reply) — não há requisito de fechamento per-thread porque o thread não existe.

**Quando consolidar em comment top-level (admitido em conjunto, não substituto):**

- Um comment top-level resumindo o batch (commit + lista de fixes) é permitido para dar contexto agregado ao reviewer.
- Mas cada thread endereçado AINDA precisa da sua reply individual. Top-level não substitui per-thread.

**Comentários não endereçados (rejeitados, deferidos):** também recebem reply, indicando o motivo:

- `Deferred to #{issue-number} — out of scope for this PR.`
- `Disagreed — keeping as is because {rationale}. Happy to discuss.`
- `Not applicable — {explanation}.`

A regra é "cada thread tem closure", não "concordo com cada comentário".

**Quando a regra se ativa:** sempre que o agente (ou autor humano) faz push de commits de fix em resposta a uma rodada de review. PR sem comentários de review ainda recebidos NÃO está sujeito à Regra 7 — ela se torna obrigatória a partir do primeiro comment endereçado.

> **Quem decide o que é "endereçado":** o autor do PR. A reply per-thread declara *a intenção do autor de ter endereçado aquele comment*. O reviewer mantém o poder de reabrir o thread se discordar — `Re-opening: the fix doesn't address {detail}` é resposta válida e a Regra 7 volta a se ativar até o próximo fechamento. Comments rejeitados/deferidos/não-aplicáveis também são "endereçados" no sentido da Regra (recebem reply explicando o motivo). O critério não é "concordância", é "fechamento documentado".

### 8. Varredura multi-reviewer antes de declarar fix round completa

A Regra 7 governa o **comportamento de resposta** depois que um commit endereça comentários. Esta Regra 8 governa a **varredura prévia**: antes de declarar uma fix round completa, pedir re-revisão ou marcar a PR como pronta para merge, o autor (ou agente em seu nome) DEVE listar e processar comments de **todos** os reviewers ativos no PR — Argos, bots terceiros (`gemini-code-assist`, `coderabbitai`, `Copilot`, `qodo-merge-pro`) e humanos — **não somente Argos**.

**Por que existe:** Argos é o revisor multi-eixo nativo da Ahrena; bots terceiros capturam padrões complementares (estilo idiomático, performance, segurança, sugestões de refatoração). Tratar Argos como "o" revisor e ignorar comments de bots terceiros produz PRs que recebem `Argos APPROVED` mas chegam ao merge com threads não-respondidos — gerando ruído para o reviewer humano e desperdiçando o sinal dos bots.

**Mecanismo de varredura:**

```bash
# Resumos de review por reviewer (Argos + bots terceiros + humanos)
gh pr view $PR_NUMBER --repo $OWNER/$REPO --json reviews \
  --jq '.reviews[] | {author: .author.login, state, submittedAt}'

# PR review comments (comments por linha de código) agregados por reviewer
gh api "repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments" \
  --jq 'group_by(.user.login) | map({reviewer: .[0].user.login, count: length})'

# Issue comments na aba Conversation (não-threaded)
gh api "repos/$OWNER/$REPO/issues/$PR_NUMBER/comments" \
  --jq '.[] | {user: .user.login, body: .body[:200]}'
```

**Auxílio do warrior-argos:** o body consolidado de review do Argos inclui uma subseção "Threads de outros reviewers — pendentes" (per `warrior-argos` Fase 3) listando comments abertos de bots terceiros e humanos. Isso é um **auxílio**, não um substituto — a varredura ainda DEVE ser executada pelo agente que aplica os fixes para capturar comments postados depois do review do Argos.

**Critério de "fix round completa":**

- Todos os BLOCKERs do Argos endereçados; **E**
- Todos os comments de bots terceiros avaliados (acatados com fix, declinados com razão, ou deferidos com Issue follow-up); **E**
- Todos os comments humanos avaliados; **E**
- Cada thread endereçado tem reply individual per Regra 7.

Declarar fix round completa, pedir re-revisão ou marcar a PR como pronta para merge enquanto algum thread (de qualquer reviewer) ainda estiver aberto sem closure documentado é PROIBIDO.

## HARD-GATE

Conforme [`lex-hard-gate-pattern`](framework/pt-BR/_foundation/quality/lexis/lex-hard-gate-pattern.md), o bloqueio textual desta Lex é canonicamente expresso como:

```
<HARD-GATE>
warrior-athena, warrior-apollo, warrior-hephaestus e qualquer outro
agente NÃO DEVE mergear PR sem que ele satisfaça TODOS os critérios:

  (a) Issue associada está em conformidade com lex-issue-quality
  (b) Branch segue formato {type}/{issue-number}-{slug} per lex-git-branches
  (c) PR body inclui Closes #N ou Refs #N per lex-issue-first
  (d) Labels da issue espelhadas no PR
  (e) Exatamente uma label de tamanho (size/XS a size/XXL) aplicada
  (f) Labels específicas de PR (breaking change, security, release)
      aplicadas quando aplicável
  (g) Assignee = autor do PR
  (h) Pelo menos um reviewer solicitado a partir de .github/CODEOWNERS
  (i) Label `status: <name>` aplicada per lex-issue-status (entrada
      em `status: to review` ao abrir o PR; espelha `status:` do plano)
  (j) Seção "Session Trace" presente no body quando
      session_tracking.enabled == true e o branch tem heartbeat files
      associados, per codex-session-tracking §7 (PRs human-driven
      podem usar a frase canônica de exceção)
  (k) Cada comentário de review endereçado por um commit de fix tem
      reply individual no thread original com SHA + 1-linha de
      justificativa, per Regra 7 (comentários não endereçados —
      rejeitados, deferidos — também recebem reply explicando o
      motivo). Top-level comment de resumo é permitido em conjunto,
      mas NÃO substitui a reply per-thread.
  (l) Antes de pedir re-revisão ou marcar PR como pronto para merge,
      o agente varreu comments de TODOS os reviewers ativos
      (Argos, bots terceiros — gemini-code-assist, coderabbitai,
      Copilot, qodo-merge-pro — e humanos), avaliou cada thread e
      endereçou ou declinou com closure documentado, per Regra 8.
      Endereçar apenas BLOCKERs do Argos e ignorar threads de bots
      terceiros é PROIBIDO.

Esta regra se aplica a TODO PR, independentemente de:
  - tamanho percebido ("é uma mudança trivial")
  - urgência ("incêndio em produção")
  - quem solicitou ("o CEO pediu")
  - confiança do time ("o reviewer já viu")

Exceção única declarada: PRs automáticos do Dependabot e ferramentas
de varredura de segurança seguem seu próprio fluxo. Toda outra
exceção exige justificativa explícita no PR.
</HARD-GATE>
```

### Aplicação a Stacked PRs

Em fluxos de **stacked Pull Requests** (`codex-stacked-prs`), cada camada da cadeia é um **PR real** no GitHub. O HARD-GATE acima é avaliado **por PR da stack**, não uma única vez para a cadeia inteira: cada camada precisa satisfazer **todos** os critérios (a)–(l) antes de ser mergeada. Os critérios em si não mudam; apenas o escopo de aplicação é por camada.

Implicações operacionais:

- **Labels da issue (d):** espelhadas em todos os PRs da stack.
- **Label de tamanho (e):** calculada pelo diff de **cada camada** contra sua base (não contra `main` da stack inteira).
- **Closes/Refs (c, via `lex-issue-first`):** camadas intermediárias usam `Refs #N`; a última usa `Closes #N`.
- **Reviewers de CODEOWNERS (h):** solicitados em cada PR; podem ser os mesmos quando os arquivos tocados se sobrepõem ao mesmo owner.

`kata-stacked-pr-create` automatiza o espelhamento em todas as camadas para reduzir esforço manual, mas não relaxa nenhum critério.

## Exemplos

### Correto

```bash
# Issue #42 com labels: documentation 📃, ci 🏗️
# Diff: 4.516 adições + 2.877 exclusões → size/XXL

gh pr create \
  --title "docs: create public documentation site with MkDocs" \
  --body "Closes #42" \
  --base main \
  --assignee "@me"

gh pr edit 42 --add-label "documentation 📃,ci 🏗️,size/XXL"
```

### Incorreto

```bash
# ❌ PR criado sem labels
gh pr create --title "docs: add site" --body "Closes #42"
# Faltam: labels espelhadas da issue, label de tamanho, assignee

# ❌ Label de tamanho não aplicada porque "o Actions vai fazer"
# Quando o Actions não está configurado, o agente DEVE aplicar manualmente
```

## Validação Automatizada

- **Ferramenta:** GitHub Actions PR size labeler (auto-aplica `size/*`); GitHub Branch Protection com `required_pull_request_reviews` exigindo aprovação de code owners; checklist de revisão verifica labels espelhadas, assignee e reviewers; `kata-contributing-pr` aplica todas as regras desta Lexis ao criar PRs.
- **Quando:** na criação e atualização do PR; no checklist de revisão; auditoria mensal do CODEOWNERS dos repositórios.
- **Métrica:** 0 PRs com merge sem label de tamanho; 0 PRs com merge sem espelhamento das labels da issue; 0 PRs sem assignee; 0 PRs com merge sem nenhum reviewer solicitado; 0 PRs com merge com comentários de review endereçados por commit mas sem reply per-thread; 0 PRs com merge com comments de bots terceiros (gemini-code-assist, coderabbitai, Copilot, qodo-merge-pro) sem closure documentado per Regra 8; 100% dos repositórios Guardia com `.github/CODEOWNERS` configurado.
