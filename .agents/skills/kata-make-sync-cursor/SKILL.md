---
name: kata-make-sync-cursor
description: "Sincronizar .cursor/ (Make sync-cursor). Regenerar .cursor/ a partir de .ahrena/framework/ e .ahrena/artifacts/ via target sync-cursor"
---

# Kata: Sincronizar .cursor/ (Make sync-cursor)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Regenerar `.cursor/` a partir de `.ahrena/framework/` e `.ahrena/artifacts/` via target `sync-cursor`

## Workflow

```
Progresso:
- [ ] 1. Consultar codex-make (equivalência sem Make para sync-cursor)
- [ ] 2. Verificar .ahrena/update.py e .ahrena/.directives
- [ ] 3. Determinar terminal
- [ ] 4. Executar sync-cursor (make ou equivalente)
- [ ] 5. Reportar resultado
```

### Passo 1: Consultar codex-make

1. Ler `codex-make` (target `sync-cursor` e seção **Equivalência sem Make**)
2. Identificar o comando: `make sync-cursor [variáveis]` ou `python .ahrena/update.py --target . --sync-cursor`

### Passo 2: Verificar .ahrena/update.py e .ahrena/.directives

1. Verificar que o projeto tem `.ahrena/update.py` e `.ahrena/.directives` (instalação prévia do Ahrena)
2. Se não existir, informar que é necessário instalar antes (`/cry-make install` ou bootstrap)

### Passo 3: Determinar terminal

1. Ler `.ahrena/.directives` (seção `terminal`) conforme `lex-terminal-type`; se ausente, inferir do SO

### Passo 4: Executar sync-cursor

1. Se `make` disponível: executar `make sync-cursor [variáveis]` no diretório do projeto
2. Se `make` não disponível: executar `python .ahrena/update.py --target <TARGET> --sync-cursor` conforme codex-make
3. Capturar saída e código de saída

### Passo 5: Reportar resultado

1. Apresentar a saída ao usuário; em caso de falha, indicar erro e sugerir correção

## Saídas

| Saída | Formato |
|-------|---------|
| Sucesso | Saída do comando sync-cursor |
| Falha | Mensagem de erro e sugestão de correção |
