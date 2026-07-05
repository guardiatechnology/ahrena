# Codex: Idempotência em APIs e Eventos da Plataforma Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — idempotência

## Visão Geral

Este Codex descreve as regras de idempotência para operações que modificam estado na plataforma Guardia (APIs e eventos). Objetiva consistência de dados, confiabilidade em retries e deduplicação, em conformidade com a especificação de Idempotência do Hub.

## Contexto

- **Domínio:** idempotência em APIs REST e em eventos (publicação e consumo).
- **Público-alvo:** implementadores de APIs e processadores de eventos.
- **Atualização:** quando a especificação de Idempotência no Hub for alterada.

## Conteúdo

### Princípios fundamentais

1. **Mesmo resultado:** operações idempotentes DEVEM produzir o mesmo resultado para múltiplas execuções com os mesmos parâmetros.
2. **Chave + hash:** a verificação NÃO DEVE depender só da chave; DEVE considerar a combinação da chave e do hash do payload (requisição ou evento). Algoritmo do hash: SHA-256.
3. **Chave fornecida pelo cliente:** a chave de idempotência DEVE ser fornecida pelo cliente; DEVE ser única por operação e escopo de rota; DEVE ser UUID (RFC 9562).
4. **Armazenamento:** estado de idempotência DEVE ser armazenado em cache distribuído e resiliente; retenção mínima 2 horas, máxima 24 horas.
5. **Segurança e auditoria:** estado armazenado de forma segura, acesso auditável; tentativas maliciosas de repetição monitoradas e mitigadas; logs com identificadores rastreáveis.

### Pontos de enforcement (edge interceptors)

A idempotência é aplicada no **edge interceptor** de cada borda de entrada que modifica estado — um único interceptor de fronteira por borda, não wiring por-handler nem por-service. Cada interceptor resolve a chave a partir do próprio adapter e delega ao núcleo de idempotência compartilhado; a representação de replay é escolhida por borda.

| Borda | Interceptor | Resolução da chave | Representação de replay |
|-------|-------------|--------------------|-------------------------|
| REST | interceptor de rota/request em POST/PATCH/PUT | header `Idempotency-Key` do cliente (passthrough) | snapshot da resposta HTTP armazenado |
| Agente | interceptor de tool-dispatch em tools que modificam estado | determinística — SHA-256 do input canônico resolvido (content) | modelo de resultado armazenado |
| Worker/evento | interceptor de message-dispatch nos consumidores | `idempotencykey` da mensagem | modelo de resultado armazenado / ACK |

O interceptor é o único ponto de enforcement: qualquer borda que modifique estado sem um é uma lacuna. Qualquer nova borda de entrada que modifique estado DEVE passar pelo seu próprio edge interceptor ou ser documentada como exceção.

A borda de agente deriva a chave de forma determinística em vez de exigir um UUID fornecido pelo cliente (princípio 3): o chamador é um LLM, não um cliente com token de retry. Esse desvio DEVE ser registrado em um ADR pelo projeto consumidor.

### Implementação em APIs

- Endpoints que modificam estado (POST, PATCH) DEVEM ser idempotentes.
- O header `Idempotency-Key` DEVE ser obrigatório nesses endpoints.
- Quando não informado: retornar `400 BAD REQUEST`, código `ERR400_MISSING_OR_MALFORMED_HEADER`, motivo `IDEMPOTENCY_KEY_REQUIRED`.
- A resposta DEVE incluir o mesmo header `Idempotency-Key` recebido e o `Content-Digest` com o hash do payload.
- A chave DEVE ser propagada por todas as camadas (incluindo eventos de domínio e webhooks).
- Primeira execução: armazenar resultado, hash do payload, chave e timestamp.
- Requisições subsequentes com mesma chave e mesmo hash: retornar resultado original armazenado; NÃO reexecutar; incluir header `Last-Modified` com data original.
- Quando a chave já estiver registrada mas o hash do payload for diferente: rejeitar com `409 CONFLICT`, código `ERR409_SERVER_STATE_CONFLICT`, motivo `CONFLICTING_IDEMPOTENT_REQUEST`.

### Implementação em eventos

- Todos os eventos publicados pela plataforma DEVEM ser idempotentes.
- O campo `idempotencykey` DEVE estar presente no payload (conforme spec de eventos).
- O consumidor DEVE registrar o estado de execução com base na chave e no hash do evento.
- O evento é único por `idempotencykey`.
- Se o evento já tiver sido processado: ignorar, retornar ACK ao broker; NÃO reexecutar a lógica; a execução original PODE ser registrada em logs para auditoria.

### Quando usar

- Em qualquer operação que modifique o estado do sistema (APIs e eventos).
- Em fluxos críticos (criação de transações, usuários, contratos).
- Em sistemas sujeitos a falhas de rede, replicações ou timeouts.
- Sempre que o cliente ou consumidor tiver política de retry ativa.

### Quando não usar

- Em operações puramente de leitura (GET, eventos de consulta).
- Em fluxos que não geram efeitos colaterais.
- Em chamadas que por definição devem sempre produzir resultado novo (ex.: geração de UUID aleatório, polling).

### Comportamentos esperados

#### APIs

- **Primeira requisição (chave nova):** executar a operação; armazenar resultado, hash do payload, chave e timestamp; retornar resposta com status apropriado (ex.: 201); incluir header `Idempotency-Key` e `Content-Digest`.
- **Requisição repetida (mesma chave e mesmo hash):** NÃO reexecutar; retornar o resultado original armazenado; incluir header `Last-Modified` com a data da primeira execução; status idêntico ao da primeira resposta.
- **Requisição com mesma chave e hash diferente:** rejeitar com `409 CONFLICT`; código `ERR409_SERVER_STATE_CONFLICT`; motivo `CONFLICTING_IDEMPOTENT_REQUEST`; NÃO alterar estado nem sobrescrever o resultado anterior.

#### Eventos

- **Primeiro recebimento de um evento (idempotencykey nova):** processar normalmente; registrar chave e hash; enviar ACK ao broker.
- **Evento duplicado (mesma idempotencykey já processada):** ignorar o processamento; retornar ACK ao broker; NÃO reexecutar a lógica; a execução original PODE ser registrada em logs para auditoria.

### Dependências técnicas

- **Cache distribuído:** sistema de cache resiliente para armazenar estado de idempotência (chave, hash, resultado, timestamp).
- **Hash:** algoritmo SHA-256 para o hash do payload (requisição ou corpo do evento).
- **Roteamento:** chave única por operação e escopo de rota; propagação da chave em todas as camadas (APIs, eventos, webhooks).

### Segurança e compliance

- Estado de idempotência armazenado de forma segura; acesso auditável.
- Tentativas maliciosas de repetição (mesma chave, payloads distintos) monitoradas e mitigadas (ex.: rate limit, alertas).
- Logs com identificadores rastreáveis (chave, correlation_id) para conformidade e investigação.
- Retenção do estado entre 2 e 24 horas; não armazenar dados sensíveis no cache de idempotência além do estritamente necessário.

## Referências

- Draft RFC The Idempotency-Key Header Field
- RFC 9562 (UUID)
