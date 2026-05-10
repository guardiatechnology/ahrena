---
plan_id: "042"
title: "setup-preflight-and-mcp-transport-preference"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#81"
created_at: "2026-05-10T00:00:00Z"
updated_at: "2026-05-10T00:00:00Z"
---

# Plan: Setup preflight + MCP transport preference

## Objective

Eliminar a expectativa implícita de que o ambiente já tenha as ferramentas que o Ahrena exige. Garantir que `make bootstrap`/`install` falhe cedo com mensagem clara para hard requirements (Python, git, make) e ofereça instalar soft requirements (gh, gpg) via gerenciador nativo. **Codificar no framework (Lex + Codex) uma ordem de preferência de transporte MCP** — `HTTP remoto → binário nativo → npx → Docker` — e aplicar essa ordem aos servidores hoje declarados: GitHub e Notion migram para HTTP (zero dep local); Figma fica em npx por falta de HTTP/binário oficial, com Node instalado de forma lazy. A ordem governa também todo MCP futuro adicionado ao framework.

## Steps

- [x] **Step 1 — Issue + branch.** Abrir issue `feature-request` (template + label `feature request ➕` + assignee `@me` + type `Feature`) descrevendo Why/What/How (per `lex-issue-quality`). Criar worktree `.worktrees/{N}-setup-preflight-mcp-transport/` (per `lex-git-worktrees`) com branch `feat/{N}-setup-preflight-mcp-transport` (per `lex-git-branches`). **Done 2026-05-10**: issue #81 criada com label, type `Feature`, assignee, Why/What/How; worktree em `.worktrees/81-setup-preflight-mcp-transport/`, branch `feat/81-setup-preflight-mcp-transport`.
- [x] **Step 2 — Codificar a ordem de preferência de transporte no framework.** Atualizar **dois artefatos existentes**, replicados nas três línguas (`pt-BR`, `es`, `en`) por causa de `lex-framework-language`:
  - `framework/{lang}/_foundation/tooling/lexis/lex-mcp.md` — adicionar **Regra nova** "Preferência de transporte": ao declarar ou ativar um servidor MCP, o agente DEVE escolher o transporte na ordem:
    1. **HTTP remoto** (hosted pelo fornecedor) — quando o servidor oficial existir.
    2. **Binário nativo** stdio — quando o fornecedor publica binário oficial (ex.: `github-mcp-server`).
    3. **npx** (pacote npm) — quando só houver opção Node.
    Desvios DEVEM ser justificados em comentário (`_comment`) no JSON do servidor. Adicionar bloco `<HARD-GATE>` per `lex-hard-gate-pattern`? **Não** — é regra de preferência com desvio justificável, não bloqueio absoluto. Fica como Regra textual MUST.
  - `framework/{lang}/_foundation/tooling/codex/codex-mcp-common.md` — adicionar seção "Transport preference rationale" com tabela trade-offs (dep local, latência, atualização, controle de versão) pelos três degraus. Notar que Docker não está hoje na hierarquia oficial; quando um MCP em Docker aparecer, o degrau será reavaliado por ADR. Referenciar a Regra nova em `lex-mcp`.
  - Sincronizar `.claude/`/`.cursor/` rodando `python3 scripts/install.py --self --target . --platform claude-code` e `--platform cursor` (per memory reference).
- [x] **Step 3 — `scripts/preflight.py`.** Novo módulo. Funções:
  - `check_tool(name, version_flag=None, min_version=None)` → `(found: bool, version: str | None, path: str | None)`.
  - `detect_os()` → `"macos" | "linux-debian" | "linux-rhel" | "windows"`.
  - `install_tool(name, os_kind)` → roda `brew install`/`apt-get install`/`winget install`. Já existe precedente em `install.py:1781-1786` (rtk via brew); generalizar.
  - `run(level: Literal["hard","soft","mcp"], spec: list[ToolSpec]) → PreflightReport`. Imprime tabela `[ok|missing] tool ─ version ─ hint`. Hard `missing` → `sys.exit(1)`. Soft `missing` → pergunta interativa `install? [Y/n]` (skip em `--non-interactive`).
