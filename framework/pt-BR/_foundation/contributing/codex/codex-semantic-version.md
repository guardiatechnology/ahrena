# Codex: Versionamento Semântico

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Versionamento de releases e tags em repositórios Guardia

## Visão Geral

Este Codex é a referência para aplicar Semantic Versioning 2.0 (SemVer) em repositórios Guardia. Define quando incrementar MAJOR, MINOR ou PATCH, como SemVer se relaciona com Conventional Commits e como usar git tags para marcar releases. É consultado pelo `kata-tag` e pelo `cry-tag`.

## Contexto

- **Domínio:** Identificadores de versão, releases e tags no Git
- **Público-alvo:** Agentes de IA executando `kata-tag` e desenvolvedores que publicam releases
- **Atualização:** Quando a convenção de versionamento do projeto for alterada

## Conteúdo

### Princípios

1. **MAJOR (X):** incrementado quando há mudanças incompatíveis com versões anteriores (breaking changes). Consumidores que dependem da versão anterior podem precisar de alterações.
2. **MINOR (Y):** incrementado quando nova funcionalidade é adicionada de forma compatível. Código existente continua funcionando.
3. **PATCH (Z):** incrementado quando correções de bugs ou ajustes compatíveis são feitos. Comportamento público não muda de forma incompatível.

### Formato da Versão

```
MAJOR.MINOR.PATCH[-pré-release][+metadados]
```

| Parte | Obrigatória | Exemplo |
|-------|:-----------:|---------|
| MAJOR.MINOR.PATCH | Sim | `1.2.3` |
| Pré-release | Não | `1.2.3-alpha.1`, `1.0.0-rc.2` |
| Metadados de build | Não | `1.2.3+build.42` |

O prefixo `v` na tag (ex.: `v1.2.3`) é recomendado para compatibilidade com ferramentas e convenção comum. O projeto DEVE adotar uma forma (`v` ou sem `v`) e mantê-la consistente.

### Relação com Conventional Commits

O histórico de commits no formato Conventional Commits permite inferir o tipo de bump para a próxima versão:

| Situação nos commits desde o último tag | Incremento recomendado |
|----------------------------------------|-------------------------|
| Pelo menos um commit com `BREAKING CHANGE:` ou tipo `feat!` / `fix!` | MAJOR |
| Pelo menos um `feat` (sem breaking) | MINOR |
| Apenas `fix`, `perf`, `docs`, `chore`, `style`, `refactor`, `test`, `ci`, `build` | PATCH |
| Nenhum commit relevante para release | Não criar tag ou usar pré-release |

Quando o usuário não informa a versão no `cry-tag` ou no `kata-tag`, o agente pode sugerir a próxima versão com base nessa tabela e no último tag existente.

### Quando Incrementar Cada Número

| Componente | Quando incrementar | Exemplo |
|------------|--------------------|---------|
| MAJOR | API pública removida ou alterada de forma incompatível; mudança de comportamento que quebra contratos | Remoção de parâmetro obrigatório, mudança de tipo de retorno |
| MINOR | Nova funcionalidade backward-compatible | Novo endpoint, novo parâmetro opcional |
| PATCH | Correção de bug, ajuste de documentação, melhoria de performance sem mudar contrato | Bug fix, typo em mensagem, otimização interna |

Após incrementar MAJOR, MINOR e PATCH são resetados para 0 (ex.: após `1.2.3`, o próximo MAJOR é `2.0.0`). Após incrementar MINOR, PATCH é resetado para 0 (ex.: `1.2.3` → `1.3.0`).

### Pré-release e Metadados

- **Pré-release:** identificadores como `alpha`, `beta`, `rc` seguem a especificação SemVer 2.0. Ex.: `v1.2.3-alpha.1`, `v2.0.0-rc.1`. Úteis para publicar versões de teste sem alterar o número de release estável.
- **Metadados de build:** sufixo `+build.42` ou `+20260308` não altera a precedência da versão. Usado para distinguir builds do mesmo número de versão.

### Aplicação em Git Tags

| Prática | Descrição |
|---------|-----------|
| Tag no commit de release | Criar a tag no commit que representa o estado daquele release (geralmente o último commit da release). |
| Uma tag por versão | Cada identificador SemVer (ex.: `v1.2.3`) deve aparecer no máximo uma vez no repositório. |
| Tags assinadas | Conforme `lex-signed-commits`, tags de release DEVEM ser assinadas com GPG (`git tag -s`). |
| Tag anotada | Usar `git tag -a` (ou `-s` que implica anotada) para incluir mensagem e metadados; permite changelog e referência estável. |

Comando típico para criar tag de release:

```
git tag -s v1.2.3 -m "Release 1.2.3"
```

Para enviar a tag ao remoto:

```
git push origin v1.2.3
```

### Restrições Técnicas

- O formato DEVE obedecer à especificação [SemVer 2.0.0](https://semver.org/).
- Tags de release não podem usar nomes que não sejam SemVer (ex.: `latest`, `release-1.2`).
- O projeto DEVE documentar se usa prefixo `v` ou não e manter consistência.

## Glossário

| Termo | Definição |
|-------|-----------|
| MAJOR | Primeiro número da versão; mudanças incompatíveis |
| MINOR | Segundo número da versão; nova funcionalidade compatível |
| PATCH | Terceiro número da versão; correções compatíveis |
| Pré-release | Identificador opcional após o PATCH (ex.: alpha, beta, rc) |
| Build metadata | Metadados opcionais após `+`; não afetam precedência |
| Tag anotada | Tag Git que armazena objeto com mensagem e referência ao commit |
| Tag assinada | Tag Git assinada com GPG para verificação de autenticidade |

## Referências

- [Semantic Versioning 2.0.0](https://semver.org/)
- `lex-semantic-version` — Lei que exige SemVer para releases
- `lex-signed-commits` — Lei que exige assinatura GPG em tags de release
- `codex-commit-standards` — Tipos de commit e impacto em SemVer
- `kata-tag` — Procedimento para criar tags conformes
- `cry-tag` — Comando recorrente para executar git tag
