# Codex: Tipografía de Guardia — Poppins, Lastica y Roboto

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Tipografía en comunicación corriente, logos y sistemas digitales

## Visión general

Guardia adopta **Poppins** como tipografía corriente, **Lastica** como exclusiva de los logotipos y **Roboto** como fallback nativo para entornos restringidos. Este Codex consolida jerarquía, uso por canal, instalación y declaración CSS.

## Contexto

- **Dominio:** identidad tipográfica en cualquier canal (UI, decks, documentos, redes sociales, correo, app).
- **Público objetivo:** diseñadores, frontend, mobile, marketing, comercial, agentes de IA que producen texto en piezas visuales.
- **Actualización:** cuando la página *Tipografia* en Notion sea revisada.

## Contenido

### Poppins (corriente)

Sans-serif geométrica moderna de la Indian Type Foundry, distribuida bajo SIL Open Font License (Google Fonts).

- **Estructura:** geométrica con curvas suaves y trazo consistente.
- **Pesos:** 9 (Thin 100 → Black 900) con itálicas.
- **Soporte:** Latin, Latin Extended, Devanagari.
- **Por qué Poppins:** coherencia visual con Lastica (geometría), versatilidad para jerarquías, distribución libre vía Google Fonts (sin barreras de licencia).

### Jerarquía tipográfica recomendada

| Elemento | Peso | Observación |
|----------|------|-------------|
| Título principal (H1) | Bold (700) o SemiBold (600) | Primera jerarquía de lectura |
| Título secundario (H2) | SemiBold (600) | Secciones dentro del documento |
| Subtítulo (H3/H4) | Medium (500) | Subdivisiones y destacados |
| Cuerpo de texto | Regular (400) | Texto corrido estándar |
| Texto de apoyo | Light (300) | Leyendas, notas al pie, metadatos |
| Énfasis | Itálica o SemiBold (600) | Destacado puntual |

### Dónde usar Poppins

Documentos internos (memos, reportes, políticas, actas); presentaciones comerciales e institucionales; propuestas, contratos y materiales para clientes; correos formales y firmas; interfaces digitales y materiales de producto; posts en redes sociales y blog; materiales de marketing y eventos.

### Lastica (exclusiva de los logos)

Sans-serif geométrica creada por Alberto Fontense, escogida para la construcción de los logotipos de Guardia. Reservada para:

- Construcción de los logotipos de Guardia
- Firma oficial de la marca
- Aplicaciones donde la marca aparece como sello o endoso

Usar exclusivamente los archivos oficiales de los logotipos. NO usar en cuerpos de texto, títulos editoriales o piezas que no sean logotipo.

### Roboto (fallback)

Sans-serif diseñada por Christian Robertson para Google, distribuida bajo Apache License 2.0. Tipografía estándar del Android y Google Workspace, presente nativamente en prácticamente cualquier dispositivo.

**Cuándo usar Roboto:**

- Sistemas o plataformas restringidos a la importación de fuentes externas
- Entornos corporativos con restricción de instalación
- Correos en los que el cliente renderiza solo fuentes nativas
- Documentos compartidos con terceros que usan fuentes nativas
- Fallback en CSS cuando Poppins falla en la carga

La jerarquía de Roboto sigue el mismo patrón de pesos de Poppins (sustitución directa).

### Declaración en CSS

```css
font-family: 'Poppins', 'Roboto', sans-serif;
```

Garantiza priorización de Poppins y fallback automático en Roboto.

### Instalación

Poppins disponible en [Google Fonts](https://fonts.google.com/specimen/Poppins):

- **macOS:** `.ttf` abierto en Font Book.
- **Windows:** `.ttf` instalado vía Configuración → Fuentes.
- **Google Workspace:** disponible nativamente en Docs, Slides, Sheets.
- **Microsoft 365:** instalar en el SO para uso en Word, PowerPoint, Excel.
- **Web:** importar vía `<link>` o `@import` desde Google Fonts.
- **Figma y Canva:** disponible nativamente.

## Referencias

- Notion — Branding / Tipografia
- Poppins (Google Fonts, SIL OFL); Roboto (Apache 2.0); Lastica (propietaria)
- Tokens tipográficos en `@guardia/design-system`
