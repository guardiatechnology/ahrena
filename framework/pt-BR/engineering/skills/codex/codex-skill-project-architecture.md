# Codex: Arquitetura de Projeto de Skill (Ahrena)

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Estrutura interna de um projeto de skill no repositório Ahrena (`skills/{slug}/`), papel de cada subdiretório, ciclo `dev → build → dist`, e reuso dos codex de arquitetura existentes durante a autoria

## Visão Geral

Cada skill externo é um **projeto de primeira classe** no repositório Ahrena, com fonte versionada em `skills/{slug}/`. O projeto segue os Pilares Ahrena durante a autoria — widgets adotam `codex-frontend-architecture`, scripts e tools em Python adotam `codex-python-architecture`, regras de qualidade vêm das Lexis correspondentes — sem duplicação. O resultado final é um pacote no formato Anthropic Agent Skills (per `codex-skill-anthropic-agent-skills`), entregue em `.dist/`.

Este Codex define **somente o layout do projeto fonte e o ciclo dev/build/dist**. Não cobre:

- Detalhes do formato Anthropic Agent Skills → `codex-skill-anthropic-agent-skills`
- Convenção de tools MCP e widgets React (manifestos, bindings) → `codex-skill-tools-and-widgets`
- Estrutura final do pacote em `.dist/` → `lex-skill-package-structure` + codex correspondente

## Contexto

- **Domínio:** projetos de skill versionados no repositório Ahrena
- **Público-alvo:** autores de skill, `kata-init-skill`, agentes que delegam edição (`warrior-hephaestus` para widgets, `warrior-apollo` para scripts/tools Python)
- **Atualização:** quando a convenção de subdiretórios mudar; quando novos tipos de artefato forem introduzidos

## Conteúdo

### Layout canônico do projeto fonte

```
skills/{slug}/
├── SKILL.md # Frontmatter Agent Skills + corpo (orquestra os demais artefatos)
├── .skill-manifest.json # Esqueleto; preenchido com refs+hashes pelo build
├── skill.config.json # Config local do projeto (idioma, runtimes, ports do dev server)
├── references/ # Markdown adicional (level-3 da spec) — opcional
├── scripts/ # JS ou Python — utilitários executáveis pelo agente — opcional
│ ├── package.json # quando JS
│ ├── pyproject.toml # quando Python
│ └── src/
├── tools/ # MCP tools (lógica) — convenção Ahrena, opcional
│ ├── mcp.config.json
│ └── handlers/
└── widgets/ # React (TS) — UI — convenção Ahrena, opcional
 ├── package.json
 ├── manifest.json
 └── src/
```

`{slug}` é kebab-case válido per spec Anthropic (`a-z`, `0-9`, hífen; sem hífen no início/fim; sem `--`; **idêntico ao `name` no SKILL.md**).

### Mapeamento spec Anthropic ↔ projeto Ahrena

| Item | Onde fica na spec (`.dist/{slug}/`) | Onde fica no projeto fonte (`skills/{slug}/`) | Status |
|------|--------------------------------------|------------------------------------------------|--------|
| `SKILL.md` | raiz | raiz | nativo da spec |
| `references/` | raiz | raiz | nativo |
| `scripts/` | raiz (executáveis prontos) | raiz (fonte; build congela em `.build/`) | nativo |
| `assets/` | raiz | (criado pelo autor quando necessário) | nativo |
| `tools/` (MCP) | raiz | raiz | **convenção Ahrena**, fora da spec |
| `widgets/` (React) | raiz | raiz | **convenção Ahrena**, fora da spec |
| `.skill-manifest.json` | raiz | raiz (esqueleto, completado no build) | **convenção Ahrena** |
| `skill.config.json` | (não vai pro pacote) | raiz | **convenção Ahrena** (apenas dev/build) |

Convenções Ahrena (`tools/`, `widgets/`, `.skill-manifest.json`) são **extensões** da spec — agentes externos que só conhecem a spec ignoram esses diretórios; agentes que conhecem a convenção Ahrena consomem.

### `SKILL.md` no projeto fonte

O `SKILL.md` no projeto fonte é o mesmo arquivo que vai pro pacote final (build apenas reescreve paths relativos quando necessário). Estrutura mínima:

```markdown
---
name: scheduled-payments-skill
description: Schedules and approves bank transfers using widgets connected to Python tools. Use when the user wants to create or approve a scheduled transfer.
license: Apache-2.0
metadata:
 version: "0.1.0"
 language: pt-BR
 spec_version: "agentskills.io/specification@2026-04"
---

# Scheduled Payments Skill

## Quando usar
{...}

## Fluxo
1. Renderize o widget `widgets/transfer-form/` para o usuário.
2. Quando o usuário confirma, invoque a tool `tools/handlers/create_transfer.py`.
3. Mostre o resultado no widget de confirmação.

## Referências
- Detalhes do formulário: [references/FORM.md](references/FORM.md)
- Tool de criação: `tools/handlers/create_transfer.py`
```

