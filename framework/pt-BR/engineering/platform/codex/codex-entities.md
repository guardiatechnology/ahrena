# Codex: Modelo de Entidades da Plataforma Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — estrutura base de entidades

## Visão Geral

Este Codex descreve o modelo estrutural mínimo que todas as entidades da plataforma Guardia devem seguir. Objetiva consistência entre serviços, interoperabilidade entre domínios e aderência a requisitos de segurança, rastreabilidade e conformidade (Compliance by Design). Aplica-se a APIs, bases de dados, eventos de domínio e integrações externas.

## Contexto

- **Domínio:** modelo de entidades persistentes e rastreáveis da plataforma Guardia.
- **Público-alvo:** implementadores, arquitetos e agentes de IA que modelam ou consomem entidades.
- **Atualização:** quando a especificação de Entidades no Hub for alterada ou quando um PDR aprovar exceção.

## Conteúdo

### Estrutura base obrigatória

| Propriedade | Tipo | Obrigatório | Descrição |
|-------------|------|-------------|-----------|
| entity_id | UUID v7 | Sim | Identificador único da entidade, imutável, gerado pelo sistema. RFC 9562 (ordenação temporal). |
| entity_type | string | Sim | Tipo de entidade; deve pertencer a lista controlada conhecida pelo sistema. |
| external_entity_id | string | Não | Identificador no sistema externo; máx. 36 caracteres; único por entity_type quando presente. |
| created_at | datetime | Sim | Data e hora de criação em UTC (RFC 3339); gerado na criação; não alterável. |
| updated_at | datetime | Sim | Data e hora da última atualização em UTC; atualizado a cada modificação; na criação = created_at; no descarte = discarded_at. |
| discarded_at | datetime | Não | Soft delete; quando preenchido, entidade permanece para rastreabilidade. |
| metadata | JSON Object | Não | Chaves e valores string; ideal ≤ 4KB, máx. 10KB; atualizações via JSON Merge Patch (RFC 7386); não conter dados sensíveis sem previsão legal. |
| version | integer | Sim | Inicia em 1; incrementado com updated_at; nunca reiniciado (mesmo após restauração). Conflito de versão: última vence. |
| history | array | Não | Snapshots de versões anteriores; últimas 10 versões, até 365 dias; auditoria e rollback. Omitido em respostas temporais e eventos; disponível em endpoint api/v1/<entity_type>/<entity_id>/history. |

### Princípios

1. **Identificação única:** entity_id UUID v7 garante unicidade global e ordenação temporal.
2. **Rastreabilidade temporal:** created_at, updated_at e discarded_at permitem auditoria e sincronização.
3. **Integridade e concorrência:** version permite controle de concorrência e detecção de conflitos.
4. **Histórico e reversibilidade:** history preserva últimas versões para auditoria e rollback.
5. **Interoperabilidade:** external_entity_id e metadata permitem integração com sistemas externos.

### Quando aplicar

Este modelo DEVE ser adotado sempre que:

- Um novo recurso de domínio for modelado;
- APIs forem expostas internamente ou externamente;
- Eventos de domínio forem gerados;
- Dados precisarem de unicidade, rastreabilidade, reversibilidade ou interoperabilidade.

Exceções DEVEM ser justificadas e aprovadas pelo Comitê Diretivo e registradas em PDR.

### Restrições técnicas

- entity_id: UUID v7 (RFC 9562).
- Timestamps: UTC, RFC 3339.
- metadata: apenas chave e valor string; atualização via JSON Merge Patch (RFC 7386).
- history: omitido de create/update/delete/get por padrão; fornecido somente no endpoint de histórico.

## Glossário

| Termo | Definição |
|-------|------------|
| entity_id | Identificador único global da entidade (UUID v7). |
| entity_type | Tipo catalogado da entidade no sistema. |
| soft delete | Descarte lógico via discarded_at; entidade mantida para rastreabilidade. |
| history | Array de snapshots de versões anteriores para auditoria. |

## Referências

- [Especificação de Entidades — Hub Guardia](https://hub.guardia.finance/docs/specifications/entities/)
- RFC 9562: UUID Version 7
- RFC 7386: JSON Merge Patch
- RFC 3339: Date and Time on the Internet: Timestamps
