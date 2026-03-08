# Ahrena: AI-First Capability Framework

O **Ahrena** é um Capability Framework AI-first que estrutura conhecimento, processos e comportamento de agentes de IA através de uma **taxonomia unificada** aplicável a qualquer disciplina de negócio.

Leis inquebráveis (Lexis), bases de conhecimento (Codex), procedimentos repetíveis (Katas), agentes especializados (Warriors) e comandos recorrentes (Cries) são organizados por disciplina (Clade) e área de conhecimento (Subclade), criando um sistema extensível que orienta como humanos e IA colaboram em qualquer domínio.

### Princípios

1. **IA como Copiloto, não Piloto:** Humanos mantêm controle final sobre decisões críticas
2. **Processo sobre Ferramenta:** Padronização de processos tem prioridade sobre padronização de ferramentas
3. **Artefatos como Código:** Leis, manuais, procedimentos e comandos são versionados, auditáveis e portáveis
4. **Agnóstico de Plataforma:** `framework/` é a fonte da verdade; `.cursor/` e outras IDEs são derivações

---

## Instalação

### Pré-requisitos

- **Python 3.8+** — necessário para executar o instalador
- **Make** (opcional) — para bootstrap e atualizações via Makefile
  - **Windows:** `choco install make` ou `winget install GnuWin32.Make`
  - **macOS:** incluído com Xcode Command Line Tools (`xcode-select --install`)
  - **Linux:** incluído na maioria das distros (`sudo apt install make`)

### Primeira instalação

O instalador baixa o framework do GitHub e configura o projeto. Não é necessário clonar o repositório.

#### Via Makefile (recomendado)

Baixe o `Makefile` para a raiz do projeto e use `make bootstrap`. O Makefile pode ser commitado no repositório para que todo o time use o mesmo fluxo.

**macOS / Linux:**

```bash
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/Makefile -o Makefile
make bootstrap PLATFORM=cursor
```

**Windows (PowerShell):**

```powershell
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/Makefile -OutFile Makefile
make bootstrap PLATFORM=cursor
```

**Com opções:**

```bash
make bootstrap PLATFORM=cursor VERSION=v0.1.0 LANGUAGE=en
make bootstrap PLATFORM=cursor CLADES=_foundation,documentation
make bootstrap  # somente framework, sem plataforma
```

#### Via one-liner (sem Make)

**macOS / Linux:**

```bash
# Somente framework (.ahrena/)
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 -

# Framework + Cursor IDE
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 - --platform cursor

# Versão específica + idioma padrão
curl -sSL https://github.com/guardiafinance/ahrena/releases/download/v0.1.0/install.py | python3 - --version v0.1.0 --language en --platform cursor

# Apenas clades específicos
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 - --clades _foundation,documentation --platform cursor
```

**Windows (PowerShell):**

```powershell
# Somente framework (.ahrena/)
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py; Remove-Item install.py

# Framework + Cursor IDE
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform cursor; Remove-Item install.py
```

### Atualização

O update detecta automaticamente a plataforma instalada e preserva o `.directives`:

**Via Makefile (raiz do projeto):**

```bash
make update
make update VERSION=v0.2.0
```

**Via Makefile (.ahrena/):**

```bash
make -f .ahrena/Makefile update
```

**Via script direto:**

```bash
# macOS / Linux
python3 .ahrena/update.py
python3 .ahrena/update.py --version v0.2.0

# Windows (PowerShell)
python .ahrena/update.py
python .ahrena/update.py --version v0.2.0
```

### Desinstalação

Remove todos os arquivos instalados pelo Ahrena (`.ahrena/` e arquivos gerados no `.cursor/` — rules, skills, commands e agents). Pede confirmação antes de remover.

**Via Makefile:**

```bash
make uninstall
```

**Via script direto:**

```bash
# macOS / Linux
python3 .ahrena/uninstall.py
python3 .ahrena/uninstall.py --force    # sem confirmação

# Windows (PowerShell)
python .ahrena/uninstall.py
python .ahrena/uninstall.py --force
```

### Opções

