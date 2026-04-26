# Kata: Servidor Local de Documentación (MkDocs)

> **Prefijo:** `kata-` | **Tipo:** Habilidad Repetible | **Alcance:** Servidor local de documentación Markdown para el directorio `docs/` usando MkDocs

## Objetivo

Este Kata define el procedimiento para **iniciar un servidor local de documentación** que sirve todos los archivos `.md` en `docs/` (modelos de dominio, documentos de API, eventos) como un sitio navegable en `http://localhost:8000`, usando MkDocs. El servidor recarga automáticamente al detectar cambios en los archivos, lo que lo hace útil durante sesiones activas de diseño.

## Cuándo Usar

- Cuando un desarrollador o agente quiera navegar por la documentación generada localmente (tras ejecutar `cry-feature-design`, `cry-api-design` o `cry-event-storm`)
- Cuando se estén revisando o validando modelos de dominio, docs de API y docs de eventos como un sitio unificado antes de hacer commit
- Cuando sea invocado por un Warrior o directamente desde el CLI como utilidad de desarrollo

## Entradas

| Entrada | Requerida | Descripción |
|---------|:---------:|-------------|
| Raíz del proyecto | Sí | Directorio donde residen `.ahrena/.directives` y `mkdocs.yml` (directorio de trabajo actual por defecto) |
| Puerto | No | Puerto para el servidor. Por defecto: `8000` |

## Flujo de Trabajo

```
Progreso:
- [ ] 1. Leer directivas
- [ ] 2. Verificar instalación de MkDocs
- [ ] 3. Resolver docs_dir
- [ ] 4. Verificar o generar mkdocs.yml
- [ ] 5. Iniciar servidor
```

### Paso 1: Leer Directivas

1. Leer `.ahrena/.directives` para obtener:
   - `paths.domain` — documentos de modelo de dominio (ej.: `docs/domain`)
   - `paths.oas` — especificación y documentos de API (ej.: `docs/oas`)
   - `paths.events` — documentos de eventos (ej.: `docs/events`)
2. Derivar `docs_dir` como el directorio padre común de los tres paths (ej.: `docs/` cuando todos los paths son `docs/{sección}`)
3. Si los paths divergen y no existe padre común, usar `docs/` como predeterminado y avisar al usuario

### Paso 2: Verificar Instalación de MkDocs

1. Ejecutar `mkdocs --version`
2. Si MkDocs no se encuentra:
   - Ejecutar `pip install mkdocs mkdocs-material`
   - Si pip no está disponible, informar al usuario y detener con un mensaje claro: "Instale Python y pip primero, luego ejecute `pip install mkdocs mkdocs-material`"
3. Verificar si el tema Material está disponible: `python -c "import material"` (opcional; usado en el Paso 4)

### Paso 3: Resolver docs_dir

1. Confirmar que `docs_dir` es un directorio que existe en la raíz del proyecto
2. Si no existe, crearlo: `mkdir -p {docs_dir}`
3. Si `docs_dir` está vacío, crear un `index.md` mínimo:
   ```markdown
   # Guardia Platform Docs

   Documentación generada por el framework Ahrena.
   Navegue usando la barra lateral.
   ```

### Paso 4: Verificar o Generar mkdocs.yml

1. Verificar si `mkdocs.yml` existe en la raíz del proyecto
2. **Si existe:** usar tal cual — no sobrescribir; proceder al Paso 5
3. **Si no existe:** generar un `mkdocs.yml` mínimo:

```yaml
site_name: Guardia Platform Docs
docs_dir: {docs_dir}
theme:
  name: material   # usa 'mkdocs' si mkdocs-material no está instalado
```

   - Si el tema Material no está instalado (verificación del Paso 2 falló), usar `name: mkdocs`
   - Escribir el archivo en la raíz del proyecto como `mkdocs.yml`
   - Informar al usuario: "`mkdocs.yml` generado en la raíz del proyecto. Edítelo para personalizar navegación, tema o nombre del sitio."

### Paso 5: Iniciar Servidor

1. Ejecutar `mkdocs serve --dev-addr 127.0.0.1:{puerto}` (puerto por defecto: `8000`)
2. Informar al usuario:
   - URL: `http://127.0.0.1:8000` (o el puerto configurado)
   - Directorio de docs que se sirve: `{docs_dir}/`
   - Hot-reload: activo (los cambios en archivos `.md` actualizan automáticamente)
3. El servidor corre en primer plano; el usuario lo detiene con `Ctrl+C`

## Entregable

Un servidor MkDocs corriendo en `http://127.0.0.1:8000` sirviendo todos los archivos `.md` en `docs/` como un sitio navegable con recarga automática al detectar cambios.

## Observaciones

- MkDocs descubre automáticamente todos los archivos `.md` en `docs_dir` cuando no se define ninguna clave `nav` en `mkdocs.yml`. Para personalizar el orden de navegación, agregue una sección `nav:` manualmente.
- El tema Material (`mkdocs-material`) ofrece búsqueda, modo oscuro y navegación mejorada. Instale con `pip install mkdocs-material`.
- El servidor es solo para desarrollo local — no lo exponga públicamente sin autenticación.

## Referencias

- `lex-directives` — paths canónicos leídos en el Paso 1
- `kata-domain-model`, `kata-api-design-doc`, `kata-events-doc` — katas que producen los archivos `.md` servidos por este kata
