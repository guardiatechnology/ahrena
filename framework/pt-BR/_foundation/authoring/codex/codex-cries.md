# Codex: Como Escrever Bons Cries

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Criação de Cries (comandos recorrentes)

## Visão Geral

Este Codex documenta como projetar comandos recorrentes eficazes no Ahrena. Aborda quando criar um Cry vs usar um Kata diretamente, design de prompt templates, parâmetros e a cadeia Cry → Kata/Warrior. É consultado pelo `kata-create-cry` durante a criação de novos Cries. O kata usa este Codex no **Passo 1** (leitura dos critérios) e no **Passo 3** (redação das seções); a **Validação Final** do Kata verifica as Restrições Técnicas e a Anatomia descritas abaixo.

## Contexto

- **Domínio:** Design de comandos de produtividade para agentes de IA
- **Público-alvo:** Agentes de IA executando `kata-create-cry` e mantenedores do framework
- **Atualização:** Quando novos padrões de qualidade forem identificados para Cries

## Conteúdo

### Princípios

1. **Rapidez:** Um Cry existe para economizar tempo. Se a invocação é tão complexa quanto executar o Kata diretamente, o Cry não tem valor.
2. **Delegação:** O Cry não contém lógica própria — ele delega para um Kata (opcionalmente via um Warrior). O Cry é o ponto de entrada, não o procedimento.
3. **Parâmetros mínimos:** O Cry deve exigir o mínimo de informação do usuário, usando defaults inteligentes do `.directives` para o restante.
4. **Previsibilidade:** O mesmo Cry com os mesmos parâmetros deve produzir o mesmo resultado.
5. **Regra de invocação (inquebrável):** O Cry **NÃO PODE** invocar Lexis. O Cry **NÃO PODE** acessar Codex diretamente. O Cry invoca **SOMENTE** Katas e/ou Warriors. A consulta a Lexis e Codex é feita pelo Kata ou Warrior invocado, nunca pelo Cry como ação direta.
6. **Sem comandos externos sem Kata:** O Cry **NÃO PODE** definir ou prescrever como procedimento principal a execução de comandos externos (ex.: `git`, `make`, `npm`, `pnpm`, `python`, scripts de shell) sem que exista um **Kata** que encapsule esse procedimento e que o Cry invoque. Se o fluxo do comando envolve rodar ferramentas externas, deve existir um Kata (ex.: `kata-sync`, `kata-rebase`) que descreva os passos, e o Cry apenas invoca esse Kata (ou um Warrior que o orquestre). Um Cry que descreve "execute git X, depois Y" no corpo do artefato, sem invocar um Kata existente, é não conforme — o procedimento deve estar no Kata; o Cry é apenas o atalho de invocação.

### Anatomia de um Bom Cry

| Seção | Propósito | Critério de Qualidade |
|-------|-----------|----------------------|
| **Descrição** | O que o comando faz em uma frase | Clara e direta |
| **Uso** | Sintaxe de invocação | Formato: `/cry-nome <obrigatório> [opcional]` |
| **Parâmetros** | Tabela de argumentos | Nome, obrigatoriedade, descrição e exemplo |
| **O que o Comando Faz** | Lista numerada de ações | 3-6 passos de alto nível |
| **Prompt Template** | Instruções enviadas ao agente | Contexto + Tarefa + Formato de saída |
| **Exemplo de Invocação** | Input e output concretos | Demonstra uso real |
| **Diferença de Kata** | Tabela comparativa | Cry vs Kata para este caso |

### Design de Parâmetros

| Prática | Exemplo |
|---------|---------|
| Mínimo de parâmetros obrigatórios | Apenas o essencial que não pode ter default |
| Defaults inteligentes | Idiomas vêm do `.directives`, não do usuário |
| Formato explícito | "Código BCP 47" é mais claro que "idioma" |
| Consistência com outros Cries | Mesmo padrão de nomeação e ordem |

### Design de Prompt Template

O prompt template é o coração funcional do Cry. Estrutura recomendada:

```
Contexto:
- {{parâmetro1}}
- {{parâmetro2}}

Tarefa:
[Instrução clara do que fazer, referenciando Kata e/ou Warrior]

Formato de saída:
[Como o resultado deve ser apresentado]
```

Boas práticas:
- Referenciar o Kata a ser executado por nome
- Se houver Warrior, instruir o agente a assumir o papel
- Definir formato de saída explicitamente
- Usar variáveis com `{{duplas chaves}}` para parâmetros

### Cadeia de Invocação

Um Cry pode seguir dois padrões:

**Padrão 1: Cry → Kata (direto)**
```
/cry-new-lex "code review" → kata-create-lexis
```
Usado quando não há Warrior dedicado para o domínio.

