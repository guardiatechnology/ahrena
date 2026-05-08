# Codex: Anthropic Agent Skills (formato SKILL.md)

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Especificação canônica do formato Agent Skills da Anthropic — formato externo consumido por Claude API, Claude Code, Cursor, Codex CLI e outros agentes que adotaram a spec aberta

## Visão Geral

Agent Skills é um padrão aberto promovido pela Anthropic para empacotar capacidades modulares que estendem agentes de IA. Cada Skill é um diretório com um arquivo `SKILL.md` (YAML frontmatter + Markdown) que o agente carrega progressivamente: metadata sempre, corpo quando ativado, recursos sob demanda.

Este Codex é a referência conceitual e de campos da spec. Não cobre a convenção Ahrena de bundlar tools MCP e widgets React — isso fica em `codex-skill-tools-and-widgets`. Não cobre o layout do projeto fonte no repositório — isso fica em `codex-skill-project-architecture`.

Fonte canônica da spec: [agentskills.io/specification](https://agentskills.io/specification). Documentação Anthropic: [platform.claude.com/docs/en/agents-and-tools/agent-skills/overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

## Contexto

- **Domínio:** formato externo de skill (entrega final consumida por agentes fora do Ahrena)
- **Público-alvo:** autores de skills, `kata-init-skill`
- **Atualização:** quando a spec oficial evoluir; revisar `metadata.spec_version` do skill produzido

## Conteúdo

### Estrutura de diretório

Um skill é um diretório com, no mínimo, um `SKILL.md`:

```
skill-name/
├── SKILL.md # Obrigatório — metadata + instruções
├── scripts/ # Opcional — código executável
├── references/ # Opcional — documentação adicional
├── assets/ # Opcional — templates, recursos estáticos
└── ... # Quaisquer outros arquivos
```

**Restrição importante:** o nome do diretório raiz **DEVE** ser idêntico ao valor do campo `name` no frontmatter.

### Frontmatter do SKILL.md

| Campo | Obrigatório | Restrições |
|-------|:-----------:|------------|
| `name` | Sim | 1-64 chars; somente `a-z`, `0-9` e hífen; não inicia/termina em hífen; sem `--`; **deve casar com o nome do diretório** |
| `description` | Sim | 1-1024 chars; não-vazio; descreve **o que faz** e **quando usar** |
| `license` | Não | Nome de licença ou referência a arquivo `LICENSE` bundlado |
| `compatibility` | Não | 1-500 chars; requisitos de ambiente (produto-alvo, pacotes de sistema, acesso à rede) |
| `metadata` | Não | Mapa chave→valor arbitrário para propriedades não definidas pela spec |
| `allowed-tools` | Não | String separada por espaços, ferramentas pré-aprovadas (experimental; suporte varia por agente) |

#### `name`

Identificador do skill. Casa com o nome do diretório raiz. Não pode usar palavras reservadas (`anthropic`, `claude`) per documentação Anthropic.

Válidos: `pdf-processing`, `data-analysis`, `code-review`.

Inválidos: `PDF-Processing` (uppercase), `-pdf` (hífen no início), `pdf--processing` (hífens consecutivos).

#### `description`

Texto que o agente lê na partida (Level 1) para decidir quando ativar o skill. **Deve incluir keywords concretas** que casem com a tarefa do usuário; descrições genéricas (`"helps with PDFs"`) reduzem ativação correta.

Bom: *"Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction."*

#### `license`

Identificação curta (ex.: `Apache-2.0`, `MIT`) ou apontamento para arquivo bundlado (ex.: `Proprietary. LICENSE.txt has complete terms`).

#### `compatibility`

Quando o skill tem requisitos não-óbvios. Exemplos válidos:

```yaml
compatibility: Designed for Claude Code (or similar products)
compatibility: Requires git, docker, jq, and access to the internet
compatibility: Requires Python 3.14+ and uv
```

A maioria dos skills não precisa do campo.

#### `metadata`

Mapa livre. Convenções Ahrena (não da spec) que o build do projeto consumidor pode honrar:

| Chave | Uso Ahrena |
|-------|------------|
| `version` | Semver per `lex-semantic-version` (ex.: `"0.1.0"`) |
| `language` | BCP 47 do conteúdo do skill (`pt-BR`, `es`, `en`) |
| `author` | Pessoa, time ou organização autora |
| `spec_version` | Versão da spec Agent Skills validada (controle de drift) |

Outras chaves são livres; o agente que consome só vê o mapa cru. Recomenda-se prefixar chaves específicas de organização (ex.: `guardia.bounded_context: scheduled-payments`) para evitar colisão.

#### `allowed-tools`

String separada por espaços, no formato `Tool` ou `Tool(escopo)`:

```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

**Experimental** — suporte varia entre Claude Code, Claude API e outros agentes. Tratar como sugestão, não como contrato forte.

### Corpo do SKILL.md (Markdown após o frontmatter)

Sem restrição estrutural. O agente lê o corpo inteiro quando ativa o skill (Level 2). Recomendações da spec:

- Manter abaixo de **500 linhas** e **5.000 tokens**
- Mover material extenso para `references/`
- Incluir: passos, exemplos de input/output, edge cases comuns

Sem restrição não significa ausência de critério — corpo verboso afeta token budget de toda invocação.

### Diretórios opcionais

#### `scripts/`

Código executável invocado pelo agente via bash. Linguagens aceitas dependem do runtime do agente (Python, Bash, Node são comuns). Devem:

- Ser self-contained ou documentar dependências de forma explícita
- Emitir mensagens de erro úteis
- Tratar edge cases sem crash silencioso

Quando o agente roda um script, **só a saída** entra no contexto — o código fonte permanece no filesystem (Level 3). Isso torna script mais barato em tokens do que pedir ao agente para gerar código equivalente inline.

#### `references/`

Markdown adicional para o agente carregar **sob demanda**. Convenção comum:

- `REFERENCE.md` — referência técnica detalhada
- `FORMS.md` — templates ou formatos estruturados
- Arquivos por domínio (`finance.md`, `legal.md`)

Manter cada arquivo focado e curto reduz custo quando o agente puxa apenas o que precisa.

#### `assets/`

Recursos estáticos: templates de documento, imagens, data files (CSV, JSON), schemas. O agente abre quando o fluxo da tarefa demanda.

### Carregamento progressivo (3 níveis)

| Nível | Quando carrega | Custo aproximado | Conteúdo |
|-------|----------------|------------------|----------|
| 1 — Metadata | Sempre, na partida | ~100 tokens por skill | `name` + `description` do frontmatter |
| 2 — Instruções | Quando o skill é ativado | < 5.000 tokens recomendado | Corpo Markdown do `SKILL.md` |
| 3 — Recursos | Sob demanda | Praticamente ilimitado (não entra no contexto até ler) | Arquivos em `scripts/`, `references/`, `assets/` |

A partição de conteúdo em camadas é o princípio central da spec. Skills bem desenhados respeitam essa hierarquia — metadata enxuto, corpo conciso, peso em recursos.

### Referências entre arquivos

Caminhos **relativos à raiz do skill**:

```markdown
Veja [o guia de referência](references/REFERENCE.md) para detalhes.

Para extrair, rode: `scripts/extract.py`
```

A spec recomenda manter referências em **um nível de profundidade** a partir do `SKILL.md`. Cadeias profundas dificultam carregamento progressivo.

### Disponibilidade por superfície

Skill produzido na spec Anthropic é consumível por:

| Superfície | Suporte | Distribuição |
|------------|---------|--------------|
| Claude API | Pre-built + custom | Endpoint `/v1/skills`; requer beta headers `code-execution-2025-08-25`, `skills-2025-10-02`, `files-api-2025-04-14` |
| Claude Code | Custom | Filesystem — `~/.claude/skills/{slug}/` (pessoal) ou `.claude/skills/{slug}/` (projeto) |
| claude.ai | Pre-built + custom (zip upload em Settings → Features; planos Pro+) | Por usuário; sem distribuição org-wide |
| Cursor / Codex CLI / Gemini CLI | Adotaram a spec aberta | Filesystem similar ao Claude Code |

Skills **não sincronizam automaticamente entre superfícies** — upload separado por superfície.

### Restrições de runtime

| Superfície | Rede | Pacotes |
|------------|------|---------|
| Claude API | Sem acesso externo | Apenas pré-instalados; sem instalação em runtime |
| Claude Code | Mesmo acesso do programa do usuário | Recomenda-se instalar local ao skill, não global |
| claude.ai | Variável (config do admin/user) | Conforme superfície |

`compatibility` no frontmatter é onde declarar essas dependências — agentes que não satisfazem podem recusar ativação.

### Validação

A spec mantém o CLI [`skills-ref`](https://github.com/agentskills/agentskills/tree/main/skills-ref):

```bash
skills-ref validate ./my-skill
```

Confere frontmatter válido, naming, e estrutura mínima. Stack de build do projeto consumidor pode integrar essa validação.

### Segurança

Documentação Anthropic é explícita: tratar skill como software instalado. Skill malicioso pode invocar tools de modo prejudicial, vazar dados ou executar código fora do propósito declarado. Auditar:

- Cada arquivo bundlado (SKILL.md, scripts, references, assets)
- Chamadas de rede (skills que buscam URLs externas têm risco amplificado)
- Padrões de acesso a arquivo / bash incompatíveis com o `description`

Skills produzidos no Ahrena são auditáveis pela trilha de commit (refs snapshotadas com hash, manifest determinístico em).

## Restrições

- A spec **não define** layout para tools MCP nem widgets UI. A convenção Ahrena (`codex-skill-tools-and-widgets`,) cria diretórios `tools/` e `widgets/` adicionais — agentes que só conhecem a spec ignoram esses diretórios. Documentar a convenção como "extensão Ahrena" é mandatório no SKILL.md gerado.
- A spec **não define** versionamento do skill em si — Ahrena coloca em `metadata.version` (semver per `lex-semantic-version`).
- A spec **não define** internacionalização — Ahrena coloca em `metadata.language`. Cada skill empacotado é mono-idioma.

## Glossário

| Termo | Definição |
|-------|-----------|
| Agent Skills | Padrão aberto da Anthropic para skills baseados em filesystem |
| SKILL.md | Arquivo raiz com frontmatter + corpo |
| Progressive disclosure | Carregamento em 3 níveis (metadata, instruções, recursos) |
| Pre-built Skill | Skill da Anthropic disponível sem upload (PowerPoint, Excel, Word, PDF) |
| Custom Skill | Skill criado por terceiro, distribuído via filesystem ou upload |

## Referências

- [Spec canônica — agentskills.io/specification](https://agentskills.io/specification)
- [Documentação Anthropic — Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Repo aberto — anthropics/skills](https://github.com/anthropics/skills)
- [Engineering blog — Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- `codex-skill-project-architecture` — layout do projeto fonte Ahrena (`skills/{slug}/`)
- `codex-skill-tools-and-widgets` — convenção Ahrena para `tools/` (MCP) e `widgets/` (React)
- `lex-skill-project-structure` — lei do layout do projeto fonte
