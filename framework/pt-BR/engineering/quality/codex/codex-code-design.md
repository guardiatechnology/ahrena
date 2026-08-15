# Codex: Design de Código e Clean Code

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Decisões de design, legibilidade e refatoração em qualquer stack

## Visão Geral

Este Codex transforma Clean Code em critérios de decisão. Ele não prescreve uma estética universal: orienta como equilibrar intenção, coesão, acoplamento, simplicidade, evolução e risco operacional.

## Contexto

- **Domínio:** design interno de software e refatoração segura
- **Público-alvo:** agentes e pessoas que implementam ou revisam código
- **Atualização:** quando os analisadores, a arquitetura canônica ou o dicionário de patterns do Ahrena mudar

## Conteúdo

### Princípios

1. **Intenção antes de concisão:** o leitor deve entender a decisão de negócio sem reconstruir detalhes acidentais.
2. **Coesão antes de tamanho:** uma unidade pequena que separa dados e comportamento relacionados pode piorar o design.
3. **Abstração sob evidência:** extraia quando existe variação real, uma política estável ou repetição semântica; não por contagem mecânica.
4. **SOLID como diagnóstico:** use os princípios para formular riscos, não como checklist para adicionar interfaces.
5. **Mudança protegida:** refatoração preserva comportamento e começa com evidência executável.

### Perguntas de Decisão

| Sinal | Pergunta | Resposta preferida |
|---|---|---|
| Função extensa | Há mais de uma razão de negócio para mudar? | Separar por responsabilidade observável |
| Duplicação | As cópias representam a mesma regra e mudam juntas? | Extrair; caso contrário, tolerar semânticas distintas |
| Interface nova | Existe segundo consumidor ou variação prevista por decisão concreta? | Criar só com evidência; evitar interface especulativa |
| Muitos parâmetros | Eles formam um conceito do domínio? | Value Object ou Parameter Object com invariantes |
| Condicional crescente | Os ramos representam políticas substituíveis? | Strategy/polimorfismo; não aplicar a um caso estável simples |
| Dependência externa | O modelo externo vaza para o domínio? | Adapter ou Anti-Corruption Layer |

### Smells São Hipóteses

Um smell inicia uma investigação; não prova defeito. Antes de escolher um pattern, registre: problema observado, pressão de mudança, opção simples, opção estrutural, trade-offs e critério de reversão. Sempre inclua **quando não usar**.

### Refatoração Segura

1. Capture o comportamento atual com testes de caracterização quando ele não estiver protegido.
2. Estabeleça baseline de testes, análise estática e, quando relevante, latência/alocação.
3. Faça uma transformação por vez e execute o menor conjunto confiável de verificações.
4. Preserve contratos públicos, dados, telemetria e semântica de falha.
5. Separe mudança de comportamento de reorganização estrutural quando isso melhorar a revisão.

### Decisões Vigentes

| Decisão | Status | Consequência |
|---|---|---|
| Limites objetivos ficam em `lex-clean-code` | Confirmada | Este Codex mantém os trade-offs contextuais |
| Patterns exigem `use_when`, `avoid_when` e trade-offs | Proposta para o Ahrena v2 | Evita cargo cult e prepara o dicionário consultável |

### Restrições Técnicas

- Não introduzir pattern sem nomear o problema que ele resolve e o cenário em que deve ser removido ou evitado.
- Não mudar contrato, schema ou semântica de erro sob o rótulo de refatoração.
- Não usar métrica de cobertura, complexidade ou tamanho isoladamente como prova de qualidade.
- Não registrar informação sensível em comentários, nomes, testes ou telemetria.

## Glossário

| Termo | Definição |
|---|---|
| Pressão de mudança | Evidência de que uma área muda por razões diferentes ou recorrentes |
| Smell | Sinal que merece investigação, não diagnóstico definitivo |
| Falsa abstração | Compartilhamento estrutural entre conceitos que não têm a mesma semântica |

## Referências

- `lex-clean-code`, `lex-dry`, `lex-no-silent-tech-debt`
- `kata-safe-refactoring`
