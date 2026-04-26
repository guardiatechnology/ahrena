# Codex: Componentes vía @guardia/design-system

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Consumo de componentes de UI en código de Guardia

## Visión general

La biblioteca `@guardia/design-system` es la fuente de verdad para los componentes de interfaz de Guardia (botones, cards, alertas, formularios, badges, bloques de contenido, layouts agénticos, charts). Este Codex orienta cómo consumir, componer y contribuir con la biblioteca, sosteniendo la ley [lex-design-system-library](../lexis/lex-design-system-library.md): **toda UI de Guardia DEBE consumir `@guardia/design-system`**.

## Contexto

- **Dominio:** consumo de componentes en React/React Native (y otros runtimes que la biblioteca soporte).
- **Público objetivo:** frontend, mobile, fullstack, agentes de IA que producen código de UI (warrior-hephaestus, warrior-iris).
- **Actualización:** en cada release de la biblioteca; cuando la página *Componentes* en Notion sea revisada.

## Contenido

### Premisa central

`@guardia/design-system` encapsula el stack del Design System (shadcn/ui + Tailwind + CopilotKit + Lucide + tokens de marca) y expone componentes listos con tokens y accesibilidad incorporados. **No consumir shadcn/ui, Radix, MUI o Chakra directamente.** El contrato con la marca está en la biblioteca, no en los primitivos.

### Instalación

```bash
# pnpm (preferido)
pnpm add @guardia/design-system

# npm
npm install @guardia/design-system

# yarn
yarn add @guardia/design-system
```

Configurar la hoja de estilos y el provider en el boot de la app:

```tsx
import '@guardia/design-system/styles.css';
import { GuardiaProvider } from '@guardia/design-system';

export function App({ children }: { children: React.ReactNode }) {
  return <GuardiaProvider>{children}</GuardiaProvider>;
}
```

> Los nombres exactos (`GuardiaProvider`, paths de import) siguen lo publicado en la biblioteca; consultar el README del repo `@guardia/design-system` antes de copiar literalmente.

### Cómo elegir un componente

1. Buscar primero en el catálogo Chromatic o en el README de la biblioteca.
2. Combinar variantes y props existentes antes de crear abstracciones locales.
3. Si no hay componente equivalente, abrir issue en el repo `@guardia/design-system` con:
   - caso de uso real (link a la pantalla o material que motiva la demanda);
   - propuesta de API (props, variantes, estados);
   - referencia visual (Figma o screenshot).
4. Mientras la issue se discute, crear un wrapper *temporal* dentro del producto, marcado con TODO apuntando a la issue, jamás un primitivo paralelo (sin tokens).

### Componentes principales (mapa esperado)

La biblioteca organiza componentes en familias. Los nombres pueden variar según los releases; la tabla siguiente es referencia conceptual:

| Familia | Ejemplos | Uso |
|---------|----------|-----|
| Acción | `Button`, `IconButton`, `MenuButton` | Disparar comando o navegación |
| Entrada | `Input`, `TextArea`, `Select`, `Combobox`, `DatePicker`, `Switch`, `Checkbox`, `Radio` | Captura de datos |
| Feedback | `Alert`, `Toast`, `Banner`, `Skeleton`, `EmptyState` | Estados informativos |
| Estructura | `Card`, `Sheet`, `Dialog`, `Drawer`, `Tabs`, `Accordion` | Contenedores y segmentación |
| Tipografía | `Heading`, `Text`, `Code`, `InlineCode` | Jerarquía textual con tokens |
| Navegación | `Breadcrumbs`, `Pagination`, `Stepper` | Orientación dentro del producto |
| Datos | `Table`, `DataGrid`, `Badge`, `Avatar`, `Progress`, `Stat` | Presentación tabular e indicadores |
| Charts | `LineChart`, `BarChart`, `AreaChart`, `PieChart` (sobre shadcn/ui Charts) | Data viz con colores semánticos |
| Marca | `Logo`, `LogoMark` | Aplicación automática de la variante por fondo |
| Agéntico | `ChatPanel`, `Workspace`, `PlanTrace`, `SourceCard`, `ApprovalGate` | Patrones AI-First (CopilotKit) |

