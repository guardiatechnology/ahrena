# Codex: Sistema de Pilares do Ahrena

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Criação, validação e evolução de artefatos do framework

## Visão Geral

Este Codex é a referência central sobre o sistema de Pilares do Ahrena. Descreve a natureza de cada Pilar, como se relacionam entre si, como validar artefatos e como o framework utiliza seus próprios artefatos para evoluir — o conceito de autossuficiência. Operacionaliza a `lex-pilars` com critérios verificáveis e checklists de validação por Pilar. Para documentação detalhada de cada Pilar (como escrever bem, critérios de qualidade), consulte os Codex específicos: `codex-lexis`, `codex-codex`, `codex-katas`, `codex-warriors`, `codex-cries`.

## Contexto

- **Domínio:** Taxonomia, arquitetura e validação do framework Ahrena
- **Público-alvo:** Agentes de IA que criam ou validam artefatos; mantenedores do framework; revisores de PR
- **Atualização:** Sempre que um novo Pilar for criado, as relações entre Pilares mudarem ou a `lex-pilars` for alterada

## Conteúdo

### Os Cinco Pilares

O Ahrena organiza todo conhecimento em cinco Pilares, cada um com um papel distinto. O prefixo de cada Pilar é o valor definido em `naming.prefixes` em `.ahrena/.directives` (chaves: `lexis`, `codex`, `katas`, `warriors`, `cries`); quem define é o usuário ou o projeto.

| Pilar | Chave em naming.prefixes | Natureza | Pergunta que responde |
|-------|--------------------------|----------|----------------------|
| **Lexis** | `lexis` | Lei inquebrável | "O que é proibido ou obrigatório?" |
| **Codex** | `codex` | Manual de referência | "O que preciso saber sobre este domínio?" |
| **Katas** | `katas` | Procedimento repetível | "Como executo esta tarefa passo a passo?" |
| **Warriors** | `warriors` | Agente especializado | "Quem é responsável por este domínio?" |
| **Cries** | `cries` | Comando recorrente | "Como invoco esta ação rapidamente?" |

### Hierarquia de Autoridade

Os Pilares possuem uma hierarquia implícita de autoridade:

1. **Lexis** — autoridade máxima. Nenhum outro artefato pode contradizer uma Lexis. São absolutas.
2. **Codex** — fonte de verdade para conhecimento de domínio. Orienta decisões.
3. **Katas** — procedimentos que obedecem Lexis e consultam Codex.
4. **Warriors** — agentes que seguem Lexis, consultam Codex e executam Katas.
5. **Cries** — atalhos que disparam Katas ou invocam Warriors.

### Relações entre Pilares

```
Lexis ─────────── governa ──────────► todos os outros
Codex ─────────── informa ──────────► Katas, Warriors
Katas ─────────── executado por ────► Warriors, agentes genéricos
Warriors ─────── invocado por ──────► Cries, usuários
Cries ──────────── dispara ─────────► Katas (via Warriors ou diretamente)
```

Cada Pilar pode referenciar artefatos de outros Pilares:

| Pilar | Referencia | É referenciado por |
|-------|------------|--------------------|
| Lexis | — | Codex, Katas, Warriors |
| Codex | Lexis | Katas, Warriors |
| Katas | Lexis, Codex | Warriors, Cries |
| Warriors | Lexis, Codex, Katas | Cries |
| Cries | Katas, Warriors | — |

**Regras de invocação (resumo):**

| De (quem invoca) | Pode invocar / acessar |
|------------------|-------------------------|
| Cry | Apenas Kata(s) e/ou Warrior(s) |
| Warrior | Kata(s); pode consultar Lexis e Codex |
| Warrior Orquestrador | Kata(s) próprios **e** pode delegar fases a outros Warriors (via handoff por checkpoint) |
| Kata | Nenhum artefato como "invocação"; aplica Lexis e consulta Codex |

### Warrior Orquestrador (tipo especial)

Um **Warrior Orquestrador** é um Warrior cujo papel é coordenar um fluxo multi-fase que envolve outros Warriors especialistas. Diferente do Warrior comum, ele pode delegar fases específicas a outros Warriors via handoff documentado em `.ahrena/workflow/.../checkpoint.md`.

**Exemplo:** `warrior-athena` (clade `engineering/workflow/`) orquestra o fluxo Issue-Driven Development em 7 fases, delegando:
- Fase 3 (API) → `warrior-daedalus`
- Fase 3 (eventos) → `warrior-kronos`
- Fase 4 (implementação Python) → `warrior-apollo`

**Regras para Warriors Orquestradores:**
- Devem ter nome, identidade e persona como qualquer outro Warrior
- A delegação só ocorre via handoff por checkpoint (estado persistido), não por chamada direta
- O Warrior Orquestrador permanece responsável pela integridade global do fluxo, mesmo durante a delegação
- A delegação deve estar explicitamente documentada na seção "Warriors delegados" do próprio Warrior

