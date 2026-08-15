# Lexis: Estrutura Obrigatória de Projeto de Skill

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Projetos de skill versionados no repositório Ahrena (fonte em `skills/{slug}/`, intermediário em `.build/`, entrega em `.dist/`)

## Lei

> **Todo projeto de skill DEVE residir em `{paths.skills_root}/{slug}/` (default `skills/{slug}/`) com layout canônico definido em `codex-skill-project-architecture`: presença obrigatória de `SKILL.md` e `skill.config.json` na raiz; `{slug}` em kebab-case válido per spec Anthropic e idêntico ao campo `name` do frontmatter do `SKILL.md`; separação física entre fonte (`{paths.skills_root}/`), intermediário (`{paths.skills_build}/`, gitignored) e entrega (`{paths.skills_dist}/`, committed); conteúdo do projeto respeitando integralmente as Lexis de qualidade aplicáveis ao tipo de cada artefato (widgets → `lex-frontend-*`; scripts/tools Python → `lex-python-*`; logging cross-language → `lex-logging-decorator`; MCP → `lex-mcp`). Editar artefatos diretamente em `{paths.skills_build}/` ou `{paths.skills_dist}/` é PROIBIDO — esses diretórios são derivados; mudanças entram pela fonte.**

## Regras

### 1. Localização e nomenclatura

- Diretório raiz do projeto: `{paths.skills_root}/{slug}/` (default `skills/{slug}/`)
- `{slug}`: 1-64 chars, somente `a-z`, `0-9` e hífen; sem hífen no início ou fim; sem `--` consecutivo (per spec Anthropic — `codex-skill-anthropic-agent-skills`)
- `{slug}` deve ser **idêntico** ao valor de `name` no frontmatter do `SKILL.md`
- Não usar nomes reservados pela documentação Anthropic (`anthropic`, `claude`)

### 2. Arquivos obrigatórios na raiz do projeto

| Arquivo | Papel |
|---------|-------|
| `SKILL.md` | Frontmatter Anthropic Agent Skills + corpo Markdown |
| `skill.config.json` | Configuração local do projeto (idioma, runtimes, ports do dev server, refs externas a snapshotar) |

`.skill-manifest.json` esqueleto **deve existir** após o scaffold, mas é **escrito** apenas pelo build. No PR 1 o esqueleto contém `schema_version` e campos vazios.

### 3. Subdiretórios opcionais

Permitidos no projeto fonte conforme `codex-skill-project-architecture`:

- `references/` — Markdown adicional (level 3 da spec)
- `scripts/` — código JS ou Python executável pelo agente
- `tools/` — MCP tools próprias do skill (convenção Ahrena)
- `widgets/` — componentes React (convenção Ahrena)
- `assets/` — recursos estáticos da spec

Subdiretórios fora dessa lista exigem justificativa explícita no `SKILL.md` ou em `skill.config.json` (campo `metadata.notes` ou equivalente). O agente que edita não cria novos top-level sem justificativa.

### 4. Separação fonte / intermediário / entrega

| Tipo | Path default | Versionado | Quem escreve |
|------|--------------|:----------:|--------------|
| Fonte | `skills/{slug}/` | Sim | Autor (humano ou agente, durante autoria) |
| Intermediário | `.build/{slug}/` | **Não** (em `.gitignore`) | Build (stack do projeto consumidor) |
| Entrega | `.dist/{slug}.skill` | Sim | Packaging (stack do projeto consumidor) |

Editar `.build/` ou `.dist/` manualmente quebra determinismo do build e auditabilidade. **Mudanças entram pela fonte**, sempre.

### 5. Conformidade com Pilares e Lexis aplicáveis

O conteúdo do projeto **herda** as Lexis de qualidade já codificadas no framework:

