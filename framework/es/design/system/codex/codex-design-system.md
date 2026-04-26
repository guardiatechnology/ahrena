# Codex: Design System de Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Capa de ejecución del Brand Kit en cualquier interfaz o material

## Visión general

El Design System es la capa de ejecución del Brand Kit. Mientras el Brand Kit responde *qué* es la marca, el Design System responde *cómo* la marca se materializa en cada punto de contacto. Este Codex consolida principios, alcance, gobernanza, fuentes de referencia y stack de implementación. Es la puerta de entrada antes de construir pantallas, materiales, dashboards o piezas.

## Contexto

- **Dominio:** gobernanza y ejecución visual de la marca en producto, sitio, app y canales digitales.
- **Público objetivo:** diseñadores, frontend, mobile, agentes de IA que producen UI (warrior-hephaestus, warrior-iris).
- **Actualización:** cuando la página *Design System* en Notion sea revisada o haya cambios en stack/gobernanza.

## Contenido

### Relación con el Brand Kit

| Brand Kit | Design System |
|-----------|---------------|
| Logomarca y Logotipos | Cómo aparecen los logos en interfaces, materiales y firmas |
| Colores | Tokens aplicados en componentes, estados y categorías de datos |
| Tipografía | Escalas jerárquicas en botones, cards, tablas y dashboards |
| Voz de marca | Microcopy, etiquetas, mensajes de error y confirmación |
| Fotografía | Tratamiento de imágenes en banners, cards y materiales promocionales |

La coherencia entre identidad y ejecución es lo que hace a la marca **reconocible**, no solo bonita.

### Alcance

| Área | Contenido |
|------|-----------|
| AI-First Experience | Directriz estructural de UX agéntica: conversación primaria, workspace en vivo, transparencia, control graduado |
| Componentes | Patrones reutilizables (botones, cards, alertas, formularios, badges, bloques de contenido) |
| Elementos gráficos | Texturas, patrones, formas auxiliares, recursos decorativos |
| Íconos | Biblioteca de símbolos para acciones, navegación, estados, categorías |
| Gráficos | Patrones para data viz, dashboards e infografías |

### Dónde se aplica

1. **Plataforma** — pantallas de conciliación, dashboards, flujos operativos, reportes.
2. **Sitio y materiales comerciales** — landing pages, one-pagers, decks, propuestas.
3. **App** — interfaces móviles con adaptaciones de densidad y toque.
4. **Canales de mensajería** — WhatsApp, Telegram, Slack (stickers, cards interactivos, plantillas).
5. **Documentos técnicos** — contratos, reportes operativos, comunicaciones formales.

Las adaptaciones se permiten en dimensión y densidad. **La identidad nunca cambia.**

### Principios

1. **AI-First por defecto.** Experiencia agéntica; Isac es el centro de la interacción. Las funcionalidades son capacidades del agente, no destinos de navegación. Detalles en [codex-ai-first-experience](codex-ai-first-experience.md).
2. **Token antes que valor crudo.** Los componentes consumen tokens (color, tipografía, espaciado), nunca valores hardcodeados. Cambio en el token propaga en todo el sistema.
3. **Composición sobre personalización.** Combinar componentes existentes antes de crear nuevos. La personalización genera divergencia; la divergencia genera retrabajo.
4. **La accesibilidad es requisito.** WCAG 2.1 AA es el piso, no la meta. Foco, lector de pantalla y teclado forman parte del componente.
5. **La densidad sirve al contexto.** Dashboards densos y formularios amplios coexisten; lo que cambia es la aplicación de los tokens de espaciado.
6. **Documentar la excepción.** Toda fuga del estándar necesita justificación registrada (alimenta la evolución del sistema).

### Fuentes de referencia

| Fuente | Qué vive ahí |
|--------|--------------|
| Notion | Intención, reglas de uso, principios y gobernanza (fuente conceptual) |
| Código (`@guardia/design-system`) | Implementación oficial — fuente de verdad para comportamiento |
| Chromatic | Catálogo visual versionado (todos los estados de cada componente) |
| Figma | Biblioteca de diseño con variantes y tokens reflejados |

**Las divergencias se tratan como bug.** La corrección comienza en el origen de la divergencia y propaga a los demás puntos.

### Stack de implementación

- **Componentes:** [shadcn/ui](https://ui.shadcn.com/) como base, [Tailwind CSS](https://tailwindcss.com/) para estilo, [CopilotKit](https://www.copilotkit.ai/) para interacciones agénticas. Hoy Tailwind v3; migración a v4 condicional a la compatibilidad.
- **Íconos:** [Lucide](https://lucide.dev/).
- **Gráficos:** [shadcn/ui Charts](https://ui.shadcn.com/charts), respetando el schema de colores de data viz.
- **Distribución:** biblioteca `@guardia/design-system` (consumo obligatorio, ver [lex-design-system-library](../lexis/lex-design-system-library.md)).

### Gobernanza

Las propuestas de nuevos componentes, patrones, íconos o tipos de gráfico pasan por el flujo de gobernanza. Antes de crear algo nuevo, verificar si el problema no está resuelto por un patrón existente. Los vacíos reales se vuelven issues en el repositorio de `@guardia/design-system` con contexto, caso de uso y propuesta.

El sistema evoluciona con uso. Cada activo necesita resistir la pregunta: **¿esto se va a reutilizar o es específico de un caso?**

### Enlaces útiles

- Repositorio: [github.com/guardiatechnology/design-system](https://github.com/guardiatechnology/design-system) (en revisión)
- Catálogo Chromatic: [69e15f3b0534f646ac88774b-cpmytvatdp.chromatic.com](https://69e15f3b0534f646ac88774b-cpmytvatdp.chromatic.com/) (en revisión)
- Library Chromatic: [chromatic.com/library?appId=69e15f3b0534f646ac88774b](https://www.chromatic.com/library?appId=69e15f3b0534f646ac88774b)
- Figma: [figma.com/design/F0TkqO6HigGa3C0P8XK9zL/Design-System](https://www.figma.com/design/F0TkqO6HigGa3C0P8XK9zL/Design-System) (despriorizado)

## Referencias

- Notion — Branding / Design System
- [codex-design-system-components](codex-design-system-components.md), [codex-ai-first-experience](codex-ai-first-experience.md)
- [lex-design-system-library](../lexis/lex-design-system-library.md), [lex-ai-first-experience](../lexis/lex-ai-first-experience.md)
