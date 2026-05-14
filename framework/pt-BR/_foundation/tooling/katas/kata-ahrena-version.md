# Kata: Resolver Versão do Framework Ahrena

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Resolução sob demanda da versão instalada do framework Ahrena

## Objetivo

Resolver a versão do framework Ahrena atualmente em uso em uma string SemVer determinística e de linha única. A cadeia de resolução faz fallback de um manifesto canônico gravado na instalação (`.ahrena/.version` no projeto consumidor) para uma leitura via `git describe` no próprio repositório do framework, de modo que o kata funcione tanto em **modo consumidor** (caso típico depois de `make install`) quanto em **modo dev** (um agente ou pessoa rodando diretamente no clone do repositório do framework).

## Quando Usar

- Quando uma pessoa invoca `/cry-ahrena-version` e pergunta "qual versão do Ahrena está aqui?"
- Quando um warrior precisa registrar a versão do framework em um artefato de auditoria (corpo de PR, issue, nota de release)
- Em troubleshooting de compatibilidade quando a versão do framework não está visível na working tree

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| diretório de trabalho | Sim | Implícito — a cadeia de resolução lê arquivos relativos ao diretório atual |

O kata não recebe parâmetros; o diretório de trabalho é o único input.

## Workflow

```
Progresso:
- [ ] 1. Ler .ahrena/.version (modo consumidor)
- [ ] 2. Fazer fallback para git describe (modo dev)
- [ ] 3. Formatar e emitir a string de versão
- [ ] 4. Validação final
```

### Passo 1: Ler `.ahrena/.version`

1. Procurar `.ahrena/.version` relativo ao diretório de trabalho atual
2. Se o arquivo existir: ler o conteúdo, remover espaços e o newline final, usar o resultado como string de versão
3. Se o arquivo estiver vazio após o strip, tratar como ausente e seguir para o Passo 2
4. Se o arquivo existir e contiver string não vazia: pular direto para o Passo 3

### Passo 2: Fallback para `git describe`

1. Alcançado apenas quando `.ahrena/.version` está ausente ou vazio
2. Executar `git describe --tags --abbrev=0` para ler a tag mais recente
3. Se uma tag for retornada: remover o `v` inicial quando presente e usar o resultado como string de versão. Esse é o caminho de **modo dev** — execução do kata dentro do repositório do framework antes de qualquer install
4. Refinamento opcional: `git describe --tags` (sem `--abbrev=0`) retorna uma string mais rica como `0.13.1-3-gabc1234` quando o HEAD está adiante da última tag. Ambas as formas são aceitáveis; o fallback canônico é `--abbrev=0` por estabilidade, com a forma estendida disponível quando o invocador quer saber a distância exata até a tag
5. Se `git` estiver indisponível, o diretório não for um repositório git, ou não houver tags: seguir para o Passo 4 com erro explícito

### Passo 3: Formatar e emitir

1. A saída é uma única linha contendo apenas a string SemVer (sem prefixo `v`, sem aspas, sem metadados)
2. Em modo dev, a string PODE conter um sufixo `-N-gSHORT` por semântica do `git describe` — isso está correto (indica build de desenvolvimento N commits adiante da última tag); o kata não remove o sufixo
3. Imprimir a string e retornar

### Passo 4: Validação final

Antes de entregar a saída, verifique:

- [ ] A saída é uma única linha não vazia
- [ ] A saída não começa com `v` (o prefixo é removido)
- [ ] Quando nem `.ahrena/.version` nem `git describe` conseguiram resolver um valor: o kata DEVE emitir mensagem de erro estruturada — `framework version unknown; run \`make update\` in this project, or create a SemVer tag in the framework repo` — e sair com código de status diferente de zero

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| string de versão | Texto simples de uma linha (ex.: `0.13.1` ou `0.13.1-3-gabc1234`) | stdout |
| mensagem de erro | Texto simples de uma linha em stderr | stderr (exit não zero) |

## Exemplo de Execução

### Modo consumidor (típico)

```
$ cat .ahrena/.version
0.13.1

$ <kata-ahrena-version>
0.13.1
```

### Modo dev (repositório do framework, HEAD na tag)

```
$ git describe --tags --abbrev=0
v0.13.1

$ <kata-ahrena-version>
0.13.1
```

### Modo dev (repositório do framework, HEAD adiante da última tag)

```
$ git describe --tags
v0.13.1-3-gabc1234

$ <kata-ahrena-version>
0.13.1-3-gabc1234
```

### Install de branch (consumidor rodou `make install VERSION=main`)

```
$ cat .ahrena/.version
main

$ <kata-ahrena-version>
main
```

A saída é o literal `main` (ou o nome literal da branch) — o arquivo é a fonte da verdade e o kata não remodela valores que não são SemVer.

### Caminho de falha (sem `.ahrena/.version`, sem tags git)

```
$ <kata-ahrena-version>
framework version unknown; run `make update` in this project, or create a SemVer tag in the framework repo
$ echo $?
1
```

## Restrições

- O kata NÃO DEVE consultar a rede. As duas fontes de verdade são locais (`.ahrena/.version` e `git describe`); consulta a GitHub Releases é proibida
- O kata NÃO DEVE remodelar o valor lido em `.ahrena/.version`. Se o arquivo contiver `main` ou nome de branch, esse valor exato é emitido; sintetizar `0.0.0-main+<sha>` ou qualquer outro SemVer substituto é PROIBIDO
- O kata NÃO DEVE imprimir contexto extra (banner, rótulo de versão, decoração) — a saída é a string nua de versão, destinada ao consumo por outros comandos e warriors

## Referências

- `cry-ahrena-version` — comando de entrada que invoca este kata
- `lex-semantic-version` — regras de SemVer respeitadas pelo manifesto
