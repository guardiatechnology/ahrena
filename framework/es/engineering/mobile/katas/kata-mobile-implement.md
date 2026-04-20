# Kata: Implementar Feature Mobile

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Implementación de feature mobile en iOS y Android (paridad), con offline-first, accesibilidad, pruebas y observabilidad

## Objetivo

Dada feature con requisitos (ACs numerados) y diseño arquitectural, producir implementación mobile completa en iOS y Android (o single codebase RN/Flutter) con: paridad funcional, offline-first (caché + queue), accesibilidad, pruebas en tres niveles (unit, integration, E2E), observabilidad (crash + analytics + performance), y release preparada para TestFlight + Play Console Internal Track.

## Cuándo Usar

- Feature mobile nueva o evolución significativa
- Invocada por `warrior-iris` directamente o vía delegación de `warrior-athena` en la Fase 4 cuando el target incluye mobile

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-----------|
| Descripción + ACs | Sí | Requisitos funcionales numerados |
| Contrato de API | No | OAS del backend (producido por Daedalus) |
| Design | No | Figma, wireframes, mocks |
| Stack objetivo | Sí | React Native / Flutter / Native / Mixed |

## Workflow

```
Progreso:
- [ ] 1. Clarificar requisitos (incluye comportamiento offline)
- [ ] 2. Consultar patrones del codebase y design system
- [ ] 3. Definir estrategia offline por feature
- [ ] 4. Implementar capas (service, hook, screen, component)
- [ ] 5. Cubrir accesibilidad (VoiceOver + TalkBack)
- [ ] 6. Escribir pruebas (unit + integration + E2E)
- [ ] 7. Agregar telemetría (crash, analytics, performance)
- [ ] 8. Build y smoke test en iOS + Android
- [ ] 9. Preparar release notes y checklist de paridad
```

### Paso 1: Clarificar requisitos

Preguntas en lote (hasta 5 por ronda):

1. **Offline**: ¿cuál comportamiento en flight mode? ¿Caché permitido?
2. **Paridad**: ¿release iOS y Android simultáneo? (asumir sí, las desviaciones necesitan ADR)
3. **Autenticación**: ¿la feature exige user logado? ¿biometría?
4. **Push notifications**: ¿la feature envía? ¿recibe?
5. **Deep link**: ¿la feature tiene URL compartible?

### Paso 2: Consultar codebase y design system

- Identificar patrón de estructura (`features/` vs. folders por pantalla).
- Usar UI kit existente (no inventar `<Button>` nuevo).
- Respetar tokens de design (colores, espaciamiento, tipografía).

### Paso 3: Estrategia offline

Para cada acción:

| Acción | Comportamiento |
|---|---|
| Lectura de datos del servidor | Caché con TTL; servir caché al abrir; refetch en background |
| Creación/edición | Optimista + queue local + sync |
| Acción destructiva sin red | Poner en cola pero dejar explícito al usuario |

Documentar decisión por pantalla o feature.

### Paso 4: Implementar capas

Siguiendo `codex-mobile-architecture`:

1. **Service** (API client + local storage): contratos tipados, caché, queue.
2. **Hook / ViewModel**: lógica de estado, llamadas al service.
3. **Screen**: composición de components; lifecycle; navegación.
4. **Components**: reutilizables, sin lógica de negocio.

Incremental: comenzar por el service (testable), después hook, después UI.

### Paso 5: Accesibilidad

Para cada control:

- **Label** (VoiceOver + TalkBack anuncian).
- **Role** correcto (button, link, heading).
- **State** expuesto (disabled, selected, expanded).
- **Hints** cuando la acción no es obvia.
- **Orden de foco** lógico.

Probar con lector de pantalla real antes de considerar listo.

### Paso 6: Pruebas

Conforme `codex-mobile-architecture`:

- **Unit**: hooks puros, utilities, reducers.
- **Component**: renderización, interacción básica.
- **Integration**: flow completo con mock de API (MSW o fixture).
- **E2E**: 1-2 jornadas críticas de la feature (Detox, Maestro, XCUITest).

Cada prueba marca AC correspondiente (`AC-N` convención).

### Paso 7: Telemetría

- **Crash**: ¿la feature involucra código nuevo que puede crashear? — ya cubierto por el SDK (Crashlytics/Sentry).
- **Analytics**: eventos de éxito/fallo de acciones clave; schema unificado iOS + Android.
- **Performance**: trace en llamadas de red y operaciones pesadas.
- **Logs**: sin PII, estructurados.

### Paso 8: Build + smoke test

- Build release en iOS (Xcode, `.ipa`) y Android (`.aab`).
- Instalar en device real (al menos uno de cada platform).
- Smoke test: caso feliz + escenario offline + accesibilidad rápida.
- Screenshots para release notes.

### Paso 9: Release notes + checklist paridad

- Notes por plataforma en el lenguaje de la app (pt-BR).
- Checklist (`lex-mobile-platform-parity`):
  - [ ] iOS build sometido a TestFlight
  - [ ] Android build sometido a Play Console Internal
  - [ ] Feature comparada lado a lado; comportamiento idéntico
  - [ ] Analytics events presentes en ambos
  - [ ] Deep link probado en ambos (si aplica)

## Salidas

| Salida | Formato | Destino |
|-------|---------|---------|
| Código feature | archivos conforme stack | `src/features/{feature}/` |
| Pruebas | conforme stack | al lado o en `__tests__/` |
| Builds release | `.ipa` + `.aab` | TestFlight + Play Console Internal |
| Release notes | Markdown | `docs/releases/vX.Y.Z.md` |
| Checklist paridad | Markdown | En el PR |

## Restricciones

- **Paridad obligatoria**: ship en ambas plataformas en la misma release o ADR justificando.
- **Offline-first**: toda feature tiene comportamiento definido en 3 estados de red.
- **La accesibilidad no es opcional**: VoiceOver + TalkBack funcionan antes del ship.
- **Las pruebas cubren ACs**: trazabilidad `AC-N`.

## Referencias

- `lex-mobile-platform-parity`, `lex-mobile-offline-first`
- `codex-mobile-architecture`
- `lex-frontend-accessibility` — principios de a11y transversales
- `warrior-iris`
