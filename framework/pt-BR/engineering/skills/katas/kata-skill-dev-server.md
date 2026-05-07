# Kata: Dev server local de skill (widgets HMR + script runner + tools stub)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Levantar ambiente de desenvolvimento local para um projeto de skill em `{paths.skills_root}/{slug}/`, com widgets em HMR (Vite), script runner HTTP/JSON e tool stub MCP, conforme `codex-skill-build-pipeline`

## Objetivo

Permitir iteração rápida em um projeto de skill levantando, em uma única invocação, os três servidores que cobrem widgets, scripts e tools. O kata respeita opt-outs do `skill.config.json` — se o projeto não tem `widgets/`, o servidor de widgets não sobe; idem para scripts e tools.

## Quando Usar

- Quando o usuário invoca `/cry-skill-dev <slug>`
- Antes de rodar `kata-build-skill`, para validar widgets, scripts e tools manualmente
- Quando ajustar bindings em `widgets/manifest.json` e validar `called_via`

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `slug` | Sim | Nome do projeto em `{paths.skills_root}/{slug}/` |
| `widgets_port` | Não | Override de porta dos widgets (default: `skill.config.json` → `dev_server.widgets_port` → `5173`) |
| `scripts_port` | Não | Override de porta do script runner (default: `5174`) |
| `tools_stub_port` | Não | Override de porta do tool stub (default: `5175`) |
| `only` | Não | Subconjunto a levantar (`widgets`, `scripts`, `tools`); default: todos os disponíveis |

## Workflow

```
Progresso:
- [ ] 1. Resolver projeto e config
- [ ] 2. Verificar pré-condições (paths, manifestos, ports livres)
- [ ] 3. Levantar widgets (Vite dev) quando aplicável
- [ ] 4. Levantar script runner quando aplicável
- [ ] 5. Levantar tool stub quando aplicável
- [ ] 6. Reportar URLs e instruções
- [ ] 7. Acompanhar até o usuário sinalizar parar
```

### Passo 1: Resolver projeto e config

1. Ler `.ahrena/.directives` para resolver `paths.skills_root` (default `skills`)
2. Confirmar que `{paths.skills_root}/{slug}/` existe; abortar se não
3. Ler `{paths.skills_root}/{slug}/skill.config.json`; aplicar overrides de input sobre os valores do arquivo
4. Resolver subconjuntos via `only` ou pela presença de `widgets/`, `scripts/`, `tools/`

### Passo 2: Verificar pré-condições

1. Para widgets: confirmar `widgets/package.json`, `widgets/manifest.json`, `widgets/src/`; checar se `node_modules/` existe (rodar `npm install` ou `pnpm install` quando ausente)
2. Para scripts (Python): confirmar `scripts/pyproject.toml` ou `scripts/uv.lock` (executar `uv sync` quando necessário)
3. Para scripts (JS): confirmar `scripts/package.json`; rodar install se ausente
4. Para tools: confirmar `tools/mcp.config.json` válido (JSON Schema de cada tool); confirmar handler refs existentes
5. Verificar disponibilidade de ports (lsof / netstat conforme `lex-terminal-type`); se ocupada, sugerir override

### Passo 3: Levantar widgets (Vite dev) quando `widgets/` existe e `only` permite

1. Comando: `cd {paths.skills_root}/{slug}/widgets && vite --port {widgets_port} --host`
2. Vite carrega `vite.config.ts` (se existir) ou usa defaults; React + TS detectados automaticamente
3. HMR ativo; logs propagados para o usuário
4. URL exposta: `http://localhost:{widgets_port}/`

### Passo 4: Levantar script runner quando `scripts/` existe e `only` permite

Script runner é servidor HTTP/JSON minimal que expõe cada script como endpoint:

| `runtimes.scripts` | Implementação default | Comando |
|--------------------|----------------------|---------|
| `python` | `uv run` + servidor leve (FastAPI ou stdlib http.server) | `cd {paths.skills_root}/{slug}/scripts && uv run python -m skill_runner --port {scripts_port}` (módulo `skill_runner` é parte do scaffold quando o autor opta por Python; quando ausente, kata aponta o autor para `codex-skill-build-pipeline`) |
| `node` | Express/Fastify/server stdlib | `cd {paths.skills_root}/{slug}/scripts && npm run dev:server -- --port {scripts_port}` |

