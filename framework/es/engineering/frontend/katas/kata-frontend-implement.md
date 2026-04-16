# Kata: Implementar Feature Frontend

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Implementación de feature frontend desde el requisito hasta el código probado, tipado y accesible

## Objetivo

Dada una feature frontend (componente, página, flujo de interacción), producir una implementación completa en TypeScript con pruebas comportamentales, accesibilidad, tipos estrictos y adherencia a los patrones arquitecturales del proyecto. Incluye componentes de UI, hooks/composables, integración con API, gestión de estado y pruebas.

## Cuándo Usar

- Cuando una feature frontend ha sido descrita (brief + requisitos) y necesita ser implementada
- Invocada por `warrior-hephaestus` directamente o vía delegación de `warrior-athena` en la Fase 4 del flujo Issue-Driven

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Descripción de la feature | Sí | Requisitos + criterios de aceptación (ACs numerados si viene del flujo Issue-Driven) |
| Contrato de API | No | OAS o tipos de request/response (ideal: producido por `warrior-daedalus`) |
| Diseño o wireframe | No | Figma, imágenes o descripción textual de UI |
| Stack detectado | Sí | Framework (React/Next/Vue/Angular), lenguaje (TS), herramientas (testing, styling) |

## Workflow

```
Progreso:
- [ ] 1. Clarificar requisitos y contratos
- [ ] 2. Consultar patrones del codebase
- [ ] 3. Planificar estructura (componentes, hooks, capas)
- [ ] 4. Implementar tipos y contratos
- [ ] 5. Implementar componentes con accesibilidad
- [ ] 6. Implementar integración de datos
- [ ] 7. Escribir pruebas comportamentales
- [ ] 8. Validar (lint, typecheck, test, a11y)
```

### Paso 1: Clarificar requisitos y contratos

1. Consultar `.ahrena/.directives` conforme a `lex-directives`.
2. Si los ACs están numerados (flujo Issue-Driven), mapear cada AC a un comportamiento verificable.
3. Preguntas al usuario en lote (hasta 5 por ronda):
   - Estados de carga, error y vacío: ¿cómo se comportan?
   - Validaciones de formulario: ¿client-only o con feedback del servidor?
   - ¿Comportamiento en mobile vs desktop?
   - ¿Autenticación necesaria para acceder?
   - ¿Feature flag o A/B test aplicable?

### Paso 2: Consultar patrones del codebase

1. Leer `codex-frontend-architecture` e identificar:
   - Dónde se ubican las features (`src/features/`, `app/`, etc.)
   - Dónde se ubica el UI kit (`src/components/`)
   - Qué librería de server state (TanStack Query, SWR, etc.)
   - Qué librería de forms (react-hook-form, Formik)
   - Qué enfoque de styling (Tailwind, CSS Modules, etc.)
2. Seguir las convenciones existentes antes de introducir nuevas.

### Paso 3: Planificar estructura

Para la feature, decidir:

1. **Rutas nuevas** (si aplica): path, layout, loading/error states.
2. **Componentes** a crear o modificar — lista con la responsabilidad de cada uno.
3. **Hooks/composables** a crear — lógica reutilizable.
4. **Integración con API** — qué endpoints serán consumidos.
5. **Estado** — server, client, URL, form.
6. **Pruebas** — qué comportamientos probar y en qué nivel (unit, componente, integración, E2E).

Presentar el plan al usuario antes de codificar features grandes (> 200 líneas).

### Paso 4: Implementar tipos y contratos

1. Si existe OAS, generar tipos vía `openapi-typescript` o validar con Zod.
2. Definir los tipos de las entidades y props de los componentes.
3. Definir los tipos de eventos personalizados (si los hay).
4. Aplicar `lex-frontend-typing`: strict, sin `any` sin justificación.

### Paso 5: Implementar componentes con accesibilidad

Para cada componente:

1. Usar HTML semántico (`<button>`, `<form>`, `<nav>`, etc.) — `lex-frontend-accessibility`.
2. Labels asociadas a inputs, `aria-*` cuando sea necesario.
3. Estados de foco visibles.
4. Probar la navegación por teclado durante el desarrollo.
5. Aplicar los design tokens existentes para espaciado, colores, tipografía.

### Paso 6: Implementar integración de datos

1. **Server state:** usar la librería del proyecto (TanStack Query, SWR, etc.) — cache, error, loading automáticos.
2. **Mutations:** incluir `onSuccess` para invalidar queries o actualizar el cache; optimistic update donde sea adecuado.
3. **Forms:** validar con Zod/Yup en el cliente; reusar el schema para los tipos.
4. **Seguridad:** nunca exponer secretos en el bundle (`lex-frontend-security`); sanitizar cualquier HTML dinámico.

### Paso 7: Escribir pruebas comportamentales

Para cada AC (o comportamiento, si no hay un flujo estructurado):

1. Escribir la prueba desde el punto de vista del usuario (`lex-frontend-testing`).
2. Usar queries accesibles (`getByRole`, `getByLabelText`).
3. Marcar cada prueba con el AC correspondiente (si el flujo es Issue-Driven):

```typescript
describe("Refund form", () => {
  it("creates refund on submit AC-1", async () => {
    render(<RefundForm paymentId="p123" />);
    await userEvent.type(screen.getByLabelText(/amount/i), "100");
    await userEvent.click(screen.getByRole("button", { name: /submit/i }));
    expect(await screen.findByText(/refund processing/i)).toBeInTheDocument();
  });
});
```

4. Cubrir: caso feliz, error de validación, error de API, estado de loading, estado vacío.
5. Agregar pruebas a11y automatizadas con `jest-axe` o `axe-core/playwright`.

### Paso 8: Validar

Ejecutar localmente:

1. `yarn typecheck` (o `tsc --noEmit`) — 0 errores.
2. `yarn lint` — incluyendo `eslint-plugin-jsx-a11y`.
3. `yarn test` — todas las pruebas pasan.
4. `yarn test:e2e` si hay E2E relevante.
5. Lighthouse manual en una página afectada (accesibilidad ≥ 95, performance ≥ 80).

Si está en el flujo Issue-Driven, el `kata-quality-gate` ejecutará estas verificaciones de manera sistemática en el Gate 2.

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Código de la feature | `.ts`, `.tsx`, `.css`, etc. | Conforme a la arquitectura del proyecto |
| Pruebas | `.test.ts`, `.test.tsx` | Junto a los componentes o en `__tests__/` |
| Tipos | Interfaces y schemas | En `types/` o junto a los componentes |
| Documentación del componente (si es reutilizable) | Storybook o JSDoc | Conforme al estándar del proyecto |

## Restricciones

- **Seguir los patrones existentes:** antes de introducir un nuevo pattern, verificar si no hay un equivalente ya usado en el codebase.
- **Sin romper accesibilidad:** ningún commit puede degradar la a11y (Lighthouse, axe deben permanecer en verde).
- **Sin `any` implícito:** `lex-frontend-typing` es mandatorio.
- **Pruebas de comportamiento, no de implementación:** `lex-frontend-testing`.
- **Commits pequeños:** separar estructura/esqueleto de lógica; forms de integración; pruebas de código de producción.

## Referencias

- `lex-frontend-typing`, `lex-frontend-testing`, `lex-frontend-accessibility`, `lex-frontend-security`
- `codex-frontend-architecture` — patrones de estructura y capas
- `warrior-hephaestus` — agente que ejecuta este kata
- `kata-api-design-oas` — contrato de API producido por Daedalus
