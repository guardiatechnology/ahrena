# Cry: Consultar o Grafo da Base de Código

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Engenharia — consulta rápida ao grafo de conhecimento de código

## Descrição

Atalho para construir, atualizar ou consultar o grafo de conhecimento de um repositório. O comando invoca `kata-codebase-graph`, que executa o procedimento completo: verifica habilitação, constrói ou atualiza o grafo, checa desatualização e devolve a resposta com procedência declarada.

O uso mais frequente é responder "quem quebra se eu alterar isto", que é a pergunta de dependência reversa que a leitura ad hoc do repositório não responde.

## Uso

```
/cry-graph [pergunta ou nó] [--repo <caminho>] [--depth N] [--refresh]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `pergunta ou nó` | Não | Rótulo do nó a analisar ou pergunta aberta. Sem argumento, o comando constrói ou atualiza o grafo e reporta hubs | `VersionSeal` |
| `--repo` | Não | Caminho do repositório. Padrão: repositório atual | `--repo ../financial-context` |
| `--depth` | Não | Profundidade da travessia reversa. Padrão: 2 | `--depth 3` |
| `--refresh` | Não | Força atualização do grafo antes de consultar | `--refresh` |

## O que o Comando Faz

1. Invoca `kata-codebase-graph` com os argumentos recebidos
2. O Kata verifica `graphify.enabled` e a presença do binário; se indisponível, reporta e encerra sem erro
3. O Kata constrói ou atualiza o grafo em modo determinístico e compara `built_at_commit` com o `HEAD`
4. O Kata executa a consulta adequada à pergunta e devolve a resposta com commit de origem, modo de extração e confiança das arestas

## Prompt Template

```
Execute kata-codebase-graph.

Contexto:
- Repositório: {{--repo | repositório atual}}
- Alvo da consulta: {{pergunta ou nó | nenhum — apenas construir/atualizar e reportar hubs}}
- Profundidade da travessia reversa: {{--depth | 2}}
- Forçar atualização: {{--refresh | não}}

Tarefa:
Siga o workflow de kata-codebase-graph do passo 1 ao 6. Quando houver
alvo de consulta, priorize a travessia reversa (impacto) sobre a direta.
Se o grafo estiver indisponível, desabilitado ou desatualizado, declare
a situação e devolva o controle sem erro.

Formato de saída:
- Linha de procedência: built_at_commit, modo de extração, contagem de nós
  e arestas com a divisão EXTRACTED / INFERRED
- Tabela de componentes afetados no formato de kata-architecture-brief
  (Componente | Tipo | Ação | ACs cobertos)
- Identificação explícita dos componentes vindos de travessia reversa
- Marcação das linhas sustentadas apenas por arestas INFERRED
```

## Exemplo de Invocação

**Input:**

```
/cry-graph VersionSeal --repo ../financial-context --depth 2
```

**Output esperado:**

```
Grafo: built_at_commit 3b1c756 (igual ao HEAD) · modo --code-only
20.882 nós · 49.563 arestas · 45.782 EXTRACTED / 3.781 INFERRED

VersionSeal — grau 238, comunidade 1
Definido em components/commons/infra/data/version/seal.py:L34

Impacto reverso (profundidade 2):
| Componente | Tipo | Ação | ACs cobertos |
|---|---|---|---|
| components/commons/application/services/_lifecycle_test.py:L49 | teste | revisar | — |
| components/commons/infra/data/contracts/version_record.py:L39 | módulo | avaliar (INFERRED) | — |

1 linha sustentada apenas por aresta INFERRED. Confirmar antes de tratar
como fronteira de escopo.
```

## Restrições

- Não constrói o grafo por conta própria: delega integralmente a `kata-codebase-graph`
- Não instala o binário do Graphify
- Não versiona `graph.json`
- Não bloqueia o fluxo quando o grafo está indisponível — reporta e encerra sem erro
- Não apresenta resultado sem a linha de procedência

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Invocação rápida | Procedimento completo |
| **Complexidade** | Baixa: recebe argumentos e delega | Alta: 6 passos com validação final |
| **Configura agente?** | Não | Sim |
| **Exemplo** | `/cry-graph VersionSeal` | `kata-codebase-graph` do passo 1 ao 6 |
