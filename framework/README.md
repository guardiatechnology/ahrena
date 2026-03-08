# Framework — Guia do Desenvolvedor

🇺🇸 [English](README.en.md) | 🇪🇸 [Español](README.es.md)

> Guia prático para quem contribui com o repositório do Ahrena. Para uso do framework em projetos, consulte o [README principal](../README.md).

## Estrutura

```
framework/
├── .directives.sample           # Template de diretivas (copiado para .ahrena/.directives na instalação)
├── templates/                   # Templates base de cada Pilar
│   ├── lex-sample.md
│   ├── codex-sample.md
│   ├── kata-sample.md
│   ├── warrior-sample.md
│   └── cry-sample.md
│
├── pt-BR/                       # Idioma padrão (fonte da verdade)
│   ├── _foundation/
│   │   ├── authoring/           # Guias de criação de artefatos
│   │   ├── contributing/        # Fluxo de contribuição e commit
│   │   ├── process/             # Convenções de processo (checkpoints, diretivas)
│   │   ├── quality/             # Padrões mínimos de qualidade
│   │   ├── tooling/             # Automação (Makefile)
│   │   └── i18n/                # Estrutura de idiomas do framework
│   └── documentation/
│       └── i18n/                # Sistema de tradução (Hermes)
│
├── en/                          # Inglês (mesma estrutura)
└── es/                          # Espanhol (mesma estrutura)
```

O idioma padrão (`pt-BR`) é a **fonte da verdade**. Mudanças começam nele e são traduzidas para os demais idiomas via `/cry-translate`.

## Fluxo de Desenvolvimento

### 1. Editar artefatos no `framework/`

Edite os arquivos `.md` dentro de `framework/{lang}/`. Respeite:

- **Endereçamento:** `{lang}/{clade}/{subclade}/{pilar}/{prefixo}-{nome}.md`
- **Templates:** use os templates de `framework/templates/` como base (`lex-template-usage`)
- **i18n:** toda mudança no idioma padrão deve ser propagada para os demais idiomas

### 2. Testar localmente

Após editar, regenere a instalação local para validar que os artefatos Cursor são gerados corretamente:

```bash
make dev-install PLATFORM=cursor
```

Isso copia `framework/` para `.ahrena/framework/`, gera o `.cursor/` (rules, skills, commands, agents) e preserva o `.directives` existente.

### 3. Verificar artefatos gerados

O instalador transforma cada Pilar no formato nativo do Cursor:

| Pilar | Origem | Destino Cursor |
|-------|--------|----------------|
| Lexis | `framework/{lang}/.../lexis/lex-*.md` | `.cursor/rules/.../lex-*.mdc` |
| Codex | `framework/{lang}/.../codex/codex-*.md` | `.cursor/rules/.../codex-*.mdc` |
| Katas | `framework/{lang}/.../katas/kata-*.md` | `.cursor/skills/kata-*/SKILL.md` |
| Warriors | `framework/{lang}/.../warriors/warrior-*.md` | `.cursor/skills/warrior-*/SKILL.md` + `.cursor/agents/warrior-*.md` |
| Cries | `framework/{lang}/.../cries/cry-*.md` | `.cursor/commands/.../cry-*.md` |

O idioma usado para gerar os artefatos Cursor é definido por `language.cursor` no `.directives` (padrão: `en`).

### 4. Commitar

Use `/cry-commit` para criar commits conformes. As 4 Lexis de commit são:

- `lex-conventional-commits` — formato `type(scope): description`
- `lex-small-commits` — um propósito por commit
- `lex-commit-language` — subject em inglês
- `lex-signed-commits` — assinatura GPG obrigatória

### 5. Contribuir

Use `/cry-contribute pr` para abrir o Pull Request. O `kata-contribute` guia todo o fluxo via MCP.

## Criando Novos Artefatos

### Via comandos (recomendado)

```
/cry-new-lex          # Nova Lexis
/cry-new-codex        # Novo Codex
/cry-new-kata         # Novo Kata
/cry-new-warrior      # Novo Warrior
/cry-new-cry          # Novo Cry
```

Cada comando invoca o kata correspondente (`kata-create-*`) que:
1. Usa o template oficial como base
2. Posiciona o artefato na taxonomia correta
3. Cria nos 3 idiomas obrigatórios

### Manualmente

1. Copiar o template de `framework/templates/{pilar}-sample.md`
2. Posicionar em `framework/pt-BR/{clade}/{subclade}/{pilar}/{prefixo}-{nome}.md`
3. Preencher as seções obrigatórias
4. Traduzir para `en/` e `es/` (via `/cry-translate`)
5. Rodar `make dev-install PLATFORM=cursor` para validar

## Convenções

| Aspecto | Padrão |
|---------|--------|
| Casing de arquivos | `kebab-case` (`lex-no-secrets.md`) |
| Casing de diretórios | `kebab-case` (`engineering/backend/`) |
| Extensão no framework | `.md` |
| Extensão no Cursor | `.mdc` (rules), `.md` (skills, commands, agents) |
| Prefixos | `lex-`, `codex-`, `kata-`, `warrior-`, `cry-` |
| Clades reservados | `_foundation` (prefixo `_`) |

## Targets do Makefile

| Target | Descrição |
|--------|-----------|
| `make dev-install PLATFORM=cursor` | Instala usando fontes locais |
| `make bootstrap PLATFORM=cursor` | Primeira instalação (baixa do GitHub) |
| `make install PLATFORM=cursor` | Reinstala a partir de `.ahrena/install.py` |
| `make update` | Atualiza para última versão |
| `make clean` | Remove arquivos instalados |

## Referências

- [README principal](../README.md) — Documentação pública do Ahrena
- [Sistema de Tradução](pt-BR/documentation/i18n/README.md) — Documentação do Hermes
- `.ahrena/.directives` — Diretivas canônicas do framework
- `_foundation/contributing/codex/codex-contributing` — Fluxo de contribuição
- `_foundation/contributing/katas/kata-contribute` — Procedimento de PR
