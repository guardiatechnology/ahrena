# Lexis: Tags Anotadas e Assinadas

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrantável | **Escopo:** Tags Git em repositórios Guardia

## Lei

> **Toda tag empurrada para um remoto Guardia DEVE ser uma tag anotada (não lightweight) assinada com chave GPG. Empurrar tag lightweight para `origin` é PROIBIDO. A tag DEVE seguir Semantic Versioning conforme `lex-semantic-version` e a assinatura DEVE ser verificável localmente antes do push conforme `lex-signed-commits`.**

## Cobertura

- **Aplica-se a:** todas as tags Git empurradas para qualquer remoto Guardia (release, pre-release, internas). Tags locais não publicadas estão fora do alcance da regra, mas estarão sujeitas a ela ao serem empurradas.
- **Agentes vinculados:** todos os contribuidores (humanos e IA) — incluindo `warrior-janus`, `warrior-athena`, e qualquer Kata que crie tag (`kata-tag`, `kata-release-publish`).
- **Exceções:** Nenhuma. Lexis não admitem exceções. Tags lightweight pré-existentes no histórico do remoto permanecem (a regra é forward-looking) — não há migração retroativa.

## Regras

### 1. Tipo do objeto: anotada

Toda tag empurrada DEVE ser do tipo `tag` no Git (objeto próprio, com autor, data, mensagem e assinatura). Tags lightweight (apenas ponteiro para commit, sem objeto próprio) não satisfazem esta Lex.

### 2. Assinatura GPG obrigatória

Toda tag empurrada DEVE ser assinada com GPG. Lightweight tags são tecnicamente incapazes de carregar assinatura — somente tags anotadas suportam GPG. A assinatura DEVE ser verificada localmente antes do push.

### 3. Versionamento Semântico

O nome da tag DEVE seguir o formato definido em `lex-semantic-version` (MAJOR.MINOR.PATCH, com pré-release e metadados de build opcionais). Tags fora do formato SemVer são rejeitadas pela validação combinada das duas Lexis.

### 4. Validação server-side obrigatória

Todo repositório Guardia que adota Ahrena DEVE ter o workflow `.github/workflows/validate-tag.yml` ativo. Esse workflow:

- Bloqueia tags lightweight (verifica o tipo do objeto no remoto).
- Bloqueia tags fora do formato SemVer.
- Verifica a assinatura GPG em best-effort (sem falhar quando a chave pública não está disponível ao runner — a assinatura é regra local autoritativa).
- Apaga a tag remota inválida antes de encerrar com falha, evitando que workflows reativos consumam tag inválida.

### 5. Sem criação direta no remoto

A criação de tag via UI/API do GitHub (que produz lightweight tag automaticamente) é PROIBIDA. Tags DEVEM nascer localmente, ser assinadas localmente, e ser empurradas via `git push`.

## HARD-GATE

Conforme [`lex-hard-gate-pattern`](../../quality/lexis/lex-hard-gate-pattern.md), o bloqueio textual desta Lex é canonicamente expresso como:

```
<HARD-GATE>
warrior-janus, warrior-athena e qualquer outro agente (humano ou IA)
NÃO DEVE empurrar tag para remoto Guardia sem que ela satisfaça
TODOS os critérios:

  (a) Tag é do tipo `tag` no Git (anotada — não lightweight)
  (b) Tag está assinada com GPG e a assinatura foi verificada
      localmente antes do push
  (c) Nome segue Semantic Versioning (lex-semantic-version)
  (d) Repositório-alvo tem `.github/workflows/validate-tag.yml` ativo

Esta regra se aplica a TODA tag, independentemente de:
  - propósito declarado ("é só uma tag de debug")
  - urgência ("preciso publicar agora")
  - tipo de release (major, minor, patch, pre-release)
  - tamanho percebido da mudança

Exceção única declarada: Nenhuma. Tags lightweight pré-existentes
no histórico permanecem (regra forward-looking); não há migração
retroativa, mas nenhuma nova tag lightweight pode ser empurrada.

Nota: a verificação server-side de assinatura GPG é best-effort
(depende da chave pública estar disponível ao runner). O bloqueio
duro server-side fica em (a) "anotada" + (c) "SemVer-válida"; a
assinatura é exigida localmente antes do push.
</HARD-GATE>
```

## Consequências de Violação

1. **Bloqueio automático:** o workflow `validate-tag.yml` apaga a tag remota e falha a execução.
2. **Alerta:** o autor do push recebe notificação da Action falha; o release que dependeria da tag não acontece.
3. **Remediação:** recriar a tag localmente como anotada + assinada, validar localmente, e empurrar novamente.

## Validação Automatizada

- **Ferramenta:** workflow `.github/workflows/validate-tag.yml` (server-side, autoritativo) + verificação local antes do push pelo agente/contribuidor.
- **Momento:** no push da tag para `origin` (server-side); antes do push (client-side).
- **Métrica:** 0 tags lightweight em `origin` após esta Lex entrar em vigor; 100% das tags com assinatura GPG verificável localmente.

## Referências

- `lex-semantic-version` — formato MAJOR.MINOR.PATCH para nome da tag
- `lex-signed-commits` — assinatura GPG (mesma raiz aplicada a commits)
- [Git Tag — git-scm.com](https://git-scm.com/docs/git-tag)
