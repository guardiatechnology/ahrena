# Codex: MCP — Padrões Comuns

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Padrões transversais para qualquer integração de servidor MCP (Model Context Protocol) — preâmbulo consumido por todas as referências `codex-mcp-{servidor}`

## Visão Geral

Este Codex centraliza os padrões conceituais e operacionais compartilhados por toda integração de servidor MCP no Ahrena (GitHub, Notion, Figma e qualquer novo servidor adicionado). Documentos individuais `codex-mcp-{servidor}` agora focam em ferramentas, parâmetros e exemplos específicos daquele servidor, delegando o preâmbulo comum para este arquivo. O objetivo é reduzir consumo de tokens quando múltiplos codexes MCP são referenciados na mesma operação e manter autenticação, configuração e fallback em sincronia entre servidores.

## Contexto

- **Domínio:** qualquer servidor MCP integrado em Cursor ou Claude Code.
- **Público-alvo:** Warriors e Katas que invocam ferramentas MCP; consultado junto ao codex específico do servidor.
- **Atualização:** quando o framework adiciona novo servidor MCP, introduz nova plataforma (além de Cursor/Claude Code), ou muda o padrão de auth.

## Conteúdo

### O que é MCP, brevemente

MCP (Model Context Protocol) expõe capacidades de sistemas externos (serviços de API) diretamente a agentes IA através de uma interface padronizada de ferramentas, com autenticação gerenciada pela plataforma (Cursor, Claude Code) e sem construção manual de chamadas de API. Cada ferramenta MCP aparece ao agente como uma chamada de função tipada.

### Padrão de configuração compartilhado

Cada servidor MCP é definido por um template JSON em `framework/mcp/<name>.json` com dois blocos de plataforma — `cursor` e `claude-code` — mesclados por `scripts/install.py` na config da respectiva plataforma:

```
.cursor/mcp.json          ← populado a partir do bloco "cursor"
.claude/settings.json     ← populado a partir do bloco "claude-code"
```

O merge é **aditivo**: entradas gerenciadas pelo usuário para outros servidores são preservadas; apenas servidores listados em `mcp.servers` em `.ahrena/.directives` são escritos/sobrescritos.

### Preferência de transporte — racional dos trade-offs

`lex-mcp` §5 estabelece a ordem obrigatória ao declarar um servidor MCP: **HTTP remoto → binário nativo → npx**. Cada degrau adiciona uma classe distinta de dependência local. Os trade-offs por degrau:

| Degrau | Dep. local | Latência | Atualização | Controle de versão | Quando preferir |
|---|---|---|---|---|---|
| HTTP remoto | nenhuma | rede + servidor hospedado | fornecedor (server-side) | fornecedor | default quando o fornecedor oferece endpoint oficial |
| Binário nativo stdio | executável instalado | stdio local | release versionado | usuário (escolhe a versão a instalar) | sem HTTP; o fornecedor publica binário oficial |
| npx | Node.js + cache npm | stdio local com overhead de Node | a cada execução (`npx -y`) | pacote npm | sem HTTP nem binário oficial |

**Por que HTTP é default:**
- Zero dependência local — o usuário não precisa instalar runtime nem binário; o servidor evolui sem release manual.
- Auth padronizada via header (`Authorization: Bearer ...`) ou OAuth-per-user, ambos aceitos pelas plataformas (Cursor e Claude Code).
- Falha exposta em status HTTP claro (401/403/429/5xx) com retry exponencial automático nos clients oficiais.

**Por que binário é segunda escolha:**
- Funciona offline e tem latência mínima (sem hop de rede).
- Oferece controle preciso de versão — útil quando o fornecedor introduz breaking changes em releases.
- Custo: usuário precisa instalar/atualizar manualmente (ou via gerenciador de pacotes).

**Por que npx fica por último:**
- Arrasta Node.js como dependência transitiva — runtime pesado para um único caso de uso.
- `npx -y` faz download/cache a cada execução fria (cold start), introduzindo latência inicial.
- Pacotes npm de terceiros podem ser arquivados ou comprometidos sem aviso (cadeia de suprimentos mais frágil que vendor-hosted).

