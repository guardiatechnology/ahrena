---
plan_id: "008"
title: "headroom-context-compression"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-06T00:00:00Z"
updated_at: "2026-05-09T00:00:00Z"
---

# Plano: Integração com Headroom (camada local de compressão de contexto)

## Objetivo

Codificar adoção opcional do [Headroom](https://github.com/chopratejas/headroom) no framework Ahrena. Entregar Codex de referência cobrindo instalação, wrap do Claude Code, integração MCP opcional, política de privacidade e interação com Lexis existentes; uma diretiva nova em `.directives` para opt-in por projeto; um Cry de atalho. Independente dos plans 004/005/006/007.

## Contexto

Headroom é uma camada local que comprime tudo que entra no contexto do LLM (tool outputs, logs, RAG chunks, código, JSON, imagens), preservando acurácia (GSM8K 0.870→0.870, TruthfulQA +0.030, SQuAD v2 / BFCL 97%) e oferecendo retrieval reversível (CCR — modelo chama `headroom_retrieve` para puxar bytes originais sob demanda). Reduções reportadas em workloads agênticos reais (e reproduzíveis via `python -m headroom.evals suite --tier 1`): code search 17,765→1,408 (92%), SRE incident debugging 65,694→5,118 (92%), GitHub issue triage 54,174→14,761 (73%), codebase exploration 78,502→41,254 (47%). Apache 2.0, roda local, sem egresso de dados.

Validação documental feita em 2026-05-09 contra README oficial (https://github.com/chopratejas/headroom) e docs `/docs/mcp` e `/docs/failure-learning`. Achados que orientam o plano:

- **Wrap one-liner para Claude Code:** `headroom wrap claude --memory --code-graph` levanta proxy local e injeta `ANTHROPIC_BASE_URL` apontando para ele
- **MCP server — dois modos:**
  - **Local stdio (default):** `headroom mcp install` escreve config diretamente em `~/.claude/settings.json` (Claude Code) ou `~/Library/Application Support/Claude/claude_desktop_config.json` (Claude Desktop). **Não conversa nativamente com o pattern Ahrena `framework/mcp/{server}.json` + merge via `install.py`.** Decisão: capturar empiricamente no smoke test o que `headroom mcp install` escreve e replicar em `framework/mcp/headroom.json` (provável: `{"command": "headroom", "args": ["mcp", "stdio"]}` ou similar). Risco de drift quando o vendor mudar — Codex documenta o risco
  - **HTTP remoto:** `headroom mcp serve --transport http --port 8080`; out of scope deste plan
  - Tools expostas: `headroom_compress`, `headroom_retrieve`, `headroom_stats`
- **Cross-agent memory (`headroom learn`):**
  - Escreve em **dois lugares**: `CLAUDE.md` no projeto **e** `~/.claude/projects/*/memory/MEMORY.md` (mesmo arquivo do auto-memory da harness Claude Code — risco novo)
  - Usa markers HTML próprios `<!-- headroom:learn:start -->` / `<!-- headroom:learn:end -->`. **Não colidem com o bloco AHRENA** mas convivem no mesmo arquivo
  - **Dry-run por default** — só escreve com `--apply`. Reduz drasticamente o risco do step 5: o smoke test inicial é seguro
- **Bundle do RTK — não é colisão de namespace.** Headroom embute o binário [`rtk-ai/rtk`](https://github.com/rtk-ai/rtk), o **mesmo** RTK que o usuário deste repo já tem instalado (`/usr/local/bin/rtk` v0.38.0 confirmado em 2026-05-09; declarado em `~/.claude/RTK.md` global como token-killer). Risco real é **divergência de versão** (Headroom pode bundlar versão diferente e prepend no PATH, sobrepondo a v0.38.0) e **interação com hook RTK do user** (mencionado em RTK.md global mas não localizado em `~/.claude/settings.json` — pode estar em outro caminho de hook ou inativo). Codex documenta `which rtk` + `rtk --version` antes/depois do `headroom wrap` para diagnóstico
- **Extras enxutos:** `pip install "headroom-ai[proxy,mcp]"` cobre wrap+MCP sem baixar Kompress-base (~100MB+); `[all]` inclui o modelo ML. Codex documenta ambos
- **Combinação com plan-007:** Headroom reduz custo; plan-007 estampa o custo. Se ambos ativos, o stamp mostra a economia real

Decisões fechadas:

1. **Adoção:** opt-in via `.directives.tooling.headroom.enabled: true`. Default `false` — não levantar proxy/setar env vars sem declaração explícita do projeto
2. **MCP:** **reusar a diretiva `mcp.servers` existente.** Não criar flag separada. Headroom ganha um arquivo `framework/mcp/headroom.json` (mesmo padrão de `github.json`/`notion.json`/`figma.json`); usuário ativa adicionando `headroom` em `mcp.servers` em `.directives`. `lex-mcp` já cobre o resto. Conteúdo do JSON é **derivado empiricamente** do que `headroom mcp install` escreve — Codex documenta como atualizar quando o vendor mudar
3. **Memory:** `--memory` é trade-off, não recomendação default. Codex apresenta as duas opções honestamente:
   - **`--memory` ativo:** Headroom escreve em `~/.claude/projects/*/memory/MEMORY.md` (mesmo arquivo do auto-memory da harness Claude Code). **Não há flag de redirect útil** — `headroom learn --claude-dir <path>` isola mas então o agente não lê de volta (anula o benefício). Risco de colisão real existe; smoke test do step 6 valida na prática
   - **`--memory` desativado:** sem cross-agent learning, mas auto-memory da harness fica intocado. Caminho conservador para projetos com auto-memory ativo
   
   Codex deixa explícito (a) flags reais do `learn` (`--project`, `--all`, `--apply`, `--agent`, `--model`, `--workers`, `--claude-dir`); (b) markers do Headroom não invadem o bloco AHRENA mas convivem no mesmo `CLAUDE.md`; (c) dry-run é default — sempre revisar diff antes de `--apply`
4. **Code graph:** off por default (custo computacional maior); opt-in via flag
5. **Privacy:** documentar a claim de zero egresso e como verificar (proxy local, ausência de chamadas outbound para domínios não-LLM); validação por `tcpdump`/firewall fica a cargo do projeto adotante
6. **Sequenciamento com plan-022:** plan-022 entrega `codex-token-optimization` (manual mestre das 6 técnicas) e `lex-token-budget` (HARD-GATE com campo `token_budget` no frontmatter). **Plan-022 mergeia ANTES de plan-008.** Plan-008 não cria um Codex paralelo de "como otimizar tokens" — `codex-headroom` é Codex de **tooling** (`_foundation/tooling/codex/`), específico da ferramenta, e referencia `codex-token-optimization` como manual mestre. Reciprocamente, `codex-token-optimization` lista Headroom entre as técnicas e linka para `codex-headroom`. Quando `lex-token-budget` estiver ativa, `codex-headroom` declara `token_budget` no frontmatter como qualquer outro artefato

## Escopo

### Artefatos a criar (3 idiomas)

| Pilar | Arquivo | Conteúdo principal |
|---|---|---|
| Codex | `_foundation/tooling/codex/codex-headroom.md` | **Codex de tooling, NÃO de estratégia** — referencia `codex-token-optimization` (plan-022) como manual mestre. Conteúdo específico: conceito de context compression e CCR; instalação (`pip install "headroom-ai[all]"` para tudo, `[proxy,mcp]` para wrap+MCP sem ML local; requisitos: Python 3.10–3.13); modos de uso (wrap CLI, SDK Python/TS, proxy, MCP, middleware ASGI); comando `headroom wrap claude --memory [--code-graph]`; verificação de funcionamento; integração MCP via `lex-mcp` (e nota sobre drift do JSON de config); referência ao `ahrena_*` MCP server do plan-021 como caminho cirúrgico para consulta de Lexis em sessão comprimida; risco de cadeia com plan-023 (tradução via LLM em rota Headroom-comprimida); política de privacidade local; **convivência com bloco AHRENA em CLAUDE.md** (markers Headroom `<!-- headroom:learn:start/end -->` vs AHRENA — diferentes, coexistem); **`headroom learn` é dry-run por default** — sempre revisar antes de `--apply`; interação com `~/.claude/projects/*/memory/MEMORY.md` da harness Claude Code; divergência de versão com `rtk-ai/rtk` v0.38.0 pré-instalado (`which rtk` + `rtk --version`); benchmarks com fonte oficial e reprodutor (`python -m headroom.evals suite --tier 1`); link para `/docs/failure-learning`; limitações conhecidas e quando NÃO usar (sessões muito curtas onde overhead supera ganho); `token_budget` no frontmatter conforme `lex-token-budget` (plan-022) |
| Cry | `_foundation/tooling/cries/cry-claude-with-headroom.md` | Atalho que invoca `headroom wrap claude` com flags lidas de `.directives.tooling.headroom.*`; valida que `tooling.headroom.enabled: true` antes de levantar proxy |

### Atualizações em artefatos existentes (3 idiomas)

| Arquivo | Mudança |
|---|---|
| `framework/.directives.sample` | Adicionar bloco comentado: `tooling.headroom.{enabled,wrap_command,memory,code_graph}`. Default `enabled: false`. **Não inclui flag MCP** — ativação MCP é via `mcp.servers` existente |
| `framework/mcp/headroom.json` (novo) | Config de servidor MCP no padrão dos demais (github/notion/figma): `command`/`args` para Cursor e Claude Code. A linha exata (`headroom mcp serve` ou equivalente) é confirmada no smoke test antes da redação |
| `_foundation/process/lexis/lex-directives.md` | Adicionar `tooling.headroom.*` à tabela "Application by section" |
| `framework/platforms.yaml` | Registrar `_foundation/tooling/codex/codex-headroom` e o cry em `cursor.rules`/`claude-code.rules` com `paths: ["~/.headroom/**", ".headroom/**"]` para lazy-load (Headroom guarda config em `~/.headroom/`) |

**Observação:** `lex-mcp` **não precisa de mudança** — a regra existente ("agent MUST NOT use MCP servers not listed in `mcp.servers`") já governa Headroom como qualquer outro server. Codex apenas referencia.

### Estrutura da diretiva proposta

```yaml
# ─── Headroom (Context Compression) ──────────────────────────────
# Local proxy/library that compresses tool outputs, logs, code, and
# RAG chunks before they reach the LLM. Reversible (CCR). Claims
# zero data egress and ~50-90% token reduction on agentic workloads.
# To enable Headroom MCP tools (headroom_compress, headroom_retrieve,
# headroom_stats), add 'headroom' to the existing `mcp.servers` list
# above — same mechanism as github/notion/figma (governed by lex-mcp).
# See codex-headroom for setup and limitations.

# tooling:
#   headroom:
#     enabled: false              # true | false
#     wrap_command: claude        # claude | codex | cursor | aider | copilot
#     memory: true                # use --memory (cross-agent learning)
#     code_graph: false           # use --code-graph (codebase intel)
```

## Fora de escopo

- **Headroom como dependência obrigatória** — adoção segue opcional; sem nova Lexis
- **Implementação ou patches no Headroom** — só integramos a CLI oficial
- **Validação independente dos benchmarks** — codex cita números do vendor com data e fonte; auditoria de benchmarks própria fica fora do framework
- **Integração com Cursor IDE neste plan** — codex menciona `headroom wrap cursor` mas o cry foca em Claude Code. Cursor pode ganhar cry próprio em iteração futura
- **Cross-agent memory entre Claude Code e Codex** — recurso do Headroom; codex documenta mas não introduz Lexis sobre isso

## Steps

- [x] 0. **Validação documental** (feita 2026-05-09): README oficial + `/docs/mcp` + `/docs/failure-learning` confirmados. Achados consolidados na seção *Contexto*. Pendentes empíricos: (a) JSON exato escrito por `headroom mcp install`; (b) impacto real em workload representativo; (c) verificação de coexistência markers Headroom × AHRENA × MEMORY.md
- [ ] 1. Abrir issue guarda-chuva no repo `guardiatechnology/ahrena`
- [ ] 2. Criar branch `feat/{N}-headroom-integration` e worktree
- [ ] 3. Atualizar status deste plan para `in-progress`
- [ ] 4. Smoke test prévio: `pip install "headroom-ai[all]"` (ou `[proxy,mcp]` para versão enxuta) no ambiente, rodar `headroom wrap claude --memory` num projeto sandbox, validar que a sessão Claude Code sobe contra o proxy local. Capturar tokens before/after numa interação representativa
- [ ] 5. **Capturar config MCP empiricamente:** rodar `headroom mcp install` em ambiente sandbox e capturar **(a)** o JSON exato escrito em `~/.claude/settings.json` (mcpServers.headroom); **(b)** se há env vars necessárias; **(c)** se o comando aceita stdio puro. Esse output é a base de `framework/mcp/headroom.json`
- [ ] 6. Validar coexistência em `CLAUDE.md`: rodar uma sessão Claude Code com Headroom, invocar `headroom learn` **sem `--apply`** (dry-run), conferir o diff proposto. Confirmar que markers `<!-- headroom:learn:start/end -->` não invadem o bloco AHRENA. Repetir para `~/.claude/projects/*/memory/MEMORY.md` — registrar se Headroom respeita conteúdo pré-existente do auto-memory da harness
- [ ] 7. Criar `framework/mcp/headroom.json` espelhando o capturado no step 5, com nota explicando como atualizar quando o vendor mudar
- [ ] 8. Redigir `codex-headroom` em pt-BR (instalação com extras enxutos vs. completos, wrap, MCP via `mcp.servers` + risco de drift do JSON, memory + dry-run obrigatório antes de `--apply`, interação com MEMORY.md da harness, code-graph, privacidade, RTK collision, coexistência markers, benchmarks com fonte oficial e reprodutor, link para `/docs/failure-learning`, limitações)
- [ ] 9. Traduzir `codex-headroom` para `es` e `en`
- [ ] 10. Redigir `cry-claude-with-headroom` em pt-BR
- [ ] 11. Traduzir cry para `es` e `en`
- [ ] 12. Atualizar `framework/.directives.sample` com bloco `tooling.headroom` (sem flag MCP) e nota orientando a adicionar `headroom` em `mcp.servers` quando quiser as MCP tools
- [ ] 13. Atualizar `lex-directives.md` (3 línguas) na tabela
- [ ] 14. Adicionar entries em `framework/platforms.yaml`
- [ ] 15. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e equivalente Cursor
- [ ] 16. Smoke test final (sem MCP): ativar `tooling.headroom.enabled: true`, rodar o cry, validar proxy
- [ ] 17. Smoke test final (com MCP): adicionar `headroom` em `mcp.servers`, rerodar `install.py`, validar que `.cursor/mcp.json` e `.claude/settings.json` recebem o config de Headroom mergeado e que `headroom_compress`/`headroom_retrieve`/`headroom_stats` aparecem na sessão
- [ ] 18. Commits atômicos por artefato; subject em inglês + body bilíngue; assinados
- [ ] 19. Push e abrir PR via `kata-contributing-pr` (com stamp do plan-007 se já tiver mergeado)
- [ ] 20. Após merge: arquivar plan e remover worktree

## Dependências

- **plan-022 mergeado antes deste plan** — `codex-token-optimization` precisa existir para que `codex-headroom` possa referenciá-lo como manual mestre; `lex-token-budget` precisa estar ativa para que `codex-headroom` declare `token_budget` no frontmatter desde o nascimento
- Python 3.10–3.13 disponível no ambiente do step 4 (verificar com `python3 --version`)
- `pip` ou `pipx` para instalar `headroom-ai` (extras `[proxy,mcp]` para enxuto, `[all]` para Kompress-base + ML stack)
- `gh` CLI autenticado
- Rede para baixar Kompress-base do HuggingFace na primeira execução (modelo ~100MB+) — só se `[all]` ou `[ml]`
- Acesso à doc oficial https://headroom-docs.vercel.app/docs e ao repo https://github.com/chopratejas/headroom durante a redação
- Independente dos plans 004/005/006/007 — pode rodar em qualquer ordem em relação a esses
- **Cross-link recíproco com plan-022**: quando este plan executar, atualizar `codex-token-optimization` (criado por 022) listando Headroom como técnica e linkando para `codex-headroom`

## Riscos

- **Benchmarks reportados podem não refletir os workloads reais do projeto.** Mitigação: codex cita números com fonte oficial (README do repo) e o reprodutor `python -m headroom.evals suite --tier 1`. Smoke test no step 4 mede impacto real numa interação representativa antes da adoção ampla
- **Headroom proxy quebrar em algum modelo/cliente menos comum.** Mitigação: codex declara explicitamente os modelos validados (Anthropic via `claude` wrap); outros ficam best-effort
- **Divergência de versão RTK entre Headroom-bundled e o `rtk-ai/rtk` já instalado pelo user.** Não é colisão de namespace (mesma origem) mas Headroom pode prepend sua cópia no PATH e sobrepor a versão do user (caso confirmado no ambiente do mantenedor: `/usr/local/bin/rtk` v0.38.0 em macOS). Mitigação: codex documenta o diagnóstico **cross-platform** (`which rtk` em bash/zsh, `Get-Command rtk` em PowerShell; `rtk --version` em ambos), e `rtk gain` para comparar telemetria do token-killer antes/depois do `headroom wrap`. Localização do hook RTK ativo no IDE/CLI fica a cargo do projeto adotante (varia entre macOS, Linux e Windows — paths diferentes para `~/.claude/`, `~/Library/Application Support/`, `%APPDATA%`); codex enumera os caminhos típicos sem prescrever um único
- **`framework/mcp/headroom.json` ficar defasado em relação ao JSON real escrito por `headroom mcp install`.** Mitigação: step 5 captura empiricamente o output corrente; codex documenta exatamente como recapturar e atualizar quando o vendor mudar a config. Risco residual aceito — Headroom é vendor externo
- **`headroom learn --apply` colidindo com o auto-memory da harness Claude Code no `~/.claude/projects/*/memory/MEMORY.md`.** Investigado em 2026-05-09: as flags reais são apenas `--project`, `--all`, `--apply`, `--agent`, `--model`, `--workers`, `--claude-dir`. **Não existe `--memory-path`/`--output`/`--memory-file`.** `--claude-dir` redireciona toda a estrutura mas **anula o benefício** (agente da harness só lê do default `~/.claude/`). Mitigação real é binária: (a) aceitar o risco — dry-run default já protege, smoke test do step 6 valida coexistência de markers Headroom (`<!-- headroom:learn:start/end -->`) com o índice da harness e a regeneração de ambos os lados; (b) não usar `--memory` no `headroom wrap`, perdendo cross-agent learning. Codex apresenta as duas saídas honestamente, sem recomendar uma como universal
- **`headroom learn` adicionar bloco em `CLAUDE.md` ao lado do bloco AHRENA.** Mitigação: markers são distintos (`headroom:learn:` vs `AHRENA`) e ambos são marker-based — coexistem sem invasão. Codex documenta a coexistência e recomenda revisar o `CLAUDE.md` antes do commit
- **MCP integration aumentar superfície de ataque.** Mitigação: opt-in via `mcp.servers` (não-default); mesmo controle que outros servers MCP via `lex-mcp`
- **Privacidade — claim de "zero data egress" não auditada por nós.** Mitigação: codex cita a claim com fonte; recomenda validação em `tcpdump`/firewall por times sensíveis; não fazemos auditoria
- **Custo computacional do Kompress-base local (~100MB+, cold start).** Mitigação: codex documenta extras enxutos `[proxy,mcp]` (sem o modelo ML) como alternativa para times que não precisam de compressão de texto livre
- **Compressão em cadeia com plan-023 (i18n runtime via MCP) pode degradar fidelidade da tradução.** Plan-023 traduz `pt-BR` → `es`/`en` via LLM em runtime; se Headroom estiver wrappando o Claude Code do projeto adotante, o source pt-BR passa pelo proxy comprimido **antes** da tradução, alterando o input que o tradutor LLM recebe. Mitigação: codex documenta o cenário; recomenda projetos que adotam plan-023 validarem empiricamente a paridade es/en com vs sem Headroom; oferece duas saídas (a) desativar Headroom em rotas de tradução, (b) usar SDK direto (sem proxy) para chamadas de tradução. Cross-link recíproco esperado em plan-023 quando ele for implementado
- **Sobreposição com plan-021 (Ahrena MCP server) no `mcp.servers`.** Não é conflito direto — `mcp.servers` aceita N entries — mas Codex deve referenciar plan-021: para consultar Lexis/Codex durante uma sessão Headroom-comprimida, o Ahrena MCP server é o caminho cirúrgico (em vez de o agente fazer grep, que seria comprimido pelo Headroom)

## Verificação

1. **Pré-requisito plan-022:** `codex-token-optimization` e `lex-token-budget` mergeados; `codex-headroom` referencia o primeiro e declara `token_budget` no frontmatter
2. **Estrutura:** 2 artefatos novos (codex + cry) × 3 línguas = 6 arquivos + 1 `framework/mcp/headroom.json`
3. **Diretiva:** bloco `tooling.headroom` presente em `.directives.sample` com `enabled: false` default e **sem** flag MCP redundante
4. **CLAUDE.md auto-gerado:** lista `_foundation/tooling/codex-headroom.md`
5. **MCP via diretiva existente:** adicionar `headroom` a `mcp.servers` é o único passo para ativar as MCP tools — `lex-mcp` rege automaticamente
6. **Cross-reference:** `lex-directives.md` atualizado nas 3 línguas; `lex-mcp.md` **não modificado** (regra existente já cobre); `codex-token-optimization` (plan-022) atualizado listando Headroom; `codex-headroom` aponta para plan-021 (Ahrena MCP server) e cita risco com plan-023 (i18n runtime)
7. **Smoke test (sem MCP):** sessão Claude Code wrappada produz output funcional, com redução de tokens visível em workload representativo. Comparativo `rtk gain` antes/depois capturado para detectar interação com o token-killer pré-instalado
8. **Smoke test (com MCP):** quando `headroom` em `mcp.servers`, `install.py` mergeia `framework/mcp/headroom.json` em `.cursor/mcp.json` e `.claude/settings.json`; `headroom_compress`/`headroom_retrieve`/`headroom_stats` aparecem na sessão
9. **AHRENA markers preservados:** `headroom learn` (com `--apply`) não invade o bloco AHRENA do `CLAUDE.md`; markers `headroom:learn:` ficam em região distinta. Inclusive teste em `~/.claude/projects/*/memory/MEMORY.md` para detectar interação com auto-memory da harness
10. **RTK convivência (cross-platform):** `rtk --version` antes e depois do wrap registrado em macOS (smoke test do mantenedor); codex documenta o equivalente em Linux (idem bash/zsh) e Windows (`Get-Command rtk`, `rtk --version` em PowerShell). Registrar se Headroom prepend-ou no PATH ou respeitou a versão pré-instalada
11. **Regressão zero:** projetos com `tooling.headroom.enabled: false` (default) não veem mudança
12. **PR:** body referencia `Closes #{N}`; HARD-GATE de `lex-pr-quality` atendido
