# Kata: Redigir Cenários BDD de Negócio a partir da Issue e do Notion

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Independente — produz cenários BDD focados em negócio a partir de uma issue do GitHub e do Notion, e os escreve de volta no corpo da issue

## Objetivo

Ler uma issue do GitHub (e páginas relacionadas no Notion quando o MCP estiver configurado), produzir uma lista de cenários Gherkin focados em negócio e persisti-los no corpo da issue dentro dos marcadores `<!-- bdd:scenarios:start -->` / `<!-- bdd:scenarios:end -->`. A kata nunca lê código-fonte de aplicação ou de testes; os cenários codificam a intenção de negócio, não uma descrição do que a implementação já faz.

## Quando Usar

- Antes do início da implementação, em uma feature na qual BDD agrega valor (tier-1, domínio regulado, regras de negócio complexas).
- Invocada através de `/cry-bdd-create-scenarios <issue>`.
- Opcional e independente — independente de `/cry-implement-issue` e do Gate 2.

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Número da issue | Sim | Número da issue no GitHub (ex.: `42`) |
| Repositório | Sim | `owner/repo` (padrão: detectado via git remote) |
| Raiz do Notion | Não | Página de contexto no Notion; padrão: `knowledge.notion.root_page` em `.directives` |
| Confirmação do usuário | Sim | Confirmação explícita antes da kata escrever na issue via MCP |

## Workflow

```
Progresso:
- [ ] 1. Verificar MCP e diretivas
- [ ] 2. Ler a issue (título, corpo, comentários)
- [ ] 3. Buscar contexto no Notion, se disponível
- [ ] 4. Detectar cenários API/UI existentes no corpo da issue
- [ ] 5. Redigir cenários focados em negócio (duplicar, não substituir)
- [ ] 6. Executar validação de linguagem (sem verbos HTTP, status codes, formatos de payload)
- [ ] 7. Apresentar o bloco bdd:scenarios proposto ao usuário
- [ ] 8. Sob confirmação, atualizar o corpo da issue via GitHub MCP
- [ ] 9. Reportar títulos e slugs dos cenários ao usuário
```

### Passo 1: Verificar MCP e diretivas

1. Ler `.ahrena/.directives` conforme `lex-directives`.
2. Confirmar que `github` está em `mcp.servers` (conforme `lex-mcp`); sem isso, parar e informar o usuário.
3. Confirmar que `notion` está em `mcp.servers` (opcional). Quando ausente, prosseguir sem enriquecimento via Notion e informar ao usuário que o contexto virá apenas da issue.
4. Confirmar variáveis de ambiente: `GITHUB_PAT` (obrigatória); `NOTION_API_KEY` (quando Notion está no escopo).

### Passo 2: Ler a issue

1. Usar `kata-mcp-github-read` para buscar a issue: título, corpo, labels, assignees, comentários.
2. Parar se a issue não existir ou tiver corpo vazio.
3. Se o corpo já contiver um bloco `<!-- bdd:scenarios:start -->`, capturar o conteúdo atual para fins de diff (reexecuções são merges, não sobrescritas cegas).
4. **Código-fonte é proibido.** Sem `git show`, sem Read em `src/`, `tests/`, `app/`, `domain/`, etc. A perspectiva da kata é o que o negócio quer; código responde a uma pergunta diferente.

### Passo 3: Buscar contexto no Notion (opcional)

Quando `notion` está ativo:

1. Extrair termos de domínio do título e do corpo da issue (nomes de entidades, operações, papéis).
2. Usar `kata-mcp-notion-read` em modo `search` para 3-5 termos de alto sinal (evitar custo excessivo).
3. Para hits relevantes, buscar em modo `page` com profundidade `full`.
4. Filtrar por estratégia de produto, regras de negócio e decisões anteriores de produto. Pular páginas irrelevantes.
5. Registrar: título da página, URL, trecho relevante.

### Passo 4: Detectar cenários API/UI existentes