> Esta tabla es viva. La fuente de verdad es el catálogo Chromatic + README del repo.

### Ejemplo de composición

```tsx
import {
  Card,
  Heading,
  Text,
  Stat,
  Badge,
  Button,
  Alert,
} from '@guardia/design-system';

export function ReconciliationSummary({ summary, onApprove }: Props) {
  return (
    <Card variant="elevated" padding="lg">
      <Heading level={2}>Conciliación Cielo — 25/04</Heading>
      <Text tone="muted">127 transacciones analizadas en 4m12s</Text>

      <Stat label="Conciliadas" value={119} tone="positive" />
      <Stat label="Pendientes" value={8} tone="attention" />

      {summary.pendingCount > 0 && (
        <Alert tone="warning">
          {summary.pendingCount} transacciones requieren revisión antes del cierre.
        </Alert>
      )}

      <Badge tone="info">Fuente: extracto bancario + EDI Cielo</Badge>
      <Button intent="primary" onClick={onApprove}>Aprobar cierre</Button>
    </Card>
  );
}
```

Nota: ningún estilo inline, ningún color hex, ningún import de shadcn/ui o Radix.

### Composición vs. personalización

- **Composición (preferido):** combinar componentes listos. Variaciones vía `variant`, `intent`, `tone`, `size`.
- **Slot pattern:** cuando se necesite sustituir una región del componente, usar slots/children expuestos por la API.
- **Style overrides:** aceptados *solo* para densidad/espaciado vía tokens (p. ej., `paddingY="sm"`). Nunca sobrescribir colores ni tipografía.
- **Personalización local:** cuando sea inevitable, aislar en un *adapter* claramente marcado como `// TODO: contribuir a @guardia/design-system — issue #N`.

### Tokens

Los tokens se exponen por la biblioteca vía tema (variables CSS) y helpers tipados (p. ej., `useTokens()`). Nunca usar valores hex, fuentes o tamaños hardcodeados; siempre referenciar tokens.

```tsx
import { useTokens } from '@guardia/design-system';

const tokens = useTokens();
// tokens.color.brand.violet[500] → '#4F186D'
// tokens.spacing.lg → '24px'
```

### Accesibilidad

- Cada componente de la biblioteca ya entrega: foco visible, soporte a teclado, ARIA correcto, contraste WCAG 2.1 AA mínimo.
- En producto, garantizar que la composición preserve esas propiedades: no envolver `Button` en `<div onClick>`, no esconder `<label>`, no cambiar `Heading` por `<div>` estilizado.
- Probar con axe-core y lector de pantalla en pantallas críticas.

### Versionado y actualización

- La biblioteca sigue **SemVer**. Cambios breaking → major; nuevas features → minor; correcciones → patch.
- Actualizar regularmente (idealmente vía Renovate/Dependabot semanal).
- En breaking, leer el changelog antes; correr pruebas visuales (Chromatic) y E2E.

### Cuándo contribuir vs. cuándo consumir

| Situación | Acción |
|-----------|--------|
| Componente existe y atiende | Consumir directo |
| Componente existe, pero falta variante/prop | Abrir PR en `@guardia/design-system` añadiendo la variante |
| Componente no existe, patrón repetible | Abrir issue + proponer componente nuevo |
| Patrón único de un producto, no reutilizable | Componer con primitivos de la biblioteca dentro del producto, sin volverlo primitivo paralelo |

## Referencias

- [lex-design-system-library](../lexis/lex-design-system-library.md) — uso obligatorio
- [codex-design-system](codex-design-system.md) — visión general
- [codex-ai-first-experience](codex-ai-first-experience.md) — componentes agénticos
- Repo: `@guardia/design-system` (github.com/guardiatechnology/design-system)
- Catálogo Chromatic
