# Kata: Push para o Framework

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Incorporação de artefatos de projeto ao framework

## Objetivo

Este Kata define o procedimento para incorporar ao framework canônico os artefatos que foram criados no espaço do projeto (`.ahrena/artifacts/`). Copia os arquivos para `framework/`, garante as traduções nos idiomas obrigatórios e opcionalmente remove as cópias do projeto.

## Quando Usar

- Quando artefatos em `.ahrena/artifacts/` foram validados e estão prontos para fazer parte do framework
- Quando o usuário solicita explicitamente incorporar artefatos do projeto ao framework
- Quando invocado pelo `cry-push-to-framework`

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Alvo | Não | Caminho(s) relativo(s) em `paths.project_artifacts` (ex: `pt-BR/engineering/quality/lexis/lex-foo.md`) ou "todos". Se omitido, o agente lista artefatos existentes e pergunta ou processa todos |
| Remover do projeto | Não | Se "sim", remove os arquivos de `.ahrena/artifacts/` após copiar para o framework. Default: "não" |

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

### Passo 3: Cópia para o Framework e i18n

Para cada artefato da lista:

1. Caminho de origem: `{paths.project_artifacts}/{lang}/{clade}/{subclade}/{pilar}/{arquivo}`
2. Caminho de destino no framework: `{paths.framework}/{lang}/{clade}/{subclade}/{pilar}/{arquivo}`
3. Criar os diretórios de destino no framework se não existirem
4. Copiar o arquivo do projeto para o framework (sobrescrever se já existir)
5. Verificar idiomas: para cada idioma em `language.i18n` que ainda não tenha o arquivo no framework:
   - Se existir no projeto em outro idioma, copiar
   - Se não existir, executar `kata-translate` a partir do arquivo no idioma padrão e salvar em `framework/{lang}/...`
6. Registrar quais arquivos foram copiados e quais traduções foram criadas

### Passo 4: Remoção Opcional do Projeto

1. Se o input **Remover do projeto** for "sim":
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
| Artefatos no framework | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/{pilar}/` |
| Traduções (se faltavam) | Markdown (`.md`) | Mesmo caminho em cada `framework/{lang}/` |
| Relatório | Texto | Resposta ao usuário |

## Restrições

- Não alterar o conteúdo dos artefatos durante a cópia (copiar tal qual, exceto ao gerar traduções)
- Sempre garantir que, após o Push, cada artefato exista no framework em todos os idiomas de `language.i18n`
- Se um arquivo já existir no framework e for mais recente ou diferente, considerar sobrescrever apenas se o artefato do projeto for explicitamente o que se deseja promover

## Referências

- `codex-pilars` — Artefatos no projeto (.ahrena) e fluxo Push
- `kata-translate` — Procedimento de tradução para gerar idiomas faltantes
- `.ahrena/.directives` — paths.project_artifacts, paths.framework, language.i18n