Recomendações da spec se aplicam: **< 500 linhas**, **< 5.000 tokens**, conteúdo extenso vai para `references/`.

### `skill.config.json`

Configuração local do projeto, **não vai para o pacote final**. Lida pelo `kata-init-skill` (scaffold) e pela stack de build/release do projeto consumidor.

Esqueleto canônico:

```json
{
 "schema_version": 1,
 "language": "pt-BR",
 "runtimes": {
 "scripts": "python | node",
 "widgets": "react"
 },
 "dev_server": {
 "widgets_port": 5173,
 "scripts_port": 5174,
 "tools_stub_port": 5175
 },
 "build": {
 "bundler": "vite",
 "minify": true,
 "source_maps": false
 },
 "external_refs": [
 {
 "kind": "lexis",
 "id": "_foundation/tooling/lexis/lex-mcp"
 }
 ]
}
```

`external_refs` lista artefatos do framework Ahrena (lex/codex/kata) que devem ser snapshotados em `references/` durante o build. A resolução é responsabilidade do build do projeto consumidor.

### Subdiretórios — papel e detalhes

#### `SKILL.md` + `references/` (nativos da spec)

Domínio do autor; sem regra Ahrena além do que `codex-skill-anthropic-agent-skills` define.

#### `scripts/` (nativo da spec)

Código executável invocado pelo agente. **Linguagem:** JS (Node) ou Python — escolha por contexto:

- Python para lógica de domínio, integração com APIs estruturadas, processamento de dados (alinhado a `codex-python-architecture`, `codex-python-tooling`)
- JS para utilidades de DOM, geração de markup, interação com runtime de browser
- Mistura é permitida (um skill pode ter ambos)

Cada script segue as Lexis e codex da sua linguagem **sem ajuste**:

| Aspecto | Python | JS/TS |
|---------|--------|-------|
| Tipagem | `lex-python-typing` (mypy strict) | `lex-frontend-typing` (TS strict) — quando aplicável |
| Erros | `lex-python-error-handling`, `lex-python-result-type` | tratamento idiomático |
| Testes | `lex-python-testing` | `lex-frontend-testing` |
| Logging | `lex-logging-decorator` (cross-language) | `lex-logging-decorator` |
| Segurança | `lex-python-security` | `lex-frontend-security` |

Detalhes de **conexão script ↔ widget** ficam em `codex-skill-tools-and-widgets`.

#### `tools/` (convenção Ahrena, opcional)

MCP tools que o agente externo invoca durante a execução do skill. Servem como ferramentas de domínio próprias do skill, sem expor artefatos brutos do Ahrena.

Detalhamento (manifest, registro, conexão) em `codex-skill-tools-and-widgets`. No PR 1 (scaffold), o diretório existe vazio com `mcp.config.json` placeholder e um exemplo trivial em `handlers/`.

#### `widgets/` (convenção Ahrena, opcional)

Componentes React que o agente renderiza no chat. **Arquitetura herda integralmente** `codex-frontend-architecture`:

- Camadas (Pages → Features → Components → Hooks → Services → State)
- Server state via TanStack Query / SWR; client state via Zustand / Context conforme escopo
- Tipos derivados de OpenAPI quando disponível (via `openapi-typescript`)
- Acessibilidade WCAG 2.1 AA per `lex-frontend-accessibility`
- Segurança per `lex-frontend-security` (sem `dangerouslySetInnerHTML` sem sanitização, sem secrets em bundle)
- Testes per `lex-frontend-testing`
- Design system Guardia per `lex-design-system-library` quando o widget for renderizado em superfície Guardia

Detalhamento de manifest, props, eventos e binding com scripts/tools em `codex-skill-tools-and-widgets`. No PR 1, o diretório vem vazio com `package.json` mínimo e um componente exemplo.

### Reuso de codex e Lexis durante a autoria

| Conteúdo do projeto | Codex de arquitetura aplicável | Lexis aplicáveis (sem ajuste) |
|---------------------|--------------------------------|-------------------------------|
| `widgets/` (React) | `codex-frontend-architecture` | `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-security`, `lex-frontend-testing`, `lex-design-system-library` |
| `scripts/` Python | `codex-python-architecture`, `codex-python-tooling`, `codex-python-testing`, `codex-python-logging` | `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-error-handling`, `lex-python-result-type`, `lex-python-error-object`, `lex-logging-decorator` |
| `scripts/` JS | (futuro `codex-js-architecture` quando emergir) | `lex-frontend-typing` quando TS; `lex-logging-decorator` |
| `tools/` (MCP) | `codex-mcp-common`, `codex-python-architecture` quando handler em Python | `lex-mcp`, mais as Lexis de Python/JS conforme handler |
| `SKILL.md` corpo | `codex-skill-anthropic-agent-skills` | `lex-tone` (estilo direto, sem buzzwords) |

