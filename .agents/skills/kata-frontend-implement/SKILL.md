---
name: kata-frontend-implement
description: "Implementar Feature Frontend. Implementação de feature frontend do requisito ao código testado, tipado e acessível"
---

# Kata: Implementar Feature Frontend

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Implementação de feature frontend do requisito ao código testado, tipado e acessível

## Workflow

```
Progresso:
- [ ] 1. Clarificar requisitos e contratos
- [ ] 2. Consultar padrões do codebase
- [ ] 3. Planejar estrutura (componentes, hooks, camadas)
- [ ] 4. Implementar tipos e contratos
- [ ] 5. Implementar componentes com acessibilidade
- [ ] 6. Implementar integração de dados
- [ ] 7. Escrever testes comportamentais
- [ ] 8. Validar (lint, typecheck, test, a11y)
```

### Passo 1: Clarificar requisitos e contratos

1. Consultar `.ahrena/.directives` conforme `lex-directives`.
2. Se ACs estão numerados (fluxo Issue-Driven), mapear cada AC a um comportamento testável.
3. Perguntas ao usuário em lote (até 5 por rodada):
   - Estados de carregamento, erro e vazio: como se comportam?
   - Validações de formulário: client-only ou com feedback do servidor?
   - Comportamento em mobile vs desktop?
   - Autenticação necessária para acessar?
   - Feature flag ou A/B test aplicável?

### Passo 2: Consultar padrões do codebase

1. Ler `codex-frontend-architecture` e identificar:
   - Onde ficam features (`src/features/`, `app/`, etc.)
   - Onde fica o UI kit (`src/components/`)
   - Qual biblioteca de state server (TanStack Query, SWR, etc.)
   - Qual biblioteca de forms (react-hook-form, Formik)
   - Qual abordagem de styling (Tailwind, CSS Modules, etc.)
2. Seguir convenções existentes antes de introduzir novas.

### Passo 3: Planejar estrutura

Para a feature, decidir:

1. **Rotas novas** (se aplicável): caminho, layout, loading/error states.
2. **Componentes** a criar ou modificar — lista com responsabilidade de cada.
3. **Hooks/composables** a criar — lógica reutilizável.
4. **Integração com API** — quais endpoints serão consumidos.
5. **Estado** — server, client, URL, form.
6. **Testes** — quais comportamentos testar e em que nível (unit, componente, integração, E2E).

Apresentar plano ao usuário antes de codificar grandes features (> 200 linhas).

### Passo 4: Implementar tipos e contratos

1. Se existe OAS, gerar tipos via `openapi-typescript` ou validar com Zod.
2. Definir tipos das entidades e props de componentes.
3. Definir tipos de eventos customizados (se houver).
4. Aplicar `lex-frontend-typing`: strict, sem `any` sem justificativa.

### Passo 5: Implementar componentes com acessibilidade

Para cada componente:

1. Usar HTML semântico (`<button>`, `<form>`, `<nav>`, etc.) — `lex-frontend-accessibility`.
2. Labels associadas a inputs, `aria-*` quando necessário.
3. Estados de foco visíveis.
4. Testar navegação por teclado durante o desenvolvimento.
5. Aplicar tokens de design existentes para espaçamento, cores, tipografia.

### Passo 6: Implementar integração de dados

1. **Server state:** usar a biblioteca do projeto (TanStack Query, SWR, etc.) — cache, error, loading automáticos.
2. **Mutations:** incluir `onSuccess` para invalidar queries ou atualizar cache; optimistic update onde adequado.
3. **Forms:** validar com Zod/Yup no cliente; reusar schema para tipos.
4. **Segurança:** nunca expor segredos no bundle (`lex-frontend-security`); sanitizar qualquer HTML dinâmico.

### Passo 7: Escrever testes comportamentais

Para cada AC (ou comportamento, se não há fluxo estruturado):

1. Escrever teste do ponto de vista do usuário (`lex-frontend-testing`).
2. Usar queries acessíveis (`getByRole`, `getByLabelText`).
3. Marcar cada teste com o AC correspondente (se fluxo Issue-Driven):

```typescript
describe("Refund form", () => {
  it("creates refund on submit AC-1", async () => {
    render(<RefundForm paymentId="p123" />);
    await userEvent.type(screen.getByLabelText(/amount/i), "100");
    await userEvent.click(screen.getByRole("button", { name: /submit/i }));
    expect(await screen.findByText(/refund processing/i)).toBeInTheDocument();
  });
});
```

4. Cobrir: caso feliz, erro de validação, erro de API, estado de loading, estado vazio.
5. Adicionar testes a11y automatizados com `jest-axe` ou `axe-core/playwright`.

### Passo 8: Validar

Executar localmente:

1. `yarn typecheck` (ou `tsc --noEmit`) — 0 erros.
2. `yarn lint` — incluindo `eslint-plugin-jsx-a11y`.
3. `yarn test` — todos os testes passam.
4. `yarn test:e2e` se houver E2E relevante.
5. Lighthouse manual em uma página afetada (acessibilidade ≥ 95, performance ≥ 80).

Se está no fluxo Issue-Driven, o `kata-quality-gate` executará estas verificações de forma sistemática no Gate 2.

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Código da feature | `.ts`, `.tsx`, `.css`, etc. | Conforme arquitetura do projeto |
| Testes | `.test.ts`, `.test.tsx` | Ao lado dos componentes ou em `__tests__/` |
| Tipos | Interfaces e schemas | Em `types/` ou junto aos componentes |
| Documentação de componente (se reutilizável) | Storybook ou JSDoc | Conforme padrão do projeto |

## Restrições

- **Seguir padrões existentes:** antes de introduzir novo pattern, verificar se não há equivalente já usado no codebase.
- **Sem quebrar acessibilidade:** nenhum commit pode degradar a11y (Lighthouse, axe devem continuar verdes).
- **Sem `any` implícito:** `lex-frontend-typing` é mandatório.
- **Testes de comportamento, não de implementação:** `lex-frontend-testing`.
- **Commits pequenos:** separar estrutura/esqueleto de lógica; forms de integração; testes de código de produção.
