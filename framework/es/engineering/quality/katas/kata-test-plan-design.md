# Kata: Diseñar Plan de Pruebas

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Diseño de plan de pruebas para una feature — distribuye los ACs por los niveles correctos, define cobertura esperada, identifica riesgos y gaps

## Objetivo

Dada una feature con requisitos (ACs numerados) y arquitectura (componentes afectados), producir un **plan de pruebas estructurado** que mapea cada AC a los niveles apropiados (unit, integration, E2E), identifica escenarios de error y borde, y documenta gaps conocidos. El plan sirve como entrada para que Apollo/Hephaestus implementen pruebas con trazabilidad, y como input para que el Gate 2 valide cobertura.

## Cuándo Usar

- Fase 2.5 (opcional) del flujo Issue-Driven, cuando la feature es compleja lo suficiente para beneficiarse de un plan explícito antes de la implementación
- Invocada por `warrior-hera` directamente o delegada por `warrior-athena` en features tier-1
- También aplicable fuera del flujo Issue-Driven para auditar cobertura de feature existente

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-----------|
| Requisitos (ACs) | Sí | `.issues/{n}/02-requirements.md` o lista equivalente |
| Arquitectura | Sí | Lista de componentes afectados (fase 3 del flujo Issue-Driven) |
| Stack | Sí | Lenguajes, frameworks detectados |
| Criticidad | No | Tier (1/2/3/4); default 2 |

## Workflow

```
Progreso:
- [ ] 1. Mapear ACs a los niveles de prueba apropiados
- [ ] 2. Identificar escenarios más allá del caso feliz
- [ ] 3. Identificar fronteras y riesgos
- [ ] 4. Definir cobertura objetivo por componente
- [ ] 5. Listar herramientas y fixtures necesarias
- [ ] 6. Persistir en .issues/{n}/02b-test-plan.md
- [ ] 7. Actualizar checkpoint
```

### Paso 1: Mapear ACs a los niveles

Para cada AC:

1. Identificar **tipo de comportamiento**: ¿lógica pura? ¿persistencia? ¿UI? ¿integración externa?
2. Atribuir nivel primario conforme decision tree en `codex-test-strategy`:
   - Lógica pura → **Unit**
   - Persistencia / integración real → **Integration**
   - Contrato externo / flujo multi-endpoint → **E2E API**
   - Jornada de usuario crítica → **E2E UI**
3. Decidir si el AC también merece cobertura en nivel adyacente (ej.: AC del repositorio tiene unit del domain + integration del repo).

Producir tabla:

| AC | Comportamiento | Nivel primario | Nivel adyacente | Justificación |
|---|---|---|---|---|
| AC-1 | Crear refund vía POST /v1/refunds | Integration | E2E API | Cruza service + repository + DB real |
| AC-2 | Idempotencia vía Idempotency-Key | Integration | Unit (hash key) | — |
| AC-3 | Refund después de 30 días retorna 422 | Unit (domain) | Integration | Regla pura de negocio + integración prueba HTTP |

### Paso 2: Escenarios más allá del caso feliz

Para cada AC, **obligatorio** identificar:

- **Errores conocidos**: inputs inválidos, precondiciones no cumplidas
- **Bordes**: límites (amount = 0, amount = máximo), concurrencia (doble submit)
- **Idempotencia / replay**: ¿repetir la operación produce el mismo resultado?
- **Fallos de dependencia**: BD fuera, API externa 500, timeout

Los escenarios extras se convierten en **pruebas adicionales** (no duplican ACs, los extienden).

### Paso 3: Fronteras y riesgos

Listar explícitamente:

- **Fronteras externas** que serán mockeadas: ¿cuáles? ¿cómo? ¿contratos actualizados?
- **Datos sensibles** en fixtures: enmascarar/redact; nunca datos reales de clientes.
- **Costos reales** de E2E (ej.: Stripe sandbox genera token real → limpieza necesaria).
- **Tiempo de ejecución estimado**: sumar por nivel; si pasa el budget (`codex-test-strategy`), escalar a humano.

### Paso 4: Cobertura objetivo

Por criticidad:

| Tier | Cobertura mínima | Mutation score | Comentario |
|---|---:|---:|---|
| Tier 1 (ingresos, seguridad crítica) | 90% | >70% | Inversión justificada |
| Tier 2 (importante) | 80% | — | Default |
| Tier 3 | 70% | — | Cobertura básica |
| Tier 4 (interno) | 60% | — | Solo camino feliz + errores obvios |

Ajustar `quality.coverage_threshold` en `.ahrena/.directives` si es diferente del default 80%.

### Paso 5: Herramientas y fixtures

- **Herramientas por nivel**: conforme `codex-test-strategy`
- **Fixtures reutilizables**: identificar factories nuevas necesarias
- **Contenedores**: listar imágenes Docker (Postgres, Redis, LocalStack para AWS)
- **Datos de prueba**: datasets necesarios; dónde quedan (fixtures/, seeds/)

### Paso 6: Persistir el plan

Estructura en `.issues/{n}/02b-test-plan.md`:

```markdown
# Plan de Pruebas — Issue #{n}: {título}

- **Referencias:** [Requisitos](./02-requirements.md) · [Arquitectura](./03-architecture.md)
- **Criticidad (tier):** 2
- **Cobertura objetivo:** 80%

## Mapeo AC → Niveles

| AC | Nivel primario | Nivel adyacente | Justificación |
|---|---|---|---|

## Escenarios adicionales

### AC-1
- Errores: amount negativo, payment_id inexistente, pago ya reembolsado
- Bordes: refund igual al valor original; refund 1 centavo menos
- Idempotencia: 2x mismo Idempotency-Key → 1 refund
- Fallos: BD timeout, evento no publica

## Fronteras mockeadas

- Stripe: sandbox cuando esté disponible, contract test vs Pact
- SNS: real en staging; moto/localstack en integration

## Recursos necesarios

- Contenedor: `postgres:16`
- Fixtures nuevas: `RefundFactory`, `PaymentWithCaptureFactory`
- Dataset: ninguno nuevo (reusa fixtures globales)

## Riesgos y gaps

- E2E UI no cubierto en esta iteración (sin UI de refund para cliente final aún)
- Mutation testing: correr en ciclo offline mensual (no en el CI de cada PR)
```

### Paso 7: Actualizar checkpoint

Agregar entrada en `.ahrena/workflow/issue-{n}/checkpoint.md`:

```yaml
test_plan:
  artifact: .issues/{n}/02b-test-plan.md
  total_acs_mapped: 5
  coverage_target: 80
  tier: 2
```

## Salidas

| Salida | Formato | Destino |
|-------|---------|---------|
| Plan de pruebas estructurado | Markdown | `.issues/{n}/02b-test-plan.md` |
| Mapeo AC → niveles | Tabla en el plan | — |
| Lista de fixtures/contenedores | Sección en el plan | — |

## Restricciones

- **No escribe pruebas**: esta kata planea; la escritura real es de Apollo/Hephaestus.
- **Plan vinculante para Gate 2**: si el plan define Integration para AC-1, el Gate 2 verifica que exista integration test para AC-1.
- **Tier declarado explícitamente**: si se omite, el Gate 2 asume tier 2 (80% cobertura).
- **Destino fijo**: `.issues/{n}/02b-test-plan.md` (siguiendo convención de `lex-issue-driven`).

## Referencias

- `lex-test-pyramid`, `lex-test-isolation`
- `codex-test-strategy`
- `warrior-hera`
- `kata-quality-gate` — consume el plan en el Gate 2
- `lex-issue-driven`
