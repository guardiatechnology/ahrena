# Codex: git-spice (gs) — automação de stacked branches

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Instalação, setup, catálogo de comandos e mapeamento operacional do `git-spice` quando o projeto adota essa ferramenta para Stacked Pull Requests

## Conteúdo

### 1. Versão mínima testada

| Item | Valor |
|------|-------|
| `git-spice` mínimo testado | `0.28.0` |
| `git` mínimo exigido pelo gs | `2.38` |
| Forges suportados | GitHub, GitLab (a partir de gs 0.9.0), Bitbucket Cloud (a partir de gs 0.25.0) |

> **Importante:** o binário instalado pelo Homebrew se chama `git-spice`, não `gs`. O alias `gs` é convenção de shell (`alias gs='git-spice'`); a documentação oficial e este Codex usam `gs` por concisão. Sempre que um agente executa o comando programaticamente, deve invocar `git-spice` para evitar depender de alias do usuário.

### 2. Instalação

| Plataforma | Comando |
|------------|---------|
| macOS / Linux (Homebrew) | `brew install git-spice` |
| Qualquer SO com Go ≥ 1.22 | `go install go.abhg.dev/gs@latest` |
| Debian / Ubuntu | `.deb` em [releases](https://github.com/abhinav/git-spice/releases) |
| Fedora / RHEL | `.rpm` em releases |
| Alpine | `.apk` em releases |
| Arch Linux (AUR) | `git-spice-bin` |

Após instalar, adicionar o alias se desejado:

```bash
# bash / zsh
echo "alias gs='git-spice'" >> ~/.zshrc

# fish
abbr -a gs git-spice
```

Verificação:

```bash
git-spice --version
# git-spice 0.28.0 ou superior
```

### 3. Setup por repositório (uma vez)

#### 3.1 Inicialização

Dentro do repositório (em qualquer worktree, inclusive o worktree compartilhado de uma stack):

```bash
git-spice repo init --trunk main --remote origin
```

| Flag | Significado |
|------|-------------|
| `--trunk=BRANCH` | Branch protegida contra writes (`main`, `master`, `release/*`). Honra `lex-protected-trunk` |
| `--remote=NAME` | Remote para push de branches submetidas (default: `origin`) |
| `--upstream=NAME` | Remote contra o qual abrir CRs; só difere de `--remote` em fork mode |
| `--reset` | Esquece toda a metadata do `gs` para o repositório (raro; usar quando metadata corrompeu) |

Se `--upstream` não for passado, gs usa o mesmo remote do `--remote`. Re-rodar `repo init` em repo já inicializado migra branches existentes para o novo trunk se ele mudar.

A metadata fica em `.git/spice/` (dentro do `.git/`, não rastreada — não precisa de `.gitignore`).

#### 3.2 Autenticação

```bash
git-spice auth login
```

O prompt oferece:

| Método | Quando preferir |
|--------|-----------------|
| **CLI** | `gh` (ou `glab`) já autenticado na máquina — `gs` reusa o token; opção mais rápida em ambiente Ahrena |
| **OAuth** | Fluxo de browser; sem `gh` instalado |
| **GitHub App** | Instalação per-repo; útil em organizações com SSO restritivo |
| **Git Credential Manager** | Reuso de credenciais já armazenadas pelo Git |
| **Personal Access Token** | Token gerado manualmente; menos seguro que OAuth |

O token é armazenado em keyring do SO (Keychain no macOS, Secret Service no Linux, Credential Manager no Windows). Para revalidar:

```bash
git-spice auth status            # checa estado
git-spice auth login --refresh   # renova
git-spice auth logout            # remove
```

> **Ahrena rule:** não persistir tokens em arquivos versionados nem em `.ahrena/.directives` (per `lex-mcp` rule 2 e práticas equivalentes). Usar exclusivamente o keyring do SO.

### 4. Catálogo de comandos por categoria

Versão de referência: gs 0.28.0. Cada subcomando tem alias curto entre parênteses.

#### 4.1 Repositório

| Comando | Função |
|---------|--------|
| `gs repo (r) init (i)` | Inicializa metadata do gs no repo (define trunk, remotes) |
| `gs repo (r) sync (s)` | Pull do trunk + apaga branches já mergeadas + opcional `--restack` |
| `gs repo (r) restack (r)` | Restack de **todas** as branches rastreadas pelo gs |

#### 4.2 Branch

| Comando | Função |
|---------|--------|
| `gs branch (b) track (tr)` | Importa branch existente para o gs (opcional `--base`) |
| `gs branch (b) untrack (untr)` | Remove branch do tracking sem deletar |
| `gs branch (b) checkout (co)` | Troca de branch dentro da stack |
| `gs branch (b) create (c)` | Cria nova branch acima da atual; commita stage atual; aceita `--target`, `--insert`, `--below`, `-m`, `-a` |
| `gs branch (b) delete (d, rm)` | Apaga branch (local + tracking) |
| `gs branch (b) submit (s)` | Cria/atualiza CR só da branch atual |
| `gs branch (b) restack (r)` | Restack só da branch atual contra a base |
| `gs branch (b) onto (on)` | Move a branch para outra base (substitui `git rebase --onto` em casos comuns) |
| `gs branch (b) rename (rn, mv)` | Renomeia branch e atualiza metadata |
| `gs branch (b) fold (fo)` | Mergeia a branch na sua base (consolida camadas) |
| `gs branch (b) split (sp)` | Divide a branch em múltiplas branches por commit |
| `gs branch (b) squash (sq)` | Squash da branch em commit único |
| `gs branch (b) edit (e)` | `git rebase -i` aware do stack |
| `gs branch (b) diff (di)` | Diff entre branch e base |

#### 4.3 Stack / Upstack / Downstack

| Comando | Função |
|---------|--------|
| `gs stack (s) submit (s)` | Submete **toda** a stack (cria/atualiza CR de cada camada) |
| `gs stack (s) restack (r)` | Restack de toda a stack |
| `gs stack (s) edit (e)` | Reordena ou remove camadas via editor (uso esporádico) |
| `gs stack (s) delete (d)` | Apaga **todas** as branches da stack |
| `gs upstack (us) submit (s)` | Submete só a branch atual e as acima |
| `gs upstack (us) restack (r)` | Restack só da branch atual e das acima |
| `gs upstack (us) onto (o)` | Move a branch atual + camadas acima para nova base |
| `gs upstack (us) delete (d)` | Apaga só as branches acima |
| `gs downstack (ds) track (tr)` | Importa branches abaixo no grafo |
| `gs downstack (ds) submit (s)` | Submete só a branch atual e as abaixo |
| `gs downstack (ds) edit (e)` | Reordena camadas abaixo |

#### 4.4 Commit

| Comando | Função |
|---------|--------|
| `gs commit (c) create (c)` | Atalho para `git commit` + `gs upstack restack` (mantém camadas acima sincronizadas) |
| `gs commit (c) amend (a)` | Atalho para `git commit --amend` + `gs upstack restack` |
| `gs commit (c) split (sp)` | Divide o último commit em múltiplos |
| `gs commit (c) fixup (f)` | Cria commit fixup contra commit anterior |
| `gs commit (c) pick (p)` | Cherry-pick aware do stack |

Flags relevantes (`commit create` / `commit amend`):

| Flag | Função |
|------|--------|
| `-a, --all` | Stage automático de modificados (equivale a `git commit -a`) |
| `-m, --message=MSG` | Mensagem inline |
| `--no-verify` | Pula hooks `pre-commit`/`commit-msg` (use com cautela; consultar `lex-conventional-commits`) |
| `--signoff` | Adiciona `Signed-off-by:` (não é assinatura GPG; ver seção 7) |
| `--no-edit` (só amend) | Não abre editor |

#### 4.5 Rebase

| Comando | Função |
|---------|--------|
| `gs rebase (rb) continue (c)` | Continua rebase interrompido por conflito (substitui `git rebase --continue`) |
| `gs rebase (rb) abort (a)` | Aborta rebase em curso |

#### 4.6 Log e navegação

| Comando | Função |
|---------|--------|
| `gs log (l) short (s)` | Lista branches rastreadas (visualização de stack) |
| `gs log (l) long (l)` | Lista branches + commits |
| `gs up (u)` | Sobe uma camada |
| `gs down (d)` | Desce uma camada |
| `gs top (U)` | Vai ao topo da stack |
| `gs bottom (D)` | Vai à base da stack |
| `gs trunk` | Vai ao trunk (`main`) |

### 5. Mapeamento operação → vanilla → gs

Tabela de equivalência entre o caminho vanilla descrito em `codex-stacked-prs` e o caminho gs. Use durante a tradução mental quando alternar entre projetos.

| Operação | Vanilla (`git` + `gh`) | git-spice |
|----------|------------------------|-----------|
| Inicializar suporte a stacks no repo | (nenhum setup) | `gs repo init --trunk main` (uma vez) |
| Criar a primeira camada da stack | `git checkout -b feat/N-stack-1-slug main` | `gs branch create feat/N-stack-1-slug` (com stage) |
| Criar camada acima | `git checkout -b feat/N-stack-2-slug feat/N-stack-1-slug` | `gs branch create feat/N-stack-2-slug` (estando em camada 1, com stage) |
| Commitar mantendo camadas acima sincronizadas | `git commit && for i in superiores: git checkout {i} && git rebase {i-1} && git push --force-with-lease` | `gs commit create -m "..."` (auto-restack das camadas acima) |
| Amendar commit já submetido | `git commit --amend && cascade rebase manual` | `gs commit amend [--no-edit]` (auto-restack) |
| Rebasear contra trunk avançado | `git fetch && git rebase origin/main && cascade rebase manual` | `gs repo sync --restack` |
| Submeter PR só da camada atual | `gh pr create --base $PREV --head $THIS ...` | `gs branch submit` |
| Submeter PRs de toda a stack | loop de N `gh pr create` | `gs stack submit [--draft] [--fill]` |
| Atualizar PRs após push | (auto via push da head) | `gs branch submit` ou `gs stack submit` (idempotente) |
| Force-push seguro | `git push --force-with-lease` | gs já usa lease por default; `--force` bypassa |
| Apagar branches mergeadas | manual: `git push origin --delete` + `git branch -D` | `gs repo sync` (faz cleanup local; `--delete-branch` no merge cuida do remoto) |
| Atualizar `base` do PR após merge da camada inferior | `gh pr edit $PR --base main` | `gs repo sync` rebaseia automaticamente; `gs branch submit` recria com nova base |
| Resolver conflito em rebase | `git rebase --continue` / `--abort` | `gs rebase continue` / `gs rebase abort` |
| Reordenar camadas no meio | recriar manualmente | `gs stack edit` |

### 6. Force-push: lease por default

Diferente do `git push`, `gs branch submit` e `gs stack submit` aplicam `--force-with-lease` automaticamente — o push é recusado se um revisor commitou em cima desde o último fetch.

| Flag | Comportamento |
|------|---------------|
| (default) | `--force-with-lease` implícito |
| `--force` | Bypass do lease — equivale a `git push --force` cego |
| `--no-verify` | Pula `pre-push` hooks |

> **Regra Ahrena:** nunca passar `--force` sem motivo registrado. O default já cobre 99% dos casos. `--no-verify` requer autorização explícita do usuário (mesma disciplina aplicada ao caminho vanilla).

### 7. Interação com hooks e GPG

#### 7.1 Hooks pre-commit / commit-msg

`gs commit create` e `gs commit amend` rodam hooks como `git commit` faria. Para hooks pesados (linters, testes), o auto-restack pode ser lento porque cada camada acima refaz o ciclo de hook. Mitigações:

1. **Otimizar hooks** — mover validações pesadas para CI; deixar pre-commit rápido (≤ 1s).
2. **Hook condicional por estado de stack** — hook que detecta `.git/spice/` ativa pode escolher modo lite.
3. **`--no-verify` deliberado** — em casos extremos, com autorização do usuário e justificativa registrada (idealmente no body do PR).

#### 7.2 Assinatura GPG (lex-signed-commits)

`gs` respeita a config global do git (`commit.gpgsign=true`, `user.signingkey`). Como `gs commit create/amend` chama `git commit` por baixo, a assinatura é preservada normalmente; não há flag específica em `gs`. Em rebase de auto-restack, o git re-aplica os commits e — se `commit.gpgsign=true` — assina os novos commits resultantes com a chave configurada.

Verificação:

```bash
git log --show-signature -3
# esperado: "Good signature from ..." em cada commit das camadas
```

> **Atenção:** `--signoff` (`Signed-off-by:`) é um trailer em texto plano, não assinatura criptográfica. `lex-signed-commits` exige assinatura GPG verificável; o trailer é opcional e ortogonal.

### 8. Workflow recomendado (resumido)

1. `gs repo init --trunk main` — uma vez por repo.
2. `gs auth login` (método **CLI** se `gh` está logado).
3. Worktree compartilhado da stack (per `codex-stacked-prs` seção 4): `git worktree add .worktrees/{N}-{slug}-stack -b feat/{N}-stack-1-{slug} main`.
4. `cd .worktrees/{N}-{slug}-stack`
5. Editar arquivos, `git add`, `gs commit create -m "feat(scope): camada 1 — schema (1/N)"`.
6. `gs branch create feat/{N}-stack-2-{slug}` (estando em stage acima dos arquivos da camada 2). Repetir até a última camada.
7. `gs stack submit --draft` para abrir todos os PRs como rascunho de uma só vez (ou `--fill` para preencher título/body do commit).
8. Para cada PR criado, espelhar labels/assignee/reviewers via `gh pr edit` (ver `kata-stacked-pr-create` seção "Variant: git-spice"). `gs stack submit` aceita `--label`, `--reviewer`, `--assign` mas não diferencia por camada — para mirror exato use `gh pr edit`.
9. Iteração de review: `gs commit amend` na camada criticada, depois `gs branch submit` (idempotente).
10. Merge bottom-up: `gh pr merge --squash` da camada base; depois `gs repo sync` para rebasear o resto e apagar a camada mergeada localmente.

### 9. Limitações conhecidas

| Limitação | Origem |
|-----------|--------|
| Cross-fork PR (forks com upstream e push remotes diferentes) só cria CR para branches diretamente sobre o trunk | Doc oficial — `guide/limits/` |
| Squash-merge upstream apaga histórico unsquashed; camadas superiores precisam de `gs repo sync` (e às vezes `gs upstack restack`) para refletir | Doc oficial |
| Bitbucket Cloud sem suporte a labels, assignees ou template enumeration via `gs submit` | Doc oficial |
| Repositórios que dismissam approval ao trocar base do PR são incompatíveis com stacks (limitação do GitHub, não do `gs`) | Doc oficial |
| Reorder de camadas via `gs stack edit` é bem suportado, mas hooks que dependem de ordem específica de commits podem confundir o restack — testar antes em sandbox | Operacional |

### 10. Troubleshooting

| Sintoma | Causa provável | Resolução |
|---------|----------------|-----------|
| `gs commit create` falha com "branch is not tracked" | Branch criada com `git checkout -b` em vez de `gs branch create` | `gs branch track` para importar |
| `gs stack submit` recusa push | `--force-with-lease` detectou divergência (alguém commitou na branch remota) | `git fetch origin {branch}` e investigar; nunca `--force` sem entender |
| Auto-restack entra em loop com hook pesado | Hook re-acionando rebase | Otimizar hook ou usar `--no-verify` com autorização |
| `gs auth status` mostra "not logged in" mas `gh` está | Método de auth selecionado foi diferente de **CLI** na primeira vez | `gs auth login --refresh` e escolher **CLI** |
| Squash merge upstream gera "artificial conflicts" no rebase | Histórico squashed não bate com o que `gs` esperava | `gs repo sync` resolve a maioria; senão `gs upstack onto main` |
| `gs repo init --trunk main` falha com "trunk does not exist" | Branch trunk ainda não existe localmente | `git fetch origin && git checkout main && gs repo init --trunk main` |
| Confusão sobre `gs` vs `git-spice` | Alias não configurado | Usar `git-spice` direto em scripts; `gs` só em shell interativo |

### 11. Diretiva relacionada

A escolha entre `vanilla` e `gs` é controlada por `.ahrena/.directives`:

```yaml
stacked_prs:
  tool: gs        # vanilla (default) | gs
```

| Valor | Comportamento |
|-------|---------------|
| `vanilla` (ou ausente) | Katas executam o procedimento `git` + `gh` clássico |
| `gs` | Katas executam a seção "Variant: git-spice" — pré-condição: `git-spice` instalado e `gs repo init` rodado |

Mudar de `vanilla` para `gs` num projeto com stacks ativas exige importação manual via `gs branch track` para cada branch existente. Não há automação para essa migração.
