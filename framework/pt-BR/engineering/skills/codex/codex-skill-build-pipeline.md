# Codex: Pipeline de Build de Skills (Ahrena)

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Pipeline determinístico que lê `skills/{slug}/`, valida manifestos, compila widgets, congela scripts, valida tools e emite `.build/{slug}/` + `.build/{slug}.zip`

## Visão Geral

O build é a ponte entre **fonte** (`skills/{slug}/`, autorada com Pilares Ahrena) e **entrega** (`.dist/{slug}.skill`, formato Anthropic). Ele:

1. Valida `SKILL.md`, `skill.config.json`, manifestos de tools e widgets
2. Compila widgets React (Vite) com source maps configuráveis
3. Congela scripts (lock de dependências) sem instalar runtime alvo
4. Valida `tools/mcp.config.json` e resolve refs de handlers
5. Reescreve paths e bindings para o formato pós-build
6. Emite `.build/{slug}/` com layout pronto para empacotamento (PR 3) e `.build/{slug}.zip` testável manualmente em outro agente

Este codex documenta o **contrato** do pipeline. A implementação operacional vive em `kata-build-skill`. O empacotamento final em `.dist/` (snapshot de refs externas com commit hash, manifesto raiz com hashes) é cobertura de PR 3 (`kata-package-skill`, `lex-skill-export-determinism`).

## Contexto

- **Domínio:** transformação fonte → intermediário (`.build/`); precondição para empacotamento
- **Público-alvo:** `kata-skill-dev-server`, `kata-build-skill`; autores que precisam entender o que esperar do build
- **Atualização:** quando defaults de tooling (Vite, uv, Node) mudarem; quando a estrutura do `.skill-manifest.json` evoluir

## Conteúdo

### Defaults de tooling

| Camada | Ferramenta | Versão alvo | Justificativa |
|--------|------------|-------------|---------------|
| Bundler de widgets | **Vite** | 5.x | Velocidade, zero-config para React + TS, output multi-formato, dev server com HMR |
| Runtime JS de scripts | **Node** | 20 LTS | Estável, suporte ESM nativo |
| Runtime Python de scripts e handlers | **uv** + **Python 3.12** | uv ≥ 0.4 | Alinhado a `codex-python-tooling`; install reprodutível e rápido |
| Empacotador final | `zip` POSIX (BSD/Info-ZIP) | qualquer | Entrega zip testável; `kata-package-skill` (PR 3) define o formato `.skill` final |

`skill.config.json` permite override por projeto (`build.bundler`, `runtimes.scripts`); o pipeline rejeita combinações inconsistentes (ex.: `widgets/` presente sem bundler suportado).

### Ports default no dev server

| Servidor | Porta default | Override | Função |
|----------|--------------:|----------|--------|
| Widgets HMR (Vite) | `5173` | `dev_server.widgets_port` | Renderização e hot reload |
| Script runner | `5174` | `dev_server.scripts_port` | Endpoints HTTP/JSON expondo `scripts/` aos widgets |
| Tool stub MCP | `5175` | `dev_server.tools_stub_port` | Mock local de tools declarados em `tools/mcp.config.json` |

`kata-skill-dev-server` levanta os três sob demanda (somente os necessários ao skill em desenvolvimento).

### Pipeline — fases

```
skills/{slug}/                                    .build/{slug}/
   │
   ├─ Phase 1: Validate
   │     ├─ SKILL.md frontmatter (codex-skill-anthropic-agent-skills)
   │     ├─ skill.config.json (schema_version, runtimes, ports)
   │     ├─ tools/mcp.config.json (handler refs existem, JSON Schema válido)
   │     └─ widgets/manifest.json (entries existem, bindings consistentes)
   │
   ├─ Phase 2: Build widgets (quando widgets/ existe)
   │     ├─ vite build --mode production
   │     ├─ ouput em .build/{slug}/widgets/
   │     └─ manifest.json reescrito apontando para entries compiladas
   │
   ├─ Phase 3: Freeze scripts (quando scripts/ existe)
   │     ├─ Python: uv lock → copy src + uv.lock para .build/{slug}/scripts/
   │     ├─ JS: npm/pnpm lock + copy src + lockfile
   │     └─ paths em scripts mantidos (não compilados)
   │
   ├─ Phase 4: Resolve tools (quando tools/ existe)
   │     ├─ valida cada handler ref (path:funcao existe)
   │     ├─ copia mcp.config.json + handlers/ para .build/{slug}/tools/
   │     └─ reescreve handler refs para paths pós-build (se necessário)
   │
   ├─ Phase 5: Rewrite bindings
   │     ├─ widgets/manifest.json: bindings com kind: script perdem called_via
   │     │   localhost (somente dev) e ganham campo called_via_prod (path
   │     │   resolvido pelo host) ou são marcados como "via_tool" quando
   │     │   o build sugere migração de script→tool
   │     └─ SKILL.md: paths citados em ./scripts/, ./tools/, ./widgets/
   │       conferidos contra arquivos efetivamente emitidos
   │
   ├─ Phase 6: Emit
   │     ├─ SKILL.md (cópia + cabeçalho de aviso de convenção quando há tools/widgets)
   │     ├─ .skill-manifest.json (esqueleto preenchido com hashes — só campos
   │     │   determináveis no build; references[] com snapshots de framework
   │     │   é responsabilidade do PR 3)
   │     └─ {slug}.zip (zip lexicograficamente ordenado; sem timestamps)
   │
   └─ Done
```

