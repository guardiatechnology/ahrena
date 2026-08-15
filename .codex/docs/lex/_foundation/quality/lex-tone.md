# Lexis: Tom e Estilo de Escrita Obrigatórios

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Produção de artefatos e comunicação no contexto Ahrena

## Lei

> **Todo agente DEVE aplicar as diretrizes de tom e estilo de escrita definidas em `naming.tone_and_writing_style` no arquivo `.ahrena/.directives` ao produzir artefatos (Lexis, Codex, Katas, Warriors, Cries), documentação e comunicação no contexto do Ahrena. Se a seção não existir, o agente DEVE adotar tom direto, estratégico e baseado em clareza e propósito.**

## Regras

### 1. Consulta às diretrizes

Ao produzir texto no contexto do Ahrena, o agente **DEVE**:

1. Consultar `.ahrena/.directives` (conforme `lex-directives`).
2. Verificar se existe a seção `naming.tone_and_writing_style`.
3. Se existir, internalizar cada item da lista e aplicá-lo ao redigir ou revisar conteúdo.
4. Se não existir, adotar princípios equivalentes: estilo direto e estratégico, clareza, dados e propósito; evitar adornos e abstrações que desviem do essencial.

### 2. Escopo de aplicação

O tom e o estilo aplicam-se a:

- Conteúdo de artefatos do framework (Lei, Propósito, Conteúdo, Exemplos, etc.).
- Documentação gerada no contexto do projeto (README, ADRs, comentários em código quando forem documentação).
- Comunicação produzida pelo agente em resposta a solicitações no contexto Ahrena (respostas, resumos, instruções).

Não se aplica a código-fonte (variáveis, funções) exceto quando o usuário solicitar que comentários ou documentação inline sigam o mesmo estilo.

### 3. Não modificação da seção sem autorização

O agente **NÃO PODE** adicionar ou alterar a seção `naming.tone_and_writing_style` em `.ahrena/.directives` sem solicitação explícita do usuário.

## Exemplos

### Alinhado ao tom (diretrizes típicas)

- Frase direta e com propósito: "Todo artefato DEVE usar o prefixo do Pilar."
- Evitar adornos: preferir "A Lei estabelece a obrigação" a "É importante destacar que a Lei vem estabelecer a obrigação."
- Apoiar em estrutura lógica: usar Why/What/How ou Problema/Causa/Solução quando fizer sentido.

### Desalinhado

- Texto vago: "A coisa deve ser feita de forma adequada."
- Buzzword sem significado: "Solução disruptiva e inovadora."
- Excesso de travessões ou dois-pontos para contextualizar: "O framework — que é muito importante — deve ser usado — sempre — da seguinte forma:"

## Validação Automatizada

- **Ferramenta:** revisão humana ou pelo próprio agente com checklist baseado em `codex-tone`.
- **Momento:** na criação ou revisão de artefatos e na entrega de comunicação.
- **Métrica:** conteúdo produzido deve estar em conformidade com as diretrizes de `tone_and_writing_style` quando a seção existir.
