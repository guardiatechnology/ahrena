# Codex: Servidor MCP do Ahrena

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Servidor MCP interno do framework Ahrena para Cursor e Claude Code

## Visão Geral

Este Codex é a referência do **servidor MCP `ahrena`** — o servidor interno do framework que expõe Lexis, Codex, Katas, Warriors e Cries como ferramentas consultáveis (read-only) por qualquer cliente MCP. Diferente de `github`/`notion`/`figma` (integrações externas opt-in), o `ahrena` é **default-on**: já vem ativo em todo projeto que adota Ahrena. Consultado por agentes que precisam consumir o framework de forma cirúrgica (sem carregar arquivos inteiros) ou por agentes externos sem acesso a `.claude/`/`.cursor/` (Strands, automações, scripts).

## Contexto

- **Domínio:** Consulta read-only ao framework Ahrena (artefatos de Lexis, Codex, Katas, Warriors, Cries) e leitura de `.ahrena/.directives`.
- **Público-alvo:** Agentes IA do Cursor e Claude Code; agentes externos (Strands, `apollo-agents`); scripts que precisam ler o framework programaticamente.
- **Atualização:** Quando novas ferramentas forem adicionadas ao servidor (mutação no contrato de tools); quando o canal de distribuição mudar (release v1 GitHub Release → v2 PyPI).

## Conteúdo

### Configuração por plataforma

A configuração canônica está em `framework/mcp/ahrena.json`. O `install.py` mergeia ela em:

**Cursor (`.cursor/mcp.json`):**
```json
"ahrena": {
  "command": "ahrena-mcp",
  "args": ["--root", "${workspaceFolder}"]
}
```

**Claude Code (`.mcp.json` no root do projeto + `enabledMcpjsonServers` em `.claude/settings.json`):**
```json
"ahrena": {
  "command": "ahrena-mcp",
  "args": ["--root", "${workspaceFolder}"]
}
```

> O comando `ahrena-mcp` é o console script declarado em `tools/ahrena-mcp/pyproject.toml` (`[project.scripts]`). Ele fica disponível em `PATH` após o `install.py` rodar `pipx install -e .ahrena/tools/ahrena-mcp` (ver §Instalação). Não há dependência de PyPI nem de `uv`/`uvx` para o caminho default-on funcionar.

### Ferramentas disponíveis

| Ferramenta | Descrição |
|---|---|
| `ahrena_query_lex` | Retorna o markdown completo de uma Lexis (e.g., `lex-idempotency`) |
| `ahrena_get_codex` | Retorna o markdown completo de um Codex (e.g., `codex-restful-apis`) |
| `ahrena_list_warriors` | Lista warriors; filtro opcional por `clade` (e.g., `engineering`) |
| `ahrena_list_cries` | Lista cries (slash commands) registradas no framework |
| `ahrena_search` | Busca ranqueada em todo o framework; filtros por `pilar` e `lang` |
| `ahrena_resolve_ref` | Verifica se um ref existe (e.g., `lex-idempotency`); fallback cross-language |
| `ahrena_get_directives` | Retorna `.ahrena/.directives` parseado |

### Parâmetros das ferramentas

**`ahrena_query_lex`**
```
name (string, obrigatório) — nome curto da Lex (e.g., "lex-idempotency")
lang (string, opcional)    — código BCP 47; default: language.default em .directives
```

**`ahrena_get_codex`**
```
name (string, obrigatório) — nome curto do Codex
lang (string, opcional)    — default: language.default em .directives
```

**`ahrena_list_warriors`**
```
clade (string, opcional)   — filtro por clade (e.g., "engineering"); vazio = sem filtro
lang  (string, opcional)   — default: language.default
```

**`ahrena_list_cries`**
```
lang (string, opcional)    — default: language.default
```

**`ahrena_search`**
```
query (string, obrigatório) — termo de busca
pilar (string, opcional)    — "lexis" \| "codex" \| "katas" \| "warriors" \| "cries"; vazio = todos
lang  (string, opcional)    — default: language.default
limit (integer, opcional)   — default: 30
```

Saída: lista ranqueada por número de matches no arquivo, com `artifact`, `pilar`, `lang`, `path`, `line`, `snippet`, `score`.