**Princípio:** o projeto de skill é um cliente das mesmas regras que governam o resto da plataforma. Não há "regras de skill" paralelas que dupliquem qualidade já codificada.

### Ciclo dev → build → dist

```
skills/{slug}/ # FONTE (versionada, autoria com Pilares)
 │
 ▼
 localhost — widgets HMR + script runner + tools stub
 │
 ▼
.build/{slug}/ # INTERMEDIÁRIO (gitignored)
 ├── widgets/ (React compilado)
 ├── scripts/ (deps lockadas)
 ├── tools/ (config validada)
 ├── references/ (snapshots de external_refs)
 ├── SKILL.md (paths reescritos)
 ├── .skill-manifest.json (com hashes)
 └── {slug}.zip (testável em outro agente)
 │
 ▼
.dist/{slug}.skill # ENTREGA (committed)
```

Regras (algumas ainda só consagradas no PR 1, outras codificadas em PRs futuros):

- **Fonte é a verdade.** `.build/` e `.dist/` são derivados; nenhum agente edita esses diretórios manualmente
- **`.build/` é gitignored.** `.dist/` é committed (consumível por agentes que não têm Ahrena)
- **Determinismo.** Build deve produzir hashes idênticos para mesmo input; ordering lexicográfico, sem timestamps voláteis
- **Snapshots por commit hash.** `.skill-manifest.json` registra `source_commit` para cada ref do framework

No PR 1 (scaffold), apenas o layout fonte é estabelecido; build e packaging são placeholders.

### Diretivas relacionadas

`.ahrena/.directives` introduz três paths para localizar fonte e saídas:

```yaml
paths:
 skills_root: skills # diretório fonte dos projetos de skill
 skills_build: .build # intermediário (gitignored)
 skills_dist: .dist # entrega final (committed)
```

Projetos podem sobrescrever (ex.: `skills_root: my-skills/`); agentes consultam a chave em vez de assumir literal.

### `.gitignore` recomendado

`.build/` no `.gitignore` raiz; `.dist/` permanece versionado:

```
.build/
```

`kata-init-skill` (escopo deste PR) garante que a entrada existe quando inicializa o primeiro skill.

## Restrições

- **Skill não é Pilar do framework.** Não tem prefix em `framework/`, não aparece em `naming.prefixes`. É projeto externo governado pelos artefatos deste codex e do `lex-skill-project-structure`.
- **Convenções Ahrena (`tools/`, `widgets/`) são opcionais.** Skills podem existir só com `SKILL.md` + `scripts/`/`references/` puros da spec. A convenção entra quando o skill precisa de UI ou MCP próprio.
- **Mono-idioma por skill.** `metadata.language` declara um idioma; produzir o mesmo skill em pt-BR e en exige dois projetos `skills/{slug}-ptbr/` e `skills/{slug}-en/` ou um mecanismo de localização interno (não governado neste PR).
- **Slug do diretório == `name` do frontmatter.** Spec exige; `kata-init-skill` valida.

## Glossário

| Termo | Definição |
|-------|-----------|
| Projeto de skill | Diretório `skills/{slug}/` versionado no repositório Ahrena |
| Slug | Nome em kebab-case do projeto, idêntico ao `name` da spec |
| Pacote | Saída em `.dist/{slug}.skill` (formato Anthropic Agent Skills) |
| Build intermediário | Saída em `.build/{slug}/` (testável em localhost; não é entrega) |
| Convenção Ahrena | Diretórios e arquivos não definidos pela spec (`tools/`, `widgets/`, `.skill-manifest.json`, `skill.config.json`) |
| External ref | Artefato do framework Ahrena (lex/codex/kata) snapshotado em `references/` no build |

## Referências

- `codex-skill-anthropic-agent-skills` — spec externa
- `codex-frontend-architecture` — arquitetura para `widgets/`
- `codex-python-architecture`, `codex-python-tooling` — arquitetura para `scripts/` e `tools/` Python
- `codex-mcp-common` — padrões MCP usados em `tools/`
- `lex-skill-project-structure` — lei do layout
- `lex-directives` — onde os paths `skills_root/build/dist` são lidos
- `lex-frontend-*`, `lex-python-*` — qualidade aplicável aos artefatos por linguagem
