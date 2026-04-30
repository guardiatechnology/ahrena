# Lexis: DRY (Único Locus para Conhecimento de Domínio)

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Engenharia — Backend, Frontend e Mobile: representação de conhecimento de domínio em código de aplicação

## Propósito

Conhecimento de domínio duplicado diverge com o tempo. Uma cópia recebe a correção, outra não, e o sistema entra em inconsistência silenciosa que só aparece em produção (cálculo errado de imposto, validação aceita em um fluxo e rejeita em outro, mapeamento de erro diferente entre serviços). Esta Lei evita esse custo onde ele é real (regras que mudam juntas) sem cair em abstração prematura (false-DRY), preservando a regra dos três como gatilho objetivo de extração e exigindo decisão arquitetural explícita (ADR) quando o mesmo conhecimento atravessa bounded contexts.

## Lei

> **Todo conhecimento de domínio único (regra de negócio, validação, cálculo, fórmula, mapeamento) implementado em código de aplicação DEVE existir em exatamente um locus canônico do codebase dentro do mesmo bounded context. Reaparecimento desse conhecimento em ≥ 3 locais do mesmo bounded context OBRIGA extração para módulo compartilhado interno ao contexto; reaparecimento em ≥ 2 bounded contexts OBRIGA registro de ADR escolhendo entre (a) shared kernel, (b) duplicação intencional com justificativa explícita, ou (c) anti-corruption layer. Duplicação silenciosa de conhecimento de domínio é PROIBIDA.**

## Abrangência

- **Aplica-se a:**
  - Código de aplicação em Python (backend), TypeScript/JavaScript (frontend, Node), Swift, Kotlin e Dart (mobile)
  - Validações de domínio (CPF, CNPJ, IBAN, regras de elegibilidade)
  - Fórmulas de cálculo (impostos, juros, taxas, conversão de moeda)
  - Mapeamentos canônicos (códigos de erro do domínio, status, tipos de evento)
  - Schemas compartilhados que codificam regra de negócio
- **Fora do objeto desta Lei (não são violações por construção):**
  - Testes, fixtures e factories (independência exigida por `lex-test-isolation`)
  - Boilerplate idiomático da linguagem (imports, signatures repetitivas, decoradores triviais)
  - Similaridade estrutural sem identidade de domínio (false-DRY: dois `validate_id` que parecem iguais mas representam conceitos distintos)
  - Componentes de UI (governados por `lex-design-system-library`)
  - Módulos de infraestrutura como código (governados por `lex-aws-iac`, regra 4)
- **Agentes vinculados:** `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`, `warrior-athena` (Gate 2 do fluxo Issue-Driven)
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Bloqueio automático:** Gate 2 (`kata-quality-gate`) reprova o PR quando o detector identifica reaparecimento de regra de domínio em ≥ 3 locais do mesmo bounded context sem extração, ou em ≥ 2 bounded contexts sem ADR correspondente em `docs/adr/`.
2. **Alerta:** notifica o owner do bounded context afetado e o tech lead da feature.
3. **Remediação:** o autor do PR escolhe entre (a) extrair o conhecimento para módulo compartilhado interno ao bounded context (caminho default intra-contexto), ou (b) abrir ADR registrando a decisão arquitetural cross-context (shared kernel, duplicação intencional ou anti-corruption layer) e referenciá-lo no PR.

## Exemplos

### Correto

```python
# libs/validation/tax_id.py — único locus canônico no bounded context "platform"
def validate_tax_id(tax_id: str) -> bool:
    """Valida CPF ou CNPJ conforme regras da Receita Federal."""
    ...

# refund/use_cases/create_refund.py
from libs.validation.tax_id import validate_tax_id

# payment/use_cases/process_payment.py
from libs.validation.tax_id import validate_tax_id

# kyc/checks/identity.py
from libs.validation.tax_id import validate_tax_id
```

```python
# Cross-bounded-context: ADR registrado em docs/adr/ADR-014-tax-id-validation-shared-kernel.md
# decidindo (a) shared kernel: libs/shared/tax_id.py consumido por platform e fiscal
# Decisão documentada, acoplamento consciente.
```

### Incorreto

```python
# refund/validators.py
def validate_tax_id(tax_id: str) -> bool:
    return len(tax_id) == 11 and tax_id.isdigit()

# payment/utils.py — duplicata silenciosa nº 2
def is_valid_tax_id(tax_id: str) -> bool:
    return len(tax_id) == 11 and tax_id.isdigit()

# kyc/checks.py — duplicata silenciosa nº 3 (gatilho da regra dos três disparado)
def check_cpf(value: str) -> bool:
    if not value.isdigit() or len(value) != 11:
        return False
    return True

# billing/helpers.py — duplicata silenciosa nº 4 com lógica divergente
def cpf_valid(s: str) -> bool:
    return s.isdigit() and len(s) in (11, 14)  # diverge: aceita CNPJ
```

```typescript
// fiscal/calculator.ts (bounded context "fiscal")
function calculateTaxRate(amount: number): number { return amount * 0.18; }

// platform/billing/tax.ts (bounded context "platform") — duplicata cross-context sem ADR
function calculateTaxRate(amount: number): number { return amount * 0.18; }
// PROIBIDO: mesma regra em dois bounded contexts sem decisão arquitetural registrada.
```

## Validação Automatizada

- **Ferramenta:**
  - **JavaScript/TypeScript:** `jscpd` (detecção AST + linha) configurado com threshold de 30 linhas; `eslint-plugin-sonarjs` (regras `no-duplicate-string`, `no-identical-functions`)
  - **Python:** `pylint --disable=all --enable=R0801` (duplicate-code) com `min-similarity-lines=30`; revisão por `warrior-apollo` em PRs identificando reaparecimento de regras de domínio
  - **Cross-language e cross-context:** SonarQube duplication detector com tags por bounded context; auditoria por `warrior-athena` no Gate 2 verificando presença de ADR para duplicações cross-context
  - **ADR:** validação de existência em `docs/adr/` quando o detector aponta cross-bounded-context
- **Momento:** pre-commit (jscpd/pylint local), CI em todo PR (full scan), Gate 2 do fluxo Issue-Driven (verifica ADR para casos cross-context), auditoria mensal de tendência
- **Métrica:** 0 PRs mergeados com novo bloco ≥ 30 linhas representando regra de domínio reaparecendo em ≥ 3 locais do mesmo bounded context sem extração; 100% das duplicações cross-bounded-context com ADR correspondente; tendência mensal não crescente do índice de duplicação reportado pelo SonarQube
