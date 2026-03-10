# Codex: Caminhos Canônicos do Framework

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Uso de paths no framework Ahrena

## Visão Geral

Este Codex descreve os caminhos canônicos definidos na seção `paths` do `.ahrena/.directives`. Explica quando usar cada path, quando criar artefatos em `project_artifacts` em vez de no framework, e como os scripts de instalação e atualização usam esses caminhos. Consulte `lex-directives` para a obrigação de usar caminhos canônicos; consulte `codex-directives` para o significado de cada chave do `.directives`.

## Contexto

- **Domínio:** Paths do framework e fluxo projeto vs framework
- **Público-alvo:** Agentes de IA que criam ou referenciam artefatos; mantenedores e integradores
- **Atualização:** Quando novos paths forem adicionados ao `.directives` ou o fluxo projeto/framework mudar

## Conteúdo

### Paths principais

| Path | Onde existe | Uso |
|------|--------------|-----|
| `paths.root` | Em todo projeto que adota Ahrena | Raiz do framework no projeto — `.ahrena/`. Scripts (install, update, uninstall) e Makefile são copiados ou referenciados a partir daqui. |
| `paths.directives` | Dentro de `paths.root` | Arquivo `.ahrena/.directives`. Fonte da verdade para paths, language, terminal, naming. |
| `paths.templates` | No repositório do Ahrena (repo fonte) | Pasta `templates/` com lex-sample.md, codex-sample.md, etc. Usada pelo instalador e por agentes ao criar artefatos (via `paths.samples.*`). |
| `paths.framework` | No repositório do Ahrena | Pasta `framework/` com a árvore por idioma (pt-BR, es, en) e por clade/subclade/pilar. Em projeto consumidor, pode ser uma cópia em `.ahrena/framework/` após instalação. |
| `paths.project_artifacts` | No projeto que adota Ahrena | `.ahrena/artifacts/`. Artefatos criados aqui são específicos do projeto e podem ser validados antes de serem incorporados ao framework. |

### Paths de destino (especificações e documentação)

| Path | Uso |
|------|-----|
| `paths.oas` | Diretório onde colocar especificações OpenAPI e documento de API (ex.: `docs/oas`). Criado pelo agente ou pelo instalador se não existir. Katas e Warriors de design de API escrevem aqui. |
| `paths.events` | Diretório onde colocar documentação de eventos (CloudEvents) (ex.: `docs/events`). Criado pelo agente ou pelo instalador se não existir. |

### Paths dos templates (samples)

| Path | Conteúdo |
|------|----------|
| `paths.samples.lexis` | Template oficial de Lexis (ex.: `templates/lex-sample.md`) |
| `paths.samples.codex` | Template oficial de Codex |
| `paths.samples.katas` | Template oficial de Katas |
| `paths.samples.warriors` | Template oficial de Warriors |
| `paths.samples.cries` | Template oficial de Cries |

Ao criar um novo artefato, o agente deve carregar o template correspondente a partir do path definido em `.directives` (ou do valor padrão documentado em `codex-directives`). Em geral os paths são relativos ao repositório do framework (ex.: `templates/lex-sample.md`).

### Quando usar project_artifacts vs framework

| Situação | Onde criar | Justificativa |
|----------|------------|---------------|
| Artefato em validação; pode nunca ir para o framework | `paths.project_artifacts` | Iteração local sem poluir o framework canônico |
| Artefato estável aprovado para o repositório Ahrena | `paths.framework` (no repo do framework) | Faz parte da árvore compartilhada; deve existir em todos os idiomas de `language.i18n` |
| Contribuidor trabalhando no repo Ahrena | Diretamente em `framework/` no repo | Não usa `project_artifacts`; edita a árvore canônica |
| Consumidor que quer propor artefato ao framework | Criar em `project_artifacts`, depois usar `kata-push-to-framework` | Fluxo recomendado em `codex-pilars` |

### Uso pelos scripts

- **install.py / update.py:** leem `paths` (implícito ao ler `.directives`) para saber onde copiar framework, templates e onde gerar `.cursor/` quando `--platform cursor` é usado.
- **kata-push-to-framework:** copia de `paths.project_artifacts` para `paths.framework` (modo local) ou envia alterações para o repositório remoto do framework (modo remoto).

## Glossário

| Termo | Definição |
|-------|-----------|
| Caminho canônico | Path definido em `.ahrena/.directives` sob a seção `paths`; todos os agentes devem usá-lo ao referenciar ou criar artefatos |
| Projeto consumidor | Repositório que instalou o Ahrena (via install.py ou Makefile) e que pode ter `.ahrena/framework/` e `.ahrena/artifacts/` |
| Repo do framework | Repositório que contém a árvore canônica `framework/` e `templates/` |

## Referências

- `lex-directives` — Obrigação de usar caminhos canônicos
- `codex-directives` — Manual do arquivo `.directives` (seção paths)
- `codex-pilars` — Fluxo de artefatos no projeto e Push para o framework
- `.ahrena/.directives` — Fonte dos valores de paths
