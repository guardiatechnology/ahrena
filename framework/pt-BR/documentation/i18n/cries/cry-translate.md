# Cry: Traduzir Documento

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Tradução de documentação técnica

## Descrição

Comando rápido para traduzir um documento para um ou mais idiomas. Invoca o `warrior-translator` (Hermes) que executa o `kata-translate`, consultando as regras e guias específicos de cada idioma-alvo.

## Uso

```
/cry-translate <arquivo> [idioma] [--order]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `arquivo` | Sim | Caminho do documento a traduzir | `framework/pt-BR/_foundation/process/lexis/lex-directives.md` |
| `idioma` | Não | Código(s) BCP 47 do idioma alvo. Se omitido, traduz para todos os idiomas de `language.i18n` exceto o de origem | `es`, `en`, `es,en` |
| `--order` | Não | Especifica a ordem de tradução. Se omitido, segue a ordem de `language.i18n` | `--order en,es` |

## Ordem de Tradução

Quando múltiplos idiomas são alvo, o Cry define a **ordem de execução**:

1. **Padrão:** segue a ordem definida em `language.i18n` no `.ahrena/.directives` (atualmente: pt-BR → es → en), excluindo o idioma de origem
2. **Personalizada:** quando `--order` é especificado, segue a ordem informada
3. **Sequencial:** cada idioma é traduzido completamente antes de passar ao próximo

**Exemplo de ordem padrão (fonte em pt-BR):**
1. Traduz para es (consultando `lex-language-es` + `codex-language-es`)
2. Traduz para en (consultando `lex-language-en` + `codex-language-en`)

## O que o Comando Faz

1. Lê `.ahrena/.directives` para obter idiomas e ordem
2. Identifica o idioma de origem a partir do caminho ou conteúdo
3. Determina o(s) idioma(s) alvo e a ordem de execução
4. Invoca o `warrior-translator` com o `kata-translate`
5. Para cada idioma na ordem:
   a. Consulta `lex-language-{lang}` e `codex-language-{lang}`
   b. Traduz o documento
   c. Salva no caminho correto
6. Reporta os arquivos criados

## Prompt Template

```
Contexto:
- Arquivo-fonte: {{arquivo}}
- Idioma(s) alvo: {{idioma}} (ou todos de language.i18n exceto o de origem)
- Ordem: {{order}} (ou conforme language.i18n)

Tarefa:
Assuma o papel do warrior-translator (Hermes). Consulte .ahrena/.directives
para obter os idiomas obrigatórios. Para cada idioma-alvo na ordem definida:
1. Consulte lex-language + lex-language-{lang} + codex-language + codex-language-{lang}
2. Leia o arquivo-fonte e execute o kata-translate
3. Salve a tradução no caminho correto

Formato de saída:
Lista de arquivos criados com confirmação de validação por idioma.
```

## Exemplo de Invocação

**Traduzir para todos os idiomas:**

```
/cry-translate framework/pt-BR/_foundation/process/lexis/lex-directives.md
```

**Output:**
```
Hermes — Tradução concluída.

Ordem de execução: es → en

Arquivos criados:
1. framework/es/_foundation/process/lexis/lex-directives.md ✓
2. framework/en/_foundation/process/lexis/lex-directives.md ✓

Validação por idioma:
- es: ✓ seções preservadas, termos canônicos intactos, voz impessoal aplicada
- en: ✓ seções preservadas, termos canônicos intactos, active voice aplicada
```

**Traduzir para idioma específico:**

```
/cry-translate docs/architecture.md en
```

## Restrições

- Não modifica o arquivo-fonte — apenas gera traduções
- Segue as regras de `lex-language` e `lex-language-{lang}`
- Termos canônicos do Ahrena não são traduzidos
- A ordem de tradução respeita `language.i18n` ou `--order`

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Invocação rápida (comando) | Procedimento completo (6 passos) |
| **Complexidade** | Baixa (comando + parâmetros) | Alta (workflow detalhado) |
| **Configura agente?** | Sim (invoca warrior-translator) | Sim (define o procedimento) |
| **Ordem de tradução** | Define a ordem | Não define ordem (executa 1 idioma por vez) |

## Referências

- `warrior-translator` — Agente invocado por este Cry
- `kata-translate` — Procedimento executado pelo warrior
- `lex-language`, `lex-language-{lang}` — Regras consultadas
- `codex-language`, `codex-language-{lang}` — Guias consultados
