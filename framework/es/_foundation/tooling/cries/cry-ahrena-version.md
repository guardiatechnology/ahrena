# Cry: Mostrar Versión del Framework Ahrena

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Consulta bajo demanda de la versión instalada del framework Ahrena

## Descripción

Atajo que imprime la versión del framework Ahrena actualmente en uso. El Cry no recibe parámetros y delega la resolución a `kata-ahrena-version`, que lee primero `.ahrena/.version` (manifiesto canónico escrito en la instalación) y hace fallback a `git describe` cuando el working tree es el propio repositorio del framework.

## Uso

```
/cry-ahrena-version
```

## Parámetros

Ninguno. El Cry no acepta argumentos.

## Qué Hace el Comando

1. Invoca `kata-ahrena-version` contra el directorio de trabajo actual
2. Imprime la cadena de versión resuelta en una única línea
3. En caso de fallo (sin `.ahrena/.version` y sin tag git legible), imprime el mensaje de error estructurado del kata y sale con un código distinto de cero

## Plantilla de Prompt

```
Contexto:
- Directorio de trabajo: actual

Tarea:
Ejecutar kata-ahrena-version. Emitir solo la cadena de versión de una línea que
el kata devuelve. No agregar prefijos, sufijos, decoraciones ni explicaciones.
Si el kata falla, emitir el mensaje de error del kata literalmente.

Formato de salida:
Texto plano de una línea (ej. `0.13.1`, `0.13.1-3-gabc1234`, `main`) en stdout,
o el mensaje de error estructurado del kata en stderr.
```

## Ejemplo de Invocación

**Proyecto consumidor tras el install:**

```
$ /cry-ahrena-version
0.13.1
```

**Repositorio del framework antes del install (modo dev, HEAD más allá del último tag):**

```
$ /cry-ahrena-version
0.13.1-3-gabc1234
```

**Proyecto instalado desde una branch:**

```
$ /cry-ahrena-version
main
```

## Restricciones

- El Cry NO DEBE agregar ninguna salida más allá de lo que el kata devuelve — sin banner, sin etiqueta de versión, sin metadatos
- El Cry NO DEBE consultar la red. El kata invocado es local por diseño
- El Cry NO DEBE modificar ningún archivo. Es una consulta de solo lectura

## Diferencia con el Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Punto de entrada; cero parámetros | Procedimiento de resolución con cadena de fallback explícita |
| **Salida** | Pass-through de la cadena de una línea del kata | Cadena SemVer de una línea (o error estructurado) |
| **Efectos colaterales** | Ninguno | Ninguno |

## Referencias

- `kata-ahrena-version` — procedimiento invocado por este Cry
