# Lexis: Versionamento Semântico Obrigatório

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Versões e tags de release em repositórios Guardia

## Propósito

Identificadores de versão previsíveis permitem que consumidores, ferramentas e pipelines saibam o tipo de mudança entre releases. Semantic Versioning 2.0 (SemVer) estabelece um contrato claro: MAJOR para mudanças incompatíveis, MINOR para funcionalidades compatíveis, PATCH para correções compatíveis.

Esta Lexis garante que todo release em repositórios Guardia use o mesmo padrão, permitindo automação de changelogs, dependências e CI/CD.

## Lei

> **Todo identificador de versão de release e toda tag de release DEVE seguir Semantic Versioning 2.0 (MAJOR.MINOR.PATCH). Nenhuma exceção.**

## Regras

### 1. Formato obrigatório

O identificador de versão DEVE ser no formato `X.Y.Z`, onde:

- **MAJOR (X):** inteiro não negativo; incrementado quando há mudanças incompatíveis na API
- **MINOR (Y):** inteiro não negativo; incrementado quando nova funcionalidade é adicionada de forma compatível
- **PATCH (Z):** inteiro não negativo; incrementado quando correções compatíveis são feitas

### 2. Tags no Git

Tags usadas para marcar releases DEVEM usar o formato SemVer. O prefixo `v` é recomendado para compatibilidade com ferramentas (ex.: `v1.2.3`). As variantes `v1.2.3` e `1.2.3` são aceitas; o projeto DEVE adotar uma convenção e mantê-la consistente.

### 3. Tags de release assinadas e anotadas

Tags de release também DEVEM ser assinadas com GPG, conforme `lex-signed-commits`, e anotadas (`git tag -a -s`), conforme `lex-annotated-tags`. Tags lightweight são tecnicamente incapazes de carregar assinatura — somente tags anotadas suportam GPG.

### 4. Pré-release e metadados

Identificadores de pré-release (ex.: `v1.2.3-alpha.1`) e metadados de build (ex.: `v1.2.3+build.42`) seguem a especificação SemVer 2.0 e são permitidos quando documentados no `codex-semantic-version`.

## Abrangência

- **Aplica-se a:** todos os repositórios Guardia que publicam releases versionados
- **Agentes vinculados:** todos
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Inconsistência:** consumidores e ferramentas não conseguem inferir o tipo de mudança
2. **Automação quebrada:** pipelines que dependem de ordem semântica ou parsing de versão falham
3. **Remediação:** criar nova tag no formato correto; documentar a convenção no repositório

## Exemplos

### Correto

```
v1.0.0
v2.1.3
1.0.0
v1.2.3-alpha.1
v1.2.3+build.42
```

### Incorreto

```
release-1.2      # não é MAJOR.MINOR.PATCH
1.2              # falta PATCH
v1.2.3.4         # mais de três segmentos numéricos (a menos que seja pré-release/metadados SemVer)
latest           # identificador não numérico para release
```

## Validação Automatizada

- **Ferramenta:** validação por regex ou parser SemVer (ex.: em CI ou pre-push hook)
- **Momento:** antes de push de tag ou no pipeline de release
- **Métrica:** 0 tags de release em formato inválido toleradas

## Referências

- [Semantic Versioning 2.0.0](https://semver.org/)
- `lex-signed-commits` — Assinatura GPG obrigatória para tags de release
- `lex-annotated-tags` — Tags empurradas para remoto DEVEM ser anotadas + assinadas
- `codex-semantic-version` — Manual de referência para aplicação de SemVer no projeto
