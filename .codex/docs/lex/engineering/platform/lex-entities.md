# Lexis: Estrutura Base de Entidades

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Plataforma Guardia — modelo de entidades

## Lei

> **Toda entidade persistente e rastreável da plataforma Guardia DEVE seguir a estrutura base definida na especificação de Entidades do Hub e referenciada no Codex de entidades (entity_id, entity_type, version, history, created_at, updated_at, discarded_at e demais propriedades obrigatórias).**

## Exemplos

### Correto

Entidade com entity_id (UUID v7), entity_type, created_at, updated_at, version, e demais propriedades da spec; history omitido em respostas temporais; endpoint de histórico disponível quando aplicável.

### Incorreto

Recurso de API ou evento que represente entidade persistente sem entity_id, sem version ou sem timestamps (created_at/updated_at) conforme a especificação de Entidades.

## Validação Automatizada

- **Ferramenta:** revisão de design e código contra codex-entities; validação de contrato (OpenAPI/schema) quando disponível.
- **Momento:** revisão de PR e design de novos recursos.
- **Métrica:** 0 entidades persistentes fora da estrutura base, salvo exceções documentadas em PDR.
