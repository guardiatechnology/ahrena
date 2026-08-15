# Codex: Como Escrever Bons Warriors

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Criação de Warriors (agentes especializados)

## Conteúdo

### Princípios

1. **Identidade clara:** Um Warrior deve ter nome, papel e persona que o distinguem. A identidade não é cosmética — ela ancora o comportamento esperado.
2. **Escopo delimitado:** O que um Warrior "Faz" é tão importante quanto o que "Não Faz". Responsabilidades vagas levam a sobreposição e conflito entre Warriors.
3. **Consulta explícita:** Todo Warrior deve declarar quais Lexis segue, quais Codex consulta e quais Katas executa. Sem isso, o comportamento é imprevisível.
4. **Escalação definida:** Um Warrior deve saber quando parar e pedir ajuda humana. Autonomia sem limites é risco.
5. **Orquestração de Katas:** Um Warrior orquestra um ou mais Katas (seleciona, ordena, combina resultados). Pode consultar Lexis e Codex; não substitui a definição de um Kata — a lógica procedimental fica no Kata.

### Anatomia de um Bom Warrior

| Seção | Propósito | Critério de Qualidade |
|-------|-----------|----------------------|
| **Identidade** | Nome, papel, domínio e persona | Nomes memoráveis; persona que informa o tom |
| **Missão** | Propósito central em 1-2 frases | Específica e acionável |
| **Responsabilidades** | Faz / Não Faz | Listas balanceadas e sem ambiguidade |
| **Consulta** | Lexis, Codex e Katas referenciados | Tabelas com identificador e descrição |
| **Comportamento** | Tom, fluxo de atuação, escalação | Concreto e verificável |
| **Exemplo de Interação** | Cenário de uso real | Input do usuário + resposta do Warrior |

### Design de Identidade

A identidade de um Warrior orienta seu comportamento:

| Elemento | Função | Diretriz |
|----------|--------|----------|
| **Nome** | Identificação e memorabilidade | Nomes mitológicos, históricos ou simbólicos que evoquem o papel |
| **Papel** | O que faz em termos profissionais | Título claro (ex: "Arquiteto de Software", "Tradutor Especialista") |
| **Domínio** | Onde atua | Área específica (ex: "decisões arquiteturais e qualidade de código") |
| **Persona** | Como se comporta | 2-3 adjetivos que definem o tom (ex: "metódico, criterioso, focado em trade-offs") |

### Design de Responsabilidades

A seção "Faz" / "Não Faz" define o contorno do Warrior:

**Bom "Faz":**
- Elabora ADRs com análise de trade-offs
- Revisa PRs com foco em arquitetura

**Mau "Faz":**
- Ajuda com código (vago demais)
- Faz tudo relacionado a backend (escopo infinito)

**Bom "Não Faz":**
- Não toma decisões de produto (isso é do PM)
- Não faz deploy em produção (isso é DevOps)

**Mau "Não Faz":**
- Não faz coisas ruins (óbvio e inútil)

### Design da Cadeia de Consulta

Todo Warrior declara três tabelas de referência:

1. **Lexis** — as leis que obedece (sempre `lex-directives` + outras)
2. **Codex** — os manuais que consulta para tomar decisões
3. **Katas** — os procedimentos que executa

A cadeia deve ser completa: se o Warrior executa uma tarefa, deve haver um Kata correspondente. Se toma decisões sobre um domínio, deve haver um Codex correspondente.

### Design de Escalação

Critérios de escalação definem quando o Warrior para e pede ajuda:

| Tipo | Exemplo |
|------|---------|
| Impacto alto | "Decisão impacta mais de 3 módulos" |
| Custo financeiro | "Trade-off envolve custo significativo" |
| Conflito de regras | "Conflito entre Lexis e requisito de negócio" |
| Incerteza | "Informação insuficiente para tomar decisão" |

### Padrões e Convenções

| Aspecto | Padrão | Exemplo |
|---------|--------|---------|
| Nomenclatura | `warrior-{nome-em-kebab-case}` | `warrior-spartacus` |
| Nome do Warrior | Substantivo próprio memorável | Hermes, Spartacus, Athena |
| Missão | Máximo 2 frases em blockquote | > "Garantir que toda decisão arquitetural seja documentada..." |
| Exemplo de interação | Input real do usuário + resposta estruturada | Demonstra o tom e o fluxo do Warrior |

### Armadilhas Comuns

| Armadilha | Problema | Solução |
|-----------|----------|---------|
| Warrior genérico | "Assistente de código" — sem identidade | Definir papel, domínio e persona específicos |
| Escopo ilimitado | Faz tudo, não especializa em nada | Usar "Não Faz" para delimitar |
| Sem cadeia de consulta | Comportamento imprevisível | Declarar Lexis, Codex e Katas explicitamente |
| Sem escalação | Warrior decide coisas que não deveria | Definir critérios claros de quando parar |
| Persona decorativa | Nome mitológico sem conexão com o papel | Escolher nome que evoque a especialidade |

### Warrior vs Agente Genérico — Quando Criar

| Situação | Resposta | Por quê |
|----------|----------|---------|
| Tarefa recorrente com escopo contínuo | Warrior | Precisa de identidade e contexto persistente |
| Tarefa pontual executada por qualquer agente | Kata | Procedimento basta |
| Múltiplos agentes com mesma especialidade | Warrior | Evita reconfigurar contexto toda vez |
| Domínio com tom e comportamento específicos | Warrior | A persona garante consistência |

### Restrições Técnicas

- Todo Warrior deve incluir **pelo menos uma Lexis** na cadeia de consulta (`lex-directives` no mínimo)
- A seção **Exemplo de Interação** deve conter um cenário completo (input do usuário + resposta estruturada do Warrior)
- O nome do arquivo deve usar o prefixo definido em `naming.prefixes.warriors` (consultar `.ahrena/.directives`) e kebab-case: `{prefixo}-{nome}.md`
- A estrutura deve seguir o template oficial: consultar `paths.samples.warriors` em `.directives` (ex.: `templates/warrior-sample.md`)
- A **Missão** deve ser uma citação em blockquote (1–2 frases)
