# Cry: Traducir Documento

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Traducción de documentación técnica

## Descripción

Comando rápido para traducir un documento a uno o más idiomas. Invoca el `warrior-translator` (Hermes) que ejecuta el `kata-translate`, consultando las reglas y guías específicas de cada idioma destino.

## Uso

```
/cry-translate <archivo> [idioma] [--order]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `archivo` | Sí | Ruta del documento a traducir | `framework/pt-BR/_foundation/process/lexis/lex-directives.md` |
| `idioma` | No | Código(s) BCP 47 del idioma destino. Si se omite, traduce a todos los idiomas de `language.i18n` excepto el de origen | `es`, `en`, `es,en` |
| `--order` | No | Especifica el orden de traducción. Si se omite, sigue el orden de `language.i18n` | `--order en,es` |

## Orden de Traducción

Cuando múltiples idiomas son destino, el Cry define el **orden de ejecución**:

1. **Predeterminado:** sigue el orden definido en `language.i18n` en `.ahrena/.directives`, excluyendo el idioma de origen
2. **Personalizado:** cuando `--order` es especificado, sigue el orden informado
3. **Secuencial:** cada idioma es traducido completamente antes de pasar al siguiente

## Lo que el Comando Hace

1. Lee `.ahrena/.directives` para obtener idiomas y orden
2. Identifica el idioma de origen a partir de la ruta o contenido
3. Determina el/los idioma(s) destino y el orden de ejecución
4. Invoca el `warrior-translator` con el `kata-translate`
5. Para cada idioma en el orden, el Warrior (vía kata-translate) consulta `lex-language-{lang}` y `codex-language-{lang}`, traduce el documento y guarda en la ruta correcta
6. Reporta los archivos creados

## Prompt Template

```
Contexto:
- Archivo fuente: {{archivo}}
- Idioma(s) destino: {{idioma}} (o todos de language.i18n excepto el de origen)
- Orden: {{order}} (o conforme language.i18n)

Tarea:
Asuma el papel del warrior-translator (Hermes). Lea .ahrena/.directives para obtener los idiomas obligatorios. Para cada idioma destino en el orden definido, ejecute el **kata-translate** (el Kata consulta las Lexis y Codex de idioma conforme su documentación). Lea el archivo fuente, ejecute el Kata y guarde la traducción en la ruta correcta.

Formato de salida:
Lista de archivos creados con confirmación de validación por idioma.
```

## Ejemplo de Invocación

**Traducir a todos los idiomas:**

```
/cry-translate framework/pt-BR/_foundation/process/lexis/lex-directives.md
```

**Traducir a idioma específico:**

```
/cry-translate docs/architecture.md en
```

## Restricciones

- No modifica el archivo fuente — solo genera traducciones
- Sigue las reglas de `lex-language` y `lex-language-{lang}`
- Términos canónicos de Ahrena no se traducen
- El orden de traducción respeta `language.i18n` o `--order`

## Diferencia con Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Invocación rápida (comando) | Procedimiento completo (6 pasos) |
| **Complejidad** | Baja (comando + parámetros) | Alta (workflow detallado) |
| **Orden de traducción** | Define el orden | No define orden |

## Referencias

- `warrior-translator` — Agente invocado por este Cry
- `kata-translate` — Procedimiento ejecutado por el Warrior (el Kata consulta las Lexis y Codex de idioma; ver documentación del Kata)
