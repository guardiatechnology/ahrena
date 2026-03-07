# Ahrena: AI-First Capability Framework

O **Ahrena** é um Capability Framework AI-first que estrutura conhecimento, processos e comportamento de agentes de IA através de uma **taxonomia unificada** aplicável a qualquer disciplina de negócio.

Leis inquebráveis (Lexis), bases de conhecimento (Codex), procedimentos repetíveis (Katas), agentes especializados (Warriors) e comandos recorrentes (Cries) são organizados por disciplina (Clade) e área de conhecimento (Subclade), criando um sistema extensível que orienta como humanos e IA colaboram em qualquer domínio.

### Princípios

1. **IA como Copiloto, não Piloto:** Humanos mantêm controle final sobre decisões críticas
2. **Processo sobre Ferramenta:** Padronização de processos tem prioridade sobre padronização de ferramentas
3. **Artefatos como Código:** Leis, manuais, procedimentos e comandos são versionados, auditáveis e portáveis
4. **Agnóstico de Plataforma:** `framework/` é a fonte da verdade; `.cursor/` e outras IDEs são derivações

---

## Taxonomia

O Ahrena organiza conhecimento em **três níveis**:

```
Clade (disciplina) → Subclade (área) → Pilar (tipo de artefato) → artefato
```

### Pilares

Pilares definem o **tipo** de cada artefato. São cinco:

#### Lexis — Leis Inquebráveis

Restrições absolutas de segurança, qualidade ou processo que **nenhum agente — humano ou IA — pode violar**.

| Aspecto | Detalhe |
|---------|---------|
| **Natureza** | Proibitiva e imperativa — define o que **nunca** pode acontecer |
| **Prefixo** | `lex-` |
| **Exceções** | Nenhuma |
| **Validação** | Automatizada (SAST, pre-commit hooks, CI pipeline) |
| **Template** | [`framework/lexis/lex-sample.md`](framework/lexis/lex-sample.md) |

**Seções:** Propósito, Lei, Abrangência, Consequências de Violação, Exemplos, Validação Automatizada.

#### Codex — Manuais de Referência

Base de conhecimento estruturada que a IA consulta para tomar decisões contextualizadas.

| Aspecto | Detalhe |
|---------|---------|
| **Natureza** | Informativa e orientadora — define **como** o sistema funciona |
| **Prefixo** | `codex-` |
| **Atualização** | A cada ADR aprovado ou mudança arquitetural |
| **Público** | Desenvolvedores, Tech Lead e IA copiloto |
| **Template** | [`framework/codex/codex-sample.md`](framework/codex/codex-sample.md) |

**Seções:** Visão Geral, Contexto, Princípios, Padrões e Convenções, Decisões Vigentes, Restrições Técnicas, Glossário, Referências.

#### Katas — Skills Repetíveis

Procedimentos que definem como agentes executam tarefas recorrentes de forma padronizada, com inputs, outputs e critérios de validação.

| Aspecto | Detalhe |
|---------|---------|
| **Natureza** | Procedimental — define **o que fazer** passo a passo |
| **Prefixo** | `kata-` |
| **Ativação** | Condições explícitas (ex: "quando o usuário pede um ADR") |
| **Garantia** | Critérios de validação verificados antes da entrega |
| **Template** | [`framework/katas/kata-sample.md`](framework/katas/kata-sample.md) |

**Seções:** Objetivo, Quando Usar, Inputs, Workflow, Outputs, Exemplo de Execução, Restrições.

#### Warriors — Agentes Especializados

Agentes de IA com identidade, escopo e responsabilidades definidos. Cada Warrior consulta Lexis, Codex e Katas relevantes.

| Aspecto | Detalhe |
|---------|---------|
| **Natureza** | Persona — define **quem** o agente é e como se comporta |
| **Prefixo** | `warrior-` |
| **Composição** | Vincula Lexis (leis), Codex (conhecimento) e Katas (habilidades) |
| **Escalação** | Critérios claros para delegar decisão a humano |
| **Template** | [`framework/warriors/warrior-sample.md`](framework/warriors/warrior-sample.md) |

