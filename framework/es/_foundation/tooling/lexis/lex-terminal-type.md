# Lexis: Uso Obligatorio del Tipo de Terminal Definido

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Ejecución de comandos en shell por agentes IA

## Propósito

En proyectos que adoptan el Ahrena, los comandos de terminal pueden ejecutarse en **bash** (Linux, macOS, WSL) o **PowerShell** (Windows nativo). Los scripts, ejemplos de documentación e instrucciones generadas por agentes deben usar la sintaxis y el intérprete correctos para el entorno del proyecto; de lo contrario, los comandos fallan o generan confusión.

Esta Lexis existe para garantizar que **todo agente use el tipo de terminal (bash o PowerShell) definido por el proyecto o por las directivas canónicas** al proponer, generar o describir comandos de shell.

## Ley

> **Todo agente DEBE usar el tipo de terminal (bash o PowerShell) definido en `.ahrena/.directives` al ejecutar o proponer comandos de shell. Si la directiva no existe, el agente DEBE inferir el tipo a partir del sistema operativo del usuario (por ejemplo, Windows → PowerShell; Linux/macOS → bash) o preguntar al usuario.**

## Reglas

### 1. Consulta a la directiva canónica

Al ejecutar o sugerir comandos de terminal, el agente **DEBE**:

1. Consultar `.ahrena/.directives` (conforme a `lex-directives`).
2. Verificar si existe la sección `terminal` con el valor `bash` o `powershell`.
3. Usar ese valor como fuente de verdad para la sintaxis y el intérprete de los comandos.

### 2. Comportamiento cuando la sección no existe

Si la sección `terminal` no está presente en `.ahrena/.directives`:

- El agente **DEBE** inferir a partir del contexto cuando sea posible (por ejemplo, información de que el entorno es Windows → PowerShell; Linux o macOS → bash).
- Si el contexto no es claro, el agente **DEBE** preguntar al usuario qué tipo de terminal usar antes de ejecutar o generar comandos que dependan del shell.

### 3. Consistencia en la sesión

Una vez definido el tipo de terminal (por directiva, inferencia o respuesta del usuario), el agente **DEBE** mantener ese tipo durante toda la sesión al proponer o ejecutar comandos, salvo instrucción explícita en contrario del usuario.

### 4. Documentación y ejemplos

En artefactos que contengan ejemplos de comandos (documentación, README, Katas, Cries), el agente **DEBE** generar los ejemplos en el tipo de terminal definido por el proyecto o indicar claramente qué shell se está usando (por ejemplo, con comentario o bloque identificado).

### 5. No modificación sin autorización

El agente **NO PUEDE** añadir o alterar la sección `terminal` en `.ahrena/.directives` sin solicitud explícita del usuario.

## Abrangência

- **Se aplica a:** todas las sesiones en que el agente ejecute o proponga comandos de shell (terminal) en el contexto del Ahrena.
- **Agentes vinculados:** todos los Warriors y agentes genéricos.
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Comandos fallidos:** el uso de sintaxis bash en entorno PowerShell (o viceversa) puede romper scripts e instrucciones.
2. **Inconsistencia:** documentación y ejemplos en un shell mientras el usuario usa otro generan retrabajo y confusión.
3. **Remediación:** el agente debe releer las directivas, identificar el tipo de terminal correcto y regenerar o corregir los comandos conforme a `codex-terminal-type`.

## Ejemplos

### Correcto

```
# .ahrena/.directives contiene:
terminal: powershell

# El agente propone comando en PowerShell:
Get-ChildItem -Path . -Filter "*.md" | Select-Object Name
```

```
# .ahrena/.directives contiene:
terminal: bash

# El agente propone comando en bash:
find . -name "*.md" -type f
```

### Incorrecto

```
# Usuario en Windows; .directives no define terminal.
# El agente asume bash y sugiere:
find . -name "*.md"

# ❌ En PowerShell nativo, find no existe como comando.
# El agente debería haber inferido PowerShell o preguntado al usuario.
```

## Validación Automatizada

- **Herramienta:** verificación por el propio agente antes de ejecutar o proponer comandos de shell.
- **Momento:** al iniciar la ejecución de un comando y al generar documentación con ejemplos de terminal.
- **Métrica:** el 100 % de los comandos de shell propuestos o ejecutados deben respetar el tipo de terminal definido o inferido.
