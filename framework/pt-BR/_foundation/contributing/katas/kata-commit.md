# Kata: Fazer Commit Padronizado

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação de commits conformes com as Lexis da Guardia

## Objetivo

Este Kata define o procedimento padronizado para criar um commit que respeite todas as Lexis de commit da Guardia — formato Conventional Commits, atomicidade, assinatura GPG e idioma.

## Quando Usar

- Quando é necessário fazer commit de alterações seguindo os padrões da Guardia
- Quando o usuário solicita ajuda para commitar mudanças
- Quando invocado pelo `cry-commit`
- Quando invocado internamente pelo `kata-contribute`

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Alterações | Sim | Arquivos staged ou indicação do que commitar |
| Tipo | Não | Tipo Conventional Commits (feat, fix, docs, etc.). Se omitido, o agente infere do diff |
| Escopo | Não | Módulo ou domínio afetado. Se omitido, o agente infere do diff |
| Descrição | Não | Texto do subject. Se omitido, o agente compõe a partir do diff |
| `--warrior <nome>` | Não | Nome do warrior que invoca o kata (ex.: `apollo`, `athena`, `hephaestus`). Habilita o roteamento bot-author quando `bot_author.enabled=true` e o nome está em `bot_author.apply_to`. Quando omitido, o fluxo é sempre commit local (humano). |

## Workflow

```
Progresso:
- [ ] 1. Análise das mudanças
- [ ] 2. Classificação e composição da mensagem
- [ ] 3. Validação contra as Lexis
- [ ] 4. Resolução do autor (humano ou ahrena-bot)
- [ ] 5. Execução do commit
- [ ] 6. Verificação final
```

### Passo 1: Análise das Mudanças

1. Executar `git status` para verificar arquivos staged
2. Se não há arquivos staged, analisar o diff e sugerir o que incluir com `git add`
3. Executar `git diff --staged` para entender o conteúdo das mudanças
4. Verificar se as mudanças são atômicas (`lex-small-commits`):
   - Todas as mudanças pertencem a um único propósito?
   - Se não, orientar o usuário a dividir em commits separados

### Passo 2: Classificação e Composição da Mensagem

1. Consultar `codex-commit-standards` para referência
2. **Identificar o tipo:** feat, fix, docs, build, chore, ci, style, refactor, perf, test
3. **Identificar o escopo:** módulo ou domínio principal afetado (opcional)
4. **Compor o subject:**
   - Imperativo presente em inglês (`lex-commit-language`)
   - Máximo 72 caracteres
   - Sem ponto final
   - Formato: `tipo(escopo): descrição`
5. **Compor o body (se necessário):**
   - Versão em inglês com tag `[en]`
   - Versão em idioma local com tag `[pt-BR]` ou `[es]` (se solicitado)
   - Detalhar o "porquê" da mudança
6. **Adicionar rodapés (se aplicável):**
   - `Closes #N` para fechar issues
   - `BREAKING CHANGE:` para mudanças incompatíveis
   - `Co-authored-by:` para pair programming

### Passo 3: Validação contra as Lexis

Verificar conformidade com cada Lexis antes de executar:

- [ ] `lex-conventional-commits`: formato `tipo(escopo): descrição` correto?
- [ ] `lex-small-commits`: mudanças atômicas (um único propósito)?
- [ ] `lex-commit-language`: subject em inglês? Tag de idioma no body?
- [ ] `lex-signed-commits`: GPG configurado? (`git config --get commit.gpgsign` = true)

Se alguma validação falhar, corrigir antes de prosseguir.

### Passo 4: Resolução do Autor (humano ou ahrena-bot)

Antes de chamar `git commit`, o kata decide entre dois caminhos de autoria:

1. **Carregar `scripts/ahrena-auth.sh`** (sempre — é no-op quando `bot_author.enabled=false`):
   ```bash
   source scripts/ahrena-auth.sh
   ```
   Quando o diretivo está desligado, o script retorna imediatamente sem exportar nada. Quando ligado, ele exporta `GH_TOKEN_AHRENA_BOT` (token de instalação do GitHub App) e as variáveis `GIT_AUTHOR_*` / `GIT_COMMITTER_*` apontando para a identidade `ahrena-bot[bot]`.

2. **Ler `bot_author.enabled` e `bot_author.apply_to`** em `.ahrena/.directives`.

3. **Decisão de roteamento:**
   - Se `bot_author.enabled == true` E o input `--warrior <nome>` foi fornecido E `<nome>` está em `bot_author.apply_to`: usar o **caminho bot-author** (Passo 5a abaixo).
   - Caso contrário (ausência de `--warrior`, master switch desligado ou warrior fora do `apply_to`): usar o **caminho humano** (Passo 5b).

