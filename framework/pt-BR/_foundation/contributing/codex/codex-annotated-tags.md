# Codex: Tags Anotadas e Assinadas

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Operação de tags Git em repositórios Guardia — criação, assinatura, verificação e validação server-side

## Visão Geral

Este Codex é o manual operacional para criar, assinar e verificar tags Git em repositórios Guardia. Documenta os comandos, opções, modos de falha e configuração GPG necessários para satisfazer `lex-annotated-tags`. É consultado pelos Katas `kata-tag` e `kata-release-publish` e pelo Warrior `warrior-janus`.

## Contexto

- **Domínio:** ciclo de vida de tags Git (criação local, assinatura, push, validação no remoto)
- **Público-alvo:** agentes de IA que criam tags (`kata-tag`, `kata-release-publish`), maintainers humanos preparando releases
- **Atualização:** quando o fluxo de criação/validação de tag muda, ou quando a Action `validate-tag.yml` evolui

## Conteúdo

### Princípios

1. **Anotada antes de assinada.** Uma tag lightweight (`git tag NOME`) não tem objeto próprio no Git — é apenas um ponteiro para um commit. Sem objeto, não há corpo para assinar. Por isso `git tag -s` implica `git tag -a`.
2. **Assinatura local, validação server-side best-effort.** A assinatura é gerada na máquina do contribuidor com a chave GPG dele. A validação no GitHub runner depende de a chave pública estar disponível ao runner — frequentemente não está. O bloqueio server-side autoritativo é o tipo do objeto (anotada vs lightweight) + nome SemVer; a assinatura é verificada localmente antes do push.
3. **Sem criação direta no remoto.** A UI/API do GitHub que cria tags produz lightweight tags. Por isso, criar tag pela UI/API é proibido pela `lex-annotated-tags`.

### Configuração GPG para Tags

Para assinar tags automaticamente sempre que `git tag -a` for usado:

```bash
git config --global tag.gpgSign true
git config --global user.signingkey <GPG-KEY-ID>
```

Verificar configuração:

```bash
git config --get tag.gpgSign      # esperado: true
git config --get user.signingkey  # esperado: ID da chave GPG (16 ou 40 caracteres hex)
```

Pré-requisitos: chave GPG gerada e publicada no GitHub (ver `kata-setup-gpg-signing`).

### Comandos de Criação

| Forma | Resultado | Conformidade com Lex |
|------|-----------|:--------------------:|
| `git tag -s v1.2.3 -m "Release 1.2.3"` | Tag anotada + assinada (canônico) | ✅ |
| `git tag -a v1.2.3 -m "Release 1.2.3"` | Tag anotada sem assinatura | ❌ (viola `lex-annotated-tags` rule 2) |
| `git tag v1.2.3` | Tag lightweight | ❌ (viola `lex-annotated-tags` rule 1) |
| `git tag -s v1.2.3 <sha>` | Tag anotada + assinada apontando para `<sha>` específico | ✅ |

Quando `tag.gpgSign true` está configurado, `git tag -a` já produz tag assinada — `-s` torna-se redundante mas inofensivo. O Kata sempre passa `-s` explicitamente por defesa em profundidade.

### Verificação Local

Antes de empurrar:

```bash
git tag -v v1.2.3
```

Saída esperada (assinatura válida):

```
object <sha>
type commit
tag v1.2.3
tagger <Author> <email> <timestamp>

Release 1.2.3
gpg: Signature made <date>
gpg: Good signature from "<Author> <email>"
```

Saída de tag lightweight (`git tag -v` falha):

```
error: <tag>: cannot verify a non-tag object of type commit.
```

Saída de tag anotada sem assinatura:

```
object <sha>
type commit
tag v1.2.3
...
error: no signature found
```

### Push

```bash
git push origin v1.2.3
```

A tag empurrada dispara `validate-tag.yml` no GitHub. Para apagar uma tag local que ainda não foi empurrada: `git tag -d v1.2.3`.

### Validação Server-side (`validate-tag.yml`)

O workflow valida cada tag empurrada para `origin`:

1. **Tipo do objeto** — `git cat-file -t $TAG`:
   - Anotada → retorna `tag` → prossegue
   - Lightweight → retorna `commit` → **falha + apaga a tag remota**
