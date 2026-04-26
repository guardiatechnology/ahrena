# Lexis: Paleta de Colores Aprobada y Combinaciones WCAG

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Identidad visual de Guardia en cualquier punto de contacto

## Propósito

Garantizar reconocimiento y accesibilidad. La paleta de Guardia carga significado (Confianza, Eficiencia, Acogida, Excelencia, Estabilidad). Colores fuera de la paleta diluyen la marca; combinaciones sin contraste bloquean usuarios y violan WCAG 2.1.

## Ley

> **Toda pieza de Guardia (interfaz, material, documento, post, slide, correo) DEBE usar exclusivamente la paleta oficial — Amarillo Brillante #FFC30A, Naranja Cálido #E07400, Rosa Suave #DB6286, Violeta Profundo #4F186D, Gris Báltico #3A3A44, Mono Blanco #FDFDFD y Mono Negro #0E1016, con las escalas 100/200/500/700/900 — y DEBE alcanzar WCAG 2.1 AA (4.5:1 para texto normal, 3:1 para texto grande/UI). La combinación Amarillo 500 sobre Blanco (1.61:1) está PROHIBIDA. Las combinaciones en el rango 3:1–4.5:1 quedan restringidas a títulos, botones y badges. Los colores de señal (Verde #00BF63, Amarillo #FFDE59, Rojo #FF3131, Azul #004AAD) están reservados para data viz y estados críticos del sistema.**

## Alcance

- **Aplica a:** UI (plataforma, sitio, app), materiales comerciales e institucionales, decks, documentos, correos, posts en redes sociales, íconos e ilustraciones.
- **Agentes vinculados:** diseñadores, frontend, mobile, marketing, soporte, agentes de IA que generen piezas visuales o interfaces.
- **Excepciones:** logotipos de partners y marcas de terceros (presentados con su color original). Casos específicos exigen ADR o registro de excepción en Notion.

## Consecuencias de Violación

1. **Identidad:** color fuera de la paleta debilita el reconocimiento y rompe coherencia con el Brand Kit.
2. **Accesibilidad:** combinación por debajo del mínimo WCAG bloquea usuarios con baja visión; expone la marca a pasivo regulatorio (LGPD, ADA, normas de accesibilidad).
3. **Remediación:** sustituir por el tono aprobado; en fondos saturados (naranja/rosa), profundizar al tono 700 antes de aplicar blanco; en fondos amarillos, sustituir el blanco por Violeta 500 o Gris 500.

## Ejemplos

### Correcto

Texto negro sobre Amarillo 500 (13.06:1, AAA); texto Blanco sobre Gris 500 (11.24:1, AAA); botón Violeta 500 con label Blanco (>7:1); badge Naranja 500 con texto Violeta 500 reservado a botones/títulos (3.96:1, AA grande); gráfico de variación financiera usando Verde Señal/Rojo Señal solo en el eje de datos.

### Incorrecto

Texto blanco sobre Amarillo 500 (1.61:1, ilegible); un color "morado aproximado" inventado para complementar la marca; verde institucional usado como color de marca en un hero; uso de #4F186D fuera de la paleta tokenizada (hardcodeado al lado de colores no aprobados).

## Validación Automatizada

- **Herramienta:** Stylelint con plugin de paleta, axe-core y Lighthouse a11y en CI; revisión visual automatizada (warrior-hephaestus) señalando combinaciones por debajo del mínimo WCAG; tokens centralizados en `@guardia/design-system`.
- **Momento:** pre-commit, CI de UI, revisión de diseño para materiales no-UI.
- **Métrica:** 0 valores cromáticos fuera de la paleta en `main`; 100% de combinaciones texto/fondo ≥ 4.5:1 (texto normal) y ≥ 3:1 (UI/grande); 0 ocurrencias de la combinación prohibida Amarillo 500 + Blanco.

## Referencias

- [codex-brand-colors](../codex/codex-brand-colors.md)
- WCAG 2.1, niveles AA y AAA
- Notion — Branding / Cores