4. **Caminho bot-author** — montar o `Co-authored-by` do humano que dirige a sessão:
   ```bash
   HUMAN_CO_AUTHOR="$(git config user.name) <$(git config user.email)>"
   ```
   Esse valor entra como trailer do commit no Passo 5a.

### Passo 5: Execução do Commit

#### Passo 5a: Caminho bot-author (servidor)

Quando o roteamento do Passo 4 selecionou o caminho bot-author:

1. Invocar `scripts/ahrena-api-commit.sh` para criar o commit via GitHub Git Data API:
   ```bash
   scripts/ahrena-api-commit.sh \
     --branch "$(git rev-parse --abbrev-ref HEAD)" \
     --message "$(cat <<'EOF'
   tipo(escopo): descrição

   [en]
   Detailed description in English.

   [pt-BR]
   Descrição detalhada em português.

   Closes #123
   EOF
   )" \
     --co-author "${HUMAN_CO_AUTHOR}"
   ```

2. O script faz `POST /git/blobs` (por arquivo staged) → `POST /git/trees` → `POST /git/commits` → `PATCH /git/refs/heads/{branch}`. O commit resultante é assinado pelo token de instalação do App (verificado pelo servidor) e atribuído a `ahrena-bot[bot]`.

3. Exit codes do script:
   - `0` — commit criado com sucesso no remoto + working tree local sincronizada.
   - `2` — falha de rede/API (commit NÃO criado). **Fallback obrigatório**: cair para o Passo 5b (caminho humano) e emitir aviso visível ao usuário explicando a degradação.
   - `3` — commit criado no remoto MAS o `git fetch && git reset --hard` local falhou. Avisar o usuário para sincronizar manualmente antes do próximo push.

4. Em caso de fallback por exit code `2`, o agente DEVE manter o conteúdo dos arquivos staged (não desfazer `git add`) e prosseguir com o Passo 5b.

#### Passo 5b: Caminho humano (local, assinatura GPG)

Quando o roteamento do Passo 4 selecionou o caminho humano (ou no fallback do 5a):

1. Executar o commit com assinatura GPG:
   ```
   git commit -S -m "<mensagem>"
   ```
2. Para mensagem multiline (com body), usar:
   ```
   git commit -S -m "$(cat <<'EOF'
   tipo(escopo): descrição

   [en]
   Detailed description in English.

   [pt-BR]
   Descrição detalhada em português.

   Closes #123
   EOF
   )"
   ```

### Passo 6: Verificação Final

- [ ] `git log -1 --format='%s'` mostra o subject correto
- [ ] **Caminho humano (5b):** `git log -1 --show-signature` mostra assinatura GPG válida
- [ ] **Caminho bot-author (5a):** `git log -1 --format='%an <%ae>'` mostra `ahrena-bot[bot]` e o commit aparece com o badge **Verified** no GitHub
- [ ] **Caminho bot-author (5a):** o body do commit contém o trailer `Co-authored-by: <humano>` quando `bot_author.commit_co_author=human`
- [ ] O commit contém apenas as mudanças pretendidas
- [ ] O subject está em inglês e segue Conventional Commits
- [ ] O commit é atômico (uma mudança lógica)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Commit assinado e formatado | Git commit | Repositório local |

## Restrições

- Nunca fazer commit sem verificar conformidade com as 4 Lexis
- Nunca misturar mudanças não relacionadas em um único commit
- No caminho humano (Passo 5b), nunca fazer commit sem assinatura GPG configurada — se GPG não está configurado, alertar o usuário e orientar a configuração
- No caminho bot-author (Passo 5a), a assinatura é servida pelo token de instalação do GitHub App; não é necessário GPG local
- Nunca silenciar uma falha do `ahrena-api-commit.sh` — sempre informar ao usuário quando há fallback para o caminho humano

## Referências

- `lex-conventional-commits` — Formato obrigatório
- `lex-signed-commits` — Assinatura GPG obrigatória (caminho humano) ou assinatura via App (caminho bot)
- `lex-small-commits` — Atomicidade obrigatória
- `lex-commit-language` — Idioma obrigatório
- `codex-commit-standards` — Guia completo de standards
- `codex-git-workflow` — Seção "Author identity" descreve o roteamento humano vs bot
- `scripts/ahrena-auth.sh` — Gate `bot_author.enabled` + resolução de credenciais do GitHub App
- `scripts/ahrena-api-commit.sh` — Commit via Git Data API (caminho bot-author)
- `cry-commit` — Atalho que invoca este Kata
