# Lexis: Frontend Security

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Prevention of XSS, CSRF, credential leakage, and insecure use of data in the frontend

## Law

> **All dynamic content rendering MUST use the framework's safe mechanisms (JSX, template binding) instead of `innerHTML`. Secrets, API keys, and tokens MUST only exist in server environment variables, never in the client bundle. User inputs MUST be validated on the client as UX, and revalidated on the server as security.**

## Rules

### 1. No `innerHTML` or `dangerouslySetInnerHTML` with unsanitized content

The agent **MUST NOT**:

1. Use `element.innerHTML = untrusted` directly.
2. Use `<div dangerouslySetInnerHTML={{ __html: untrusted }} />` without sanitization via DOMPurify or equivalent.
3. Use `v-html` (Vue) or `[innerHTML]` (Angular) with untrusted content.

Alternative: always prefer safe binding (JSX, template mustache). If rendered HTML is necessary (e.g., markdown), sanitize first:

```typescript
import DOMPurify from "dompurify";
const safeHtml = DOMPurify.sanitize(markdownToHtml(userContent));
```

### 2. No secrets in the client bundle

The agent **MUST NOT**:

1. Place API keys, client secrets, database URLs in JavaScript/TypeScript code that goes to the bundle.
2. Use environment variables with public prefixes (`NEXT_PUBLIC_`, `VITE_`, `REACT_APP_`) for sensitive data — those values go to the client.
3. Commit `.env` with real values to the repository.

**Only public values** (API URL, public OAuth client ID, feature flags) may go to the bundle. Secrets stay on the server (Next.js Server Actions/API Routes, BFF, proxy).

### 3. Authentication via HttpOnly cookies

Prefer **HttpOnly cookies** for authentication tokens:

1. Browser sends automatically; not exposed to JavaScript (immune to XSS).
2. Requires CSRF protection (token, SameSite cookie).

**Avoid** storing tokens in `localStorage` or `sessionStorage`:
- `localStorage` is accessible by any script → leakage in case of XSS.
- If used due to stack limitation, document the risk and consider short-lived tokens + rotation.

### 4. Two-level input validation

1. **On the client (UX):** immediate feedback to the user via Zod, Yup, react-hook-form validation. Prevents obviously invalid submission.
2. **On the server (security):** revalidate everything. Never trust the client.

```typescript
const schema = z.object({
  email: z.string().email(),
  age: z.number().int().min(18).max(120),
});
// Client validates for UX; server revalidates for security.
```

### 5. CSRF protection

For state-changing requests (POST, PUT, DELETE):

1. If cookie-based authentication: use `SameSite=Lax` or `SameSite=Strict`; add CSRF token via custom header.
2. If Authorization header (Bearer) authentication: CSRF is mitigated by default (browser does not send the header cross-site), but beware of endpoints that accept both.

### 6. Content Security Policy (CSP)

The application **MUST** configure CSP on the server (`Content-Security-Policy` header):

```
default-src 'self';
script-src 'self' 'nonce-{random}';
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
connect-src 'self' https://api.guardia.com;
frame-ancestors 'none';
```

Avoid `'unsafe-inline'` and `'unsafe-eval'` in `script-src`. Use nonces or hashes.

### 7. Audited dependencies

1. Run `yarn audit` (or `npm audit`) in CI.
2. Block critical or high CVEs in dependencies used in the bundle.
3. Keep dependencies up to date — especially frameworks and auth/crypto libraries.

### 8. External URLs and `target="_blank"`

Links to external URLs with `target="_blank"` **MUST** include:

```html
<a href="https://external.com" target="_blank" rel="noopener noreferrer">...</a>
```

Without `rel="noopener"`, the destination page can access `window.opener` and manipulate the original context (tabnabbing).

## Applicability

- **Applies to:** all frontend code that manipulates dynamic data, credentials, or authentication
- **Linked agents:** `warrior-hephaestus`
- **Exceptions:** None. Lexis admit no exceptions.

## Automated Validation

- **Tool:**
  - `eslint-plugin-security`, `eslint-plugin-no-unsanitized`
  - `yarn audit` / `npm audit`
  - Lighthouse security audit
  - `retire.js` to detect libs with known vulnerabilities
  - CSP Evaluator (Google) to validate policy
- **Moment:** every PR (lint + audit), every release (Lighthouse)
- **Metric:** 0 detectable XSS violations; 0 critical CVEs; CSP configured
