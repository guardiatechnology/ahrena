# Codex: Tipo de Terminal (Bash y PowerShell)

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Uso de bash y PowerShell en proyectos Ahrena

## Visión General

Este Codex es la referencia para el uso de **bash** y **PowerShell** en el contexto del Ahrena. Define cómo declarar el tipo de terminal en las directivas, cuándo usar cada uno, equivalencias comunes entre ambos y buenas prácticas para documentación y scripts. Se consulta junto con `lex-terminal-type`.

## Contexto

- **Dominio:** Ejecución de comandos en shell; scripts y ejemplos en documentación.
- **Público objetivo:** Agentes de IA que ejecutan o generan comandos de terminal; desarrolladores que mantienen scripts y documentación.
- **Actualización:** Cuando el proyecto adopte otro shell o se alteren las convenciones de terminal.

## Contenido

### Declaración en las Directivas

El tipo de terminal puede definirse en `.ahrena/.directives` en la sección `terminal`:

```yaml
# ─── Terminal ─────────────────────────────────────────────────
# Shell usado para comandos en el proyecto. Valores: bash | powershell

terminal: powershell   # Windows nativo
# terminal: bash      # Linux, macOS, WSL
```

| Valor        | Uso típico                    |
|-------------|--------------------------------|
| `bash`      | Linux, macOS, WSL, Git Bash en Windows |
| `powershell`| Windows (PowerShell Core o Windows PowerShell) |

Si la sección no existe, el agente infiere a partir del sistema operativo (por ejemplo, Windows → PowerShell) o pregunta al usuario.

### Cuándo Usar Cada Shell

| Escenario                         | Recomendación     |
|-----------------------------------|-------------------|
| Proyecto desarrollado solo en Windows | `powershell`   |
| Proyecto solo en Linux/macOS o WSL | `bash`          |
| Proyecto multiplataforma (CI en Linux, desarrollo en Windows) | Definir un estándar (ej.: `bash` para scripts versionados; documentar PowerShell en README si aplica) |
| Repositorio Ahrena (framework)    | Puede usar `bash` como estándar; documentar alternativas en PowerShell cuando sea relevante |

### Equivalencias Comunes

Comandos y conceptos frecuentemente necesarios, lado a lado:

| Acción              | Bash                    | PowerShell                    |
|---------------------|-------------------------|-------------------------------|
| Listar archivos     | `ls` o `find . -type f` | `Get-ChildItem` o `Get-ChildItem -Recurse` |
| Variable de entorno | `echo $VAR`             | `$env:VAR` o `$env:VAR`       |
| Definir variable    | `export VAR=valor`      | `$env:VAR = "valor"`          |
| Directorio actual   | `pwd`                   | `Get-Location` o `(Get-Location).Path` |
| Cambiar directorio  | `cd path`               | `Set-Location path` o `cd path` |
| Concatenar comandos | `cmd1 && cmd2`          | `cmd1; cmd2` o `cmd1; if ($?) { cmd2 }` |
| Pipe                | `cmd1 | cmd2`            | `cmd1 | cmd2`                  |
| Redirigir salida    | `cmd > archivo`         | `cmd > archivo` o `cmd | Out-File archivo` |
| Ejecutar script     | `./script.sh` o `bash script.sh` | `.\script.ps1` o `pwsh -File script.ps1` |

### Convenciones para Documentación

1. **Un shell por artefacto:** cuando el proyecto define un único tipo de terminal, los ejemplos en documentación (README, Katas, Cries) deben usar solo ese tipo.
2. **Dos shells:** si es necesario cubrir bash y PowerShell en el mismo documento, use bloques identificados (por ejemplo, "Bash:" y "PowerShell:" o pestañas/secciones separadas).
3. **Comentarios:** en scripts, use comentarios que indiquen el shell (`# bash` o `# PowerShell`) cuando no sea obvio por el contexto.

### Restricciones Técnicas

- El valor de `terminal` en `.ahrena/.directives` debe ser exactamente `bash` o `powershell` (minúsculas).
- Los scripts versionados en el repositorio deben nombrarse de forma consistente (por ejemplo, `.sh` para bash, `.ps1` para PowerShell) y documentarse en el README o en este Codex cuando sea necesario.

## Glosario

| Término     | Definición |
|------------|------------|
| bash       | Shell estándar en Linux y macOS; disponible en Windows vía WSL o Git Bash. |
| PowerShell | Shell de Microsoft; disponible en Windows (Windows PowerShell o PowerShell Core) y en Linux/macOS (PowerShell Core). |
| terminal   | Tipo de intérprete de comandos (bash o PowerShell) usado en el proyecto para ejecutar y documentar comandos de shell. |

## Referencias

- `lex-terminal-type` — Ley que exige el uso del tipo de terminal definido en las directivas.
- `lex-directives` — Consulta obligatoria a `.ahrena/.directives`.
- [PowerShell Documentation](https://docs.microsoft.com/powershell/)
- [Bash Reference Manual](https://www.gnu.org/software/bash/manual/)
