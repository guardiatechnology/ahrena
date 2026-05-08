# Kata: Inicializar proyecto de skill (scaffold)

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Scaffold de un nuevo proyecto de skill en `{paths.skills_root}/{slug}/` a partir de la plantilla `framework/templates/skill-project-sample/`

## Objetivo

Crear un nuevo proyecto de skill en el repositorio a partir de la plantilla oficial, validando el slug contra la spec Anthropic Agent Skills, sustituyendo placeholders, garantizando `.gitignore` con `.build/`, y dejando el proyecto listo para la autoría per `lex-skill-project-structure` y `codex-skill-project-architecture`.

## Cuándo Usar

- Cuando el usuario invoca `/cry-new-skill <slug>`
- Cuando un agente (humano o IA) necesita iniciar un nuevo proyecto de skill antes de producir widgets, scripts o tools

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `slug` | Sí | Nombre del proyecto en kebab-case; idéntico al `name` que se grabará en `SKILL.md` (1-64 chars, `a-z`/`0-9`/hyphen, sin guion al inicio/final, sin `--` consecutivo) |
| `description` | Sí | Frase única para el frontmatter (1-1024 chars); incluye **qué hace** y **cuándo usar** |
| `language` | No | BCP 47; default = `language.default` en `.ahrena/.directives` |
| `license` | No | Identificador (ej.: `Apache-2.0`); default vacío (campo omitido) |
| `human_title` | No | Título humano para el `# H1` en el cuerpo del `SKILL.md`; default = capitalización legible del slug |
| `with_widgets` | No | `true` (default) o `false` (controla si `widgets/` permanece en el scaffold) |
| `with_tools` | No | `true` (default) o `false` |
| `with_scripts` | No | `true` (default), `false`, `python` (default cuando true) o `js` |

## Workflow

```
Progreso:
- [ ] 1. Validar slug y description
- [ ] 2. Resolver paths y destino
- [ ] 3. Verificar precondiciones (plantilla existe, destino libre)
- [ ] 4. Copiar plantilla y sustituir placeholders
- [ ] 5. Aplicar opt-outs (with_widgets/tools/scripts)
- [ ] 6. Garantizar .gitignore con .build/
- [ ] 7. Validar resultado
- [ ] 8. Reportar
```

### Paso 1: Validar slug y description

1. Aplicar la regex `^[a-z0-9](?:(?:[a-z0-9]|-(?!-)){0,62}[a-z0-9])?$` al slug (1-64 chars, sin guion al inicio/final, sin `--`)
2. Rechazar slugs con palabras reservadas (`anthropic`, `claude`) per documentación Anthropic
3. Verificar que `description` tenga 1-1024 chars; rechazar vacío
4. En caso de violación, abortar con mensaje indicando la regla (citar `codex-skill-anthropic-agent-skills`)

### Paso 2: Resolver paths y destino

1. Leer `.ahrena/.directives` (per `lex-directives`); usar `paths.skills_root` (default `skills`), `paths.skills_build` (default `.build`), `paths.skills_dist` (default `.dist`)
2. Resolver `language` ausente para `language.default`
3. Calcular destino: `{paths.skills_root}/{slug}/`

### Paso 3: Verificar precondiciones

1. Confirmar que `framework/templates/skill-project-sample/` existe (origen)
2. Confirmar que el destino **no existe** — si existe, abortar con instrucción de remover o elegir otro slug; nunca sobrescribir
3. Garantizar que `paths.skills_root` existe (crear directorio si está ausente)

### Paso 4: Copiar plantilla y sustituir placeholders

1. Copiar el árbol de `framework/templates/skill-project-sample/` a `{paths.skills_root}/{slug}/`, **omitiendo** el `README.md` raíz de la plantilla (documentación interna del framework)
2. Sustituir placeholders en los archivos copiados:

| Placeholder | Valor |
|-------------|-------|
| `__SLUG__` | `slug` |
| `__BCP47__` | `language` resuelto |
| `__HUMAN_TITLE__` | `human_title` (default: capitalización legible del slug) |
| `__ONE_SENTENCE_DESCRIPTION_INCLUDING_WHEN_TO_USE__` | `description` |
| `__LICENSE_OR_REFERENCE__` | `license` cuando está informado; cuando ausente, **remover la línea `license:`** del frontmatter |

3. La sustitución es literal (string-match), en todos los archivos textuales (`.md`, `.json`, `.tsx`, `.ts`, `.py`, `package.json`, etc.)

