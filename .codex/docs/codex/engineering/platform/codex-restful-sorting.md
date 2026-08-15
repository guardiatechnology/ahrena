# Codex: Ordenação em APIs RESTful

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — APIs REST — ordenação

## Conteúdo

- Ordenação limitada a propriedades temporais: **created_at**, **updated_at**, **reference_at** (outros campos somente se documentados no contrato e com índice).
- Uso de índices para evitar full scan; ordenação **estável** (critério secundário ex.: entity_id) para que paginação não duplique ou pule itens.
- Parâmetros: **order_by** (default created_at), **sort** (default asc). Ausência → created_at asc.
- Valores não permitidos em order_by ou sort → 400 Bad Request (ERR400_INVALID_PARAMETER, ORDER_BY_INVALID, SORT_INVALID).
- Em cenários com **partitionamento** (ex.: por tenant), a ordenação DEVE respeitar o escopo da partição.
- Exceção: ordenação fixa por regra de negócio pode omitir order_by se justificada e registrada em PDR (Registro de Decisão de Produto).
