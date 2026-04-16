# Codex: Arquitectura Frontend

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Patrones arquitecturales para aplicaciones frontend modernas (React/Next.js como referencia; adaptable a Vue/Angular/Svelte)

## Visión General

Este Codex es la referencia para decisiones arquitecturales en frontend: cómo organizar componentes, dónde ubicar la lógica de negocio, cómo gestionar estado, cómo estructurar el ruteo, cómo abstraer la capa de datos. Consultado por `warrior-hephaestus` y por agentes que implementan features frontend.

La referencia principal asume **React + TypeScript + Next.js**, pero los principios son transferibles a Vue (Composition API + Pinia), Angular (standalone components + Signals) y Svelte (SvelteKit + stores).

## Contexto

- **Dominio:** arquitectura de aplicaciones frontend SPA o SSR
- **Público objetivo:** `warrior-hephaestus`, agentes que implementan UI
- **Actualización:** cuando el framework principal del proyecto cambia, cuando emergen nuevos patrones (Server Components, Signals, etc.)

## Contenido

### Capas de una aplicación frontend

```
┌─────────────────────────────────────────────────┐
│  Pages / Routes                                 │  (Next.js app/, Vue router, Angular routes)
│  - Composición de features en una página        │
├─────────────────────────────────────────────────┤
│  Features                                       │
│  - Bloques auto-contenidos de funcionalidad     │
│  - (ej.: refund-form, transaction-list)         │
├─────────────────────────────────────────────────┤
│  Components (UI kit)                            │
│  - Primitivos reutilizables: Button, Input,     │
│    Modal, Table. Sin lógica de negocio.         │
├─────────────────────────────────────────────────┤
│  Hooks / Composables                            │
│  - Lógica reutilizable: useAuth, useQuery,      │
│    useForm. Sin UI.                             │
├─────────────────────────────────────────────────┤
│  Services / API clients                         │
│  - Capa de acceso a la API HTTP                 │
│  - Tipos derivados del OAS                      │
├─────────────────────────────────────────────────┤
│  State (server + client)                        │
│  - Server state: React Query / SWR / TanStack   │
│  - Client state: Zustand / Jotai / Context      │
└─────────────────────────────────────────────────┘
```

### Principios de composición de componentes

1. **Single Responsibility:** un componente hace una cosa bien. Si el archivo supera las 200 líneas o tiene más de 3 responsabilidades visuales, dividir.
2. **Presentational vs Container:**
   - **Presentational:** recibe datos vía props, no hace I/O. Fácil de probar y reutilizar.
   - **Container:** busca datos, combina hooks, los pasa al presentational.
   - En React moderno con hooks, la separación es más fluida, pero el principio se mantiene: mantener la composición clara.
3. **Props mínimas y tipadas:** no pasar objetos grandes cuando 2-3 campos bastan.
4. **Composición sobre configuración:** `<Card><CardHeader/><CardBody/></Card>` es más flexible que `<Card variant="big" showHeader />`.
5. **Sin efectos colaterales en renderización:** `useEffect` para side effects; render puro para UI.

### Gestión de estado

**Regla fundamental:** separar **server state** de **client state**.

| Tipo | Ejemplo | Herramienta |
|---|---|---|
| **Server state** | Lista de refunds, perfil del usuario | **TanStack Query (React Query)**, SWR, RTK Query |
| **Client state global** | Tema, idioma, carrito (pre-checkout) | **Zustand**, Jotai, Context API |
| **Form state** | Campos de formulario en edición | **react-hook-form**, Formik, VeeValidate |
| **URL state** | Filtros, paginación, modal abierto | **searchParams** (Next.js), `useSearchParams` |
| **Local state** | Estado efímero de un componente | `useState`, `useReducer` |

**Antipatrones a evitar:**
- Redux para todo — useState local es suficiente en el 70% de los casos
- Context para estado que cambia frecuentemente — causa re-render en cascada
- Duplicar server state en client state — mantener la query como fuente de verdad

### Capa de datos (HTTP)

