# Kata: Criar Novo Cry

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação de Cries (comandos recorrentes)

## Objetivo

Este Kata define o procedimento padronizado para criar um novo Cry no Ahrena — desde o design do comando e seus parâmetros até a criação do artefato nos três idiomas obrigatórios.

## Quando Usar

- Quando é necessário criar um atalho rápido para uma tarefa recorrente
- Quando o usuário solicita explicitamente a criação de um novo Cry
- Quando invocado pelo `cry-new-cry`
- Quando um Kata existente precisa de um ponto de entrada simplificado

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Ação | Sim | O que o comando faz (ex: "traduzir documento", "gerar changelog") |
| Kata associado | Não | Kata que o Cry invoca. Se omitido, o agente deve identificar ou sugerir a criação de um Kata |
| Warrior associado | Não | Warrior que executa o Kata, se existir |
| Clade/Subclade | Não | Onde salvar na taxonomia. Se omitido, o agente deve inferir da ação |
| Destino | Não | "framework" (padrão) ou "projeto". Se "projeto", o artefato é salvo em `.ahrena/artifacts/`; depois pode ser incorporado com `kata-push-to-framework` |

## Workflow

```
Progresso:
- [ ] 1. Leitura das diretivas e referências
- [ ] 2. Design do comando
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
   - `naming.prefixes.cries` — prefixo (`cry-`)
   - `paths.project_artifacts` — se Destino for "projeto"
   - `paths.framework` — se Destino for "framework"
2. Ler `codex-cries` para internalizar os critérios de qualidade
3. Ler `templates/cry-sample.md` para ter a estrutura base
4. Verificar Cries existentes para evitar duplicidade
5. Confirmar que o Kata associado existe (ou marcar como pendente de criação)

### Passo 2: Design do Comando

1. Definir a **sintaxe de invocação**: `/cry-{nome} <obrigatório> [opcional]`
2. Definir **parâmetros**:
   - Mínimo de obrigatórios (apenas o essencial)
   - Defaults inteligentes para opcionais (do `.directives` quando possível)
   - Formato explícito para cada parâmetro
3. Definir a **cadeia de invocação**:
   - Padrão 1: Cry → Kata (quando não há Warrior)
   - Padrão 2: Cry → Warrior → Kata (quando existe Warrior dedicado)
4. Elaborar o **prompt template**:
   - Contexto com variáveis `{{param}}`
   - Tarefa referenciando o Kata por nome
   - Formato de saída explícito
5. Preparar **exemplo de invocação** com input e output concretos

### Passo 3: Redação do Artefato

Usar o `templates/cry-sample.md` como base e preencher todas as seções:

1. **Título:** `# Cry: [Nome do Comando]`
2. **Blockquote:** Prefixo, tipo e escopo
3. **Descrição:** Uma frase sobre o que o comando faz
4. **Uso:** Sintaxe com `/cry-{nome}`
5. **Parâmetros:** Tabela com nome, obrigatoriedade, descrição e exemplo
6. **O que o Comando Faz:** Lista numerada de 3-6 ações de alto nível
7. **Prompt Template:** Bloco de código com contexto, tarefa e formato
8. **Exemplo de Invocação:** Input e output concretos
9. **Restrições:** Limites do comando
10. **Diferença de Kata:** Tabela comparativa Cry vs Kata para este caso

### Passo 4: Salvamento no Caminho Correto

1. Determinar o Clade e Subclade adequados
2. Se **Destino** for "framework": compor `{paths.framework}/{lang}/{clade}/{subclade}/cries/cry-{nome}.md`. Se for "projeto": compor `{paths.project_artifacts}/{lang}/{clade}/{subclade}/cries/cry-{nome}.md`
3. Usar kebab-case para o nome do arquivo
4. Criar diretórios intermediários se necessário
5. Salvar o artefato no idioma padrão (`language.default`)

### Passo 5: Criação nos Demais Idiomas

1. Se **Destino** for "projeto", pode criar apenas no idioma padrão; os demais podem ser gerados ao executar `kata-push-to-framework`.
2. Se **Destino** for "framework" (ou se optar por todos os idiomas no projeto): para cada idioma em `language.i18n` (exceto o padrão), executar `kata-translate` ou traduzir consultando `lex-language-{lang}` e `codex-language-{lang}`; salvar no caminho equivalente sob `paths.framework/{lang}/` ou `paths.project_artifacts/{lang}/`.

### Passo 6: Validação Final

- [ ] O arquivo segue a estrutura completa do `templates/cry-sample.md`
- [ ] A sintaxe de invocação é clara (`/cry-{nome} <args>`)
- [ ] Os parâmetros obrigatórios são mínimos (1-2 idealmente)
- [ ] O prompt template usa `{{variáveis}}` e referencia o Kata
- [ ] O exemplo de invocação tem input e output concretos
- [ ] A tabela "Diferença de Kata" está preenchida
- [ ] O Kata associado existe ou está marcado como pendente
- [ ] O arquivo está salvo no caminho correto da taxonomia
- [ ] Existem versões em todos os idiomas de `language.i18n`
- [ ] O nome do arquivo usa o prefixo do Pilar definido em `naming.prefixes.cries` (consultar `.directives`) e kebab-case

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Cry no idioma padrão | Markdown (`.md`) | `framework/` ou `.ahrena/artifacts/` conforme Destino |
| Traduções | Markdown (`.md`) | Mesmo caminho em cada `{lang}/` (obrigatório se framework; opcional se projeto) |

## Restrições

- Todo Cry deve referenciar pelo menos um Kata — Cries sem Kata delegam mal
- Nunca criar um Cry com muitos parâmetros obrigatórios — se precisa de muitos inputs, o usuário deveria usar o Kata diretamente
- Sempre consultar `codex-cries` antes de redigir
- Sempre verificar Cries existentes para evitar duplicidade

## Referências

- `lex-pilars` — Definição canônica dos Pilares; validar artefato produzido (Cry invoca só Kata/Warrior)
- `codex-pilars` — Checklist de validação para Cries (seção Validação de artefatos)
- `codex-cries` — Critérios de qualidade para Cries
- `codex-pilars` — Visão geral do sistema de Pilares
- `lex-template-usage` — Lei de uso obrigatório de templates
- `lex-framework-language` — Lei de estrutura de idiomas
- `kata-translate` — Procedimento de tradução
- `templates/cry-sample.md` — Template oficial
