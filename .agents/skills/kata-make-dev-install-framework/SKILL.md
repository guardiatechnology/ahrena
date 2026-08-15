---
name: kata-make-dev-install-framework
description: "Instalar framework a partir do desenvolvimento (Make dev-install). Instalação do framework Ahrena a partir do diretório atual (raiz do repo), target dev-install"
---

# Kata: Instalar framework a partir do desenvolvimento (Make dev-install)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Instalação do framework Ahrena a partir do diretório atual (raiz do repo), target `dev-install`

## Workflow

```
Progresso:
- [ ] 1. Consultar codex-make (equivalência sem Make para dev-install)
- [ ] 2. Verificar que está na raiz do repo Ahrena (framework/, scripts/)
- [ ] 3. Determinar terminal
- [ ] 4. Executar dev-install (make ou equivalente)
- [ ] 5. Reportar resultado
```

### Passo 1: Consultar codex-make

1. Ler `codex-make` (target `dev-install` e seção **Equivalência sem Make** para instalação local no repo Ahrena)
2. Identificar o comando: `make dev-install [variáveis]` ou `python scripts/install.py --local --target . [--platform cursor]` etc.

### Passo 2: Verificar raiz do repo Ahrena

1. Confirmar que existem `framework/` e `scripts/install.py` no diretório atual (ou no diretório de trabalho)
2. Se não existir, informar que dev-install deve ser executado na raiz do repositório Ahrena

### Passo 3: Determinar terminal

1. Ler `.ahrena/.directives` (seção `terminal`) conforme `lex-terminal-type`; se ausente, inferir do SO

### Passo 4: Executar dev-install

1. Se `make` disponível: executar `make dev-install [variáveis]` na raiz do repo Ahrena
2. Se `make` não disponível: executar `python scripts/install.py --local --target <TARGET> [--platform cursor]` conforme codex-make (sem --repo/--version)
3. Capturar saída e código de saída

### Passo 5: Reportar resultado

1. Apresentar a saída ao usuário; em caso de falha, indicar erro e sugerir correção

## Saídas

| Saída | Formato |
|-------|---------|
| Sucesso | Saída do comando dev-install |
| Falha | Mensagem de erro e sugestão de correção |
