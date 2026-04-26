# Lexis: Tipografía Oficial — Poppins, Lastica y Roboto

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Comunicación tipográfica de Guardia en cualquier canal

## Propósito

Sostener coherencia tipográfica. La Lastica es propietaria de la firma de marca; la Poppins es la tipografía corriente; la Roboto es el fallback nativo para entornos con restricción de fuentes. Mezclar fuentes ad hoc, o usar Lastica en cuerpos de texto, diluye la identidad y rompe la jerarquía.

## Ley

> **Guardia DEBE usar Poppins como tipografía corriente en toda la comunicación (documentos, decks, propuestas, materiales internos, web, app, redes sociales), con jerarquía estandarizada (H1 Bold/SemiBold, H2 SemiBold, H3/H4 Medium, cuerpo Regular, apoyo Light, énfasis Itálica o SemiBold). La Lastica es EXCLUSIVA de los logotipos oficiales y de la firma de marca — está PROHIBIDO usarla en cuerpo de texto, títulos editoriales o piezas que no sean logotipo. La Roboto es el ÚNICO fallback aceptado cuando Poppins no esté disponible, declarado en CSS como `font-family: 'Poppins', 'Roboto', sans-serif;`. Otras fuentes (Inter, Montserrat, Helvetica, Arial, Lato, Open Sans, etc.) están PROHIBIDAS, salvo excepciones documentadas en ADR.**

## Alcance

- **Aplica a:** UI (web, mobile, correo), decks, documentos, propuestas, contratos, posts en redes sociales, blog, eventos, íconos con texto.
- **Agentes vinculados:** diseñadores, frontend, mobile, marketing, comercial, agentes de IA que generen piezas con texto.
- **Excepciones:** uso técnico de tipografía monoespaciada en snippets de código (libre elección entre fuentes mono populares: JetBrains Mono, Fira Code, Menlo); logotipos de partners (mantienen su tipografía original).

## Consecuencias de Violación

1. **Identidad:** mezcla de fuentes corroe el reconocimiento y la sensación de cuidado de la marca.
2. **Jerarquía:** la falta de jerarquía estandarizada debilita la lectura en decks, dashboards y materiales densos.
3. **Remediación:** sustituir por Poppins (o Roboto en fallback); reservar Lastica a los archivos oficiales de logotipo; refactorizar tokens tipográficos en `@guardia/design-system` cuando la violación ocurra en código.

## Ejemplos

### Correcto

Slide con H1 Poppins Bold 700, cuerpo en Poppins Regular 400, cita en Poppins Italic; landing page con `font-family: 'Poppins', 'Roboto', sans-serif`; firma de correo en Poppins (texto) + archivo oficial del logotipo en Lastica (imagen); contrato en Poppins con jerarquía Medium 500 para subtítulos.

### Incorrecto

Bloque de texto en Lastica (la fuente es exclusiva del logo); título en Inter o Montserrat porque "se veía bonito"; deck comercial mezclando Helvetica y Roboto; CSS sin fallback explícito (`font-family: 'Poppins', sans-serif`).

## Validación Automatizada

- **Herramienta:** regla Stylelint `font-family-no-missing-generic-family-keyword` + lista permitida (Poppins, Roboto + monoespaciada); revisión de diseño (warrior-hephaestus) detectando uso de Lastica fuera de los archivos oficiales; tokens tipográficos centralizados en `@guardia/design-system`.
- **Momento:** pre-commit, CI de UI, revisión de PR para materiales no-UI.
- **Métrica:** 0 declaraciones `font-family` con fuentes fuera de la lista permitida; 0 ocurrencias de Lastica en cuerpo de texto; 100% de las declaraciones CSS con fallback `'Poppins', 'Roboto', sans-serif`.

## Referencias

- [codex-brand-typography](../codex/codex-brand-typography.md)
- Poppins (Google Fonts, SIL OFL); Roboto (Apache 2.0); Lastica (propietaria, Alberto Fontense)
- Notion — Branding / Tipografia
