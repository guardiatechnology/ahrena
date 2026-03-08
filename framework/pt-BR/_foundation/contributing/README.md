# Contributing — Fluxo de Contribuição

> Documentação do sistema de contribuição, padrões de commit e criação de Pull Requests.

## Visão Geral

O subclade `contributing` define o fluxo unificado de contribuição da Guardia. Abrange desde as leis de commit até o procedimento de abertura de PRs via MCP. O processo é o mesmo para todos os contribuidores (internos e externos), garantindo transparência e rastreabilidade.

## Arquitetura

```mermaid
flowchart TD
    subgraph invocation ["Invocação"]
        CryCommit["/cry-commit"]
        CryContribute["/cry-contribute"]
        CryTag["/cry-tag"]
    end

    subgraph procedures ["Procedimentos"]
        KataCommit["kata-commit"]
        KataContribute["kata-contribute"]
        KataTag["kata-tag"]
    end

    subgraph knowledge ["Conhecimento"]
        CdxContributing["codex-contributing"]
        CdxCommitStd["codex-commit-standards"]
        CdxSemVer["codex-semantic-version"]
    end

    subgraph laws ["Leis"]
        LexConventional["lex-conventional-commits"]
        LexSmall["lex-small-commits"]
        LexLanguage["lex-commit-language"]
        LexSigned["lex-signed-commits"]
        LexSemVer["lex-semantic-version"]
    end

    CryCommit -->|"invoca"| KataCommit
    CryContribute -->|"invoca"| KataContribute
    CryTag -->|"invoca"| KataTag
    KataContribute -->|"usa internamente"| KataCommit
    KataContribute -->|"consulta"| CdxContributing
    KataCommit -->|"consulta"| CdxCommitStd
    KataCommit -->|"obedece"| LexConventional
    KataCommit -->|"obedece"| LexSmall
    KataCommit -->|"obedece"| LexLanguage
    KataCommit -->|"obedece"| LexSigned
    KataTag -->|"consulta"| CdxSemVer
    KataTag -->|"obedece"| LexSemVer
    KataTag -->|"obedece"| LexSigned
```

## Inventário de Artefatos

### Lexis (leis)

| Artefato | Descrição |
|----------|-----------|
| `lex-conventional-commits` | Formato obrigatório `type(scope): description` |
| `lex-small-commits` | Um propósito por commit, mudanças atômicas |
| `lex-commit-language` | Subject em inglês |
| `lex-signed-commits` | Assinatura GPG obrigatória |
| `lex-semantic-version` | Versionamento SemVer 2.0 obrigatório para releases e tags |

### Codex (conhecimento)

| Artefato | Descrição |
|----------|-----------|
| `codex-contributing` | Fluxo completo de contribuição (da discussão ao merge) |
| `codex-commit-standards` | Estrutura detalhada das mensagens de commit |
| `codex-semantic-version` | Referência para SemVer e uso de git tags em releases |

### Katas (procedimentos)

| Artefato | Descrição |
|----------|-----------|
| `kata-commit` | Procedimento para criar commits conformes |
| `kata-contribute` | Procedimento para abrir Pull Requests via MCP |
| `kata-tag` | Procedimento para aplicar versionamento semântico com git tags |

### Cries (atalhos)

| Artefato | Descrição |
|----------|-----------|
| `cry-commit` | Atalho para commitar seguindo as 4 Lexis de commit |
| `cry-contribute` | Atalho para abrir PR ou contribuir ao framework |
| `cry-tag` | Atalho para criar ou listar tags de release (SemVer) |

## Como Usar

### Commitar mudanças

```
/cry-commit
```

O agente analisa as mudanças, cria commits atômicos seguindo Conventional Commits, com subject em inglês e assinatura GPG.

### Abrir um Pull Request

```
/cry-contribute pr
```

O agente executa o `kata-contribute`, que cria o PR no repositório origin via ferramentas MCP do GitKraken.

### Versionar release (tags)

```
/cry-tag [versão] [mensagem] [commit]
/cry-tag --list
```

O agente executa o `kata-tag`: cria tag anotada e assinada em formato SemVer ou lista as tags existentes. Opcionalmente informar o commit (ID ou mensagem) ao qual a tag será apontada.

### Fluxo completo de contribuição

O `codex-contributing` define o processo passo a passo:

1. Abrir discussão no GitHub Discussions (categoria Ideas)
2. Discussão aprovada vira issue
3. Criar branch a partir de main (`feat/nome`, `fix/nome`, `docs/nome`)
4. Implementar (seguindo Lexis de commit)
5. Abrir PR preenchendo o template
6. Manter CI verde e responder ao review
7. Merge pelo maintainer

## Referências

- [CONTRIBUTING da Guardia](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `.github/pull_request_template.md` — Template de PR
- `.github/CODEOWNERS` — Arquivo de codeowners
