---
name: ""
overview: ""
todos: []
isProject: false
---

# Plano: Controle de aplicação de artefatos por plataforma (agnóstico)

## Objetivo

Controlar no Ahrena **como os artefatos do framework são aplicados em cada plataforma** (Cursor hoje; OpenAI, Claude, outros no futuro), com **nome e estrutura agnósticos**. O arquivo define duas coisas por plataforma: **(1) a regra de transposição (depara)** — qual Pilar vira qual recurso da plataforma — e **(2) como cada artefato é aplicado** (alwaysApply, globs, etc.) nesse recurso.

## Nome do arquivo

`**platforms.yaml`**

- Nome agnóstico; agrupa a configuração por plataforma (cursor, openai, claude, …).
- Localização:
  - **Default (framework):** `framework/platforms.yaml`
  - **Override (projeto):** `.ahrena/platforms.yaml`

## Regra de transposição (depara)

A **transposição** define o mapeamento **Pilar Ahrena → recurso da plataforma**. Hoje isso está hardcoded no script (ex.: em `install.py`, `PILAR_TO_CURSOR_RESOURCE`). Passa a ser definida no próprio `platforms.yaml`, por plataforma.

Para Cursor, o depara é:


| Pilar Ahrena | Recurso Cursor |
| ------------ | -------------- |
| lex          | rules          |
| codex        | rules          |
| kata         | skills         |
| warrior      | agents         |
| cry          | commands       |


Assim, Lexis e Codex viram **rules** (`.mdc` em `.cursor/rules/`), Katas viram **skills** (`.cursor/skills/…/SKILL.md`), Warriors viram **agents** (`.cursor/agents/…`), Cries viram **commands** (`.cursor/commands/…`). Outras plataformas podem definir outro depara (ex.: lex → system_prompt, codex → knowledge_base).

## Estrutura do arquivo

Cada plataforma tem: **(1) `transposition`** (pilar → recurso) e **(2) uma seção por recurso** com a aplicação (quando o recurso suportar). Para Cursor, a seção `rules` contém o mapa rule_key → **alwaysApply**, **globs** e **description**. A chave **description** é importante: o Cursor usa esse texto para aplicar a rule de forma inteligente (ex.: exibir quando a rule é relevante, ou decidir quando solicitá-la sob demanda).

### Política padrão (Cursor rules)

- **Default para todas as rules:** `alwaysApply: false` e **sempre incluir `description`** (o texto é usado pelo Cursor para aplicar a rule de forma inteligente). Todas as rules passam a ter description (definida no YAML ou derivada do corpo do artefato).
- **Exceções com `alwaysApply: true`** (carregadas em toda interação):
  - **lex-directives** — consulta obrigatória ao `.directives`; transversal a toda sessão.
  - **lex-checkpoint** — checkpoint de sessão; marcado como `true` por padrão (mesmo que o artefato ainda não esteja totalmente escrito).
- **lex-terminal-type** fica com `alwaysApply: false` e uma **description** que oriente o agente a decidir quando aplicar (ex.: "Ao executar ou propor comandos de shell, use o tipo de terminal definido em .ahrena/.directives (bash ou PowerShell). Consulte esta rule quando for rodar comandos ou gerar documentação com exemplos de terminal."). Assim o Cursor aplica a rule quando relevante (comandos, docs) em vez de sempre.

```yaml
# Platform-specific: transposition (Ahrena pilar -> platform resource) and application config.

cursor:
  transposition:
    lex: rules
    codex: rules
    kata: skills
    warrior: agents
    cry: commands

  # Default: alwaysApply false; description always present (so Cursor can apply rule intelligently).
  # Exceptions with alwaysApply true: lex-directives, lex-checkpoint.
  rules:
    _foundation/process/lexis/lex-directives:
      alwaysApply: true
      description: "Consulta obrigatória ao .directives. Todo agente deve ler .ahrena/.directives antes de produzir artefatos."
    _foundation/process/lexis/lex-checkpoint:
      alwaysApply: true
      description: "Checkpoint de sessão. Usado para salvar o contexto de uma sessão de trabalho com agentes IA."
    _foundation/tooling/lex-terminal-type:
      alwaysApply: false
      description: "Ao executar ou propor comandos de shell, use o tipo de terminal definido em .ahrena/.directives (bash ou PowerShell). Consulte esta rule quando for rodar comandos ou gerar documentação com exemplos de terminal."
    documentation/i18n/lex-language-ptbr:
      alwaysApply: false
      description: "Regras para tradução para pt-BR. Tradução de documentação técnica para pt-BR"
    engineering/platform/lex-auth:
      alwaysApply: false
      globs: ["**/openapi/**", "**/oas/**", "**/api/**"]
      description: "Autenticação e autorização em APIs Guardia. Acesso a APIs da plataforma"
  # Demais rules: sempre description (YAML ou derivada do corpo); alwaysApply false por padrão.
  # skills/commands: description sempre presente quando aplicável.

# openai:
#   transposition:
#     lex: system_rules
#     codex: context
#   ...
```

