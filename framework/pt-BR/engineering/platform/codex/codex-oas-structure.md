# Codex: Ordem de Operações em Paths OpenAPI

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — estrutura de paths em especificações OpenAPI 3.x

## Visão Geral

Este Codex define a ordem em que os métodos HTTP devem aparecer em cada path na especificação OpenAPI (OAS 3.x), para consistência e legibilidade. Todo artefato que gera ou edita especificações OAS na plataforma Guardia deve respeitar essa ordem ao documentar as operações de um path.

## Contexto

- **Domínio:** Estrutura de paths e operações em especificações OpenAPI 3.x.
- **Público-alvo:** Agentes e procedimentos que produzem ou mantêm specs OAS (kata-api-design-oas, Warrior Daedalus).
- **Atualização:** Quando a convenção da plataforma para ordem de métodos for alterada.

## Conteúdo

### Ordem obrigatória das operações

Em cada entrada de `paths` na especificação OpenAPI (YAML ou JSON), as operações (métodos HTTP) **DEVEM** ser listadas na seguinte ordem:

| Ordem | Método HTTP | Uso típico |
|:-----:|-------------|------------|
| 1 | POST | Criação de recurso |
| 2 | GET | Leitura (um ou lista) |
| 3 | PUT | Substituição completa |
| 4 | PATCH | Atualização parcial |
| 5 | DELETE | Exclusão (lógica ou física) |

Ao documentar um path (ex.: `/v1/transactions`), inclua apenas as operações que o endpoint expõe, **mantendo essa sequência**. Exemplo: se o path tem apenas POST, GET e PATCH, eles devem aparecer nessa ordem no YAML/JSON.

### Restrições técnicas

- Ao gerar ou editar uma especificação OpenAPI, o agente **DEVE** ordenar as operações de cada path conforme a tabela acima.
- Métodos não utilizados no path podem ser omitidos; os que forem documentados **DEVEM** seguir a sequência POST → GET → PUT → PATCH → DELETE.
- A ordem aplica-se ao documento OAS (chaves `post`, `get`, `put`, `patch`, `delete` em cada path), não à ordem de definição dos paths em si.

## Glossário

| Termo | Definição |
|-------|-----------|
| path | Rota de URL na spec OAS (ex.: `/v1/transactions`, `/v1/transactions/{entity_id}`) |
| operação | Método HTTP (post, get, put, patch, delete) documentado sob um path |

## Referências

- codex-restful-apis — Índice das APIs RESTful da Guardia
- [OpenAPI Specification 3.x](https://spec.openapis.org/oas/v3.0.3)
