# Lexis: Regras para Traduzir para Inglês

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Tradução de documentação técnica para inglês (en)

## Propósito

Esta Lexis define as regras específicas para traduzir documentação técnica **para Inglês (en)**. Complementa a `lex-language` (regras transversais) com particularidades linguísticas e estilísticas do inglês técnico.

## Lei

> **Toda tradução para inglês DEVE seguir as regras transversais de `lex-language` E as regras específicas definidas nesta Lexis.**

## Regras

### 1. Variante do inglês

Usar **American English** como padrão. Manter consistência ao longo de todo o documento:
- "color" (não "colour")
- "organization" (não "organisation")
- "analyze" (não "analyse")

### 2. Voz e tempo verbal

Usar **voz ativa** e **presente do indicativo** em instruções:
- "The agent reads the directives" (não "The directives are read by the agent")
- "Run the command" (não "The command should be run")
- "Create the file" (não "The file is to be created")

### 3. Concisão

Priorizar **frases curtas e diretas**:
- Eliminar redundância ("in order to" → "to")
- Evitar circunlóquios ("it is important to note that" → omitir)
- Uma ideia por frase quando possível

### 4. Terminologia industry-standard

Usar terminologia padrão da indústria de tecnologia:

| Preferir | Evitar |
|----------|--------|
| execute | perform/carry out |
| create | generate/produce (quando genérico) |
| delete | remove/eliminate (quando ação técnica) |
| configure | set up (em contexto formal) |
| validate | verify/check (quando conformidade) |

### 5. Tom

Tom **profissional-neutro**: claro, preciso, sem linguagem coloquial.
- Evitar contrações em documentação formal ("do not" em vez de "don't")
- Evitar gírias e expressões informais
- Manter consistência de registro ao longo do documento

### 6. Verbos modais (RFC 2119)

Manter a terminologia RFC 2119 para verbos modais:

| Modal | Significado |
|-------|-------------|
| MUST | Obrigatório — sem exceção |
| MUST NOT | Proibido — sem exceção |
| SHOULD | Recomendado — exceções justificadas |
| SHOULD NOT | Não recomendado — exceções justificadas |
| MAY | Opcional |

### 7. Armadilhas comuns ao traduzir de pt-BR/es

| Erro comum | Correto |
|------------|---------|
| "realize" (≠ realizar) | "perform" ou "carry out" |
| "actually" (≠ atualmente) | "currently" |
| "pretend" (≠ pretender) | "intend" |
| "library" (≠ livraria) | "bookstore" (livraria) / "library" (biblioteca) |

## Abrangência

- **Aplica-se a:** toda tradução cujo idioma-alvo seja inglês (en)
- **Agentes vinculados:** `warrior-translator` e qualquer agente que traduza para inglês
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Inconsistent translation:** text that does not follow the rules of this Lexis may mix voice, use false cognates (e.g. "realize" for "perform"), or deviate from American English.
2. **Rejection in review:** translations to English that violate the rules must be corrected before being accepted into the framework.
3. **Remediation:** the agent must consult `codex-language-en` and this Lexis and reapply the rules to the translated text.

## Exemplos

### Correto

- "The agent **MUST** consult the .directives." (active voice, MUST per RFC 2119)
- "Use the defined workflow." (concise; "workflow" kept in English when standard)

### Incorreto

- "The directives are read by the agent" (prefer active: "The agent reads the directives")
- "Actually, the user must perform the action" ("actually" ≠ "atualmente"; use "Currently" if that is the meaning)
- "The library sells books" when meaning "bookstore" (library = biblioteca; bookstore = livraria)

## Referências

- `lex-language` — Regras transversais (esta Lexis complementa)
- `codex-language-en` — Guia detalhado para tradução para inglês
