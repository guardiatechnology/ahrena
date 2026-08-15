# Ahrena: AI-First Capability Framework

O **Ahrena** é um Capability Framework AI-first que estrutura conhecimento, processos e comportamento de agentes de IA através de uma **taxonomia unificada** (Clade → Subclade → Pilar). Lexis, Codex, Katas, Warriors e Cries são organizados por disciplina e área, orientando como humanos e IA colaboram em qualquer domínio.

**Princípios:** IA como copiloto (não piloto); processo sobre ferramenta; artefatos versionados como código; `framework/` como fonte da verdade, agnóstico de plataforma.

---

## Instalação

### Pré-requisitos

O Ahrena verifica o ambiente em três camadas durante `make bootstrap` / `make install` (preflight). Veja `make preflight` para rodar os checks isoladamente.

**Hard (bloqueia o install se faltar):**
- **Python 3.8+** — interpretador para os scripts
- **git** — controle de versão
- **make** — entrypoint do Makefile

**Soft (avisa e oferece instalar):**
- **gh** (GitHub CLI) — usado pelo fluxo Issue-Driven, stacked PRs e pelo cost-stamp
- **gpg** — exigido por `lex-signed-commits`

**Lazy (instalado sob demanda quando o MCP correspondente é ativado via `make mcp-enable`):**
- **Node.js** — apenas para o servidor MCP do Figma (degrau npx). GitHub e Notion usam HTTP remoto, sem dependência local.

**Como instalar manualmente:**
- **Windows:** `winget install --id Git.Git -e`, `winget install --id GnuWin32.Make -e`, `winget install --id GitHub.cli -e`, `winget install --id GnuPG.Gpg4win -e`, `winget install --id OpenJS.NodeJS.LTS -e`.
- **macOS:** `xcode-select --install` cobre git e make (via Command Line Tools); `brew install gh gnupg node` para o restante.
- **Linux (Debian/Ubuntu):** `sudo apt-get install -y git build-essential gh gnupg nodejs npm`. RHEL/Fedora: `sudo dnf install -y git gh gnupg2 nodejs npm` + `sudo dnf groupinstall -y 'Development Tools'`.

### Plataformas

