# Codex: Arquitetura Frontend

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Padrões arquiteturais para aplicações frontend modernas (React/Next.js como referência; adaptável a Vue/Angular/Svelte)

## Conteúdo

### Camadas de uma aplicação frontend

```
┌─────────────────────────────────────────────────┐
│  Pages / Routes                                 │  (Next.js app/, Vue router, Angular routes)
│  - Composição de features em uma página         │
├─────────────────────────────────────────────────┤
│  Features                                       │
│  - Blocos auto-contidos de funcionalidade       │
│  - (ex.: refund-form, transaction-list)         │
├─────────────────────────────────────────────────┤
│  Components (UI kit)                            │
│  - Primitivos reutilizáveis: Button, Input,     │
│    Modal, Table. Sem lógica de negócio.         │
├─────────────────────────────────────────────────┤
│  Hooks / Composables                            │
│  - Lógica reutilizável: useAuth, useQuery,      │
│    useForm. Sem UI.                             │
├─────────────────────────────────────────────────┤
│  Services / API clients                         │
│  - Camada de acesso à API HTTP                  │
│  - Tipos derivados do OAS                       │
├─────────────────────────────────────────────────┤
│  State (server + client)                        │
│  - Server state: React Query / SWR / TanStack   │
│  - Client state: Zustand / Jotai / Context      │
└─────────────────────────────────────────────────┘
```

### Princípios de composição de componentes

1. **Single Responsibility:** um componente faz uma coisa bem. Se o arquivo passa de 200 linhas ou tem mais de 3 responsabilidades visuais, dividir.
2. **Presentational vs Container:**
   - **Presentational:** recebe dados via props, não faz I/O. Fácil de testar, reutilizar.
   - **Container:** busca dados, combina hooks, passa para presentational.
   - Em React moderno com hooks, a separação é mais fluida, mas o princípio continua: manter a composição clara.
3. **Props mínimas e tipadas:** não passar objetos grandes quando 2-3 campos bastam.
4. **Composição sobre configuração:** `<Card><CardHeader/><CardBody/></Card>` é mais flexível que `<Card variant="big" showHeader />`.
5. **Sem efeitos colaterais em renderização:** `useEffect` para side effects; render puro para UI.

### Gestão de estado

**Regra fundamental:** separar **server state** de **client state**.

| Tipo | Exemplo | Ferramenta |
|---|---|---|
| **Server state** | Lista de refunds, perfil do usuário | **TanStack Query (React Query)**, SWR, RTK Query |
| **Client state global** | Tema, idioma, carrinho (pré-checkout) | **Zustand**, Jotai, Context API |
| **Form state** | Campos de formulário em edição | **react-hook-form**, Formik, VeeValidate |
| **URL state** | Filtros, paginação, modal aberto | **searchParams** (Next.js), `useSearchParams` |
| **Local state** | Estado efêmero de um componente | `useState`, `useReducer` |

**Antipadrões a evitar:**
- Redux para tudo — useState local é suficiente em 70% dos casos
- Context para estado que muda frequentemente — causa re-render em cascata
- Duplicar server state em client state — manter a query como fonte de verdade

### Camada de dados (HTTP)

1. **Cliente HTTP centralizado:** um `apiClient` configurado com baseURL, interceptors, auth.
2. **Tipos derivados do OAS:** usar `openapi-typescript` ou `orval` para gerar tipos a partir do spec (produzido por `warrior-daedalus`).
3. **Queries e mutations:**
   - `useQuery` para leitura; cache automático, background refetch.
   - `useMutation` para escrita; optimistic updates quando aplicável.
4. **Tratamento de erros:** `error boundary` para erros inesperados; `onError` das queries para erros esperados.

### Roteamento

1. **File-based (Next.js app/):** páginas definidas por estrutura de pastas.
2. **Layout shared:** headers, sidebars em `layout.tsx` para evitar duplicação.
3. **Loading e error states:** `loading.tsx`, `error.tsx` em Next.js app router.
4. **Code splitting automático:** cada rota em chunk separado; lazy load features não críticas.

### Estilização

Opções principais (escolher uma e manter consistente):

| Abordagem | Quando usar |
|---|---|
| **Tailwind CSS** | Prototipagem rápida; times grandes; design system consistente |
| **CSS Modules** | Encapsulamento por componente; sem runtime overhead |
| **CSS-in-JS (Emotion, Styled)** | Temas dinâmicos; compartilhamento de valores com JS |
| **Vanilla Extract** | Zero runtime; types em CSS |

**Regra transversal:** definir **design tokens** (cores, espaçamentos, tipografia) em um lugar único, referenciados em todos os componentes.

### Performance

1. **Code splitting:** React.lazy, dynamic import, route-based splits.
2. **Memoization:** `useMemo`/`useCallback` apenas quando profiling mostra ganho real.
3. **Virtualização:** listas grandes (>100 items visíveis) usam `react-window` ou TanStack Virtual.
4. **Imagens:** `next/image` (Next.js) ou equivalente para srcset, lazy load, WebP/AVIF.
5. **Prefetching:** `<Link prefetch>` para rotas prováveis.
6. **Core Web Vitals como métrica-alvo:**
   - LCP < 2.5s
   - FID/INP < 200ms
   - CLS < 0.1

### Estrutura de diretórios (Next.js app router)

```
src/
├── app/                        # Rotas (Next.js)
│   ├── layout.tsx
│   ├── page.tsx
│   └── refunds/
│       ├── page.tsx
│       └── [id]/page.tsx
├── features/                   # Features de negócio
│   └── refunds/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       └── index.ts
├── components/                 # UI kit
│   ├── Button/
│   ├── Input/
│   └── Modal/
├── hooks/                      # Hooks globais
├── lib/                        # Utils, apiClient, helpers
├── types/                      # Tipos compartilhados
└── styles/                     # Global CSS, tokens
```

### Internacionalização (i18n)

Para projetos com múltiplos idiomas:

1. **Biblioteca:** `next-intl`, `react-i18next`, `formatjs`.
2. **Chaves semânticas:** `button.submit`, não `Enviar`.
3. **Pluralização e formato:** usar ICU MessageFormat.
4. **Data e número:** `Intl.DateTimeFormat`, `Intl.NumberFormat`.

### Observabilidade

1. **Error tracking:** Sentry, Rollbar ou equivalente; `ErrorBoundary` envia para o serviço.
2. **Web vitals:** coletar LCP/FID/CLS em produção (`web-vitals` lib + endpoint próprio ou Vercel Analytics).
3. **User analytics:** eventos de negócio (quem clicou, quem completou fluxo); sem PII.
4. **Logging estruturado:** evitar `console.log` em produção; usar logger próprio com níveis.
