# Cry: Fazer Commit

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para criar commits padronizados

## Invocação

```
/cry-commit [tipo] [escopo] [descrição]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `tipo` | Não | Tipo Conventional Commits | `feat`, `fix`, `docs` |
| `escopo` | Não | Módulo ou domínio | `auth`, `api`, `payments` |
| `descrição` | Não | Texto do subject em inglês | `"implement OAuth2"` |

Se parâmetros forem omitidos, o agente analisa `git diff --staged` e sugere automaticamente.

## Exemplos de Uso

```
# Commit com todos os parâmetros
/cry-commit feat auth "implement OAuth2 authentication"

# Commit com tipo e descrição (sem escopo)
/cry-commit fix "resolve null pointer in transaction"

# Commit automático — agente analisa o diff e sugere
/cry-commit
```

## Comportamento

1. Invoca `kata-commit` passando os parâmetros fornecidos
2. Se parâmetros forem omitidos, o agente:
   - Executa `git diff --staged`
   - Infere tipo, escopo e descrição
   - Apresenta a sugestão para confirmação
3. Valida contra as 4 Lexis de commit
4. Executa o commit assinado

## Kata Associado

`kata-commit` — Procedimento completo de criação de commit

## Referências

- `kata-commit` — Procedimento executado por este Cry
- `lex-conventional-commits` — Formato obrigatório
- `lex-signed-commits` — Assinatura GPG
- `lex-small-commits` — Atomicidade
- `lex-commit-language` — Idioma de commits
- `codex-commit-standards` — Guia de referência