| Nome | Descrição |
|------|------------|
| **Cursor** | IDE com suporte integrado: o instalador gera `.cursor/` (rules, skills, commands, agents) a partir do framework. [Suporte ao Cursor](#suporte-ao-cursor) |
| **Claude Code** | Suporte ao Claude Code: o instalador gera `.claude/` (docs, skills, commands, agents) e `CLAUDE.md` a partir do framework. [Suporte ao Claude Code](#suporte-ao-claude-code) |
| **OpenAI Codex** | Suporte nativo ao Codex: gera `AGENTS.md`, skills de repositório, agentes TOML e referências progressivas. [Suporte ao OpenAI Codex](#suporte-ao-openai-codex) |

### Primeira instalação

O instalador baixa o framework do GitHub e configura o projeto (não é necessário clonar o repositório).

**Via Makefile (recomendado):**

```powershell
# Windows (PowerShell)
Invoke-WebRequest https://github.com/guardiatechnology/ahrena/releases/latest/download/Makefile -OutFile Makefile
make bootstrap PLATFORM=cursor
```

```bash
# macOS / Linux
curl -sSL https://github.com/guardiatechnology/ahrena/releases/latest/download/Makefile -o Makefile
make bootstrap PLATFORM=cursor
```

**Via one-liner (sem Make):**

```powershell
# Windows — somente framework
Invoke-WebRequest https://github.com/guardiatechnology/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py; Remove-Item install.py

# Windows — framework + Cursor IDE
Invoke-WebRequest https://github.com/guardiatechnology/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform cursor; Remove-Item install.py

# Windows — framework + Claude Code
Invoke-WebRequest https://github.com/guardiatechnology/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform claude-code; Remove-Item install.py

# Windows — framework + OpenAI Codex
Invoke-WebRequest https://github.com/guardiatechnology/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform codex; Remove-Item install.py
```

```bash
# macOS / Linux — framework + Cursor
curl -sSL https://github.com/guardiatechnology/ahrena/releases/latest/download/install.py | python3 - --platform cursor

# macOS / Linux — framework + Claude Code
curl -sSL https://github.com/guardiatechnology/ahrena/releases/latest/download/install.py | python3 - --platform claude-code

# macOS / Linux — framework + OpenAI Codex
curl -sSL https://github.com/guardiatechnology/ahrena/releases/latest/download/install.py | python3 - --platform codex
```

**Opções do instalador:**

| Flag | Descrição |
|------|------------|
| `--platform cursor` | Gerar `.cursor/` (rules, skills, commands, agents) |
| `--platform claude-code` | Gerar `.claude/` (docs, skills, commands, agents) e `CLAUDE.md` |
| `--platform codex` | Gerar `AGENTS.md`, `.agents/skills/`, `.codex/agents/` e `.codex/docs/` |
| `--profile {full\|standard\|minimal}` | Perfil base de preferências; sobrescrito por `--with-*` / `--without-*`. Default: `full` |
| `--with-mcp / --without-mcp LISTA` | Incluir/excluir MCPs (csv); o servidor `ahrena` é sempre mantido |
| `--with-hooks / --without-hooks LISTA` | Incluir/excluir hooks (csv): `rtk`, `pr-cost-attribution` |
| `--with-features / --without-features LISTA` | Incluir/excluir features opcionais do `.directives` (`pr_cost_tracking`, `session_tracking`, `notifications`, `pm`) |
| `--with-setup / --without-setup LISTA` | Incluir/excluir itens de project setup (csv): `github-issue-templates`, `github-pr-template`, `github-codeowners`, `gitignore-merge` |
| `--list-catalog` | Imprime o catálogo (MCPs, hooks, features, project setup) e sai |
| `--clades X,Y` | Instalar apenas clades especificados (ex.: `_foundation,documentation`) |
| `--version v0.1.0` | Versão específica (tag ou branch) — instalação remota |
| `--local` | Usar o diretório atual como fonte (executar na raiz do repo Ahrena) |
| `--source PATH` | Usar clone local do Ahrena em PATH em vez de baixar do GitHub |
| `--self` | Usar o repo Ahrena que contém este script como fonte — instalação offline |
| `--language en` | Sobrescrever idioma padrão no `.directives` |
| `--directives PATH` | Usar `.directives` customizado (caminho local ou URL) |
| `--target PATH` | Instalar em outro diretório |
| `--dry-run` | Simular sem alterar nada |
| `--clean` | Remover arquivos instalados pelo Ahrena |

Quando `--clades` é usado, a seleção é salva em `.ahrena/.installed-clades` e respeitada pelo `update.py`.

**Instalação guiada por preferências:** na primeira instalação (quando `.ahrena/.directives` ainda não existe), o instalador resolve a seleção de MCPs, hooks, features opcionais e itens de project setup a partir de `--profile` + `--with-*` / `--without-*`. Sem nenhuma flag e com stdin TTY, abre um prompt interativo (pré-marcado = perfil Full). Em modo `--non-interactive` (CI), aplica diretamente a seleção resolvida. Variáveis de ambiente ausentes para MCPs selecionados geram WARNING — nunca falham a instalação. `python scripts/install.py --list-catalog` lista todas as opções.

**Project setup (`--with-setup` / `--without-setup`):** materializa convenções de GitHub do projeto além do `.directives`/MCPs/hooks: `.github/ISSUE_TEMPLATE/*.yml` (issues), `.github/pull_request_template.md` (PRs), `.github/CODEOWNERS` (preservado quando já existe; resolve a org via `git remote get-url origin`, com fallback comentado quando o remote não está no GitHub), e merge idempotente de um bloco gerenciado em `.gitignore` entre marcadores `AHRENA-GITIGNORE`. Defaults por perfil: Full traz os quatro; Standard traz três (sem auto-CODEOWNERS); Minimal não traz nenhum.

### Instalação offline

Se não houver acesso à internet, ou você queira distribuir o Ahrena em ambientes restritos, use a flag `--self` a partir de um clone local do repositório:

```bash
# Clonar o repo uma vez (com acesso)
git clone https://github.com/guardiatechnology/ahrena.git

# Instalar em qualquer projeto, de qualquer diretório, sem rede
python /caminho/para/ahrena/scripts/install.py --self --target /caminho/para/projeto --platform cursor
python /caminho/para/ahrena/scripts/install.py --self --target /caminho/para/projeto --platform claude-code
```

**Via Makefile** (a partir da raiz do repo Ahrena):

```bash
make install-to TARGET=/caminho/para/projeto PLATFORM=cursor
make install-to TARGET=/caminho/para/projeto PLATFORM=claude-code LANGUAGE=en
```

O `--self` detecta automaticamente a raiz do repo Ahrena a partir do próprio script, sem depender do diretório de trabalho atual.

### Atualização e desinstalação

| Ação | Makefile | Script direto |
|------|----------|----------------|
| **Atualizar (remoto)** | `make update` ou `make update VERSION=v0.2.0` | `python .ahrena/update.py` |
| **Atualizar (local)** | `make update LOCAL=1` ou `make update SOURCE=../ahrena` | `python .ahrena/update.py --local` ou `--source /path/to/ahrena` |
| **Re-sincronizar Cursor** | `make sync-cursor` | `python .ahrena/update.py --sync-cursor` |
| **Re-sincronizar Claude Code** | `make sync-claude-code` | `python .ahrena/update.py --sync-claude-code` |
| **Re-sincronizar OpenAI Codex** | `make sync-codex` | `python .ahrena/update.py --sync-codex` |
| **Desinstalar** | `make uninstall` | `python .ahrena/uninstall.py` (ou `--force` sem confirmação) |

**Padrão:** instalação e atualização são do **remoto** (GitHub). Para fonte local use `--local` / `--source` ou no Makefile `LOCAL=1` / `SOURCE=...`.

**Desenvolvimento local (contribuidores):** `make dev-install PLATFORM=cursor` — instala a partir do diretório atual (raiz do repo Ahrena). Para trazer o mais recente do ambiente de desenvolvimento, use `make update LOCAL=1` ou `make update SOURCE=...` no projeto instalado.

### Equivalência sem Make (Windows)

Se `make` não estiver disponível, use os scripts em PowerShell:

| Ação | Comando |
|------|---------|
| Instalação remota + Cursor | `python .ahrena/install.py --target . --version main --repo https://github.com/guardiatechnology/ahrena --platform cursor` |
| Instalação remota + Claude Code | `python .ahrena/install.py --target . --version main --repo https://github.com/guardiatechnology/ahrena --platform claude-code` |
| Instalação local (no repo Ahrena) | `python scripts/install.py --local --target . --platform cursor` |
| Instalação offline (clone) | `python C:\path\to\ahrena\scripts\install.py --self --target . --platform cursor` |
| Instalação local (path) | `python .ahrena/install.py --target . --source C:\path\to\ahrena --platform cursor` |
| Atualização remota | `python .ahrena/update.py --target .` |
| Atualização local | `python .ahrena/update.py --target . --local` ou `--source C:\path\to\ahrena` |

### O que é instalado

| Comando | `.ahrena/` | `.cursor/` | `.claude/` + `CLAUDE.md` | OpenAI Codex |
|---------|------------|------------|--------------------------|--------------|
| Sem `--platform` | framework, directives, scripts, Makefile | — | — | — |
| `--platform cursor` | idem | rules, skills, commands, agents | — | — |
| `--platform claude-code` | idem | — | docs, skills, commands, agents + CLAUDE.md + RTK hook | — |
| `--platform codex` | idem | — | — | `AGENTS.md`, `.agents/skills/`, `.codex/agents/`, `.codex/docs/`, `.codex/config.toml` |

### RTK (Rust Token Killer)

Quando você instala com `--platform claude-code`, o Ahrena também vincula o **hook `PreToolUse` do RTK** em `.claude/settings.json`. O RTK reescreve comandos comuns (`git`, `gh`, `tsc`, `pytest`, `jest`, etc.) por versões com saída compacta, reduzindo o consumo de tokens em 60–90%.

Comportamento:

- **Padrão `rtk.enabled: true`** em `.directives`: cada `make install` / `make dev-install` / `make update` reconcilia o hook idempotentemente. Quando `rtk.auto_install_binary: true` (também o padrão), o instalador detecta o binário e tenta instalá-lo quando ausente (`brew` no macOS, `curl install.sh | sh` no Linux/macOS, WSL ou `cargo` no Windows). Falhas de instalação do binário não são fatais.
- **Opt-out total**: defina `rtk.enabled: false` em `.ahrena/.directives` — install/update não tocam em nenhum artefato RTK.
- **Opt-out granular**: defina `rtk.auto_install_binary: false` para manter o wire do hook mas pular a tentativa automática de instalação do binário.
- **Fallback estrito**: o comando gravado em `settings.json` é `if command -v rtk >/dev/null 2>&1; then rtk hook claude; fi`. Quando o binário está ausente do PATH o hook termina vazio e o Claude Code segue com a entrada original — nenhum erro.

Binário e documentação: <https://github.com/rtk-ai/rtk>.

---

## MCP (Model Context Protocol)

O Ahrena suporta servidores MCP para GitHub, Notion e Figma. Quando ativados, o instalador gera automaticamente as entradas para Cursor, Claude Code ou para a seção gerenciada de `.codex/config.toml` no OpenAI Codex.

### Ativando servidores MCP

Adicione a seção `mcp` ao seu `.ahrena/.directives`:

```yaml
mcp:
  servers:
    - github
    - notion
    - figma
```

Na próxima execução de `make sync-cursor`, `make sync-claude-code` ou `make install-to`, as entradas MCP serão mescladas **de forma aditiva** — servidores gerenciados por você fora do Ahrena são preservados.

### Servidores disponíveis

| Servidor | Variável de ambiente | Uso |
|----------|---------------------|-----|
| `github` | `GH_TOKEN` | Criar issues, PRs, push de arquivos, listagem de commits |
| `notion` | `NOTION_API_KEY` | Criar e sincronizar páginas, pesquisar databases |
| `figma` | `FIGMA_API_KEY` | Extrair design tokens, specs de componentes, exportar frames |

As credenciais são sempre referenciadas via variáveis de ambiente — **nunca** hardcoded em arquivos versionados.

### Katas MCP

| Kata | Plataforma | Descrição |
|------|-----------|------------|
| `kata-mcp-github-read` | GitHub | Consulta repositórios, issues, PRs, commits e código (somente leitura) |
| `kata-mcp-notion-read` | Notion | Consulta páginas, databases e blocos do Notion (somente leitura) |
| `kata-mcp-figma-extract` | Figma | Extrai design tokens e specs de componentes do Figma |

---

## Pilares (tipos de capacidade)

| Pilar | Função | Prefixo | Detalhes |
|-------|--------|---------|----------|
| **Lexis** | Leis inquebráveis (segurança, qualidade, processo) | `lex-` | [Templates e convenções](./framework/pt-BR/README.md#estrutura) |
| **Codex** | Manuais de referência para decisões contextualizadas | `codex-` | [Templates e convenções](./framework/pt-BR/README.md#estrutura) |
| **Katas** | Procedimentos repetíveis (skills) | `kata-` | [Templates e convenções](./framework/pt-BR/README.md#estrutura) |
| **Warriors** | Agentes especializados (persona + escopo) | `warrior-` | [Templates e convenções](./framework/pt-BR/README.md#estrutura) |
| **Cries** | Comandos recorrentes (atalhos) | `cry-` | [Templates e convenções](./framework/pt-BR/README.md#estrutura) |

Descrição completa de cada Pilar e quando usar: [Framework — Guia do Desenvolvedor](./framework/pt-BR/README.md).

### Clades e Subclades

**Clade** = disciplina de negócio. **Subclade** = área de conhecimento dentro da disciplina. Detalhamento de cada Clade e links para READMEs:

| Clade | Subclades | Documentação |
|-------|-----------|----------------|
| **product** | discovery, strategy, analytics, delivery | Extensível por organização |
| **engineering** | platform, backend, frontend, devops, security, quality, workflow | [Platform (Guardia)](framework/pt-BR/engineering/platform/README.md) · [Workflow (Issue-Driven)](framework/pt-BR/engineering/workflow/README.md) · Backend (Apollo) · Frontend (Hephaestus) · DevOps (Atlas) |
| **finance** | accounting, treasury, controllership | Extensível por organização |
| **operations** | support, infrastructure, monitoring | Extensível por organização |
| **documentation** | i18n (tradução) | [Sistema de tradução / Hermes](framework/pt-BR/documentation/i18n/README.md) |
| **_foundation** | authoring, contributing, process, quality, security, tooling, i18n | Transversal a todos os Clades; [Contributing](framework/pt-BR/_foundation/contributing/README.md), [Authoring](framework/pt-BR/_foundation/authoring/README.md), [Tooling](framework/pt-BR/_foundation/tooling/README.md) |

Clades e Subclades são **extensíveis**: cada organização define os que fizerem sentido.

### Warriors disponíveis

| Warrior | Nome | Clade | Uso |
|---------|------|-------|-----|
| `warrior-translator` | Hermes | documentation/i18n | Tradução de documentação; [detalhes](framework/pt-BR/documentation/i18n/README.md) |
| `warrior-daedalus` | Daedalus | engineering/platform | Design de API RESTful (OAS); `/cry-api-design`, `/cry-full-design` |
| `warrior-kronos` | Kronos | engineering/platform | Event Storm e CloudEvents; `/cry-event-storm`, `/cry-full-design` |
| `warrior-apollo` | Apollo | engineering/backend | Router Python/.NET; Apollo-.NET prioriza corretude, memory safety e baixa pressão de GC; `/cry-python-implement`, `/cry-dotnet` |
| `warrior-hephaestus` | Hephaestus | engineering/frontend | Implementação Frontend (React/TS) com a11y e testes comportamentais |
| `warrior-atlas` | Atlas | engineering/devops | Arquitetura de soluções AWS; Well-Architected; IaC e custo |
| `warrior-hera` | Hera | engineering/quality | Estratégia de testes, plano de cobertura, auditoria de suite |
| `warrior-hestia` | Hestia | engineering/sre | SLO, runbooks, incident response, post-mortem blameless |
| `warrior-demeter` | Demeter | engineering/data | Modelagem de dados, migrations seguras, retenção LGPD |
| `warrior-iris` | Iris | engineering/mobile | Implementação iOS/Android paritária, offline-first, acessibilidade |
| `warrior-athena` | Athena | engineering/workflow | Orquestradora do fluxo Issue-Driven; `/cry-implement-issue` |

Para a arquitetura do framework (paths, diagramas, de-para com `.cursor/`), consulte o [Guia do Desenvolvedor](./framework/pt-BR/README.md#arquitetura-do-framework).

---

## Fluxo Issue-Driven Development

O Ahrena oferece um **fluxo completo de desenvolvimento orientado por issues do GitHub**, conduzido pela `warrior-athena`. A partir de uma issue, o fluxo passa por 7 fases (análise → requisitos → arquitetura → implementação → segurança → quality gate → PR), com 2 gates humanos/automáticos, geração de ADRs (`docs/adr/`) e documentação estruturada em `docs/issues/issue-{n}/`.

```bash
# Pré-requisito: mcp.servers inclui github (e opcionalmente notion) em .ahrena/.directives
/cry-implement-issue 42 guardiatechnology/ahrena
```

**Gate 1 (Escopo):** humano aprova brief + ACs + arquitetura antes da implementação.
**Gate 2 (Qualidade):** automatizado com 6 checks — rastreabilidade AC↔teste (bidirecional), scope creep, best practices, testes, cobertura, tipos.

Guia completo: [engineering/workflow/README.md](framework/pt-BR/engineering/workflow/README.md).

---

## Workflow Status

Per ADR-002 (Issue-as-plan model), o plano canônico vive em três camadas:

1. **Body da Issue do GitHub** — canonical. Summary + Plan (Objective, Steps, Risks, Dependencies, Open Questions). Audit log = timeline nativo do GitHub.
2. **`.plans/{N}.md`** (gitignored) — working memory da IA. Superset do body + blocos `<!-- not-flushed -->` para scratch. Materializado por `kata-load-plan-from-issue`; flushed por `kata-flush-plan-to-issue`.
3. **`.issues/{N}/`** (committed) — Phase artifacts (`01-brief.md` … `06-quality-report.md`) do fluxo Issue-Driven.

O enum de `status:` vive como **label** na Issue (e no PR a partir de `to review`), dividido em dois eixos disjuntos (`lex-issue-status`):

**Eixo A — Dev cycle** (Issues/PRs de feature/fix/chore):
```
todo → development → to review → review → done
                          ↘
                          abandoned (terminal alternativo)
```

**Eixo B — Release cycle** (release Issue dedicada criada por Janus):
```
to release → release → done
                  ↘
                  abandoned
```

Mutex é **intra-artefato** (cada Issue/PR carrega exatamente uma label `status:*`); cross-cycle labeling é proibido pelo HARD-GATE de `lex-issue-status`.

Owners das transições (`lex-agent-planning`):

| Transição | Owner | Eixo |
|---|---|---|
| `— → todo` | `warrior-eunomia` (fallback: agente da sessão) | A |
| `todo → development → to review` | `warrior-athena` | A |
| `to review ↔ review` | `warrior-argos` | A |
| `to review → done` | `warrior-athena` (no merge) | A |
| `— → to release → release → done` | `warrior-janus` (release Issue dedicada com `Tracks: #N1, ...`) | B |

Crie as labels do framework com `scripts/bootstrap_labels.sh [owner/repo]` ou `make bootstrap-labels`.

**Cadência de load/flush:** sincronização entre `.plans/{N}.md` e o body da Issue ocorre em 3 gatilhos canônicos: (a) cada transição de label `status:`, (b) cada Step marcado como concluído, (c) fim de sessão (heartbeat encerra). Toggles intermediários e edições de scratch (`<!-- not-flushed -->`) são livres. Documentação operacional em `codex-agent-planning`.

**Loop 3×15min:** após abrir o PR, Athena agenda 3 ciclos de 15 min e cobra o reviewer humano via MCP de notificação (`notifications.provider` em `.ahrena/.directives`, canal `notifications.channels.pr_review_timeout`) se não houver aprovação no terceiro ciclo. Manuais: `codex-notifications` (provider-agnóstico) e `codex-mcp-slack` (provider inicial).

---

## Suporte ao Cursor

O Ahrena oferece **suporte integrado ao Cursor IDE**. Com `--platform cursor` (ou `PLATFORM=cursor` no Makefile), o instalador gera o diretório `.cursor/` a partir do `framework/`, permitindo que as Lexis, Codex, Katas, Warriors e Cries sejam usadas diretamente no editor:

| Recurso Cursor | Origem no framework |
|----------------|---------------------|
| **Rules** (`.mdc`) | Lexis e Codex — contexto injetado no agente |
| **Skills** (`SKILL.md`) | Katas e Warriors — capacidades sob demanda |
| **Commands** (`.md`) | Cries — comandos rápidos via `/cry-nome` |
| **Agents** (`.md`) | Warriors — subagentes especializados |

As regras são aplicadas automaticamente conforme o escopo do projeto; skills e commands ficam disponíveis no chat.

**Configuração por plataforma:** a transposição (qual Pilar vira qual recurso) e a aplicação das rules (alwaysApply, globs, description) são definidas no arquivo **`platforms.yaml`** (default em `framework/platforms.yaml`, override em `.ahrena/platforms.yaml`). Detalhes em [codex-platforms](framework/pt-BR/_foundation/process/codex/codex-platforms.md).

---

## Suporte ao Claude Code

O Ahrena oferece **suporte integrado ao Claude Code**. Com `--platform claude-code`, o instalador gera `.claude/` e `CLAUDE.md` a partir do `framework/`:

| Recurso Claude Code | Origem no framework |
|---------------------|---------------------|
| **Docs** (`.md`) | Lexis e Codex — documentação de referência injetada no contexto |
| **Skills** (`SKILL.md`) | Katas — procedimentos repetíveis sob demanda |
| **Commands** (`.md`) | Cries — comandos rápidos via `/cry-nome` |
| **Agents** (`.md`) | Warriors — subagentes especializados |
| **CLAUDE.md** | Lexis essenciais injetadas diretamente no contexto da sessão |

A configuração `claude-code.docs` no `platforms.yaml` controla quais artefatos são injetados diretamente no `CLAUDE.md` (`essential: true`) versus listados como referência (`essential: false`).

## Suporte ao OpenAI Codex

Com `--platform codex`, o Ahrena produz recursos nativos do OpenAI Codex sem depender da estrutura do Claude Code:

| Recurso Codex | Origem no Ahrena |
|---|---|
| Seção gerenciada em `AGENTS.md` | Contrato operacional essencial e roteamento do framework |
| `.codex/docs/lex/` | Lexis completas para consulta sob demanda |
| `.codex/docs/codex/` | Manuais de referência do pilar Ahrena Codex |
| `.agents/skills/<nome>/SKILL.md` | Katas e Cries, descobertos como skills do repositório |
| `.codex/agents/<nome>.toml` | Warriors como agentes especializados |

O instalador preserva todo conteúdo existente fora dos marcadores em `AGENTS.md`. A desinstalação remove apenas os recursos identificáveis do Ahrena e não apaga configurações Codex pertencentes ao projeto. Cries são projetadas como skills porque custom prompts são pessoais e o Codex recomenda skills para fluxos reutilizáveis e compartilhados.

---

## Validador de estrutura

O Ahrena inclui um validador para garantir que o conteúdo do framework segue as convenções antes de uma transposição.

```bash
# Validar tudo
make validate
# ou
python scripts/validate.py

# Validar checks específicos
python scripts/validate.py --check naming,platforms
```

| Check | O que valida |
|-------|-------------|
| `naming` | Todo `.md` começa com prefixo de Pilar ou é `README.md` |
| `path` | Arquivo está no diretório correto do Pilar (`lexis/`, `katas/`, etc.) |
| `sections` | Seções obrigatórias presentes (lei em Lexis, workflow em Kata, etc.) |
| `i18n` | Todo arquivo em `pt-BR/` tem correspondente em `en/` e `es/` |
| `platforms` | Todo `lex-` e `codex-` tem entrada em `cursor.rules` do `platforms.yaml` |

Exit code `0` = tudo passou; `1` = violações encontradas. Pode ser usado como pre-commit hook.