2. **Formato SemVer** — regex `^v?[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$`. Tag fora do padrão → **falha + apaga**.
3. **Assinatura GPG** — `git tag -v $TAG` em best-effort:
   - Boa assinatura → log `✓ GPG signature verified`
   - Chave pública ausente no runner → log `WARNING` (não falha — assinatura é validada localmente)
   - Sem assinatura → log `WARNING` (assinatura é regra local; ver Princípio 2)

### Apagar Tag Remota Inválida

Quando a Action detecta uma tag inválida (lightweight ou nome inválido), ela apaga a referência remota antes de falhar. Comando:

```bash
gh api -X DELETE repos/:owner/:repo/git/refs/tags/$TAG
```

O prefixo `repos/:owner/:repo/git/` é **obrigatório** — sem ele a chamada retorna HTTP 404. Em GitHub Actions, `${{ github.repository }}` substitui `:owner/:repo`.

### Modos de Falha e Remediação

| Sintoma | Causa | Remediação |
|---------|-------|------------|
| Action `validate-tag.yml` falha com `Lightweight tag rejected` | Tag foi criada com `git tag NOME` | Apagar local (`git tag -d`), recriar com `git tag -s NOME -m`, empurrar |
| `git tag -v` falha com `no signature found` | `tag.gpgSign` não está em `true`; chave GPG não configurada | Configurar `tag.gpgSign` + `user.signingkey` (ver acima); recriar tag |
| Push aceito mas Release não aparece | `validate-tag.yml` rejeitou; tag foi apagada do remoto | Verificar log da Action; recriar tag respeitando as 3 regras |
| `gh api -X DELETE refs/tags/$TAG` retorna 404 | Caminho incompleto (faltou `repos/:owner/:repo/git/`) | Usar o path completo |
| `git tag -v` no runner emite `WARNING` sobre chave ausente | Chave pública do signatário não está no runner; assinatura foi validada localmente | Aceitar — verificação no runner é best-effort por design |

### Exemplos Operacionais

**Fluxo canônico — release minor:**

```bash
# 1. Confirmar HEAD do trunk e CI verde
git fetch origin
git checkout main && git pull
gh run list --commit "$(git rev-parse HEAD)" --limit 5 --json status,conclusion

# 2. Criar tag anotada + assinada
git tag -s v1.3.0 -m "Release v1.3.0: warrior-janus orchestrator"

# 3. Validar localmente antes do push
git tag -v v1.3.0

# 4. Empurrar
git push origin v1.3.0

# 5. Aguardar validate-tag.yml + workflow de release
gh run watch "$(gh run list --workflow validate-tag.yml --commit $(git rev-parse v1.3.0) \
                 --limit 1 --json databaseId --jq '.[0].databaseId')"
```

**Apontando para commit específico (não HEAD):**

```bash
git tag -s v1.3.0 -m "Release v1.3.0" abc123f
```

**Recuperação após push de tag inválida:**

```bash
# Cenário: tag lightweight chegou ao remoto; Action apagou e falhou
git tag -d v1.3.0                            # apaga local (estava lightweight)
git tag -s v1.3.0 -m "Release v1.3.0"        # recria correta
git tag -v v1.3.0                            # confirma assinatura local
git push origin v1.3.0                       # nova tentativa
```

### Restrições Técnicas

- Tag **DEVE** ser criada localmente — UI/API do GitHub não suportam tag anotada + assinada nativamente.
- `tag.gpgSign true` no Git **DEVE** estar configurado no ambiente do agente/contribuidor antes do primeiro release.
- A Action `validate-tag.yml` **DEVE** estar presente em todo repositório Guardia que adota Ahrena — caso contrário, a regra é apenas client-side e pode ser burlada.

## Referências

- `lex-annotated-tags` — Lei que este Codex operacionaliza
- `lex-semantic-version` — Formato do nome da tag
- `lex-signed-commits` — Mesma raiz de assinatura GPG aplicada a commits
- `codex-semantic-version` — Manual de SemVer (companion deste Codex)
- `kata-tag` — Habilidade que aplica este manual para criar uma tag
- `kata-release-publish` — Habilidade que empurra a tag e aguarda a validação
- [Git Tag — git-scm.com](https://git-scm.com/docs/git-tag)
- [`git tag -v` reference](https://git-scm.com/docs/git-tag#Documentation/git-tag.txt--v)
