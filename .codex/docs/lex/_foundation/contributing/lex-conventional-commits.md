# Lexis: Conventional Commits Obrigatório

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Todos os commits em repositórios Guardia

## Lei

> **Todo commit DEVE seguir o formato Conventional Commits: `<tipo>[escopo opcional]: <descrição>`.**

## Regras

### 1. Formato obrigatório

Todo commit deve seguir a estrutura:

```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé(s) opcional(is)]
```

### 2. Tipos permitidos

| Tipo | Quando usar |
|------|-------------|
| `feat` | Nova funcionalidade (correlaciona com MINOR no SemVer) |
| `fix` | Correção de bug (correlaciona com PATCH no SemVer) |
| `docs` | Alterações em documentação |
| `build` | Mudanças no sistema de build ou dependências externas |
| `chore` | Tarefas de manutenção que não alteram código de produção |
| `ci` | Mudanças em configuração de CI/CD |
| `style` | Formatação, semicolons, espaços — sem mudança de lógica |
| `refactor` | Refatoração que não adiciona feature nem corrige bug |
| `perf` | Melhoria de performance |
| `test` | Adição ou correção de testes |

### 3. Breaking changes

Commits que introduzem mudanças incompatíveis DEVEM:
- Adicionar `!` após o tipo/escopo: `feat(api)!: change auth endpoint`
- Ou incluir `BREAKING CHANGE:` no rodapé

### 4. Escopo

O escopo é opcional e fornece contexto adicional entre parênteses: `feat(auth): add OAuth2 support`.

## Exemplos

### Correto

```
feat(auth): implement OAuth2 authentication

[pt-BR]
Implementa fluxo de autenticação OAuth2 com suporte para múltiplos provedores.

Closes #123
```

```
fix: resolve null pointer in transaction processing
```

```
docs(api): update endpoint documentation for v2
```

### Incorreto

```
# Sem tipo — VIOLA A LEI
updated the login page

# Tipo inválido — VIOLA A LEI
feature: add new button

# Múltiplas mudanças misturadas — VIOLA lex-small-commits também
feat: add login, fix header, update docs
```

## Validação Automatizada

- **Ferramenta:** commitlint com `@commitlint/config-conventional`
- **Momento:** pre-commit hook e CI pipeline
- **Métrica:** 0 commits fora do formato tolerados