Essa formalização evita encadeamento descontrolado entre Warriors e mantém a clareza das responsabilidades.

### Kit de Criação

Para que o framework seja autossuficiente, cada Pilar possui um **Kit de Criação** composto por:

| Peça | Pilar | Função |
|------|-------|--------|
| Codex do Pilar | Codex | Conhecimento sobre o que é e como escrever bem |
| Kata de criação | Kata | Procedimento passo a passo para criar um novo artefato |
| Cry de invocação | Cry | Atalho rápido para disparar a criação |

A cadeia de execução é:

```
/cry-new-{pilar} → kata-create-{pilar} → codex-{pilar} + template + lexis
```

### Como Decidir qual Pilar Usar

| Situação | Pilar | Justificativa |
|----------|-------|---------------|
| Preciso estabelecer uma regra absoluta que ninguém pode violar | **Lexis** | Leis não admitem exceções |
| Preciso documentar conhecimento de domínio para consulta | **Codex** | Base de conhecimento estruturada |
| Preciso padronizar como uma tarefa recorrente é executada | **Kata** | Procedimento com inputs, passos e outputs |
| Preciso de um agente dedicado com identidade e escopo | **Warrior** | Especialista com persona e responsabilidades |
| Preciso de um atalho rápido para uma ação do dia a dia | **Cry** | Invocação rápida de 1-2 passos |

Perguntas de refinamento:

- **É uma restrição absoluta?** → Lexis
- **É conhecimento para consulta?** → Codex
- **É um procedimento multi-passo?** → Kata
- **Precisa de persona e escopo contínuo?** → Warrior
- **É uma invocação simples e rápida?** → Cry

### Padrões e Convenções

| Aspecto | Padrão | Exemplo |
|---------|--------|---------|
| Nomenclatura de arquivo | `{prefixo}-{nome}.md` (prefixo em `naming.prefixes`) | Conforme `.directives` |
| Casing | kebab-case | `codex-framework-language.md` |
| Endereçamento | `{lang}/{clade}/{subclade}/{pilar}/{arquivo}` | `pt-BR/engineering/quality/lexis/lex-code-review.md` |
| Criação dual | framework (`.md`) + IDE (formato da plataforma) | `.md` + `.mdc` (Cursor) |

### Restrições Técnicas

- Todo artefato **DEVE** seguir o template oficial do seu Pilar (`paths.samples` em `.directives`)
- Todo artefato **DEVE** existir nos idiomas definidos em `language.i18n`
- O idioma padrão (`language.default`) é a fonte da verdade
- Nomes de arquivo usam o prefixo do Pilar definido em `naming.prefixes` e kebab-case
- Termos canônicos (Lexis, Codex, Katas, Warriors, Cries, Clade, Subclade, Pilar) nunca são traduzidos

---

### Validação de artefatos

Consulte sempre a `lex-pilars` como Lei; os critérios abaixo operacionalizam a validação.

**Como validar:**

1. **Identificar o Pilar pretendido** do artefato (pelo nome, diretório ou declaração do autor).
2. **Consultar a `lex-pilars`** para as regras inquebráveis daquele Pilar.
3. **Aplicar o checklist** abaixo para o Pilar correspondente.
4. **Verificar relações de invocação:** se o artefato for um Cry, confirmar que ele só invoca Kata(s) e/ou Warrior(s); se for um Kata, confirmar que aplica Lexis e Codex; se for um Warrior, confirmar que orquestra Katas.

#### Lexis

**Definição em uma frase:** Lexis é lei inquebrável que governa o framework; não admite exceção.

| Critério | Obrigatório |
|----------|-------------|
| Nome do arquivo usa o prefixo definido em `naming.prefixes.lexis` (consultar `.directives`) e kebab-case | Sim |
| Contém seção **Lei** com declaração imperativa (DEVE/NÃO PODE) | Sim |
| Contém seção **Abrangência** e **Exceções: Nenhuma** (ou equivalente) | Sim |
| Estrutura segue o template oficial (paths.samples.lexis) | Sim |
| Não é invocada por Cry como "ação" — Cry invoca Kata/Warrior que consultam Lexis | Sim |

**Não-conformidade:** Arquivo de Lexis que descreve recomendação em vez de obrigação; Lexis com cláusula de exceção; Cry cujo fluxo inclui "invocar" ou "executar" uma Lexis diretamente.

**Exemplo válido:** `lex-directives` — declara que todo agente DEVE ler `.ahrena/.directives`; sem exceções; consultada por outros artefatos, não invocada por Cry.

#### Codex

**Definição em uma frase:** Codex é manual de referência que organiza conhecimento para orientar decisões; é consultado, não executado.