### Paso 5: Aplicar opt-outs

1. `with_widgets=false`: remover el directorio `widgets/`; remover la mención a widgets en el `SKILL.md` (sección "Tools, scripts, and widgets")
2. `with_tools=false`: remover el directorio `tools/`
3. `with_scripts=false`: remover el directorio `scripts/`
4. `with_scripts=js`: cambiar el valor `runtimes.scripts` en `skill.config.json` a `node`; ajustar `scripts/README.md` removiendo la sección de Python; mantener `scripts/` vacío con `.gitkeep`
5. `with_scripts=python`: mantener como está (default de la plantilla)

### Paso 6: Garantizar `.gitignore`

1. Verificar `.gitignore` en la raíz del repositorio
2. Si la entrada `{paths.skills_build}/` (o `.build/` cuando default) no existe, **agregarla** con cabecera de comentario:

```
# External skill projects — build intermediates (per lex-skill-project-structure)
.build/
```

3. Si ya existe, no duplicar

### Paso 7: Validar resultado

1. Confirmar que `{paths.skills_root}/{slug}/SKILL.md` existe
2. Confirmar que `{paths.skills_root}/{slug}/skill.config.json` existe
3. Confirmar que el frontmatter de `SKILL.md` tiene `name: {slug}` (validar igualdad)
4. Confirmar que **ningún** placeholder `__...__` permanece en los archivos del proyecto creado

### Paso 8: Reportar

1. Mostrar al usuario:
   - Ruta del proyecto creado
   - Slug, description, language, license aplicados
   - Subdirectorios incluidos (widgets/scripts/tools, según opt-outs)
   - Próximos pasos: editar el cuerpo del `SKILL.md`, agregar componentes en `widgets/src/`, etc.
2. Apuntar a `codex-skill-project-architecture` para la autoría.

## Salidas

| Salida | Formato |
|--------|---------|
| Éxito | Directorio `{paths.skills_root}/{slug}/` poblado; `.gitignore` actualizado cuando necesario |
| Falla (slug inválido) | Mensaje citando `codex-skill-anthropic-agent-skills`; ningún archivo creado |
| Falla (destino existe) | Mensaje instruyendo remover o cambiar slug; ningún archivo modificado |
| Falla (plantilla ausente) | Mensaje indicando que `framework/templates/skill-project-sample/` está faltando — posible corrupción de la instalación |

## Ejemplo de Ejecución

### Input

```
/cry-new-skill scheduled-payments-skill \
  description="Schedules and approves bank transfers using widgets connected to Python tools. Use when the user wants to create or approve a scheduled transfer." \
  license=Apache-2.0
```

### Salida esperada

```
✅ Proyecto creado: skills/scheduled-payments-skill/
   ├── SKILL.md                 (name: scheduled-payments-skill, language: es, license: Apache-2.0)
   ├── skill.config.json
   ├── .skill-manifest.json
   ├── references/REFERENCE.md
   ├── scripts/                 (Python — pyproject.toml a agregar al iniciar)
   ├── tools/                   (mcp.config.json placeholder)
   └── widgets/                 (React — package.json + tsconfig.json listos)

.gitignore actualizado: .build/ agregado.

Próximos pasos:
- Editar skills/scheduled-payments-skill/SKILL.md (cuerpo)
- Agregar componentes en widgets/src/
- Agregar handlers en tools/handlers/
```

## Restricciones

- No sobrescribir proyecto existente
- No modificar `.directives`
- No tocar `.build/` ni `.dist/` (esas carpetas pertenecen al build y al packaging de los PRs futuros)
- Todo mensaje al usuario en pt-BR, es o en según `language.default`; nombres técnicos (slug, frontmatter, placeholder) preservados
- Slug inválido aborta el kata sin efecto colateral

## Referencias

- `codex-skill-anthropic-agent-skills` — reglas de naming, frontmatter, layout
- `codex-skill-project-architecture` — arquitectura del proyecto fuente y mapeo spec ↔ Ahrena
- `lex-skill-project-structure` — ley del layout y separación fuente/build/dist
- `lex-template-usage` — uso obligatorio de plantilla
- `lex-directives` — lectura de `paths.skills_*`
- `lex-terminal-type` — sintaxis de comandos shell cuando el kata necesita tocar el filesystem en PowerShell vs. bash
- `cry-new-skill` — punto de entrada del usuario
- `framework/templates/skill-project-sample/` — origen del scaffold
