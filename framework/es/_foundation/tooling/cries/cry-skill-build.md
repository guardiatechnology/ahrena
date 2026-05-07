# Cry: Build de skill

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para invocar `kata-build-skill` y producir `.build/{slug}/` + zip a partir de la fuente versionada

## Descripción

Atajo que invoca `kata-build-skill` para un proyecto en `{paths.skills_root}/{slug}/`, ejecutando el pipeline determinístico (Validate → Build widgets → Freeze scripts → Resolve tools → Rewrite bindings → Emit) descrito en `codex-skill-build-pipeline`. El resultado es `{paths.skills_build}/{slug}/` + `{paths.skills_build}/{slug}.zip`, testeables en otro agente Claude Code antes del empaquetado final en `.dist/` (PR 3).

## Uso

```
/cry-skill-build <slug> [opciones]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `slug` | Sí | Proyecto en `{paths.skills_root}/{slug}/` | `hello-skill` |
| `clean` | No | `true` borra `.build/{slug}/` antes; default `false` | `clean=true` |
| `skip_zip` | No | `true` omite la emisión del zip; default `false` | `skip_zip=true` |

## Qué Hace el Comando

1. Resuelve `paths.skills_root`, `paths.skills_build` en `.ahrena/.directives`
2. Confirma la existencia del proyecto fuente
3. Invoca `kata-build-skill` con los parámetros
4. Reporta path de salida, hash sha256 y tamaño del zip
5. Sugiere paso siguiente (cargar zip en otro agente para test, o aguardar `kata-package-skill` en el PR 3)

## Prompt Template

```
Contexto:
- slug: {{slug}}
- clean: {{clean}} (opcional, default false)
- skip_zip: {{skip_zip}} (opcional, default false)

Tarea:
Invoque kata-build-skill con los parámetros de arriba. El kata:
1. Resuelve paths y config
2. Phase 1 — Validate (frontmatter, skill.config, manifests)
3. Phase 2 — Build widgets (Vite production)
4. Phase 3 — Freeze scripts (lock preservado, sin instalación)
5. Phase 4 — Resolve tools (handler refs validadas)
6. Phase 5 — Rewrite bindings (called_via dev → called_via_prod)
7. Phase 6 — Emit (.build/ + .skill-manifest.json + zip)
8. Validar idempotencia

Aborte en el primer fallo de cualquier phase.

Formato de salida:
Path de .build/, hash sha256 del zip, tamaño. En caso de error,
mensaje específico indicando phase y regla violada.
```

## Ejemplo de Invocación

```
/cry-skill-build hello-skill
```

**Salida esperada:**

```
✅ Build de hello-skill concluido.
   Salida: .build/hello-skill/
   Zip:   .build/hello-skill.zip   (124 KB)
   sha256: 7a8c…

Próximos pasos:
- Cargar el zip en otro agente Claude Code para test manual
- kata-package-skill (PR 3) entrega .dist/hello-skill.skill auditable
```

## Restricciones

- El Cry **no modifica** `skills/{slug}/` (solo lectura)
- El Cry **no toca** `.dist/`
- Mensajes al usuario en `language.default`; identificadores técnicos preservados
- `lex-terminal-type`: los comandos shell respetan el terminal definido

## Diferencia con Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Atajo 1:1 | Pipeline en 9 pasos (6 phases + validación + report) |
| **Validación** | Forma de los parámetros | Frontmatter, manifests, refs, idempotencia |
| **Efecto** | Invoca el kata | Escribe `.build/{slug}/` + zip + manifest |

## Referencias

- `kata-build-skill` — procedimiento invocado
- `codex-skill-build-pipeline` — contrato del pipeline
- `codex-skill-tools-and-widgets` — schemas de los manifests
- `lex-skill-project-structure` — separación fuente/build/dist
- `cry-skill-dev` — paso anterior natural (validación manual)
- `kata-package-skill` (PR 3) — consumidor del `.build/` para `.dist/`
