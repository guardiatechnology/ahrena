# Lexis: Pruebas Comportamentales en Frontend

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Estrategia de pruebas para aplicaciones frontend (unitarias, de componentes, integración, E2E)

## Propósito

Las pruebas de frontend tienen un propósito específico: garantizar que la UI **se comporta** como el usuario espera, en todos los flujos relevantes. Las pruebas que verifican detalles de implementación (estado interno, snapshots sin revisión, llamadas a métodos) dan falsa seguridad y se rompen en cada refactor. Las pruebas que verifican comportamiento (lo que el usuario ve y puede hacer) sobreviven a los refactors y capturan regresiones reales.

Esta Lexis existe para garantizar que **todo componente con lógica de negocio o interacción tenga pruebas**, que **las pruebas sean comportamentales (user-centric)** y que **los mocks se usen únicamente en las fronteras externas** (API, Date, crypto, storage).

## Ley

> **Todo componente con lógica de negocio o interacción del usuario DEBE tener pruebas comportamentales escritas desde el punto de vista del usuario. Las pruebas DEBEN usar queries accesibles (`getByRole`, `getByLabelText`) en lugar de selectores estructurales (`getByTestId` solo como último recurso). Los mocks DEBEN limitarse a las fronteras externas: API, Date, timers, storage, APIs del navegador.**

## Reglas

### 1. Probar comportamiento, no implementación

El agente **DEBE**:

1. Escribir pruebas que simulen acciones del usuario (click, type, submit, navigate).
2. Afirmar sobre el resultado observable: qué cambia en pantalla, qué request se realiza, qué mensaje aparece.
3. Evitar aserciones sobre estado interno de componentes (`state.loading`), llamadas a métodos internos o implementación de hooks.

```typescript
// ❌ Prueba implementación
expect(component.state.loading).toBe(true);

// ✅ Prueba comportamiento
expect(screen.getByRole("status", { name: /loading/i })).toBeInTheDocument();
```

### 2. Preferir queries accesibles

Orden de preferencia (según Testing Library):

1. `getByRole` con `name` — prioritario; refleja cómo los lectores de pantalla ven la UI
2. `getByLabelText` — para inputs con labels
3. `getByPlaceholderText`, `getByText` — cuando no hay rol semántico
4. `getByDisplayValue`, `getByAltText`, `getByTitle`
5. `getByTestId` — **último recurso**, cuando ninguna query semántica funciona

Usar `getByTestId` sin justificación indica una UI no accesible (ver `lex-frontend-accessibility`).

### 3. Mocks solo en las fronteras

El agente **PUEDE** mockear:

- Llamadas HTTP (MSW, `fetch`, axios) — frontera con la API
- `Date.now()`, `setTimeout` — frontera con el timing
- `localStorage`, `sessionStorage`, `indexedDB` — frontera con la persistencia
- `navigator.clipboard`, `navigator.geolocation` — frontera con APIs del navegador
- `crypto.randomUUID` — cuando se requiere determinismo

El agente **NO DEBE**:

- Mockear hooks internos de la aplicación (`useAuth`, `useCart`) — renderizar con el provider real
- Mockear componentes hijos — probar el árbol real
- Mockear funciones de utilidad internas — usarlas con datos de prueba

### 4. Cobertura por tipo de prueba

| Tipo | Cuándo usar | Coverage objetivo |
|---|---|---|
| Unitaria (pura) | Funciones puras, utils, formatters | 100% |
| De componente | Componentes con lógica o interacción | Cobertura de los estados visibles + flujos de usuario |
| Integración | Múltiples componentes en conjunto (form + submit, lista + filtro) | Flujos principales |
| E2E (Playwright, Cypress) | Jornadas críticas (login, checkout, onboarding) | 3-7 jornadas principales |

### 5. Sin snapshots sin revisión

Las snapshot tests (`toMatchSnapshot`) **DEBEN**:

- Ser revisados en cada cambio — el diff del snapshot necesita ser leído y aprobado
- Ser pequeños y enfocados (no hacer snapshot de la página completa)
- Tener un mensaje explicando por qué existe el snapshot

Los snapshots grandes aceptados ciegamente tienen valor cero.

## Alcance

- **Aplica a:** todo el código frontend con lógica de negocio o interacción (componentes, hooks, stores)
- **Agentes vinculados:** `warrior-hephaestus`
- **Excepciones:** los componentes puramente decorativos (ej.: `<Divider />`, iconos) pueden no exigir prueba — documentar la decisión

## Consecuencias de Violación

1. **Pruebas frágiles:** las aserciones en implementación se rompen en cada refactor sin detectar regresión real
2. **Falsa seguridad:** coverage alto con pruebas de implementación no previene bugs de usuario
3. **Lentitud en la evolución:** cada cambio de UI requiere reescribir pruebas
4. **Remediación:** reescribir pruebas en estilo user-centric; preferir queries semánticas; reducir los mocks internos

## Validación Automatizada

- **Herramienta:** Jest, Vitest, Testing Library; E2E con Playwright o Cypress
- **Momento:** local en desarrollo (watch mode), CI en el PR, `kata-quality-gate` Check 4 en `engineering/workflow`
- **Métrica:** las pruebas pasan; cobertura conforme a `quality.coverage_threshold` en `.ahrena/.directives`

## Referencias

- `codex-frontend-architecture` — dónde probar cada capa
- `lex-frontend-accessibility` — las queries accesibles exigen una UI accesible
- [Testing Library — Query Priority](https://testing-library.com/docs/queries/about/#priority)
- [Kent C. Dodds — Testing Implementation Details](https://kentcdodds.com/blog/testing-implementation-details)
