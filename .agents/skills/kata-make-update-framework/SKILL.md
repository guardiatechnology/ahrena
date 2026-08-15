---
name: kata-make-update-framework
description: "Atualizar framework (Make update). Atualização da instalação do framework Ahrena via target update do Makefile"
---

# Kata: Atualizar framework (Make update)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Atualização da instalação do framework Ahrena via target `update` do Makefile

## Workflow

```
Progresso:
- [ ] 1. Consultar codex-make (variáveis e equivalência sem Make para update)
- [ ] 2. Verificar .ahrena/update.py
- [ ] 3. Determinar terminal
- [ ] 4. Executar update (make ou equivalente)
- [ ] 5. Reportar resultado
```

### Passo 1: Consultar codex-make

1. Ler `codex-make` (variáveis e seção **Equivalência sem Make**) para o target `update`
2. Identificar o comando a executar conforme as variáveis (remoto vs LOCAL/SOURCE)

### Passo 2: Verificar .ahrena/update.py

1. Verificar que o projeto tem `.ahrena/update.py` (instalação prévia do Ahrena)
2. Se não existir, informar que é necessário instalar antes (`/cry-make install` ou equivalente)

### Passo 3: Determinar terminal

1. Ler `.ahrena/.directives` (seção `terminal`) conforme `lex-terminal-type`; se ausente, inferir do SO
2. Usar o tipo para o comando equivalente (PowerShell no Windows, conforme codex-make)

### Passo 4: Executar update

1. Se `make` disponível: executar `make update [variáveis]` no diretório do projeto (ou conforme TARGET)
2. Se `make` não disponível: executar o comando da seção "Equivalência sem Make" do `codex-make` para atualização remota ou local
3. Capturar saída e código de saída

### Passo 5: Reportar resultado

1. Apresentar a saída ao usuário; em caso de falha, indicar erro e sugerir correção

## Saídas

| Saída | Formato |
|-------|---------|
| Sucesso | Saída do comando de atualização |
| Falha | Mensagem de erro e sugestão de correção |
