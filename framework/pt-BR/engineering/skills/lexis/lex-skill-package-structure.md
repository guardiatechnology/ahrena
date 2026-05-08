# Lexis: Estrutura Obrigatória do Pacote `.skill` Entregue

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Pacotes `.skill` versionados em `{paths.skills_dist}/` (default `.dist/`) — entrega final consumida por agentes externos no formato Anthropic Agent Skills

## Lei

> **Todo pacote `.skill` em `{paths.skills_dist}/` (default `.dist/`) MUST conter (1) `SKILL.md` com frontmatter Anthropic Agent Skills válido (`name` 1-64 chars kebab-case casando com o nome do diretório do pacote, `description` 1-1024 chars), (2) `.skill-manifest.json` válido contra o schema canônico Ahrena (`schema_version`, `skill.name`, `skill.version`, `skill.language`, `framework.ahrena_commit` não-vazio, `references[]` e `files[]`), (3) para cada entrada em `files[]`: o arquivo MUST existir no pacote e seu `sha256` MUST conferir, (4) para cada entrada em `references[]`: arquivo presente em `references/<id>.md` com `snapshot_sha256` conferindo, e `source_commit` não-vazio, (5) zero arquivos órfãos no pacote (todo arquivo entregue MUST estar declarado em `files[]`). A lei governa o output empacotado; ela é AGNOSTIC ao build — `Vite`, `uv`, `Node`, `zip`, ports, ferramentas de empacotamento são responsabilidade exclusiva da stack do projeto consumidor (Makefile, GitHub Actions, npm scripts, devops próprio). Ahrena valida o que chega em `.dist/`, não como o build chegou lá.**

## Abrangência

- **Aplica-se a:** todo `.skill` (diretório ou arquivo selado per spec Anthropic) entregue em `{paths.skills_dist}/`, em qualquer idioma declarado em `metadata.language`
- **Agentes vinculados:** reviewer humano, `kata-quality-gate` quando integrar a verificação, autores que adicionam/modificam pacotes em `.dist/`
- **Exceções:** Nenhuma. Lexis não admitem exceções. `.skill` produzidos por automação ou manualmente seguem a mesma lei

## Schema canônico do `.skill-manifest.json`

```json
{
  "schema_version": 1,
  "skill": {
    "name": "scheduled-payments-skill",
    "version": "0.1.0",
    "language": "pt-BR"
  },
  "framework": {
    "ahrena_commit": "956826f0419aea431e72b8d1796a409d0351e749"
  },
  "references": [
    {
      "kind": "lexis",
      "id": "engineering/skills/lexis/lex-skill-project-structure",
      "source_commit": "956826f0419aea431e72b8d1796a409d0351e749",
      "snapshot_path": "references/lex-skill-project-structure.md",
      "snapshot_sha256": "a1b2c3..."
    }
  ],
  "files": [
    { "path": "SKILL.md", "sha256": "..." },
    { "path": ".skill-manifest.json", "sha256": "self" },
    { "path": "widgets/dist/index.js", "sha256": "..." },
    { "path": "references/lex-skill-project-structure.md", "sha256": "..." }
  ]
}
```

| Campo | Obrigatório | Restrição |
|-------|:-----------:|-----------|
| `schema_version` | Sim | Inteiro; atual: `1` |
| `skill.name` | Sim | Casa com o nome do diretório do `.skill` |
| `skill.version` | Sim | Semver per `lex-semantic-version` |
| `skill.language` | Sim | BCP 47 |
| `framework.ahrena_commit` | Sim | SHA-1 ou SHA-256 do commit do framework Ahrena que produziu o pacote; **não pode ser vazio** |
| `references[]` | Sim (lista pode ser vazia) | Cada entrada: `kind`, `id`, `source_commit` (não-vazio), `snapshot_path` (relativo ao pacote), `snapshot_sha256` |
| `files[]` | Sim (lista não-vazia) | Lista lexicograficamente ordenada de TODOS os arquivos do pacote com seus `sha256`; entrada `.skill-manifest.json` pode usar valor `"self"` (manifest se referenciando) |

## Regras

### 1. SKILL.md frontmatter válido

Per `codex-skill-anthropic-agent-skills`:

- `name`: regex `^[a-z0-9](?:[a-z0-9]|-(?!-)){0,62}[a-z0-9]?$`, 1-64 chars, sem palavras reservadas (`anthropic`, `claude`)
- `name` casa com o nome do diretório raiz do `.skill`
- `description`: 1-1024 chars, não-vazio
- Outros campos opcionais (license, compatibility, metadata, allowed-tools) per spec quando presentes

### 2. `.skill-manifest.json` válido

- Parseia como JSON
- Schema conforme tabela acima
- `framework.ahrena_commit` é SHA não-vazio (40+ caracteres hexadecimais)
- `files[]` contém **toda** entrada que existe no pacote (sem órfãos)
- Ordering de `files[]` é lexicográfica por `path` (per requisito de auditabilidade)

### 3. Hashes conferem

Para cada `files[].path`:

- O arquivo existe no pacote
- `sha256(<arquivo>) == files[<i>].sha256` (exceto para `.skill-manifest.json` que pode usar valor `"self"`)

Para cada `references[]`:

- `references/<...>.md` existe (path relativo ao pacote)
- `sha256(<arquivo de snapshot>) == references[<i>].snapshot_sha256`
- `source_commit` é SHA não-vazio (referenciando o commit do framework Ahrena de onde a referência foi snapshotada)

