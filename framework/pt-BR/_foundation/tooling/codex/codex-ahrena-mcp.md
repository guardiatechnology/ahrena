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
  "command": "uvx",
  "args": ["ahrena-mcp"]
}
```

**Claude Code (`.mcp.json` no root do projeto + `enabledMcpjsonServers` em `.claude/settings.json`):**
```json
"ahrena": {
  "command": "uvx",
  "args": ["ahrena-mcp"]
}
```

> O comando `uvx ahrena-mcp` resolve o pacote publicado em PyPI sob demanda (zero-install). Pré-requisito: `uv` instalado no host (`brew install uv` no macOS, `pipx install uv` em outros ambientes). Antes da release v1, configure manualmente um `command` apontando para um Python que tenha `pip install -e <ahrena-repo>/tools/ahrena-mcp` aplicado (ver §Instalação interim).

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
pilar (string, opcional)    — "lexis" | "codex" | "katas" | "warriors" | "cries"; vazio = todos
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

#### Adoção padrão (default-on)

Toda nova adoção do framework Ahrena ativa `ahrena` automaticamente:

1. `framework/.directives.sample` lista `mcp.servers: [ahrena]` descomentado por padrão.
2. `scripts/install.py` mergeia `framework/mcp/ahrena.json` em `.cursor/mcp.json` e `.mcp.json` no root do projeto, e adiciona `ahrena` ao `enabledMcpjsonServers` em `.claude/settings.json`.
3. Adopter executa `make install` (ou equivalente) — pronto.

Para opt-out: comentar a linha `- ahrena` em `.ahrena/.directives` antes do install. Para desativar pós-install: remover `ahrena` de `enabledMcpjsonServers` (Claude Code) ou de `mcpServers` em `.cursor/mcp.json` e `.mcp.json` (ambas plataformas).

#### Instalação interim (pré-release)

Antes do release `v0.1.0a1` (ver `.claude/plans/plan-021-ahrena-mcp-server.md` §Release & Distribution), `uvx ahrena-mcp` falha porque o pacote ainda não está em PyPI. Workaround:

1. Clonar o repo Ahrena (já feito se você consome o framework).
2. `pip install -e <ahrena-repo>/tools/ahrena-mcp` no Python que será usado pelo MCP client.
3. Substituir, em `.ahrena/mcp/ahrena.json` (override local), o `command` por `python` e `args` por `["-m", "ahrena_mcp.server"]`.
4. Rodar `install.py` novamente para mergear o override.

Após release v1, esse passo desaparece — `uvx ahrena-mcp` resolve automaticamente.

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
- **Cache só por `mtime`** — edições concorrentes no framework durante uma sessão longa só são detectadas no próximo `get`.
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
