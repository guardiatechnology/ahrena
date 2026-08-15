# Lexis: Segurança em Frontend

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Prevenção de XSS, CSRF, vazamento de credenciais e uso inseguro de dados no frontend

## Lei

> **Toda renderização de conteúdo dinâmico DEVE usar os mecanismos seguros do framework (JSX, template binding) em vez de `innerHTML`. Segredos, API keys e tokens DEVEM estar apenas em variáveis de ambiente do servidor, nunca no bundle do cliente. Inputs do usuário DEVEM ser validados no cliente como UX, e revalidados no servidor como segurança.**

## Regras

### 1. Sem `innerHTML` ou `dangerouslySetInnerHTML` com conteúdo não sanitizado

O agente **NÃO PODE**:

1. Usar `element.innerHTML = untrusted` diretamente.
2. Usar `<div dangerouslySetInnerHTML={{ __html: untrusted }} />` sem sanitização via DOMPurify ou equivalente.
3. Usar `v-html` (Vue) ou `[innerHTML]` (Angular) com conteúdo não confiável.

Alternativa: sempre preferir binding seguro (JSX, template mustache). Se HTML renderizado é necessário (ex.: markdown), sanitizar primeiro:

```typescript
import DOMPurify from "dompurify";
const safeHtml = DOMPurify.sanitize(markdownToHtml(userContent));
```

### 2. Sem segredos no bundle do cliente

O agente **NÃO PODE**:

1. Colocar API keys, client secrets, database URLs em código JavaScript/TypeScript que vai para o bundle.
2. Usar variáveis de ambiente com prefixos públicos (`NEXT_PUBLIC_`, `VITE_`, `REACT_APP_`) para dados sensíveis — esses valores vão para o cliente.
3. Commit de `.env` com valores reais no repositório.

**Apenas valores públicos** (URL da API, client ID de OAuth público, feature flags) podem ir para o bundle. Segredos ficam no servidor (Next.js Server Actions/API Routes, BFF, proxy).

### 3. Autenticação via HttpOnly cookies

Preferir **HttpOnly cookies** para tokens de autenticação:

1. Browser envia automaticamente; não exposto a JavaScript (imune a XSS).
2. Requer CSRF protection (token, SameSite cookie).

**Evitar** armazenar tokens em `localStorage` ou `sessionStorage`:
- `localStorage` é acessível por qualquer script → vazamento em caso de XSS.
- Se usar por limitação de stack, documentar o risco e considerar tokens de curta duração + rotação.

### 4. Validação de input em dois níveis

1. **No cliente (UX):** feedback imediato ao usuário via Zod, Yup, react-hook-form validation. Impede envio obviamente inválido.
2. **No servidor (segurança):** revalidar tudo. Nunca confiar no cliente.

```typescript
const schema = z.object({
  email: z.string().email(),
  age: z.number().int().min(18).max(120),
});
// Cliente valida para UX; servidor revalida para segurança.
```

### 5. Proteção contra CSRF

Para requisições que mudam estado (POST, PUT, DELETE):

1. Se autenticação via cookie: usar `SameSite=Lax` ou `SameSite=Strict`; adicionar CSRF token via header customizado.
2. Se autenticação via Authorization header (Bearer): CSRF é mitigado por padrão (navegador não envia o header em cross-site), mas cuidado com endpoints que aceitam ambos.

### 6. Content Security Policy (CSP)

A aplicação **DEVE** configurar CSP no servidor (header `Content-Security-Policy`):

```
default-src 'self';
script-src 'self' 'nonce-{random}';
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
connect-src 'self' https://api.guardia.com;
frame-ancestors 'none';
```

Evitar `'unsafe-inline'` e `'unsafe-eval'` em `script-src`. Usar nonces ou hashes.

### 7. Dependências auditadas

1. Executar `yarn audit` (ou `npm audit`) no CI.
2. Bloquear CVEs críticos ou altos em dependências usadas no bundle.
3. Manter dependências atualizadas — especialmente frameworks e bibliotecas de auth/crypto.

### 8. URLs externas e `target="_blank"`

Links para URLs externas com `target="_blank"` **DEVEM** incluir:

```html
<a href="https://external.com" target="_blank" rel="noopener noreferrer">...</a>
```

Sem `rel="noopener"`, a página destino pode acessar `window.opener` e manipular o contexto original (tabnabbing).

## Validação Automatizada

- **Ferramenta:**
  - `eslint-plugin-security`, `eslint-plugin-no-unsanitized`
  - `yarn audit` / `npm audit`
  - Lighthouse security audit
  - `retire.js` para detectar libs com vulnerabilidades conhecidas
  - CSP Evaluator (Google) para validar política
- **Momento:** cada PR (lint + audit), cada release (Lighthouse)
- **Métrica:** 0 violações de XSS detectáveis; 0 CVEs críticos; CSP configurada
