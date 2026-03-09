# Ahrena: AI-First Capability Framework

O **Ahrena** é um Capability Framework AI-first que estrutura conhecimento, processos e comportamento de agentes de IA através de uma **taxonomia unificada** (Clade → Subclade → Pilar). Lexis, Codex, Katas, Warriors e Cries são organizados por disciplina e área, orientando como humanos e IA colaboram em qualquer domínio.

**Princípios:** IA como copiloto (não piloto); processo sobre ferramenta; artefatos versionados como código; `framework/` como fonte da verdade, agnóstico de plataforma.

---

## Instalação

### Pré-requisitos

- **Python 3.8+** — necessário para o instalador
- **Make** (opcional) — para bootstrap e atualizações
  - **Windows:** `choco install make` ou `winget install GnuWin32.Make`
  - **macOS:** Xcode Command Line Tools (`xcode-select --install`)
  - **Linux:** na maioria das distros já incluso (`sudo apt install make`)

### Plataformas

| Nome | Descrição |
|------|------------|
| **Cursor** | IDE com suporte integrado: o instalador gera `.cursor/` (rules, skills, commands, agents) a partir do framework. [Suporte ao Cursor](#suporte-ao-cursor) |

### Primeira instalação

O instalador baixa o framework do GitHub e configura o projeto (não é necessário clonar o repositório).

**Via Makefile (recomendado):**

```powershell
# Windows (PowerShell)
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/Makefile -OutFile Makefile
make bootstrap PLATFORM=cursor
```

```bash
# macOS / Linux
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/Makefile -o Makefile
make bootstrap PLATFORM=cursor
```

**Via one-liner (sem Make):**

```powershell
# Windows — somente framework
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py; Remove-Item install.py

# Windows — framework + Cursor IDE
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform cursor; Remove-Item install.py
```

```bash
# macOS / Linux — framework + Cursor
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 - --platform cursor
```

**Opções do instalador:**

| Flag | Descrição |
|------|------------|
| `--platform cursor` | Gerar `.cursor/` (rules, skills, commands, agents) |
| `--clades X,Y` | Instalar apenas clades especificados (ex.: `_foundation,documentation`) |
| `--version v0.1.0` | Versão específica (tag ou branch) |
| `--language en` | Sobrescrever idioma padrão no `.directives` |
| `--directives PATH` | Usar `.directives` customizado (caminho local ou URL) |
| `--target PATH` | Instalar em outro diretório |
| `--dry-run` | Simular sem alterar nada |
| `--clean` | Remover arquivos instalados pelo Ahrena |

Quando `--clades` é usado, a seleção é salva em `.ahrena/.installed-clades` e respeitada pelo `update.py`.

### Atualização e desinstalação

| Ação | Makefile | Script direto |
|------|----------|----------------|
| **Atualizar** | `make update` ou `make update VERSION=v0.2.0` | `python .ahrena/update.py` |
| **Desinstalar** | `make uninstall` | `python .ahrena/uninstall.py` (ou `--force` sem confirmação) |

**Desenvolvimento local (contribuidores):** `make dev-install PLATFORM=cursor` — usa os fontes locais de `framework/` em vez de baixar do GitHub.

### O que é instalado

| Comando | `.ahrena/` | `.cursor/` |
|---------|------------|------------|
| Sem `--platform` | framework, directives, scripts, Makefile | — |
| `--platform cursor` | idem | rules, skills, commands, agents |

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
| **engineering** | platform, backend, frontend, devops, security, quality | [Platform (Guardia)](framework/pt-BR/engineering/platform/README.md) |
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

Para a arquitetura do framework (paths, diagramas, de-para com `.cursor/`), consulte o [Guia do Desenvolvedor](./framework/pt-BR/README.md#arquitetura-do-framework).

---

## Suporte ao Cursor

O Ahrena oferece **suporte integrado ao Cursor IDE**. Com `--platform cursor` (ou `PLATFORM=cursor` no Makefile), o instalador gera o diretório `.cursor/` a partir do `framework/`, permitindo que as Lexis, Codex, Katas, Warriors e Cries sejam usadas diretamente no editor:

| Recurso Cursor | Origem no framework |
|----------------|---------------------|
| **Rules** (`.mdc`) | Lexis e Codex — contexto injetado no agente |
| **Skills** (`SKILL.md`) | Katas e Warriors — capacidades sob demanda |
| **Commands** (`.md`) | Cries — comandos rápidos via `/cry-nome` |
| **Agents** (`.md`) | Warriors — subagentes especializados |

As regras são aplicadas automaticamente conforme o escopo do projeto; skills e commands ficam disponíveis no chat. Para instalar com Cursor, use `make bootstrap PLATFORM=cursor` ou `python install.py --platform cursor`.
