# Codex: Flujo de Contribución Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Contribución a repositorios Guardia

## Visión General

Este Codex documenta el flujo de contribución de Guardia, desde la propuesta inicial hasta el merge. El proceso es único para todos los contribuidores (internos y externos), garantizando transparencia y trazabilidad. Es consultado por el `kata-contribute` durante el flujo de envío.

## Contexto

- **Dominio:** Flujo de trabajo de contribución open source
- **Público objetivo:** Agentes de IA, desarrolladores y contribuidores de la comunidad
- **Actualización:** Cuando las políticas de contribución de Guardia cambien

## Contenido

### Principios

1. **Discusión primero:** Los cambios significativos comienzan con una discusión, no con código. El alineamiento de expectativas evita retrabajo.
2. **Trazabilidad:** Todo cambio debe estar conectado a una issue. La única excepción son las correcciones triviales (typos).
3. **Calidad verificable:** CI obligatorio. El código que no pasa los tests no es aceptado.
4. **Transparencia:** El proceso es el mismo para todos. Sin atajos, sin excepciones.

### Flujo de Contribución

```
1. Abrir discusión en GitHub Discussions (categoría: Ideas)
   → Explicar: QUÉ, POR QUÉ, CÓMO (Golden Circle)
2. Si se aprueba, la discusión se convierte en issue
3. Crear branch a partir de main
   → Convención: feat/nombre, fix/nombre, docs/nombre
4. Implementar el cambio (siguiendo Lexis de commit)
5. Abrir PR rellenando la plantilla .github/pull_request_template.md
6. Mantener CI verde y responder al review
7. Tras aprobación, el merge lo realiza el maintainer
```

Para correcciones triviales (typos, formato), los pasos 1 y 2 pueden omitirse (abrir PR directamente con referencia al problema).

### Estándares y Convenciones

| Aspecto | Estándar |
|---------|----------|
| Discusiones | GitHub Discussions, categoría "Ideas" |
| Issues | Creadas a partir de discusiones aprobadas |
| Branches | `feat/nombre`, `fix/nombre`, `docs/nombre` |
| PRs | Título en Conventional Commits, body con plantilla rellenada |
| CI | Debe pasar antes del merge |

### Requisitos de PR

| Requisito | Detalles |
|-----------|----------|
| Commits firmados | Todos "Verified" (`lex-signed-commits`) |
| Formato de commits | Conventional Commits (`lex-conventional-commits`) |
| Commits atómicos | Un cambio por commit (`lex-small-commits`) |
| Idioma | Subject en inglés (`lex-commit-language`) |
| Sin conflictos | Branch actualizado con main |
| CI verde | Todos los checks pasando |
| Review | Al menos un aprobador |

### Decisiones Vigentes

| Decisión | Estado |
|----------|--------|
| Comunicación oficial en inglés | Activa |
| Issues pueden estar en cualquier idioma | Activa |
| Modelo Open Core con Apache 2.0 para Core Modules | Activa |

### Restricciones Técnicas

- Los PRs con commits no firmados se rechazan automáticamente
- El branch `main` está protegido — merge solo vía PR aprobado
- El CI es obligatorio — los PRs con checks fallidos no pueden ser merged

## Glosario

| Término | Definición |
|---------|------------|
| Golden Circle | Framework de comunicación: QUÉ, POR QUÉ, CÓMO |
| Branch protection | Reglas de GitHub que protegen branches de cambios directos |

## Referencias

- [CONTRIBUTING de Guardia](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `.github/CODEOWNERS` — Archivo de codeowners del repositorio
- `lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language` — Lexis de commit
- `codex-commit-standards` — Estándares de mensaje de commit
- `kata-contribute` — Procedimiento para contribuir vía PR
