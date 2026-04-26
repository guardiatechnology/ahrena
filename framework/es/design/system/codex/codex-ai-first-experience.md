# Codex: AI-First Experience — Patrón Conversación + Workspace

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** UX agéntica de la plataforma y de la app de Guardia

## Visión general

La experiencia de Guardia es **agéntica por defecto**. Isac es el centro de la interacción — no un asistente acoplado a un SaaS clásico. El usuario describe el resultado; el agente planea, ejecuta y rinde cuentas. La UI existe para que esto sea legible, controlable y auditable. Este Codex consolida principios, patrón de layout, reglas de uso, ejemplos e implicaciones para el Design System.

## Contexto

- **Dominio:** experiencia del usuario en producto principal (plataforma y app), con presencia permanente de Isac.
- **Público objetivo:** diseñadores, frontend, mobile, producto, agentes de IA que producen UI (warrior-hephaestus, warrior-iris).
- **Actualización:** cuando la página *AI-First Experience* en Notion sea revisada.

## Contenido

### Principios

1. **Conversación como interfaz primaria.** La superficie principal es el diálogo con Isac. Las pantallas, paneles y visualizaciones nacen como respuesta del agente o como contexto invocado por la conversación — no como destino de navegación.
2. **Intención sobre funcionalidad.** El usuario expresa el resultado deseado (conciliar, investigar, aprobar). Isac decide herramientas, fuentes y pasos. La UI no expone funcionalidades aisladas esperando que el usuario las combine.
3. **Transparencia del razonamiento.** Toda ejecución es observable en tiempo real (plan, pasos, fuentes consultadas, decisiones tomadas). Nada ocurre en caja negra.
4. **Control graduado.** El usuario puede pausar, intervenir, corregir o tomar cualquier etapa. La autonomía de Isac es un espectro ajustable, no un interruptor.
5. **Artefactos bajo demanda.** Tablas, gráficos, reportes y dashboards se generan cuando sirven a la decisión en curso. Ningún artefacto vive como menú permanente esperando que el usuario lo abra.
6. **Auditabilidad nativa.** Cada acción genera rastro versionado (input, contexto, decisión, resultado). La interfaz da acceso directo a ese historial.
7. **Memoria estructurada.** El contexto de la operación (clientes, conciliaciones en curso, reglas, preferencias) se externaliza y es recuperado por el agente, no apilado en estados de pantalla.

### Patrón de layout

Conversación + workspace en vivo, alineado con referencias de mercado (Claude de Anthropic y Manus AI de Meta).

| Región | Función | Contenido |
|--------|---------|-----------|
| Izquierda (o superior en mobile) | Conversación con Isac | Entrada principal, historial de la sesión, plan de ejecución, status |
| Derecha (o inferior en mobile) | Workspace dinámico | Renderiza lo que Isac está consultando o produciendo (tabla de transacciones, vista de conciliación, documento, panel, fuente externa) |

El workspace es **reactivo al diálogo**. Cuando la conversación cambia de contexto, el workspace acompaña. El usuario no navega para encontrar una pantalla.

### Reglas de uso

#### Hacer

- Partir siempre de la intención del usuario y dejar que Isac descomponga en pasos.
- Mostrar el plan antes de la ejecución cuando la tarea tenga impacto relevante (escritura, aprobación, envío externo).
- Mostrar fuentes consultadas y datos usados en cada decisión.
- Permitir editar el plan, bloquear pasos o aprobar etapas sensibles antes de la ejecución.
- Generar artefactos como resultado del trabajo agéntico, con link directo al contexto que los originó.
- Preservar memoria de largo plazo fuera de la pantalla (archivos, estado persistido, preferencias), invocada cuando sea relevante.
- Tratar acciones irreversibles (envío de mensaje, asiento contable, liberación de valor) como puntos de confirmación explícita.

#### No hacer

