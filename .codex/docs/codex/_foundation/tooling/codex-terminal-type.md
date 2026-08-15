# Codex: Tipo de Terminal (Bash e PowerShell)

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Uso de bash e PowerShell em projetos Ahrena

## Conteúdo

### Declaração nas Diretivas

O tipo de terminal pode ser definido em `.ahrena/.directives` na seção `terminal`:

```yaml
# ─── Terminal ─────────────────────────────────────────────────
# Shell usado para comandos no projeto. Valores: bash | powershell

terminal: powershell   # Windows nativo
# terminal: bash      # Linux, macOS, WSL
```

| Valor        | Uso típico                    |
|-------------|--------------------------------|
| `bash`      | Linux, macOS, WSL, Git Bash no Windows |
| `powershell`| Windows (PowerShell Core ou Windows PowerShell) |

Se a seção não existir, o agente infere a partir do sistema operacional (por exemplo, Windows → PowerShell) ou pergunta ao usuário.

### Quando Usar Cada Shell

| Cenário                         | Recomendação     |
|---------------------------------|------------------|
| Projeto desenvolvido só no Windows | `powershell`   |
| Projeto só em Linux/macOS ou WSL | `bash`          |
| Projeto multiplataforma (CI em Linux, dev em Windows) | Definir um padrão (ex.: `bash` para scripts versionados, documentar PowerShell em README se necessário) |
| Repositório Ahrena (framework)  | Pode usar `bash` como padrão; documentar alternativas em PowerShell quando relevante |

### Equivalências Comuns

Comandos e conceitos frequentemente necessários, lado a lado:

| Ação              | Bash                    | PowerShell                    |
|-------------------|-------------------------|------------------------------|
| Listar arquivos   | `ls` ou `find . -type f`| `Get-ChildItem` ou `Get-ChildItem -Recurse` |
| Variável de ambiente | `echo $VAR`          | `$env:VAR` ou `$env:VAR`     |
| Definir variável  | `export VAR=valor`      | `$env:VAR = "valor"`          |
| Diretório atual   | `pwd`                   | `Get-Location` ou `(Get-Location).Path` |
| Mudar diretório   | `cd path`               | `Set-Location path` ou `cd path` |
| Concatenar comandos | `cmd1 && cmd2`        | `cmd1; cmd2` ou `cmd1; if ($?) { cmd2 }` |
| Pipe               | `cmd1 | cmd2`            | `cmd1 | cmd2`                  |
| Redirecionar saída | `cmd > arquivo`         | `cmd > arquivo` ou `cmd | Out-File arquivo` |
| Executar script   | `./script.sh` ou `bash script.sh` | `.\script.ps1` ou `pwsh -File script.ps1` |

### Convenções para Documentação

1. **Um shell por artefato:** quando o projeto define um único tipo de terminal, exemplos em documentação (README, Katas, Cries) devem usar apenas esse tipo.
2. **Dois shells:** se for necessário cobrir bash e PowerShell no mesmo documento, use blocos identificados (por exemplo, "Bash:" e "PowerShell:" ou abas/seções separadas).
3. **Comentários:** em scripts, use comentários que indiquem o shell (`# bash` ou `# PowerShell`) quando não estiver óbvio pelo contexto.

### Restrições Técnicas

- O valor de `terminal` em `.ahrena/.directives` deve ser exatamente `bash` ou `powershell` (minúsculas).
- Scripts versionados no repositório devem ser nomeados de forma consistente (por exemplo, `.sh` para bash, `.ps1` para PowerShell) e documentados no README ou neste Codex quando necessário.
