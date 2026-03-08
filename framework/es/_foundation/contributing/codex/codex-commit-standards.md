# Codex: Estándares de Commit

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Escritura de mensajes de commit en repositorios Guardia

## Visión General

Este Codex es la referencia completa sobre cómo escribir buenos mensajes de commit siguiendo el formato Conventional Commits, las reglas de idioma y las buenas prácticas de Guardia. Es consultado por el `kata-commit` durante la composición de mensajes.

## Contexto

- **Dominio:** Mensajes de commit e historial de versionado
- **Público objetivo:** Agentes de IA que ejecutan `kata-commit` y desarrolladores
- **Actualización:** Cuando las convenciones de commit de Guardia cambien

## Contenido

### Principios

1. **Claridad:** El mensaje debe comunicar qué cambió y por qué, sin ambigüedad.
2. **Trazabilidad:** Cada commit debe poder conectarse a una issue, decisión o contexto.
3. **Automatización:** El formato debe permitir la generación automática de changelogs y versionado semántico.
4. **Accesibilidad:** Cualquier persona debe comprender el commit sin leer el diff.

### Estructura del Mensaje

```
<tipo>[alcance opcional]: <descripción>

[cuerpo opcional]

[pie(s) opcional(es)]
```

| Parte | Obligatoria | Reglas |
|-------|:-----------:|--------|
| Tipo | Sí | Uno de los tipos permitidos por `lex-conventional-commits` |
| Alcance | No | Contexto entre paréntesis (ej: `auth`, `api`, `db`) |
| Descripción (subject) | Sí | Imperativo, presente, máximo 72 caracteres, en inglés |
| Cuerpo (body) | No | Detalla el "por qué", puede incluir etiqueta `[idioma]` |
| Pie (footer) | No | Referencias, breaking changes, co-authors |

### Tipos — Cuándo Utilizar Cada Uno

| Tipo | Uso | Impacto SemVer | Ejemplo |
|------|-----|:--------------:|---------|
| `feat` | Nueva funcionalidad para el usuario | MINOR | `feat(payments): add PIX support` |
| `fix` | Corrección de error | PATCH | `fix(auth): resolve token expiration race condition` |
| `docs` | Documentación | Ninguno | `docs(api): update rate limiting section` |
| `build` | Sistema de build, dependencias | Ninguno | `build: upgrade Go to 1.22` |
| `chore` | Mantenimiento sin impacto en producción | Ninguno | `chore: update .gitignore` |
| `ci` | Configuración de CI/CD | Ninguno | `ci: add coverage report to pipeline` |
| `style` | Formato sin cambio de lógica | Ninguno | `style: fix indentation in handler` |
| `refactor` | Refactorización sin cambio de comportamiento | Ninguno | `refactor(core): extract validation logic` |
| `perf` | Mejora de rendimiento | PATCH | `perf(query): add index for user lookup` |
| `test` | Adición o corrección de pruebas | Ninguno | `test(auth): add integration tests for OAuth2` |

### Cómo Escribir Buenos Subjects

| Regla | Ejemplo Bueno | Ejemplo Malo |
|-------|---------------|-------------|
| Imperativo presente | `add user validation` | `added user validation` |
| Sin punto final | `fix null pointer` | `fix null pointer.` |
| Máximo 72 caracteres | `feat(auth): add OAuth2 support` | `feat(auth): add OAuth2 support with Google, GitHub, and Microsoft providers including token refresh` |
| Letra minúscula después del tipo | `feat: add support` | `feat: Add Support` |
| En inglés | `fix: resolve timeout` | `fix: resolver timeout` |

### Cómo Utilizar Alcances

El alcance contextualiza el cambio. Buenas prácticas:

| Práctica | Ejemplo |
|----------|---------|
| Utilizar nombre del módulo/dominio | `feat(payments): ...` |
| Consistencia dentro del proyecto | Siempre `auth`, nunca alternar con `authentication` |
| Omitir cuando el cambio es transversal | `chore: update dependencies` |

### Cómo Estructurar el Body

```
feat(auth): implement OAuth2 authentication

[en]
Implement OAuth2 authentication flow with support for multiple providers:
- Add OAuth2 client configuration
- Create authentication handlers for Google and GitHub
- Implement token validation and refresh logic

[es]
Implementa flujo de autenticación OAuth2 con soporte para múltiples proveedores:
- Agrega configuración del cliente OAuth2
- Crea handlers de autenticación para Google y GitHub
- Implementa lógica de validación y actualización de tokens

Closes #123
```

Reglas del body:
- Versión en inglés (`[en]`) primero
- Versión en idioma local con etiqueta BCP 47 (`[pt-BR]`, `[es]`)
- Línea en blanco entre subject y body
- Pies al final: `Closes #123`, `BREAKING CHANGE:`, `Co-authored-by:`

### Breaking Changes

Dos formas válidas de indicar un breaking change:

```
# Forma 1: ! después del tipo/alcance
feat(api)!: change authentication endpoint

BREAKING CHANGE: /auth/login moved to /v2/auth/login

# Forma 2: solo en el pie
feat(api): change authentication endpoint

BREAKING CHANGE: /auth/login moved to /v2/auth/login
```

### Estándares y Convenciones

| Aspecto | Estándar | Referencia |
|---------|----------|------------|
| Formato | Conventional Commits v1.0.0 | `lex-conventional-commits` |
| Firma | GPG obligatoria | `lex-signed-commits` |
| Granularidad | Atómico, un cambio | `lex-small-commits` |
| Idioma | Subject en inglés | `lex-commit-language` |

### Restricciones Técnicas

- El subject no puede exceder 72 caracteres
- Línea en blanco obligatoria entre subject y body
- El tipo debe ser uno de los 10 tipos permitidos
- Los breaking changes deben utilizar `!` o `BREAKING CHANGE:` en el pie

## Glosario

| Término | Definición |
|---------|-----------|
| Subject | Primera línea del commit: `tipo(alcance): descripción` |
| Body | Texto detallado después del subject, separado por línea en blanco |
| Footer | Metadatos al final: referencias, breaking changes, co-authors |
| Alcance | Contexto entre paréntesis que indica el módulo o dominio afectado |
| Breaking change | Cambio que rompe la compatibilidad con versiones anteriores |

## Referencias

- [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [CONTRIBUTING de Guardia](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `lex-conventional-commits` — Ley de formato obligatorio
- `lex-signed-commits` — Ley de firma GPG
- `lex-small-commits` — Ley de commits atómicos
- `lex-commit-language` — Ley de idioma de commits
- `kata-commit` — Procedimiento para realizar commits conformes
