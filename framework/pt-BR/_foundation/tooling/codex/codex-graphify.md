# Codex: Graphify — Grafo de Conhecimento de Código

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Engenharia — compreensão de código, mapeamento de impacto e apoio ao design técnico

## Visão Geral

Graphify é uma ferramenta de linha de comando que transforma um repositório em um grafo de conhecimento consultável. A extração de código é feita por AST via tree-sitter, localmente e sem chamadas de API. Documentos, PDFs, imagens e esquemas de banco passam por uma passagem semântica opcional que usa um modelo de linguagem.

O valor para a Guardia é específico: responder perguntas de dependência reversa. O passo 2 de `kata-architecture-brief` produz a tabela de componentes afetados, e essa tabela é a fronteira de escopo consumida por `kata-quality-gate` na verificação de scope creep. Hoje a tabela é montada lendo o repositório de forma ad hoc, o que encontra dependências diretas e não encontra as reversas. O comando `graphify affected` responde "quem quebra se eu alterar isto" com precisão de `arquivo:linha`.

Este Codex documenta a superfície real da versão medida (0.9.33), o modelo de custo aferido em repositório Guardia e as limitações observadas. Não substitui a documentação do fornecedor; registra o que foi verificado.

## Contexto

- **Domínio:** compreensão de bases de código, mapeamento de impacto, apoio ao design técnico
- **Público-alvo:** warriors de engenharia (`warrior-apollo`, `warrior-hephaestus`, `warrior-athena`), desenvolvedores, revisores de PR
- **Atualização:** a cada mudança de versão do Graphify que altere comandos, formato de `graph.json` ou modelo de custo

## Conteúdo

### Princípios

1. **A extração de código é determinística; a semântica não é.** O modo `--code-only` roda AST local, sem chave de API e sem rede. Ele é reproduzível e pode ser usado em automação. A passagem semântica depende de um modelo de linguagem e não oferece a mesma garantia.
2. **O grafo é insumo consultivo, nunca gate de CI.** Quem decide é o agente; o grafo informa. `scripts/validate.py` é determinístico por projeto e não deve passar a depender de uma passagem semântica.
3. **`INFERRED` não significa "gerado por LLM".** A confiança da aresta descreve como a relação foi resolvida, não qual motor a produziu. Ver "Padrões e Convenções".
4. **O grafo envelhece a cada commit.** `graph.json` carrega `built_at_commit`. Consultar um grafo desatualizado sem verificar esse campo produz respostas erradas com aparência de precisão.
5. **A ferramenta é opcional.** Todo consumo do grafo precisa degradar de forma limpa quando o binário está ausente, `graphify.enabled` é `false` ou o grafo está velho.

### Padrões e Convenções

#### Confiança das arestas

| Confiança | Significado | Exemplo de relação |
|-----------|-------------|--------------------|
| `EXTRACTED` | A relação está explícita no código-fonte | `imports`, `calls`, `contains` |
| `INFERRED` | A relação foi resolvida pela heurística do Graphify | `uses` derivado de resolução de tipo |

Medição em `financial-context`: das 49.563 arestas, **45.782 são `EXTRACTED` e 3.781 são `INFERRED`** — e **todas** carregam `_origin: ast`. Ou seja, arestas `INFERRED` aparecem no modo `--code-only`, sem nenhuma chamada de API. O modo continua determinístico; ele apenas não é livre de `INFERRED`.

#### Estrutura de `graph.json`

| Campo | Tipo | Observação |
|-------|------|------------|
| `nodes` | lista | Chaves: `label`, `file_type`, `source_file`, `source_location`, `_origin`, `id`, `community`, `norm_label` |
| `links` | lista | Arestas. Chaves: `relation`, `confidence`, `source_file`, `source_location`, `weight`, `_origin`, `source`, `target`, `confidence_score` |
| `hyperedges` | lista | Vazia na extração medida |
| `built_at_commit` | string | Commit de origem do grafo — base canônica para detecção de desatualização |
| `directed` | booleano | `false` na extração medida |
| `multigraph` | booleano | `false` na extração medida |

A lista de arestas chama-se `links`, não `edges` (convenção D3).

#### Catálogo de comandos verificado

