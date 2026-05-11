---
plan_id: "027"
title: "warrior-janus-release-orchestrator"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#88"
created_at: "2026-05-08T00:00:00Z"
updated_at: "2026-05-10T00:00:00Z"
---

# Plano: warrior-janus — Orquestrador de Release com Annotated Tags

## Objetivo

Criar `warrior-janus`, primeiro warrior dedicado a fechar o ciclo de entrega: analisa Conventional Commits desde a última tag, propõe bump SemVer + changelog, **aguarda aprovação humana** e então publica annotated tag assinada + GitHub Release. Codifica em nova `lex-annotated-tags` a regra "toda tag remota MUST ser annotated + assinada" e adiciona camada de enforcement server-side (GitHub Action) que rejeita tags lightweight publicadas. Resolve dor concreta: hoje a decisão de versão e a redação do changelog são manuais, propensas a erro, e a Lexis exige tag assinada mas não annotated — uma tag lightweight assinada não existe.

## Contexto

### Por que agora

- `lex-signed-commits` já exige tags assinadas, mas só `git tag -a -s` (annotated) suporta assinatura — uma "lightweight signed tag" é tecnicamente impossível, então a regra atual tem um gap não codificado.
- `kata-tag` e `cry-tag` existem para criar tags, mas nada calcula a próxima versão, gera changelog, ou valida estado do trunk antes do release.
- O padrão "warrior especialista + gate humano" (espelha `warrior-athena` Gate 1/Gate 2) ainda não cobre o momento "fechar release".
- Releases acontecem em frequência baixa mas o custo de erro é alto (versão errada, changelog vazio, tag não assinada que escapa para `origin`).

### Decisões já alinhadas com o usuário

1. Regra "annotated + assinada para toda tag remota" → **nova `lex-annotated-tags`** (não estende `lex-semantic-version`; assunto distinto, separação semântica clara).
2. Enforcement server-side (GitHub Action) **incluído neste plano** — não fica para plano separado.
3. Janus é orquestrador fino: dois katas (`prepare` + `publish`) com gate humano explícito entre eles. Cry `cry-release` é o entrypoint.
4. **Janus NUNCA cria a GitHub Release.** A Release é criada automaticamente pelo workflow `release.yml` quando a tag `v*` é empurrada para `origin`. Janus só atualiza as notas via `gh release edit` **depois** que o workflow conclui. Detalhes em "Lições aprendidas" abaixo.

### Lições aprendidas (v0.11.0 / PR #68 — 2026-05-09)

A v0.11.0 foi a primeira release deste repositório criada com assistência do agente. O fluxo executado revelou um anti-padrão que MUST estar codificado em Janus:

**O que aconteceu:**

1. Agente assinou e empurrou a tag `v0.11.0` (correto).
2. O workflow `.github/workflows/release.yml` disparou no `push tags: ['v*']`, fez o zip dos artefatos e criou a Release com notas auto-geradas (`generate_release_notes: true`, autor `github-actions[bot]`).
3. Agente, sem saber do workflow, tentou `gh release create v0.11.0 ...` com notas customizadas → **falhou com HTTP 422** (`tag_name was used by an immutable release`).
4. Agente caiu para `gh release edit v0.11.0 --notes-file ...` para sobrescrever o body — funcionou, mas saiu do padrão das releases anteriores (que mantêm o body auto-gerado).

**Regra para Janus (e qualquer agente de release):**

- **NEVER** invocar `gh release create` quando o repositório-alvo tem um workflow do tipo `on: push: tags: ['v*']` que já cria a Release. Isso é o padrão em todos os repositórios Guardia que adotam Ahrena.
- **MUST** detectar a presença do workflow (existência de `.github/workflows/*release*.yml` com trigger por tag) **antes** de decidir entre "criar via API" e "deixar o workflow criar".
- **MUST** aguardar o workflow concluir antes de tentar editar as notas. Em runners rápidos a Release aparece em poucos segundos, mas há janela de corrida; a forma robusta é polar `gh run list --workflow release.yml --commit <sha> --json status,conclusion`.
- **MUST** preservar a Release auto-gerada por padrão. Só sobrescrever via `gh release edit` quando o `kata-release-prepare` tiver produzido um changelog substancialmente mais informativo do que o auto. Caso contrário, deixar o auto.
- **MUST** registrar no log do `kata-release-publish` qual caminho foi seguido ("auto preserved" ou "auto overwritten with custom notes") — auditável.

**Anti-padrão a documentar nos exemplos do warrior e do kata:**

```
# ❌ INCORRETO (causa HTTP 422 quando workflow cria Release antes)
git push origin v1.2.3
gh release create v1.2.3 --notes-file ./changelog.md

# ✅ CORRETO (espera o workflow + edita só se necessário)
git push origin v1.2.3
gh run watch $(gh run list --workflow release.yml --commit $(git rev-parse v1.2.3) \
                  --limit 1 --json databaseId --jq '.[0].databaseId')
# Workflow concluiu; Release foi criada automaticamente.
# Só edita as notas se o changelog do kata-release-prepare for mais informativo.
gh release edit v1.2.3 --notes-file ./changelog.md
```

