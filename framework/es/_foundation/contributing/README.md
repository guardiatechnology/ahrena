# Contributing — Flujo de Contribución

> Documentación del sistema de contribución, estándares de commit y creación de Pull Requests.

## Visión General

El Subclade `contributing` define el flujo unificado de contribución de Guardia. Abarca desde las Lexis de commit hasta el procedimiento de apertura de PRs vía MCP. El proceso es el mismo para todos los contribuidores (internos y externos), garantizando transparencia y trazabilidad.

## Arquitectura

```mermaid
flowchart TD
    subgraph invocation ["Invocación"]
        CryCommit["/cry-commit"]
        CryContribute["/cry-contribute"]
    end

    subgraph procedures ["Procedimientos"]
        KataCommit["kata-commit"]
        KataContribute["kata-contribute"]
    end

    subgraph knowledge ["Conocimiento"]
        CdxContributing["codex-contributing"]
        CdxCommitStd["codex-commit-standards"]
    end

    subgraph laws ["Lexis de Commit"]
        LexConventional["lex-conventional-commits"]
        LexSmall["lex-small-commits"]
        LexLanguage["lex-commit-language"]
        LexSigned["lex-signed-commits"]
    end

    CryCommit -->|"invoca"| KataCommit
    CryContribute -->|"invoca"| KataContribute
    KataContribute -->|"usa internamente"| KataCommit
    KataContribute -->|"consulta"| CdxContributing
    KataCommit -->|"consulta"| CdxCommitStd
    KataCommit -->|"obedece"| LexConventional
    KataCommit -->|"obedece"| LexSmall
    KataCommit -->|"obedece"| LexLanguage
    KataCommit -->|"obedece"| LexSigned
```

## Inventario de Artefactos

### Lexis (leyes de commit)

| Artefacto | Descripción |
|-----------|-------------|
| `lex-conventional-commits` | Formato obligatorio `type(scope): description` |
| `lex-small-commits` | Un propósito por commit, cambios atómicos |
| `lex-commit-language` | Subject en inglés |
| `lex-signed-commits` | Firma GPG obligatoria |

### Codex (conocimiento)

| Artefacto | Descripción |
|-----------|-------------|
| `codex-contributing` | Flujo completo de contribución (de la discusión al merge) |
| `codex-commit-standards` | Estructura detallada de los mensajes de commit |

### Katas (procedimientos)

| Artefacto | Descripción |
|-----------|-------------|
| `kata-commit` | Procedimiento para crear commits conformes |
| `kata-contribute` | Procedimiento para abrir Pull Requests vía MCP |

### Cries (atajos)

| Artefacto | Descripción |
|-----------|-------------|
| `cry-commit` | Atajo para commitear siguiendo las 4 Lexis |
| `cry-contribute` | Atajo para abrir PR o contribuir al framework |

## Cómo Usar

### Commitear cambios

```
/cry-commit
```

El agente analiza los cambios, crea commits atómicos siguiendo Conventional Commits, con subject en inglés y firma GPG.

### Abrir un Pull Request

```
/cry-contribute pr
```

El agente ejecuta el `kata-contribute`, que crea el PR en el repositorio origin vía herramientas MCP de GitKraken.

### Flujo completo de contribución

El `codex-contributing` define el proceso paso a paso:

1. Abrir discusión en GitHub Discussions (categoría Ideas)
2. Discusión aprobada se convierte en issue
3. Crear branch a partir de main (`feat/nombre`, `fix/nombre`, `docs/nombre`)
4. Implementar (siguiendo Lexis de commit)
5. Abrir PR completando el template
6. Mantener CI verde y responder al review
7. Merge por el maintainer

## Referencias

- [CONTRIBUTING de Guardia](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `.github/pull_request_template.md` — Template de PR
- `.github/CODEOWNERS` — Archivo de codeowners