| Flag | Descrição |
|------|-----------|
| `--platform cursor` | Gerar `.cursor/` (rules, skills, commands, agents) |
| `--clades X,Y` | Instalar apenas os clades especificados (ex: `_foundation,documentation`) |
| `--version v0.1.0` | Versão específica (tag ou branch) |
| `--language en` | Sobrescrever idioma padrão no `.directives` |
| `--directives PATH` | Usar `.directives` customizado (caminho local ou URL) |
| `--target PATH` | Instalar em outro diretório |
| `--dry-run` | Mostrar o que seria feito sem alterar nada |
| `--clean` | Remover arquivos instalados pelo Ahrena |

> **Nota:** quando `--clades` é usado, a seleção é salva em `.ahrena/.installed-clades` e respeitada automaticamente pelo `update.py`. Para alterar os clades em um update, passe `--clades` novamente.

### O que é instalado

| Comando | `.ahrena/` | `.cursor/` |
|---------|------------|------------|
| Sem `--platform` | framework + directives + scripts + Makefile | — |
| `--platform cursor` | framework + directives + scripts + Makefile | rules, skills, commands, agents |

---

## Taxonomia

O Ahrena organiza conhecimento em **três níveis**:

```
Clade (disciplina) → Subclade (área) → Pilar (tipo de capacidade) → Capability (capacidade)
```

### Pilares

Pilares definem o **tipo** de cada capacidade. São cinco:

#### Lexis — Leis Inquebráveis

Restrições absolutas de segurança, qualidade ou processo que **nenhum agente — humano ou IA — pode violar**.

| Aspecto | Detalhe |
|---------|---------|
| **Natureza** | Restritiva e imperativa — define o que **nunca** pode acontecer ou que **sempre** deve acontecer |
| **Prefixo** | `lex-` |
| **Quando usar** | Quando há risco de violação de segurança, qualidade ou processo crítico |
| **Governança** | Sem exceções; validação automatizada sempre que possível |
| **Template** | [`framework/templates/lex-sample.md`](framework/templates/lex-sample.md) |

#### Codex — Manuais de Referência

Base de conhecimento estruturada que a IA consulta para tomar decisões contextualizadas.

| Aspecto | Detalhe |
|---------|---------|
| **Natureza** | Informativa e orientadora — define **como** o sistema funciona |
| **Prefixo** | `codex-` |
| **Quando usar** | Quando uma decisão, padrão ou convenção relevante precisa ser documentada |
| **Governança** | Atualizado a cada decisão relevante ou mudança estrutural; consultado por equipe e IA |
| **Template** | [`framework/templates/codex-sample.md`](framework/templates/codex-sample.md) |

#### Katas — Skills Repetíveis

Procedimentos que definem como agentes executam tarefas recorrentes de forma padronizada, com inputs, outputs e critérios de validação.

| Aspecto | Detalhe |
|---------|---------|
| **Natureza** | Procedimental — define **o que fazer** passo a passo |
| **Prefixo** | `kata-` |
| **Quando usar** | Quando uma tarefa recorrente precisa ser executada de forma padronizada |
| **Governança** | Critérios de validação verificados antes da entrega |
| **Template** | [`framework/templates/kata-sample.md`](framework/templates/kata-sample.md) |

#### Warriors — Agentes Especializados

Agentes de IA com identidade, escopo e responsabilidades definidos. Cada Warrior consulta Lexis, Codex e Katas relevantes.

| Aspecto | Detalhe |
|---------|---------|
| **Natureza** | Persona — define **quem** o agente é e como se comporta |
| **Prefixo** | `warrior-` |
| **Quando usar** | Quando um agente especializado com identidade e escopo definidos é necessário |
| **Governança** | Vincula Lexis, Codex e Katas; critérios claros de escalação para humano |
| **Template** | [`framework/templates/warrior-sample.md`](framework/templates/warrior-sample.md) |

#### Cries — Comandos Recorrentes

Atalhos de produtividade que automatizam tarefas repetitivas. Diferem dos Katas por serem invocações rápidas, não procedimentos completos.

