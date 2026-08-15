---
name: kata-create-warrior
description: "Criar Novo Warrior. Criação de Warriors (agentes especializados)"
---

# Kata: Criar Novo Warrior

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação de Warriors (agentes especializados)

## Workflow

```
Progresso:
- [ ] 1. Leitura das diretivas e referências
- [ ] 2. Design da identidade
- [ ] 3. Definição de responsabilidades e consulta
- [ ] 4. Redação do artefato
- [ ] 5. Salvamento no caminho correto
- [ ] 6. Criação nos demais idiomas
- [ ] 7. Validação final
```

### Passo 1: Leitura das Diretivas e Referências

1. Ler `.ahrena/.directives` para obter:
   - `language.default` — idioma padrão
   - `language.i18n` — idiomas obrigatórios
   - `naming.addressing` — padrão de endereçamento
   - `naming.prefixes.warriors` — prefixo (`warrior-`)
   - `paths.project_artifacts` — se Destino for "projeto"
   - `paths.framework` — se Destino for "framework"
2. Ler `codex-warriors` para internalizar os critérios de qualidade
3. Ler `templates/warrior-sample.md` para ter a estrutura base
4. Verificar Warriors existentes para evitar sobreposição de responsabilidades

### Passo 2: Design da Identidade

1. **Nome:** Escolher um nome memorável que evoque o papel (mitológico, histórico ou simbólico)
2. **Papel:** Título profissional claro (ex: "Tradutor Especialista de Documentação Técnica")
3. **Domínio:** Área específica de atuação com delimitação clara
4. **Persona:** 2-3 adjetivos que definem o tom (ex: "metódico, criterioso, focado em trade-offs")
5. **Missão:** 1-2 frases em blockquote que resumem o propósito central

### Passo 3: Definição de Responsabilidades e Consulta

1. Listar responsabilidades positivas ("Faz") — ações concretas e específicas
2. Listar exclusões ("Não Faz") — limites claros para evitar escopo infinito
3. Mapear a cadeia de consulta:
   - **Lexis:** quais leis o Warrior segue (sempre incluir `lex-directives`)
   - **Codex:** quais manuais consulta para tomar decisões
   - **Katas:** quais procedimentos executa
4. Definir critérios de escalação — quando o Warrior para e pede ajuda humana
5. Definir o fluxo de atuação: Recebe → Consulta → Analisa → Produz → Valida

### Passo 4: Redação do Artefato

Usar o `templates/warrior-sample.md` como base e preencher todas as seções:

1. **Título:** `# Warrior: [Nome] — [Descrição Breve]`
2. **Blockquote:** Prefixo, tipo e escopo
3. **Identidade:** Nome, papel, domínio e persona
4. **Missão:** Citação em blockquote
5. **Responsabilidades:** Listas "Faz" e "Não Faz"
6. **Consulta:** Tabelas de Lexis, Codex e Katas
7. **Comportamento:** Tom, fluxo de atuação e critérios de escalação
8. **Exemplo de Interação:** Input do usuário + resposta estruturada do Warrior

### Passo 5: Salvamento no Caminho Correto

1. Determinar o Clade e Subclade adequados
2. Se **Destino** for "framework": compor `{paths.framework}/{lang}/{clade}/{subclade}/warriors/warrior-{nome}.md`. Se for "projeto": compor `{paths.project_artifacts}/{lang}/{clade}/{subclade}/warriors/warrior-{nome}.md`
3. Usar kebab-case para o nome do arquivo (nome do warrior)
4. Criar diretórios intermediários se necessário
5. Salvar o artefato no idioma padrão (`language.default`)

### Passo 6: Criação nos Demais Idiomas

1. Se **Destino** for "projeto", pode criar apenas no idioma padrão; os demais podem ser gerados ao executar `kata-push-to-framework`.
2. Se **Destino** for "framework" (ou se optar por todos os idiomas no projeto): para cada idioma em `language.i18n` (exceto o padrão), executar `kata-translate` ou traduzir consultando `lex-language-{lang}` e `codex-language-{lang}`; salvar no caminho equivalente sob `paths.framework/{lang}/` ou `paths.project_artifacts/{lang}/`.

### Passo 7: Validação Final

- [ ] O arquivo segue a estrutura completa do `templates/warrior-sample.md`
- [ ] A identidade tem nome, papel, domínio e persona
- [ ] A missão está em blockquote com 1-2 frases
- [ ] "Faz" e "Não Faz" são listas equilibradas e sem ambiguidade
- [ ] A cadeia de consulta inclui pelo menos `lex-directives`
- [ ] Os critérios de escalação são concretos
- [ ] O exemplo de interação tem input e output completos
- [ ] O arquivo está salvo no caminho correto da taxonomia
- [ ] Existem versões em todos os idiomas de `language.i18n`
- [ ] O nome do arquivo usa o prefixo do Pilar definido em `naming.prefixes.warriors` (consultar `.directives`) e kebab-case

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Warrior no idioma padrão | Markdown (`.md`) | `framework/` ou `.ahrena/artifacts/` conforme Destino |
| Traduções | Markdown (`.md`) | Mesmo caminho em cada `{lang}/` (obrigatório se framework; opcional se projeto) |

## Restrições

- Nunca criar um Warrior genérico sem escopo delimitado
- Nunca criar um Warrior sem cadeia de consulta explícita
- Nunca criar um Warrior sem critérios de escalação
- Sempre consultar `codex-warriors` antes de redigir
- Sempre verificar Warriors existentes para evitar sobreposição de responsabilidades
