# Lexis: Idioma de Commits

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Todos os commits em repositórios Guardia

## Lei

> **A mensagem principal (subject) de todo commit DEVE ser escrita em inglês. O corpo (body) PODE incluir texto em idioma local, desde que precedido pela tag `[idioma]`.**

## Regras

### 1. Subject em inglês

A primeira linha do commit (subject) DEVE ser escrita em inglês, seguindo o formato Conventional Commits.

### 2. Body com tag de idioma

Se o contribuidor desejar incluir descrição em idioma local, DEVE usar a tag de idioma entre colchetes no corpo:
- `[pt-BR]` para português brasileiro
- `[es]` para espanhol
- Qualquer código BCP 47 válido

### 3. Tradução em inglês primeiro

Se o body contém texto em idioma local, a versão em inglês DEVE aparecer primeiro (com tag `[en]`), seguida pela versão local.

### 4. Ferramentas de tradução

O uso de ferramentas como DeepL ou Google Tradutor é encorajado para garantir qualidade da mensagem em inglês. Manter o texto original junto com a tradução ajuda a mitigar erros.

## Exemplos

### Correto

```
feat(auth): implement OAuth2 authentication

[en]
Implement OAuth2 authentication flow with support for multiple providers:
- Add OAuth2 client configuration
- Create authentication handlers for Google and GitHub
- Implement token validation and refresh logic
- Add unit tests for auth flow

[pt-BR]
Implementa fluxo de autenticação OAuth2 com suporte para múltiplos provedores:
- Adiciona configuração do cliente OAuth2
- Cria handlers de autenticação para Google e GitHub
- Implementa lógica de validação e refresh de tokens
- Adiciona testes unitários para o fluxo de auth

Closes #123
```

```
fix: resolve null pointer in transaction processing
```

### Incorreto

```
# Subject em português — VIOLA A LEI
feat(auth): implementar autenticação OAuth2

# Body sem tag de idioma — VIOLA A LEI
feat(auth): implement OAuth2

Implementa fluxo de autenticação OAuth2.
(Falta a tag [pt-BR] antes do texto em português)
```

## Validação Automatizada

- **Ferramenta:** commitlint com regra customizada para idioma do subject
- **Momento:** pre-commit hook e CI pipeline
- **Métrica:** 100% dos subjects em inglês
