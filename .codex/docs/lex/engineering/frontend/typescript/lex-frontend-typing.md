# Lexis: Tipagem Estrita em Frontend

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Código TypeScript em aplicações frontend (React, Next.js, Vue, Angular)

## Lei

> **Todo código frontend DEVE ser escrito em TypeScript com `strict: true` no `tsconfig.json`. `any` explícito DEVE ser justificado com comentário; `any` implícito é proibido. Contratos com APIs externas DEVEM ser tipados via interfaces ou tipos derivados de schema (OpenAPI, Zod).**

## Regras

### 1. TypeScript strict sempre ativo

O `tsconfig.json` do projeto **DEVE** conter no mínimo:

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

`strict: true` habilita um conjunto de verificações essenciais. `noUncheckedIndexedAccess` adiciona segurança em acessos por índice (`array[i]` retorna `T | undefined`).

### 2. Sem `any` implícito ou explícito sem justificativa

O agente **NÃO PODE**:

1. Deixar parâmetros de função sem anotação de tipo quando o tipo não pode ser inferido.
2. Usar `any` explícito sem comentário justificando (ex.: `// any: lib sem tipos oficiais`).
3. Usar `as any` para silenciar erros de tipo — só como último recurso com justificativa.

Alternativas preferidas:
- `unknown` quando o tipo é dinâmico mas controlado (com narrowing explícito)
- Tipos genéricos quando o tipo varia
- Schemas (Zod, Yup) quando o dado vem de fonte externa não-tipada

### 3. Contratos com API tipados explicitamente

Toda chamada de API **DEVE** ter tipos de request e response declarados. Caminhos aceitos:

1. **Gerado de OpenAPI:** usar ferramenta como `openapi-typescript` ou `orval` para gerar tipos a partir do spec OAS
2. **Zod schemas:** declarar schema com Zod, derivar tipo com `z.infer<typeof Schema>`, validar em runtime
3. **Interfaces manuais:** aceitável se pequeno e estável; documentar origem do contrato

Exemplo com Zod:
```typescript
const RefundSchema = z.object({
  id: z.string().uuid(),
  amount: z.number().positive(),
  status: z.enum(["pending", "completed", "failed"]),
});
type Refund = z.infer<typeof RefundSchema>;
```

### 4. Props de componentes tipadas

Componentes React/Vue/Angular **DEVEM** ter props tipadas via interface ou type. Sem `React.FC<any>` nem props implícitas.

```typescript
interface ButtonProps {
  onClick: () => void;
  variant?: "primary" | "secondary";
  disabled?: boolean;
  children: React.ReactNode;
}
```

### 5. Estado tipado

Hooks (`useState`, `useReducer`) e stores (Zustand, Redux, Pinia) **DEVEM** ter o tipo declarado quando o valor inicial é `null`, `undefined` ou não permite inferência correta.

```typescript
// ❌ tipo inferido como null
const [user, setUser] = useState(null);

// ✅ tipo explícito
const [user, setUser] = useState<User | null>(null);
```

## Validação Automatizada

- **Ferramenta:** `tsc --noEmit` no CI; `kata-quality-gate` Check 6 em `engineering/workflow`
- **Momento:** a cada commit/PR
- **Métrica:** 0 erros do TypeScript; 0 usos de `any` não justificados
