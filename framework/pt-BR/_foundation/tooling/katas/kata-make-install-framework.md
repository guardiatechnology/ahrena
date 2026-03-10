# Kata: Instalar framework (Make install)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Instalação do framework Ahrena via target `install` do Makefile

## Objetivo

Instalar o framework Ahrena no projeto (remoto ou local), executando o target `install` do Makefile — ou o comando equivalente em PowerShell/Python quando `make` não estiver disponível. Suporta variáveis PLATFORM, TARGET, SOURCE, LOCAL, VERSION, REPO e demais (ver `codex-make`).

## Quando Usar

- Quando o usuário invoca `/cry-make install` (com ou sem variáveis)
- Quando for necessário instalar o framework pela primeira vez ou reinstalar (remoto ou a partir de clone local)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Variáveis | Não | Ex.: `PLATFORM=cursor`, `TARGET=.`, `SOURCE=../ahrena`, `LOCAL=1`, `VERSION=main`, `REPO=...`. Consultar `codex-make` para a lista completa |

## Workflow

```
Progresso:
- [ ] 1. Consultar codex-make (variáveis e equivalência sem Make para install)
- [ ] 2. Verificar Makefile ou .ahrena/install.py
- [ ] 3. Determinar terminal
- [ ] 4. Executar install (make ou equivalente)
- [ ] 5. Reportar resultado
```

### Passo 1: Consultar codex-make

1. Ler `codex-make` (variáveis e seção **Equivalência sem Make**) para o target `install`
2. Identificar o comando a executar conforme as variáveis passadas (remoto vs LOCAL/SOURCE)

### Passo 2: Verificar Makefile ou .ahrena/install.py

1. Se na raiz do repo Ahrena: verificar que `Makefile` e `scripts/install.py` existem
2. Se em projeto que já tem Ahrena: verificar que `.ahrena/install.py` existe (ou que existe `Makefile` na raiz do repo para dev-install)
3. Em caso de ausência, informar ao usuário e sugerir correção

### Passo 3: Determinar terminal

1. Ler `.ahrena/.directives` (seção `terminal`) conforme `lex-terminal-type`; se ausente, inferir do SO
2. Usar o tipo para escolher a sintaxe do comando equivalente (PowerShell no Windows, conforme codex-make)

### Passo 4: Executar install

1. Se `make` disponível: executar `make install [variáveis]` no diretório correto (raiz do repo ou conforme TARGET)
2. Se `make` não disponível: executar o comando da seção "Equivalência sem Make" do `codex-make` para instalação remota, local (no repo) ou local (path), conforme variáveis
3. Capturar saída e código de saída

### Passo 5: Reportar resultado

1. Apresentar a saída ao usuário; em caso de falha, indicar erro e sugerir correção (ex.: equivalência sem Make, verificação de path)

## Saídas

| Saída | Formato |
|-------|---------|
| Sucesso | Saída do comando de instalação |
| Falha | Mensagem de erro e sugestão de correção |

## Referências

- `codex-make` — Variáveis e equivalência sem Make para `install`
- `lex-terminal-type` — Tipo de terminal
- `cry-make` — Comando que pode invocar este Kata (target `install`)
