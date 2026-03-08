# Kata: Criar Novo Codex

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação de Codex (manuais de referência)

## Objetivo

Este Kata define o procedimento padronizado para criar um novo Codex no Ahrena — desde a definição do domínio de conhecimento até a criação do artefato nos três idiomas obrigatórios.

## Quando Usar

- Quando é necessário documentar conhecimento de domínio para consulta por agentes de IA
- Quando o usuário solicita explicitamente a criação de um novo Codex
- Quando invocado pelo `cry-new-codex`

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Domínio | Sim | Área de conhecimento a documentar (ex: "arquitetura do sistema", "padrões de API") |
| Público-alvo | Não | Quem consultará este Codex. Se omitido, assume "agentes de IA e desenvolvedores" |
| Clade/Subclade | Não | Onde salvar na taxonomia. Se omitido, o agente deve inferir do domínio |

## Workflow

```
Progresso:
- [ ] 1. Leitura das diretivas e referências
- [ ] 2. Estruturação do conhecimento
- [ ] 3. Redação do artefato
- [ ] 4. Salvamento no caminho correto
- [ ] 5. Criação nos demais idiomas
- [ ] 6. Validação final
```

### Passo 1: Leitura das Diretivas e Referências

1. Ler `.ahrena/.directives` para obter:
   - `language.default` — idioma padrão
   - `language.i18n` — idiomas obrigatórios
   - `naming.addressing` — padrão de endereçamento
   - `naming.prefixes.codex` — prefixo (`codex-`)
2. Ler `codex-codex` para internalizar os critérios de qualidade
3. Ler `templates/codex-sample.md` para ter a estrutura base
4. Verificar Codex existentes no Clade/Subclade alvo para evitar duplicidade

### Passo 2: Estruturação do Conhecimento

1. Delimitar o escopo: o que este Codex cobre e o que não cobre
2. Identificar os princípios fundamentais do domínio (3-5 princípios)
3. Mapear padrões e convenções relevantes (tabela: aspecto, padrão, exemplo)
4. Listar decisões vigentes, se aplicável
5. Identificar restrições técnicas do domínio
6. Definir o gatilho de atualização (quando o Codex precisa ser revisado)

### Passo 3: Redação do Artefato

Usar o `templates/codex-sample.md` como base e preencher todas as seções:

1. **Título:** `# Codex: [Nome do Manual]`
2. **Blockquote:** Prefixo, tipo e escopo
3. **Visão Geral:** Uma descrição concisa do domínio coberto (máximo 2 parágrafos)
4. **Contexto:** Domínio, público-alvo e gatilho de atualização
5. **Conteúdo:**
   - Princípios: lista numerada com descrição e justificativa
   - Padrões e Convenções: tabela estruturada
   - Decisões Vigentes: tabela com ADR, decisão e status (se aplicável)
   - Restrições Técnicas: lista de limites concretos
6. **Diagrama de Referência:** Quando o domínio se beneficia de visualização
7. **Glossário:** Termos do domínio com definições contextuais
8. **Referências:** Links para artefatos relacionados

### Passo 4: Salvamento no Caminho Correto

1. Determinar o Clade e Subclade adequados para o domínio
2. Compor o caminho: `framework/{lang}/{clade}/{subclade}/codex/codex-{nome}.md`
3. Usar kebab-case para o nome do arquivo
4. Criar diretórios intermediários se necessário
5. Salvar o artefato no idioma padrão (`language.default`)

### Passo 5: Criação nos Demais Idiomas

1. Para cada idioma em `language.i18n` (exceto o padrão):
   - Executar `kata-translate` com o arquivo criado no Passo 4
   - Ou traduzir diretamente consultando `lex-language-{lang}` e `codex-language-{lang}`
2. Salvar cada tradução no caminho equivalente sob `framework/{lang}/`

### Passo 6: Validação Final

- [ ] O arquivo segue a estrutura completa do `templates/codex-sample.md`
- [ ] A Visão Geral delimita o escopo em no máximo 2 parágrafos
- [ ] O Contexto inclui gatilho de atualização concreto
- [ ] Os princípios são acionáveis (não platitudes genéricas)
- [ ] Tabelas são usadas para informação estruturada
- [ ] O Glossário define termos no contexto deste Codex
- [ ] O arquivo está salvo no caminho correto da taxonomia
- [ ] Existem versões em todos os idiomas de `language.i18n`
- [ ] O nome do arquivo usa o prefixo `codex-` e kebab-case

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Codex no idioma padrão | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/codex/codex-{nome}.md` |
| Traduções | Markdown (`.md`) | Mesmo caminho em cada `framework/{lang}/` |

## Restrições

- Nunca criar um Codex enciclopédico — se o escopo é muito amplo, dividir em Codex menores
- Nunca criar um Codex sem gatilho de atualização — Codex estáticos se tornam obsoletos
- Sempre consultar `codex-codex` antes de redigir
- Sempre verificar Codex existentes para evitar duplicidade ou sobreposição

## Referências

- `codex-codex` — Critérios de qualidade para Codex
- `codex-pilars` — Visão geral do sistema de Pilares
- `lex-template-usage` — Lei de uso obrigatório de templates
- `lex-framework-language` — Lei de estrutura de idiomas
- `kata-translate` — Procedimento de tradução
- `templates/codex-sample.md` — Template oficial
