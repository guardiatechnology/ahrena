# Kata: Desinstalar framework (Make uninstall)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Remoção da instalação do framework Ahrena via target `uninstall` do Makefile

## Objetivo

Remover a instalação do framework Ahrena do projeto, com confirmação do usuário (salvo uso de flag de força). Equivalente ao target `uninstall` do Makefile — ou ao comando equivalente em PowerShell/Python quando `make` não estiver disponível.

## Quando Usar

- Quando o usuário invoca `/cry-make uninstall` (com ou sem variáveis, ex.: TARGET)
- Quando for necessário desinstalar o Ahrena do projeto (remove `.ahrena/` e arquivos do Ahrena em `.cursor/`)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Variáveis | Não | Ex.: `TARGET=.`. Consultar `codex-make` |

## Workflow

```
Progresso:
- [ ] 1. Consultar codex-make (equivalência sem Make para uninstall)
- [ ] 2. Verificar .ahrena/uninstall.py
- [ ] 3. Determinar terminal
- [ ] 4. Executar uninstall (make ou equivalente)
- [ ] 5. Reportar resultado
```

### Passo 1: Consultar codex-make

1. Ler `codex-make` (target `uninstall` e seção **Equivalência sem Make**)
2. Identificar o comando: `make uninstall [variáveis]` ou `python .ahrena/uninstall.py --target .` (e opcionalmente `--force` para pular confirmação)

### Passo 2: Verificar .ahrena/uninstall.py

1. Verificar que o projeto tem `.ahrena/uninstall.py`
2. Se não existir, informar que o Ahrena pode já ter sido removido ou que a instalação está incompleta

### Passo 3: Determinar terminal

1. Ler `.ahrena/.directives` (seção `terminal`) conforme `lex-terminal-type`; se ausente, inferir do SO

### Passo 4: Executar uninstall

1. Se `make` disponível: executar `make uninstall [variáveis]` no diretório do projeto
2. Se `make` não disponível: executar `python .ahrena/uninstall.py --target <TARGET>` conforme codex-make (o script pode pedir confirmação)
3. Capturar saída e código de saída

### Passo 5: Reportar resultado

1. Apresentar a saída ao usuário; em caso de falha, indicar erro e sugerir correção

## Saídas

| Saída | Formato |
|-------|---------|
| Sucesso | Saída do comando uninstall (confirmação de remoção) |
| Falha | Mensagem de erro e sugestão de correção |

## Referências

- `codex-make` — Target uninstall e equivalência sem Make
- `lex-terminal-type` — Tipo de terminal
- `cry-make` — Comando que pode invocar este Kata (target `uninstall`)
