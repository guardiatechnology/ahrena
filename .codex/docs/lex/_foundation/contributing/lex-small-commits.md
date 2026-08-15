# Lexis: Commits Atômicos Obrigatórios

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Todos os commits em repositórios Guardia

## Lei

> **Todo commit DEVE ser atômico — representando uma única mudança lógica que pode ser integrada independentemente.**

## Regras

### 1. Uma mudança por commit

Cada commit DEVE conter alterações relacionadas a um único propósito. Não misturar:
- Feature + bug fix
- Refatoração + nova funcionalidade
- Formatação + mudança de lógica

### 2. Funcionalidade isolada

Cada commit DEVE deixar o código em estado funcional. O projeto DEVE compilar e os testes existentes DEVEM passar após cada commit individual.

### 3. Granularidade adequada

Se um commit está grande demais, DEVE ser dividido em commits menores. Se um commit é trivial demais (ex: renomear uma variável em um único lugar), pode ser agrupado com mudanças relacionadas.

### 4. Independência

Cada commit DEVE poder ser compreendido e, se necessário, revertido sem impactar partes não relacionadas do código.

## Exemplos

### Correto

```
# Commit 1: apenas a feature
feat(auth): add OAuth2 client configuration

# Commit 2: apenas os testes
test(auth): add unit tests for OAuth2 flow

# Commit 3: apenas a documentação
docs(auth): document OAuth2 setup instructions
```

### Incorreto

```
# Um commit com tudo misturado — VIOLA A LEI
feat(auth): add OAuth2, fix header bug, update README, refactor utils

# Este commit faz 4 coisas não relacionadas:
# 1. Adiciona OAuth2 (feat)
# 2. Corrige bug no header (fix)
# 3. Atualiza README (docs)
# 4. Refatora utils (refactor)
# Deveria ser 4 commits separados.
```

## Validação Automatizada

- **Ferramenta:** revisão humana + análise de diff por agente IA
- **Momento:** code review no PR
- **Métrica:** cada commit deve ter um único tipo Conventional Commits e afetar um escopo coerente