### Determinismo no build (intermediário)

Mesmas entradas devem produzir o mesmo `.build/{slug}/` e o mesmo `{slug}.zip`. Regras:

- **Ordering lexicográfico** ao listar arquivos para zip (`zip -X`, `find . | sort`); evita ordem dependente de filesystem
- **Sem timestamps voláteis**: `mtime` dos arquivos no zip é fixado em `1980-01-01` (mínimo do formato) ou no commit hash do `skills/{slug}/` (epoch da última modificação versionada)
- **Sem source maps com paths absolutos**: `source_maps: false` por default em `skill.config.json`; quando `true`, paths são reescritos para relativos à raiz do projeto
- **Vite com mode `production`** sempre; modo dev (com HMR) é exclusivo de `kata-skill-dev-server`
- **Locks copiados, não regenerados**: `uv.lock` / `package-lock.json` da fonte são preservados (não re-resolvidos no build), garantindo reprodutibilidade

Cobertura completa de determinismo (incluindo snapshot de refs externas com commit hash) fica em `lex-skill-export-determinism` (PR 3).

### Cache

`.build/{slug}/` é gitignored. `kata-build-skill` aceita flag `--clean` para apagar e regenerar; sem flag, build incremental quando possível (Vite gerencia cache próprio em `node_modules/.vite/`). Hashes registrados no `.skill-manifest.json` permitem verificar drift posteriormente.

### Hashes em `.skill-manifest.json`

No fim da Phase 6, o build escreve `files[]` com:

```json
{
  "files": [
    { "path": "SKILL.md", "sha256": "..." },
    { "path": "widgets/dist/index.js", "sha256": "..." },
    { "path": "tools/mcp.config.json", "sha256": "..." }
  ]
}
```

`references[]` (snapshots de refs externas do framework) **não** é preenchido neste estágio — é responsabilidade de `kata-package-skill` (PR 3) ao consolidar `.dist/`. PR 2 entrega `references[]: []` no manifest.

### Falhas — modos comuns

| Falha | Causa | Saída esperada |
|-------|-------|----------------|
| `SKILL.md` frontmatter inválido | name/description fora dos limites | Erro citando regras de `codex-skill-anthropic-agent-skills`; build aborta antes de Phase 2 |
| Handler ref inválida em `tools/mcp.config.json` | Path:funcao não existe | Erro listando ref e localização; aborta na Phase 1 |
| Widget entry inválida em `widgets/manifest.json` | Path do entry não existe | Erro com sugestão de correção; aborta na Phase 1 |
| `uv.lock` ausente quando `runtimes.scripts: python` | Lockfile não foi gerado pelo autor | Erro instruindo `uv lock` na pasta `scripts/`; aborta na Phase 3 |
| Vite build falha | Erro de TS strict, import quebrado, etc. | Saída do Vite propagada; aborta na Phase 2 |
| Binding `kind: script` sem `called_via` em dev | Manifesto incompleto | Erro instruindo declarar `called_via`; aborta na Phase 5 |

### Integração com Storybook / Playwright (opcional)

Skills que adotam Storybook ou Playwright em `widgets/` mantêm essas ferramentas como **dev dependencies**; o build não as inclui em `.build/{slug}/`. Stories e specs são parte da fonte (versionada), não da entrega.

## Restrições

- Build é **idempotente**: rodar duas vezes seguidas com fonte inalterada produz `.build/{slug}/` byte-idêntico
- Build **não modifica** `skills/{slug}/` (apenas lê)
- Build **não toca** `.dist/` (responsabilidade do PR 3)
- Pipeline aborta na primeira falha; não tenta seguir parcialmente
- Logs do pipeline seguem `lex-logging-decorator` quando emitidos por handlers Ahrena (boot CLI fica no `kata-build-skill`)

## Glossário

| Termo | Definição |
|-------|-----------|
| Phase | Etapa nomeada do pipeline (Validate, Build widgets, Freeze scripts, Resolve tools, Rewrite bindings, Emit) |
| Freeze | Cópia de `scripts/` com lockfile preservado; sem instalar dependências no `.build/` |
| Tool stub | Mock local da tool, usado pelo dev server; **não** vai para `.build/` |
| Pipeline incremental | Reexecução que aproveita cache de Vite quando válido |

## Referências

- `codex-skill-anthropic-agent-skills` — schema do `SKILL.md` validado em Phase 1
- `codex-skill-tools-and-widgets` — schemas de `mcp.config.json` e `manifest.json`
- `codex-skill-project-architecture` — fluxo dev → build → dist em alto nível
- `codex-python-tooling` — uv como runtime alvo de Python
- `codex-frontend-architecture` — restrições aplicáveis a widgets
- `lex-skill-project-structure` — lei que separa fonte/build/dist
- `lex-skill-export-determinism` (PR 3) — determinismo da entrega final
- `kata-skill-dev-server` — orquestração de dev server que precede o build
- `kata-build-skill` — implementação operacional deste pipeline
