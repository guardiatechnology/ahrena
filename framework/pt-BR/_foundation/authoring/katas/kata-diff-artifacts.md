# Kata: Diff de Artefatos

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Comparação de artefatos do projeto com o framework

## Objetivo

Comparar `.ahrena/artifacts` (e, quando aplicável, `.ahrena/framework`) com o framework em modo **local** (vs framework no repo) ou **remoto** (vs versão mais recente do framework no GitHub). Identificar o que seria incorporado, o que difere ou o que está desatualizado em relação ao remoto.

## Quando Usar

- Antes do push, para ver o que será incorporado ou o que difere entre projeto e framework
- Para inspecionar divergência entre artefatos do projeto e o framework (local ou remoto)
- Quando invocado por `cry-diff-artifacts`

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Modo | Sim | `local` ou `remote`. Local: compara com `paths.framework` no repo. Remote: compara com a versão mais recente do framework no repositório remoto (obtida via MCP do GitHub). |
| Alvo | Não | Caminho(s) relativo(s) em `paths.project_artifacts` ou "todos". Se omitido, considerar todos os artefatos. |

## Workflow

```
Progresso:
- [ ] 1. Leitura das diretivas
- [ ] 2. Modo local: comparação com framework local
- [ ] 3. Modo remote: comparação com versão mais recente (via MCP do GitHub)
- [ ] 4. Validação final e relatório
```

### Passo 1: Leitura das Diretivas

1. Ler `.ahrena/.directives` para obter:
   - `paths.project_artifacts` — raiz dos artefatos de projeto
   - `paths.framework` — raiz do framework (para modo local)
   - Em modo **remote:** URL ou ref do repositório do framework / branch de comparação (ex.: `paths.framework_repo` ou `repo.framework`), se existir

### Passo 2: Modo local — Comparação com Framework Local

1. Listar arquivos `.md` em `paths.project_artifacts` por path relativo `{lang}/{clade}/{subclade}/{pilar}/{arquivo}`.
2. Para cada path lógico de artefato, comparar com `paths.framework/{lang}/{clade}/{subclade}/{pilar}/{arquivo}`:
   - existe só em artifacts;
   - existe só no framework;
   - existe em ambos (nesse caso, produzir diff de conteúdo, ex.: diferença de linhas).
3. Opcional: incluir `.ahrena/framework/` na comparação com `paths.framework/` (mesma estrutura) para ver divergências entre a cópia instalada e o framework do repo.
4. Saída: tabela ou lista com colunas "Artefato", "Em artifacts", "Em framework", "Diff (sim/não ou resumo)".

### Passo 3: Modo remote — Comparação com Versão Mais Recente

1. **Obrigatório:** usar o **MCP do GitHub** para obter o conteúdo da versão mais recente do framework no repositório remoto (branch principal, ex.: `main`). O agente **DEVE** usar as ferramentas MCP do GitHub (ex.: leitura de conteúdo de arquivos no repo, listagem de árvore, comparação) para obter os artefatos do framework no remoto.
2. Comparar: (a) arquivos em `.ahrena/artifacts/` vs mesmo path na versão remota do framework (obtida via MCP); (b) arquivos em `paths.framework` local (se existir) vs mesmo path na versão remota. Saída: "só local", "só remoto", "diferente" (com resumo de diff quando possível).
3. Em modo remote **não** substituir o MCP do GitHub por apenas `git fetch`/clone em linha de comando; o diff remoto **DEVE** basear-se em dados obtidos via MCP do GitHub.

### Passo 4: Validação Final

- [ ] Relatório entregue ao usuário com as diferenças encontradas
- [ ] Nenhuma alteração foi feita nos arquivos (somente leitura)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Relatório de diff | Texto (e opcionalmente estruturado) | Resposta ao usuário |

Conteúdo do relatório: artefatos apenas em artifacts, apenas no framework (local ou remoto), e os que diferem (com indicação de diff).

## Restrições

- Somente leitura; não modificar `.ahrena/` nem `framework/`.
- Em modo **remote**, é **obrigatório** usar o MCP do GitHub para obter o estado do framework no remoto; não usar apenas git local para comparação.

## Referências

- `codex-pilars` — Fluxo e conceitos de artefatos no projeto e Push
- `.ahrena/.directives` — paths.project_artifacts, paths.framework
- `kata-push-to-framework` — Procedimento de incorporação ao framework
- Modo remote: MCP do GitHub (servidor configurado para o repositório do framework)