### Mapeamento de fluxo

```
cry-release
  └─→ warrior-janus
        ├─→ kata-release-prepare
        │     ├─ git fetch --tags
        │     ├─ identifica última tag (git describe --tags --abbrev=0)
        │     ├─ analisa commits desde a tag (git log --pretty)
        │     ├─ classifica Conventional Commits → propõe bump (major | minor | patch)
        │     ├─ gera changelog draft agrupado por tipo (feat / fix / docs / ...)
        │     ├─ checa trunk state (CI verde, sem PRs abertos do milestone)
        │     └─ apresenta proposta ao humano
        │
        ├─→ [GATE HUMANO] aprovação explícita
        │
        └─→ kata-release-publish (só após aprovação)
              ├─ invoca kata-tag (-a -s)
              ├─ git push origin <tag>
              ├─ DETECTA workflow de release no repo-alvo (.github/workflows/*release*.yml com trigger por tag)
              ├─ SE workflow existe → aguarda conclusão via `gh run watch <run-id>`; Release é criada por github-actions[bot]
              │       └─ opcional: `gh release edit` para sobrescrever notas com o changelog do prepare (apenas se mais informativo)
              ├─ SE workflow NÃO existe → fallback `gh release create --notes-file <changelog>` (caminho legado)
              └─ verifica que Action validate-tag passou
```

## Escopo

### Artefatos a criar (todos em pt-BR + es + en por `lex-framework-language`)

| # | Tipo    | Nome                       | Path                                                                              |
|---|---------|----------------------------|-----------------------------------------------------------------------------------|
| 1 | Lexis   | `lex-annotated-tags`       | `framework/{lang}/_foundation/contributing/lexis/lex-annotated-tags.md`           |
| 2 | Kata    | `kata-release-prepare`     | `framework/{lang}/_foundation/contributing/katas/kata-release-prepare.md`         |
| 3 | Kata    | `kata-release-publish`     | `framework/{lang}/_foundation/contributing/katas/kata-release-publish.md`         |
| 4 | Warrior | `warrior-janus`            | `framework/{lang}/_foundation/contributing/warriors/warrior-janus.md`             |
| 5 | Cry     | `cry-release`              | `framework/{lang}/_foundation/contributing/cries/cry-release.md`                  |

### Artefatos a atualizar

| # | Tipo     | Nome                       | Mudança                                                                          |
|---|----------|----------------------------|----------------------------------------------------------------------------------|
| 6 | Kata     | `kata-tag`                 | Reforçar uso de `-a -s` (annotated + signed); referenciar `lex-annotated-tags`   |
| 7 | Lexis    | `lex-semantic-version`     | Adicionar referência cruzada para `lex-annotated-tags` na seção "Tags em Git"    |
| 8 | Config   | `framework/platforms.yaml` | Registrar `lex-annotated-tags` em `cursor.rules` (`lex-platforms-rules`)         |

### Enforcement server-side

| # | Arquivo                                  | Descrição                                                                                          |
|---|------------------------------------------|----------------------------------------------------------------------------------------------------|
| 9 | `.github/workflows/validate-tag.yml`     | Roda em `on: push: tags: ['*']`. Falha + apaga tag remota se `git cat-file -t $TAG != "tag"`.     |

Pre-push hook local **fora de escopo deste plano** (depende de hook framework que ainda não temos; fica para plano futuro). Mitigação suficiente: Action server-side autoritativa.

## Steps

