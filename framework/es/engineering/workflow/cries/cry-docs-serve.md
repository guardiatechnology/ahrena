# Cry: cry-docs-serve

> **Prefijo:** `cry-` | **Tipo:** Comando de Ejecución | **Alcance:** Servidor local MkDocs de documentación para cualquier directorio Markdown

## Descripción

Inicia un servidor local MkDocs para navegar archivos `.md` como un sitio navegable en `http://127.0.0.1:8000`. Acepta un `docs-path` opcional para servir cualquier directorio en lugar del derivado de `.directives` — útil en proyectos donde el directorio de documentación no es `docs/` (ej.: en el repositorio Ahrena, el propio directorio del framework es la documentación).

## Cuándo Usar

- Tras ejecutar `cry-feature-design`, `cry-api-design` o `cry-event-storm`, para revisar los documentos generados como un sitio unificado
- Cuando se quiera navegar por modelos de dominio, especificaciones de API y documentos de eventos localmente antes de hacer commit
- Cuando la documentación del proyecto está fuera de `docs/` (ej.: `framework/` en Ahrena)

## Sintaxis

```
/cry-docs-serve [docs-path] [port]
```

## Parámetros

| Parámetro | Requerido | Descripción |
|-----------|:---------:|-------------|
| `docs-path` | No | Ruta del directorio a servir (ej.: `framework/`, `docs/`). Si se omite, la ruta se deriva de `.directives` (`paths.domain`, `paths.oas`, `paths.events`). |
| `port` | No | Puerto para el servidor. Por defecto: `8000`. |

## Invoca

| Kata | Descripción |
|------|-------------|
| `kata-docs-serve` | Verifica la instalación de MkDocs, resuelve `docs_dir`, genera `mkdocs.yml` si está ausente e inicia el servidor |

## Ejemplos

```
/cry-docs-serve
```
Deriva el directorio de documentación de `.directives` y lo sirve en `http://127.0.0.1:8000`.

---

```
/cry-docs-serve framework/
```
Sirve el directorio `framework/` en `http://127.0.0.1:8000`. Usar este comando en el repositorio Ahrena, donde el propio framework es la documentación.

---

```
/cry-docs-serve docs/
```
Sirve explícitamente `docs/` en `http://127.0.0.1:8000`.

---

```
/cry-docs-serve framework/ 8080
```
Sirve `framework/` en `http://127.0.0.1:8080`.

## Entregable

Un servidor MkDocs en ejecución accesible en `http://127.0.0.1:{port}` sirviendo todos los archivos `.md` del directorio especificado o derivado, con hot-reload al detectar cambios en los archivos.

## Observaciones

- El servidor corre en primer plano; deténgalo con `Ctrl+C`.
- Cuando se omite `docs-path`, se utiliza el directorio padre común de `paths.domain`, `paths.oas` y `paths.events` en `.directives`.
- Si `mkdocs.yml` no existe en la raíz del proyecto, se genera uno mínimo automáticamente (nunca sobrescribe uno existente).
- El tema Material (`mkdocs-material`) se utiliza cuando está disponible; en caso contrario, se aplica el tema predeterminado de MkDocs.

## Referencias

- `kata-docs-serve` — procedimiento al que este cry delega
- `lex-directives` — paths canónicos leídos cuando se omite `docs-path`