| Critério | Obrigatório |
|----------|-------------|
| Nome do arquivo usa o prefixo definido em `naming.prefixes.codex` (consultar `.directives`) e kebab-case | Sim |
| Contém **Visão Geral**, **Contexto** e **Conteúdo** (ou equivalente ao template) | Sim |
| Natureza é referência/consulta; não descreve procedimento de execução passo a passo como foco principal | Sim |
| Estrutura segue o template oficial (paths.samples.codex) | Sim |
| Não é invocado por Cry como "ação" — Cry invoca Kata/Warrior que consultam Codex | Sim |

**Não-conformidade:** Artefato de Codex que é na prática um procedimento numerado (deveria ser Kata); Cry que "lê" ou "aplica" um Codex diretamente como única ação, em vez de invocar um Kata/Warrior.

**Exemplo válido:** `codex-lexis` — manual de como escrever boas Lexis; consultado por `kata-create-lexis`; não é invocado por Cry.

#### Katas

**Definição em uma frase:** Kata é procedimento repetível que aplica Lexis e consulta Codex para executar uma tarefa com entradas, passos e saídas definidos.

| Critério | Obrigatório |
|----------|-------------|
| Nome do arquivo usa o prefixo definido em `naming.prefixes.katas` (consultar `.directives`) e kebab-case | Sim |
| Contém objetivo, contexto de aplicação, entradas, processo (passos) e saídas (ou equivalente ao template) | Sim |
| Referencia Lexis e/ou Codex aplicáveis na seção de Referências ou no corpo | Sim |
| É invocado por Cries e/ou Warriors; não invoca outro Kata diretamente como "comando" (Warrior orquestra múltiplos Katas) | Sim |
| Estrutura segue o template oficial (paths.samples.katas) | Sim |

**Não-conformidade:** Artefato de Kata sem passos claros ou sem referência a Lex/Codex; Cry que executa lógica detalhada sem delegar a um Kata.

**Exemplo válido:** `kata-create-lexis` — passos numerados; consulta `codex-lexis` e template; invocado por `cry-new-lex`.

#### Warriors

**Definição em uma frase:** Warrior é agente especializado que orquestra um ou mais Katas e pode consultar Lexis e Codex; tem identidade (persona) e escopo definidos.

| Critério | Obrigatório |
|----------|-------------|
| Nome do arquivo usa o prefixo definido em `naming.prefixes.warriors` (consultar `.directives`) e kebab-case | Sim |
| Contém identidade (nome, domínio), responsabilidades e Katas que orquestra (ou equivalente ao template) | Sim |
| Referencia pelo menos uma Lexis (em geral `lex-directives`) e Codex/Katas aplicáveis | Sim |
| É invocado por Cries ou usuários; orquestra Katas (não substitui a definição de um Kata) | Sim |
| Estrutura segue o template oficial (paths.samples.warriors) | Sim |

**Não-conformidade:** Artefato de Warrior que não orquestra nenhum Kata; Cry que invoca um Warrior inexistente ou que descreve lógica que deveria estar em um Kata.

**Exemplo válido:** `warrior-translator` — orquestra `kata-translate`; consulta Lexis e Codex de i18n; invocado por `cry-translate`.

#### Cries

**Definição em uma frase:** Cry é comando de execução de alto nível que invoca somente Katas e/ou Warriors; nunca invoca Lexis nem acessa Codex diretamente.

| Critério | Obrigatório |
|----------|-------------|
| Nome do arquivo usa o prefixo definido em `naming.prefixes.cries` (consultar `.directives`) e kebab-case | Sim |
| Documenta claramente qual Kata e/ou qual(is) Warrior é(são) invocado(s) | Sim |
| Não contém instrução para "invocar" ou "executar" uma Lexis | Sim |
| Não contém instrução para "aplicar" ou "ler" um Codex como ação única do comando (o Codex é consultado pelo Kata/Warrior invocado) | Sim |
| Se invoca múltiplos Katas, há um Warrior que orquestra esses Katas ou o Cry descreve a ordem e delega a um Warrior | Sim |
| Estrutura segue o template oficial (paths.samples.cries) | Sim |

**Não-conformidade:** Cry cujo prompt diz "leia a lex-X e aplique"; Cry que "consulte o codex-Y e faça X" sem invocar um Kata ou Warrior que encapsule essa consulta e ação.

**Exemplo válido:** `cry-new-lex` — invoca `kata-create-lexis`; o Kata, por sua vez, consulta `codex-lexis` e Lexis. O Cry não acessa Codex nem Lexis diretamente.

---

### Artefatos no projeto (.ahrena)

Artefatos podem ser criados primeiro no **espaço do projeto** (`.ahrena/artifacts/`), específicos para aquele repositório. Isso permite iterar e validar antes de incorporar ao framework canônico.

