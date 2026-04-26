# Lexis: Uso Obrigatório da Biblioteca @guardia/design-system

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Plataforma, site, app e materiais digitais da Guardia

## Propósito

Garantir coerência visual, acessibilidade e governança ao consumir componentes de UI. Reimplementar botões, inputs, cards, alertas, formulários ou qualquer outro padrão fora da biblioteca oficial gera divergência cromática, drift de tokens e regressões de acessibilidade — tudo isso quebra a promessa de coerência do Brand Kit e do Design System.

## Lei

> **Toda interface da Guardia (plataforma, site, app, e-mails transacionais, dashboards) DEVE consumir componentes da biblioteca `@guardia/design-system`. É proibido reimplementar primitivos (botão, input, card, alerta, modal, badge, toast, etc.) ou aplicar valores cromáticos, tipográficos ou de espaçamento hardcoded em vez dos tokens expostos pela biblioteca. Composição (combinar componentes existentes) é o único caminho permitido para variações; novos primitivos seguem o fluxo de governança do Design System.**

## Abrangência

- **Aplica-se a:** todo código de UI versionado da Guardia (React, React Native, e-mails, landing pages, micro-frontends).
- **Agentes vinculados:** desenvolvedores frontend/mobile, designers que abrirem PRs de código, agentes de IA que gerem componentes (warrior-hephaestus, warrior-iris e variantes).
- **Exceções:** apenas durante prototipação descartável, em repositórios marcados como `prototype/*` ou `spike/*`. Qualquer código que avance para produção, mesmo via merge parcial, DEVE migrar para `@guardia/design-system` antes do deploy. Lacunas reais (componente inexistente na biblioteca) DEVEM ser endereçadas via contribuição na biblioteca, registrada em ADR.

## Consequências de Violação

1. **Bloqueio de PR:** revisão de design e CI rejeita PRs que importem `shadcn/ui`, `@radix-ui/*`, `mui`, `chakra-ui` diretamente, ou definam classes Tailwind com cores fora dos tokens.
2. **Divergência cromática:** componentes "soltos" não recebem updates de tokens (ex.: rebrand, ajuste WCAG) e quebram coerência entre canais.
3. **Remediação:** substituir o componente local pelo equivalente em `@guardia/design-system`; quando o equivalente não existir, abrir issue no repositório da biblioteca com caso de uso e proposta antes de seguir.

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

## Referências

- [codex-design-system](../codex/codex-design-system.md), [codex-design-system-components](../codex/codex-design-system-components.md)
- Biblioteca: `@guardia/design-system` ([repo](https://github.com/guardiatechnology/design-system))
- Catálogo visual: Chromatic; espelho de design: Figma