**Seções:** Identidade, Missão, Responsabilidades (faz/não faz), Consulta, Comportamento, Exemplo de Interação.

#### Cries — Comandos Recorrentes

Atalhos de produtividade que automatizam tarefas repetitivas. Diferem dos Katas por serem invocações rápidas, não procedimentos completos.

| Aspecto | Detalhe |
|---------|---------|
| **Natureza** | Invocação — define um **atalho** rápido e reutilizável |
| **Prefixo** | `cry-` |
| **Invocação** | Via `/cry-[nome]` no chat |
| **Complexidade** | Baixa (1-2 passos), ao contrário dos Katas (multi-passo) |
| **Template** | [`framework/cries/cry-sample.md`](framework/cries/cry-sample.md) |

**Seções:** Descrição, Uso, Parâmetros, Ações, Prompt Template, Exemplo de Invocação, Restrições.

---

### Clades e Subclades

**Clade** — Disciplina de negócio. Agrupa todo o conhecimento relevante a uma mesma disciplina.

**Subclade** — Área de conhecimento dentro da disciplina. Refina o escopo do Clade por especialidade.

| Clade | Descrição | Exemplos de Subclades |
|-------|-----------|----------------------|
| **Product** | Gestão de produto, ciclo de vida e estratégia | Discovery, Strategy, Analytics, Delivery |
| **Engineering** | Desenvolvimento, arquitetura e infraestrutura | Backend, Frontend, DevOps, Security, Quality |
| **Finance** | Gestão financeira, contábil e regulatória | Accounting, Compliance, Reporting |
| **Operations** | Processos operacionais e suporte | Support, Infrastructure, Monitoring |

> Clades e Subclades são **extensíveis**: cada organização cria os que fizerem sentido para o seu contexto.

#### Endereçamento

```
<clade>/<subclade>/<pilar>/<prefixo>-<nome>.md
```

| Caminho | Leitura |
|---------|---------|
| `product/discovery/codex/codex-prioritization.md` | Manual sobre priorização, na área Discovery da disciplina Product |
| `engineering/security/lexis/lex-no-secrets.md` | Lei sobre secrets, na área Security da disciplina Engineering |
| `product/delivery/katas/kata-release-notes.md` | Procedimento de release notes, na área Delivery de Product |
| `engineering/quality/warriors/warrior-spartacus.md` | Agente Spartacus, na área Quality de Engineering |
| `finance/compliance/cries/cry-audit-check.md` | Comando de audit check, na área Compliance de Finance |

#### Visualização

```
┌──────────────────────────────────────────────────────────────────┐
│                       TAXONOMIA AHRENA                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Clade              Subclade              Pilar                  │
│  ─────              ────────              ─────                  │
│                                                                  │
│  Product ──────┬── Discovery ──────────┬── Lexis                 │
│                ├── Strategy            ├── Codex                 │
│                ├── Analytics           ├── Katas                 │
│                └── Delivery            ├── Warriors              │
│                                        └── Cries                 │
│  Engineering ──┬── Backend                                       │
│                ├── Frontend                                      │
│                ├── DevOps                                        │
│                ├── Security                                      │
│                └── Quality                                       │
│                                                                  │
│  Finance ──────┬── Accounting                                    │
│                ├── Compliance                                    │
│                └── Reporting                                     │
│                                                                  │
│  Operations ───┬── Support                                       │
│                ├── Infrastructure                                │
│                └── Monitoring                                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Estrutura do Repositório

### `framework/` — Fonte da verdade

Templates e artefatos em `.md` puro, agnóstico de plataforma:

```
framework/
│
│   # Templates (modelos base de cada Pilar)
├── lexis/lex-sample.md
├── codex/codex-sample.md
├── katas/kata-sample.md
├── warriors/warrior-sample.md
├── cries/cry-sample.md
│
│   # Artefatos por Clade → Subclade → Pilar
├── product/
│   ├── discovery/
│   │   ├── codex/codex-prioritization.md
│   │   ├── katas/kata-pdr.md
│   │   └── warriors/
│   │       ├── warrior-isac.md
│   │       └── warrior-leonidas.md
│   └── delivery/
│       └── katas/kata-release-notes.md
│
├── engineering/
│   ├── architecture/
│   │   ├── codex/codex-architecture.md
│   │   └── katas/kata-adr.md
│   ├── quality/
│   │   ├── katas/
│   │   │   ├── kata-code-review.md
│   │   │   └── kata-gherkin-tests.md
│   │   └── warriors/
│   │       ├── warrior-flama.md
│   │       └── warrior-spartacus.md
│   └── security/
│       └── lexis/lex-no-secrets.md
│
└── foundation/                         # Clade transversal
    ├── process/
    │   ├── codex/codex-ahrena-sdlc.md
    │   └── lexis/lex-process.md
    ├── quality/
    │   └── lexis/lex-quality.md
    └── security/
        └── lexis/lex-security.md
