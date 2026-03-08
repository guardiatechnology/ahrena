# Codex: Versionado Semántico

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Versionado de releases y tags en repositorios Guardia

## Visión General

Este Codex es la referencia para aplicar Semantic Versioning 2.0 (SemVer) en repositorios Guardia. Define cuándo incrementar MAJOR, MINOR o PATCH, cómo SemVer se relaciona con Conventional Commits y cómo usar git tags para marcar releases. Es consultado por `kata-tag` y por `cry-tag`.

## Contexto

- **Dominio:** Identificadores de versión, releases y tags en Git
- **Público objetivo:** Agentes de IA que ejecutan `kata-tag` y desarrolladores que publican releases
- **Actualización:** Cuando la convención de versionado del proyecto cambie

## Contenido

### Principios

1. **MAJOR (X):** se incrementa cuando hay cambios incompatibles con versiones anteriores (breaking changes). Los consumidores que dependen de la versión anterior pueden necesitar modificaciones.
2. **MINOR (Y):** se incrementa cuando se añade nueva funcionalidad de forma compatible. El código existente sigue funcionando.
3. **PATCH (Z):** se incrementa cuando se realizan correcciones de bugs o ajustes compatibles. El comportamiento público no cambia de forma incompatible.

### Formato de la Versión

```
MAJOR.MINOR.PATCH[-pré-release][+metadatos]
```

| Parte | Obligatoria | Ejemplo |
|-------|:----------:|---------|
| MAJOR.MINOR.PATCH | Sí | `1.2.3` |
| Pré-release | No | `1.2.3-alpha.1`, `1.0.0-rc.2` |
| Metadatos de build | No | `1.2.3+build.42` |

El prefijo `v` en el tag (ej.: `v1.2.3`) se recomienda para compatibilidad con herramientas y convención común. El proyecto DEBE adoptar una forma (`v` o sin `v`) y mantenerla consistente.

### Relación con Conventional Commits

El historial de commits en formato Conventional Commits permite inferir el tipo de bump para la próxima versión:

| Situación en los commits desde el último tag | Incremento recomendado |
|---------------------------------------------|------------------------|
| Al menos un commit con `BREAKING CHANGE:` o tipo `feat!` / `fix!` | MAJOR |
| Al menos un `feat` (sin breaking) | MINOR |
| Solo `fix`, `perf`, `docs`, `chore`, `style`, `refactor`, `test`, `ci`, `build` | PATCH |
| Ningún commit relevante para release | No crear tag o usar pré-release |

Cuando el usuario no indica la versión en `cry-tag` o en `kata-tag`, el agente puede sugerir la próxima versión con base en esta tabla y en el último tag existente.

### Cuándo Incrementar Cada Número

| Componente | Cuándo incrementar | Ejemplo |
|------------|--------------------|---------|
| MAJOR | API pública eliminada o alterada de forma incompatible; cambio de comportamiento que rompe contratos | Eliminación de parámetro obligatorio, cambio de tipo de retorno |
| MINOR | Nueva funcionalidad backward-compatible | Nuevo endpoint, nuevo parámetro opcional |
| PATCH | Corrección de bug, ajuste de documentación, mejora de rendimiento sin cambiar contrato | Bug fix, typo en mensaje, optimización interna |

Tras incrementar MAJOR, MINOR y PATCH se reinician a 0 (ej.: tras `1.2.3`, el siguiente MAJOR es `2.0.0`). Tras incrementar MINOR, PATCH se reinicia a 0 (ej.: `1.2.3` → `1.3.0`).

### Pré-release y Metadatos

- **Pré-release:** identificadores como `alpha`, `beta`, `rc` siguen la especificación SemVer 2.0. Ej.: `v1.2.3-alpha.1`, `v2.0.0-rc.1`. Útiles para publicar versiones de prueba sin alterar el número de release estable.
- **Metadatos de build:** sufijo `+build.42` o `+20260308` no altera la precedencia de la versión. Se usa para distinguir builds del mismo número de versión.

### Aplicación en Git Tags

| Práctica | Descripción |
|----------|-------------|
| Tag en el commit de release | Crear el tag en el commit que representa el estado de ese release (generalmente el último commit del release). |
| Un tag por versión | Cada identificador SemVer (ej.: `v1.2.3`) debe aparecer como máximo una vez en el repositorio. |
| Tags firmadas | Conforme a `lex-signed-commits`, los tags de release DEBEN estar firmados con GPG (`git tag -s`). |
| Tag anotada | Usar `git tag -a` (o `-s` que implica anotada) para incluir mensaje y metadatos; permite changelog y referencia estable. |

Comando típico para crear tag de release:

```
git tag -s v1.2.3 -m "Release 1.2.3"
```

Para enviar el tag al remoto:

```
git push origin v1.2.3
```

### Restricciones Técnicas

- El formato DEBE cumplir la especificación [SemVer 2.0.0](https://semver.org/).
- Los tags de release no pueden usar nombres que no sean SemVer (ej.: `latest`, `release-1.2`).
- El proyecto DEBE documentar si usa prefijo `v` o no y mantener consistencia.

## Glosario

| Término | Definición |
|---------|------------|
| MAJOR | Primer número de la versión; cambios incompatibles |
| MINOR | Segundo número de la versión; nueva funcionalidad compatible |
| PATCH | Tercer número de la versión; correcciones compatibles |
| Pré-release | Identificador opcional tras el PATCH (ej.: alpha, beta, rc) |
| Build metadata | Metadatos opcionales tras `+`; no afectan precedencia |
| Tag anotada | Tag Git que almacena objeto con mensaje y referencia al commit |
| Tag firmada | Tag Git firmada con GPG para verificación de autenticidad |

## Referencias

- [Semantic Versioning 2.0.0](https://semver.org/)
- `lex-semantic-version` — Ley que exige SemVer para releases
- `lex-signed-commits` — Ley que exige firma GPG en tags de release
- `codex-commit-standards` — Tipos de commit e impacto en SemVer
- `kata-tag` — Procedimiento para crear tags conformes
- `cry-tag` — Comando recurrente para ejecutar git tag
