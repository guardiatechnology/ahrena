# Kata: Resolver Versión del Framework Ahrena

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Resolución bajo demanda de la versión instalada del framework Ahrena

## Objetivo

Resolver la versión del framework Ahrena actualmente en uso en una cadena SemVer determinista y de una sola línea. La cadena de resolución hace fallback desde un manifiesto canónico escrito en la instalación (`.ahrena/.version` en el proyecto consumidor) hacia una lectura mediante `git describe` en el propio repositorio del framework, de modo que el kata funcione tanto en **modo consumidor** (el caso típico tras `make install`) como en **modo dev** (un agente o persona ejecutando directamente desde un clon del repositorio del framework).

## Cuándo Usar

- Cuando una persona invoca `/cry-ahrena-version` y pregunta "¿qué versión de Ahrena está aquí?"
- Cuando un warrior necesita registrar la versión del framework en un artefacto de auditoría (cuerpo de PR, issue, nota de release)
- En troubleshooting de compatibilidad cuando la versión del framework no es visible desde el working tree

## Inputs

| Input | Requerido | Descripción |
|-------|:---------:|-------------|
| directorio de trabajo | Sí | Implícito — la cadena de resolución lee archivos relativos al directorio actual |

El kata no recibe parámetros; el directorio de trabajo es la única entrada.

## Workflow

```
Progreso:
- [ ] 1. Leer .ahrena/.version (modo consumidor)
- [ ] 2. Hacer fallback a git describe (modo dev)
- [ ] 3. Formatear y emitir la cadena de versión
- [ ] 4. Validación final
```

### Paso 1: Leer `.ahrena/.version`

1. Buscar `.ahrena/.version` relativo al directorio de trabajo actual
2. Si el archivo existe: leer el contenido, eliminar espacios y el newline final, usar el resultado como cadena de versión
3. Si el archivo está vacío tras el strip, tratarlo como ausente y continuar al Paso 2
4. Si el archivo existe y contiene una cadena no vacía: saltar directo al Paso 3

### Paso 2: Fallback a `git describe`

1. Solo se alcanza cuando `.ahrena/.version` está ausente o vacío
2. Ejecutar `git describe --tags --abbrev=0` para leer el tag más reciente
3. Si se devuelve un tag: eliminar la `v` inicial cuando esté presente y usar el resultado como cadena de versión. Este es el camino de **modo dev** — ejecución del kata dentro del repositorio del framework antes de cualquier install
4. Refinamiento opcional: `git describe --tags` (sin `--abbrev=0`) devuelve una cadena más rica como `0.13.1-3-gabc1234` cuando HEAD ha avanzado más allá del último tag. Ambas formas son aceptables; el fallback canónico es `--abbrev=0` por estabilidad, con la forma extendida disponible cuando quien invoca quiere conocer la distancia exacta hasta el tag
5. Si `git` no está disponible, el directorio no es un repositorio git o no existen tags: continuar al Paso 4 con error explícito

### Paso 3: Formatear y emitir

1. La salida es una única línea que contiene solo la cadena SemVer (sin prefijo `v`, sin comillas, sin metadatos)
2. En modo dev la cadena PUEDE contener un sufijo `-N-gSHORT` por la semántica de `git describe` — eso es correcto (indica build de desarrollo N commits más allá del último tag); el kata no elimina el sufijo
3. Imprimir la cadena y retornar

### Paso 4: Validación final

Antes de entregar la salida, verificar:

- [ ] La salida es una única línea no vacía
- [ ] La salida no empieza con `v` (el prefijo se elimina)
- [ ] Cuando ni `.ahrena/.version` ni `git describe` lograron resolver un valor: el kata DEBE emitir un mensaje de error estructurado — `framework version unknown; run \`make update\` in this project, or create a SemVer tag in the framework repo` — y salir con un código distinto de cero

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| cadena de versión | Texto plano de una línea (ej. `0.13.1` o `0.13.1-3-gabc1234`) | stdout |
| mensaje de error | Texto plano de una línea en stderr | stderr (exit no cero) |

## Ejemplo de Ejecución

### Modo consumidor (típico)

```
$ cat .ahrena/.version
0.13.1

$ <kata-ahrena-version>
0.13.1
```

### Modo dev (repositorio del framework, HEAD sobre el tag)

```
$ git describe --tags --abbrev=0
v0.13.1

$ <kata-ahrena-version>
0.13.1
```

### Modo dev (repositorio del framework, HEAD más allá del último tag)

```
$ git describe --tags
v0.13.1-3-gabc1234

$ <kata-ahrena-version>
0.13.1-3-gabc1234
```

### Install desde branch (el consumidor ejecutó `make install VERSION=main`)

```
$ cat .ahrena/.version
main

$ <kata-ahrena-version>
main
```

La salida es el literal `main` (o el nombre literal de la branch) — el archivo es la fuente de verdad y el kata no remodela valores que no son SemVer.

### Camino de falla (sin `.ahrena/.version`, sin tags git)

```
$ <kata-ahrena-version>
framework version unknown; run `make update` in this project, or create a SemVer tag in the framework repo
$ echo $?
1
```

## Restricciones

- El kata NO DEBE consultar la red. Las dos fuentes de verdad son locales (`.ahrena/.version` y `git describe`); consultar GitHub Releases está prohibido
- El kata NO DEBE remodelar el valor leído desde `.ahrena/.version`. Si el archivo contiene `main` o el nombre de una branch, ese valor exacto se emite; sintetizar `0.0.0-main+<sha>` o cualquier otro SemVer sustituto está PROHIBIDO
- El kata NO DEBE imprimir contexto adicional (banner, etiqueta de versión, decoración) — la salida es la cadena desnuda de versión, pensada para el consumo por otros comandos y warriors

## Referencias

- `cry-ahrena-version` — comando de entrada que invoca este kata
- `lex-semantic-version` — reglas de SemVer respetadas por el manifiesto