| Conteúdo do skill | Lexis e codex de qualidade aplicáveis |
|-------------------|---------------------------------------|
| `widgets/` (React/TS) | `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-security`, `lex-frontend-testing`, `lex-design-system-library` (quando renderizado em superfície Guardia), `codex-frontend-architecture` |
| `scripts/` Python | `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-error-handling`, `lex-python-result-type`, `lex-python-error-object`, `codex-python-architecture`, `codex-python-tooling` |
| `scripts/` JS/TS | `lex-frontend-typing` (quando TS), tratamento idiomático de erros |
| `tools/` MCP | `lex-mcp`, `codex-mcp-common`, mais Lexis da linguagem do handler |
| Logging em qualquer linguagem | `lex-logging-decorator` |
| Texto em `SKILL.md` e `references/` | `lex-tone` |
| Skill usada como tooling de PoV de agent | `lex-agent-construction-directives` (Diretriz 03 — Ferramentas Concretas no rigor pré-operacional; `stage: pre-operational` declarado no system prompt do PoV consumidor) |

Violar Lexis de qualidade dentro de um projeto de skill é violação direta — não há "modo skill" que afrouxe regra existente.

**Nota sobre skills consumidas em PoV de agent:** quando a skill é o artefato de implementação de um PoV de `warrior-claudionor` (`cry-pov --kind skill`), o consumidor — não a skill em si — declara `stage: pre-operational` no system prompt do PoV (`docs/{context}/agents-pov/system-prompt.md`), per `lex-agent-construction-directives`. A skill como artefato distribuível continua governada apenas por esta Lexis.

### 6. `.gitignore` mínimo

O repositório com projetos de skill **deve** ter `.build/` em `.gitignore` (raiz ou path equivalente quando `paths.skills_build` for sobrescrito).

`.dist/` **não** vai pro `.gitignore` — é entrega versionada.

`kata-init-skill` garante a entrada quando o primeiro projeto é criado.

## Exemplos

### Correto

```
skills/scheduled-payments-skill/
├── SKILL.md                    # frontmatter com name: scheduled-payments-skill
├── skill.config.json
├── .skill-manifest.json        # esqueleto
├── widgets/
│   ├── package.json
│   └── src/transfer-form/index.tsx
└── scripts/
    └── src/validate_amount.py

.build/                         # gitignored
.dist/                          # committed
```

```yaml
# SKILL.md
---
name: scheduled-payments-skill   # idêntico ao diretório
description: Schedules and approves bank transfers using widgets connected to Python tools. Use when the user wants to create or approve a scheduled transfer.
license: Apache-2.0
metadata:
  version: "0.1.0"
  language: pt-BR
---
```

### Incorreto

```
my-skills/payments/              # ❌ fora de paths.skills_root sem override declarado
skills/Payments_Skill/           # ❌ slug com underscore e maiúscula
skills/payments-skill/SKILL.md   # ❌ frontmatter com name: payments (não casa com diretório)
.build/payments-skill/widgets/   # ❌ edição direta no intermediário
.dist/payments-skill.skill/      # ❌ edição direta na entrega
```

```
skills/payments-skill/
├── SKILL.md
└── widgets/src/Form.jsx         # ❌ TS strict não aplicado, viola lex-frontend-typing
                                 # mesmo dentro de projeto de skill, lex-frontend-* vale
```

## Validação Automatizada

- **Ferramenta:**
  - `kata-init-skill` valida slug, frontmatter, presença de arquivos obrigatórios na criação
  - `kata-skill-validate` (via `scripts/skills/validate.py`) executa a verificação determinística desta Lex — invocado por `warrior-claudionor` e por `cry-skill --mode validate`
  - PR review (humano) confere layout enquanto `kata-quality-gate` não integra
  - Lint genérico (existente) detecta violação de `lex-frontend-*` / `lex-python-*` dentro do projeto, sem necessidade de regra nova
  - `.gitignore` raiz contém `.build/` (verificável por inspeção)
- **Momento:** scaffold (`kata-init-skill`); a cada edição (`kata-skill-validate`); PR review; futura integração no Gate 2
- **Métrica:** 0 projetos de skill com `name` divergente do slug; 0 commits que editam `.build/` ou `.dist/` diretamente; 100% dos projetos com `SKILL.md` + `skill.config.json` na raiz
