# Lexis: Accesibilidad en Frontend (WCAG 2.1 AA)

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Accesibilidad en todas las interfaces web producidas por la aplicación frontend

## Propósito

La accesibilidad no es una feature opcional: es un requisito legal (LGPD art. 18, Ley Brasileña de Inclusión, ADA, EAA europea) y ético. Una UI inaccesible excluye a usuarios con deficiencia visual, motora, cognitiva o auditiva, y empobrece la experiencia de todos (teclado, dispositivos asistivos, ambientes ruidosos). Para agentes IA que generan código frontend, ignorar la accesibilidad es construir deuda legal y humana.

Esta Lexis existe para garantizar que **toda UI producida cumpla como mínimo con WCAG 2.1 nivel AA**, que **los elementos interactivos sean navegables por teclado**, que **el contenido sea anunciado correctamente por lectores de pantalla** y que **el contraste de colores sea adecuado**.

## Ley

> **Toda UI producida DEBE cumplir con WCAG 2.1 nivel AA como mínimo. Los elementos interactivos DEBEN ser alcanzables y operables por teclado. Las imágenes e iconos con significado DEBEN tener texto alternativo. Los formularios DEBEN tener labels asociadas. Los colores DEBEN cumplir un contraste de 4.5:1 para texto normal y 3:1 para texto grande. El estado dinámico DEBE ser anunciado a las tecnologías asistivas.**

## Reglas

### 1. HTML semántico

El agente **DEBE**:

1. Usar elementos nativos: `<button>`, `<a>`, `<nav>`, `<main>`, `<header>`, `<footer>`, `<article>`, `<section>`.
2. No reinventar: un `<div onClick={...}>` con role y tabindex es peor que un `<button>`.
3. Usar la heading hierarchy correcta: `h1` único por página, `h2` para secciones, `h3` anidado a `h2`, etc.

### 2. Navegación por teclado

Todo elemento interactivo **DEBE**:

1. Ser alcanzable vía `Tab` (orden lógico).
2. Ser activable vía `Enter` (enlaces) o `Space` (botones, checkboxes).
3. Tener foco visible (no eliminar `:focus-visible` del CSS).
4. Soportar `Esc` para cerrar modales, dropdowns, drawers.
5. Soportar teclas `Arrow` en listas, menús, tabs, radio groups (según ARIA Authoring Practices).

### 3. Imágenes y medios

1. **Toda `<img>`** con significado **DEBE** tener `alt` descriptivo.
2. **Las imágenes decorativas** usan `alt=""` (explícito, no omitido).
3. **Los iconos que son botones** usan `aria-label` o texto visualmente oculto (`.sr-only`).
4. **Los videos** deben tener subtítulos; **los audios** deben tener transcripción.

### 4. Formularios

1. **Todo `<input>`, `<textarea>`, `<select>`** **DEBE** tener `<label>` asociada vía `htmlFor` o anidamiento.
2. **Los campos obligatorios** se marcan con `required` e indicación visual + `aria-required="true"`.
3. **Los errores de validación** se exponen vía `aria-invalid="true"` + mensaje en `aria-describedby`.
4. **Los agrupamientos** usan `<fieldset>` + `<legend>`.

### 5. Contraste y colores

1. **Texto normal (≤18px)**: contraste mínimo 4.5:1 contra el fondo.
2. **Texto grande (≥18px bold o ≥24px regular)**: contraste mínimo 3:1.
3. **Iconos y elementos gráficos**: contraste mínimo 3:1.
4. **El color nunca es el único indicador** de estado (ej.: un error rojo también tiene icono + texto).
5. Probar con herramientas automatizadas (axe, Lighthouse) y manualmente en modo "daltonismo".

### 6. Contenido dinámico

1. **La carga asíncrona** usa `aria-busy="true"` o `role="status"` para indicar estado.
2. **Los mensajes flash (toasts, alerts)** usan `role="alert"` (assertive) o `role="status"` (polite).
3. **Los modales** son focus-trapped y devuelven el foco al elemento que los abrió; usan `aria-modal="true"` y `role="dialog"`.
4. **Las rutas SPA** mueven el foco al contenido nuevo después de navegar.

### 7. Idioma y orden de lectura

1. **`<html lang="es">`** (o el idioma por defecto del proyecto).
2. **El contenido en otro idioma** usa `lang="en"` en el elemento padre.
3. **El orden de lectura** en el DOM refleja el orden visual (sin `order` en flex/grid que rompa el flujo lógico).

## Alcance

- **Aplica a:** toda UI renderizada, incluyendo componentes de librerías de terceros (si una librería no es accesible, sustituirla o contribuir con el fix)
- **Agentes vinculados:** `warrior-hephaestus` y cualquier otro agente que genere frontend
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Exclusión de usuarios:** las personas con discapacidad no pueden usar la aplicación — problema ético y de alcance
2. **Riesgo legal:** LGPD, Ley Brasileña de Inclusión (LBI), EAA pueden derivar en acciones regulatorias o judiciales
3. **SEO perjudicado:** los sitios inaccesibles tienen peor ranking (Google usa señales de accesibilidad)
4. **Remediación:** correr axe/Lighthouse; corregir violaciones críticas inmediatamente; agregar pruebas de accesibilidad en CI

## Validación Automatizada

- **Herramienta:**
  - `eslint-plugin-jsx-a11y` (lint)
  - `@axe-core/react` o `jest-axe` (pruebas)
  - Lighthouse accessibility audit (CI)
  - Playwright/Cypress + axe-core (E2E)
- **Momento:** cada PR; verificación manual con lector de pantalla en cada release significativo
- **Métrica:** 0 violaciones WCAG AA detectables automáticamente

## Referencias

- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [Ley Brasileña de Inclusión (LBI)](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm)
- `lex-frontend-testing` — queries accesibles en pruebas
