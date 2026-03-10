# Cry: Ejecutar Makefile

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Ejecución de targets del Makefile del repositorio Ahrena

## Descripción

Comando rápido para ejecutar un target del Makefile en la raíz del repositorio Ahrena. El Cry **elige el Kata** según el target indicado por el usuario y delega la ejecución. Consulta `codex-make` para variables y equivalencia sin Make.

## Uso

```
/cry-make <target> [variables]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `target` | Sí | Target del Makefile a ejecutar | `install`, `update`, `dev-install`, `bootstrap` |
| `variables` | No | Variables para make (formato `NOMBRE=valor`) | `PLATFORM=cursor`, `SOURCE=../ahrena`, `LOCAL=1` |

Para la lista completa de targets y variables, consulte `codex-make`.

## Despacho por target

| Target | Kata ejecutado |
|--------|----------------|
| `install` | `kata-make-install-framework` |
| `update` | `kata-make-update-framework` |
| `dev-install` | `kata-make-dev-install-framework` |
| `bootstrap` | `kata-make-bootstrap-framework` |
| `sync-cursor` | `kata-make-sync-cursor` |
| `uninstall` | `kata-make-uninstall-framework` |
| `clean` | `kata-make-clean-framework` |

Los targets no listados arriba son inválidos para este Cry; informe al usuario y liste los targets válidos.

## Qué hace el comando

1. Valida el target con base en la tabla anterior (targets del `codex-make`)
2. Si el target es inválido: informe al usuario y liste los targets válidos; no ejecute kata
3. Según el target válido, elige el Kata correspondiente (tabla anterior)
4. Ejecuta el Kata elegido con las variables proporcionadas
5. El Kata verifica el entorno, ejecuta `make` o el equivalente (conforme codex-make) y reporta el resultado
6. Presenta la salida al usuario o el error con sugerencia de corrección

## Prompt Template

```
Contexto:
- Target: {{target}}
- Variables: {{variables}} (opcional)

Tarea:
Según el target solicitado, ejecute el Kata correspondiente:
- install → kata-make-install-framework
- update → kata-make-update-framework
- dev-install → kata-make-dev-install-framework
- bootstrap → kata-make-bootstrap-framework
- sync-cursor → kata-make-sync-cursor
- uninstall → kata-make-uninstall-framework
- clean → kata-make-clean-framework
- target no listado arriba → informe target inválido y liste los targets válidos (no ejecute kata)

Consulte codex-make para variables válidas y equivalencia sin Make cuando
make no esté disponible. Reporte la salida del comando o el error con
sugerencia de corrección.

Formato de salida:
Salida del comando ejecutado o mensaje de error con indicación de cómo corregir.
```

## Ejemplo de invocación

**Instalar para Cursor:**

```
/cry-make install PLATFORM=cursor
```

**Salida esperada:** salida de `make install PLATFORM=cursor` (o del comando equivalente en PowerShell, si make no está disponible).

**Actualizar desde local:**

```
/cry-make update LOCAL=1
```

## Diferencia de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Punto de entrada; decide qué Kata ejecutar según el target; targets inválidos → mensaje y lista | Procedimiento específico por target (install, update, dev-install, bootstrap, sync-cursor, uninstall, clean) |
| **Parámetros** | Mínimos (target + variables opcionales) | Variables procesadas; consulta al codex-make |
| **Contenido** | No contiene tablas de referencia; solo la tabla de despacho | No duplica tablas; remite al codex-make |

## Referencias

- `kata-make-install-framework` — Instalación del framework (target `install`)
- `kata-make-update-framework` — Actualización (target `update`)
- `kata-make-dev-install-framework` — Instalación desde desarrollo (target `dev-install`)
- `kata-make-bootstrap-framework` — Primera instalación (target `bootstrap`)
- `kata-make-sync-cursor` — Regenerar .cursor/ (target `sync-cursor`)
- `kata-make-uninstall-framework` — Desinstalar (target `uninstall`)
- `kata-make-clean-framework` — Limpiar sin confirmación (target `clean`)
- `codex-make` — Variables, targets y equivalencia sin Make
- `Makefile` — Archivo en la raíz del repositorio
