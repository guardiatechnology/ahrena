# Lexis: DRY (Single Locus for Domain Knowledge)

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Engineering — Backend, Frontend, and Mobile: representation of domain knowledge in application code

## Law

> **Every unique piece of domain knowledge (business rule, validation, calculation, formula, mapping) implemented in application code MUST exist in exactly one canonical locus of the codebase within the same bounded context. Reappearance of that knowledge in ≥ 3 places of the same bounded context REQUIRES extraction to a shared module internal to the context; reappearance in ≥ 2 bounded contexts REQUIRES an ADR deciding between (a) shared kernel, (b) intentional duplication with explicit justification, or (c) anti-corruption layer. Silent duplication of domain knowledge is FORBIDDEN.**

## Coverage

- **Applies to:**
  - Application code in Python (backend), TypeScript/JavaScript (frontend, Node), Swift, Kotlin, and Dart (mobile)
  - Domain validations (CPF, CNPJ, IBAN, eligibility rules)
  - Calculation formulas (taxes, interest, fees, currency conversion)
  - Canonical mappings (domain error codes, statuses, event types)
  - Shared schemas that encode business rules
- **Out of scope (not violations by construction):**
  - Tests, fixtures, and factories (independence required by `lex-test-isolation`)
  - Idiomatic language boilerplate (imports, repetitive signatures, trivial decorators)
  - Structural similarity without identity of meaning (false-DRY: two `validate_id` functions that look alike but represent distinct concepts)
  - UI components (governed by `lex-design-system-library`)
  - Infrastructure-as-code modules (governed by `lex-aws-iac`, rule 4)
- **Bound agents:** `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`, `warrior-athena` (Gate 2 of the Issue-Driven flow)
- **Exceptions:** None. Lexis admit no exceptions.

## Violation Consequences

1. **Automatic block:** Gate 2 (`kata-quality-gate`) rejects the PR when the detector identifies a domain rule reappearing in ≥ 3 places of the same bounded context without extraction, or in ≥ 2 bounded contexts without a corresponding ADR in `docs/adr/`.
2. **Alert:** notifies the owner of the affected bounded context and the feature's tech lead.
3. **Remediation:** the PR author chooses between (a) extracting the knowledge into a shared module internal to the bounded context (default intra-context path), or (b) opening an ADR recording the cross-context architectural decision (shared kernel, intentional duplication, or anti-corruption layer) and referencing it in the PR.

## Examples

### Correct

```python
# libs/validation/tax_id.py — single canonical locus within the "platform" bounded context
def validate_tax_id(tax_id: str) -> bool:
    """Validates CPF or CNPJ according to Receita Federal rules."""
    ...

# refund/use_cases/create_refund.py
from libs.validation.tax_id import validate_tax_id

# payment/use_cases/process_payment.py
from libs.validation.tax_id import validate_tax_id

# kyc/checks/identity.py
from libs.validation.tax_id import validate_tax_id
```

```python
# Cross-bounded-context: ADR recorded in docs/adr/ADR-014-tax-id-validation-shared-kernel.md
# deciding (a) shared kernel: libs/shared/tax_id.py consumed by platform and fiscal
# Decision documented, coupling deliberate.
```

### Incorrect

```python
# refund/validators.py
def validate_tax_id(tax_id: str) -> bool:
    return len(tax_id) == 11 and tax_id.isdigit()

# payment/utils.py — silent duplicate #2
def is_valid_tax_id(tax_id: str) -> bool:
    return len(tax_id) == 11 and tax_id.isdigit()

# kyc/checks.py — silent duplicate #3 (rule-of-three trigger fired)
def check_cpf(value: str) -> bool:
    if not value.isdigit() or len(value) != 11:
        return False
    return True

# billing/helpers.py — silent duplicate #4 with divergent logic
def cpf_valid(s: str) -> bool:
    return s.isdigit() and len(s) in (11, 14)  # diverges: accepts CNPJ
```

```typescript
// fiscal/calculator.ts (bounded context "fiscal")
function calculateTaxRate(amount: number): number { return amount * 0.18; }

// platform/billing/tax.ts (bounded context "platform") — cross-context duplicate without ADR
function calculateTaxRate(amount: number): number { return amount * 0.18; }
// FORBIDDEN: same rule across two bounded contexts without a recorded architectural decision.
```

## Automated Validation

- **Tool:**
  - **JavaScript/TypeScript:** `jscpd` (AST + line detection) configured with a 30-line threshold; `eslint-plugin-sonarjs` (rules `no-duplicate-string`, `no-identical-functions`)
  - **Python:** `pylint --disable=all --enable=R0801` (duplicate-code) with `min-similarity-lines=30`; review by `warrior-apollo` on PRs identifying reappearance of domain rules
  - **Cross-language and cross-context:** SonarQube duplication detector with tags per bounded context; audit by `warrior-athena` at Gate 2 verifying the presence of an ADR for cross-context duplications
  - **ADR:** existence check in `docs/adr/` whenever the detector flags cross-bounded-context
- **When:** pre-commit (jscpd/pylint local), CI on every PR (full scan), Gate 2 of the Issue-Driven flow (verifies ADR for cross-context cases), monthly trend audit
- **Metric:** 0 PRs merged with a new block ≥ 30 lines representing a domain rule reappearing in ≥ 3 places of the same bounded context without extraction; 100% of cross-bounded-context duplications backed by a corresponding ADR; non-increasing monthly trend of the duplication index reported by SonarQube