1. **Cliente HTTP centralizado:** un `apiClient` configurado con baseURL, interceptors, auth.
2. **Tipos derivados del OAS:** usar `openapi-typescript` u `orval` para generar tipos a partir del spec (producido por `warrior-daedalus`).
3. **Queries y mutations:**
   - `useQuery` para lectura; cache automático, background refetch.
   - `useMutation` para escritura; optimistic updates cuando sea aplicable.
4. **Manejo de errores:** `error boundary` para errores inesperados; `onError` de las queries para errores esperados.

### Ruteo

1. **File-based (Next.js app/):** páginas definidas por la estructura de carpetas.
2. **Layout compartido:** headers, sidebars en `layout.tsx` para evitar duplicación.
3. **Loading y error states:** `loading.tsx`, `error.tsx` en Next.js app router.
4. **Code splitting automático:** cada ruta en un chunk separado; lazy load de features no críticas.

### Estilización

Opciones principales (elegir una y mantener consistente):

| Enfoque | Cuándo usar |
|---|---|
| **Tailwind CSS** | Prototipado rápido; equipos grandes; design system consistente |
| **CSS Modules** | Encapsulamiento por componente; sin runtime overhead |
| **CSS-in-JS (Emotion, Styled)** | Temas dinámicos; compartir valores con JS |
| **Vanilla Extract** | Zero runtime; types en CSS |

**Regla transversal:** definir **design tokens** (colores, espaciados, tipografía) en un único lugar, referenciados en todos los componentes.

### Performance

1. **Code splitting:** React.lazy, dynamic import, route-based splits.
2. **Memoization:** `useMemo`/`useCallback` solo cuando el profiling muestra ganancia real.
3. **Virtualización:** las listas grandes (>100 items visibles) usan `react-window` o TanStack Virtual.
4. **Imágenes:** `next/image` (Next.js) o equivalente para srcset, lazy load, WebP/AVIF.
5. **Prefetching:** `<Link prefetch>` para rutas probables.
6. **Core Web Vitals como métrica objetivo:**
   - LCP < 2.5s
   - FID/INP < 200ms
   - CLS < 0.1

### Estructura de directorios (Next.js app router)

```
src/
├── app/                        # Rutas (Next.js)
│   ├── layout.tsx
│   ├── page.tsx
│   └── refunds/
│       ├── page.tsx
│       └── [id]/page.tsx
├── features/                   # Features de negocio
│   └── refunds/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       └── index.ts
├── components/                 # UI kit
│   ├── Button/
│   ├── Input/
│   └── Modal/
├── hooks/                      # Hooks globales
├── lib/                        # Utils, apiClient, helpers
├── types/                      # Tipos compartidos
└── styles/                     # Global CSS, tokens
```

### Internacionalización (i18n)

Para proyectos con múltiples idiomas:

1. **Librería:** `next-intl`, `react-i18next`, `formatjs`.
2. **Claves semánticas:** `button.submit`, no `Enviar`.
3. **Pluralización y formato:** usar ICU MessageFormat.
4. **Fecha y número:** `Intl.DateTimeFormat`, `Intl.NumberFormat`.

### Observabilidad

1. **Error tracking:** Sentry, Rollbar o equivalente; `ErrorBoundary` envía al servicio.
2. **Web vitals:** recopilar LCP/FID/CLS en producción (`web-vitals` lib + endpoint propio o Vercel Analytics).
3. **User analytics:** eventos de negocio (quién clickeó, quién completó el flujo); sin PII.
4. **Logging estructurado:** evitar `console.log` en producción; usar logger propio con niveles.

## Referencias

- `lex-frontend-typing` — tipado estricto
- `lex-frontend-testing` — estrategia de pruebas
- `lex-frontend-accessibility` — WCAG obligatorio
- `lex-frontend-security` — XSS, CSP, secrets
- [React docs](https://react.dev)
- [Next.js App Router](https://nextjs.org/docs/app)
- [TanStack Query](https://tanstack.com/query)
- [Web Vitals](https://web.dev/vitals/)