**`ahrena_resolve_ref`**
```
ref  (string, obrigatório) — nome curto (e.g., "lex-idempotency")
lang (string, opcional)    — default: language.default
```

Saída: `{exists, name, pilar, lang, path}`. Quando o ref existe em outra língua mas não na solicitada, retorna o resultado com chave `warning` indicando o fallback.

**`ahrena_get_directives`**
Sem parâmetros. Retorna o YAML parseado de `.ahrena/.directives`.

### Quando usar (e quando não)

**Use as ferramentas do `ahrena` quando:**
- O agente precisa consultar **uma** Lexis ou Codex específico no meio da sessão (sem inflar contexto via `@` import do arquivo inteiro).
- O agente precisa fazer busca cross-pilar (`circuit breaker` em qualquer artefato; ranking por score).
- O agente é externo ao Cursor/Claude Code e não tem acesso aos arquivos espelhados em `.cursor/`/`.claude/` (e.g., Strands, scripts CI, `apollo-agents`).
- O agente precisa resolver um ref de forma determinística (`lex-idempotency` existe? em qual path?).

**NÃO use o `ahrena` para:**
- Carregar **muitos** artefatos de uma vez — leitura direta de filesystem é mais eficiente.
- Mutar artefatos do framework. O servidor é read-only por design (write tools `ahrena_create_lex` etc. estão fora de escopo na primeira iteração).
- Substituir as Lexis com `alwaysApply: true` que o Cursor/Claude Code carregam no boot — essas continuam sendo o mecanismo nativo de governança eager.

### Instalação

#### Adoção padrão (default-on, via `install.py`)

Toda adoção do framework Ahrena ativa `ahrena` automaticamente. O `scripts/install.py` faz tudo:

1. **Copia o source do pacote** — `tools/ahrena-mcp/` (do source repo Ahrena) é copiado para `.ahrena/tools/ahrena-mcp/` no projeto adopter, sem `.venv` nem caches.
2. **Instala via `pipx`** — `pipx install -e .ahrena/tools/ahrena-mcp`. O console script `ahrena-mcp` (declarado em `pyproject.toml`) fica disponível em `PATH`.
3. **Mergeia configs MCP** — `framework/mcp/ahrena.json` é mergeado em `.cursor/mcp.json` (Cursor) e `.mcp.json` no root + `enabledMcpjsonServers: ["ahrena"]` em `.claude/settings.json` (Claude Code).
4. **Pré-requisito ativador** — `framework/.directives.sample` lista `mcp.servers: [ahrena]` descomentado por padrão; quando `ahrena` está em `mcp.servers`, os passos acima rodam.

Adopter roda `make install` (ou equivalente `python3 .ahrena/install.py`) — pronto. Após reinício do cliente MCP (Claude Code/Cursor), as 7 ferramentas `ahrena_*` aparecem.

**Comportamento em re-install / update:**
- Primeira vez (não-instalado): `pipx install` silencioso.
- Pacote já instalado + sessão interativa: prompt `[y/N]` para reinstalar (default-no, preserva).
- Pacote já instalado + não-TTY (CI): preserva sem prompt.

**Opt-out:** comentar a linha `- ahrena` em `.ahrena/.directives` antes do install. Para desativar pós-install: rodar `scripts/uninstall.py` (que chama `pipx uninstall ahrena-mcp` best-effort) ou remover `ahrena` de `enabledMcpjsonServers` no `.claude/settings.json` + de `mcpServers` em `.cursor/mcp.json` e `.mcp.json`.

#### Quando `pipx` não está disponível