| Comando | Função |
|---------|--------|
| `extract <caminho>` | Extração completa headless (AST + semântica) para CI e scripts |
| `extract --code-only` | Indexa apenas código por AST local; ignora documentos, artigos e imagens |
| `update <caminho>` | Reextrai arquivos de código e atualiza o grafo, sem LLM |
| `affected "X"` | Travessia reversa: nós impactados por X. Aceita `--relation` e `--depth` |
| `explain "X"` | Nó e vizinhança em linguagem simples, com grau e arestas de entrada e saída |
| `path "A" "B"` | Caminho mais curto entre dois nós |
| `query "<pergunta>"` | Travessia BFS do grafo para uma pergunta. `--budget` limita a saída em tokens |
| `god-nodes` | Nós mais conectados (hubs arquiteturais) |
| `check-update <caminho>` | Verifica a flag `needs_update`; seguro para cron |
| `cluster-only <caminho>` | Reexecuta clusterização e regenera o relatório. `--no-label` evita chamadas de LLM |
| `benchmark [graph.json]` | Mede a redução de tokens frente à abordagem de corpus completo |
| `diagnose multigraph` | Reporta risco de colapso de arestas com mesmos extremos |
| `watch <caminho>` | Observa uma pasta e reconstrói o grafo a cada mudança |
| `install --platform P` | Instala o Graphify como skill no diretório de configuração da plataforma |
| `hook install` | Instala hooks git de post-commit e post-checkout |
| `merge-driver` | Driver de merge git que faz união de dois `graph.json` |

`graphify-mcp` é um segundo executável instalado junto. Ele serve o grafo por MCP em transporte `stdio` ou HTTP Streamable, com `--api-key`, `--host`, `--port` e `--stateless`. Pelo `lex-mcp` regra 5 isso é **tier 2 (binário nativo stdio)**; o tier 1 (HTTP remoto hospedado pelo fornecedor) não existe para este fornecedor. A decisão de declarar o servidor em `mcp.servers` é tratada na esteira de instalação, não neste Codex.

#### Backends do modelo de linguagem

`--backend` aceita `gemini`, `kimi`, `claude`, `openai`, `deepseek`, `ollama` e `claude-cli`.

O backend **`claude-cli`** é o caminho recomendado na Guardia. Ele roteia pela CLI do Claude Code instalada localmente, via `claude -p --output-format json`, e autentica com a assinatura Pro/Max existente. Sua tabela de preço é literalmente `{"input": 0.0, "output": 0.0}`: o consumo é cobrado do plano, não de crédito de API pay-as-you-go. Nenhuma chave de API separada é necessária.

Duas consequências práticas: `--max-concurrency` é forçado a 1 para `claude-cli`, e cada invocação carrega o contexto local do Claude Code. Ver "Restrições Técnicas".

### Decisões Vigentes

| Decisão | Situação |
|---------|----------|
| `graph.json` fica fora do versionamento, em cache sob `.ahrena/`, e `graphify-out/` entra no bloco gerenciado do `.gitignore` | Ativa |
| Detecção de desatualização usa `built_at_commit` e `graphify check-update`, sem marcação paralela de SHA | Ativa |
| Consumo do grafo é consultivo; nenhum gate de CI depende de passagem semântica | Ativa |

Sobre a primeira decisão: o fornecedor oferece `graphify merge-driver` justamente para equipes que **versionam** `graph.json`, resolvendo conflitos por união. A Guardia divergiu dessa prática porque um `graph.json` versionado é uma segunda representação da estrutura do código, sujeita a divergir do código real — o que `lex-dry` proíbe. A divergência é deliberada e está registrada aqui.

### Restrições Técnicas