| Aspecto | Detalhe |
|---------|---------|
| **Natureza** | Invocação — define um **atalho** rápido e reutilizável |
| **Prefixo** | `cry-` |
| **Quando usar** | Quando uma tarefa simples e repetitiva pode ser automatizada via comando rápido |
| **Governança** | Baixa complexidade (1-2 passos); invocado via `/cry-[nome]` no chat |
| **Template** | [`framework/templates/cry-sample.md`](framework/templates/cry-sample.md) |

---

### Clades e Subclades

**Clade** — Disciplina de negócio. Agrupa todo o conhecimento relevante a uma mesma disciplina.

**Subclade** — Área de conhecimento dentro da disciplina. Refina o escopo do Clade por especialidade.

#### Product

Gestão de produto, ciclo de vida e estratégia. Cobre desde a descoberta de oportunidades até a entrega contínua de valor ao usuário.

| Subclade | Foco |
|----------|------|
| Discovery | Pesquisa, validação de hipóteses e priorização |
| Strategy | Visão de produto, roadmap e métricas de sucesso |
| Analytics | Dados de uso, experimentação e insights |
| Delivery | Planejamento de releases, rollout e comunicação |

#### Engineering

Desenvolvimento, arquitetura e infraestrutura. Abrange todo o ciclo técnico — do código ao deploy — incluindo qualidade e segurança.

| Subclade | Foco |
|----------|------|
| Backend | APIs, serviços, lógica de negócio e integrações |
| Frontend | Interfaces, componentes e experiência do desenvolvedor |
| DevOps | CI/CD, infraestrutura como código e observabilidade |
| Security | Proteção de dados, autenticação e conformidade técnica |
| Quality | Testes, revisão de código e padrões de qualidade |

#### Finance

Gestão financeira, contábil e controladoria. Estrutura processos que exigem precisão, rastreabilidade e conformidade com normas fiscais e contábeis.

| Subclade | Foco |
|----------|------|
| Accounting | Lançamentos, conciliação e fechamento contábil |
| Treasury | Fluxo de caixa, pagamentos, recebimentos e gestão de liquidez |
| Controllership | Planejamento financeiro, orçamento, relatórios gerenciais e KPIs |

#### Operations

Processos operacionais e suporte. Garante que sistemas e equipes funcionem de forma estável e eficiente no dia a dia.

| Subclade | Foco |
|----------|------|
| Support | Atendimento, escalonamento e base de conhecimento |
| Infrastructure | Servidores, redes, capacidade e disaster recovery |
| Monitoring | Alertas, dashboards e resposta a incidentes |

#### Documentation

Tradução, internacionalização e gestão de documentação técnica. Contém artefatos genéricos que se aplicam a qualquer tipo de documentação — do framework, de projetos ou de qualquer outro conteúdo técnico.

| Subclade | Foco |
|----------|------|
| i18n | Tradução multilíngue — regras por idioma, procedimentos, agente tradutor e comando |

> O Clade `documentation/i18n/` inclui o **Warrior Hermes** — um agente tradutor especialista que consulta regras e guias específicos de cada idioma-alvo (pt-BR, en, es) para garantir traduções precisas e consistentes. Para detalhes completos, veja o [README do Sistema de Tradução](framework/pt-BR/documentation/i18n/README.md).

#### _Foundation — Clade Transversal

_Foundation é um **Clade especial** que não pertence a uma disciplina específica. Seus artefatos atuam de forma **transversal**, aplicando-se a todos os demais Clades simultaneamente.

Enquanto Clades como Product ou Engineering contêm conhecimento específico de suas disciplinas, _Foundation define as **regras, processos e padrões que atravessam todas elas** — segurança global, qualidade mínima e processos comuns que todo agente e todo artefato devem respeitar, independentemente do domínio.

| Subclade | Foco |
|----------|------|
| Process | SDLC, fluxos de trabalho e convenções comuns a todas as disciplinas |
| Quality | Padrões mínimos de qualidade válidos para qualquer artefato |
| Security | Políticas de segurança aplicáveis a todo o sistema |
| i18n | Estrutura de pastas por idioma dentro de `framework/` — regras de navegação e espelhamento |

> Na prática: uma Lexis em `_foundation/security/` aplica-se a **todos** os Clades — não apenas a Engineering. Ao criar um artefato em qualquer Clade, o agente deve consultar _Foundation primeiro para garantir conformidade com as regras transversais.

