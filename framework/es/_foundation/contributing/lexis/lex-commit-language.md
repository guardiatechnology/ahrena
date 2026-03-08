# Lexis: Idioma de Commits

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Todos los commits en repositorios Guardia

## Propósito

El inglés es la lengua franca de la ingeniería de software. Los mensajes de commit en inglés garantizan que cualquier contribuidor — independientemente del idioma nativo — pueda comprender el historial del proyecto. Al mismo tiempo, permitir el cuerpo en idioma local con etiqueta ayuda a mitigar errores de traducción.

Esta Lexis garantiza que el mensaje principal del commit sea en inglés, con opción de cuerpo en idioma local, conforme lo definido por el CONTRIBUTING de Guardia.

## Ley

> **El mensaje principal (subject) de todo commit DEBE estar escrito en inglés. El cuerpo (body) PUEDE incluir texto en idioma local, siempre que esté precedido por la etiqueta `[idioma]`.**

## Reglas

### 1. Subject en inglés

La primera línea del commit (subject) DEBE estar escrita en inglés, siguiendo el formato Conventional Commits.

### 2. Body con etiqueta de idioma

Si se desea incluir una descripción en idioma local, se DEBE utilizar la etiqueta de idioma entre corchetes en el cuerpo:
- `[pt-BR]` para portugués brasileño
- `[es]` para español
- Cualquier código BCP 47 válido

### 3. Traducción en inglés primero

Si el body contiene texto en idioma local, la versión en inglés DEBE aparecer primero (con etiqueta `[en]`), seguida por la versión local.

### 4. Herramientas de traducción

Se recomienda el uso de herramientas como DeepL o Google Traductor para garantizar la calidad del mensaje en inglés. Mantener el texto original junto con la traducción ayuda a mitigar errores.

## Alcance

- **Se aplica a:** todos los repositorios Guardia
- **Agentes vinculados:** todos
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Bloqueo automático:** commit con subject en idioma no inglés es señalizado
2. **Alerta:** el revisor solicita la corrección del subject
3. **Remediación:** reescribir con `git commit --amend`

## Ejemplos

### Correcto

```
feat(auth): implement OAuth2 authentication

[en]
Implement OAuth2 authentication flow with support for multiple providers:
- Add OAuth2 client configuration
- Create authentication handlers for Google and GitHub
- Implement token validation and refresh logic
- Add unit tests for auth flow

[es]
Implementa flujo de autenticación OAuth2 con soporte para múltiples proveedores:
- Agrega configuración del cliente OAuth2
- Crea handlers de autenticación para Google y GitHub
- Implementa lógica de validación y actualización de tokens
- Agrega pruebas unitarias para el flujo de auth

Closes #123
```

```
fix: resolve null pointer in transaction processing
```

### Incorrecto

```
# Subject en español — VIOLA LA LEY
feat(auth): implementar autenticación OAuth2

# Body sin etiqueta de idioma — VIOLA LA LEY
feat(auth): implement OAuth2

Implementa flujo de autenticación OAuth2.
(Falta la etiqueta [es] antes del texto en español)
```

## Validación Automatizada

- **Herramienta:** commitlint con regla personalizada para idioma del subject
- **Momento:** pre-commit hook y CI pipeline
- **Métrica:** 100% de los subjects en inglés

## Referencias

- [CONTRIBUTING de Guardia — Idiomas](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `lex-conventional-commits` — Formato obligatorio de commits
- `codex-commit-standards` — Guía completa de estándares de commit
