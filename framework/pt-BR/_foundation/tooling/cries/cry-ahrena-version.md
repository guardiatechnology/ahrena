# Cry: Mostrar Versão do Framework Ahrena

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Consulta sob demanda da versão instalada do framework Ahrena

## Descrição

Atalho que imprime a versão do framework Ahrena atualmente em uso. O Cry não recebe parâmetros e delega a resolução ao `kata-ahrena-version`, que lê primeiro `.ahrena/.version` (manifesto canônico gravado no install) e faz fallback para `git describe` quando a working tree é o próprio repositório do framework.

## Uso

```
/cry-ahrena-version
```

## Parâmetros

Nenhum. O Cry não aceita argumentos.

## O que o Comando Faz

1. Invoca `kata-ahrena-version` contra o diretório de trabalho atual
2. Imprime a string de versão resolvida em uma única linha
3. Em caso de falha (sem `.ahrena/.version` e sem tag git legível), imprime a mensagem de erro estruturada do kata e sai com status diferente de zero

## Template de Prompt

```
Contexto:
- Diretório de trabalho: atual

Tarefa:
Executar kata-ahrena-version. Emitir apenas a string de versão de uma linha que
o kata retorna. Não adicionar prefixos, sufixos, decorações ou explicações. Se o
kata falhar, emitir a mensagem de erro do kata literalmente.

Formato de saída:
Texto simples de uma linha (ex.: `0.13.1`, `0.13.1-3-gabc1234`, `main`) em stdout,
ou a mensagem de erro estruturada do kata em stderr.
```

## Exemplo de Invocação

**Projeto consumidor após install:**

```
$ /cry-ahrena-version
0.13.1
```

**Repositório do framework antes do install (modo dev, HEAD adiante da última tag):**

```
$ /cry-ahrena-version
0.13.1-3-gabc1234
```

**Projeto instalado a partir de uma branch:**

```
$ /cry-ahrena-version
main
```

## Restrições

- O Cry NÃO DEVE adicionar nenhuma saída além do que o kata retorna — sem banner, sem rótulo de versão, sem metadados
- O Cry NÃO DEVE consultar a rede. O kata invocado é local por design
- O Cry NÃO DEVE modificar nenhum arquivo. É uma consulta apenas de leitura

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Ponto de entrada; zero parâmetros | Procedimento de resolução com cadeia de fallback explícita |
| **Saída** | Pass-through da string de uma linha do kata | String SemVer de uma linha (ou erro estruturado) |
| **Efeitos colaterais** | Nenhum | Nenhum |

## Referências

- `kata-ahrena-version` — procedimento invocado por este Cry
