# Lexis: Conventional Commits Obligatorio

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Todos los commits en repositorios Guardia

## Propósito

Un historial de commits legible y estandarizado es fundamental para el versionado semántico automático, la generación de changelogs y la comprensión de la evolución del código. Sin un formato uniforme, el historial se vuelve ruidoso y pierde valor como herramienta de trazabilidad.

Esta Lexis garantiza que todo commit siga el formato Conventional Commits, alineado con las directrices del CONTRIBUTING de Guardia.

## Ley

> **Todo commit DEBE seguir el formato Conventional Commits: `<tipo>[alcance opcional]: <descripción>`.**

## Reglas

### 1. Formato obligatorio

Todo commit debe seguir la estructura:

```
<tipo>[alcance opcional]: <descripción>

[cuerpo opcional]

[pie(s) opcional(es)]
```

### 2. Tipos permitidos

| Tipo | Cuándo se utiliza |
|------|-------------------|
| `feat` | Nueva funcionalidad (correlaciona con MINOR en SemVer) |
| `fix` | Corrección de error (correlaciona con PATCH en SemVer) |
| `docs` | Cambios en documentación |
| `build` | Cambios en el sistema de build o dependencias externas |
| `chore` | Tareas de mantenimiento que no alteran código de producción |
| `ci` | Cambios en configuración de CI/CD |
| `style` | Formato, punto y coma, espacios — sin cambio de lógica |
| `refactor` | Refactorización que no agrega funcionalidad ni corrige errores |
| `perf` | Mejora de rendimiento |
| `test` | Adición o corrección de pruebas |

### 3. Breaking changes

Los commits que introducen cambios incompatibles DEBEN:
- Agregar `!` después del tipo/alcance: `feat(api)!: change auth endpoint`
- O incluir `BREAKING CHANGE:` en el pie

### 4. Alcance

El alcance es opcional y proporciona contexto adicional entre paréntesis: `feat(auth): add OAuth2 support`.

## Alcance

- **Se aplica a:** todos los repositorios Guardia
- **Agentes vinculados:** todos
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Bloqueo automático:** commit rechazado por hook o CI
2. **Alerta:** PR marcado como non-compliant
3. **Remediación:** reescribir el commit con `git commit --amend` o `git rebase -i`

## Ejemplos

### Correcto

```
feat(auth): implement OAuth2 authentication

[pt-BR]
Implementa fluxo de autenticação OAuth2 com suporte para múltiplos provedores.

Closes #123
```

```
fix: resolve null pointer in transaction processing
```

```
docs(api): update endpoint documentation for v2
```

### Incorrecto

```
# Sin tipo — VIOLA LA LEY
updated the login page

# Tipo inválido — VIOLA LA LEY
feature: add new button

# Múltiples cambios mezclados — VIOLA lex-small-commits también
feat: add login, fix header, update docs
```

## Validación Automatizada

- **Herramienta:** commitlint con `@commitlint/config-conventional`
- **Momento:** pre-commit hook y CI pipeline
- **Métrica:** 0 commits fuera del formato tolerados

## Referencias

- [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [CONTRIBUTING de Guardia](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `codex-commit-standards` — Guía completa sobre cómo escribir buenos mensajes
- `kata-commit` — Procedimiento para realizar commits conformes
