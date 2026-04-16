# Lexis: Tipado Estricto en Frontend

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Código TypeScript en aplicaciones frontend (React, Next.js, Vue, Angular)

## Propósito

Las aplicaciones frontend manipulan datos provenientes de múltiples fuentes (API, URL, localStorage, form inputs, props) y renderizan UI reactiva a esos datos. Sin tipado estricto, los errores que deberían detectarse en compile-time se manifiestan en runtime, rompiendo la UI del usuario final, generando estados inconsistentes y degradando la experiencia.

Esta Lexis existe para garantizar que **todo código frontend sea escrito en TypeScript con modo estricto activado**, que **los contratos con APIs y entidades sean tipados explícitamente**, y que **`any` implícito o explícito no sea permitido fuera de casos frontera justificados**.

## Ley

> **Todo código frontend DEBE ser escrito en TypeScript con `strict: true` en el `tsconfig.json`. El `any` explícito DEBE ser justificado con un comentario; el `any` implícito está prohibido. Los contratos con APIs externas DEBEN ser tipados mediante interfaces o tipos derivados de un schema (OpenAPI, Zod).**

## Reglas

### 1. TypeScript strict siempre activo

El `tsconfig.json` del proyecto **DEBE** contener como mínimo:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUncheckedIndexedAccess": true
  }
}
```

`strict: true` habilita un conjunto de verificaciones esenciales. `noUncheckedIndexedAccess` añade seguridad en accesos por índice (`array[i]` retorna `T | undefined`).

### 2. Sin `any` implícito o explícito sin justificación

El agente **NO PUEDE**:

1. Dejar parámetros de función sin anotación de tipo cuando el tipo no puede ser inferido.
2. Usar `any` explícito sin un comentario que lo justifique (ej.: `// any: lib sin tipos oficiales`).
3. Usar `as any` para silenciar errores de tipo; solo como último recurso con justificación.

Alternativas preferidas:
- `unknown` cuando el tipo es dinámico pero controlado (con narrowing explícito)
- Tipos genéricos cuando el tipo varía
- Schemas (Zod, Yup) cuando el dato viene de una fuente externa no tipada

### 3. Contratos con API tipados explícitamente

Toda llamada a una API **DEBE** tener tipos de request y response declarados. Caminos aceptados:

1. **Generado desde OpenAPI:** usar una herramienta como `openapi-typescript` u `orval` para generar tipos a partir del spec OAS
2. **Zod schemas:** declarar un schema con Zod, derivar el tipo con `z.infer<typeof Schema>`, validar en runtime
3. **Interfaces manuales:** aceptable si es pequeño y estable; documentar el origen del contrato

Ejemplo con Zod:
```typescript
const RefundSchema = z.object({
  id: z.string().uuid(),
  amount: z.number().positive(),
  status: z.enum(["pending", "completed", "failed"]),
});
type Refund = z.infer<typeof RefundSchema>;
```

### 4. Props de componentes tipadas

Los componentes React/Vue/Angular **DEBEN** tener props tipadas mediante interface o type. Sin `React.FC<any>` ni props implícitas.

```typescript
interface ButtonProps {
  onClick: () => void;
  variant?: "primary" | "secondary";
  disabled?: boolean;
  children: React.ReactNode;
}
```

### 5. Estado tipado

Los hooks (`useState`, `useReducer`) y stores (Zustand, Redux, Pinia) **DEBEN** tener el tipo declarado cuando el valor inicial es `null`, `undefined` o no permite una inferencia correcta.

```typescript
// ❌ tipo inferido como null
const [user, setUser] = useState(null);

// ✅ tipo explícito
const [user, setUser] = useState<User | null>(null);
```

## Alcance

- **Aplica a:** todo el código frontend del repositorio (`.ts`, `.tsx`, `.vue`, `.svelte`, etc.)
- **Agentes vinculados:** `warrior-hephaestus` y otros warriors que actúen en frontend
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Runtime errors en producción:** los tipos incorrectos se convierten en `undefined is not a function` en el navegador del cliente
2. **Contratos rotos silenciosamente:** la API cambia y el frontend continúa compilando pero se rompe en runtime
3. **Refactoring peligroso:** sin tipos, renombrar un campo exige pruebas manuales en cada uso
4. **Remediación:** activar `strict` en el `tsconfig.json`, corregir errores incrementalmente (usar `// @ts-expect-error` con justificación únicamente como puente temporal)

## Validación Automatizada

- **Herramienta:** `tsc --noEmit` en CI; `kata-quality-gate` Check 6 en `engineering/workflow`
- **Momento:** en cada commit/PR
- **Métrica:** 0 errores de TypeScript; 0 usos de `any` no justificados

## Referencias

- `codex-frontend-architecture` — patrones arquitecturales de frontend
- [TypeScript Handbook — strict mode](https://www.typescriptlang.org/tsconfig#strict)