```

Para criar um novo artefato: copie o `*-sample.md` do Pilar correspondente, coloque-o no Clade/Subclade adequado e preencha os campos `[]`.

### De-Para: `framework/` → `.cursor/`

Ao implementar no Cursor, os `.md` são copiados como `.mdc` com frontmatter YAML. A hierarquia Clade → Subclade é preservada:

| Pilar | Recurso Cursor | Prefixo | Destino |
|-------|----------------|---------|---------|
| **Lexis** | Rules | `lex-` | `.cursor/rules/<clade>/<subclade>/lexis/` |
| **Codex** | Rules | `codex-` | `.cursor/rules/<clade>/<subclade>/codex/` |
| **Katas** | Rules | `kata-` | `.cursor/rules/<clade>/<subclade>/katas/` |
| **Warriors** | Rules | `warrior-` | `.cursor/rules/<clade>/<subclade>/warriors/` |
| **Cries** | Commands | `cry-` | `.cursor/commands/<clade>/<subclade>/` |

```
.cursor/
├── rules/
│   ├── samples/
│   │   ├── lex-sample.mdc
│   │   ├── codex-sample.mdc
│   │   ├── kata-sample.mdc
│   │   └── warrior-sample.mdc
│   ├── product/
│   │   ├── discovery/
│   │   │   ├── codex/codex-prioritization.mdc
│   │   │   ├── katas/kata-pdr.mdc
│   │   │   └── warriors/
│   │   │       ├── warrior-isac-accounting-specialist.mdc
│   │   │       ├── warrior-teka-banking-regulatory-specialist.mdc
│   │   │       └── warrior-tiago-product-discovery-specialist.mdc
│   │   └── delivery/
│   │       └── katas/kata-release-notes-devops-specialist.mdc
│   ├── engineering/
│   │   ├── architecture/
│   │   │   ├── codex/codex-architecture.mdc
│   │   │   └── katas/kata-adr.mdc
│   │   ├── quality/
│   │   │   ├── katas/
│   │   │   │   ├── kata-code-review.mdc
│   │   │   │   └── kata-gherkin-tests.mdc
│   │   │   └── warriors/
│   │   │       ├── warrior-flama.mdc
│   │   │       └── warrior-spartacus.mdc
│   │   └── security/
│   │       └── lexis/lex-no-secrets.mdc
│   └── foundation/
│       ├── process/
│       │   ├── codex/codex-ahrena-sdlc.mdc
│       │   └── lexis/lex-process.mdc
│       ├── quality/
│       │   └── lexis/lex-quality.mdc
│       └── security/
│           └── lexis/lex-security.mdc
├── skills/
│   └── samples/
│       ├── kata-sample.mdc
│       └── warrior-sample.mdc
└── commands/
    └── samples/
        └── cry-sample.mdc
```
