# Lexis: Seguridad en Frontend

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Prevención de XSS, CSRF, filtración de credenciales y uso inseguro de datos en el frontend

## Propósito

El frontend es el primer objetivo de los ataques: corre en el navegador del usuario, es visible para cualquiera con DevTools y recibe datos de fuentes no confiables (URLs, inputs, APIs externas). El código frontend inseguro permite XSS (inyección de scripts en el contexto del usuario), filtración de tokens, CSRF y exposición de datos sensibles. Los agentes IA que generan frontend deben tratar la seguridad como un prerrequisito, no como un ítem opcional.

Esta Lexis existe para garantizar que **todo contenido dinámico sea escapado**, que **credenciales y secretos nunca aparezcan en el código bundled**, que **los headers de seguridad estén configurados** y que **los inputs del usuario sean validados en el cliente** (además del servidor).

## Ley

> **Toda renderización de contenido dinámico DEBE usar los mecanismos seguros del framework (JSX, template binding) en vez de `innerHTML`. Los secretos, API keys y tokens DEBEN estar únicamente en variables de entorno del servidor, nunca en el bundle del cliente. Los inputs del usuario DEBEN ser validados en el cliente como UX, y revalidados en el servidor como seguridad.**

## Reglas

### 1. Sin `innerHTML` o `dangerouslySetInnerHTML` con contenido no sanitizado

El agente **NO PUEDE**:

1. Usar `element.innerHTML = untrusted` directamente.
2. Usar `<div dangerouslySetInnerHTML={{ __html: untrusted }} />` sin sanitización vía DOMPurify o equivalente.
3. Usar `v-html` (Vue) o `[innerHTML]` (Angular) con contenido no confiable.

Alternativa: siempre preferir binding seguro (JSX, template mustache). Si es necesario renderizar HTML (ej.: markdown), sanitizar primero:

```typescript
import DOMPurify from "dompurify";
const safeHtml = DOMPurify.sanitize(markdownToHtml(userContent));
```

### 2. Sin secretos en el bundle del cliente

El agente **NO PUEDE**:

1. Colocar API keys, client secrets, database URLs en código JavaScript/TypeScript que va al bundle.
2. Usar variables de entorno con prefijos públicos (`NEXT_PUBLIC_`, `VITE_`, `REACT_APP_`) para datos sensibles — esos valores van al cliente.
3. Hacer commit de `.env` con valores reales en el repositorio.

**Solo valores públicos** (URL de la API, client ID de OAuth público, feature flags) pueden ir al bundle. Los secretos permanecen en el servidor (Next.js Server Actions/API Routes, BFF, proxy).

### 3. Autenticación vía HttpOnly cookies

Preferir **HttpOnly cookies** para tokens de autenticación:

1. El browser los envía automáticamente; no están expuestos a JavaScript (inmunes a XSS).
2. Requiere CSRF protection (token, SameSite cookie).

**Evitar** almacenar tokens en `localStorage` o `sessionStorage`:
- `localStorage` es accesible por cualquier script → filtración en caso de XSS.
- Si se usa por limitación del stack, documentar el riesgo y considerar tokens de corta duración + rotación.

### 4. Validación de input en dos niveles

1. **En el cliente (UX):** feedback inmediato al usuario vía Zod, Yup, react-hook-form validation. Impide envío obviamente inválido.
2. **En el servidor (seguridad):** revalidar todo. Nunca confiar en el cliente.

```typescript
const schema = z.object({
  email: z.string().email(),
  age: z.number().int().min(18).max(120),
});
// El cliente valida para UX; el servidor revalida para seguridad.
```

### 5. Protección contra CSRF

Para requests que cambian estado (POST, PUT, DELETE):

1. Si la autenticación es vía cookie: usar `SameSite=Lax` o `SameSite=Strict`; agregar CSRF token vía header personalizado.
2. Si la autenticación es vía Authorization header (Bearer): CSRF se mitiga por defecto (el navegador no envía el header en cross-site), pero cuidado con endpoints que aceptan ambos.

### 6. Content Security Policy (CSP)

La aplicación **DEBE** configurar CSP en el servidor (header `Content-Security-Policy`):

```
default-src 'self';
script-src 'self' 'nonce-{random}';
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
connect-src 'self' https://api.guardia.com;
frame-ancestors 'none';
```

Evitar `'unsafe-inline'` y `'unsafe-eval'` en `script-src`. Usar nonces o hashes.

### 7. Dependencias auditadas

1. Ejecutar `yarn audit` (o `npm audit`) en CI.
2. Bloquear CVEs críticos o altos en dependencias usadas en el bundle.
3. Mantener las dependencias actualizadas, especialmente frameworks y librerías de auth/crypto.

### 8. URLs externas y `target="_blank"`

Los enlaces a URLs externas con `target="_blank"` **DEBEN** incluir:

```html
<a href="https://external.com" target="_blank" rel="noopener noreferrer">...</a>
```

Sin `rel="noopener"`, la página destino puede acceder a `window.opener` y manipular el contexto original (tabnabbing).

## Alcance

- **Aplica a:** todo código frontend que manipula datos dinámicos, credenciales o autenticación
- **Agentes vinculados:** `warrior-hephaestus`
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **XSS:** el atacante inyecta JavaScript en el contexto del usuario — puede robar tokens, hacer acciones en nombre del usuario, exfiltrar datos
2. **Filtración de credenciales:** los secretos en el bundle se extraen en minutos; requieren rotación inmediata
3. **CSRF:** acciones no autorizadas ejecutadas en nombre del usuario autenticado
4. **Remediación:**
   - XSS: sanitizar todos los puntos de inserción; revisar código con DOMPurify o equivalente
   - Secretos filtrados: rotar inmediatamente; auditar logs de acceso
   - Revisar CSP y headers de seguridad

## Validación Automatizada

- **Herramienta:**
  - `eslint-plugin-security`, `eslint-plugin-no-unsanitized`
  - `yarn audit` / `npm audit`
  - Lighthouse security audit
  - `retire.js` para detectar libs con vulnerabilidades conocidas
  - CSP Evaluator (Google) para validar la política
- **Momento:** cada PR (lint + audit), cada release (Lighthouse)
- **Métrica:** 0 violaciones de XSS detectables; 0 CVEs críticos; CSP configurada

## Referencias

- [OWASP Top 10 (con foco en A03 Injection, A07 Auth Failures)](https://owasp.org/www-project-top-ten/)
- [MDN — Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- `lex-mcp` — nunca hardcoded credentials
- `lex-python-security` — equivalente en el backend
