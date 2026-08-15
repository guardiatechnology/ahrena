# Codex: Tom e Estilo de Escrita

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Aplicação de tone_and_writing_style no Ahrena

## Conteúdo

### Origem das diretrizes

As diretrizes estão em `.ahrena/.directives`, seção `naming.tone_and_writing_style`, em geral como uma lista de frases. Cada item é uma regra de estilo que o agente deve seguir. A `lex-tone` exige que todo agente as aplique; este Codex explica como.

### Interpretação das diretrizes típicas

| Diretriz (exemplo) | Interpretação | Aplicação |
|--------------------|---------------|-----------|
| Estilo direto e estratégico, guiado por clareza, dados e propósito | Evitar rodeios; estruturar argumentos com lógica; usar Why/What/How ou Problema/Causa/Solução quando útil | Introduções e conclusões objetivas; seções com tópicos claros |
| Evitar adornos ou abstrações que desviem do essencial | Cortar frases decorativas; cada frase deve acrescentar informação ou ação | Remover "É importante notar que...", "Vale destacar..." quando não forem necessários |
| Apoiar afirmações com números, evidências ou referências verificáveis | Quando fizer sentido, citar métricas, fontes ou critérios concretos | Em seções de Validação, Consequências, Exemplos |
| Tom que combine confiança, acessibilidade e visão prática | Escrever com segurança sem ser arrogante; ser útil e acionável | Instruções no imperativo ("DEVE", "Consulte"); evitar hesitação desnecessária |
| Ambição ligada à viabilidade | Grandes ideias acompanhadas de passos concretos | Em propósitos e objetivos: não só "o que" mas "como" quando relevante |
| Evitar travessões ou dois-pontos para contextualizar (a menos que pedido) | Usar parênteses para nuances dentro da frase; reservar reticências para interrupção ou continuação | Preferir "O agente deve consultar o arquivo (conforme lex-directives)" a "O agente deve — conforme lex-directives — consultar o arquivo" |
| Eliminar buzzwords sem significado | Usar vocabulário técnico só quando necessário e com conceito claro | Evitar "solução disruptiva", "inovação" vaga; preferir termos precisos |
| Respostas que ajudem a decidir e avançar | Texto deve orientar decisão ou ação, não apenas informar | Incluir "Próximo passo", "Recomendação" ou conclusão acionável quando fizer sentido |
| Para e-mails, posts ou conteúdo para terceiros: entregar só o texto final | Quando o usuário pedir redação para compartilhar, não acrescentar comentário ou introdução; apenas o conteúdo pronto | Respeitar pedidos explícitos de "apenas o texto" ou "pronto para enviar" |

### Exemplos: alinhado vs desalinhado

**Alinhado:**

- "Todo artefato DEVE usar o prefixo do Pilar definido em `.directives`."
- "Se a seção `terminal` não existir, o agente infere pelo sistema operacional ou pergunta ao usuário."
- "A cadeia de invocação é: Cry → (Warrior) → Kata. Lexis e Codex são consultados, não invocados pelo Cry."

**Desalinhado:**

- "É fundamental que os artefatos utilizem o prefixo correto." (menos imperativo; preferir "DEVE")
- "Quando não houver terminal, pode-se inferir ou perguntar." (vago; especificar agente e ação)
- "A coisa toda funciona assim: o Cry chama algo, e aí Lexis e Codex entram na história." (informal e impreciso)

### Por tipo de artefato

| Tipo | Foco do tom |
|------|-------------|
| Lexis | Declaração imperativa clara; consequências concretas; sem exceções |
| Codex | Referência objetiva; tabelas e listas; gatilhos de atualização explícitos |
| Katas | Passos acionáveis; inputs/outputs claros; validação verificável |
| Warriors | Identidade e escopo nítidos; "Faz" e "Não Faz" concretos |
| Cries | Descrição em uma frase; prompt template com tarefa e formato de saída |

### Restrições técnicas

- O agente não deve inventar diretrizes; deve aplicar apenas as listadas em `naming.tone_and_writing_style` (ou o equivalente padrão quando a seção não existir).
- Em caso de conflito entre duas diretrizes, priorizar clareza e ação (o que ajuda mais o leitor a decidir ou executar).
