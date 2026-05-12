# Cry: Ciclo de Skill (implement / validate / package)

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para invocar `warrior-claudionor` y conducir el ciclo `implement → validate → package` de un proyecto de skill Anthropic Agent Skills

## Descripción

Atajo para el ciclo de skill después del scaffold inicial (`cry-new-skill`). Invoca `warrior-claudionor`, que orquesta uno de tres katas (o los tres en secuencia), con Hephaestus/Apollo delegados según el gap.

> **Cuándo preferir `cry-pov`:** si el objetivo es **PoV de agent** (probar valor al cliente vía stack Anthropic — Skills, Subagents, Plugins — con observabilidad nativa y value-proof), use `cry-pov` como entry point preferencial. `cry-pov --kind skill` dispara el ciclo POV completo (7 katas POV + `kata-skill-implement`) y produce `docs/{context}/agents-pov/` consumible por Mêtis vía `--from-pov`. `cry-skill` se mantiene como entry point cuando el objetivo es **empaquetar una skill como artefacto distribuible** aislado del ciclo POV.

## Invocación

```
/cry-skill --mode <implement|validate|package|all> --slug <name> [--dry-run]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `--mode` | Sí | Fase del ciclo a ejecutar: `implement` (autoría con delegación), `validate` (verificación determinística), `package` (build → dist + manifest), o `all` (encadena los tres) | `--mode all` |
| `--slug` | Sí | Nombre del proyecto (idéntico al nombre del directorio en `{paths.skills_root}/`) | `--slug scheduled-payments-skill` |
| `--dry-run` | No | Presenta el plan sin persistir cambios en `{paths.skills_build}/`, `{paths.skills_dist}/` ni en el proyecto | `--dry-run` |

Si `--dry-run` se pasa con `--mode package`, el paquete final no se escribe — solo el reporte de lo que se produciría.

## Lo Que Hace el Comando

1. Resuelve `paths.skills_root/skills_build/skills_dist` en `.ahrena/.directives`
2. Confirma que el proyecto existe en `{paths.skills_root}/{slug}/`
3. Invoca `warrior-claudionor` pasando `mode`, `slug` y `dry_run`
4. Claudionor despacha al/los kata(s):
   - `--mode implement` → `kata-skill-implement` (delega widgets a Hephaestus, tools/scripts Python a Apollo, redacta `SKILL.md`/`references/`)
   - `--mode validate` → `kata-skill-validate` (verifica `lex-skill-project-structure`)
   - `--mode package` → `kata-skill-validate` (precondición) + `kata-skill-package` (build → dist + manifest validado contra `lex-skill-package-structure`)
   - `--mode all` → encadena los tres; aborta al primer error
5. Reporta el resultado final (paths producidos, conteo de archivos, violaciones)

## Prompt Template

```
Contexto:
- mode: {{mode}}             # implement | validate | package | all
- slug: {{slug}}
- dry_run: {{dry_run}}        # default false

Tarea:
Invoque warrior-claudionor con los parámetros anteriores. El warrior:
1. Lee .ahrena/.directives (paths.skills_*) y verifica que skills/{slug}/
   existe
2. Despacha a el/los kata(s) según `mode`
3. En `package` y `all`, aborta si kata-skill-validate retorna `error`
4. En `implement`, delega vía Agent a warrior-hephaestus (widgets) y
   warrior-apollo (tools/scripts Python); redacta SKILL.md y
   references/ in-house
5. Reporta paths producidos, conteo de archivos y violaciones por
   severidad

Aborte si: el slug no existe en paths.skills_root, mode inválido o
.ahrena/.directives ausente.

Formato de salida:
Reporte estructurado por fase (implement / validate / package), con
delegaciones nombradas y estado final. En caso de error, identifica el
kata + la regla violada y el paso de remediación.
```

## Ejemplos de Invocación

```
# Ciclo completo: identifica gaps, implementa, valida y empaqueta
/cry-skill --mode all --slug scheduled-payments-skill

# Solo validación determinística (CI o pre-commit)
/cry-skill --mode validate --slug scheduled-payments-skill

# Solo empaquetado (tras desarrollo manual)
/cry-skill --mode package --slug scheduled-payments-skill

# Preview de lo que sería empaquetado, sin escribir bajo .dist/
/cry-skill --mode package --slug scheduled-payments-skill --dry-run

# Solo implementación (continuar donde se dejó)
/cry-skill --mode implement --slug scheduled-payments-skill
```

**Salida esperada (`--mode all` en éxito):**

```
🛠  warrior-claudionor — ciclo completo para 'scheduled-payments-skill'

Fase 1/3 — kata-skill-implement
  Delegaciones: Hephaestus (widgets), Apollo (tools + scripts)
  Archivos producidos: 4 widgets, 2 handlers, 1 test
  SKILL.md + references/ actualizados

Fase 2/3 — kata-skill-validate
  ✅ no violations

Fase 3/3 — kata-skill-package
  ✅ package: .dist/scheduled-payments-skill.skill (18 archivos)
```

## Restricciones

- El Cry **no modifica** `.ahrena/.directives` ni `framework/`
- El Cry **no actúa** sin un proyecto existente en `{paths.skills_root}/{slug}/`; para crear uno nuevo, use `cry-new-skill`
- El Cry **no crea** branch, worktree ni commit — la disciplina de versionado queda con el usuario (`lex-issue-first`, `lex-git-worktrees`, `lex-pr-quality`)
- Mensajes humanos en el idioma definido por `language.default`; los identificadores técnicos (slug, modes, paths) se preservan

## Diferencia con Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Atajo que recoge `--mode` + `--slug` y despacha | Procedimiento completo (validate/package/implement, individualmente) |
| **Validación** | Forma de los parámetros | Lógica de cada fase, con delegaciones |
| **Efecto** | Invoca `warrior-claudionor` | Lee/escribe filesystem, delega o ejecuta script |

## Referencias

- `warrior-claudionor` — Warrior invocado por este Cry
- `kata-skill-implement` — invocado en `--mode implement` o `all`
- `kata-skill-validate` — invocado en `--mode validate`, `package` y `all`
- `kata-skill-package` — invocado en `--mode package` y `all`
- `cry-new-skill` — antecesor (scaffold antes del ciclo)
- `lex-skill-project-structure`, `lex-skill-package-structure` — leyes verificadas
- `lex-directives` — lectura de `paths.skills_*`
