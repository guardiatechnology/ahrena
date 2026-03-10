# Lexis: Uso Obrigatório de Templates

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Criação de qualquer artefato do Ahrena

## Propósito

O Ahrena mantém templates oficiais (samples) para cada Pilar da taxonomia — Lexis, Codex, Katas, Warriors e Cries. Esses templates garantem consistência estrutural, completude de informações e padronização entre todos os artefatos do framework.

Sem essa padronização, agentes podem gerar artefatos com seções faltantes, estrutura inconsistente ou nomenclatura divergente, comprometendo a interoperabilidade e a governança do sistema.

Esta Lexis existe para garantir que **todo novo artefato seja criado a partir do template oficial correspondente**, preservando a integridade estrutural do framework.

## Lei

> **Todo agente DEVE utilizar o template oficial (sample) do Pilar correspondente como base estrutural ao criar qualquer novo artefato do Ahrena — Lexis, Codex, Kata, Warrior ou Cry.**

## Regras

### 1. Template obrigatório por Pilar

Antes de criar um novo artefato, o agente **DEVE** consultar o template (sample) correspondente ao Pilar. Os caminhos canônicos estão em `.ahrena/.directives` na seção `paths.samples` (ex.: `paths.samples.lexis`, `paths.samples.codex`, etc.). Valores típicos no repositório Ahrena:

| Pilar | Template (paths.samples em .directives) | Template (.cursor/) |
|-------|----------------------------------------|---------------------|
| **Lexis** | `templates/lex-sample.md` | `.cursor/rules/samples/lex-sample.mdc` |
| **Codex** | `templates/codex-sample.md` | `.cursor/rules/samples/codex-sample.mdc` |
| **Katas** | `templates/kata-sample.md` | `.cursor/skills/samples/kata-sample.mdc` |
| **Warriors** | `templates/warrior-sample.md` | `.cursor/skills/samples/warrior-sample.mdc` |
| **Cries** | `templates/cry-sample.md` | `.cursor/commands/samples/cry-sample.mdc` |

O agente **DEVE** usar os valores de `paths.samples` do `.directives` quando disponíveis; a tabela acima reflete a convenção padrão.

### 2. Processo de criação

Ao receber uma solicitação para criar um novo artefato, o agente **DEVE**:

1. **Identificar o Pilar** — determinar se o artefato é uma Lexis, Codex, Kata, Warrior ou Cry.
2. **Ler o template** — carregar o conteúdo do sample correspondente usando a tabela acima.
3. **Usar como base estrutural** — criar o novo artefato mantendo todas as seções, headings e estrutura do template.
4. **Preencher os campos** — substituir os campos entre colchetes `[]` pelo conteúdo específico do artefato.
5. **Remover instruções do template** — eliminar textos explicativos genéricos do sample (ex: "Descreva por que esta lei existe") e substituí-los pelo conteúdo real.
6. **Respeitar o endereçamento** — salvar no caminho correto conforme a taxonomia: `<clade>/<subclade>/<pilar>/<prefixo>-<nome>.md`.

### 3. Estrutura inviolável

O agente **NÃO PODE**:

- Omitir seções obrigatórias definidas no template.
- Inventar uma estrutura própria ignorando o template.
- Alterar os headings padrão do template (pode adicionar sub-seções, nunca remover as existentes).

### 4. Criação dual (framework + IDE)

Quando o contexto exigir, o agente **DEVE** criar o artefato em ambos os locais:

- **`framework/`** — versão canônica em `.md` puro, sem frontmatter de IDE.
- **`.cursor/`** (ou outra IDE) — versão derivada em `.mdc` com frontmatter YAML apropriado.

### 5. Frontmatter obrigatório no `.cursor/`

Ao criar a versão `.mdc` para o Cursor, o agente **DEVE** incluir o frontmatter YAML correto no início do arquivo, delimitado por `---`. O frontmatter varia conforme o recurso Cursor utilizado:

