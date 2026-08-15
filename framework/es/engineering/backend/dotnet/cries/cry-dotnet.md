# Cry: Trabajo .NET

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Entrada única para implementación, review, refactorización y debug .NET

## Descripción

Invoca Apollo-.NET y `kata-dotnet-delivery` en el modo solicitado, usando el contrato técnico real del repositorio.

## Uso

```
/cry-dotnet <implement|review|refactor|debug> <objetivo> [evidencia]
```

## Parámetros

| Parámetro | Obligatorio | Descripción |
|---|:---:|---|
| `modo` | Sí | Operación a ejecutar |
| `objetivo` | Sí | Feature, diff, componente o fallo |
| `evidencia` | No | Issue, logs, stack trace, contrato o restricciones |

## Lo que Hace el Comando

1. Invoca `warrior-apollo-dotnet` con el contexto recibido.
2. El Warrior ejecuta `kata-dotnet-delivery` en el modo indicado.
3. Devuelve cambio validado, findings priorizados o diagnóstico con evidencia.

## Prompt Template

```
Contexto:
- Modo: {{modo}}
- Objetivo: {{objetivo}}
- Evidencia: {{evidencia}}

Tarea:
Asume `warrior-apollo-dotnet` y ejecuta `kata-dotnet-delivery`. Descubre SDK/TFM y comandos del repositorio antes de actuar. Aplica las Lexis .NET, `codex-dotnet-engineering`, `codex-code-design` y `codex-domain-driven-design` cuando exista trabajo de dominio.

Salida:
- Resultado principal
- Validaciones ejecutadas y resultados
- Riesgos residuales o bloqueos
```

## Ejemplo de Invocación

`/cry-dotnet implement "Agregar autorización idempotente" "Contrato OAS en docs/cards/oas"`

## Diferencia de Kata

| Aspecto | Cry | Kata |
|---|---|---|
| Papel | Entrada rápida | Procedimiento completo y verificable |
| Inputs | Modo, objetivo, evidencia | Descubrimiento, baseline, ejecución y validación |
| Lógica | Delega | Define pasos |

## Restricciones

- El Cry no ejecuta herramientas directamente; delega al Kata mediante el Warrior.
- Si el modo es inválido, solicitar corrección antes de continuar.

## Referencias

- `warrior-apollo-dotnet`, `kata-dotnet-delivery`
