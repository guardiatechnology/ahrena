# Kata: Aplicar Versionamento Semântico com Git Tag

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação de tags de release conformes com `lex-semantic-version`, `lex-signed-commits` e `lex-annotated-tags`

## Objetivo

Este Kata define o procedimento padronizado para aplicar versionamento semântico no projeto usando git tags: determinar a próxima versão (ou usar a informada), validar contra as Lexis e criar **tag anotada e assinada** (`git tag -a -s`). Tags lightweight (`git tag NOME` sem `-a`/`-s`) são PROIBIDAS por `lex-annotated-tags` — somente tags anotadas suportam assinatura GPG.

## Quando Usar

- Quando é necessário criar uma tag de release seguindo Semantic Versioning 2.0
- Quando o usuário solicita ajuda para marcar uma versão no repositório
- Quando invocado pelo `cry-tag` para criar tag (não para listar)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Versão | Não | Identificador SemVer (ex.: `1.2.3` ou `v1.2.3`). Se omitido, o agente sugere com base no histórico de tags e commits |
| Mensagem | Não | Mensagem de anotação da tag. Se omitida, usar mensagem padrão (ex.: "Release X.Y.Z") |
| Commit | Não | ID (hash) ou mensagem (subject) do commit ao qual a tag será apontada. Se omitido, usar HEAD |

## Workflow

```
Progresso:
- [ ] 1. Verificar estado do repositório
- [ ] 2. Determinar próxima versão
- [ ] 3. Validar formato contra lex-semantic-version
- [ ] 4. Criar tag anotada e assinada
- [ ] 5. Verificação final
```

### Passo 1: Verificar Estado do Repositório e Resolver o Commit-Alvo

1. Executar `git status` para confirmar que não há alterações não commitadas que devam entrar no release (ou que o usuário está ciente)
2. Executar `git tag -l` (ou `git tag -l --sort=-v:refname`) para listar tags existentes e obter a última versão
3. **Resolver o commit onde a tag será criada:**
   - Se o usuário informou **commit** (ID ou mensagem): resolver para um hash válido.
     - Se for um hash (ou abreviação): `git rev-parse <ref>` para obter o commit.
     - Se for mensagem (subject): buscar commit cujo subject corresponda, ex.: `git log -1 --all --format=%H --grep="<mensagem>"` ou busca por subject; em caso de múltiplos matches, usar o mais recente ou pedir confirmação ao usuário.
   - Se **commit** foi omitido: usar HEAD (`git rev-parse HEAD`).
4. Opcional: executar `git log <último-tag>..<commit-alvo> --oneline` para ver commits desde o último tag (útil para sugerir versão)

### Passo 2: Determinar Próxima Versão

1. Consultar `codex-semantic-version` para regras de incremento
2. Se o usuário informou a versão, usá-la (normalizar para o formato adotado pelo projeto, ex.: com ou sem `v`)
3. Se a versão foi omitida:
   - Obter o último tag no formato SemVer
   - Analisar os commits desde esse tag (ex.: `git log <último-tag>..HEAD --pretty=format:'%s'`)
   - Aplicar a tabela do codex: BREAKING CHANGE / feat! / fix! → MAJOR; feat → MINOR; fix/perf/etc. → PATCH
   - Se não houver último tag, sugerir `v1.0.0` (ou `1.0.0`) como primeira versão
4. Garantir que o identificador está no formato MAJOR.MINOR.PATCH (com ou sem prefixo `v`)

### Passo 3: Validação contra lex-semantic-version

Antes de criar a tag, verificar:

- [ ] O identificador segue Semantic Versioning 2.0 (MAJOR.MINOR.PATCH)
- [ ] Não é um formato inválido (ex.: `release-1.2`, `1.2`, `latest`)
- [ ] Pré-release ou metadados (se usados) seguem a especificação SemVer 2.0
- [ ] A tag ainda não existe no repositório (`git tag -l '<versão>'` vazio)

Se alguma validação falhar, corrigir ou orientar o usuário antes de prosseguir.

### Passo 4: Criar Tag Anotada e Assinada

1. Verificar que GPG está configurado para assinatura de tags (`lex-signed-commits`): `git config --get user.signingkey`
2. Se não estiver configurado, alertar o usuário e orientar a configuração; não criar tag sem assinatura
3. Definir a mensagem da tag: usar a mensagem fornecida pelo usuário ou padrão (ex.: "Release 1.2.3")
4. Usar o **commit-alvo** resolvido no Passo 1 (HEAD ou o commit informado pelo usuário).
5. Executar:
   ```
   git tag -s <versão> <commit-alvo> -m "<mensagem>"
   ```
   Exemplo (tag no HEAD): `git tag -s v1.2.3 -m "Release 1.2.3"` (equivale a `git tag -s v1.2.3 HEAD -m "Release 1.2.3"`).
   Exemplo (tag em commit específico): `git tag -s v1.2.3 abc123f -m "Release 1.2.3"`

### Passo 5: Verificação Final

- [ ] A tag existe: `git tag -l '<versão>'` retorna a versão
- [ ] A tag é assinada: `git tag -v <versão>` (ou `git show <versão>`) mostra verificação GPG
- [ ] O formato está correto conforme `lex-semantic-version`
- [ ] Informar ao usuário que para publicar a tag é necessário: `git push origin <versão>`

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Tag criada | Git tag (anotada e assinada) | Repositório local |
| Instrução de push | Texto | Ex.: "Para publicar: git push origin v1.2.3" |

## Restrições

- Nunca criar tag de release sem conformidade com `lex-semantic-version` (formato SemVer 2.0)
- Nunca criar tag de release sem assinatura GPG; seguir `lex-signed-commits`
- **Nunca usar `git tag NOME` (lightweight)** — `lex-annotated-tags` proíbe push de tag lightweight; somente `git tag -a -s` produz tag válida
- Se o usuário pedir apenas listar tags (ex.: via `cry-tag --list`), não executar este Kata de criação; apenas listar com `git tag -l` (e opcionalmente `-n` ou ordenação)
- Referenciar sempre `codex-semantic-version` e `lex-semantic-version` ao sugerir ou validar versão

## Exemplos

### Correto

```bash
# Tag anotada e assinada
git tag -s v1.2.3 -m "Release 1.2.3"
git tag -v v1.2.3   # verifica assinatura
git push origin v1.2.3
```

### Incorreto

```bash
# ❌ Tag lightweight — viola lex-annotated-tags
git tag v1.2.3
# (sem -a/-s; sem mensagem; sem assinatura)

# ❌ Tag anotada sem assinatura — viola lex-signed-commits + lex-annotated-tags
git tag -a v1.2.3 -m "Release"
# (anotada mas não assinada)
```

## Referências

- `lex-semantic-version` — Formato SemVer obrigatório para releases
- `lex-signed-commits` — Assinatura GPG obrigatória para tags de release
- `lex-annotated-tags` — Tags empurradas para remoto DEVEM ser anotadas + assinadas
- `codex-semantic-version` — Manual de referência para SemVer e git tags
- `codex-annotated-tags` — Manual operacional para tags anotadas (config GPG, comandos, verificação, modos de falha)
- `cry-tag` — Atalho que invoca este Kata para criar tag (e listar tags)
- `kata-release-publish` — Kata que invoca este via `warrior-janus`