1. Procurar no corpo da issue por blocos cercados ```gherkin e por marcadores `Scenario:`.
2. Capturá-los como **cenários API/UI** (saída original dos templates). Mantê-los.
3. Eles servem de semente para a duplicação em forma de negócio (Passo 5).
4. O agente não modifica nem remove os originais.

### Passo 5: Redigir cenários de negócio

Para cada comportamento implícito na issue e no contexto do Notion:

1. Identificar o ator em termos de domínio (cliente, operador, sistema atuando por conta própria — nunca "a API" ou "o user agent").
2. Identificar a ação em termos de domínio (solicitar um reembolso, agendar uma transferência, aprovar uma liberação — nunca um verbo HTTP).
3. Identificar o resultado observável (um registro é criado, uma notificação é despachada, ocorre uma transição de estado — nunca um status code ou formato de payload).
4. Escrever o cenário em Gherkin:

```gherkin
Scenario: <Title in product language>
  Given <precondition stated in domain terms>
  When <action stated in domain terms>
  Then <observable business outcome>
  And <additional outcome, if any>
```

5. Cobrir happy path, principais casos de erro/borda, e idempotência ou replay quando relevante.
6. Não inventar regras ausentes da issue ou do Notion; em vez disso, listá-las em uma sub-seção `## Pending Questions` dentro do mesmo bloco.

### Passo 6: Validação de linguagem

Rejeitar qualquer linha redigida que contenha:

- Verbos HTTP em caixa alta (`POST`, `GET`, `PUT`, `PATCH`, `DELETE`).
- Status codes quando adjacentes a "status", "code" ou "returns" (regex `\b[1-5]\d{2}\b`).
- Tokens de formato de payload (`{` / `}` cercando chaves no formato de campo; `Content-Type`, `Accept`, `Idempotency-Key`).
- Seletores DOM/UI (`#`, `.`, `[data-`).
- Nomes de framework de implementação (`fastapi`, `react`, `redis`, `kafka` quando usados como elemento de `Then`).

Para cada rejeição: reescrever a linha em termos de negócio, ou escalar o conflito ao usuário.

### Passo 7: Apresentar o bloco proposto

Mostrar ao usuário o bloco `bdd:scenarios` proposto, junto a quaisquer cenários API/UI existentes que permanecerão inalterados. Aguardar confirmação explícita ("sim, atualize a issue") antes de prosseguir.

### Passo 8: Atualizar o corpo da issue

1. Se o corpo da issue já tiver um bloco `<!-- bdd:scenarios:start -->` ... `<!-- bdd:scenarios:end -->`, substituir o conteúdo dele in-place.
2. Caso contrário, anexar o bloco ao final do corpo, precedido por uma linha em branco.
3. Usar GitHub MCP `update_issue` (ou equivalente) com o novo corpo. Não alterar título, labels, assignees ou qualquer outro campo.
4. Formato do bloco:

```
<!-- bdd:scenarios:start -->
## BDD Scenarios (Business)

Scenario: ...
  Given ...
  When ...
  Then ...

Scenario: ...
  Given ...
  When ...
  Then ...

## Pending Questions (optional)
- ...
<!-- bdd:scenarios:end -->
```

### Passo 9: Reportar

Imprimir ao usuário: lista de títulos de cenários, seus slugs (para uso como marcadores de teste), a URL para a issue atualizada e quaisquer questões pendentes capturadas.

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Lista de cenários com slugs | Resposta em Markdown | Visível ao usuário |
| Corpo da issue atualizado | Issue do GitHub | Repositório remoto (via MCP) |

## Restrições

- **Código é proibido como fonte.** A kata não pode executar nenhuma ferramenta que leia código-fonte ou código de teste.
- **Originais são preservados.** Cenários API/UI já presentes na issue são duplicados em forma de negócio, nunca modificados ou removidos.
- **Atualização idempotente do bloco.** Reexecutar a kata substitui apenas o bloco `bdd:scenarios`; o restante do corpo permanece intacto.
- **Confirmação obrigatória.** Sem atualização da issue sem confirmação explícita do usuário; essa ação é visível a outros.
- **Sem regras de negócio inventadas.** Qualquer coisa não presente na issue ou no Notion vai para `Pending Questions`, não para um `Scenario:`.

## Referências

- `lex-bdd-scenarios` — lei de redação (fontes, linguagem, persistência)
- `lex-bdd-coverage` — lei de cobertura (usada a jusante pela kata de validação)
- `codex-bdd` — metodologia, convenções de marcadores, anti-patterns
- `lex-mcp`, `kata-mcp-github-read`, `kata-mcp-notion-read` — regras de uso de MCP
- `kata-bdd-validate-scenarios` — procedimento sucessor (após a implementação)
