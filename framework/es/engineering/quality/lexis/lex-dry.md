# Lexis: DRY (Locus Único para Conocimiento de Dominio)

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Ingeniería — Backend, Frontend y Mobile: representación de conocimiento de dominio en código de aplicación

## Propósito

El conocimiento de dominio duplicado diverge con el tiempo. Una copia recibe la corrección, otra no, y el sistema entra en una inconsistencia silenciosa que solo aparece en producción (cálculo erróneo de impuesto, validación aceptada en un flujo y rechazada en otro, mapeo de error distinto entre servicios). Esta Ley evita ese costo donde es real (reglas que cambian juntas) sin caer en abstracción prematura (false-DRY), preservando la regla de los tres como disparador objetivo de extracción y exigiendo decisión arquitectónica explícita (ADR) cuando el mismo conocimiento atraviesa bounded contexts.

## Ley

> **Todo conocimiento de dominio único (regla de negocio, validación, cálculo, fórmula, mapeo) implementado en código de aplicación DEBE existir en exactamente un locus canónico del codebase dentro del mismo bounded context. La reaparición de ese conocimiento en ≥ 3 lugares del mismo bounded context OBLIGA a su extracción a un módulo compartido interno al contexto; la reaparición en ≥ 2 bounded contexts OBLIGA al registro de un ADR que decida entre (a) shared kernel, (b) duplicación intencional con justificación explícita, o (c) anti-corruption layer. La duplicación silenciosa de conocimiento de dominio está PROHIBIDA.**

## Alcance

- **Se aplica a:**
  - Código de aplicación en Python (backend), TypeScript/JavaScript (frontend, Node), Swift, Kotlin y Dart (mobile)
  - Validaciones de dominio (CPF, CNPJ, IBAN, reglas de elegibilidad)
  - Fórmulas de cálculo (impuestos, intereses, tasas, conversión de moneda)
  - Mapeos canónicos (códigos de error del dominio, estados, tipos de evento)
  - Schemas compartidos que codifican regla de negocio
- **Fuera del objeto de esta Ley (no son violaciones por construcción):**
  - Tests, fixtures y factories (independencia exigida por `lex-test-isolation`)
  - Boilerplate idiomático del lenguaje (imports, signatures repetitivas, decoradores triviales)
  - Similitud estructural sin identidad de dominio (false-DRY: dos `validate_id` que parecen iguales pero representan conceptos distintos)
  - Componentes de UI (gobernados por `lex-design-system-library`)
  - Módulos de infraestructura como código (gobernados por `lex-aws-iac`, regla 4)
- **Agentes vinculados:** `warrior-apollo`, `warrior-hephaestus`, `warrior-iris`, `warrior-athena` (Gate 2 del flujo Issue-Driven)
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de la Violación

1. **Bloqueo automático:** Gate 2 (`kata-quality-gate`) rechaza el PR cuando el detector identifica reaparición de regla de dominio en ≥ 3 lugares del mismo bounded context sin extracción, o en ≥ 2 bounded contexts sin ADR correspondiente en `docs/adr/`.
2. **Alerta:** notifica al owner del bounded context afectado y al tech lead de la feature.
3. **Remediación:** el autor del PR elige entre (a) extraer el conocimiento a un módulo compartido interno al bounded context (camino por defecto intra-contexto), o (b) abrir un ADR que registre la decisión arquitectónica cross-context (shared kernel, duplicación intencional o anti-corruption layer) y referenciarlo en el PR.

## Ejemplos

### Correcto

```python
# libs/validation/tax_id.py — locus canónico único en el bounded context "platform"
def validate_tax_id(tax_id: str) -> bool:
    """Valida CPF o CNPJ según las reglas de la Receita Federal."""
    ...

# refund/use_cases/create_refund.py
from libs.validation.tax_id import validate_tax_id

# payment/use_cases/process_payment.py
from libs.validation.tax_id import validate_tax_id

# kyc/checks/identity.py
from libs.validation.tax_id import validate_tax_id
```

```python
# Cross-bounded-context: ADR registrado en docs/adr/ADR-014-tax-id-validation-shared-kernel.md
# decidiendo (a) shared kernel: libs/shared/tax_id.py consumido por platform y fiscal
# Decisión documentada, acoplamiento consciente.
```

### Incorrecto

```python
# refund/validators.py
def validate_tax_id(tax_id: str) -> bool:
    return len(tax_id) == 11 and tax_id.isdigit()

# payment/utils.py — duplicado silencioso n.º 2
def is_valid_tax_id(tax_id: str) -> bool:
    return len(tax_id) == 11 and tax_id.isdigit()

# kyc/checks.py — duplicado silencioso n.º 3 (disparador de la regla de los tres activado)
def check_cpf(value: str) -> bool:
    if not value.isdigit() or len(value) != 11:
        return False
    return True

# billing/helpers.py — duplicado silencioso n.º 4 con lógica divergente
def cpf_valid(s: str) -> bool:
    return s.isdigit() and len(s) in (11, 14)  # diverge: acepta CNPJ
```

```typescript
// fiscal/calculator.ts (bounded context "fiscal")
function calculateTaxRate(amount: number): number { return amount * 0.18; }

// platform/billing/tax.ts (bounded context "platform") — duplicado cross-context sin ADR
function calculateTaxRate(amount: number): number { return amount * 0.18; }
// PROHIBIDO: misma regla en dos bounded contexts sin decisión arquitectónica registrada.
```

## Validación Automatizada

- **Herramienta:**
  - **JavaScript/TypeScript:** `jscpd` (detección AST + línea) configurado con umbral de 30 líneas; `eslint-plugin-sonarjs` (reglas `no-duplicate-string`, `no-identical-functions`)
  - **Python:** `pylint --disable=all --enable=R0801` (duplicate-code) con `min-similarity-lines=30`; revisión por `warrior-apollo` en PRs identificando reaparición de reglas de dominio
  - **Cross-language y cross-context:** SonarQube duplication detector con tags por bounded context; auditoría por `warrior-athena` en el Gate 2 verificando la presencia de ADR para duplicaciones cross-context
  - **ADR:** validación de existencia en `docs/adr/` cuando el detector señala cross-bounded-context
- **Momento:** pre-commit (jscpd/pylint local), CI en cada PR (full scan), Gate 2 del flujo Issue-Driven (verifica ADR para casos cross-context), auditoría mensual de tendencia
- **Métrica:** 0 PRs mergeados con un nuevo bloque ≥ 30 líneas que represente una regla de dominio reapareciendo en ≥ 3 lugares del mismo bounded context sin extracción; 100% de las duplicaciones cross-bounded-context con ADR correspondiente; tendencia mensual no creciente del índice de duplicación reportado por SonarQube
