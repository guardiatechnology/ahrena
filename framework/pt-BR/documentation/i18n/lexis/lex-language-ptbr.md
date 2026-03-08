# Lexis: Regras para Traduzir para Português Brasileiro

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Tradução de documentação técnica para pt-BR

## Propósito

Esta Lexis define as regras específicas para traduzir documentação técnica **para o Português Brasileiro (pt-BR)**. Complementa a `lex-language` (regras transversais) com particularidades linguísticas, estilísticas e culturais do pt-BR.

## Lei

> **Toda tradução para pt-BR DEVE seguir as regras transversais de `lex-language` E as regras específicas definidas nesta Lexis.**

## Regras

### 1. Pronome de tratamento

Usar **"você"** como pronome de tratamento. Nunca usar "tu", "vós" ou tratamento excessivamente formal como "Vossa Senhoria". O tom é técnico-acessível.

### 2. Norma culta

A tradução **DEVE** seguir a norma culta do Português Brasileiro:
- Acentuação rigorosa (é, á, ã, ç, etc.)
- Pontuação correta (vírgulas em orações subordinadas, ponto e vírgula em enumerações complexas)
- Concordância verbal e nominal
- Regência verbal e nominal

### 3. Termos técnicos em inglês

Termos técnicos consolidados na comunidade de tecnologia **DEVEM** ser mantidos em inglês quando não há equivalente consolidado em pt-BR:

| Manter em inglês | Traduzir |
|------------------|----------|
| deploy | implantar (quando verbo genérico) |
| commit | — (nunca traduzir) |
| merge | — (nunca traduzir) |
| branch | — (nunca traduzir) |
| pull request | — (nunca traduzir) |
| framework | — (nunca traduzir) |
| template | modelo (quando contexto não-técnico) |
| workflow | fluxo de trabalho |
| feedback | retorno / resposta |
| output | saída |
| input | entrada |
| bug | defeito / erro |
| feature | funcionalidade / recurso |

### 4. Anglicismos

Evitar anglicismos quando há equivalente consolidado em pt-BR:
- **"excluir"** e não "deletar"
- **"implementar"** e não "implementar" (já é pt-BR, ok)
- **"configurar"** e não "setar"
- **"finalizar"** e não "finalizar" (já é pt-BR, ok)
- **"criar"** e não "criar" (já é pt-BR, ok)

### 5. Tom

Tom **formal-acessível**: técnico sem ser rebuscado, direto sem ser coloquial.
- Usar voz ativa quando possível
- Frases objetivas, sem rodeios
- Evitar jargão desnecessário
- Manter a seriedade sem ser pedante

### 6. Verbos modais

Traduzir verbos modais com precisão:

| Inglês | Português |
|--------|-----------|
| MUST | DEVE |
| MUST NOT | NÃO DEVE / NÃO PODE |
| SHOULD | DEVERIA / RECOMENDA-SE |
| MAY | PODE |

### 7. Estruturas formais

Para instruções e documentação técnica:
- "O agente **DEVE**..." (não "O agente tem que...")
- "É necessário..." (não "Precisa...")
- "Recomenda-se..." (não "É bom que...")

## Abrangência

- **Aplica-se a:** toda tradução cujo idioma-alvo seja pt-BR
- **Agentes vinculados:** `warrior-translator` e qualquer agente que traduza para pt-BR
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Referências

- `lex-language` — Regras transversais (esta Lexis complementa)
- `codex-language-ptbr` — Guia detalhado para tradução para pt-BR
