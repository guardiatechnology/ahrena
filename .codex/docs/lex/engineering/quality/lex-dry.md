# Lexis: DRY (Único Locus para Conhecimento de Domínio)

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Engenharia — Backend, Frontend e Mobile: representação de conhecimento de domínio em código de aplicação

## Lei

> **Todo conhecimento de domínio único (regra de negócio, validação, cálculo, fórmula, mapeamento) implementado em código de aplicação DEVE existir em exatamente um locus canônico do codebase dentro do mesmo bounded context. Reaparecimento desse conhecimento em ≥ 3 locais do mesmo bounded context OBRIGA extração para módulo compartilhado interno ao contexto; reaparecimento em ≥ 2 bounded contexts OBRIGA registro de ADR escolhendo entre (a) shared kernel, (b) duplicação intencional com justificativa explícita, ou (c) anti-corruption layer. Duplicação silenciosa de conhecimento de domínio é PROIBIDA.**

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