- [x] **Step 4 — Integrar preflight no `install.py`.** Em `main()` após parse_args, antes de Phase 1: chamar `preflight.run("hard", HARD_TOOLS)` e depois `preflight.run("soft", SOFT_TOOLS)`. Constantes `HARD_TOOLS=[git, make]` (python já checado), `SOFT_TOOLS=[gh, gpg]`. Adicionar flag `--skip-preflight` (paridade com `--skip-rtk`) e `--non-interactive`. **Done 2026-05-10**: helper `_run_preflight(args)` chamado após `parse_args`; flags adicionadas ao parser. Distribuição: `preflight.py` adicionado à lista de scripts copiados para `.ahrena/` (`scripts/install.py:1259`); cobertura parcial do Step 10 (mcp_enable.py será adicionado depois).
- [x] **Step 5 — Aplicar preferência ao `framework/mcp/github.json`** (degrau 1 — HTTP). Tanto Cursor quanto Claude Code usam o servidor remoto oficial em `https://api.githubcopilot.com/mcp/`. Bloco Cursor não muda (já é HTTP). Bloco Claude Code passa de `npx` para HTTP com `"type": "http"`. Interpolação de env var difere por plataforma: Cursor `${env:GITHUB_PAT}`, Claude Code `${GITHUB_PAT}` (doc oficial `code.claude.com/docs/en/mcp`). Adicionar `requires: []` em ambos.
  ```json
  {
    "cursor":      { "url": "https://api.githubcopilot.com/mcp/", "headers": {"Authorization": "Bearer ${env:GITHUB_PAT}"}, "requires": [] },
    "claude-code": { "type": "http", "url": "https://api.githubcopilot.com/mcp/", "headers": {"Authorization": "Bearer ${GITHUB_PAT}"}, "requires": [] }
  }
  ```
  **Sem arquivo de escape hatch versionado.** Reversão para npx fica documentada em `codex-mcp-github` (Step 11) — usuário copia/cola o bloco antigo no override de projeto (`.ahrena/mcp/github.json`) com `_comment` justificando o desvio, conforme a Regra do Step 2.
- [x] **Step 6 — Aplicar preferência ao `framework/mcp/notion.json`** (degrau 1 — HTTP). Tanto Cursor quanto Claude Code usam `https://mcp.notion.com/mcp`. Auth é via OAuth-por-usuário (browser flow na primeira chamada) em vez de `NOTION_API_KEY` compartilhado. Adicionar `requires: []`.
  ```json
  {
    "cursor":      { "url": "https://mcp.notion.com/mcp", "requires": [] },
    "claude-code": { "type": "http", "url": "https://mcp.notion.com/mcp", "requires": [] }
  }
  ```
  **Sem arquivo de escape hatch versionado.** Reversão para npx fica documentada em `codex-mcp-notion` (Step 11) — times que preferem `NOTION_API_KEY` compartilhado copiam o bloco antigo no override de projeto (`.ahrena/mcp/notion.json`) com `_comment` justificando. Documentar no PR a mudança de UX (OAuth per-user vs env var).
- [x] **Step 7 — `framework/mcp/figma.json` fica em npx + Node lazy** (degrau 3 — npx; sem HTTP/binário oficial). Anotar `requires: ["bin:node"]` nos dois blocos. Node passa a ser dep lazy: instalado só ao ativar o MCP via `make mcp-enable SERVER=figma`. Documentar no PR a alternativa Figma Dev Mode MCP local (`http://127.0.0.1:3845/sse`, exige Figma desktop) para usuários que prefiram esse caminho.
- [x] **Step 8 — `scripts/mcp_enable.py`.** Lê `framework/mcp/{server}.json`, resolve `requires` para a platform alvo (`--platform cursor|claude-code`), chama `preflight.run("mcp", ...)` para instalar deps faltantes (só Figma hoje), então merge no arquivo MCP do projeto (`.mcp.json` para Claude Code, `.cursor/mcp.json` para Cursor). Sub-comandos: `enable SERVER`, `disable SERVER`, `list`.
- [x] **Step 9 — Target `make mcp-enable SERVER=...` e `make mcp-list`.** Wrapper de `python3 .ahrena/mcp_enable.py`. Atualizar `make help`.
- [x] **Step 10 — Distribuir os novos scripts.** `scripts/preflight.py` e `scripts/mcp_enable.py` precisam ir para `.ahrena/` no install (assim como `install.py`/`update.py`/`uninstall.py` já vão). Olhar a função que copia scripts em `install.py` e adicionar os dois novos arquivos à lista.
- [ ] **Step 11 — Docs.** README (3 idiomas) ganha seção curta "Prerequisites" listando hard/soft/lazy. `codex-mcp-github` e `codex-mcp-notion` (3 línguas cada) documentam que Claude Code agora usa HTTP, e incluem snippet de override (`.ahrena/mcp/{server}.json` com bloco npx + `_comment`) para quem precisar do caminho antigo. `codex-mcp-figma` documenta a alternativa Dev Mode local. Sem novo Lexis — `lex-mcp` já cobre via Step 2.
- [ ] **Step 12 — Validação manual.**
  - `make bootstrap` em VM macOS clean → falha esperada se git ausente; oferece brew install em gh ausente; conclui **sem Node**.
  - `make mcp-enable SERVER=github` → grava `.mcp.json` com bloco HTTP. Zero deps instaladas.
  - `make mcp-enable SERVER=notion` → grava bloco HTTP. Zero deps. Primeira chamada do MCP dispara OAuth.
  - `make mcp-enable SERVER=figma` → detecta Node ausente, oferece instalar; grava config npx.
  - `make mcp-list` → mostra servidores conhecidos, transporte (`http`/`stdio-npx`) e estado (`enabled`/`available`/`missing-deps`).
