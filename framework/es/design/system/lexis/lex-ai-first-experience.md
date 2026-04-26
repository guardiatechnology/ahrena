# Lexis: Experiencia AI-First por Defecto

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Plataforma y app de Guardia (interfaces orientadas al usuario final)

## Propósito

Sostener el posicionamiento de **contabilidad agéntica**. El usuario describe el resultado; Isac planea, ejecuta y rinde cuentas. Recrear una arquitectura clásica de SaaS (sidebar de módulos, formularios estáticos, dashboards permanentes, chat como flotante accesorio) invierte la jerarquía agéntica y rompe el producto.

## Ley

> **Toda interfaz usada por humanos en la plataforma y en la app de Guardia DEBE adoptar el patrón AI-First: conversación con Isac como superficie primaria, workspace en vivo reactivo al diálogo, transparencia del razonamiento en tiempo real (plan, fuentes, decisiones), control graduado (pausar, intervenir, aprobar) y auditabilidad nativa. Está PROHIBIDO construir arquitectura principal con menús laterales de funcionalidades, modales bloqueantes pre-conversación, dashboards permanentes para que el usuario monitoree o esconder lo que el agente está haciendo detrás de loaders genéricos.**

## Alcance

- **Aplica a:** plataforma web, app móvil, pantallas internas con interacción humana significativa.
- **Agentes vinculados:** diseñadores de producto, frontend, mobile, agentes de IA que producen código de UI (warrior-hephaestus, warrior-iris).
- **Excepciones:** vistas puramente operativas sin usuario (p. ej., pantallas de superusuario/admin de bajo volumen), correos transaccionales y páginas estáticas de marketing. Toda excepción en producto principal exige propuesta en Notion, con justificación y aprobación del CEO o responsable de Brand.

## Consecuencias de Violación

1. **Posicionamiento:** la marca de "contabilidad agéntica" pierde sustento; el producto se vuelve "otro SaaS más".
2. **Auditabilidad:** acciones del agente sin rastro visible impiden al usuario validar y aprender.
3. **Remediación:** rehacer la arquitectura de la pantalla con conversación + workspace; mover funcionalidades a capacidades invocadas por la conversación; añadir plan, fuentes y controles antes de retomar el release.

## Ejemplos

### Correcto

Pantalla inicial = chat con Isac en primer plano; el workspace renderiza, en tiempo real, las fuentes consultadas y los artefactos (tablas, gráficos, documentos) como respuesta de la conversación; las acciones irreversibles (envío, baja contable, liberación de valor) son puntos de confirmación explícita; el usuario puede pausar, editar el plan o aprobar pasos sensibles.

### Incorrecto

Pantalla inicial con sidebar (Conciliación, Reportes, Reglas, Integraciones) y el chat de Isac como botón flotante en la esquina; formulario con 12 campos para crear una regla en lugar de descripción en lenguaje natural; loaders genéricos sin detalle de plan o fuentes; respuesta final reducida a "Listo. 127 transacciones conciliadas." sin rastro.

## Validación Automatizada

- **Herramienta:** revisión de diseño (warrior-hephaestus + revisor humano de Brand) con checklist agéntico; pruebas E2E confirmando que toda jornada crítica parte de la conversación; auditoría periódica del árbol de navegación.
- **Momento:** revisión de diseño (pre-implementación), revisión de PR de UI, auditoría trimestral de producto.
- **Métrica:** 0 pantallas principales con sidebar de funcionalidades como arquitectura primaria; 100% de las acciones irreversibles con confirmación explícita; rastro completo de plan/fuentes en 100% de las ejecuciones de Isac visibles para el usuario.

## Referencias

- [codex-ai-first-experience](../codex/codex-ai-first-experience.md)
- [codex-design-system](../codex/codex-design-system.md)
- Notion — Design System / AI-First Experience
