# Kata: Preparar Release (Bump + Changelog)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Fase 1 do ciclo de release orquestrado por `warrior-janus` — análise de commits, proposta de bump SemVer, geração de changelog e verificação de estado do trunk

## Objetivo

Este Kata define o procedimento padronizado para analisar Conventional Commits desde a última tag, propor o bump SemVer apropriado (major/minor/patch ou "sem release"), redigir um changelog draft agrupado por tipo, e verificar que o trunk está em estado adequado para liberar. O Kata **encerra apresentando a proposta ao humano**; a publicação acontece em `kata-release-publish` somente após aprovação explícita.

## Quando Usar

- Quando `warrior-janus` é invocado para iniciar um ciclo de release
- Quando o usuário invoca `cry-release` (com ou sem `--dry-run` / `--type`)
- Como passo independente para preview de versão e changelog sem publicar

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Bump override | Não | `major`, `minor`, ou `patch` para sobrescrever a heurística (via `cry-release --type`) |
| Modo dry-run | Não | Quando ativo, gera proposta mas não persiste nada (via `cry-release --dry-run`) |
| Base ref | Não | Tag ou ref de partida (default: última tag SemVer no remoto) |

## Workflow

```
Progresso:
- [ ] 1. Sincronizar tags e identificar última versão
- [ ] 2. Coletar commits desde a última tag
- [ ] 3. Classificar Conventional Commits e propor bump
- [ ] 4. Gerar changelog draft
- [ ] 5. Checar estado do trunk
- [ ] 6. Apresentar proposta ao humano
```

### Passo 1: Sincronizar Tags e Identificar Última Versão

1. Executar `git fetch --tags --prune-tags origin` para garantir visão atualizada.
2. Identificar a última tag SemVer:
   ```bash
   LAST_TAG=$(git describe --tags --abbrev=0 --match 'v[0-9]*.[0-9]*.[0-9]*' 2>/dev/null || true)
   ```
   - Se nenhuma tag existir, registrar **first-release** e tratar como `v0.0.0` para fins de análise; o bump inicial sugerido é `v0.1.0` (minor) quando há `feat:` ou `v1.0.0` se o time decide marcar GA (humano decide na Etapa 6).
3. Resolver o SHA correspondente à tag para uso em `git log <SHA>..HEAD`.

### Passo 2: Coletar Commits Desde a Última Tag

1. Executar:
   ```bash
   git log "${LAST_TAG:-$(git rev-list --max-parents=0 HEAD | tail -1)}"..HEAD \
     --no-merges \
     --pretty=format:'%H%x09%s%x09%b%x1e'
   ```
2. Separar cada commit em três campos: SHA, subject, body.
3. Descartar commits cujo subject não tenha prefixo válido de Conventional Commits — registrar separadamente em "commits sem tipo" (a serem listados ao humano como ruído potencial).

### Passo 3: Classificar Conventional Commits e Propor Bump

Aplicar a tabela:

| Sinal no commit | Bump |
|-----------------|------|
| Body contém linha começando com `BREAKING CHANGE:` | **major** |
| Subject usa `<type>!:` ou `<type>(<scope>)!:` | **major** |
| Subject começa com `feat:` ou `feat(...):` | **minor** |
| Subject começa com `fix:`, `perf:`, ou `revert:` | **patch** |
| Apenas commits `docs:`, `chore:`, `ci:`, `style:`, `test:`, `refactor:`, `build:` | **none** (sem release) |

Regra de combinação: aplicar o **maior** bump entre os encontrados (major > minor > patch).

Se houver override `--type`, **usar o override** mas registrar na proposta a heurística calculada para o humano comparar.

Calcular a próxima versão:
```
v1.2.3 + major → v2.0.0
v1.2.3 + minor → v1.3.0
v1.2.3 + patch → v1.2.4
v1.2.3 + none  → (sem release; encerrar com mensagem clara)
```

### Passo 4: Gerar Changelog Draft

Agrupar commits classificados por tipo, na ordem: `feat` → `fix` → `perf` → `refactor` → `docs` → `build` → `ci` → `chore` → `test` → `style` → `revert`. Para cada commit, formato:

```
- <scope-se-houver>: <subject sem o prefixo> (<short-sha>) by @<autor>
```

