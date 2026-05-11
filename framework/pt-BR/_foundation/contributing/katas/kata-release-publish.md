# Kata: Publicar Release (Tag Anotada + GitHub Release)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Fase 2 do ciclo de release orquestrado por `warrior-janus` — criação de tag anotada/assinada, push para o remoto, espera/edição do release via GitHub Action e verificação de pós-condições

## Objetivo

Este Kata define o procedimento que **publica de fato** o release após aprovação humana obtida em `kata-release-prepare`. O Kata cria a tag anotada e assinada (via `kata-tag`), empurra para o remoto, **detecta se há um workflow `release.yml` que cria GitHub Release automaticamente** e age conforme: aguarda a Release auto-gerada ou, em repositórios sem workflow, cria a Release via `gh release create`. Verifica que `validate-tag.yml` aprovou a tag.

## Quando Usar

- Quando `warrior-janus` recebeu aprovação humana explícita após `kata-release-prepare`
- Nunca diretamente sem o passo de preparação — o Kata pressupõe que a versão e o changelog foram acordados

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Próxima versão | Sim | String SemVer aprovada (ex.: `v1.3.0`) — vinda de `kata-release-prepare` |
| Caminho do changelog | Sim | `.ahrena/workflow/release/changelog-vX.Y.Z.draft.md` aprovado pelo humano |
| Commit-alvo | Não | SHA específico para a tag (default: HEAD do trunk no momento da aprovação) |

## Pré-condições (bloqueantes)

- [ ] `kata-release-prepare` foi executado e o humano respondeu **"sim"** explicitamente
- [ ] Versão respeita `lex-semantic-version`
- [ ] GPG configurado (`lex-signed-commits` / `lex-annotated-tags`)
- [ ] `.github/workflows/validate-tag.yml` existe no repositório-alvo
- [ ] Branch trunk com CI verde no commit-alvo (revalidar — janela pode ter sido aberta entre prepare e publish)

Se qualquer pré-condição falhar: **abortar**, registrar motivo, retornar controle ao humano.

## Workflow

```
Progresso:
- [ ] 1. Revalidar pré-condições
- [ ] 2. Detectar workflow de release no repositório-alvo
- [ ] 3. Criar tag anotada e assinada (via kata-tag)
- [ ] 4. Empurrar tag para o remoto
- [ ] 5. Aguardar validate-tag.yml concluir com sucesso
- [ ] 6. Tratar o ciclo da GitHub Release (workflow ou fallback)
- [ ] 7. Verificar pós-condições e relatar
```

### Passo 1: Revalidar Pré-condições

Reexecutar as checagens listadas em "Pré-condições" (não confiar no estado de minutos atrás). Se qualquer item falhar, abortar e devolver controle ao humano.

### Passo 2: Detectar Workflow de Release

Este passo é **crítico** — a ausência dele causou bug em v0.11.0 (race condition entre `gh release create` e workflow automático).

A detecção tem dois critérios; **ambos** precisam casar para classificar um arquivo como release-creating:

1. **Trigger em push de tag** — qualquer das grafias YAML válidas: `tags: ['v*']`, `tags: 'v*'`, ou bloco `tags:\n  - "v*"` (lista YAML).
2. **Step que cria GitHub Release** — `softprops/action-gh-release`, `actions/create-release`, ou chamada explícita a `gh release create` / API `POST /releases`.

Sem (2), um workflow apenas-CI disparado por tag seria erroneamente classificado como release-creating; sem (1), um workflow `workflow_dispatch` que cria release manualmente seria erroneamente esperado.

```bash
RELEASE_WORKFLOW=""
for wf in .github/workflows/*.yml .github/workflows/*.yaml; do
  [ -f "$wf" ] || continue

  # (1) trigger em push de tag — cobre grafias com colchetes, string e lista YAML
  has_tag_trigger=0
  if grep -qE '^\s*tags:\s*\[' "$wf" \
     || grep -qE "^\s*tags:\s*['\"]?v" "$wf" \
     || awk '/^\s*tags:\s*$/,/^\s*[^[:space:]-]/' "$wf" | grep -qE '^\s*-\s*["'\'']?v'; then
    has_tag_trigger=1
  fi
  [ $has_tag_trigger -eq 1 ] || continue

  # (2) step que cria GitHub Release
  if grep -qE 'softprops/action-gh-release|actions/create-release|gh release create|POST /repos/.+/releases' "$wf"; then
    RELEASE_WORKFLOW="$wf"
    break
  fi
done
```

