# Cry: Nuevo Proyecto de Skill

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Inicialización de un nuevo proyecto de skill en el repositorio, en formato Anthropic Agent Skills, con layout Ahrena

## Descripción

Atajo para crear un nuevo proyecto de skill en `{paths.skills_root}/{slug}/` (default `skills/{slug}/`) a partir de la plantilla oficial. Invoca `kata-init-skill`, que valida el slug contra la spec Anthropic Agent Skills, copia `framework/templates/skill-project-sample/`, sustituye placeholders y garantiza `.gitignore` con `.build/`.

## Uso

```
/cry-new-skill <slug> [opciones]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `slug` | Sí | Nombre del proyecto en kebab-case (1-64 chars, `a-z`/`0-9`/hyphen, sin guion al inicio/final, sin `--`) | `scheduled-payments-skill` |
| `description=` | Sí | Frase única del frontmatter (1-1024 chars), con **qué hace** + **cuándo usar** | `description="Schedules transfers..."` |
| `language=` | No | BCP 47; default = `language.default` en `.directives` | `language=en` |
| `license=` | No | Identificador (`Apache-2.0`, `MIT`) o referencia | `license=Apache-2.0` |
| `human_title=` | No | Título humano para el `# H1` del `SKILL.md` | `human_title="Scheduled Payments"` |
| `with_widgets=` | No | `true` (default) o `false` | `with_widgets=false` |
| `with_tools=` | No | `true` (default) o `false` | `with_tools=false` |
| `with_scripts=` | No | `python` (default), `js`, o `false` | `with_scripts=js` |

## Lo que el Comando Hace

1. Valida slug y description contra la spec Anthropic Agent Skills (regex y límites)
2. Resuelve `paths.skills_root` en `.ahrena/.directives` (default `skills`)
3. Verifica que el destino `{paths.skills_root}/{slug}/` no exista
4. Invoca `kata-init-skill` con los parámetros recibidos
5. Reporta ruta creada, opt-outs aplicados, y próximos pasos

## Plantilla del Prompt

```
Contexto:
- slug: {{slug}}
- description: {{description}}
- language: {{language}} (opcional)
- license: {{license}} (opcional)
- human_title: {{human_title}} (opcional)
- with_widgets: {{with_widgets}} (default true)
- with_tools: {{with_tools}} (default true)
- with_scripts: {{with_scripts}} (default python)

Tarea:
Invoque kata-init-skill con los parámetros arriba. El kata:
1. Valida slug y description per codex-skill-anthropic-agent-skills
2. Copia framework/templates/skill-project-sample/ a
   {paths.skills_root}/{slug}/, sustituyendo placeholders
3. Aplica opt-outs (with_widgets, with_tools, with_scripts)
4. Garantiza .gitignore con .build/
5. Reporta el resultado

Aborte si: slug inválido, destino ya existe, o plantilla ausente.

Formato de salida:
Confirmación del proyecto creado, lista de subdirectorios, próximos pasos
para la autoría. En caso de error, mensaje específico y corrección sugerida.
```

## Ejemplo de Invocación

```
/cry-new-skill scheduled-payments-skill \
  description="Schedules and approves bank transfers using widgets connected to Python tools. Use when the user wants to create or approve a scheduled transfer." \
  license=Apache-2.0
```

**Salida esperada:**

```
✅ Proyecto creado: skills/scheduled-payments-skill/
   SKILL.md, skill.config.json, .skill-manifest.json
   widgets/ (React + TS)
   scripts/ (Python)
   tools/ (MCP placeholder)
   references/REFERENCE.md

.gitignore: .build/ agregado.

Próximos pasos:
- Editar SKILL.md (cuerpo)
- Agregar componentes en widgets/src/
- Agregar handlers en tools/handlers/
- cry-skill-dev / cry-skill-build llegan en el PR 2
```

## Restricciones

- El Cry no modifica `.ahrena/.directives` (per `lex-directives`)
- El Cry no crea proyecto si el destino ya existe; el usuario decide remover o elegir otro slug
- Los mensajes al usuario en el idioma de `language.default`; identificadores técnicos (slug, frontmatter, placeholder) preservados

## Diferencia respecto al Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Atajo 1:1 que recolecta parámetros y despacha | Procedimiento completo de scaffold (8 pasos) |
| **Validación** | Forma de los parámetros | Conformidad con la spec Anthropic + filesystem |
| **Efecto** | Invoca el Kata | Escribe archivos, actualiza `.gitignore` |

## Referencias

- `kata-init-skill` — procedimiento invocado
- `codex-skill-anthropic-agent-skills` — reglas de slug, description, frontmatter
- `codex-skill-project-architecture` — layout y rol de los subdirectorios
- `lex-skill-project-structure` — ley del layout
- `framework/templates/skill-project-sample/` — origen del scaffold
