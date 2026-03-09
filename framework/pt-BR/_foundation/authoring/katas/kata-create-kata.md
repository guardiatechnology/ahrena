# Kata: Criar Novo Kata

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação de Katas (procedimentos repetíveis)

## Objetivo

Este Kata define o procedimento padronizado para criar um novo Kata no Ahrena — desde a decomposição da tarefa em passos até a criação do artefato nos três idiomas obrigatórios. Este é o Kata que cria Katas — o mecanismo de autorreplicação do framework.

## Quando Usar

- Quando é necessário padronizar uma tarefa recorrente em procedimento estruturado
- Quando o usuário solicita explicitamente a criação de um novo Kata
- Quando invocado pelo `cry-new-kata`

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Tarefa | Sim | Descrição da tarefa a ser padronizada (ex: "criar ADR", "fazer code review") |
| Contexto | Não | Informações adicionais sobre o domínio ou restrições da tarefa |
| Clade/Subclade | Não | Onde salvar na taxonomia. Se omitido, o agente deve inferir da tarefa |
| Destino | Não | "framework" (padrão) ou "projeto". Se "projeto", o artefato é salvo em `.ahrena/artifacts/`; depois pode ser incorporado com `kata-push-to-framework` |

## Workflow

```
Progresso:
- [ ] 1. Leitura das diretivas e referências
- [ ] 2. Decomposição da tarefa
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
   - `naming.prefixes.katas` — prefixo (`kata-`)
   - `paths.project_artifacts` — se Destino for "projeto"
   - `paths.framework` — se Destino for "framework"
2. Ler `codex-katas` para internalizar os critérios de qualidade
3. Ler `templates/kata-sample.md` para ter a estrutura base
4. Verificar Katas existentes para evitar duplicidade

### Passo 2: Decomposição da Tarefa

1. Identificar os **inputs** necessários:
   - O que é obrigatório?
   - O que pode ter default?
   - Qual o formato esperado de cada input?
2. Decompor a tarefa em **passos atômicos** (4-8 passos ideal):
   - Cada passo faz uma única coisa
   - Cada passo tem sub-ações numeradas
   - Cada passo é verificável antes de avançar
3. Identificar os **outputs**:
   - O que é produzido?
   - Em qual formato?
   - Onde é salvo?
4. Definir **critérios de validação**:
   - Checklist de forma (estrutura, formatação)
   - Checklist de conteúdo (completude, correção)
5. Se a tarefa tem menos de 4 passos, considerar se deveria ser um Cry em vez de Kata

### Passo 3: Redação do Artefato

Usar o `templates/kata-sample.md` como base e preencher todas as seções:

1. **Título:** `# Kata: [Nome do Procedimento]`
2. **Blockquote:** Prefixo, tipo e escopo
3. **Objetivo:** Uma frase sobre o que o procedimento produz
4. **Quando Usar:** Lista de condições de ativação (3-4 itens)
5. **Inputs:** Tabela com nome, obrigatoriedade e descrição
6. **Workflow:**
   - Checklist de progresso no início (checkboxes)
   - Cada passo com título descritivo e sub-ações numeradas
   - Último passo sempre "Validação Final"
7. **Outputs:** Tabela com formato e destino
8. **Restrições:** Lista de limites do que o Kata não pode fazer

### Passo 4: Salvamento no Caminho Correto

1. Determinar o Clade e Subclade adequados para a tarefa
2. Se **Destino** for "framework": compor `{paths.framework}/{lang}/{clade}/{subclade}/katas/kata-{nome}.md`. Se for "projeto": compor `{paths.project_artifacts}/{lang}/{clade}/{subclade}/katas/kata-{nome}.md`
3. Usar kebab-case para o nome do arquivo
4. Criar diretórios intermediários se necessário
5. Salvar o artefato no idioma padrão (`language.default`)

### Passo 5: Criação nos Demais Idiomas

1. Se **Destino** for "projeto", pode criar apenas no idioma padrão; os demais podem ser gerados ao executar `kata-push-to-framework`.
2. Se **Destino** for "framework" (ou se optar por todos os idiomas no projeto): para cada idioma em `language.i18n` (exceto o padrão), executar `kata-translate` ou traduzir consultando `lex-language-{lang}` e `codex-language-{lang}`; salvar no caminho equivalente sob `paths.framework/{lang}/` ou `paths.project_artifacts/{lang}/`.

### Passo 6: Validação Final

- [ ] O arquivo segue a estrutura completa do `templates/kata-sample.md`
- [ ] O Objetivo descreve o output em uma frase clara
- [ ] Os Inputs têm obrigatoriedade e defaults definidos
- [ ] O Workflow tem checklist de progresso no início
- [ ] Cada passo faz uma única coisa (atômico)
- [ ] O último passo é "Validação Final" com checkboxes
- [ ] O número de passos está entre 4 e 8
- [ ] Os Outputs especificam formato e destino
- [ ] O arquivo está salvo no caminho correto da taxonomia
- [ ] Existem versões em todos os idiomas de `language.i18n`
- [ ] O nome do arquivo usa o prefixo `kata-` e kebab-case

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Kata no idioma padrão | Markdown (`.md`) | `framework/` ou `.ahrena/artifacts/` conforme Destino |
| Traduções | Markdown (`.md`) | Mesmo caminho em cada `{lang}/` (obrigatório se framework; opcional se projeto) |

## Restrições

- Se a tarefa tem menos de 4 passos, considerar criar um Cry em vez de Kata
- Se a tarefa tem mais de 8 passos, considerar dividir em Katas menores
- Nunca criar um Kata com passos vagos — cada passo deve ter sub-ações concretas
- Sempre consultar `codex-katas` antes de redigir
- Sempre incluir validação final como último passo

## Referências

- `codex-katas` — Critérios de qualidade para Katas
- `codex-pilars` — Visão geral do sistema de Pilares
- `lex-template-usage` — Lei de uso obrigatório de templates
- `lex-framework-language` — Lei de estrutura de idiomas
- `kata-translate` — Procedimento de tradução
- `templates/kata-sample.md` — Template oficial
