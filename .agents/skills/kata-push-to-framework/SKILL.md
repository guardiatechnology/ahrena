---
name: kata-push-to-framework
description: "Push para o Framework. Incorporação de artefatos de projeto ao framework"
---

# Kata: Push para o Framework

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Incorporação de artefatos de projeto ao framework

## Workflow

```
Progresso:
- [ ] 1. Leitura das diretivas
- [ ] 2. Identificação dos artefatos a incorporar
- [ ] 3. Cópia para o framework e i18n
- [ ] 4. Remoção opcional do projeto
- [ ] 5. Validação final
```

### Passo 1: Leitura das Diretivas

1. Ler `.ahrena/.directives` para obter:
   - `paths.project_artifacts` — raiz dos artefatos de projeto (ex: `.ahrena/artifacts/`)
   - `paths.framework` — raiz do framework (ex: `framework/`)
   - `language.default` — idioma padrão
   - `language.i18n` — idiomas obrigatórios
   - Em modo **remote:** `paths.framework_repo` ou `repo.framework` (URL ou slug do repositório do framework no GitHub), se existir
2. Confirmar que o diretório `paths.project_artifacts` existe; se não existir, informar que não há artefatos para incorporar e encerrar

### Passo 2: Identificação dos Artefatos a Incorporar

1. Se o input **Alvo** foi fornecido:
   - Se for "todos", listar recursivamente todos os arquivos `.md` sob `paths.project_artifacts`
   - Se for um ou mais caminhos relativos, validar que cada um existe sob `paths.project_artifacts` e adicionar à lista
2. Se o input **Alvo** não foi fornecido:
   - Listar todos os arquivos `.md` sob `paths.project_artifacts`
   - Se não houver nenhum, informar e encerrar
   - Se houver, processar todos (ou perguntar ao usuário qual(is) incorporar)
3. Para cada artefato, extrair: `{lang}/{clade}/{subclade}/{pilar}/{arquivo}` (o path relativo dentro de project_artifacts)
4. Validar que a estrutura segue o padrão de endereçamento (lang/clade/subclade/pilar); ignorar ou alertar sobre arquivos que não seguem

### Passo 3: Cópia para o Framework e i18n (modo local) ou Envio ao remoto (modo remote)

**Se --local:**

Para cada artefato da lista:

1. Caminho de origem: `{paths.project_artifacts}/{lang}/{clade}/{subclade}/{pilar}/{arquivo}`
2. Caminho de destino no framework: `{paths.framework}/{lang}/{clade}/{subclade}/{pilar}/{arquivo}`
3. Criar os diretórios de destino no framework se não existirem
4. Copiar o arquivo do projeto para o framework (sobrescrever se já existir)
5. Verificar idiomas: para cada idioma em `language.i18n` que ainda não tenha o arquivo no framework:
   - Se existir no projeto em outro idioma, copiar
   - Se não existir, executar `kata-translate` a partir do arquivo no idioma padrão e salvar em `framework/{lang}/...`
6. Registrar quais arquivos foram copiados e quais traduções foram criadas

**Se --remote:**

1. Não escrever em `paths.framework` no disco local.
2. Preparar o conjunto de arquivos a incorporar no mesmo layout que em `framework/{lang}/{clade}/{subclade}/{pilar}/` (incluindo traduções faltantes via `kata-translate` em memória ou em área temporária).
3. **Obrigatório:** executar o fluxo de sincronização com o repositório do framework **usando exclusivamente o MCP do GitHub**. O agente **DEVE** usar as ferramentas MCP do GitHub disponíveis (ex.: servidor `project-0-ahrena-github` ou equivalente) para: criar branch para as alterações, aplicar os arquivos preparados (commit), push, abrir PR. Todas as operações no repositório remoto do framework devem ser feitas via MCP do GitHub.
4. Registrar arquivos preparados, branch criada e link do PR retornado pelo MCP do GitHub.

### Passo 4: Remoção Opcional do Projeto

1. Se o input **Remover do projeto** for "sim":
   - Em modo **local:** após a cópia para `framework/`; em modo **remote:** após envio bem-sucedido (ex.: após abertura do PR via MCP do GitHub).
   - Para cada artefato processado, remover o(s) arquivo(s) em `paths.project_artifacts` (todos os idiomas do mesmo artefato)
   - Remover diretórios vazios sob `paths.project_artifacts` se aplicável
2. Se for "não", deixar os arquivos no projeto inalterados

### Passo 5: Validação Final

- [ ] Todos os artefatos alvo foram copiados para `framework/`
- [ ] Para cada artefato, existem versões em todos os idiomas de `language.i18n` no framework
- [ ] Nenhum arquivo foi corrompido (conteúdo preservado)
- [ ] Se "Remover do projeto" foi sim, os arquivos foram removidos de `.ahrena/artifacts/`
- [ ] Relatório entregue ao usuário com lista de arquivos incorporados e traduções geradas

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Artefatos no framework (modo local) | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/{pilar}/` |
| Traduções (se faltavam, modo local) | Markdown (`.md`) | Mesmo caminho em cada `framework/{lang}/` |
| Modo remote | — | Relatório com arquivos preparados, branch, link do PR (retornado pelo MCP do GitHub) |
| Relatório | Texto | Resposta ao usuário |

## Restrições

- Não alterar o conteúdo dos artefatos durante a cópia ou ao preparar para envio (copiar tal qual, exceto ao gerar traduções)
- Sempre garantir que, após o Push, cada artefato exista no framework em todos os idiomas de `language.i18n` (no destino: local ou remoto)
- Em modo **remote**, **é obrigatório usar o MCP do GitHub**; não usar apenas git em linha de comando para push ou abertura de PR
- Se um arquivo já existir no framework e for mais recente ou diferente, considerar sobrescrever apenas se o artefato do projeto for explicitamente o que se deseja promover