Roteamento:

- Cada arquivo em `scripts/src/` exporta uma função handler nomeada
- Endpoint default: `POST /{filename-sem-extensao}`
- Body: JSON validado pelo runner contra schema (quando declarado em `widgets/manifest.json`)

URL exposta: `http://localhost:{scripts_port}/`

### Passo 5: Levantar tool stub quando `tools/` existe e `only` permite

Tool stub é um servidor MCP local mockado:

1. Lê `tools/mcp.config.json`
2. Para cada tool declarada, expõe endpoint `POST /tools/{tool_name}`
3. Resposta default: eco da entrada com flag `_stub: true`; autor sobrescreve em `tools/handlers/{tool_name}_stub.py` (ou `.js`) quando precisar de comportamento específico
4. URL exposta: `http://localhost:{tools_stub_port}/`

Tool stub é exclusivo do dev — `kata-build-skill` (Phase 4) valida o handler real, não o stub.

### Passo 6: Reportar URLs e instruções

Ao final do bring-up:

```
✅ Dev server ativo para {slug}:
   Widgets:      http://localhost:{widgets_port}/        (HMR Vite)
   Script runner: http://localhost:{scripts_port}/       (Python uv)
   Tool stub:    http://localhost:{tools_stub_port}/    (MCP mock)

Bindings de widgets/manifest.json:
   - TransferForm → tool: validate_amount    (stub em /tools/validate_amount)
   - TransferForm → script: scripts/src/format_currency.py (em /format-currency)

Para parar: Ctrl-C neste terminal.
Para build: /cry-skill-build {slug}
```

### Passo 7: Acompanhar até o usuário parar

1. Manter foreground do processo Vite (HMR principal); script runner e tool stub em background quando suportado pelo terminal
2. Logs de cada servidor são prefixados (`[widgets]`, `[scripts]`, `[tools]`) para facilitar diagnóstico
3. Em caso de crash de qualquer subprocesso, reportar e oferecer reiniciar
4. Ctrl-C encerra todos os subprocessos limpamente

## Saídas

| Saída | Formato |
|-------|---------|
| Sucesso | URLs ativas + foreground com logs até o usuário interromper |
| Falha (projeto inexistente) | Mensagem citando `lex-skill-project-structure` |
| Falha (port ocupada) | Mensagem instruindo override via `--*_port` |
| Falha (manifest inválido) | Mensagem citando `codex-skill-tools-and-widgets` com a regra violada |
| Falha (dependência não instalada) | Mensagem instruindo `uv sync` / `npm install` no diretório correspondente |

## Exemplo de Execução

```
/cry-skill-dev hello-skill
```

```
✅ Dev server ativo para hello-skill:
   Widgets:      http://localhost:5173/
   Tool stub:    http://localhost:5175/
   (sem scripts/ — pulado)

Pressione Ctrl-C para encerrar.
```

## Restrições

- Não modifica `skills/{slug}/` (somente lê)
- Não escreve em `.build/` ou `.dist/`
- Tool stub é **mock**; nunca usado em produção
- Ports default são opinionados; sempre permite override
- Logs respeitam `lex-logging-decorator` quando integrados; CLI boot do kata é exceção permitida (boundary de aplicação)
- `lex-terminal-type`: comandos shell respeitam o terminal definido em `.directives` (bash | powershell)

## Referências

- `codex-skill-build-pipeline` — defaults de tooling, ports, fases do build (precondições do dev server e o que ele simula)
- `codex-skill-tools-and-widgets` — schemas de `mcp.config.json` e `manifest.json` validados pelas pré-condições
- `codex-skill-project-architecture` — fluxo dev → build → dist
- `codex-frontend-architecture` — convenções de Vite e dev server aplicáveis aos widgets
- `lex-skill-project-structure` — lei do layout
- `lex-terminal-type` — terminal e sintaxe de comandos
- `cry-skill-dev` — atalho do usuário
- `kata-build-skill` — passo seguinte natural após validação no dev
