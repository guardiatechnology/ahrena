# Lexis: Tags Anotadas e Assinadas

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrantável | **Escopo:** Tags Git em repositórios Guardia

## Lei

> **Toda tag empurrada para um remoto Guardia DEVE ser uma tag anotada (`git tag -a`) assinada com chave GPG (`git tag -s`). Empurrar tag lightweight (criada sem `-a`/`-s`/`-m`) para `origin` é PROIBIDO. A tag DEVE seguir Semantic Versioning conforme `lex-semantic-version` e a assinatura DEVE ser verificável conforme `lex-signed-commits`.**

## Cobertura

- **Aplica-se a:** todas as tags Git empurradas para qualquer remoto Guardia (release, pre-release, internas). Tags locais não publicadas estão fora do alcance da regra, mas estarão sujeitas a ela ao serem empurradas.
- **Agentes vinculados:** todos os contribuidores (humanos e IA) — incluindo `warrior-janus`, `warrior-athena`, e qualquer Kata que crie tag (`kata-tag`, `kata-release-publish`).
- **Exceções:** Nenhuma. Lexis não admitem exceções. Tags lightweight pré-existentes no histórico do remoto permanecem (a regra é forward-looking) — não há migração retroativa.

## Regras

### 1. Tag anotada com mensagem

Toda tag DEVE ser criada com `git tag -a` (ou `-s`, que implica `-a`) e mensagem explícita via `-m` ou editor. Tags lightweight (`git tag NOME`) carecem de autor, data, mensagem e assinatura — não satisfazem esta Lex.

```bash
# Correto
git tag -a v1.2.3 -m "Release v1.2.3"

# Correto (assinado, implica anotada)
git tag -s v1.2.3 -m "Release v1.2.3"

# INCORRETO — lightweight
git tag v1.2.3
```

### 2. Assinatura GPG obrigatória

Toda tag empurrada DEVE ser assinada com GPG (`git tag -s`). Tag lightweight é tecnicamente incapaz de carregar assinatura — somente tags anotadas suportam GPG. A assinatura DEVE ser verificável via `git tag -v <tag>`.

Configuração recomendada para assinatura automática:

```bash
git config --global tag.gpgSign true
git config --global user.signingkey <GPG-KEY-ID>
```

### 3. Versionamento Semântico

O nome da tag DEVE seguir o formato definido em `lex-semantic-version` (`vMAJOR.MINOR.PATCH`, com pré-release e metadados de build opcionais). Tags fora do formato SemVer são rejeitadas pela validação combinada das duas Lexis.

### 4. Validação server-side

O workflow `.github/workflows/validate-tag.yml` DEVE estar configurado em todo repositório Guardia que adota Ahrena. Esse workflow:

- Dispara em `on: push: tags: ['*']`.
- Executa `git cat-file -t $TAG`; falha quando o tipo retornado não é `tag` (lightweight retorna `commit`).
- Executa `git tag -v $TAG`; falha quando a assinatura não verifica.
- Apaga a tag remota (`gh api -X DELETE repos/:owner/:repo/git/refs/tags/$TAG`) antes de encerrar com falha, evitando que outros workflows reativos consumam tag inválida.

### 5. Sem criação direta no remoto

A criação de tag via UI/API do GitHub (que produz lightweight tag automaticamente) é PROIBIDA. Tags DEVEM nascer localmente, com `git tag -a -s`, e ser empurradas via `git push origin <tag>`.

## HARD-GATE

Conforme [`lex-hard-gate-pattern`](../../quality/lexis/lex-hard-gate-pattern.md), o bloqueio textual desta Lex é canonicamente expresso como:

```
<HARD-GATE>
warrior-janus, warrior-athena e qualquer outro agente (humano ou IA)
NÃO DEVE empurrar tag para remoto Guardia sem que ela satisfaça
TODOS os critérios:

  (a) Foi criada com `git tag -a` (anotada)
  (b) Foi assinada com `git tag -s` (GPG) — `git tag -v` local confirma a assinatura antes do push
  (c) Nome segue Semantic Versioning (lex-semantic-version)
  (d) Repositório-alvo tem `.github/workflows/validate-tag.yml` ativo

Nota: a verificação server-side via `git tag -v` no runner é best-effort
(depende de a chave pública estar disponível ao runner). O bloqueio
duro server-side fica em (a) "anotada" + (c) "SemVer-válida"; a
assinatura é exigida localmente antes do push.

Esta regra se aplica a TODA tag, independentemente de:
  - propósito declarado ("é só uma tag de debug")
  - urgência ("preciso publicar agora")
  - tipo de release (major, minor, patch, pre-release)
  - tamanho percebido da mudança

Exceção única declarada: Nenhuma. Tags lightweight pré-existentes
no histórico permanecem (regra forward-looking); não há migração
retroativa, mas nenhuma nova tag lightweight pode ser empurrada.
</HARD-GATE>
```

## Consequências de Violação

1. **Bloqueio automático:** o workflow `validate-tag.yml` apaga a tag remota e falha a execução.
2. **Alerta:** o autor do push recebe notificação da Action falha; o release que dependeria da tag não acontece.
3. **Remediação:** recriar a tag localmente com `git tag -a -s -m`, validar com `git tag -v`, e empurrar novamente.

## Exemplos

### Correto

```bash
# Maintainer cria tag anotada e assinada
git tag -a v1.2.3 -s -m "Release v1.2.3: warrior-janus orchestrator"
git tag -v v1.2.3   # confirma assinatura
git push origin v1.2.3

# validate-tag.yml dispara, valida, conclui com sucesso
# release.yml dispara em seguida, cria GitHub Release
```

### Incorreto

```bash
# Lightweight tag — VIOLA A LEI
git tag v1.2.3
git push origin v1.2.3
# → validate-tag.yml: `git cat-file -t v1.2.3` retorna `commit` (não `tag`)
# → tag apagada do remoto, workflow falha

# Tag anotada mas não assinada — VIOLA A LEI
git tag -a v1.2.3 -m "Release"
git push origin v1.2.3
# → validate-tag.yml: `git tag -v v1.2.3` falha (sem assinatura)
# → tag apagada do remoto, workflow falha

# Tag criada via UI do GitHub — VIOLA A LEI
# (a UI sempre gera lightweight tag, sem assinatura local)
```

## Validação Automatizada

- **Ferramenta:** workflow `.github/workflows/validate-tag.yml` (server-side, autoritativo) + `kata-release-publish` (client-side, preventivo).
- **Momento:** ao empurrar tag para `origin` (server-side); ao orquestrar release (client-side).
- **Métrica:** 0 tags lightweight em `origin` após esta Lex entrar em vigor; 100% das tags com assinatura GPG verificável.

## Referências

- `lex-semantic-version` — formato MAJOR.MINOR.PATCH para nome da tag
- `lex-signed-commits` — assinatura GPG (mesma raiz; tags reforçam o mesmo princípio)
- `kata-tag` — procedimento de criação de tag (usa `git tag -a -s`)
- `kata-release-publish` — Kata orquestrador de Janus que invoca `kata-tag`
- `warrior-janus` — Warrior orquestrador do ciclo de release
- [Git Tag — git-scm.com](https://git-scm.com/docs/git-tag)