- [ ] **Step 13 — PR.** `gh pr create` com `Closes #{N}`, espelhar labels da issue, size label, assignee `@me`, reviewer via CODEOWNERS. Per `lex-pr-quality`. Marcar como BREAKING change no body (mudanças nos blocos `claude-code` de `github.json` e `notion.json`, e auth Notion virou OAuth).

## Dependencies

- Nenhum outro plan bloqueante. Não toca em `lex-*` críticos além de adicionar referência em `codex-mcp-common` e `codex-mcp-github`.
- Depende de `gh` estar disponível na máquina do executor para abrir a issue (Step 1) — bootstrap por hand se necessário.

## Risks

- **Risco 1 — Breaking change no GitHub MCP do Claude Code.** Usuários hoje rodam `npx @modelcontextprotocol/server-github`; após o update vão usar HTTP remoto. Mitigação: documentar como BREAKING no PR + CHANGELOG; `codex-mcp-github` traz snippet pronto para override em `.ahrena/mcp/github.json` (desvio admitido pela Regra do Step 2).
- **Risco 2 — Breaking change no Notion MCP + mudança de auth.** Migração de `NOTION_API_KEY` env var compartilhado para OAuth-per-user. Times que dependiam de config compartilhada terão atrito. Mitigação: `codex-mcp-notion` traz snippet pronto para override em `.ahrena/mcp/notion.json` para quem precisa do caminho antigo; CHANGELOG explica a mudança de UX.
- **Risco 3 — PAT scopes do endpoint hosted da GitHub.** O `api.githubcopilot.com/mcp/` aceita PAT, mas talvez exija scopes diferentes do servidor npx. Mitigação: documentar exatamente quais scopes o PAT precisa após teste manual.
- **Risco 4 — `winget`/`apt-get` precisam de elevação.** O `install_tool` pode falhar silenciosamente em ambientes não-sudoers. Mitigação: capturar exit code e cair para "imprima este comando e rode você mesmo".
- **Risco 5 — `--non-interactive` em CI quebrar se uma soft dep faltar.** Mitigação: em non-interactive, soft missing → log de WARN, continua. Só hard bloqueia.
- **Risco 6 — Preflight rodando em `make sync-cursor` é ruído.** Mitigação: rodar preflight só em `bootstrap`/`install`/`update`, não em syncs.
- **Risco 7 — Indisponibilidade dos servidores remotos (GitHub/Notion).** Cair quando o endpoint estiver fora deixa o usuário sem MCP. Mitigação: Claude Code já faz retry exponencial (3 tentativas iniciais per doc); escape hatches `*-npx.json` documentados.
- **Risco 8 — Mudança em `lex-mcp` pode quebrar consumers externos do framework.** Adicionar regra nova é aditivo (não breaking), mas validações que pré-existam podem reclamar de configs antigas que não respeitam a ordem. Mitigação: a regra admite desvio justificado via `_comment` no JSON — usuários downstream não precisam migrar imediatamente.
