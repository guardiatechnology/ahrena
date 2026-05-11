# Lexis: Versionado Semántico Obligatorio

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Versiones y tags de release en repositorios Guardia

## Propósito

Los identificadores de versión predecibles permiten que consumidores, herramientas y pipelines sepan el tipo de cambio entre releases. Semantic Versioning 2.0 (SemVer) establece un contrato claro: MAJOR para cambios incompatibles, MINOR para funcionalidades compatibles, PATCH para correcciones compatibles.

Esta Lexis garantiza que todo release en repositorios Guardia use el mismo estándar, permitiendo automatización de changelogs, dependencias y CI/CD.

## Ley

> **Todo identificador de versión de release y todo tag de release DEBE seguir Semantic Versioning 2.0 (MAJOR.MINOR.PATCH). Ninguna excepción.**

## Reglas

### 1. Formato obligatorio

El identificador de versión DEBE tener el formato `X.Y.Z`, donde:

- **MAJOR (X):** entero no negativo; se incrementa cuando hay cambios incompatibles en la API
- **MINOR (Y):** entero no negativo; se incrementa cuando se añade nueva funcionalidad de forma compatible
- **PATCH (Z):** entero no negativo; se incrementa cuando se realizan correcciones compatibles

### 2. Tags en Git

Los tags usados para marcar releases DEBEN usar el formato SemVer. El prefijo `v` se recomienda para compatibilidad con herramientas (ej.: `v1.2.3`). Las variantes `v1.2.3` y `1.2.3` son aceptadas; el proyecto DEBE adoptar una convención y mantenerla consistente.

### 3. Tags de release firmados y anotados

Los tags de release también DEBEN estar firmados con GPG, conforme a `lex-signed-commits`, y anotados (`git tag -a -s`), conforme a `lex-annotated-tags`. Los tags lightweight son técnicamente incapaces de cargar firma — solo los tags anotados soportan GPG.

### 4. Pré-release y metadatos

Los identificadores de pré-release (ej.: `v1.2.3-alpha.1`) y metadatos de build (ej.: `v1.2.3+build.42`) siguen la especificación SemVer 2.0 y están permitidos cuando se documentan en `codex-semantic-version`.

## Alcance

- **Se aplica a:** todos los repositorios Guardia que publican releases versionados
- **Agentes vinculados:** todos
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Inconsistencia:** consumidores y herramientas no pueden inferir el tipo de cambio
2. **Automatización rota:** pipelines que dependen de orden semántico o parsing de versión fallan
3. **Remediación:** crear nuevo tag en el formato correcto; documentar la convención en el repositorio

## Ejemplos

### Correcto

```
v1.0.0
v2.1.3
1.0.0
v1.2.3-alpha.1
v1.2.3+build.42
```

### Incorrecto

```
release-1.2      # no es MAJOR.MINOR.PATCH
1.2              # falta PATCH
v1.2.3.4         # más de tres segmentos numéricos (a menos que sea pré-release/metadatos SemVer)
latest           # identificador no numérico para release
```

## Validación Automatizada

- **Herramienta:** validación por regex o parser SemVer (ej.: en CI o pre-push hook)
- **Momento:** antes del push de tag o en el pipeline de release
- **Métrica:** 0 tags de release en formato inválido toleradas

## Referencias

- [Semantic Versioning 2.0.0](https://semver.org/)
- `lex-signed-commits` — Firma GPG obligatoria para tags de release
- `lex-annotated-tags` — Los tags empujados al remoto DEBEN ser anotados + firmados
- `codex-semantic-version` — Manual de referencia para aplicación de SemVer en el proyecto
