# Lexis: Strict Typing in Frontend

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** TypeScript code in frontend applications (React, Next.js, Vue, Angular)

## Purpose

Frontend applications manipulate data coming from multiple sources (API, URL, localStorage, form inputs, props) and render UI reactive to that data. Without strict typing, errors that should be caught at compile-time manifest at runtime — breaking the end user's UI, generating inconsistent states, and degrading the experience.

This Lexis exists to ensure that **all frontend code is written in TypeScript with strict mode enabled**, that **contracts with APIs and entities are explicitly typed**, and that **implicit or explicit `any` is not allowed outside of justified edge cases**.

## Law

> **All frontend code MUST be written in TypeScript with `strict: true` in `tsconfig.json`. Explicit `any` MUST be justified with a comment; implicit `any` is prohibited. Contracts with external APIs MUST be typed via interfaces or types derived from schemas (OpenAPI, Zod).**

## Rules

### 1. TypeScript strict always on

The project's `tsconfig.json` **MUST** contain at minimum:

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

`strict: true` enables a set of essential checks. `noUncheckedIndexedAccess` adds safety to indexed accesses (`array[i]` returns `T | undefined`).

### 2. No implicit or explicit `any` without justification

The agent **MUST NOT**:

1. Leave function parameters without type annotation when the type cannot be inferred.
2. Use explicit `any` without a justifying comment (e.g., `// any: lib without official types`).
3. Use `as any` to silence type errors — only as a last resort with justification.

Preferred alternatives:
- `unknown` when the type is dynamic but controlled (with explicit narrowing)
- Generic types when the type varies
- Schemas (Zod, Yup) when the data comes from an untyped external source

### 3. API contracts explicitly typed

Every API call **MUST** have declared request and response types. Accepted paths:

1. **Generated from OpenAPI:** use a tool like `openapi-typescript` or `orval` to generate types from the OAS spec
2. **Zod schemas:** declare schema with Zod, derive type with `z.infer<typeof Schema>`, validate at runtime
3. **Manual interfaces:** acceptable if small and stable; document contract origin

Example with Zod:
```typescript
const RefundSchema = z.object({
  id: z.string().uuid(),
  amount: z.number().positive(),
  status: z.enum(["pending", "completed", "failed"]),
});
type Refund = z.infer<typeof RefundSchema>;
```

### 4. Typed component props

React/Vue/Angular components **MUST** have props typed via interface or type. No `React.FC<any>` nor implicit props.

```typescript
interface ButtonProps {
  onClick: () => void;
  variant?: "primary" | "secondary";
  disabled?: boolean;
  children: React.ReactNode;
}
```

### 5. Typed state

Hooks (`useState`, `useReducer`) and stores (Zustand, Redux, Pinia) **MUST** have the type declared when the initial value is `null`, `undefined`, or does not allow correct inference.

```typescript
// ❌ type inferred as null
const [user, setUser] = useState(null);

// ✅ explicit type
const [user, setUser] = useState<User | null>(null);
```

## Applicability

- **Applies to:** all frontend code in the repository (`.ts`, `.tsx`, `.vue`, `.svelte`, etc.)
- **Linked agents:** `warrior-hephaestus` and other warriors acting on frontend
- **Exceptions:** None. Lexis admit no exceptions.

## Consequences of Violation

1. **Runtime errors in production:** incorrect types become `undefined is not a function` in the client's browser
2. **Silently broken contracts:** API changes and the frontend keeps compiling but breaks at runtime
3. **Dangerous refactoring:** without types, renaming a field requires manual testing at every usage
4. **Remediation:** enable `strict` in `tsconfig.json`, fix errors incrementally (use `// @ts-expect-error` with justification only as a temporary bridge)

## Automated Validation

- **Tool:** `tsc --noEmit` in CI; `kata-quality-gate` Check 6 in `engineering/workflow`
- **Moment:** at every commit/PR
- **Metric:** 0 TypeScript errors; 0 unjustified uses of `any`

## References

- `codex-frontend-architecture` — frontend architectural patterns
- [TypeScript Handbook — strict mode](https://www.typescriptlang.org/tsconfig#strict)
