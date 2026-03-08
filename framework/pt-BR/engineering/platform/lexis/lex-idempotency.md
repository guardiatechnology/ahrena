# Lexis: Idempotência em Operações que Modificam Estado

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Plataforma Guardia — APIs e eventos

## Propósito

Garantir que operações que modificam estado (APIs e eventos) na plataforma Guardia sejam idempotentes, preservando consistência de dados e confiabilidade em ambientes com falhas de rede, timeouts ou retries. Evitar duplicação de transações, inconsistências de estado e efeitos colaterais indesejados.

## Lei

> **Operações que modificam estado (APIs e eventos) na plataforma Guardia DEVEM ser idempotentes conforme a especificação de Idempotência do Hub; endpoints que modificam estado (POST, PATCH, etc.) DEVEM exigir e validar o header Idempotency-Key; eventos publicados DEVEM incluir idempotencykey e consumidores DEVEM registrar e deduplicar por chave e hash.**

## Abrangência

- **Aplica-se a:** endpoints HTTP de mutação (POST, PATCH, PUT) e publicação/consumo de eventos na plataforma Guardia.
- **Agentes vinculados:** todos os implementadores de APIs e processadores de eventos.
- **Exceções:** Nenhuma para operações que modificam estado; operações puramente de leitura (GET, eventos de consulta) não são abrangidas.

## Consequências de Violação

1. **Duplicação:** transações ou efeitos aplicados mais de uma vez.
2. **Inconsistência:** estado divergente entre consumidores e provedores.
3. **Remediação:** implementar idempotência conforme spec e reprocessar ou corrigir dados afetados.

## Exemplos

### Correto

Endpoint POST com Idempotency-Key obrigatório; retorno 400 quando ausente; 409 quando mesma chave com payload diferente; evento com idempotencykey no payload; consumidor ignora evento já processado e retorna ACK.

### Incorreto

Endpoint de mutação sem exigência de Idempotency-Key; evento sem idempotencykey; consumidor reexecutando lógica para mesma chave e hash.

## Validação Automatizada

- **Ferramenta:** revisão de contrato (OpenAPI) e código; testes de retry com mesma chave.
- **Momento:** revisão de PR e testes de integração.
- **Métrica:** 0 endpoints de mutação sem Idempotency-Key; 0 eventos sem idempotencykey quando a spec se aplicar.

## Referências

- [Especificação de Idempotência — Hub Guardia](https://hub.guardia.finance/docs/specifications/idempotency/)
- codex-idempotency (engineering/platform)
- RFC 9562 (UUID); Draft RFC Idempotency-Key Header
