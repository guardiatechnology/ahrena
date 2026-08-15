# Lexis: Uso Obrigatório da Biblioteca @guardia/design-system

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Plataforma, site, app e materiais digitais da Guardia

## Lei

> **Toda interface da Guardia (plataforma, site, app, e-mails transacionais, dashboards) DEVE consumir componentes da biblioteca `@guardia/design-system`. É proibido reimplementar primitivos (botão, input, card, alerta, modal, badge, toast, etc.) ou aplicar valores cromáticos, tipográficos ou de espaçamento hardcoded em vez dos tokens expostos pela biblioteca. Composição (combinar componentes existentes) é o único caminho permitido para variações; novos primitivos seguem o fluxo de governança do Design System.**

## Exemplos

### Correto

```tsx
import { Button, Card, Alert, useTokens } from '@guardia/design-system';

export function ApprovalCard({ onApprove }: Props) {
  return (
    <Card variant="elevated">
      <Alert tone="warning">Pendente de aprovação</Alert>
      <Button intent="primary" onClick={onApprove}>Aprovar</Button>
    </Card>
  );
}
```

### Incorreto

```tsx
// Reimplementa primitivos e usa cores hardcoded — VIOLA A LEI
export function ApprovalCard({ onApprove }: Props) {
  return (
    <div style={{ background: '#4F186D', padding: 24, borderRadius: 8 }}>
      <span style={{ color: '#FFC30A' }}>Pendente</span>
      <button
        onClick={onApprove}
        className="bg-orange-600 text-white px-4 py-2"
      >
        Aprovar
      </button>
    </div>
  );
}
```

## Validação Automatizada

- **Ferramenta:** ESLint com `no-restricted-imports` bloqueando `@radix-ui/*`, `@mui/*`, `@chakra-ui/*`, `shadcn-ui`; Stylelint/Tailwind plugin proibindo cores fora da paleta tokenizada; revisão automática de PR (warrior-hephaestus) marcando reimplementações.
- **Momento:** pre-commit (lint), CI (build + lint), revisão de PR.
- **Métrica:** 0 imports proibidos no `main`; 0 valores cromáticos hardcoded fora dos tokens; tempo médio < 1 dia entre identificação de gap e issue aberta na biblioteca.