### 4. Sem arquivos órfãos

Todo arquivo no diretório do pacote (recursivo, exceto o próprio `.skill-manifest.json`) MUST aparecer em `files[]`. Arquivos órfãos quebram a auditabilidade do que foi entregue.

### 5. Agnostic ao build

A lei NÃO prescreve:

- Bundler de widgets (Vite, esbuild, Webpack, Rollup — escolha do projeto)
- Runtime de scripts (Python via uv, pip, conda; Node, Bun, Deno; etc.)
- Comando de empacotamento (zip, tar, formato proprietário, etc.)
- Ferramenta de cálculo de hash, ordering, mtime
- Pipeline de CI/CD (GitHub Actions, GitLab CI, Jenkins, manual local)
- Ports, hosts, ambientes de dev local

A stack do projeto consumidor decide. A lei só valida o que chega em `.dist/`.

## HARD-GATE

Per [`lex-hard-gate-pattern`](../../../_foundation/quality/lexis/lex-hard-gate-pattern.md), o bloqueio textual canônico:

```
<HARD-GATE>
Reviewer (humano) e qualquer agente que valide PRs MUST NOT aprovar
merge de PR que adicione ou modifique pacote `.skill` em
`{paths.skills_dist}/` (default `.dist/`) sem que o pacote satisfaça
TODOS os 5 critérios canônicos:

  (a) SKILL.md com frontmatter Anthropic válido (name, description)
      e name idêntico ao nome do diretório do pacote
  (b) .skill-manifest.json válido contra o schema (schema_version,
      skill, framework.ahrena_commit não-vazio, references[], files[])
  (c) Para cada files[].path: arquivo presente + sha256 confere
  (d) Para cada references[]: snapshot presente + snapshot_sha256
      confere + source_commit não-vazio
  (e) Zero arquivos órfãos (todo arquivo no pacote em files[])

Esta regra aplica-se a TODO pacote .skill em .dist/, independentemente de:
  - tamanho percebido ("é só uma versão menor")
  - urgência ("precisa entregar hoje")
  - quem solicitou ("o cliente está pedindo")
  - confiança no autor ("o autor já validou local")

Exceção declarada: Nenhuma. Reapresentar pacote corrigido se algum
critério falhar.
</HARD-GATE>
```

## Consequências de Violação

1. **Bloqueio de merge:** PR contendo `.skill` que falhe qualquer um dos 5 critérios é rejeitado pelo reviewer ou (futuramente) pelo `kata-quality-gate` integrado.
2. **Alerta:** validador automático identifica o critério violado e o caminho do arquivo problemático.
3. **Remediação:** o autor corrige o pacote (regenera o build, atualiza manifest, completa hashes, declara arquivos órfãos) e reapresenta. Não há merge condicional.

## Exemplos

### Correto

```
.dist/hello-skill.skill/
├── SKILL.md                         # name: hello-skill (casa com diretório)
├── .skill-manifest.json             # schema_version=1, ahrena_commit=956826f..., 5 files, 1 ref
├── references/
│   └── lex-skill-project-structure.md   # snapshot, snapshot_sha256 confere, source_commit=956826f...
└── widgets/
    └── dist/
        └── index.js                  # listado em files[], sha256 confere
```

`.skill-manifest.json` listando todos os 5 arquivos em `files[]` ordenados; nenhum arquivo órfão.

### Incorreto

```
.dist/hello-skill.skill/
├── SKILL.md                         # name: helloskill (não casa com diretório)  ❌ critério (a)
├── .skill-manifest.json             # framework.ahrena_commit: ""                ❌ critério (b)
├── references/
│   └── lex-skill-project-structure.md   # source_commit: ""                       ❌ critério (d)
├── extras/
│   └── debug.log                     # arquivo presente, NÃO em files[]            ❌ critério (e)
└── widgets/
    └── dist/
        └── index.js                  # sha256 declarado divergente                 ❌ critério (c)
```

PR contendo este pacote deve ser bloqueado em review por 5 critérios violados simultaneamente.

## Validação Automatizada

- **Ferramenta:** validador Python (futuro) usando `jsonschema` para validar `.skill-manifest.json` e `hashlib.sha256` para conferir cada arquivo declarado; check de arquivos órfãos via diferença entre `os.walk(pacote)` e `manifest.files[]`. Enquanto o validador automático não existe, reviewer humano executa o checklist no PR.
- **Momento:** PR review (humano hoje; futuro Gate 2 via `kata-quality-gate` quando o validador for integrado); CI quando habilitado.
- **Métrica:** 0 PRs merged com pacote `.skill` violando qualquer um dos 5 critérios; 0 entradas com `framework.ahrena_commit` ou `source_commit` vazios; 0 arquivos órfãos.

## Referências

- `codex-skill-anthropic-agent-skills` — frontmatter SKILL.md, naming, file references
- `codex-skill-project-architecture` — estrutura do projeto fonte que produz o pacote
- `codex-skill-tools-and-widgets` — convenção dos manifestos `tools/` e `widgets/`
- `lex-skill-project-structure` — separação fonte/build/dist
- `lex-semantic-version` — versionamento de `skill.version`
- `lex-hard-gate-pattern` — pattern textual aplicado nesta lei
