# Lexis: Uso Correcto del Logotipo de Guardia

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Logotipo, símbolo y logo aislado de Guardia en cualquier aplicación

## Propósito

Preservar legibilidad y reconocimiento. El logotipo principal (símbolo violeta con G naranja + Lastica) tiene versiones para cada contexto cromático. Aplicar la versión incorrecta (p. ej., principal sobre fondo violeta) hace que el símbolo se confunda con el fondo y rompa la identidad.

## Ley

> **Toda aplicación del logotipo de Guardia DEBE usar SOLO los archivos oficiales y DEBE seleccionar la variante correcta según el fondo: (1) **Logotipo principal** (símbolo violeta + G naranja) sobre fondos claros y oscuros fuera del espectro del violeta; (2) **Logotipo secundario** (símbolo naranja + G violeta) sobre fondos en el espectro del violeta; (3) **Monocromático negro** sobre fondos claros cuando el color no esté disponible; (4) **Monocromático blanco** sobre fondos oscuros cuando el color no esté disponible; (5) **Logo aislado** (sin la palabra "Guardia") solo en aplicaciones reducidas (favicon, avatar, firma compacta) o donde la marca ya esté establecida en el contexto. Está PROHIBIDO recolorear, distorsionar, rotar, aplicar contornos, sombras, gradientes o efectos; sustituir la Lastica por otra fuente; reducir el logotipo por debajo de la dimensión mínima documentada; o aplicar la versión incorrecta al fondo (p. ej., logotipo principal sobre violeta).**

## Alcance

- **Aplica a:** UI (favicons, headers, pantalla de login), correos, decks, propuestas, contratos, redes sociales, eventos, regalos, videos, alianzas.
- **Agentes vinculados:** diseñadores, marketing, comercial, frontend/mobile (favicon, headers), agentes de IA que produzcan piezas con la marca.
- **Excepciones:** parodias internas claramente marcadas (off-brand), celebraciones estacionales aprobadas por Brand. Toda excepción pública exige aprobación del CEO o responsable designado de Brand.

## Consecuencias de Violación

1. **Identidad:** logotipo distorsionado o recoloreado debilita el reconocimiento y crea sensación de descuido.
2. **Legibilidad:** versión incorrecta para el fondo vuelve invisible el símbolo.
3. **Remediación:** sustituir por el archivo oficial correspondiente; restaurar dimensiones originales; eliminar efectos aplicados; revisar checklist de variante por fondo antes de republicar.

## Ejemplos

### Correcto

Sitio sobre fondo blanco usando el logotipo principal; pantalla de login con fondo Violeta 500 usando el logotipo secundario; contrato en B/N usando el monocromático negro sobre página blanca; favicon usando el logo violeta aislado; banner sobre Violeta Profundo usando el logo naranja transparente; firma de correo con logotipo principal exportado de los archivos oficiales.

### Incorrecto

Logotipo principal sobre fondo Violeta 500 (el símbolo violeta se funde con el fondo); logotipo recoloreado en verde para "combinar con el tema del post"; logotipo con sombra "para destacar"; texto "Guardia" tipeado en Helvetica simulando el logotipo; logo por debajo de 16px de altura en UI; logotipo distorsionado a 16:9 para llenar un banner.

## Validación Automatizada

- **Herramienta:** revisión automatizada (warrior-hephaestus + revisor humano de Brand) detectando logotipos no oficiales o aplicaciones en fondo conflictivo; biblioteca `@guardia/design-system` exponiendo un único componente `<Logo variant="..." />` que siempre elige la variante correcta.
- **Momento:** revisión de PR de UI; revisión de Brand para piezas comerciales e institucionales; auditoría trimestral de assets externos.
- **Métrica:** 0 logotipos recoloreados/distorsionados en piezas publicadas; 100% de las aplicaciones en producto consumiendo `<Logo />` de la biblioteca; 0 aplicaciones de la versión principal sobre fondo en el espectro del violeta.

## Referencias

- [codex-brand-logo](../codex/codex-brand-logo.md)
- Notion — Branding / Logomarca e Logotipos
