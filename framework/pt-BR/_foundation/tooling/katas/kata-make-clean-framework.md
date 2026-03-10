# Kata: Limpar framework (Make clean)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Remoção dos arquivos instalados pelo Ahrena (sem confirmação) via target `clean` do Makefile

## Objetivo

Remover **todos** os arquivos instalados pelo Ahrena no projeto (`.ahrena/` e arquivos do Ahrena em `.cursor/`), **sem pedir confirmação**. Equivalente ao target `clean` do Makefile — ou ao comando equivalente em PowerShell/Python quando `make` não estiver disponível. Diferente de `uninstall`, que pode solicitar confirmação.

## Quando Usar

- Quando o usuário invoca `/cry-make clean` (com ou sem variáveis, ex.: TARGET)
- Quando for necessário remover a instalação do Ahrena de forma não interativa (ex.: scripts, CI)
- Quando se deseja "resetar" o projeto em relação ao framework sem interação

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Variáveis | Não | Ex.: `TARGET=.`. Consultar `codex-make` |

## Workflow

```
Progresso:
- [ ] 1. Consultar codex-make (equivalência sem Make para clean)
- [ ] 2. Verificar .ahrena/install.py (usado para --clean)
- [ ] 3. Determinar terminal
- [ ] 4. Executar clean (make ou equivalente)
- [ ] 5. Reportar resultado
```

### Passo 1: Consultar codex-make

1. Ler `codex-make` (target `clean` e seção **Equivalência sem Make**)
2. Identificar o comando: `make clean [variáveis]` ou `python .ahrena/install.py --target . --clean`

### Passo 2: Verificar .ahrena/install.py

1. Para clean via equivalente: o script `install.py` com `--clean` remove os arquivos; se `.ahrena/` já foi removido, o comando pode falhar — nesse caso, informar que já está limpo
2. Se `make` estiver disponível, o Makefile chama `.ahrena/install.py --clean`; portanto `.ahrena/install.py` deve existir antes do clean (ou o Makefile está na raiz do repo)

### Passo 3: Determinar terminal

1. Ler `.ahrena/.directives` (seção `terminal`) conforme `lex-terminal-type`; se ausente, inferir do SO

### Passo 4: Executar clean

1. Se `make` disponível: executar `make clean [variáveis]` no diretório do projeto
2. Se `make` não disponível: executar `python .ahrena/install.py --target <TARGET> --clean` conforme codex-make
3. Capturar saída e código de saída

### Passo 5: Reportar resultado

1. Apresentar a saída ao usuário; em caso de falha, indicar erro e sugerir correção

## Saídas

| Saída | Formato |
|-------|---------|
| Sucesso | Saída do comando clean (confirmação de remoção) |
| Falha | Mensagem de erro e sugestão de correção |

## Referências

- `codex-make` — Target clean e equivalência sem Make
- `lex-terminal-type` — Tipo de terminal
- `cry-make` — Comando que pode invocar este Kata (target `clean`)