---

> Clades e Subclades são **extensíveis**: cada organização cria os que fizerem sentido para o seu contexto.

### Warriors Disponíveis

Warriors são agentes especializados prontos para uso. O Ahrena inclui os seguintes Warriors built-in:

| Warrior | Nome | Clade | Descrição |
|---------|------|-------|-----------|
| `warrior-translator` | **Hermes** | `documentation/i18n` | Tradutor de documentação técnica. Consulta regras e guias específicos por idioma-alvo (pt-BR, en, es) para garantir traduções precisas. Invocável via `/cry-translate`. [Documentação completa](framework/pt-BR/documentation/i18n/README.md) |

#### Endereçamento

O idioma é sempre o primeiro segmento do caminho no framework:

```
{lang}/{clade}/{subclade}/{pilar}/{prefixo}-{nome}.md
```

| Caminho | Leitura |
|---------|---------|
| `pt-BR/_foundation/security/lexis/lex-security.md` | Lei de segurança transversal em pt-BR |
| `en/product/discovery/codex/codex-prioritization.md` | Manual sobre priorização em inglês |
| `es/engineering/security/lexis/lex-no-secrets.md` | Lei sobre secrets em espanhol |
| `pt-BR/documentation/i18n/warriors/warrior-translator.md` | Agente Hermes (tradutor) em pt-BR |
| `en/engineering/quality/warriors/warrior-spartacus.md` | Agente Spartacus em inglês |

#### Visualização

```
┌───────────────────────────────────────────────────────────────────┐
│                        TAXONOMIA AHRENA                           │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Clade               Subclade              Pilar                  │
│  ─────               ────────              ─────                  │
│                                                                   │
│  product/ ──────┬── discovery/ ──────────┬── lexis/               │
│                 ├── strategy/            ├── codex/               │
│                 ├── analytics/           ├── katas/               │
│                 └── delivery/            ├── warriors/            │
│                                          └── cries/               │
│  engineering/ ──┬── backend/                                      │
│                 ├── frontend/                                     │
│                 ├── devops/                                       │
│                 ├── security/                                     │
│                 └── quality/                                      │
│                                                                   │
│  finance/ ──────┬── accounting/                                   │
│                 ├── compliance/                                   │
│                 └── reporting/                                    │
│                                                                   │
│  operations/ ───┬── support/                                      │
│                 ├── infrastructure/                               │
│                 └── monitoring/                                   │
│                                                                   │
│  documentation/ ──── i18n/           Hermes (tradutor)            │
│                                                                   │
│  ═══════════════════════════════════════════════════════          │
│  _foundation/ ──┬── process/        ← aplica-se a TODOS           │
│   (transversal) ├── quality/          os Clades acima             │
│                 ├── security/                                     │
│                 └── i18n/                                         │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Estrutura do Repositório

### `.ahrena/`

Ponto de entrada canônico do framework. Todo projeto que adota o Ahrena **DEVE** ter este diretório na raiz do repositório. Contém as diretivas globais que governam o comportamento de todos os agentes.

```
.ahrena/
├── .directives          # Configurações canônicas (idioma, nomenclatura, paths)
```

### `framework/`

Templates e artefatos em `.md` puro, agnóstico de plataforma. O **idioma é o primeiro nível de navegação** — cada pasta de idioma contém a árvore completa de Clades, Subclades e Pilares:

```
framework/
├── .directives.sample
│
├── templates/                          # Templates (modelos base de cada Pilar)
│   ├── lex-sample.md
│   ├── codex-sample.md
│   ├── kata-sample.md
│   ├── warrior-sample.md
│   └── cry-sample.md
│
├── pt-BR/                              # Idioma padrão (fonte da verdade)
│   │
│   │   # Artefatos por Clade → Subclade → Pilar
│   ├── _foundation/
│   │   ├── process/lexis/lex-*.md
│   │   ├── quality/lexis/lex-*.md
│   │   └── i18n/
│   │       ├── lexis/lex-framework-language.md
│   │       └── codex/codex-framework-language.md
│   │
│   └── documentation/i18n/             # Sistema de tradução
│       ├── README.md                   # Documentação completa
│       ├── lexis/
│       │   ├── lex-language.md         # Regras transversais
│       │   ├── lex-language-ptbr.md    # Regras para pt-BR
│       │   ├── lex-language-en.md      # Regras para en
│       │   └── lex-language-es.md      # Regras para es
│       ├── codex/
│       │   ├── codex-language.md       # Guia transversal
│       │   ├── codex-language-ptbr.md
│       │   ├── codex-language-en.md
│       │   └── codex-language-es.md
│       ├── katas/kata-translate.md     # Procedimento (6 passos)
│       ├── warriors/warrior-translator.md  # Hermes
│       └── cries/cry-translate.md      # Comando rápido
│
├── es/                                 # Espanhol (mesma estrutura)
│   └── ...
└── en/                                 # Inglês (mesma estrutura)
    └── ...
