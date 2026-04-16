# Codex: Aplicação do framework por plataforma (platforms.yaml)

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Transposição e aplicação dos artefatos do Ahrena em cada plataforma (Cursor, futuras)

## Visão Geral

Este Codex documenta o arquivo **`platforms.yaml`**, que define, por plataforma, **como os artefatos do framework são transpostos e aplicados**: qual Pilar vira qual recurso da plataforma (transposição) e com quais opções (alwaysApply, globs, description) cada artefato é gerado. O instalador e o sync (ex.: `python .ahrena/update.py --sync-cursor`) usam esse arquivo para gerar `.cursor/` (ou outra IDE) de forma controlada e otimizada.

## Contexto

- **Domínio:** Integração do Ahrena com plataformas (Cursor hoje; OpenAI, Claude, outras no futuro)
- **Público-alvo:** Mantenedores do framework, integradores e quem customiza a geração de artefatos por plataforma
- **Atualização:** Sempre que uma nova plataforma for suportada ou a política de aplicação (alwaysApply, globs) for alterada

## Conteúdo

### Localização do arquivo

| Origem | Caminho | Uso |
|--------|---------|-----|
| **Default (framework)** | `framework/platforms.yaml` | Enviado com o framework; copiado para `.ahrena/framework/platforms.yaml` na instalação |
| **Override (projeto)** | `.ahrena/platforms.yaml` | Opcional; o projeto pode sobrescrever ou estender o default |

O merge é feito pelo script de instalação/sync: primeiro carrega o default, depois aplica o override (por chave de plataforma e, dentro de `rules`, por rule key).

### Estrutura por plataforma

Cada plataforma tem uma chave de primeiro nível (ex.: `cursor`) com:

1. **`transposition`** — mapeamento Pilar Ahrena → recurso da plataforma  
   - Exemplo Cursor: `lex` → `rules`, `codex` → `rules`, `kata` → `skills`, `warrior` → `agents`, `cry` → `commands`
2. **Seções por recurso** (ex.: `rules`) — configuração de aplicação por artefato  
   - Para Cursor: em `rules`, cada chave é o **rule key** (caminho do artefato sem idioma e sem `.md`); o valor define `alwaysApply`, `globs` e `description`.

### Regra key (rule key)

O **rule key** identifica o artefato de forma invariante entre idiomas e plataformas:

- Caminho relativo ao framework **sem** o segmento de idioma e **sem** `.md`  
- Ex.: `en/_foundation/process/lexis/lex-directives.md` → `_foundation/process/lexis/lex-directives`

### Política padrão (Cursor)

- **Default para todas as rules:** `alwaysApply: false`; **description** sempre presente (definida no YAML ou derivada do corpo do artefato), para o Cursor aplicar a rule de forma inteligente.
- **Exceções com `alwaysApply: true`** (definidas no `platforms.yaml`): ex.: `lex-directives`, `lex-checkpoint`.

### Disciplina com `alwaysApply: true` / `essential: true`

Ambas as flags inflam o contexto base de toda sessão (rules Cursor com `alwaysApply: true` são sempre carregadas; docs Claude Code com `essential: true` são inlinadas em `CLAUDE.md`). Adicionar artefato com essas flags custa tokens de contexto em 100% das sessões, não só nas relevantes.

Regras:

1. **Default é sempre `false`.** Marcar `true` exige justificativa explícita no PR que introduz a mudança.
2. **PR que adiciona `alwaysApply: true` ou `essential: true` a Lexis/Codex DEVE incluir ADR** (via `kata-adr-write`) justificando por que o artefato é essencial o suficiente para viver no contexto base de toda sessão.
3. **Revisar candidatos periodicamente** (sugerido: a cada versão major do framework): o artefato ainda é lido na maioria das sessões? Se não → rebaixar para `false`.

### Subconjunto YAML suportado pelo parser customizado

O `scripts/install.py` traz um parser YAML stdlib-only intencionalmente restrito. O parser suporta:

- Chaves de topo com chaves aninhadas (indentação 2+ espaços).
- Valores escalares: strings (com ou sem aspas, escape `"` suportado), booleanos (`true`/`false` case-insensitive), inteiros.
- Mapas aninhados via indentação.
- Listas via entradas `- item` sob chave que declara lista.

O parser **NÃO** suporta:

- Anchors (`&anchor`) e aliases (`*alias`).
- Escalares multi-linha com `|` ou `>`.
- Flow-style (`[a, b]`, `{k: v}`).
- Strings entre aspas cruzando múltiplas linhas.

Se `platforms.yaml` ou `.directives` precisa de feature fora desse subset: ou (a) refatorar para ficar no subset, ou (b) instalar `pyyaml` opcional — `scripts/install.py` detecta automaticamente e usa quando disponível.

### Uso no sync Cursor

Ao rodar `python .ahrena/update.py --sync-cursor` (ou `make sync-cursor`):

1. O script carrega `platforms.yaml` (default + override).
2. Usa `cursor.transposition` para decidir o destino de cada Pilar (path e formato).
3. Usa `cursor.rules` para montar o frontmatter dos `.mdc` (alwaysApply, globs, description). Regras não listadas recebem default: alwaysApply false, description derivada do corpo.

## Referências

- **`lex-platforms-rules`** — obrigação de que todo Lexis e Codex tenha entrada em `cursor.rules` em `platforms.yaml` (com ao menos `description`); consultar ao criar ou publicar lex/codex
- `lex-directives` — obrigação de ler `.directives`; paths e convenções
- `codex-pilars` — sistema de Pilares e fluxo de criação
- Kata / Cry de sync-cursor (ex.: `kata-make-sync-cursor`, `cry-make`) — quando regenerar `.cursor/`
