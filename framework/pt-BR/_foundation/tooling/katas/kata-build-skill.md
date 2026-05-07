# Kata: Build de skill (fonte → `.build/{slug}/` + zip)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Implementação operacional do pipeline determinístico de build descrito em `codex-skill-build-pipeline`. Lê `{paths.skills_root}/{slug}/`, valida manifestos, compila widgets, congela scripts, valida tools e emite `{paths.skills_build}/{slug}/` + zip testável

## Objetivo

Produzir um `.build/{slug}/` byte-determinístico (mesma fonte → mesmo output) e um `.build/{slug}.zip` que pode ser carregado em outro agente Claude Code (ou equivalente) para teste manual ponta-a-ponta antes do empacotamento final em `.dist/` (PR 3).

## Quando Usar

- Quando o usuário invoca `/cry-skill-build <slug>`
- Quando integração contínua precisar gerar zip testável
- Antes de invocar `kata-package-skill` (PR 3) para produzir entrega final

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `slug` | Sim | Projeto em `{paths.skills_root}/{slug}/` |
| `clean` | Não | `true` apaga `.build/{slug}/` antes de começar; default `false` (build incremental aproveitando cache do Vite) |
| `skip_zip` | Não | `true` pula a Phase 6 do zip (útil quando o consumidor é só o `kata-package-skill`); default `false` |

## Workflow

```
Progresso:
- [ ] 1. Resolver paths e config
- [ ] 2. Phase 1 — Validate
- [ ] 3. Phase 2 — Build widgets
- [ ] 4. Phase 3 — Freeze scripts
- [ ] 5. Phase 4 — Resolve tools
- [ ] 6. Phase 5 — Rewrite bindings
- [ ] 7. Phase 6 — Emit (.build/ + zip)
- [ ] 8. Validar idempotência
- [ ] 9. Reportar
```

### Passo 1: Resolver paths e config

1. Ler `.ahrena/.directives` para `paths.skills_root`, `paths.skills_build`
2. Confirmar `{paths.skills_root}/{slug}/` existe
3. Ler `skill.config.json`; aplicar overrides
4. Se `clean=true`, remover `{paths.skills_build}/{slug}/` antes de prosseguir
5. Garantir `{paths.skills_build}/{slug}/` existe (criar)

### Passo 2: Phase 1 — Validate

Per `codex-skill-build-pipeline` (Phase 1):

1. **`SKILL.md`**: parse frontmatter; validar `name` (regex spec), `description` (1-1024), `compatibility` (≤500 quando presente), `metadata.version` (semver), `metadata.language` (BCP 47)
2. **`skill.config.json`**: `schema_version: 1`, `runtimes.scripts` em `python|node`, ports presentes
3. **`tools/mcp.config.json`** (quando `tools/` existe): `schema_version: 1`, cada `tools[].name` em snake_case, `tools[].input_schema` é JSON Schema válido, `tools[].handler` aponta para arquivo+função existente
4. **`widgets/manifest.json`** (quando `widgets/` existe): `schema_version: 1`, cada `components[].entry` aponta para arquivo existente, cada `bindings[]` referencia tool ou script existente
5. **`description` no SKILL.md**: avisar (não abortar) se < 30 chars (heurística de qualidade per spec — descrições curtas reduzem ativação)

Em qualquer falha, abortar com erro específico citando a regra (`codex-skill-anthropic-agent-skills` para frontmatter, `codex-skill-tools-and-widgets` para manifests).

### Passo 3: Phase 2 — Build widgets

Quando `widgets/` existe:

1. `cd {paths.skills_root}/{slug}/widgets`
2. Garantir `node_modules/` (rodar `npm install` ou `pnpm install` quando ausente)
3. Executar `vite build --mode production` (config padrão; override via `vite.config.ts` se autor declarou)
4. Output esperado: `widgets/dist/`
5. Copiar `widgets/dist/` para `{paths.skills_build}/{slug}/widgets/`
6. Reescrever `widgets/manifest.json` em `.build/`:
   - `components[].entry` aponta para arquivo compilado correspondente em `dist/`
   - `bindings[]` preservados; rewrite ocorre na Phase 5
7. Copiar `manifest.json` reescrito para `.build/{slug}/widgets/manifest.json`

### Passo 4: Phase 3 — Freeze scripts

Quando `scripts/` existe:

1. Para Python (`runtimes.scripts: python`):
   - Confirmar `scripts/uv.lock` (gerar com `uv lock` quando ausente, abortando se autor não permitiu mutação)
   - Copiar `scripts/src/`, `scripts/pyproject.toml`, `scripts/uv.lock` para `.build/{slug}/scripts/`
2. Para Node (`runtimes.scripts: node`):
   - Confirmar lockfile (`package-lock.json` ou `pnpm-lock.yaml`)
   - Copiar `scripts/src/`, `scripts/package.json`, lockfile para `.build/{slug}/scripts/`
3. Não instalar dependências em `.build/` (o consumidor instala no carregamento)

### Passo 5: Phase 4 — Resolve tools

Quando `tools/` existe:

1. Validar cada `tools[].handler` (path:funcao existe e é callable)
2. Copiar `tools/mcp.config.json` para `.build/{slug}/tools/`
3. Copiar `tools/handlers/` para `.build/{slug}/tools/handlers/` (preservar estrutura)
4. Quando handler é Python e `runtimes.scripts: python`, reusar `uv.lock` de `scripts/` (handlers podem importar de `scripts/src/`)

