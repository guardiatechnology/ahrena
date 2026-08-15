---
name: cry-make
description: "Executar Makefile. Execução de targets do Makefile do repositório Ahrena"
---

# Cry: Executar Makefile

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Execução de targets do Makefile do repositório Ahrena

## Uso

```
/cry-make <target> [variáveis]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `target` | Sim | Target do Makefile a executar | `install`, `update`, `dev-install`, `bootstrap` |
| `variáveis` | Não | Variáveis para o make (formato `NOME=valor`) | `PLATFORM=cursor`, `SOURCE=../ahrena`, `LOCAL=1` |

Para a lista completa de targets e variáveis, consulte `codex-make`.

## Despacho por target

| Target | Kata executado |
|--------|----------------|
| `install` | `kata-make-install-framework` |
| `update` | `kata-make-update-framework` |
| `dev-install` | `kata-make-dev-install-framework` |
| `bootstrap` | `kata-make-bootstrap-framework` |
| `sync-cursor` | `kata-make-sync-cursor` |
| `uninstall` | `kata-make-uninstall-framework` |
| `clean` | `kata-make-clean-framework` |

Targets não listados acima são inválidos para este Cry; informe o usuário e liste os targets válidos.

## O que o Comando Faz

1. Valida o target com base na tabela acima (targets do `codex-make`)
2. Se o target for inválido: informe o usuário e liste os targets válidos; não execute kata
3. Com base no target válido, escolhe o Kata correspondente (tabela acima)
4. Executa o Kata escolhido com as variáveis fornecidas
5. O Kata consulta codex-make, verifica o ambiente, executa `make` ou o equivalente e reporta o resultado
6. Apresenta a saída ao usuário ou o erro com sugestão de correção

## Prompt Template

```
Contexto:
- Target: {{target}}
- Variáveis: {{variáveis}} (opcional)

Tarefa:
Com base no target solicitado, execute o Kata correspondente:
- install → kata-make-install-framework
- update → kata-make-update-framework
- dev-install → kata-make-dev-install-framework
- bootstrap → kata-make-bootstrap-framework
- sync-cursor → kata-make-sync-cursor
- uninstall → kata-make-uninstall-framework
- clean → kata-make-clean-framework
- target não listado acima → informe target inválido e liste os targets válidos (não execute kata)

O Kata consulta codex-make para variáveis válidas e equivalência sem Make
quando make não estiver disponível. Reporte a saída do comando ou o erro
com sugestão de correção.

Formato de saída:
Saída do comando executado ou mensagem de erro com indicação de como corrigir.
```
