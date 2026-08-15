# Lexis: Testes Comportamentais em Frontend

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Estratégia de testes para aplicações frontend (unitários, componentes, integração, E2E)

## Lei

> **Todo componente com lógica de negócio ou interação do usuário DEVE ter testes comportamentais escritos do ponto de vista do usuário. Testes DEVEM usar queries acessíveis (`getByRole`, `getByLabelText`) em vez de seletores estruturais (`getByTestId` apenas como último recurso). Mocks DEVEM ser limitados às fronteiras externas: API, Date, timers, storage, APIs do navegador.**

## Regras

### 1. Testar comportamento, não implementação

O agente **DEVE**:

1. Escrever testes que simulam ações do usuário (click, type, submit, navigate).
2. Asserir no resultado observável: o que muda na tela, que requisição é feita, que mensagem aparece.
3. Evitar asserções sobre estado interno de componentes (`state.loading`), chamadas de método interno ou implementação de hooks.

```typescript
// ❌ Testa implementação
expect(component.state.loading).toBe(true);

// ✅ Testa comportamento
expect(screen.getByRole("status", { name: /loading/i })).toBeInTheDocument();
```

### 2. Preferir queries acessíveis

Ordem de preferência (conforme Testing Library):

1. `getByRole` com `name` — prioritário; reflete como leitores de tela veem a UI
2. `getByLabelText` — para inputs com labels
3. `getByPlaceholderText`, `getByText` — quando não há role semântico
4. `getByDisplayValue`, `getByAltText`, `getByTitle`
5. `getByTestId` — **último recurso**, quando nenhuma query semântica funciona

Usar `getByTestId` sem justificativa indica UI não acessível (ver `lex-frontend-accessibility`).

### 3. Mocks apenas nas fronteiras

O agente **PODE** mockar:

- Chamadas HTTP (MSW, `fetch`, axios) — fronteira com API
- `Date.now()`, `setTimeout` — fronteira com timing
- `localStorage`, `sessionStorage`, `indexedDB` — fronteira com persistência
- `navigator.clipboard`, `navigator.geolocation` — fronteira com APIs do navegador
- `crypto.randomUUID` — quando determinismo é necessário

O agente **NÃO DEVE**:

- Mockar hooks internos da aplicação (`useAuth`, `useCart`) — renderizar com provider real
- Mockar componentes filhos — testar a árvore real
- Mockar funções de utility internas — usá-las com dados de teste

### 4. Cobertura por tipo de teste

| Tipo | Quando usar | Coverage-alvo |
|---|---|---|
| Unitário (puro) | Funções puras, utils, formatters | 100% |
| Componente | Componentes com lógica ou interação | Cobertura dos estados visíveis + fluxos de usuário |
| Integração | Múltiplos componentes em conjunto (form + submit, lista + filtro) | Fluxos principais |
| E2E (Playwright, Cypress) | Jornadas críticas (login, checkout, onboarding) | 3-7 jornadas principais |

### 5. Sem snapshots sem revisão

Snapshot tests (`toMatchSnapshot`) **DEVEM**:

- Ser revisados em cada mudança — o diff do snapshot precisa ser lido e aprovado
- Ser pequenos e focados (não snapshot da página inteira)
- Ter mensagem explicando por que o snapshot existe

Snapshots grandes e aceitos cegamente têm valor zero.

## Validação Automatizada

- **Ferramenta:** Jest, Vitest, Testing Library; E2E com Playwright ou Cypress
- **Momento:** local no dev (watch mode), CI no PR, `kata-quality-gate` Check 4 em `engineering/workflow`
- **Métrica:** testes passam; cobertura conforme `quality.coverage_threshold` em `.ahrena/.directives`
