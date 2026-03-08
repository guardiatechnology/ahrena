# Cry: Executar Makefile

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Execução de targets do Makefile do repositório Ahrena

## Invocação

```
/cry-make <target> [variáveis]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `target` | Sim | Target do Makefile a executar | `install`, `bootstrap`, `clean` |
| `variáveis` | Não | Variáveis de ambiente para o make | `PLATFORM=cursor VERSION=1.0.0` |

## Targets Disponíveis

| Target | Descrição |
|--------|-----------|
| `bootstrap` | Configura o ambiente de desenvolvimento |
| `install` | Instala o framework na plataforma especificada |
| `update` | Atualiza uma instalação existente |
| `uninstall` | Remove a instalação do framework |
| `clean` | Limpa artefatos temporários |

## Exemplos de Uso

```
# Instalar para Cursor
/cry-make install PLATFORM=cursor

# Bootstrap do ambiente
/cry-make bootstrap

# Limpar artefatos
/cry-make clean

# Instalar versão específica
/cry-make install PLATFORM=cursor VERSION=1.0.0
```

## Comportamento

1. Verifica que o `Makefile` existe na raiz do repositório
2. Valida que o target solicitado existe
3. Executa `make <target> [variáveis]`
4. Reporta a saída do comando ao usuário
5. Se o comando falhar, apresenta o erro e sugere correção

## Nota

Este Cry é **específico do repositório Ahrena** — ele não é um artefato genérico do framework. Ele existe para facilitar a execução de tarefas de desenvolvimento e manutenção dentro do próprio projeto do Ahrena.

## Referências

- `Makefile` — Arquivo de automação na raiz do repositório
- [GNU Make Manual](https://www.gnu.org/software/make/manual/)