Registrar no log:
- `RELEASE_WORKFLOW="<path>"` → caminho "workflow-driven"
- `RELEASE_WORKFLOW=""` → caminho "fallback" (`gh release create`)

**Limites conhecidos da heurística:**
- Workflows que delegam a criação da Release para outro workflow via `workflow_call` exigem inspeção transitiva — fora do escopo desta heurística. Documentar no Janus como caso a tratar manualmente.
- Action customizada (não as três listadas) que cria Release passa despercebida; nesse caso, o humano que mantém o repo SHOULD nomear o workflow com `release` no nome do arquivo e adicionar comentário `# creates-github-release: true` (convenção sugerida para futura iteração da heurística).

### Passo 3: Criar Tag Anotada e Assinada

Invocar `kata-tag` passando:
- Versão aprovada (ex.: `v1.3.0`)
- Mensagem da tag: primeira linha do changelog (`# Release v1.3.0`) ou padrão `"Release v1.3.0"`
- Commit-alvo (default HEAD; respeitar se humano informou outro)

`kata-tag` retorna a tag criada localmente. Validar com `git tag -v <versão>` antes de prosseguir.

### Passo 4: Empurrar Tag para o Remoto

```bash
git push origin "$NEXT_TAG"
```

Capturar exit code. Se push falhar (ex.: tag já existe no remoto), abortar com mensagem clara — não tentar reusar tag.

A partir deste ponto, a tag está visível no GitHub e workflows reativos podem disparar.

### Passo 5: Aguardar validate-tag.yml

A Action `validate-tag.yml` (introduzida por `lex-annotated-tags`) verifica que a tag é anotada + assinada + SemVer-válida. **Aguardar sua conclusão**.

> **Atenção (race):** após `git push`, o GitHub leva alguns segundos para registrar o workflow run. Consultar `gh run list` imediatamente pode retornar `[]`. O Kata DEVE polar até encontrar o `databaseId`, com timeout.

```bash
TAG_SHA=$(git rev-parse "$NEXT_TAG")
RUN_ID=""
DEADLINE=$(($(date +%s) + 60))
while [ -z "$RUN_ID" ]; do
  RUN_ID=$(gh run list \
    --workflow validate-tag.yml \
    --commit "$TAG_SHA" \
    --limit 1 \
    --json databaseId \
    --jq '.[0].databaseId // empty')
  if [ -n "$RUN_ID" ]; then break; fi
  if [ $(date +%s) -ge $DEADLINE ]; then
    echo "Timeout aguardando validate-tag.yml registrar run para $NEXT_TAG"
    exit 1
  fi
  sleep 3
done

gh run watch "$RUN_ID" --exit-status
```

Se `validate-tag.yml` falhar: a tag remota é apagada pela própria Action; relatar ao humano e encerrar com falha. A remediação é refazer a tag local (provavelmente um problema de assinatura) e tentar publicar de novo.

### Passo 6: Tratar o Ciclo da GitHub Release

**Caminho A — workflow-driven (`RELEASE_WORKFLOW != ""`):**

1. Aguardar conclusão do workflow de release (mesmo polling do Passo 5 para evitar race condition):
   ```bash
   REL_RUN_ID=""
   DEADLINE=$(($(date +%s) + 60))
   while [ -z "$REL_RUN_ID" ]; do
     REL_RUN_ID=$(gh run list \
       --workflow "$(basename "$RELEASE_WORKFLOW")" \
       --commit "$TAG_SHA" \
       --limit 1 \
       --json databaseId \
       --jq '.[0].databaseId // empty')
     if [ -n "$REL_RUN_ID" ]; then break; fi
     if [ $(date +%s) -ge $DEADLINE ]; then
       echo "Timeout aguardando $(basename "$RELEASE_WORKFLOW") registrar run para $NEXT_TAG"
       exit 1
     fi
     sleep 3
   done

   gh run watch "$REL_RUN_ID" --exit-status
   ```
