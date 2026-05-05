[Nome da Lei]. [Etapa do SDLC]

# Lexis: [Nome da Lei]

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** [Etapa do SDLC]

## Lei

> **[Declaração clara, inequívoca e imperativa da lei]**

Exemplo: "Nenhum secret, credencial ou chave de API pode ser commitado em repositório sob qualquer circunstância."

## Exemplos

### Correto

```
# .env (nunca commitado — está no .gitignore)
DATABASE_URL=postgres://user:pass@host/db

# No código, usa variável de ambiente
db_url = os.environ["DATABASE_URL"]
```

### Incorreto

```
# Credencial hardcoded no código — VIOLA A LEI
db_url = "postgres://admin:s3cr3t@prod-host/db"
```

## Validação Automatizada

Descreva como a conformidade é verificada automaticamente:

- **Ferramenta:** [ex: git-secrets, gitleaks, SAST]
- **Momento:** [ex: pre-commit hook, CI pipeline]
- **Métrica:** 0 violações toleradas

---

**Modelo:** Este arquivo é um template. Para criar uma nova Lexis, copie este arquivo e substitua os campos entre colchetes.