`install.py` detecta a ausência de `pipx` no `PATH`, imprime `WARNING` no `stderr` com o link de instalação ([pipx.pypa.io](https://pipx.pypa.io/stable/installation/)), e segue (não-fatal). Caminhos para destravar:

1. **Instalar pipx e re-rodar `install.py`** (recomendado): `brew install pipx` (macOS), `python3 -m pip install --user pipx` + `python3 -m pipx ensurepath` (Linux/Windows).
2. **Instalar manualmente sem pipx**: `pip install --user .ahrena/tools/ahrena-mcp` e ajustar `PATH` para incluir `~/.local/bin` (Linux/macOS) ou `%APPDATA%\Python\Scripts` (Windows). O `command: ahrena-mcp` em `.mcp.json` continua válido.

#### Adopter externo sem framework instalado (após release)

Para agentes ou scripts que **não** rodam o `install.py` (Strands em projeto não-Ahrena, CI ad-hoc), ver `.claude/plans/plan-021-ahrena-mcp-server.md` §Release & Distribution. Após release v1 (PyPI), o caminho recomendado é `uvx ahrena-mcp --root <repo-ahrena>` (zero-install) ou `pipx install ahrena-mcp` (persistente). Pré-release, `pipx install --spec <github-release-url> ahrena-mcp`.

### Performance

Medições no spike (759 artefatos × 3 idiomas):

| Operação | Latência típica |
|---|---|
| Boot do server (cold) | ~1.0 s (Python + imports + scan inicial) |
| Boot subsequente em sessão (cache quente) | < 50 ms |
| `ahrena_query_lex` (cache hit) | < 1 ms |
| `ahrena_search` (com `ripgrep`) | 80–100 ms |
| `ahrena_search` (fallback Python regex) | 200–500 ms |

Recomendação: instalar `ripgrep` no host (`brew install ripgrep`) para o caminho rápido. Sem ripgrep, o servidor cai automaticamente no fallback Python — funciona, mas mais lento em frameworks grandes.

### Discovery do `--root`

O servidor descobre o root do framework Ahrena na seguinte ordem:

1. Flag `--root <path>` na invocação.
2. Variável de ambiente `AHRENA_ROOT`.
3. Walk-up a partir de `cwd` procurando o diretório `.ahrena/`.

Quando o servidor sobe em um projeto Ahrena, o walk-up encontra `.ahrena/` automaticamente. Adopters que rodam o servidor de fora do projeto devem usar `--root` ou `AHRENA_ROOT`.

### Limitações conhecidas (spike inicial)

- **Sem `ahrena_get_topology`** até `docs/internal/warrior-topology-2026.md` existir (depende de plan-011).
- **Cache só por `mtime` em arquivos já indexados** — `loader.get()` re-scaneia quando `mtime` muda, mas **não detecta arquivos novos nem deleções** durante uma sessão longa do server (o índice é construído no boot e atualizado por arquivo individual). Em prática isso raramente importa (artefatos do framework mudam pouco intra-sessão); quando importar, reiniciar o cliente MCP recria o índice.
- **Sem parsing de frontmatter** — tools retornam markdown bruto. Filtragem por metadados (e.g., `alwaysApply: true`) é responsabilidade do consumer.
- **Search cross-language pode dedup parcial** — um termo presente em pt-BR e en aparece duas vezes na lista de hits (uma por idioma) quando `lang` não é especificado.

## Restrições

- **Read-only.** Mutação de Lexis/Codex/Katas/Warriors/Cries via MCP está fora de escopo. Para criar artefatos, use as Cries do framework (`/cry-new-lex`, `/cry-new-codex`, etc.).
- **Não substitui `lex-mcp`.** O servidor está sujeito a `lex-mcp` rule 3 (declarado em `mcp.servers`) — `.directives.sample` já cumpre.
- **Path absoluto pinado quebra ao mover o repo.** Quando usar override local com `command: python -m ahrena_mcp.server`, a venv onde o pacote está instalado deve permanecer no path acordado.

## Referências

- `lex-mcp` — Lexis que governa o uso de servidores MCP.
- `codex-mcp-common` — Padrões MCP compartilhados (autenticação via env vars, fallback).
- `framework/mcp/ahrena.json` — Configuração canônica mergeada pelo installer.
- `tools/ahrena-mcp/` — Código-fonte do servidor (no repo Ahrena).
- `tools/ahrena-mcp/README.md` — Manual técnico do pacote (instalação, smoke test).
- `tools/ahrena-mcp/CHANGELOG.md` — Histórico de mudanças do servidor.
- `.claude/plans/plan-021-ahrena-mcp-server.md` — Plan de implementação completo, incluindo §Release & Distribution.