| Aspecto | Projeto (`.ahrena/artifacts/`) | Framework (`framework/`) |
|---------|-------------------------------|--------------------------|
| **Uso** | Específico do projeto; validação local | Parte do repositório Ahrena; compartilhado |
| **Estrutura** | Mesma do framework: `{lang}/{clade}/{subclade}/{pilar}/{prefixo}-{nome}.md` | `framework/{lang}/{clade}/{subclade}/{pilar}/` |
| **Idiomas** | Pode existir só no idioma padrão; ao fazer Push, os demais são gerados se faltarem | **DEVE** existir em todos os idiomas de `language.i18n` |
| **Quando criar aqui** | Regras ou procedimentos ainda em validação; artefatos que podem nunca ir para o framework | Artefatos estáveis e aprovados para o framework |

**Fluxo recomendado:**

1. **Criar no projeto:** use os Katas de criação (`kata-create-lexis`, `kata-create-codex`, etc.) com destino **projeto** — o artefato é salvo em `.ahrena/artifacts/{lang}/{clade}/{subclade}/{pilar}/`.
2. **Sincronizar .cursor local:** execute `python .ahrena/update.py --sync-cursor` (ou `make sync-cursor`). O update regera `.cursor/` a partir de `.ahrena/framework/` e `.ahrena/artifacts/`.
3. **Validar e comparar (opcional):** use `kata-diff-artifacts --local` para ver diferenças entre `.ahrena/artifacts` e `framework/` local; use `kata-diff-artifacts --remote` para comparar com a versão mais recente do framework no remoto.
4. **Push para o framework:** execute `kata-push-to-framework` (ou `cry-push-to-framework`) com **--local** (cópia para `framework/` no repo atual) ou **--remote** (sincronização com o repositório do framework no GitHub).
5. **Atualizar instalação:** execute `python .ahrena/update.py` (e opcionalmente `--sync-cursor`) para trazer a versão mais recente do framework.

**Push: modo local e modo remoto**

- **Local:** o repo atual contém (ou tem acesso a) a pasta `framework/`. Push = copiar `.ahrena/artifacts/` para `paths.framework`, completar i18n e opcionalmente remover do projeto. Não usa rede.
- **Remoto:** em projeto consumidor, o framework está no GitHub. Push = enviar alterações ao repositório do framework usando **obrigatoriamente o MCP do GitHub** (branch, push, abertura de PR). O agente **DEVE** usar as ferramentas MCP do GitHub para todas as operações remotas.

O path canônico do espaço de projeto é definido em `paths.project_artifacts` em `.ahrena/.directives` (valor padrão: `.ahrena/artifacts/`).

## Glossário

| Termo | Definição |
|-------|-----------|
| Pilar | Uma das cinco categorias de artefato do Ahrena |
| Clade | Primeiro nível de organização temática (ex: engineering, documentation) |
| Subclade | Segundo nível de organização dentro de um Clade (ex: quality, i18n) |
| Kit de Criação | Conjunto Codex + Kata + Cry que permite criar novos artefatos de um Pilar |
| Criação dual | Padrão de criar o artefato canônico (`.md`) e a versão derivada para a IDE |
| Endereçamento | Caminho completo de um artefato na taxonomia do framework |
| Artefatos de projeto | Artefatos criados em `.ahrena/artifacts/`, específicos do repositório, antes de serem incorporados ao framework |
| Push para o framework | Procedimento (kata-push-to-framework) que incorpora artefatos de `.ahrena/artifacts/` ao framework, em modo **local** (cópia para `framework/` no repo) ou **remoto** (sincronização com o repositório do framework no GitHub). |
| Diff de artefatos | Procedimento (kata-diff-artifacts) que compara `.ahrena/artifacts` e framework em modo **local** (vs framework local) ou **remoto** (vs versão mais recente do framework no remoto). |
| Validação de Pilar | Verificação de que um artefato satisfaz a definição e os critérios do Pilar a que pertence |
| Cadeia de invocação | Sequência Cry → (Warrior) → Kata; Lexis e Codex são consultados, não invocados pelo Cry |
| Definição canônica | Definição estabelecida na `lex-pilars` e operacionalizada neste Codex |

## Referências

- `lex-pilars` — Lei que define canonicamente os cinco Pilares e as regras de invocação (fonte da verdade para validação)
- `.ahrena/.directives` — Diretivas canônicas do framework (paths, naming.prefixes)
- `lex-template-usage` — Lei de uso obrigatório de templates
- `lex-framework-language` — Lei de estrutura de idiomas
- `codex-lexis`, `codex-codex`, `codex-katas`, `codex-warriors`, `codex-cries` — Documentação detalhada de cada Pilar (como escrever bem, critérios de qualidade)