2. Verificar que a Release existe: `gh release view "$NEXT_TAG"`.
3. Comparar notas auto-geradas com o changelog do `kata-release-prepare`:
   - Se o draft é **substancialmente mais informativo** (agrupamento por tipo, issues fechadas, breaking changes destacadas): sobrescrever com `gh release edit`.
   - Caso contrário: **preservar a Release auto-gerada** (caminho padrão).
4. Registrar no log do Kata qual caminho foi seguido — auditável.

```bash
# Sobrescrita opcional, apenas quando o draft é mais informativo
gh release edit "$NEXT_TAG" --notes-file "$CHANGELOG_PATH"
```

**Caminho B — fallback (`RELEASE_WORKFLOW == ""`):**

```bash
gh release create "$NEXT_TAG" \
  --title "Release $NEXT_TAG" \
  --notes-file "$CHANGELOG_PATH"
```

### Passo 7: Verificar Pós-condições e Relatar

- [ ] Tag local existe e `git tag -v <versão>` verifica assinatura
- [ ] Tag remota existe (`gh api repos/$OWNER/$REPO/git/refs/tags/<versão>`)
- [ ] `validate-tag.yml` concluiu com sucesso
- [ ] GitHub Release existe e é acessível
- [ ] Path do changelog (draft) movido para `.ahrena/workflow/release/changelog-<versão>.published.md` (rename simples)
- [ ] Relato final ao humano: URL da Release, caminho seguido (workflow-driven / fallback), tamanho do changelog (auto vs custom)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Tag publicada | Git tag anotada + assinada | Remoto (`origin`) |
| GitHub Release | URL HTTPS | Apresentada ao humano e registrada no log |
| Changelog publicado | Markdown | `.ahrena/workflow/release/changelog-<versão>.published.md` |
| Caminho seguido | `workflow-driven` ou `fallback` | Log do Kata (auditoria) |

## Restrições

- **NUNCA invocar `gh release create`** quando o repositório-alvo tem workflow do tipo `on: push: tags: ['v*']` que já cria a Release — racing condition causa HTTP 422 (confirmado em v0.11.0, PR #68).
- **NUNCA pular a espera de `validate-tag.yml`** — sem ela, releases inválidas podem ser visíveis a consumidores por segundos antes da Action apagar a tag.
- **NUNCA sobrescrever silenciosamente** notas auto-geradas — exigir critério "draft substancialmente mais informativo" e registrar a decisão.
- **NUNCA refazer push** após falha de `validate-tag.yml` no mesmo SHA sem corrigir a causa raiz (provavelmente assinatura inválida).
- **NUNCA invocar este Kata** sem aprovação humana explícita registrada por `kata-release-prepare` — Janus é orquestrador, não executor autônomo.

## Anti-padrão (lição aprendida — v0.11.0)

```bash
# ❌ INCORRETO — causa HTTP 422 quando workflow cria Release antes
git push origin v1.2.3
gh release create v1.2.3 --notes-file ./changelog.md
# → tag empurrada dispara release.yml, que cria a Release
# → 5 segundos depois, gh release create tenta criar de novo e falha com:
#    "tag_name was used by an immutable release"
```

```bash
# ✅ CORRETO — detecta workflow, aguarda, edita só se necessário
git push origin v1.2.3
gh run watch "$(gh run list --workflow release.yml --commit "$(git rev-parse v1.2.3)" \
                 --limit 1 --json databaseId --jq '.[0].databaseId')"
# Workflow concluiu; Release foi criada automaticamente.
# Só edita as notas se o changelog preparado for substancialmente mais informativo.
gh release edit v1.2.3 --notes-file ./changelog.md
```

## Referências

- `lex-annotated-tags` — toda tag DEVE ser anotada + assinada
- `lex-semantic-version` — formato da versão
- `lex-signed-commits` — configuração GPG
- `codex-annotated-tags` — manual operacional consultado por este Kata (config GPG, comandos, verificação)
- `kata-tag` — cria a tag localmente
- `kata-release-prepare` — Kata anterior; fornece versão aprovada + changelog
- `warrior-janus` — Warrior que orquestra prepare + gate humano + publish
- `cry-release` — cry que invoca `warrior-janus`
- Histórico: v0.11.0 (PR #68) — race condition que motivou a detecção de workflow