```

Para criar um novo artefato: copie o template correspondente de `framework/templates/` (ex: `lex-sample.md`), coloque-o no Clade/Subclade adequado e preencha os campos `[]`. O artefato **DEVE** existir em todos os idiomas de `language.i18n` — use `/cry-translate` para gerar as traduções.

### De-Para: `framework/` → `.cursor/`

Ao implementar no Cursor, cada Pilar é mapeado para o recurso nativo correspondente. Cada recurso Cursor tem seu próprio formato:

| Pilar | Recurso Cursor | Formato | Destino |
|-------|----------------|---------|---------|
| **Lexis** | Rules | `.mdc` | `.cursor/rules/<clade>/<subclade>/lex-*.mdc` |
| **Codex** | Rules | `.mdc` | `.cursor/rules/<clade>/<subclade>/codex-*.mdc` |
| **Katas** | Skills | `SKILL.md` | `.cursor/skills/kata-*/SKILL.md` |
| **Warriors** | Skills + Agents | `SKILL.md` + `.md` | `.cursor/skills/warrior-*/SKILL.md` + `.cursor/agents/warrior-*.md` |
| **Cries** | Commands | `.md` | `.cursor/commands/<clade>/<subclade>/cry-*.md` |

**Formatos nativos do Cursor:**

| Recurso | Extensão | Frontmatter | Descrição |
|---------|----------|-------------|-----------|
| Rules | `.mdc` | `description` + `alwaysApply` | Contexto injetado no agente principal |
| Skills | `SKILL.md` | `name` + `description` | Capacidades que o agente adota sob demanda |
| Commands | `.md` | `description` | Slash commands invocáveis via `/nome` |
| Agents | `.md` | `name` + `description` | Subagentes isolados com system prompt próprio |

> Warriors geram **dois artefatos**: um Skill (o agente principal adota a persona) e um Agent (subagente isolado delegado via Task). Isso permite tanto uso inline quanto delegação.

```
.cursor/
├── rules/                              # .mdc — Lexis + Codex
│   ├── samples/
│   │   ├── lex-sample.mdc
│   │   └── codex-sample.mdc
│   ├── _foundation/
│   │   ├── process/lex-*.mdc
│   │   ├── quality/lex-*.mdc
│   │   └── i18n/
│   │       ├── lex-framework-language.mdc
│   │       └── codex-framework-language.mdc
│   └── documentation/i18n/
│       ├── lex-language.mdc
│       ├── lex-language-ptbr.mdc
│       ├── lex-language-en.mdc
│       ├── lex-language-es.mdc
│       ├── codex-language.mdc
│       ├── codex-language-ptbr.mdc
│       ├── codex-language-en.mdc
│       └── codex-language-es.mdc
│
├── skills/                             # SKILL.md — Katas + Warriors
│   ├── kata-sample/SKILL.md
│   ├── warrior-sample/SKILL.md
│   ├── kata-translate/SKILL.md
│   └── warrior-translator/SKILL.md
│
├── commands/                           # .md — Cries
│   ├── samples/cry-sample.md
│   └── documentation/i18n/
│       └── cry-translate.md
│
└── agents/                             # .md — Warriors (subagentes)
    └── warrior-translator.md
```
