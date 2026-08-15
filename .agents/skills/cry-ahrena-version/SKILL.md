---
name: cry-ahrena-version
description: "Mostrar Versão do Framework Ahrena. Consulta sob demanda da versão instalada do framework Ahrena"
---

# Cry: Mostrar Versão do Framework Ahrena

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Consulta sob demanda da versão instalada do framework Ahrena

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

## Restrições

- O Cry NÃO DEVE adicionar nenhuma saída além do que o kata retorna — sem banner, sem rótulo de versão, sem metadados
- O Cry NÃO DEVE consultar a rede. O kata invocado é local por design
- O Cry NÃO DEVE modificar nenhum arquivo. É uma consulta apenas de leitura