### Passo 6: Phase 5 — Rewrite bindings

Em `widgets/manifest.json` (já em `.build/`):

1. Para cada binding `kind: script`:
   - Remover `called_via` (URL localhost de dev)
   - Adicionar `called_via_prod`: caminho relativo ao consumidor (default `./scripts/src/{filename}.{ext}`)
   - Quando `skill.config.json.build.prefer_tool_over_script: true`, marcar como `via_tool: true` para que o host invoque a tool MCP equivalente em vez de executar script direto

Em `SKILL.md` (cópia em `.build/{slug}/SKILL.md`):

1. Adicionar cabeçalho de aviso (após o frontmatter, antes do corpo) quando `tools/` ou `widgets/` presente:

   ```markdown
   > **Note:** This skill bundles `tools/` (MCP) and/or `widgets/` (React) as
   > Ahrena convention. Agents that only know the Anthropic Agent Skills spec
   > ignore those directories. See codex-skill-tools-and-widgets in the source
   > framework for binding semantics.
   ```

2. Validar que paths citados no corpo (`scripts/...`, `tools/...`, `widgets/...`) existem em `.build/`

### Passo 7: Phase 6 — Emit (.build/ + zip)

1. Escrever `.build/{slug}/.skill-manifest.json`:
   ```json
   {
     "schema_version": 1,
     "skill": { "name": "{slug}", "version": "...", "language": "..." },
     "framework": { "ahrena_commit": "{HEAD-da-fonte}" },
     "references": [],
     "files": [
       { "path": "SKILL.md", "sha256": "..." },
       { "path": "widgets/dist/index.js", "sha256": "..." },
       ...
     ]
   }
   ```
   `references[]` permanece vazio — preenchido por `kata-package-skill` (PR 3).
   `files[]` listado em ordem **lexicográfica** dos paths.
2. Quando `skip_zip=false`:
   - `mtime` de cada arquivo no zip fixado em `1980-01-01T00:00:00Z` (mínimo do formato)
   - Comando: `cd .build/{slug} && find . -type f | LC_ALL=C sort | zip -X --no-extra -@ ../{slug}.zip` (ou equivalente cross-platform)
   - Output: `{paths.skills_build}/{slug}.zip`

### Passo 8: Validar idempotência

1. Calcular sha256 do `.build/{slug}/{slug}.zip` (ou de toda a árvore quando `skip_zip=true`)
2. Comparar com hash registrado em `.skill-manifest.json` (se houver de execução anterior)
3. Em caso de drift inesperado, alertar — possíveis causas: timestamps não fixados, ordering de filesystem, source maps com paths absolutos

### Passo 9: Reportar

```
✅ Build de {slug} concluído.
   Saída: {paths.skills_build}/{slug}/
   Zip:   {paths.skills_build}/{slug}.zip   (X.X MB)
   sha256: <hash>

Conteúdo:
   - SKILL.md (cabeçalho de aviso adicionado)
   - widgets/dist/ (Vite production)
   - scripts/ (Python uv frozen)
   - tools/ (3 handlers validados)
   - .skill-manifest.json (8 files; references vazias até PR 3)

Próximos passos:
   - Carregar o zip em outro agente Claude Code para teste manual
   - kata-package-skill (PR 3) entrega .dist/{slug}.skill auditável
```

## Saídas

| Saída | Formato |
|-------|---------|
| Sucesso | `.build/{slug}/` populado + zip + manifest com hashes |
| Falha (Phase 1) | Erro específico de validação; nada escrito em `.build/` |
| Falha (Phase 2) | Saída do Vite propagada; build aborta |
| Falha (Phase 3) | Lockfile ausente — instrução para gerar |
| Falha (Phase 4) | Handler ref inválida — apontar para o handler em falta |
| Falha (Phase 5) | Bindings inconsistentes (apontam para arquivo que sumiu) |
| Falha de idempotência | Alerta com causa provável; build sobrevive mas sinaliza investigar |

## Exemplo de Execução

```
/cry-skill-build hello-skill
```

```
✅ Build de hello-skill concluído.
   Saída: .build/hello-skill/
   Zip:   .build/hello-skill.zip   (124 KB)
   sha256: 7a8c…
```

## Restrições

- Build é **somente leitura** sobre `{paths.skills_root}/{slug}/`
- Não toca `.dist/`
- Aborta na primeira falha; nunca emite parcial
- Determinismo é critério não-negociável (`codex-skill-build-pipeline` § "Determinismo no build"); cobertura completa em PR 3 (`lex-skill-export-determinism`)
- Logs de aplicação seguem `lex-logging-decorator`; saída do CLI da kata é exceção (boundary)
- `lex-terminal-type`: comandos shell na sintaxe correta

## Referências

- `codex-skill-build-pipeline` — contrato do pipeline (defaults, fases, determinismo)
- `codex-skill-tools-and-widgets` — schemas validados em Phase 1
- `codex-skill-anthropic-agent-skills` — frontmatter validado em Phase 1
- `codex-skill-project-architecture` — fluxo dev → build → dist
- `codex-python-tooling` — uv como runtime de Python
- `lex-skill-project-structure` — separação fonte/build/dist
- `lex-skill-export-determinism` (PR 3) — determinismo da entrega final
- `cry-skill-build` — atalho do usuário
- `kata-skill-dev-server` — passo anterior natural; valida manualmente antes do build
- `kata-package-skill` (PR 3) — consumidor de `.build/` para produzir `.dist/`
