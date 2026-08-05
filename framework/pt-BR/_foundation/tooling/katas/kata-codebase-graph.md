# Kata: Grafo de Conhecimento da Base de Código

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — construção, atualização e consulta do grafo de código para mapeamento de impacto

## Objetivo

Construir ou atualizar o grafo de conhecimento de um repositório com Graphify e consultá-lo para produzir a tabela de componentes afetados no formato consumido por `kata-architecture-brief`. O procedimento entrega dependências diretas **e reversas**, que é a lacuna da leitura ad hoc do repositório.

O grafo é insumo consultivo. Este Kata nunca bloqueia um fluxo: quando o Graphify está ausente, desabilitado ou o grafo está desatualizado, ele registra a indisponibilidade e devolve o controle ao agente chamador.

## Quando Usar

- No passo 2 de `kata-architecture-brief`, ao mapear os componentes afetados por um conjunto de critérios de aceite
- Na verificação de scope creep de `kata-quality-gate`, ao comparar o diff do PR com a fronteira de escopo declarada
- Ao avaliar o raio de impacto de uma mudança em contrato público, antes de alterá-lo
- Ao investigar uma base de código desconhecida e precisar identificar hubs arquiteturais

Não use quando a resposta exigir uma única leitura de arquivo já conhecido. O custo de construção do grafo não se justifica.

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Caminho do repositório | Sim | Raiz do repositório a indexar |
| Nós de interesse | Não | Rótulos ou IDs a consultar (`affected`, `explain`, `path`) |
| Critérios de aceite | Não | Necessários quando a saída alimenta a tabela de componentes de `kata-architecture-brief` |
| Modo de extração | Não | `code-only` (padrão) ou semântico. Ver `codex-graphify` |

## Workflow

Copie este checklist e acompanhe o progresso:

```
Progresso:
- [ ] 1. Verificar habilitação e disponibilidade do binário
- [ ] 2. Construir ou atualizar o grafo
- [ ] 3. Verificar desatualização via built_at_commit
- [ ] 4. Consultar o grafo
- [ ] 5. Montar a tabela de componentes afetados
- [ ] 6. Validação final
```

### Passo 1: Verificar habilitação e disponibilidade do binário

1. Leia `graphify.enabled` em `.ahrena/.directives`. Se for `false`, registre "grafo desabilitado por diretriz" e encerre o Kata sem erro.
2. Verifique se o binário existe no PATH. Se ausente, registre "Graphify não instalado" e encerre sem erro — o agente chamador segue com o comportamento anterior.
3. Não instale o binário dentro deste Kata. A instalação é responsabilidade da esteira de instalação do framework.

### Passo 2: Construir ou atualizar o grafo

1. Se não existir grafo para o repositório, execute a extração determinística:

   ```
   graphify extract <caminho> --code-only --out <cache>
   ```

   O modo `--code-only` roda AST local, não exige chave de API e não faz chamadas de rede.

2. Se já existir grafo, prefira a atualização incremental:

   ```
   graphify update <caminho>
   ```

3. Execute a passagem semântica **apenas** quando a pergunta depender de documentos, PDFs ou imagens. Nesse caso use `--backend claude-cli`, que cobra da assinatura Pro/Max e não exige chave de API separada. Invoque a partir de um diretório de trabalho neutro: cada chamada carrega o contexto local do Claude Code, e a concorrência é forçada a 1. Ver "Restrições Técnicas" em `codex-graphify`.
4. Em grafos acima de aproximadamente 5.000 nós, desative a visualização com `--no-viz`.

### Passo 3: Verificar desatualização via `built_at_commit`

1. Leia o campo `built_at_commit` de `graph.json`.
2. Compare com o `HEAD` atual do repositório.
3. Se divergirem, execute `graphify check-update <caminho>` e decida:
   - divergência pequena e a consulta não toca os arquivos alterados: prossiga e **declare** que o grafo está no commit anterior;
   - divergência relevante: atualize com `graphify update` antes de consultar.
4. Nunca apresente resultado de grafo desatualizado sem declarar o commit de origem. Uma resposta velha com aparência de precisão é pior do que a ausência de resposta.

### Passo 4: Consultar o grafo

Escolha o comando pela pergunta:

| Pergunta | Comando |
|----------|---------|
| Quem quebra se eu alterar X? | `graphify affected "X" --depth N` |
| O que é X e com o que se conecta? | `graphify explain "X"` |
| Como A se liga a B? | `graphify path "A" "B"` |
| Quais são os hubs arquiteturais? | `graphify god-nodes --top N` |
| Pergunta aberta sobre a base | `graphify query "<pergunta>" --budget N` |

1. `affected` exige rótulo único. Se retornar `No unique node match`, obtenha o ID qualificado do nó com `explain` ou inspecionando `graph.json`, e repita com o ID.
2. Registre a confiança das arestas que sustentam a resposta. `EXTRACTED` é relação explícita no código; `INFERRED` é resolução por heurística do Graphify — e ocorre também no modo `--code-only`.
3. Use `--budget` em `query` para limitar a saída em tokens.

### Passo 5: Montar a tabela de componentes afetados

Consolide o resultado no formato consumido por `kata-architecture-brief`:

| Componente | Tipo | Ação | ACs cobertos |
|---|---|---|---|

1. Cada linha derivada do grafo deve trazer a origem `arquivo:linha` fornecida pelo Graphify.
2. Separe explicitamente os componentes encontrados por travessia **reversa** — são justamente os que a leitura ad hoc não encontraria.
3. Marque as linhas sustentadas apenas por arestas `INFERRED`. Elas exigem confirmação humana antes de virar fronteira de escopo.
4. Não inclua no escopo componentes que apareceram só no grafo e não têm relação com nenhum critério de aceite.

### Passo 6: Validação Final

Antes de entregar a saída, verifique:

- [ ] O commit de origem do grafo (`built_at_commit`) está declarado na saída
- [ ] Componentes vindos de travessia reversa estão identificados como tais
- [ ] Linhas sustentadas apenas por arestas `INFERRED` estão marcadas
- [ ] Toda linha da tabela referencia ao menos um critério de aceite
- [ ] Se o grafo estava indisponível ou desatualizado, isso está declarado de forma explícita

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Tabela de componentes afetados | Markdown | Passo 2 de `kata-architecture-brief` |
| Declaração de procedência | Markdown | Mesma saída: commit de origem, modo de extração, confiança das arestas |
| Cache do grafo | JSON | `.ahrena/` (fora do versionamento) |

## Exemplo de Execução

### Input de Exemplo

```
Repositório: financial-context
Nó de interesse: VersionSeal
Pergunta: quem é impactado se eu alterar VersionSeal?
```

### Output de Exemplo

```
Grafo: built_at_commit 3b1c756 (igual ao HEAD) · modo --code-only
20.882 nós · 49.563 arestas · 45.782 EXTRACTED / 3.781 INFERRED

graphify affected "VersionSeal" --depth 2
Relações percorridas: calls, references, imports, uses, inherits, implements (+7)

Impacto reverso:
| Componente | Tipo | Ação | ACs cobertos |
|---|---|---|---|
| components/commons/application/services/_lifecycle_test.py:L49 | teste | revisar | AC-1 |
| components/commons/application/services/archive_entity_service_test.py:L35 | teste | revisar | AC-1 |
| components/commons/infra/data/contracts/version_record.py:L39 | módulo | avaliar (INFERRED) | AC-1 |

VersionSeal: grau 238, comunidade 1, definido em
components/commons/infra/data/version/seal.py:L34.

Nota: version_record.py entra apenas por aresta INFERRED (relação `uses`
resolvida por heurística). Confirmar antes de tratar como fronteira de escopo.
```

## Restrições

- Nunca bloqueie o fluxo chamador. Ausência do binário, `graphify.enabled: false` ou grafo desatualizado resultam em registro explícito e devolução do controle, não em erro
- Nunca apresente resultado sem declarar `built_at_commit` e o modo de extração
- Nunca trate aresta `INFERRED` como fato confirmado ao definir fronteira de escopo
- Nunca versione `graph.json`. O cache fica sob `.ahrena/`, fora do versionamento, conforme decisão registrada em `codex-graphify`
- Nunca execute a passagem semântica quando a pergunta é respondível por código. O modo `--code-only` é gratuito e determinístico
- Nunca instale o binário dentro deste Kata
- Consulte `codex-graphify` antes de usar qualquer comando não listado no passo 4