- [x] **1. Issue** — issue #88 aberta em guardiatechnology/ahrena com template feature-request, label `feature request ➕`, type Feature, assignee fernandoseguim, Why/What/How preenchidos
- [x] **2. Worktree** — `feat/88-warrior-janus-release-orchestrator` criada em `.worktrees/88-warrior-janus-release-orchestrator/`
- [x] **3. Lexis `lex-annotated-tags`** — criada em pt-BR com HARD-GATE bloqueando lightweight + assinatura + SemVer
- [x] **4. Tradução `lex-annotated-tags`** — versões es e en criadas
- [x] **5. Atualizar `framework/platforms.yaml`** — `_foundation/contributing/lexis/lex-annotated-tags` registrada nas seções cursor.rules e claude-code.rules
- [x] **6. Kata `kata-release-prepare`** — criado em pt-BR com regras de bump, classificação CC, template de changelog
- [x] **7. Tradução `kata-release-prepare`** — versões es e en criadas
- [x] **8. Kata `kata-release-publish`** — criado em pt-BR com detecção de workflow, antipadrão v0.11.0, exemplo correto/incorreto
- [x] **9. Tradução `kata-release-publish`** — versões es e en criadas
- [x] **10. Atualizar `kata-tag`** — `-a -s` reforçado em pt-BR/es/en com exemplos lightweight (incorreto) e cross-link
- [x] **11. Atualizar `lex-semantic-version`** — cross-link para `lex-annotated-tags` em pt-BR/es/en (rule 3 + Referências)
- [x] **12. Warrior `warrior-janus`** — criado em pt-BR (Identidade Janus bifronte, gate humano explícito, exemplo de interação completa)
- [x] **13. Tradução `warrior-janus`** — versões es e en criadas
- [x] **14. Cry `cry-release`** — criado em pt-BR com flags `--type` e `--dry-run`
- [x] **15. Tradução `cry-release`** — versões es e en criadas
- [x] **16. Workflow `validate-tag.yml`** — criado em `.github/workflows/`. Job verifica `git cat-file -t` (lightweight check), pattern SemVer regex, signature best-effort, deleta tag remota em caso de falha
- [x] **17. Sync platforms** — `install.py --self --platform claude-code` e `--platform cursor` executados; 147 docs / 71 skills / 18 agents / 39 commands gerados; YAML validados
- [ ] **18. Validação local** — `cry-release --dry-run` em ambiente real requer agente em sessão futura (artefatos são documentação-como-orquestração; teste verdadeiro só com agent runtime); validação estrutural feita via sync + YAML lint
- [ ] **19. Validação Action** — teste server-side de lightweight tag será executado **após merge na main** (Action só dispara em push de tag para `origin`; testar antes implica gerar tag de teste no remoto)
- [ ] **20. Commit + PR** — pendente

## Dependências

- **Pré-requisitos (existentes):**
  - `lex-semantic-version`, `lex-signed-commits`, `lex-conventional-commits` (regras já vigentes)
  - `kata-tag`, `cry-tag` (operações de tag)
  - `kata-mcp-github-read` e tooling MCP github para criar Release
  - `templates/lex-sample.md`, `templates/kata-sample.md`, `templates/warrior-sample.md`, `templates/cry-sample.md`
- **Ambiente:** MCP `github` ativo em `.ahrena/.directives` (já listado); GPG configurado (`kata-setup-gpg-signing`)
- **Sem dependência de plano em andamento** — plan-027 é independente dos plans 022–026

## Riscos

| # | Risco                                                                                          | Probabilidade | Mitigação                                                                                                                          |
|---|------------------------------------------------------------------------------------------------|:-------------:|------------------------------------------------------------------------------------------------------------------------------------|
| 1 | Heurística de bump SemVer falha em commits mal escritos (`feat:` que é `fix:`, etc.)           | Média         | Gate humano explícito é o ponto de correção; cry aceita `--type` para override                                                     |
| 2 | Action server-side é reativa: tag chega ao remoto antes de ser apagada, dispara outras Actions | Baixa         | Adicionar `if: github.event.head_commit` ou similar nos outros workflows; documentar no `lex-annotated-tags`                       |
| 3 | Multilingue incompleto: criar só em pt-BR e esquecer es/en quebra `lex-framework-language`     | Média         | Steps explicitamente separados por língua; checklist de PR cobre as 3 línguas                                                      |
| 4 | `kata-release-prepare` infere mal o "trunk state" (PRs abertos legitimamente fora do release)  | Baixa         | Verificação só de CI verde no commit alvo + listagem informativa de PRs abertos (não bloqueante); humano decide                    |
| 5 | Releases pré-existentes (lightweight) ficam no histórico                                       | Certa         | Não migrar retroativamente (decidido na conversa); apenas declarar a regra como forward-looking; documentar em `lex-annotated-tags`|
| 6 | GitHub Release via MCP falha por permissão/escopo do token                                     | Baixa         | `kata-release-publish` detecta falha e instrui rollback (apagar tag local + remota) ou fallback para `gh release create`           |
| 7 | Race condition: agente tenta `gh release create` enquanto o workflow `release.yml` ainda está executando, recebe HTTP 422 | Alta (sem mitigação) | Confirmado em v0.11.0. `kata-release-publish` MUST detectar o workflow antes do push, aguardar via `gh run watch`, e só então editar notas. Anti-padrão documentado em "Lições aprendidas". |
| 8 | Edição posterior das notas via `gh release edit` quando o autor original é `github-actions[bot]` é silenciosamente sobrescrita por re-runs do workflow | Baixa | Workflow não re-roda em mesma tag (só em push); risco só aparece se a tag for force-pushed (já bloqueado por `lex-protected-trunk` + `lex-annotated-tags`) |

## Decisões em aberto (a tratar na execução)

- **Nome do warrior**: `warrior-janus` confirmado.
- **Subclade do warrior**: `_foundation/contributing/warriors/`? Ou criar nova subclade `_foundation/release/`? → Decidir antes de criar; recomendação: manter em `contributing/` para não fragmentar.
- **Tag protection rules no GitHub**: separadas deste plano; tratar em plano futuro de hardening do repo.