- `**transposition`:** obrigatório por plataforma (ou fallback para o hardcoded atual no script). Define destino (path + formato) de cada pilar.
- **Seções por recurso** (`rules`, `skills`, `commands` para Cursor): opcionais; quando existem, o script usa para montar frontmatter. Para **rules**, as chaves são **alwaysApply**, **globs** e **description**; **description** é usada pelo Cursor para aplicar a rule de forma inteligente (relevância, quando mostrar ou solicitar a rule). Se não for definida no YAML, o script pode derivar do corpo do artefato (como hoje).

## Regra key (invariante entre plataformas)

A identificação do artefato continua a mesma para todas as plataformas:

- **Rule key** = path relativo ao framework **sem** o segmento de idioma e **sem** `.md`:  
`{clade}/{subclade}/{pilar}/{prefix}-{name}`  
Ex.: `en/_foundation/process/lexis/lex-directives.md` → `_foundation/process/lexis/lex-directives`.

Assim, o mesmo key pode ser usado por Cursor (para gerar `.mdc`), e no futuro por OpenAI/Claude (para decidir inclusão, prioridade, etc.), mesmo que os parâmetros sob cada plataforma sejam diferentes.

## Merge default + override

- Carregar `framework/platforms.yaml` (após install: `.ahrena/framework/platforms.yaml`) como default.
- Carregar `.ahrena/platforms.yaml` como override (se existir).
- Merge por plataforma: para a plataforma ativa (ex.: `cursor`), entradas do override sobrescrevem as do default (por rule key). Outras plataformas não precisam ser alteradas pelo override se o projeto só usar Cursor.

## Uso no script (Cursor)

- Em `install.py`, ao gerar `.cursor/`:
  - Carregar config: `load_platforms_config(ahrena_dir)` (merge de `platforms.yaml` default + override).
  - **Transposição:** usar `config["cursor"]["transposition"]` para destino de cada pilar; fallback para o mapeamento hardcoded atual se ausente.
  - **Aplicação:** para artefatos que viram `rules`, ler `config["cursor"]["rules"]`. **Default** (regra não listada ou campos omitidos): `alwaysApply: false`, **description** sempre preenchida (do YAML ou derivada do corpo do artefato). Para regras listadas, usar alwaysApply/globs/description do YAML. A description é sempre escrita no frontmatter do `.mdc` para o Cursor aplicar a rule de forma inteligente.
  - Para skills/commands, usar as seções correspondentes quando existirem.

## Outras plataformas (futuro)

- Novas plataformas = nova chave de primeiro nível em `platforms.yaml` com `transposition` (e seções por recurso).
- Ex.: `openai` pode ter `transposition: { lex: system_rules, codex: context }` e depois `system_rules:`, `context:`, etc. O tooling dessa plataforma lê `config["openai"]` e aplica o depara + o esquema de aplicação.
- O mesmo arquivo concentra, por plataforma, **quem vira o quê** (transposição) e **como é aplicado** (config por recurso).

## Resumo


| Aspecto        | Decisão                                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Arquivo        | `platforms.yaml` (default em `framework/`, override em `.ahrena/`)                                                                                     |
| Por plataforma | `transposition` (pilar → recurso) + seções por recurso (ex.: `rules` com rule_key → alwaysApply, globs, **description**)                               |
| Script Cursor  | Lê `config["cursor"]`; usa `transposition` para path/formato; usa `rules` (incl. **description** para aplicação inteligente) para frontmatter dos .mdc |
| Default rules  | `alwaysApply: false`; **description** sempre presente (YAML ou derivada do corpo). Exceções com `true`: lex-directives, lex-checkpoint                 |
| Fallback       | Se `platforms.yaml` ou `cursor.transposition` não existir, usar mapeamento hardcoded atual                                                             |


## Arquivos a criar/alterar (resumo)

1. **Criar** `framework/platforms.yaml` com seção `cursor`: `transposition` e `rules`. **Padrão:** alwaysApply false, description sempre presente. **Sempre true:** lex-directives, lex-checkpoint. lex-terminal-type com false e description que oriente o agente. Demais rules com false + description (ou derivada do corpo).
2. **Alterar** `scripts/install.py`: carregar `platforms.yaml` (default + override); usar `cursor.transposition` para decidir destino de cada pilar (substituindo ou complementando `PILAR_TO_CURSOR_RESOURCE`); usar `cursor.rules` para build_frontmatter dos artefatos que viram rules.
3. **Documentar** no framework que transposição e aplicação por plataforma vêm de `platforms.yaml`; sync Cursor usa a chave `cursor` (transposition + rules).

Assim, o depara e a aplicação ficam definidos no Ahrena e replicados no Cursor (e futuramente noutras plataformas) a partir do mesmo arquivo.