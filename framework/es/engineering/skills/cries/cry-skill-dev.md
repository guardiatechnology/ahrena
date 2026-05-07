# Cry: Dev server local de skill

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para levantar widgets HMR + script runner + tool stub en localhost para un proyecto de skill

## Descripción

Atajo que invoca `kata-skill-dev-server` para levantar el entorno de desarrollo local de un skill en `{paths.skills_root}/{slug}/`. Levanta solo los subservidores aplicables al proyecto (widgets/scripts/tools) conforme a la presencia de cada subdirectorio. Los ports default son `5173` (widgets), `5174` (scripts), `5175` (tool stub), con override vía parámetros.

## Uso

```
/cry-skill-dev <slug> [opciones]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `slug` | Sí | Proyecto en `{paths.skills_root}/{slug}/` | `hello-skill` |
| `widgets_port=` | No | Override (default `5173` o `dev_server.widgets_port`) | `widgets_port=5180` |
| `scripts_port=` | No | Override (default `5174`) | `scripts_port=5181` |
| `tools_stub_port=` | No | Override (default `5175`) | `tools_stub_port=5182` |
| `only=` | No | Subconjunto (`widgets`, `scripts`, `tools`); default todos | `only=widgets` |

## Qué Hace el Comando

1. Resuelve `paths.skills_root` en `.ahrena/.directives`
2. Confirma la existencia del proyecto y la lectura de `skill.config.json`
3. Invoca `kata-skill-dev-server` con los parámetros recibidos
4. Mantiene foreground con logs prefijados (`[widgets]`, `[scripts]`, `[tools]`) hasta Ctrl-C

## Prompt Template

```
Contexto:
- slug: {{slug}}
- widgets_port: {{widgets_port}} (opcional)
- scripts_port: {{scripts_port}} (opcional)
- tools_stub_port: {{tools_stub_port}} (opcional)
- only: {{only}} (opcional)

Tarea:
Invoque kata-skill-dev-server con los parámetros de arriba. El kata:
1. Resuelve paths y config
2. Verifica precondiciones (manifests, deps, ports)
3. Levanta widgets (Vite HMR), script runner y tool stub conforme aplica
4. Reporta URLs e instrucciones
5. Mantiene foreground hasta interrupción del usuario

Aborte si: proyecto inexistente, manifest inválido, port ocupada sin override.

Formato de salida:
URLs activas + foreground con logs hasta Ctrl-C. En caso de error, mensaje
específico y corrección sugerida.
```

## Ejemplo de Invocación

```
/cry-skill-dev hello-skill
```

**Salida esperada:**

```
✅ Dev server activo para hello-skill:
   Widgets:      http://localhost:5173/        (HMR Vite)
   (sin scripts/ — omitido)
   (sin tools/ — omitido)

Presione Ctrl-C para finalizar.
```

## Restricciones

- El Cry **no modifica** `skills/{slug}/` (solo lectura)
- El Cry **no escribe** en `.build/` ni `.dist/`
- Mensajes al usuario en `language.default`; identificadores técnicos preservados
- `lex-terminal-type`: respeta el terminal definido en `.directives`

## Diferencia con Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Atajo 1:1 | Procedimiento operacional (7 pasos) |
| **Validación** | Forma de los parámetros | Precondiciones, manifests, ports |
| **Efecto** | Invoca el kata | Levanta procesos, mantiene foreground |

## Referencias

- `kata-skill-dev-server` — procedimiento invocado
- `codex-skill-build-pipeline` — defaults de tooling y ports
- `codex-skill-tools-and-widgets` — schemas validados antes de levantar
- `cry-skill-build` — paso siguiente para generar `.build/`
