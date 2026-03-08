# Lexis: Regras para Traduzir para Espanhol

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Tradução de documentação técnica para espanhol (es)

## Propósito

Esta Lexis define as regras específicas para traduzir documentação técnica **para Espanhol neutro (es)**. Complementa a `lex-language` (regras transversais) com particularidades linguísticas, estilísticas e culturais do espanhol.

## Lei

> **Toda tradução para espanhol DEVE seguir as regras transversais de `lex-language` E as regras específicas definidas nesta Lexis.**

## Regras

### 1. Variante do espanhol

Usar **espanhol neutro** — sem regionalismos de Espanha, México, Argentina ou qualquer outro país. O objetivo é produzir documentação compreensível por qualquer falante de espanhol.

### 2. Formalidade

Manter formalidade implícita adequada a documentação técnica:
- Voz impessoal quando apropriado ("Se debe configurar..." em vez de "Tú debes configurar...")
- Evitar linguagem coloquial
- Tom profissional e acessível

### 3. Consistência de tratamento

**NÃO** misturar "tú" e "usted" no mesmo documento. Escolher um e manter consistência. Para documentação técnica, preferir construções impessoais.

### 4. Falsos cognatos com pt-BR

Atenção especial a falsos cognatos entre pt-BR e espanhol:

| Português | Espanhol (CORRETO) | Falso cognato (ERRADO) |
|-----------|-------------------|----------------------|
| esquisito (estranho) | extraño, raro | exquisito (= requintado) |
| polvo (molusco) | pulpo | polvo (= pó) |
| largo (amplo) | amplio, ancho | largo (= longo/comprido) |
| escritório | oficina | escritorio (= escrivaninha) |
| sobrenome | apellido | sobrenombre (= apelido) |
| acordar (despertar) | despertar | acordar (= combinar/lembrar) |
| vaso (recipiente) | jarrón, florero | vaso (= copo) |
| berro (grito) | grito | berro (= agrião) |

### 5. Termos técnicos em inglês

Termos técnicos universais **DEVEM** ser mantidos em inglês, assim como em pt-BR:
- commit, merge, branch, pull request, framework, deploy
- Quando traduzir: workflow → flujo de trabajo, output → salida, input → entrada

### 6. Verbos modais

| Inglês | Espanhol |
|--------|----------|
| MUST | DEBE |
| MUST NOT | NO DEBE / NO PUEDE |
| SHOULD | DEBERÍA / SE RECOMIENDA |
| MAY | PUEDE |

### 7. Pontuação e ortografia

- Usar corretamente os sinais de abertura de interrogação (¿) e exclamação (¡)
- Acentuação conforme as regras da RAE
- Atenção ao uso correto de "sólo/solo", "éste/este", conforme normas vigentes

## Abrangência

- **Aplica-se a:** toda tradução cujo idioma-alvo seja espanhol (es)
- **Agentes vinculados:** `warrior-translator` e qualquer agente que traduza para espanhol
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Referências

- `lex-language` — Regras transversais (esta Lexis complementa)
- `codex-language-es` — Guia detalhado para tradução para espanhol
