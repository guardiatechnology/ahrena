# Codex: Flujo de Contribución Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Contribución a repositorios Guardia

## Visión General

Este Codex documenta el flujo completo de contribución de Guardia — desde la propuesta inicial hasta el merge — incluyendo los dos caminos posibles: contribuidor externo (vía PR) y codeowner (commit directo). Es consultado por el `kata-contribute-pilar` durante el flujo de envío.

## Contexto

- **Dominio:** Flujo de trabajo de contribución open source
- **Público objetivo:** Agentes de IA, desarrolladores y contribuidores de la comunidad
- **Actualización:** Cuando las políticas de contribución de Guardia cambien

## Contenido

### Principios

1. **Discusión primero:** Los cambios significativos comienzan con una discusión, no con código. El alineamiento de expectativas evita retrabajo.
2. **Trazabilidad:** Todo cambio debe estar conectado a una issue. La única excepción son correcciones triviales (errores tipográficos).
3. **Calidad verificable:** CI obligatorio. El código que no pasa las pruebas no es aceptado.
4. **Transparencia:** El proceso es el mismo para todos. Los codeowners tienen un camino más corto, no un camino diferente.

### Flujo para Contribuidores Externos

```
1. Abrir discusión en GitHub Discussions (categoría: Ideas)
   → Explicar: QUÉ, POR QUÉ, CÓMO (Golden Circle)
2. Si es aprobada, la discusión se convierte en issue
3. Fork del repositorio
4. Crear branch a partir de main
5. Implementar el cambio (siguiendo las Lexis de commit)
6. Firmar el CLA (Contributor License Agreement)
7. Abrir PR respondiendo las preguntas estándar
8. Mantener CI verde y responder al review
9. Después de la aprobación, el merge es realizado por el maintainer
```

### Flujo para Codeowners

Los codeowners registrados en `.github/CODEOWNERS` pueden:

```
1. Crear branch directamente (sin fork)
2. Implementar el cambio (siguiendo las Lexis de commit)
3. Push directo al branch
4. Para cambios significativos: abrir PR para visibilidad
5. Para cambios triviales o de framework: commit directo en branch
```

La decisión entre PR y commit directo depende del impacto:

| Tipo de cambio | Camino |
|----------------|--------|
| Nuevo Pilar en el framework | Commit directo (si es codeowner) o PR |
| Cambio que afecta múltiples Clades | PR (incluso para codeowner) |
| Corrección trivial (error tipográfico) | Commit directo |
| Nueva feature en código | PR (siempre) |

### Detección de Codeowner

Para determinar si el contribuidor es codeowner, se debe verificar `.github/CODEOWNERS`:

```
# Ejemplo de CODEOWNERS
* @guardia/guardians
```

El agente puede verificar ejecutando:
```
gh api repos/{owner}/{repo}/collaborators/{username}/permission
```

### Estándares y Convenciones

| Aspecto | Estándar |
|---------|----------|
| Discusiones | GitHub Discussions, categoría "Ideas" |
| Issues | Creadas a partir de discusiones aprobadas |
| Branches | `feat/nombre`, `fix/nombre`, `docs/nombre` |
| PRs | Título en Conventional Commits, body con contexto |
| CLA | Obligatorio para contribuidores externos |
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
| CLA obligatorio para contribuidores externos | Activa |
| Comunicación oficial en inglés | Activa |
| Las issues pueden ser en cualquier idioma | Activa |
| Modelo Open Core con Apache 2.0 para Core Modules | Activa |

### Restricciones Técnicas

- Los PRs con commits no firmados son automáticamente rechazados
- El branch `main` está protegido — merge solo vía PR o por codeowners
- CI es obligatorio — los PRs con checks fallidos no pueden ser fusionados

## Glosario

| Término | Definición |
|---------|-----------|
| Codeowner | Miembro del equipo `@guardia/guardians` listado en `.github/CODEOWNERS` |
| CLA | Contributor License Agreement — acuerdo legal para contribuidores |
| Golden Circle | Framework de comunicación: QUÉ, POR QUÉ, CÓMO |
| Branch protection | Reglas de GitHub que protegen branches de cambios directos |

## Referencias

- [CONTRIBUTING de Guardia](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- [CLA de Guardia](https://hub.guardia.finance/docs/community/governance/CLA/)
- `.github/CODEOWNERS` — Archivo de codeowners del repositorio
- `lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language` — Lexis de commit
- `codex-commit-standards` — Estándares de mensaje de commit
- `kata-contribute-pilar` — Procedimiento para contribuir Pilares