#### Rules (Lexis e Codex)

```yaml
---
description: "Descrição concisa do que a rule faz e quando deve ser consultada."
globs: "padrão/glob/se/aplicável"
alwaysApply: false
---
```

| Campo | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `description` | Sim | Texto que o Cursor exibe para o agente entender quando consultar esta rule |
| `globs` | Condicional | Padrão glob de arquivos aos quais a rule se aplica. **Omitir ou deixar vazio** quando a rule se aplica a todos os arquivos ou não é vinculada a tipos de arquivo específicos |
| `alwaysApply` | Sim | `true` se a rule deve ser carregada em toda interação; `false` se deve ser ativada sob demanda ou por glob |

#### Skills (Katas e Warriors)

```yaml
---
name: prefixo-nome
description: "Descrição concisa do que a skill faz e quando deve ser usada."
---
```

| Campo | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `name` | Sim | Identificador da skill, usando o prefixo do Pilar (ex: `kata-code-review`, `warrior-spartacus`) |
| `description` | Sim | Texto que o Cursor exibe para o agente entender quando ativar esta skill |

#### Commands (Cries)

```yaml
---
description: "Descrição concisa do que o comando faz ao ser invocado."
---
```

| Campo | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `description` | Sim | Texto que o Cursor exibe para o usuário entender o que o comando faz |

### 6. Prefixo obrigatório

Todo artefato **DEVE** usar o prefixo correto do seu Pilar no nome do arquivo:

| Pilar | Prefixo | Exemplo |
|-------|---------|---------|
| Lexis | `lex-` | `lex-no-secrets.md` |
| Codex | `codex-` | `codex-architecture.md` |
| Katas | `kata-` | `kata-code-review.md` |
| Warriors | `warrior-` | `warrior-spartacus.md` |
| Cries | `cry-` | `cry-changelog.md` |

## Abrangência

- **Aplica-se a:** criação de qualquer artefato em qualquer Clade e Subclade
- **Agentes vinculados:** todos os Warriors e agentes genéricos
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Rejeição do artefato:** artefatos criados sem seguir o template oficial devem ser reescritos antes de serem aceitos.
2. **Inconsistência estrutural:** artefatos fora do padrão comprometem a navegabilidade e a governança do framework.
3. **Remediação:** o agente deve recriar o artefato usando o template correto, preservando o conteúdo já produzido mas adequando-o à estrutura padrão.

## Exemplos

### Correto

```
Usuário: Crie uma nova Lexis sobre code review obrigatório.

Agente:
1. Identifica o Pilar: Lexis
2. Lê o template: framework/lexis/lex-sample.md
3. Cria o artefato seguindo a estrutura:
   - # Lexis: Code Review Obrigatório
   - > Prefixo: lex- | Tipo: Lei Inquebável | Escopo: ...
   - ## Propósito
   - ## Lei
   - ## Abrangência
   - ## Consequências de Violação
   - ## Exemplos
   - ## Validação Automatizada
4. Salva em: engineering/quality/lexis/lex-code-review.md
5. Cria versão .cursor com frontmatter:
   ---
   description: "Code review obrigatório. Todo PR deve passar por revisão antes do merge."
   alwaysApply: false
   ---
6. Salva em: .cursor/rules/engineering/quality/lex-code-review.mdc
```

### Incorreto

```
Usuário: Crie uma nova Lexis sobre code review obrigatório.

Agente: Aqui está a lei:

# Lei de Code Review
Todo PR precisa de review.

# ❌ O agente ignorou o template, criou estrutura própria,
# omitiu seções obrigatórias e não seguiu o prefixo correto.
# A versão .mdc foi criada sem frontmatter YAML.
```

## Validação Automatizada

- **Ferramenta:** verificação pelo próprio agente antes de salvar o artefato
- **Momento:** durante a criação de qualquer novo artefato do Ahrena
- **Métrica:** 100% dos artefatos devem seguir a estrutura do template oficial do seu Pilar
