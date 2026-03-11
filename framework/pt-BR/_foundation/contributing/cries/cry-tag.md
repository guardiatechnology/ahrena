# Cry: Executar Git Tag

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para criar ou listar tags de release com versionamento semântico

## Invocação

```
/cry-tag [versão] [mensagem] [commit]
/cry-tag --list
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `versão` | Não | Identificador SemVer (com ou sem prefixo `v`) | `1.2.3`, `v1.2.3` |
| `mensagem` | Não | Mensagem de anotação da tag | `"Release 1.2.3"` |
| `commit` | Não | ID (hash) ou mensagem (subject) do commit ao qual a tag será apontada; se omitido, usa HEAD | `abc123f`, `"feat(auth): add OAuth2"` |
| `--list` | — | Listar tags existentes (não cria tag) | `/cry-tag --list` |

Se `--list` for passado, o comando apenas lista as tags (ex.: `git tag -l --sort=-v:refname`). Caso contrário, invoca `kata-tag` para criar uma nova tag.

Se a versão for omitida ao criar tag, o agente sugere a próxima versão com base no histórico de tags e commits (consultando `codex-semantic-version`). Se `commit` for informado, o agente resolve o ID ou a mensagem para um commit válido e aponta a tag para ele.

## Exemplos de Uso

```
# Criar tag com versão e mensagem
/cry-tag v1.2.3 "Release 1.2.3"

# Criar tag apontada para um commit pelo hash
/cry-tag v1.2.3 "Release 1.2.3" abc123f

# Criar tag apontada para um commit pela mensagem (subject)
/cry-tag v1.2.3 "Release 1.2.3" "feat(auth): add OAuth2"

# Criar tag só com versão (mensagem padrão, HEAD)
/cry-tag v1.2.3

# Sugestão automática — agente determina próxima versão e confirma
/cry-tag

# Listar tags
/cry-tag --list
```

## Comportamento

**Ao criar tag (sem `--list`):**

1. Invoca `kata-tag` passando versão, mensagem e commit (se fornecidos)
2. Se a versão for omitida, o agente analisa o histórico e sugere a próxima versão conforme `codex-semantic-version`
3. Valida contra `lex-semantic-version` e `lex-signed-commits`
4. Cria a tag anotada e assinada e informa como publicar (`git push origin <versão>`)

**Ao listar (`--list`):**

1. Executa `git tag -l` (opcionalmente com ordenação por versão, ex.: `--sort=-v:refname`)
2. Exibe a lista de tags; não executa o Kata de criação

## Kata Associado

`kata-tag` — Procedimento completo para aplicar versionamento semântico com git tags

## Referências

- `kata-tag` — Procedimento executado por este Cry ao criar tag (o Kata consulta as Lexis e o Codex de SemVer e assinatura; ver documentação do Kata)
