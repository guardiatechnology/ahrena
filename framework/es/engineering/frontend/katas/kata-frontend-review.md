# Kata: Revisar Código Frontend

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Revisión sistemática de código frontend por corrección, accesibilidad, tipos, pruebas, seguridad y performance

## Objetivo

Ejecutar la revisión de código frontend (típicamente en un PR o diff), verificando adherencia a las Lexis aplicables e identificando mejoras. Produce un reporte estructurado con hallazgos categorizados por severidad (bloqueante, recomendación, nota), aplicable como revisión humana o parte del `kata-quality-gate` del flujo Issue-Driven.

## Cuándo Usar

- Revisión de PR frontend antes del merge
- Revisión periódica de calidad en código existente
- Complemento al `kata-quality-gate` cuando el foco es frontend

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Diff a revisar | Sí | `git diff {base}..HEAD` o PR específico |
| Contexto | No | Issue, ACs, arquitectura esperada (viniendo de `.issues/{n}/` si aplica) |
| Alcance | No | Componentes específicos o revisión completa del diff |

## Workflow

```
Progreso:
- [ ] 1. Recolectar diff y contexto
- [ ] 2. Revisar tipado (lex-frontend-typing)
- [ ] 3. Revisar pruebas (lex-frontend-testing)
- [ ] 4. Revisar accesibilidad (lex-frontend-accessibility)
- [ ] 5. Revisar seguridad (lex-frontend-security)
- [ ] 6. Revisar arquitectura y composición
- [ ] 7. Revisar performance
- [ ] 8. Consolidar reporte por severidad
```

### Paso 1: Recolectar diff y contexto

1. Obtener el diff: `git diff {base}..HEAD`.
2. Listar los archivos tocados por tipo (`.tsx`, `.ts`, `.css`, pruebas, config).
3. Si hay ACs (flujo Issue-Driven), leer `.issues/{n}/02-requirements.md`.

### Paso 2: Revisar tipado

Contra `lex-frontend-typing`:

- [ ] ¿`any` explícito? ¿Justificado en comentario?
- [ ] ¿Props de componentes tipadas?
- [ ] ¿Hooks con estado tipado cuando no es inferible?
- [ ] ¿Contratos de API tipados (OAS o Zod)?
- [ ] ¿`unknown` usado donde `any` sería pereza?
- [ ] ¿`tsc --noEmit` pasa?

### Paso 3: Revisar pruebas

Contra `lex-frontend-testing`:

- [ ] ¿Cada componente con lógica o interacción tiene prueba?
- [ ] ¿Las pruebas usan `getByRole`/`getByLabelText` en vez de `getByTestId`?
- [ ] ¿Las pruebas verifican comportamiento, no implementación?
- [ ] ¿Mocks solo en las fronteras (API, Date, storage)?
- [ ] ¿Los snapshots son pequeños y revisados?
- [ ] ¿Caso feliz + error + loading + vacío cubiertos?
- [ ] Si el flujo es Issue-Driven: ¿cada prueba marca el AC-N correspondiente?

### Paso 4: Revisar accesibilidad

Contra `lex-frontend-accessibility`:

- [ ] ¿HTML semántico (sin `<div>` donde cabría `<button>`)?
- [ ] ¿Imágenes con `alt` apropiado?
- [ ] ¿Formularios con labels asociadas?
- [ ] ¿Funciona la navegación por teclado? (probar mentalmente o con Tab)
- [ ] ¿Foco visible?
- [ ] ¿Contraste adecuado (4.5:1 para texto normal)?
- [ ] ¿Modales con focus trap + `aria-modal`?
- [ ] ¿Contenido dinámico anunciado (`role="status"`, `aria-live`)?
- [ ] Correr `axe`/`jest-axe` en los componentes modificados.

### Paso 5: Revisar seguridad

Contra `lex-frontend-security`:

- [ ] ¿`dangerouslySetInnerHTML` / `innerHTML` sin sanitización?
- [ ] ¿Secretos en el bundle? (buscar por API keys, tokens en código `.ts`/`.tsx`)
- [ ] ¿Tokens en `localStorage` vs HttpOnly cookie?
- [ ] ¿Validación de input en dos niveles (cliente + servidor)?
- [ ] ¿`target="_blank"` con `rel="noopener noreferrer"`?
- [ ] ¿Dependencias auditadas (`yarn audit`)?

### Paso 6: Revisar arquitectura y composición

Contra `codex-frontend-architecture`:

- [ ] ¿Componentes con responsabilidad única?
- [ ] ¿Feature aislada en `features/` con barrel export?
- [ ] ¿Separación clara presentational/container?
- [ ] ¿Server state vía TanStack Query (o equivalente del proyecto), no `useState` + `useEffect`?
- [ ] ¿Sin duplicación obvia de lógica (hooks extraídos cuando sea pertinente)?
- [ ] ¿Sin `useEffect` haciendo data fetching manual cuando existe una query library?
- [ ] ¿Design tokens respetados (sin valores mágicos de color/espaciado)?

### Paso 7: Revisar performance

- [ ] ¿Listas grandes virtualizadas?
- [ ] ¿Imágenes con `next/image` o srcset equivalente?
- [ ] ¿Code splitting en las rutas?
- [ ] ¿`useMemo`/`useCallback` usado con justificación (no defensivamente)?
- [ ] ¿Bundle size razonable? (correr análisis si hubo cambio en deps)
- [ ] ¿Sin re-renders innecesarios (verificar vía React DevTools Profiler si hay sospecha)?

### Paso 8: Consolidar reporte por severidad

Estructurar los hallazgos:

```markdown
# Frontend Review — {PR o issue} #{n}

- **Fecha:** {YYYY-MM-DD}
- **Archivos revisados:** {n}
- **Hallazgos:** {B} bloqueantes, {R} recomendaciones, {N} notas

## Bloqueantes (impiden merge)

### F-1: {título}
- **Categoría:** {Typing | Testing | A11y | Security | Architecture | Performance}
- **Ubicación:** `src/features/refunds/RefundForm.tsx:42`
- **Problema:** {qué hay}
- **Recomendación:** {corrección propuesta con ejemplo de código}
- **Referencia:** `lex-frontend-{...}`

## Recomendaciones (mejoras)

### F-2: ...

## Notas (informacional)

### F-3: ...

## Resumen Positivo

{2-3 puntos bien ejecutados que valen destacar}
```

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Reporte de revisión | Markdown estructurado | Respuesta al usuario o `docs/reviews/` |
| Comentarios en PR | Comentarios línea a línea vía GitHub MCP | PR en GitHub (opcional) |

## Restricciones

- **Revisión ≠ reescritura:** este kata señala problemas; no modifica código directamente.
- **Severidad objetiva:** bloqueante = viola Lexis; recomendación = mejora de calidad; nota = observación.
- **Sin suposiciones:** cada hallazgo tiene referencia a la Lexis o Codex aplicable.
- **Tono constructivo:** señalar el problema con la solución sugerida, no solo criticar.

## Referencias

- `lex-frontend-typing`, `lex-frontend-testing`, `lex-frontend-accessibility`, `lex-frontend-security`
- `codex-frontend-architecture`
- `kata-quality-gate` — en el flujo Issue-Driven, integra los hallazgos
- `kata-mcp-github-read` — para revisar el diff en un PR remoto
