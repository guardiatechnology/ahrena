# Cry: Criar Nova Lexis

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Criação de Lexis (leis inquebráveis)

## Descrição

Comando rápido para criar uma nova Lexis no Ahrena. Invoca o `kata-create-lexis`, que consulta `codex-lexis` e o template oficial para produzir uma lei completa nos três idiomas obrigatórios.

## Uso

```
/cry-new-lex <assunto> [escopo] [--clade clade/subclade]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `assunto` | Sim | Tema da lei a ser criada | `"code review obrigatório"` |
| `escopo` | Não | Onde a lei se aplica. Se omitido, o agente infere do assunto | `"todos os repositórios"` |
| `--clade` | Não | Clade/subclade na taxonomia. Se omitido, o agente infere do assunto | `--clade engineering/quality` |

## O que o Comando Faz

1. Lê `.ahrena/.directives` para obter idiomas e convenções
2. Consulta `codex-lexis` para critérios de qualidade
3. Lê `templates/lex-sample.md` como base estrutural
4. Executa `kata-create-lexis` com os parâmetros fornecidos
5. Cria a Lexis no idioma padrão e traduz para os demais idiomas
6. Reporta os arquivos criados

## Prompt Template

```
Contexto:
- Assunto: {{assunto}}
- Escopo: {{escopo}} (ou inferir do assunto)
- Clade/Subclade: {{clade}} (ou inferir do assunto)

Tarefa:
Execute o kata-create-lexis. Consulte .ahrena/.directives para obter os
idiomas obrigatórios. Consulte codex-lexis para critérios de qualidade.
Use templates/lex-sample.md como base. Crie a Lexis no idioma padrão e
traduza para todos os idiomas de language.i18n.

Formato de saída:
Lista de arquivos criados com confirmação de que a lei é clara, unívoca
e testável.
```

## Exemplo de Invocação

**Criar Lexis com assunto:**

```
/cry-new-lex "code review obrigatório"
```

**Output:**

```
Lexis criada com sucesso.

Lei: "Todo PR DEVE ter pelo menos um revisor aprovado antes do merge."

Arquivos criados:
1. framework/pt-BR/engineering/quality/lexis/lex-code-review.md ✓
2. framework/es/engineering/quality/lexis/lex-code-review.md ✓
3. framework/en/engineering/quality/lexis/lex-code-review.md ✓

Validação:
- Univocidade: ✓ (uma interpretação possível)
- Testabilidade: ✓ (verificável via API do GitHub)
- Exceções: Nenhuma ✓
```

**Com escopo e clade explícitos:**

```
/cry-new-lex "no secrets em repositório" "todos os repositórios" --clade engineering/security
```

## Restrições

- Não cria Lexis que admitam exceções — se precisa de exceção, sugere criar um Codex
- Sempre executa `kata-create-lexis` (nunca cria diretamente)
- Sempre cria nos três idiomas obrigatórios

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Invocação rápida (1 comando) | Procedimento completo (6 passos) |
| **Complexidade** | Baixa (assunto + escopo) | Alta (concepção, redação, validação) |
| **Configura agente?** | Não | Sim (define comportamento) |
| **Exemplo** | `/cry-new-lex "code review"` | Workflow de 6 passos com checklist |

## Referências

- `kata-create-lexis` — Procedimento executado por este Cry
- `codex-lexis` — Critérios de qualidade consultados
- `templates/lex-sample.md` — Template base
