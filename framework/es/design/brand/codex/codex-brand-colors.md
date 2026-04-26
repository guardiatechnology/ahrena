# Codex: Paleta de Colores de Guardia

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Color en cualquier punto de contacto de Guardia

## Visión general

Referencia única de la paleta de Guardia: colores base con significado de marca, escalas 100/200/500/700/900, tonos mono (técnicos), colores de señal (data viz) y combinaciones WCAG aprobadas, restringidas y prohibidas. Consultar antes de aplicar color en UI, deck, documento o material gráfico.

## Contexto

- **Dominio:** identidad cromática, tokens, accesibilidad.
- **Público objetivo:** diseñadores, frontend, mobile, marketing, soporte, agentes de IA que generen piezas visuales.
- **Actualización:** cuando la página *Cores* en Notion sea revisada; los tokens en `@guardia/design-system` reflejan este Codex.

## Contenido

### Colores base y significado

| Color | HEX | Significado |
|-------|-----|-------------|
| Amarillo Brillante | `#FFC30A` | Confianza y Transparencia — optimismo y claridad |
| Naranja Cálido | `#E07400` | Eficiencia y Agilidad — energía y dinamismo |
| Rosa Suave | `#DB6286` | Acogida e Inclusión — empatía, respeto |
| Violeta Profundo | `#4F186D` | Profundidad y Excelencia — seguridad, cumplimiento |
| Gris Báltico | `#3A3A44` | Estabilidad e Integridad — profesionalismo |

### Escalas (100, 200, 500 base, 700, 900)

| Color | 100 | 200 | 500 (base) | 700 | 900 |
|-------|-----|-----|------------|-----|-----|
| Amarillo Brillante | `#FFF3CE` | `#FFE490` | `#FFC30A` | `#B28807` | `#664E04` |
| Naranja Cálido | `#F8E3CC` | `#F1C08C` | `#E07400` | `#9C5100` | `#592E00` |
| Rosa Suave | `#F7DFE6` | `#EEB8C8` | `#DB6286` | `#99445D` | `#572735` |
| Violeta Profundo | `#DBD0E1` | `#AF97BD` | `#4F186D` | `#37104C` | `#1F092B` |
| Gris Báltico | `#D7D7D9` | `#A6A6AA` | `#3A3A44` | `#28282F` | `#17171B` |

### Tonos mono (técnicos)

| Color | Uso | HEX |
|-------|-----|-----|
| Mono Blanco | Fondos claros, superficies, plot areas | `#FDFDFD` |
| Mono Negro | Tinta de texto, ejes, líneas base | `#0E1016` |

Función técnica, fuera de la paleta cromática de la marca.

### Colores de señal (data viz y estados críticos)

| Color | Semántica | HEX |
|-------|-----------|-----|
| Verde Señal | Positivo, salud, crecimiento | `#00BF63` |
| Amarillo Señal | Atención, pendiente, alerta | `#FFDE59` |
| Rojo Señal | Negativo, caída, excepción crítica | `#FF3131` |
| Azul Señal | Informativo, baseline, referencia | `#004AAD` |

Convención universal (verde = positivo, amarillo = atención, rojo = negativo, azul = informativo). **No sustituyen la paleta principal** — uso fuera de gráficos, dashboards y alertas exige justificación.

### Combinaciones WCAG aprobadas (cualquier uso)

| Fondo | Texto | Contraste | WCAG |
|-------|-------|-----------|------|
| Amarillo 500 (`#FFC30A`) | Negro | 13.06:1 | AAA en cualquier tamaño |
| Gris 500 (`#3A3A44`) | Blanco | 11.24:1 | AAA en cualquier tamaño |
| Violeta 500 (`#4F186D`) | Rosa 200 (`#EEB8C8`) | 7.32:1 | AAA en cualquier tamaño |
| Rosa 500 (`#DB6286`) | Negro | 6.10:1 | AA cualquier tamaño, AAA texto grande |
| Gris 500 (`#3A3A44`) | Gris 200 (`#A6A6AA`) | 4.63:1 | AA texto normal (evitar en cuerpos largos) |

### Combinaciones restringidas (títulos, botones, badges)

Cumplen WCAG mínimo solo para texto grande (18pt regular o 14pt bold en adelante):

| Fondo | Texto | Contraste |
|-------|-------|-----------|
| Naranja 500 (`#E07400`) | Violeta 500 (`#4F186D`) | 3.96:1 |
| Violeta 500 (`#4F186D`) | Naranja 500 (`#E07400`) | 3.96:1 |
| Rosa 500 (`#DB6286`) | Blanco | 3.44:1 |
| Naranja 500 (`#E07400`) | Blanco | 3.15:1 |

### Combinación prohibida

| Fondo | Texto | Contraste | Acción |
|-------|-------|-----------|--------|
| Amarillo 500 (`#FFC30A`) | Blanco | 1.61:1 | Eliminar; ilegible en cualquier tamaño |

### Ajustes para liberar texto de cuerpo

- Texto blanco sobre fondos saturados (naranja/rosa): profundizar al tono 700 (Naranja 700 + Blanco = 7.5:1, AAA; Rosa 700 + Blanco = 6.9:1, AA completo).
- Texto claro sobre Amarillo: sustituir blanco por Violeta 500 o Gris 500 (>7:1).
- Para identidad cromática con texto claro sobre naranja/rosa: usar Rosa 100 o Amarillo 100 en lugar del blanco.

## Referencias

- Notion — Branding / Cores
- WCAG 2.1 (AA: 4.5:1 texto normal, 3:1 grande/UI; AAA: 7:1 texto normal, 4.5:1 grande)
- Tokens implementados en `@guardia/design-system`