**Padrão 2: Cry → Warrior → Kata**
```
/cry-translate arquivo.md → warrior-translator → kata-translate
```
Usado quando existe um Warrior que adiciona persona e contexto.

### Padrões e Convenções

| Aspecto | Padrão | Exemplo |
|---------|--------|---------|
| Nomenclatura | `cry-{verbo}-{substantivo}` ou `cry-new-{pilar}` | `cry-translate`, `cry-new-lex` |
| Sintaxe | `/cry-nome <obrigatório> [opcional]` | `/cry-translate <arquivo> [idioma]` |
| Parâmetros posicionais | Obrigatórios primeiro, opcionais depois | `<arquivo> [idioma] [--flag]` |
| Flags | Prefixadas com `--` | `--order en,es` |

### Armadilhas Comuns

| Armadilha | Problema | Solução |
|-----------|----------|---------|
| Cry complexo | Muitos parâmetros obrigatórios | Reduzir a 1-2 obrigatórios, usar defaults |
| Cry sem Kata | Toda a lógica no prompt template | Extrair procedimento para um Kata |
| Cry com comandos externos sem Kata | Cry descreve "execute git X", "rode make Y" sem invocar um Kata que encapsule o fluxo | Criar o Kata (ex.: kata-sync, kata-rebase) e fazer o Cry invocá-lo; o Cry não pode ser o único lugar onde o procedimento está definido |
| Cry redundante | Duplica outro Cry existente | Verificar Cries existentes antes de criar |
| Prompt vago | "Faça algo com o arquivo" | Referenciar Kata específico e formato de saída |
| Sem exemplo | Usuário não sabe como usar | Sempre incluir exemplo com input e output |

### Cry vs Kata — Quando Criar Cada Um

| Característica | Cry | Kata |
|---------------|-----|------|
| Ponto de entrada | Usuário invoca diretamente | Agente executa internamente |
| Complexidade | Invocação simples (1 comando) | Procedimento multi-passo |
| Parâmetros | Do usuário (CLI-like) | Validados e processados |
| Contém lógica? | Não — delega para Kata | Sim — define os passos |
| Análogo | Comando shell | Script chamado pelo comando |

### Restrições Técnicas

- Todo Cry deve **referenciar e invocar pelo menos um Kata** (ou Warrior que orquestra Kata) que exista e execute o procedimento — Cry não contém lógica própria. **Violação:** Cry que descreve passos com comandos externos (git, make, etc.) sem invocar um Kata que encapsule esses passos; Cry com "Kata associado: kata-X — Pendente de criação" continua não conforme até que o Kata exista e o Cry o invoque.
- Todo Cry que envolva execução de ferramentas externas (git, make, npm, etc.) **DEVE** invocar um Kata que documente e execute esse fluxo; o Cry não pode ser o único lugar onde o procedimento está definido.
- A seção **Prompt Template** deve usar `{{variáveis}}` para parâmetros e referenciar explicitamente o Kata (e Warrior, se houver)
- O nome do arquivo deve usar o prefixo definido em `naming.prefixes.cries` (consultar `.ahrena/.directives`) e kebab-case: `{prefixo}-{nome-descritivo}.md`
- A estrutura deve seguir o template oficial: consultar `paths.samples.cries` em `.directives` (ex.: `templates/cry-sample.md`)
- A seção **Diferença de Kata** (ou equivalente) deve conter tabela comparativa Cry vs Kata para este comando

## Glossário

| Termo | Definição |
|-------|-----------|
| Prompt template | Texto parametrizado enviado ao agente quando o Cry é invocado |
| Default inteligente | Valor padrão derivado do `.directives` ou contexto |
| Cadeia de invocação | Sequência Cry → (Warrior) → Kata que define o fluxo de execução |
| Parâmetro posicional | Argumento identificado pela posição, não por nome |

## Referências

- `lex-pilars` — Lei que define canonicamente os Pilares; Cry invoca somente Kata(s) e/ou Warrior(s), nunca Lexis nem Codex
- `codex-pilars` — Visão do sistema de Pilares e checklists de validação (seção Validação de artefatos)
- `lex-directives` — Consulta obrigatória ao `.ahrena/.directives` (paths, naming.prefixes)
- `codex-katas` — Manual sobre Katas (para entender a diferença Cry vs Kata)
- `lex-template-usage` — Lei de uso obrigatório de templates
- `kata-create-cry` — Procedimento para criar novos Cries (consulta este Codex nos passos 1 e 3)
- `paths.samples.cries` em `.directives` — Caminho do template oficial (ex.: `templates/cry-sample.md`)
