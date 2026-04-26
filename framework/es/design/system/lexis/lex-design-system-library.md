# Lexis: Uso Obligatorio de la Biblioteca @guardia/design-system

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Plataforma, sitio, app y materiales digitales de Guardia

## Propósito

Garantizar coherencia visual, accesibilidad y gobernanza al consumir componentes de UI. Reimplementar botones, inputs, cards, alertas, formularios o cualquier otro patrón fuera de la biblioteca oficial genera divergencia cromática, drift de tokens y regresiones de accesibilidad — todo eso rompe la promesa de coherencia del Brand Kit y del Design System.

## Ley

> **Toda interfaz de Guardia (plataforma, sitio, app, correos transaccionales, dashboards) DEBE consumir componentes de la biblioteca `@guardia/design-system`. Está PROHIBIDO reimplementar primitivos (botón, input, card, alerta, modal, badge, toast, etc.) o aplicar valores cromáticos, tipográficos o de espaciado hardcodeados en lugar de los tokens expuestos por la biblioteca. La composición (combinar componentes existentes) es el único camino permitido para variaciones; los nuevos primitivos siguen el flujo de gobernanza del Design System.**

## Alcance

- **Aplica a:** todo código de UI versionado de Guardia (React, React Native, correos, landing pages, micro-frontends).
- **Agentes vinculados:** desarrolladores frontend/mobile, diseñadores que abran PRs de código, agentes de IA que generen componentes (warrior-hephaestus, warrior-iris y variantes).
- **Excepciones:** solo durante prototipado descartable, en repositorios marcados como `prototype/*` o `spike/*`. Cualquier código que avance a producción, incluso vía merge parcial, DEBE migrar a `@guardia/design-system` antes del deploy. Vacíos reales (componente inexistente en la biblioteca) DEBEN abordarse vía contribución a la biblioteca, registrada en ADR.

## Consecuencias de Violación

1. **Bloqueo de PR:** la revisión de diseño y CI rechazan PRs que importen `shadcn/ui`, `@radix-ui/*`, `mui`, `chakra-ui` directamente, o que definan clases Tailwind con colores fuera de los tokens.
2. **Divergencia cromática:** componentes "sueltos" no reciben actualizaciones de tokens (p. ej., rebrand, ajuste WCAG) y rompen coherencia entre canales.
3. **Remediación:** sustituir el componente local por el equivalente en `@guardia/design-system`; cuando no exista equivalente, abrir issue en el repositorio de la biblioteca con caso de uso y propuesta antes de seguir.

## Ejemplos

### Correcto

```tsx
import { Button, Card, Alert, useTokens } from '@guardia/design-system';

export function ApprovalCard({ onApprove }: Props) {
  return (
    <Card variant="elevated">
      <Alert tone="warning">Pendiente de aprobación</Alert>
      <Button intent="primary" onClick={onApprove}>Aprobar</Button>
    </Card>
  );
}
```

### Incorrecto

```tsx
// Reimplementa primitivos y usa colores hardcodeados — VIOLA LA LEY
export function ApprovalCard({ onApprove }: Props) {
  return (
    <div style={{ background: '#4F186D', padding: 24, borderRadius: 8 }}>
      <span style={{ color: '#FFC30A' }}>Pendiente</span>
      <button
        onClick={onApprove}
        className="bg-orange-600 text-white px-4 py-2"
      >
        Aprobar
      </button>
    </div>
  );
}
```

## Validación Automatizada

- **Herramienta:** ESLint con `no-restricted-imports` bloqueando `@radix-ui/*`, `@mui/*`, `@chakra-ui/*`, `shadcn-ui`; plugin Stylelint/Tailwind prohibiendo colores fuera de la paleta tokenizada; revisión automatizada de PR (warrior-hephaestus) marcando reimplementaciones.
- **Momento:** pre-commit (lint), CI (build + lint), revisión de PR.
- **Métrica:** 0 imports prohibidos en `main`; 0 valores cromáticos hardcodeados fuera de los tokens; tiempo medio < 1 día entre identificar un vacío y abrir issue en la biblioteca.

## Referencias

- [codex-design-system](../codex/codex-design-system.md), [codex-design-system-components](../codex/codex-design-system-components.md)
- Biblioteca: `@guardia/design-system` ([repo](https://github.com/guardiatechnology/design-system))
- Catálogo visual: Chromatic; espejo de diseño: Figma
