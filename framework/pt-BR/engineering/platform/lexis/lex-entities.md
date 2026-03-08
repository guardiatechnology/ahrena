# Lexis: Estrutura Base de Entidades

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Plataforma Guardia — modelo de entidades

## Propósito

Garantir que toda entidade persistente e rastreável da plataforma Guardia siga um modelo estrutural mínimo, assegurando consistência entre serviços, interoperabilidade entre domínios e aderência a requisitos de segurança, rastreabilidade e conformidade (LGPD, SOC 2, ISO 27001). Exceções sem esse padrão geram lacunas de auditoria e quebra de interoperabilidade.

## Lei

> **Toda entidade persistente e rastreável da plataforma Guardia DEVE seguir a estrutura base definida na especificação de Entidades do Hub e referenciada no Codex de entidades (entity_id, entity_type, version, history, created_at, updated_at, discarded_at e demais propriedades obrigatórias).**

## Abrangência

- **Aplica-se a:** modelagem e exposição de entidades em APIs, bases de dados, eventos de domínio e integrações da plataforma Guardia.
- **Agentes vinculados:** todos os agentes e implementadores que criem ou alterem entidades na plataforma.
- **Exceções:** Exceções somente quando justificadas e aprovadas pelo Comitê Diretivo e registradas em Registro de Decisão de Produto (PDR).

## Consequências de Violação

1. **Inconsistência:** serviços e consumidores não conseguem assumir a estrutura mínima das entidades.
2. **Auditoria:** lacunas em rastreabilidade e histórico comprometem conformidade.
3. **Remediação:** entidades fora do padrão devem ser migradas ou documentadas em PDR antes de serem aceitas.

## Exemplos

### Correto

Entidade com entity_id (UUID v7), entity_type, created_at, updated_at, version, e demais propriedades da spec; history omitido em respostas temporais; endpoint de histórico disponível quando aplicável.

### Incorreto

Recurso de API ou evento que represente entidade persistente sem entity_id, sem version ou sem timestamps (created_at/updated_at) conforme a especificação de Entidades.

## Validação Automatizada

- **Ferramenta:** revisão de design e código contra codex-entities; validação de contrato (OpenAPI/schema) quando disponível.
- **Momento:** revisão de PR e design de novos recursos.
- **Métrica:** 0 entidades persistentes fora da estrutura base, salvo exceções documentadas em PDR.

## Referências

- codex-entities (engineering/platform) (engineering/platform)
- RFC 9562 (UUID v7), RFC 7386 (JSON Merge Patch), RFC 3339 (timestamps)