- Construir menús laterales con funcionalidades apiladas (Conciliación, Reportes, Configuración) como arquitectura principal. Las funcionalidades son capacidades de Isac, no destinos.
- Abrir modales o wizards que obliguen al usuario a llenar campos antes de conversar.
- Esconder lo que el agente está haciendo (loaders genéricos o "procesando..." sin detalle).
- Duplicar el mismo dato en múltiples pantallas estáticas. Si es relevante, Isac lo trae cuando sea necesario.
- Crear dashboards permanentes que el usuario tenga que monitorear. Los dashboards se materializan bajo demanda o se disparan por reglas.
- Delegar en el usuario la orquestación entre herramientas. Si dos capacidades necesitan combinarse, es Isac quien combina.
- Tratar la autonomía como binario (manual o automático). Debe haber niveles configurables por tipo de tarea y por perfil de usuario.

### Ejemplos

#### Correcto — conciliación

Usuario: *"Concilia las liquidaciones de Cielo de ayer y avísame qué quedó abierto."*

- Isac muestra el plan: buscar extracto bancario → buscar archivo EDI de Cielo → aplicar reglas de matching → listar divergencias.
- El workspace muestra, en tiempo real, cada fuente siendo consultada y las líneas siendo conciliadas.
- El resultado aparece como artefacto (tabla de divergencias) con justificación por línea.
- El usuario puede hacer click en cualquier divergencia, preguntar por qué no coincidió, e Isac responde con rastro completo.

#### Correcto — investigación

Usuario: *"Quiero entender por qué el flujo de Pix del cliente X tiene ruido."*

- Isac propone investigación (períodos, contrapartes, patrones de valor).
- El workspace renderiza los cortes solicitados de forma progresiva.
- Ningún reporte preconstruido se abre. Todo se genera para esa pregunta específica.

#### Incorrecto — sidebar de módulos

Pantalla inicial con sidebar (Conciliación, Reportes, Reglas, Integraciones) y el chat de Isac como botón flotante en la esquina.
**Motivo:** invierte la jerarquía. Isac se vuelve accesorio de un SaaS clásico. El usuario vuelve a operar módulos en lugar de delegar intenciones.

#### Incorrecto — acción invisible

Isac ejecuta una conciliación en segundo plano y devuelve solo "Listo. 127 transacciones conciliadas."
**Motivo:** rompe transparencia y auditabilidad. El usuario no tiene cómo validar ni aprender con la operación.

#### Incorrecto — formulario extenso

Formulario con 12 campos obligatorios para crear una regla de conciliación.
**Motivo:** el usuario debería describir la regla en lenguaje natural a Isac, que estructura, valida y confirma antes de persistir.

### Implicaciones para el Design System

- **Componentes prioritarios:** burbujas de conversación, bloques de plan de ejecución, trace de pasos, cards de fuente consultada, artefactos renderizables inline (tabla, gráfico, documento) y controles de aprobación/intervención. Estos viven en `@guardia/design-system` en la familia "Agéntico" (`ChatPanel`, `Workspace`, `PlanTrace`, `SourceCard`, `ApprovalGate`).
- **Navegación:** mínima. Historial de sesiones, memoria del usuario y configuración. Ningún árbol de funcionalidades.
- **Estados de loading:** sustituidos por *streaming* de razonamiento y progreso del plan.
- **Tokens y patrones visuales:** siguen el Brand Kit; Figma traduce en componentes con paridad entre diseño y código.

### Referencias externas

Claude (Anthropic) y Manus AI (Meta) como benchmarks del patrón agéntico. La directriz se apoya en el consenso emergente de que el layout dominante para agentes combina **conversación persistente + workspace en vivo**, priorizando transparencia sobre pulido visual.

### Gobernanza

Cualquier excepción (pantalla con arquitectura tradicional, funcionalidad sin entrada agéntica) exige propuesta formal en Notion, con justificación, y aprobación del CEO o responsable designado de Brand. Las excepciones alimentan la evolución del sistema; no se vuelven regla por omisión.

## Referencias

- Notion — Branding / Design System / AI-First Experience
- [lex-ai-first-experience](../lexis/lex-ai-first-experience.md)
- [codex-design-system](codex-design-system.md), [codex-design-system-components](codex-design-system-components.md)
