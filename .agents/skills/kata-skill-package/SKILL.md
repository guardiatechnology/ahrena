---
name: kata-skill-package
description: "Empacotar Skill. Empacotamento determinístico de um projeto de skill de {paths.skills_root}/{slug}/ (fonte) para {paths.skills_dist}/{slug}.skill/ (entrega), com manifest, hashes e validação contra lex-skill-package-structure"
---

# Kata: Empacotar Skill

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Empacotamento determinístico de um projeto de skill de `{paths.skills_root}/{slug}/` (fonte) para `{paths.skills_dist}/{slug}.skill/` (entrega), com manifest, hashes e validação contra `lex-skill-package-structure`

## Workflow

```
Progresso:
- [ ] 1. Resolver paths (.ahrena/.directives + overrides)
- [ ] 2. Validar a fonte (kata-skill-validate como pré-condição)
- [ ] 3. Resolver versão/idioma do frontmatter + SHA do framework
- [ ] 4. Copiar fonte → build/{slug}/
- [ ] 5. Materializar dist/{slug}.skill/ a partir do build
- [ ] 6. Gerar .skill-manifest.json (schema_version, skill, framework, references, files)
- [ ] 7. Validar o pacote final contra lex-skill-package-structure
- [ ] 8. Reportar
```

### Passo 1: Resolver paths

1. Ler `.ahrena/.directives`, seção `paths`:
   - `paths.skills_root` (default `skills`)
   - `paths.skills_build` (default `.build`, gitignored)
   - `paths.skills_dist` (default `.dist`, committed)
2. Aplicar overrides recebidos via argumento
3. Verificar que a fonte `{repo_root}/{skills_root}/{slug}/` existe

### Passo 2: Validar a fonte como pré-condição

1. Invocar `kata-skill-validate skill_path={skills_root}/{slug}`
2. Se houver violações com severidade `error`, **abortar** sem escrever em `{skills_build}/` ou `{skills_dist}/`
3. Warnings não bloqueiam — propagar para o relatório final

### Passo 3: Resolver metadados

1. Parsear o frontmatter de `{skills_root}/{slug}/SKILL.md`:
   - `metadata.version` → vai para `manifest.skill.version`
   - `metadata.language` → vai para `manifest.skill.language`
2. Resolver `framework.ahrena_commit` via `git -C {repo_root} rev-parse HEAD`
3. Abortar se o SHA não for resolvível (≥40 chars hex) — `lex-skill-package-structure` proíbe `ahrena_commit` vazio

### Passo 4: Copiar fonte → build

1. Limpar `{repo_root}/{skills_build}/{slug}/` se existir
2. Copiar recursivamente `{skills_root}/{slug}/` → `{skills_build}/{slug}/`, ignorando `__pycache__` e `.DS_Store`
3. Não modificar nada — o build aqui é cópia 1:1 da fonte; transformações (bundle, dependências) ficam a cargo da stack do projeto consumidor, fora do escopo deste kata

### Passo 5: Materializar dist

1. Limpar `{repo_root}/{skills_dist}/{slug}.skill/` se existir
2. Copiar `{skills_build}/{slug}/` → `{skills_dist}/{slug}.skill/` (mesma exclusão de `__pycache__`/`.DS_Store`)

### Passo 6: Gerar `.skill-manifest.json`

Schema canônico (`lex-skill-package-structure`):

```json
{
  "schema_version": 1,
  "skill": {
    "name": "<slug>",
    "version": "<metadata.version>",
    "language": "<metadata.language>"
  },
  "framework": {
    "ahrena_commit": "<HEAD SHA do framework>"
  },
  "references": [
    {
      "kind": "reference",
      "id": "<derivado do path: references/<id>.md>",
      "source_commit": "<ahrena_commit>",
      "snapshot_path": "references/<id>.md",
      "snapshot_sha256": "<sha256 do arquivo>"
    }
  ],
  "files": [
    { "path": ".skill-manifest.json", "sha256": "self" },
    { "path": "SKILL.md", "sha256": "..." },
    { "path": "references/<id>.md", "sha256": "..." },
    ...
  ]
}
```

1. Entrada `.skill-manifest.json` usa o literal `"self"` como sha256 (manifest se referenciando)
2. Demais entradas: SHA-256 hexadecimal do conteúdo binário do arquivo
3. `files[]` ordenado lexicograficamente por `path`
4. `references[]` ordenado por `id`
5. Persistir em `{skills_dist}/{slug}.skill/.skill-manifest.json` com indent=2 e newline final

### Passo 7: Validar o pacote final

Invocar `scripts/skills/package.py` em modo validação (já incluso na pipeline) contra `lex-skill-package-structure`, verificando os 5 critérios:

| Critério | O que verifica |
|----------|----------------|
| (a) frontmatter | `SKILL.md` com `name == slug` e `description ∈ [1, 1024]` |
| (b) manifest | schema_version=1, skill.{name,version,language}, framework.ahrena_commit não-vazio (≥40 hex) |
| (c) files+sha | cada `files[].path` existe e seu sha256 confere (exceto `"self"` para o próprio manifest) |
| (d) references | cada `references[]` com `source_commit` não-vazio + snapshot presente + sha256 confere |
| (e) órfãos | todo arquivo no pacote aparece em `files[]` |

Qualquer falha aqui **bloqueia** o pacote — refazer a partir da fonte; jamais editar `{skills_dist}/` à mão.

### Passo 8: Reportar

1. Caminho do pacote produzido
2. Caminho do manifest
3. Número de arquivos empacotados
4. Lista de violações (vazia em caso de sucesso)
5. Exit code `0` quando o pacote passa em todos os 5 critérios; `1` caso contrário

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Diretório de entrega | `{paths.skills_dist}/{slug}.skill/` | filesystem (committed) |
| Manifest | `{paths.skills_dist}/{slug}.skill/.skill-manifest.json` | filesystem |
| Relatório | texto humano ou JSON | `stdout` |

## Exemplo de Execução

### Input

```
kata-skill-package slug=scheduled-payments-skill
```

### Output esperado

```
✅ package: .dist/scheduled-payments-skill.skill
   manifest: .dist/scheduled-payments-skill.skill/.skill-manifest.json
   files:    18
```

### Conteúdo do `.dist/scheduled-payments-skill.skill/`

```
.dist/scheduled-payments-skill.skill/
├── SKILL.md
├── .skill-manifest.json    # schema_version=1, files[], references[]
├── references/
│   └── REFERENCE.md
├── scripts/
│   └── ...
└── widgets/
    └── ...
```

## Restrições

- O kata é **agnostic ao build**: a lei `lex-skill-package-structure` é explícita — Vite/uv/Node/zip são responsabilidade da stack consumidora. Este kata copia 1:1 da fonte; transformações são responsabilidade externa
- O kata **nunca** modifica `{skills_dist}/` à mão fora do pipeline; reapresentar do zero é o único caminho de remediação
- O kata **não** atualiza `.directives` — apenas lê
- O kata **aborta** se a fonte tiver erros de validação; pacote sobre fonte inválida é proibido
- Para skills com dependências runtime (Python venv, Node node_modules), a resolução fica fora deste kata — declarar limitação em `SKILL.md` ou agendar plano dedicado
