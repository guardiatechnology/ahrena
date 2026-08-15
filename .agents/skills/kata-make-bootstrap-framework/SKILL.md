---
name: kata-make-bootstrap-framework
description: "Bootstrap do framework (Make bootstrap). Primeira instalação do framework Ahrena via target bootstrap do Makefile"
---

# Kata: Bootstrap do framework (Make bootstrap)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Primeira instalação do framework Ahrena via target `bootstrap` do Makefile

## Workflow

```
Progresso:
- [ ] 1. Consultar codex-make (equivalência sem Make para bootstrap)
- [ ] 2. Determinar terminal
- [ ] 3. Executar bootstrap (make ou equivalente)
- [ ] 4. Reportar resultado
```

### Passo 1: Consultar codex-make

1. Ler `codex-make` (target `bootstrap` e seção **Equivalência sem Make** para bootstrap)
2. Identificar o comando: `make bootstrap [variáveis]` ou o one-liner PowerShell (baixar install.py, executar, remover)

### Passo 2: Determinar terminal

1. Ler `.ahrena/.directives` (seção `terminal`) conforme `lex-terminal-type`; se ausente, inferir do SO (em bootstrap pode não existir ainda `.ahrena/`; inferir do SO)

### Passo 3: Executar bootstrap

1. Se `make` disponível: executar `make bootstrap [variáveis]` no diretório do projeto
2. Se `make` não disponível: executar o comando da seção "Equivalência sem Make" do `codex-make` para bootstrap (baixar install.py do GitHub, executar com variáveis, remover o script)
3. Capturar saída e código de saída

### Passo 4: Reportar resultado

1. Apresentar a saída ao usuário; em caso de falha, indicar erro e sugerir correção

## Saídas

| Saída | Formato |
|-------|---------|
| Sucesso | Saída do comando de bootstrap |
| Falha | Mensagem de erro e sugestão de correção |
