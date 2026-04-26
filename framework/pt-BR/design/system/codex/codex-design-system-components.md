# Codex: Componentes via @guardia/design-system

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Consumo de componentes de UI em código da Guardia

## Visão Geral

A biblioteca `@guardia/design-system` é a fonte da verdade para componentes de interface da Guardia (botões, cards, alertas, formulários, badges, blocos de conteúdo, layouts agênticos, charts). Este Codex orienta como consumir, compor e contribuir com a biblioteca, sustentando a lei [lex-design-system-library](../lexis/lex-design-system-library.md): **toda UI da Guardia DEVE consumir `@guardia/design-system`**.

## Contexto

- **Domínio:** consumo de componentes em React/React Native (e outros runtimes que a biblioteca passar a suportar).
- **Público-alvo:** frontend, mobile, fullstack, agentes de IA que produzam código de UI (warrior-hephaestus, warrior-iris).
- **Atualização:** a cada release da biblioteca; quando a página *Componentes* no Notion for revisada.

## Conteúdo

### Premissa central

`@guardia/design-system` encapsula a stack do Design System (shadcn/ui + Tailwind + CopilotKit + Lucide + tokens da marca) e expõe componentes prontos com tokens e acessibilidade incorporados. **Não consumir shadcn/ui, Radix, MUI ou Chakra diretamente.** O contrato com a marca está na biblioteca, não nos primitivos.

### Instalação

```bash
# pnpm (preferido)
pnpm add @guardia/design-system

# npm
npm install @guardia/design-system

# yarn
yarn add @guardia/design-system
```

Configurar a folha de estilos e o provider no boot do app:

```tsx
import '@guardia/design-system/styles.css';
import { GuardiaProvider } from '@guardia/design-system';

export function App({ children }: { children: React.ReactNode }) {
  return <GuardiaProvider>{children}</GuardiaProvider>;
}
```

> Os nomes exatos (`GuardiaProvider`, paths de import) seguem o que está publicado na biblioteca; conferir o README do repo `@guardia/design-system` antes de copiar literalmente.

### Como escolher um componente

1. Procurar primeiro no catálogo Chromatic ou no README da biblioteca.
2. Combinar variantes e props existentes antes de criar abstrações locais.
3. Se não houver componente equivalente, abrir issue no repo `@guardia/design-system` com:
   - caso de uso real (link para tela ou material que motiva a demanda);
   - proposta de API (props, variantes, estados);
   - referência visual (Figma ou print).
4. Enquanto a issue é discutida, criar um wrapper *temporário* dentro do produto, marcado com TODO apontando a issue, jamais um primitivo paralelo (sem tokens).

### Componentes principais (mapa esperado)

A biblioteca organiza componentes em famílias. Os nomes podem variar conforme releases; a tabela abaixo é referência conceitual:

| Família | Exemplos | Uso |
|---------|----------|-----|
| Ação | `Button`, `IconButton`, `MenuButton` | Disparar comando ou navegação |
| Entrada | `Input`, `TextArea`, `Select`, `Combobox`, `DatePicker`, `Switch`, `Checkbox`, `Radio` | Captura de dados |
| Feedback | `Alert`, `Toast`, `Banner`, `Skeleton`, `EmptyState` | Estados informativos |
| Estrutura | `Card`, `Sheet`, `Dialog`, `Drawer`, `Tabs`, `Accordion` | Containers e segmentação |
| Tipografia | `Heading`, `Text`, `Code`, `InlineCode` | Hierarquia textual com tokens |
| Navegação | `Breadcrumbs`, `Pagination`, `Stepper` | Orientação dentro do produto |
| Dados | `Table`, `DataGrid`, `Badge`, `Avatar`, `Progress`, `Stat` | Apresentação tabular e indicadores |
| Charts | `LineChart`, `BarChart`, `AreaChart`, `PieChart` (sobre shadcn/ui Charts) | Data viz com cores semânticas |
| Marca | `Logo`, `LogoMark` | Aplicação automática da variante por fundo |
| Agêntico | `ChatPanel`, `Workspace`, `PlanTrace`, `SourceCard`, `ApprovalGate` | Padrões AI-First (CopilotKit) |

> Esta tabela é viva. A fonte de verdade é o catálogo Chromatic + README do repo.

### Exemplo de composição

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
      <Heading level={2}>Conciliação Cielo — 25/04</Heading>
      <Text tone="muted">127 transações analisadas em 4m12s</Text>

      <Stat label="Conciliadas" value={119} tone="positive" />
      <Stat label="Pendentes" value={8} tone="attention" />

      {summary.pendingCount > 0 && (
        <Alert tone="warning">
          {summary.pendingCount} transações precisam de revisão antes do fechamento.
        </Alert>
      )}

      <Badge tone="info">Fonte: extrato bancário + EDI Cielo</Badge>
      <Button intent="primary" onClick={onApprove}>Aprovar fechamento</Button>
    </Card>
  );
}
```

Note: nenhum estilo inline, nenhuma cor hex, nenhum import de shadcn/ui ou Radix.

### Composição vs. customização

- **Composição (preferido):** combinar componentes prontos. Variações via `variant`, `intent`, `tone`, `size`.
- **Slot pattern:** quando precisar substituir uma região do componente, usar slots/children expostos pela API.
- **Style overrides:** aceitos *somente* para densidade/espaçamento via tokens (ex.: `paddingY="sm"`). Nunca sobrescrever cores ou tipografia.
- **Customização local:** quando inevitável, isolar em um *adapter* claramente marcado como `// TODO: contribuir para @guardia/design-system — issue #N`.

### Tokens

Tokens são expostos pela biblioteca via tema (CSS variables) e helpers tipados (ex.: `useTokens()`). Nunca usar valores hex, fontes ou tamanhos hardcoded; sempre referenciar tokens.

```tsx
import { useTokens } from '@guardia/design-system';

const tokens = useTokens();
// tokens.color.brand.violet[500] → '#4F186D'
// tokens.spacing.lg → '24px'
```

### Acessibilidade

- Cada componente da biblioteca já entrega: foco visível, suporte a teclado, ARIA correto, contraste WCAG 2.1 AA mínimo.
- Em produto, garantir que a composição preserve essas propriedades: não envolver `Button` em `<div onClick>`, não esconder `<label>`, não trocar `Heading` por `<div>` estilizado.
- Testar com axe-core e screen reader em telas críticas.

### Versionamento e atualização

- A biblioteca segue **SemVer**. Mudanças breaking → major; novas features → minor; correções → patch.
- Atualizar regularmente (idealmente via Renovate/Dependabot semanal).
- Em breaking, ler o changelog antes; rodar testes visuais (Chromatic) e E2E.

### Quando contribuir vs. quando consumir

| Situação | Ação |
|----------|------|
| Componente existe e atende | Consumir direto |
| Componente existe, mas falta variante/prop | Abrir PR em `@guardia/design-system` adicionando a variante |
| Componente não existe, padrão repetível | Abrir issue + propor componente novo |
| Padrão único de um produto, não-reutilizável | Compor com primitivos da biblioteca dentro do produto, sem virar primitivo paralelo |

## Referências

- [lex-design-system-library](../lexis/lex-design-system-library.md) — uso obrigatório
- [codex-design-system](codex-design-system.md) — visão geral
- [codex-ai-first-experience](codex-ai-first-experience.md) — componentes agênticos
- Repo: `@guardia/design-system` (github.com/guardiatechnology/design-system)
- Chromatic catalog
