# Framework — Guía del Desarrollador

🇧🇷 [Português](README.md) | 🇺🇸 [English](README.en.md)

> Guía práctica para quienes contribuyen al repositorio del Ahrena. Para uso del framework en proyectos, consulte el [README principal](../README.md).

## Estructura

```
framework/
├── .directives.sample           # Plantilla de directivas (copiado a .ahrena/.directives en la instalación)
├── templates/                   # Plantillas base de cada Pilar
│   ├── lex-sample.md
│   ├── codex-sample.md
│   ├── kata-sample.md
│   ├── warrior-sample.md
│   └── cry-sample.md
│
├── pt-BR/                       # Idioma predeterminado (fuente de verdad)
│   ├── _foundation/
│   │   ├── authoring/           # Guías de creación de artefatos
│   │   ├── contributing/        # Flujo de contribución y commit
│   │   ├── process/             # Convenciones de proceso (checkpoints, directivas)
│   │   ├── quality/             # Estándares mínimos de calidad
│   │   ├── tooling/             # Automatización (Makefile)
│   │   └── i18n/                # Estructura de idiomas del framework
│   └── documentation/
│       └── i18n/                # Sistema de traducción (Hermes)
│
├── en/                          # Inglés (misma estructura)
└── es/                          # Español (misma estructura)
```

El idioma predeterminado (`pt-BR`) es la **fuente de verdad**. Los cambios comienzan en él y se traducen a los demás idiomas mediante `/cry-translate`.

## Flujo de Desarrollo

### 1. Editar artefatos en `framework/`

Edite los archivos `.md` dentro de `framework/{lang}/`. Respete:

- **Direccionamiento:** `{lang}/{clade}/{subclade}/{pilar}/{prefixo}-{nome}.md`
- **Plantillas:** use las plantillas de `framework/templates/` como base (`lex-template-usage`)
- **i18n:** toda modificación en el idioma predeterminado debe propagarse a los demás idiomas

### 2. Probar localmente

Tras editar, regenere la instalación local para validar que los artefatos Cursor se generen correctamente:

```bash
make dev-install PLATFORM=cursor
```

Esto copia `framework/` a `.ahrena/framework/`, genera el `.cursor/` (rules, skills, commands, agents) y preserva el `.directives` existente.

### 3. Verificar artefatos generados

El instalador transforma cada Pilar al formato nativo de Cursor:

| Pilar | Origen | Destino Cursor |
|-------|--------|----------------|
| Lexis | `framework/{lang}/.../lexis/lex-*.md` | `.cursor/rules/.../lex-*.mdc` |
| Codex | `framework/{lang}/.../codex/codex-*.md` | `.cursor/rules/.../codex-*.mdc` |
| Katas | `framework/{lang}/.../katas/kata-*.md` | `.cursor/skills/kata-*/SKILL.md` |
| Warriors | `framework/{lang}/.../warriors/warrior-*.md` | `.cursor/skills/warrior-*/SKILL.md` + `.cursor/agents/warrior-*.md` |
| Cries | `framework/{lang}/.../cries/cry-*.md` | `.cursor/commands/.../cry-*.md` |

El idioma usado para generar los artefatos Cursor se define por `language.cursor` en `.directives` (predeterminado: `en`).

### 4. Commitar

Use `/cry-commit` para crear commits conformes. Las 4 Lexis de commit son:

- `lex-conventional-commits` — formato `type(scope): description`
- `lex-small-commits` — un propósito por commit
- `lex-commit-language` — subject en inglés
- `lex-signed-commits` — firma GPG obligatoria

### 5. Versionar release (tags)

Use `/cry-tag` para crear o listar tags de release en formato SemVer. El `kata-tag` aplica `lex-semantic-version` y `lex-signed-commits`. Ver `_foundation/contributing/README.md` para el inventario completo de artefactos.

### 6. Contribuir

Use `/cry-contribute pr` para abrir el Pull Request. El `kata-contribute` guía todo el flujo vía MCP.

## Creando Nuevos Artefatos

### Mediante comandos (recomendado)

```
/cry-new-lex          # Nueva Lexis
/cry-new-codex        # Nuevo Codex
/cry-new-kata         # Nuevo Kata
/cry-new-warrior      # Nuevo Warrior
/cry-new-cry          # Nuevo Cry
```

Cada comando invoca el kata correspondiente (`kata-create-*`) que:
1. Usa la plantilla oficial como base
2. Posiciona el artefato en la taxonomía correcta
3. Crea en los 3 idiomas obligatorios

### Manualmente

1. Copiar la plantilla de `framework/templates/{pilar}-sample.md`
2. Posicionar en `framework/pt-BR/{clade}/{subclade}/{pilar}/{prefixo}-{nome}.md`
3. Completar las secciones obligatorias
4. Traducir a `en/` y `es/` (mediante `/cry-translate`)
5. Ejecutar `make dev-install PLATFORM=cursor` para validar

## Convenciones

| Aspecto | Estándar |
|---------|----------|
| Casing de archivos | `kebab-case` (`lex-no-secrets.md`) |
| Casing de directorios | `kebab-case` (`engineering/backend/`) |
| Extensión en el framework | `.md` |
| Extensión en Cursor | `.mdc` (rules), `.md` (skills, commands, agents) |
| Prefijos | `lex-`, `codex-`, `kata-`, `warrior-`, `cry-` |
| Clades reservados | `_foundation` (prefijo `_`) |

## Targets del Makefile

| Target | Descripción |
|--------|-------------|
| `make dev-install PLATFORM=cursor` | Instala usando fuentes locales |
| `make bootstrap PLATFORM=cursor` | Primera instalación (descarga de GitHub) |
| `make install PLATFORM=cursor` | Reinstala a partir de `.ahrena/install.py` |
| `make update` | Actualiza a la última versión |
| `make clean` | Elimina archivos instalados |

## Referencias

- [README principal](../README.md) — Documentación pública del Ahrena
- [Sistema de Traducción](pt-BR/documentation/i18n/README.md) — Documentación del Hermes
- `.ahrena/.directives` — Directivas canónicas del framework
- `_foundation/contributing/codex/codex-contributing` — Flujo de contribución
- `_foundation/contributing/katas/kata-contribute` — Procedimiento de PR
