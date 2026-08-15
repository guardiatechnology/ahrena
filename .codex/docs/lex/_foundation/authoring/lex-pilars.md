# Lexis: Definição Canônica dos Pilares

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Estrutura e validação de artefatos do framework Ahrena

## Lei

> **Todo artefato do framework Ahrena DEVE pertencer a exatamente um Pilar e DEVE satisfazer a definição e as regras canônicas desse Pilar estabelecidas nesta Lexis. Toda invocação entre artefatos DEVE respeitar as regras de invocação definidas nesta Lexis.**

### Identificação do Pilar pelo prefixo

A forma segura de identificar se um artefato é Lexis, Codex, Kata, Warrior ou Cry é **observar o prefixo definido na diretiva**: o agente DEVE consultar `naming.prefixes` em `.ahrena/.directives` e usar os valores ali configurados (chaves `lexis`, `codex`, `katas`, `warriors`, `cries`) para validar nomes e classificar artefatos. O agente NÃO DEVE assumir que os prefixos serão sempre valores fixos (ex.: `lex-`, `codex-`); quem define é o usuário ou o projeto no `.directives`.

## Regras por Pilar

### 1. Lexis

- **Definição:** Lexis é lei inquebrável; não admite exceção.
- **Prefixo obrigatório:** o valor definido em `naming.prefixes.lexis` em `.ahrena/.directives`. Quem define o prefixo é o usuário/projeto; o agente identifica que um artefato é Lexis observando se o nome do arquivo usa o prefixo configurado para esse Pilar.
- **Estrutura:** DEVE seguir o template oficial do Pilar (`paths.samples.lexis` em `.directives`).
- **Autoridade:** Lexis governa todos os outros Pilares; nenhum artefato pode contradizer uma Lexis.
- **Invocação:** Lexis não é invocada por Cries; é consultada por Codex, Katas e Warriors.

### 2. Codex

- **Definição:** Codex é manual de referência; organiza conhecimento para orientar decisões.
- **Prefixo obrigatório:** o valor definido em `naming.prefixes.codex` em `.ahrena/.directives`. A identificação do Pilar é feita pelo prefixo configurado, não por valor fixo.
- **Estrutura:** DEVE seguir o template oficial do Pilar (`paths.samples.codex`).
- **Papel:** Informa Katas e Warriors; não é executado diretamente (não é invocado como procedimento).
- **Invocação:** Codex não é invocado por Cries; é consultado por Katas e Warriors.

### 3. Katas

- **Definição:** Kata é procedimento repetível (habilidade) que aplica Lexis e consulta Codex para executar uma tarefa clara e reproduzível.
- **Prefixo obrigatório:** o valor definido em `naming.prefixes.katas` em `.ahrena/.directives`. A identificação do Pilar é feita pelo prefixo configurado.
- **Estrutura:** DEVE seguir o template oficial do Pilar (`paths.samples.katas`).
- **Dependência:** Kata aplica Lexis e consulta Codex; não contém lógica que contradiga Lexis nem ignora Codex aplicável.
- **Invocação:** Kata é invocado por Cries (diretamente ou via Warrior) ou por Warriors.

### 4. Warriors

- **Definição:** Warrior é agente especializado que orquestra um ou mais Katas e pode consultar Lexis e Codex.
- **Prefixo obrigatório:** o valor definido em `naming.prefixes.warriors` em `.ahrena/.directives`. A identificação do Pilar é feita pelo prefixo configurado.
- **Estrutura:** DEVE seguir o template oficial do Pilar (`paths.samples.warriors`).
- **Papel:** Orquestra Katas (seleciona, ordena, combina resultados); pode consultar Lexis e Codex.
- **Invocação:** Warrior é invocado por Cries ou por usuários; não é invocado por outro Warrior como artefato formal (a não ser que o Cry instrua o agente a assumir o papel de outro Warrior).

### 5. Cries

- **Definição:** Cry é comando de execução de alto nível que ativa habilidades ou agentes.
- **Prefixo obrigatório:** o valor definido em `naming.prefixes.cries` em `.ahrena/.directives`. A identificação do Pilar é feita pelo prefixo configurado.
- **Estrutura:** DEVE seguir o template oficial do Pilar (`paths.samples.cries`).
- **Regra de invocação (inquebrável):** Cry **NÃO PODE** invocar Lexis. Cry **NÃO PODE** acessar Codex diretamente. Cry **SOMENTE** invoca Katas e/ou Warriors.
- **Relação:** Um Cry pode invocar um Kata (relação um-para-um) ou um ou mais Warriors (um-para-muitos). Se um Cry precisar invocar múltiplos Katas, DEVE existir um Warrior que orquestre esses Katas.

## Hierarquia de autoridade

1. **Lexis** — autoridade máxima; não pode ser contradita.
2. **Codex** — fonte de verdade para conhecimento; orienta Katas e Warriors.
3. **Katas** — executam aplicando Lexis e consultando Codex.
4. **Warriors** — orquestram Katas; consultam Lexis e Codex.
5. **Cries** — disparam Katas ou Warriors; nunca Lexis nem Codex.

## Exemplos

### Correto

- Cry `cry-translate` invoca o Warrior `warrior-translator`, que executa o Kata `kata-translate`; o Kata consulta Lexis e Codex de tradução.
- Cry `cry-new-lex` invoca o Kata `kata-create-lexis`; o Kata consulta `codex-lexis` e o template de Lexis; não há invocação de Lexis pelo Cry.

### Incorreto

- Cry cujo prompt instrui o agente a "ler a lex-directives e aplicar" sem invocar um Kata ou Warrior que encapsule esse procedimento — a leitura da Lex é uso pelo Kata/Warrior, não "invocação" do Cry à Lex; o Cry deve invocar um Kata ou Warrior. (Se o Cry apenas dispara um Kata que por sua vez consulta Lexis, está correto.)
- Artefato nomeado `guide-api.md` sem o prefixo do Pilar Codex (definido em `naming.prefixes.codex`) no diretório de codex — viola naming.

## Validação Automatizada

- **Ferramenta:** verificação pelo agente ou revisor com base em `lex-pilars` e `codex-pilars`; possível extensão futura com script de validação de naming e de referências.
- **Momento:** na criação de artefato (kata-create-*), na revisão de PR e na validação de Cries.
- **Métrica:** 0 artefatos fora da definição do seu Pilar; 0 Cries que invoquem Lexis ou acessem Codex diretamente.
