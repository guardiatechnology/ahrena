# Kata: Criar Nova Lexis

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação de Lexis (leis inquebráveis)

## Objetivo

Este Kata define o procedimento padronizado para criar uma nova Lexis no Ahrena — desde a concepção da lei até a criação do artefato nos três idiomas obrigatórios.

## Quando Usar

- Quando é necessário estabelecer uma restrição absoluta que nenhum agente pode violar
- Quando o usuário solicita explicitamente a criação de uma nova Lexis
- Quando invocado pelo `cry-new-lex`

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Assunto | Sim | Tema da lei (ex: "code review obrigatório", "no secrets em repositório") |
| Escopo | Não | Onde a lei se aplica (ex: "todos os repositórios", "pipeline CI/CD"). Se omitido, o agente deve inferir do assunto |
| Clade/Subclade | Não | Onde salvar o artefato na taxonomia. Se omitido, o agente deve inferir do assunto |

## Workflow

```
Progresso:
- [ ] 1. Leitura das diretivas e referências
- [ ] 2. Concepção da lei
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
   - `naming.prefixes.lexis` — prefixo (`lex-`)
2. Ler `codex-lexis` para internalizar os critérios de qualidade
3. Ler `templates/lex-sample.md` para ter a estrutura base
4. Verificar Lexis existentes no Clade/Subclade alvo para evitar duplicidade

### Passo 2: Concepção da Lei

1. Formular a declaração da lei seguindo os critérios do `codex-lexis`:
   - Sujeito claro
   - Verbo imperativo (DEVE, NÃO PODE)
   - Ação específica
   - Condição temporal (se aplicável)
2. Verificar univocidade: a lei tem uma única interpretação?
3. Verificar testabilidade: é possível verificar automaticamente?
4. Verificar necessidade: resolve um problema real?
5. Verificar imutabilidade: precisa de exceções? Se sim, considerar um Codex em vez de Lexis

### Passo 3: Redação do Artefato

Usar o `templates/lex-sample.md` como base e preencher todas as seções:

1. **Título:** `# Lexis: [Nome Descritivo]`
2. **Blockquote:** Prefixo, tipo e escopo
3. **Propósito:** Por que esta lei existe — conectar a um risco ou problema real
4. **Lei:** Declaração imperativa em blockquote (`> **[declaração]**`)
5. **Abrangência:**
   - Aplica-se a: escopo específico
   - Agentes vinculados: todos ou Warriors específicos
   - Exceções: Nenhuma (sempre)
6. **Consequências de Violação:**
   - Bloqueio automático: ação técnica
   - Alerta: quem é notificado
   - Remediação: como corrigir
7. **Exemplos:** Correto e Incorreto com blocos de código
8. **Validação Automatizada:** Ferramenta, momento e métrica

### Passo 4: Salvamento no Caminho Correto

1. Determinar o Clade e Subclade adequados para o assunto
2. Compor o caminho: `framework/{lang}/{clade}/{subclade}/lexis/lex-{nome}.md`
3. Usar kebab-case para o nome do arquivo
4. Criar diretórios intermediários se necessário
5. Salvar o artefato no idioma padrão (`language.default`)

### Passo 5: Criação nos Demais Idiomas

1. Para cada idioma em `language.i18n` (exceto o padrão):
   - Executar `kata-translate` com o arquivo criado no Passo 4
   - Ou, se o agente domina o idioma, traduzir diretamente consultando `lex-language-{lang}` e `codex-language-{lang}`
2. Salvar cada tradução no caminho equivalente sob `framework/{lang}/`

### Passo 6: Validação Final

- [ ] O arquivo segue a estrutura completa do `templates/lex-sample.md`
- [ ] A declaração da lei é clara, unívoca e imperativa
- [ ] A seção "Exceções" diz "Nenhuma"
- [ ] A seção "Validação Automatizada" especifica ferramenta, momento e métrica
- [ ] Os exemplos (Correto/Incorreto) são concretos
- [ ] O arquivo está salvo no caminho correto da taxonomia
- [ ] Existem versões em todos os idiomas de `language.i18n`
- [ ] O nome do arquivo usa o prefixo `lex-` e kebab-case

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Lexis no idioma padrão | Markdown (`.md`) | `framework/{lang}/{clade}/{subclade}/lexis/lex-{nome}.md` |
| Traduções | Markdown (`.md`) | Mesmo caminho em cada `framework/{lang}/` |

## Restrições

- Nunca criar uma Lexis que admita exceções — se precisa de exceção, deve ser um Codex
- Nunca criar uma Lexis sem validação automatizada — se não pode ser testada, repensar a formulação
- Sempre consultar `codex-lexis` antes de redigir
- Sempre verificar Lexis existentes para evitar duplicidade ou contradição

## Referências

- `codex-lexis` — Critérios de qualidade para Lexis
- `codex-pilars` — Visão geral do sistema de Pilares
- `lex-template-usage` — Lei de uso obrigatório de templates
- `lex-framework-language` — Lei de estrutura de idiomas
- `kata-translate` — Procedimento de tradução
- `templates/lex-sample.md` — Template oficial
