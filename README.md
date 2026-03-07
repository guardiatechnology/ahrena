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
| **Natureza** | Restritiva e imperativa — define o que **nunca** pode acontecer ou que **sempre** deve acontecer |
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

**Seções:** Visão Geral, Contexto, Conteúdo (Princípios, Padrões e Convenções, Decisões Vigentes, Restrições Técnicas), Diagrama de Referência, Glossário, Referências.

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

**Seções:** Descrição, Uso, Parâmetros, O que o Comando Faz, Prompt Template, Exemplo de Invocação, Restrições, Diferença de Kata.

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

Gestão financeira, contábil e regulatória. Estrutura processos que exigem precisão, rastreabilidade e conformidade com normas.

| Subclade | Foco |
|----------|------|
| Accounting | Lançamentos, conciliação e fechamento contábil |
| Compliance | Regulamentação, auditoria e controles internos |
| Reporting | Relatórios gerenciais, demonstrações e KPIs financeiros |

#### Operations

Processos operacionais e suporte. Garante que sistemas e equipes funcionem de forma estável e eficiente no dia a dia.

| Subclade | Foco |
|----------|------|
| Support | Atendimento, escalonamento e base de conhecimento |
| Infrastructure | Servidores, redes, capacidade e disaster recovery |
| Monitoring | Alertas, dashboards e resposta a incidentes |

#### _Foundation — Clade Transversal

_Foundation é um **Clade especial** que não pertence a uma disciplina específica. Seus artefatos atuam de forma **transversal**, aplicando-se a todos os demais Clades simultaneamente.

Enquanto Clades como Product ou Engineering contêm conhecimento específico de suas disciplinas, _Foundation define as **regras, processos e padrões que atravessam todas elas** — segurança global, qualidade mínima e processos comuns que todo agente e todo artefato devem respeitar, independentemente do domínio.

| Subclade | Foco |
|----------|------|
| Process | SDLC, fluxos de trabalho e convenções comuns a todas as disciplinas |
| Quality | Padrões mínimos de qualidade válidos para qualquer artefato |
| Security | Políticas de segurança aplicáveis a todo o sistema |

> Na prática: uma Lexis em `_foundation/security/` aplica-se a **todos** os Clades — não apenas a Engineering. Ao criar um artefato em qualquer Clade, o agente deve consultar _Foundation primeiro para garantir conformidade com as regras transversais.

---

> Clades e Subclades são **extensíveis**: cada organização cria os que fizerem sentido para o seu contexto.

#### Endereçamento

```
<clade>/<subclade>/<pilar>/<prefixo>-<nome>.md
```

| Caminho | Leitura |
|---------|---------|
| `_foundation/security/lexis/lex-security.md` | Lei de segurança transversal, aplicável a todos os Clades |
| `product/discovery/codex/codex-prioritization.md` | Manual sobre priorização, na área Discovery da disciplina Product |
| `engineering/security/lexis/lex-no-secrets.md` | Lei sobre secrets, na área Security da disciplina Engineering |
| `product/delivery/katas/kata-release-notes.md` | Procedimento de release notes, na área Delivery de Product |
| `engineering/quality/warriors/warrior-spartacus.md` | Agente Spartacus, na área Quality de Engineering |
| `finance/compliance/cries/cry-audit-check.md` | Comando de audit check, na área Compliance de Finance |

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
│  ═══════════════════════════════════════════════════════          │
│  _foundation/ ──┬── process/        ← aplica-se a TODOS           │
│   (transversal) ├── quality/          os Clades acima             │
│                 └── security/                                     │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Estrutura do Repositório

### `framework/`

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
│   │   ├── codex/.../codex-*.md
│   │   ├── katas/.../kata-*.md
│   │   └── warriors/.../warrior-*.md
│   └── delivery/
│       └── katas/.../kata-*.md
│       └── cries/.../cry-*.md
│
├── engineering/
│   ├── architecture/
│   │   ├── codex/.../codex-*.md
│   │   └── katas/.../kata-*.md
│   ├── quality/
│   │   ├── katas/.../kata-*.md
│   │   └── warriors/.../warrior-*.md
│   └── security/
│       ├── lexis/.../lex-*.md
│       └── warriors/.../warrior-*.md
│
└── _foundation/                        
    ├── governance/
    │   ├── codex/.../codex-*.md
    │   ├── lexis/.../lex-*.md
    ├── quality/
    │   ├── codex/.../codex-*.md
    │   ├── lexis/.../lex-*.md
    │   ├── katas/.../kata-*.md
    └── security/
       ├── codex/.../codex-*.md
       ├── lexis/.../lex-*.md
```

Para criar um novo artefato: copie o `*-sample.md` do Pilar correspondente, coloque-o no Clade/Subclade adequado e preencha os campos `[]`.

### De-Para: `framework/` → `.cursor/`

Ao implementar no Cursor, os `.md` são copiados como `.mdc` com frontmatter YAML. A hierarquia Clade → Subclade é preservada:

| Pilar | Recurso Cursor | Prefixo | Destino |
|-------|----------------|---------|---------|
| **Lexis** | Rules | `lex-` | `.cursor/rules/<clade>/<subclade>/lex-*.mdc` |
| **Codex** | Rules | `codex-` | `.cursor/rules/<clade>/<subclade>/codex-*.mdc` |
| **Katas** | Skills | `kata-` | `.cursor/skills/<clade>/<subclade>/kata-*.mdc` |
| **Warriors** | Skills | `warrior-` | `.cursor/skills/<clade>/<subclade>/warrior-*.mdc` |
| **Cries** | Commands | `cry-` | `.cursor/commands/<clade>/<subclade>/.../cry-*.mdc` |

```
.cursor/
├── rules/
│   ├── samples/
│   │   ├── lex-sample.mdc
│   │   └── codex-sample.mdc
│   ├── product/
│   │   ├── discovery/
│   │   │   ├── codex/.../codex-*.mdc
│   │   │   ├── katas/.../kata-*.mdc
│   │   │   └── warriors/.../warrior-*.mdc
│   │   └── delivery/
│   │       └── katas/.../kata-*.mdc
│   ├── engineering/
│   │   ├── architecture/
│   │   │   ├── codex/.../codex-*.mdc
│   │   │   └── katas/.../kata-*.mdc
│   │   ├── quality/
│   │   │   ├── katas/.../kata-*.mdc
│   │   │   └── warriors/.../warrior-*.mdc
│   │   └── security/
│   │       ├── lexis/.../lex-*.mdc
│   │       └── warriors/.../warrior-*.mdc
│   └── _foundation/
│       ├── governance/
│       │   ├── codex/.../codex-*.mdc
│       │   └── lexis/.../lex-*.mdc
│       ├── quality/
│       │   ├── codex/.../codex-*.mdc
│       │   ├── lexis/.../lex-*.mdc
│       │   └── katas/.../kata-*.mdc
│       └── security/
│           ├── codex/.../codex-*.mdc
│           └── lexis/.../lex-*.mdc
├── skills/
│   └── samples/
│       ├── kata-sample.mdc
│       └── warrior-sample.mdc
└── commands/
    ├── samples/
    │   └── cry-sample.mdc
    └── product/
        └── delivery/.../cry-*.mdc
```