Desvios à ordem (ex.: usar npx mesmo quando HTTP existe) **DEVEM** ser justificados em comentário (`_comment`) no JSON do servidor — ver exemplo abaixo. Justificativas comuns aceitáveis: necessidade de configuração compartilhada via env var (em vez de OAuth-per-user), ambiente air-gapped, dependência de feature presente apenas no degrau inferior.

```json
{
  "_comment": "Override: time prefere NOTION_API_KEY compartilhado em vez do OAuth-per-user do endpoint HTTP oficial. Decisão registrada em ADR-NN.",
  "cursor": {
    "command": "npx",
    "args": ["-y", "@notionhq/notion-mcp-server"],
    "env": { "NOTION_API_KEY": "${env:NOTION_API_KEY}" }
  }
}
```

Docker não está hoje na hierarquia. Quando um servidor MCP em Docker for adotado, seu degrau **DEVE** ser definido por ADR (decisão sobre overhead vs. isolamento).

### Autenticação — regra uniforme

Todas as credenciais de servidor MCP **DEVEM**:

1. Vir exclusivamente de variáveis de ambiente declaradas no template JSON.
2. Usar `${env:VAR_NAME}` no Cursor (MCP cuida da resolução) e `${VAR_NAME}` no Claude Code.
3. Nunca aparecer hardcoded em código, `.directives` ou qualquer artefato versionado (ver `lex-mcp`).

Nomes padrão de variáveis por servidor:

| Servidor | Env Var |
|---|---|
| GitHub | `GITHUB_PAT` |
| Notion | `NOTION_API_KEY` |
| Figma | `FIGMA_API_KEY` |

### Preferência sobre CLI

Conforme `lex-mcp`, quando um servidor MCP está **ativo** (listado em `mcp.servers`) E a ferramenta existe naquele servidor, o agente **DEVE** usar a ferramenta MCP em preferência a qualquer CLI equivalente (ex.: MCP `create_pull_request` sobre `gh pr create`). O codex específico do servidor lista as ferramentas disponíveis.

### Comportamento de fallback (comum)

Se o servidor MCP está indisponível no meio da operação (rede, auth expirada, ferramenta ausente):

1. Tentar novamente uma vez após breve backoff (o agente espera antes do retry; sem busy loop).
2. Se ainda falhar, o agente **DEVE** informar o usuário: qual servidor, qual ferramenta, erro observado.
3. Oferecer alternativas explícitas:
   - Usar o CLI equivalente (se disponível) rotulado como fallback.
   - Pausar o fluxo até o usuário restaurar conectividade.
   - Abortar a operação.
4. O agente **NÃO PODE** silenciosamente cair para CLI sem comunicar a indisponibilidade do MCP.

Ver `lex-mcp` §4 para a lei completa de fallback.

### Sinais comuns de falha

| Sintoma | Causa provável | Ação |
|---|---|---|
| 401 / 403 na primeira chamada | Env var ausente / expirada | Pedir ao usuário para definir/rotacionar a variável |
| 429 ou rate-limit explícito | Muitas chamadas | Back off, reduzir batch size, re-enfileirar |
| Timeout em toda chamada | Processo do servidor MCP não rodando | Reiniciar a plataforma (Cursor/Claude Code) ou checar logs de startup |
| "Tool not found" | Mismatch de versão ou servidor não listado em `mcp.servers` | Conferir config; atualizar pacote do servidor |

### Quando adicionar novo servidor MCP

1. Criar `framework/mcp/<name>.json` com blocos `cursor` e `claude-code`.
2. Adicionar `<name>` em `mcp.servers` em `.ahrena/.directives` quando pronto para uso.
3. Criar `codex-mcp-<name>.md` (específico do servidor: catálogo de ferramentas + parâmetros + exemplos); referenciar **este codex** para padrões comuns.
4. Atualizar exemplos em `lex-mcp` se o novo servidor introduz modelo de autenticação novo.
5. Se o servidor alimenta novo Kata, considerar um Kata somente-leitura primeiro (`kata-mcp-<name>-read`) antes de qualquer padrão de escrita.

## Referências

- `lex-mcp` — leis invioláveis sobre uso de ferramentas MCP
- `codex-mcp-github`, `codex-mcp-notion`, `codex-mcp-figma` — referências específicas por servidor
- [Model Context Protocol spec](https://modelcontextprotocol.io/)
