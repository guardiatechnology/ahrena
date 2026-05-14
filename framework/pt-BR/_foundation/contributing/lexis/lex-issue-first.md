# Lexis: Desenvolvimento Issue-First

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrantável | **Escopo:** Todas as mudanças de código em repositórios Guardia

## Lei

> **Toda mudança de código — feature, bugfix, refatoração, atualização de dependência ou mudança de configuração — DEVE originar-se de uma Issue do GitHub existente. Antes de abrir uma Issue nova, o contribuidor DEVE verificar se já existe uma Issue (aberta ou recém-fechada) cobrindo o tópico; a primeira Issue correspondente é dona do trabalho, e Issues paralelas para o mesmo escopo são PROIBIDAS. Nenhum branch PODE ser criado e nenhum PR PODE ser aberto sem uma Issue associada. O corpo do PR DEVE referenciar a Issue com `Closes #N` (resolve completamente) ou `Refs #N` (endereça parcialmente). PRs sem referência a uma Issue são PROIBIDOS. A única exceção é para correções triviais (erros de digitação, pontuação ou formatação sem nenhuma mudança de lógica), que PODEM ser submetidas sem uma Issue prévia usando o tipo `docs:` ou `style:` do Conventional Commits.**

## Cobertura

- **Aplica-se a:** todas as contribuições de código em todos os repositórios Guardia.
- **Agentes vinculados:** desenvolvedores, agentes de IA (warrior-athena, warrior-apollo, warrior-hephaestus).
- **Exceções:** correções triviais (apenas tipo `docs:` ou `style:`, sem mudança de lógica). Todas as outras exceções exigem justificativa explícita registrada na Issue.

## Regras

### 1. Issue antes do branch

Antes de criar um branch:

1. **Procure Issues existentes** (abertas e recém-fechadas) que já cubram o trabalho planejado — por título, label, escopo ou discussão relacionada. Use `gh issue list --search "<termos>"` ou a busca da UI do GitHub. A primeira Issue compatível é dona do trabalho.
2. **Se já existe Issue** para o tópico: use-a como anchor — referencie via `Closes #N` (resolução total) ou `Refs #N` (resolução parcial). Não abra Issue paralela cobrindo o mesmo escopo. Casos válidos para Issue nova mesmo com tópico relacionado: (a) o trabalho atual é genuinamente independente da Issue existente, (b) o escopo evoluiu e justifica desdobramento documentado nos comentários da Issue original.
3. **Se não existe Issue**: abra uma usando `kata-contributing-issue` com: **o quê** (descrição clara do objetivo), **por quê** (motivação e impacto), **resultado esperado** (critérios de aceitação ou definição de pronto).
4. Somente então crie o branch seguindo `lex-git-branches`: `{type}/{issue-number}-{slug}`.

### 2. Qualidade da Issue

Uma Issue DEVE conter no mínimo:

- Um título claro que resume o objetivo.
- Um corpo descrevendo o problema ou objetivo, contexto e resultado esperado.
- Um tipo atribuído via template em `.ahrena/contributing_templates/` (`feature-request`, `epic`, `user-story-for-api`, `user-story-for-frontend`, `tech-task`, `bug` ou `plan`).

### 3. PR referencia a Issue

Todo corpo de PR DEVE incluir um dos seguintes:

- `Closes #N` — o PR resolve completamente a Issue (GitHub a fecha automaticamente ao fazer merge).
- `Refs #N` — o PR endereça parcialmente a Issue (a Issue permanece aberta).

PRs sem referência a uma Issue são rejeitados durante a revisão.

**Plan sub-issues (`lex-agent-planning`):** um PR PODE usar `Closes #M` onde `#M` é uma Plan sub-issue sob uma Issue pai `#N`. O `Closes #M` fecha apenas a sub-issue Plan; a Issue pai `#N` fecha somente quando TODAS as suas Plans sub-issues atingem `status: done`. Quando o PR contribui parcialmente para a Plan ou contextualiza o trabalho na Issue pai, use `Refs #M` ou `Refs #N` respectivamente — nunca `Closes` em ambas simultaneamente.

### 4. Exceção: correções triviais

Mudanças limitadas exclusivamente a erros de digitação, pontuação ou formatação (sem mudança de comportamento ou lógica) PODEM ser submetidas diretamente como PR sem uma Issue prévia. Estas DEVEM usar o tipo `docs:` ou `style:` do Conventional Commits.

## Exemplos

### Corretos

```
# Issue #42 existe: "Adicionar autenticação OAuth2"
Branch: feat/42-oauth2-authentication
Corpo do PR inclui: "Closes #42"
```

```
# Issue #123 existe: "Null pointer no processamento de transações"
Branch: fix/123-null-pointer-in-transaction
Corpo do PR inclui: "Closes #123"
```

```
# Correção trivial — sem Issue necessária
Commit: docs: fix typo in CONTRIBUTING guide
```

### Incorretos

```
# ❌ Branch criado sem uma Issue
Branch: feat/new-payment-dashboard
# Não existe Issue correspondente

# ❌ Corpo do PR sem referência à Issue
Corpo do PR: "Este PR adiciona a nova funcionalidade de pagamento."
# Sem "Closes #N" ou "Refs #N"

# ❌ Mudança não trivial submetida sem uma Issue
Commit: refactor: restructure entire auth module
# Refatoração não é uma correção trivial
```

## Validação Automatizada

- **Ferramenta:** template de PR com campo obrigatório `Closes #` ou `Refs #`; verificação do GitHub Actions no corpo do PR para referência à Issue.
- **Quando:** na criação e atualização do PR.
- **Métrica:** 0 PRs com merge (excluindo exceções triviais) sem uma Issue associada.