- **Custo real é cota de plano, não dólar.** Na medição semântica, 178.164 tokens de entrada foram consumidos para processar cerca de 18.400 tokens de conteúdo — amplificação de aproximadamente 10 vezes. A causa está no código do próprio Graphify (`llm.py`): CLIs do Claude Code a partir da versão 2.1 não tratam `--system-prompt` como autoridade única e continuam carregando `CLAUDE.md`, `AGENTS.md`, skills e MCP locais em cada invocação. Um `claude -p "reply OK"` trivial na raiz do repositório reportou `total_cost_usd: 0.82` com 82.453 tokens de criação de cache.
- **Mitigação:** invoque o Graphify a partir de um diretório de trabalho neutro, não da raiz de um repositório com `CLAUDE.md` grande. O custo de bootstrap é cobrado por chamada e `claude-cli` não paraleliza.
- **`affected` exige rótulo único.** `graphify affected "EntityId"` falhou com `No unique node match for EntityId`. Rótulos ambíguos precisam do ID qualificado do nó.
- **SQL exige extra de instalação.** Arquivos `.sql` não contribuem para o grafo sem `tree_sitter_sql`. Instale com `pip install "graphifyy[sql]"` (issue upstream #1745). Relevante para contextos financeiros e fiscais.
- **Alguns arquivos JSON produzem zero nós.** Na medição, 22 arquivos não geraram nós, entre eles `ahrena.json`, `figma.json`, `github.json`, `notion.json` e `slack.json` (issue upstream #1666).
- **Grafos grandes exigem `--no-viz`.** Acima de aproximadamente 5.000 nós, a geração de `graph.html` deve ser desativada.
- **O grafo medido é não direcionado** (`directed: false`), o que afeta a interpretação de travessia reversa. Use `diagnose multigraph` para avaliar risco de colapso de arestas.
- **`.gitignore` é respeitado por padrão.** Na medição, 1.707 arquivos foram extraídos de 4.168 versionados, e as dependências de ambiente virtual ficaram corretamente fora. `--no-gitignore` inverte esse comportamento.

#### Modelo de custo aferido

Medição em `financial-context` no commit `3b1c756`, Graphify 0.9.33, 16 workers de AST.

| | `--code-only` | Semântico (`--backend claude-cli`) |
|---|---|---|
| Tempo de parede | 359 s para 1.707 arquivos (**0,21 s por arquivo**) | 322 s para 22 documentos (**14,6 s por arquivo**) |
| Nós / arestas | 20.882 / 49.563 | 36 / 163 |
| Comunidades | 738 | não aplicável (`--no-cluster`) |
| Tokens | 0 | 178.164 entrada / 40.517 saída |
| Chave de API | não exigida | não exigida (CLI local + assinatura) |
| Custo de API reportado | US$ 0,00 | US$ 0,0000 (cobrado do plano) |
| Concorrência | 16 workers | forçada a 1 |

`graphify benchmark` sobre o grafo de código: corpus de 1.044.100 palavras, cerca de 1.392.133 tokens na abordagem ingênua, contra aproximadamente 12.841 tokens por consulta — **redução de 108,4 vezes**. A faixa por pergunta foi de 83,2 vezes ("what connects the data layer to the api") a 171,0 vezes ("how does authentication work").

## Diagrama de Referência

```
                    ┌─────────────────────────┐
   repositório ───► │ extract --code-only     │  AST local, tree-sitter
                    │ (determinístico, grátis)│  0 chamadas de API
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
   docs, PDFs ────► │ passagem semântica      │  --backend claude-cli
   imagens          │ (opcional, cota de plano)│  concorrência forçada a 1
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ graph.json              │
                    │  nodes / links          │
                    │  built_at_commit  ──────┼──► base de desatualização
                    └───────────┬─────────────┘
                                │
        ┌───────────────┬───────┴───────┬────────────────┐
        ▼               ▼               ▼                ▼
    affected "X"    explain "X"    path "A" "B"     graphify-mcp
   (impacto        (nó e         (ligação entre    (stdio ou HTTP)
    reverso)        vizinhança)    dois nós)
```

## Glossário

| Termo | Definição |
|-------|-----------|
| AST | Árvore sintática abstrata. Base da extração determinística de código, via tree-sitter |
| `EXTRACTED` | Aresta explícita no código-fonte |
| `INFERRED` | Aresta resolvida por heurística do Graphify, não necessariamente por modelo de linguagem |
| Comunidade | Agrupamento de nós detectado pelo algoritmo de Leiden; aproxima a noção de subsistema |
| God node | Nó de alta conectividade; hub arquitetural |
| `built_at_commit` | Commit a partir do qual o grafo foi construído |
| Passagem semântica | Etapa opcional que usa modelo de linguagem para documentos, PDFs e imagens |
| `claude-cli` | Backend que roteia pela CLI local do Claude Code e cobra da assinatura, não de crédito de API |

## Referências

- `kata-codebase-graph` — procedimento operacional que aplica este Codex
- `cry-graph` — atalho de invocação
- `kata-architecture-brief` — consumidor do grafo no passo 2 (tabela de componentes afetados)
- `kata-quality-gate` — consome a fronteira de escopo na verificação de scope creep
- `lex-mcp` — regra 1 (preferência por ferramenta MCP) e regra 5 (hierarquia de transporte)
- `lex-dry` — fundamento da decisão de não versionar `graph.json`
- `codex-git-spice` — precedente de Codex para ferramenta externa de linha de comando
- Repositório do fornecedor: https://github.com/Graphify-Labs/graphify