Estrutura do changelog:

```markdown
# Release vX.Y.Z

> **Data:** YYYY-MM-DD
> **Bump:** major | minor | patch (vAAA.BBB.CCC → vXXX.YYY.ZZZ)
> **Issues fechadas:** #N1, #N2, ...

## ⚠ Breaking Changes
- ...

## ✨ Features
- ...

## 🐛 Fixes
- ...

## ⚡ Performance
- ...

## 🔧 Outros (refactor, docs, build, ci, chore, test, style)
- ...
```

Listar issues fechadas extraindo `Closes #N` ou `Fixes #N` dos commit bodies.

Persistir o draft em `.ahrena/workflow/release/changelog-vX.Y.Z.draft.md` (criar diretório se necessário) — exceto em `--dry-run`, onde o draft é apresentado apenas em memória.

### Passo 5: Checar Estado do Trunk

1. Identificar branch trunk (default: `main`).
2. Verificar status de CI no commit-alvo:
   ```bash
   gh run list --branch main --limit 5 --json status,conclusion,workflowName
   ```
   - Falha (`conclusion: failure` em workflow obrigatório) → **bloquear proposta**; reportar ao humano.
   - Em execução (`status: in_progress`) → **aguardar até 5 minutos**; se ainda em execução, sinalizar e deixar humano decidir.
   - Sucesso → prosseguir.
3. Listar PRs abertos no repositório (informativo, não bloqueante):
   ```bash
   gh pr list --state open --limit 20 --json number,title,labels
   ```
   - Apresentar ao humano com aviso: "Estes PRs ficarão fora do release; confirme se isso é intencional."

### Passo 6: Apresentar Proposta ao Humano

Saída estruturada apresentando:

1. **Versão atual e próxima:** `LAST_TAG` → `NEXT_TAG`
2. **Bump:** `minor` (heurística) ou `minor (override via --type)`
3. **Resumo de commits:** contagem por tipo (`feat: 3, fix: 5, ...`)
4. **Caminho do changelog draft:** `.ahrena/workflow/release/changelog-vX.Y.Z.draft.md` (ou inline se dry-run)
5. **Estado do trunk:** ✅ CI verde / ⚠ PRs abertos / ❌ CI quebrado
6. **Pergunta explícita:** "Aprovar e publicar este release? (sim / editar / cancelar)"

O Kata **encerra aqui**. A aprovação é responsabilidade do humano; a publicação é responsabilidade de `kata-release-publish`. Sem entrada explícita "sim", `warrior-janus` não invoca a fase seguinte.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Próxima versão proposta | String SemVer (ex.: `v1.3.0`) | Apresentada ao humano + payload para `kata-release-publish` |
| Changelog draft | Markdown | `.ahrena/workflow/release/changelog-vX.Y.Z.draft.md` (ou stdout em dry-run) |
| Diagnóstico do trunk | Estruturado (status, contagem) | Apresentado ao humano |
| Lista de commits sem tipo | Lista de SHAs + subjects | Apresentado ao humano (ruído potencial) |

## Restrições

- **Nunca publicar** — este Kata para na proposta. A publicação é privilégio exclusivo de `kata-release-publish` mediante aprovação humana.
- **Nunca inferir bump silenciosamente** — sempre mostrar a heurística aplicada e os commits que dispararam cada nível.
- **Nunca confundir override e heurística** — se humano usou `--type major` mas commits sugerem `patch`, ambos DEVEM aparecer na proposta para reduzir risco de erro humano.
- **Nunca pular a checagem de CI** — trunk com CI vermelho não merece release, salvo decisão humana documentada.
- **Sem release** (bump `none`) NÃO é falha do Kata; é resultado válido. Encerrar com mensagem clara.

## Referências

- `lex-conventional-commits` — formato dos commits analisados
- `lex-semantic-version` — formato da próxima versão proposta
- `lex-annotated-tags` — pré-requisito para publicação (consumido pelo Kata seguinte)
- `kata-release-publish` — Kata seguinte; recebe a versão e o changelog aprovados
- `warrior-janus` — Warrior que orquestra este Kata + gate humano + `kata-release-publish`
- `cry-release` — cry que invoca `warrior-janus`
