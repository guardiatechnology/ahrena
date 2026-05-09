# Lexis: Consulta Obligatoria al .directives

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Todas las sesiones y actividades de agentes IA

## Propósito

El Ahrena centraliza sus configuraciones canónicas en un único archivo declarativo: `.ahrena/.directives`. Ese archivo reside en el directorio `.ahrena/` — el punto de entrada canónico del framework en cualquier proyecto — y contiene instrucciones transversales como idioma predeterminado, idiomas obligatorios, convenciones de nomenclatura, rutas canónicas y otras directivas que gobiernan el comportamiento de todo el framework.

Sin la consulta obligatoria a ese archivo, los agentes pueden tomar decisiones divergentes sobre idioma, casing, prefijos y direccionamiento, generando inconsistencia entre artefactos y sesiones.

Esta Lexis existe para garantizar que **todo agente consulte y respete las directivas canónicas** definidas en `.ahrena/.directives` antes de producir cualquier salida o artefacto.

## Ley

> **Todo agente DEBE leer y aplicar las instrucciones definidas en `.ahrena/.directives` antes de iniciar cualquier actividad que produzca artefactos, documentación o comunicación en el contexto del Ahrena.**

## Reglas

### 1. Ubicación canónica

El archivo de directivas **SIEMPRE** reside en:

```
.ahrena/.directives
```

El directorio `.ahrena/` es el punto de entrada canónico del framework en cualquier proyecto que adopta el Ahrena. El agente **DEBE** buscar ese directorio en la raíz del repositorio.

### 2. Lectura obligatoria al iniciar

Al iniciar una sesión o actividad, el agente **DEBE**:

1. Localizar el directorio `.ahrena/` en la raíz del repositorio.
2. Leer el archivo `.ahrena/.directives` íntegramente.
3. Internalizar las directivas como restricciones activas para toda la sesión.

Si el directorio `.ahrena/` o el archivo `.directives` no existe, el agente **DEBE** alertar al usuario sobre la ausencia y sugerir su creación.

### 3. Directivas como fuente de verdad

Las directivas definidas en `.ahrena/.directives` tienen **precedencia** sobre:

- Suposiciones del agente basadas en entrenamiento o contexto genérico.
- Preferencias implícitas no documentadas.

Cuando haya conflicto entre una directiva y una instrucción del usuario en la sesión, el agente **DEBE** seguir la instrucción del usuario, pero **alertar** sobre la divergencia respecto a la directiva canónica.

### 4. Aplicación por sección

El agente **DEBE** aplicar cada sección de la directiva al comportamiento correspondiente:

| Sección | Aplicación |
|---------|------------|
| `paths` | Usar las rutas canónicas al referenciar o crear artefactos del framework |
| `language` | Producir documentación y artefactos en el idioma predeterminado (`default`) y garantizar que los idiomas obligatorios (`required`) sean contemplados cuando aplique |
| `naming.prefixes` | Aplicar el prefijo correcto al nombrar artefactos de cada Pilar |
| `naming.extensions` | Usar la extensión correcta según el contexto (`.md` para framework, `.mdc` para Cursor) |
| `naming.casing` | Seguir la convención de casing definida para archivos y directorios |
| `naming.addressing` | Seguir el patrón de direccionamiento al posicionar artefactos en la taxonomía |
| `naming.reserved_clades` | Reconocer los Clades especiales y respetar sus reglas de uso |
| `terminal` | Consultar para comandos de shell; usar el tipo definido (bash o PowerShell). Ver `lex-terminal-type`. |
| `naming.tone_and_writing_style` | Aplicar el tono y el estilo al producir artefactos y comunicación. Ver `lex-tone`. |
| `stacked_prs.tool` | Seleccionar la herramienta para operar Stacked Pull Requests cuando aplique: `vanilla` (default — `git` + `gh` puros) o `gs` (git-spice). Ver `codex-stacked-prs`. |
| `paths.skills_root` | Directorio raíz de los proyectos de skill externos (default `skills`). Ver `lex-skill-project-structure`. |
| `paths.skills_build` | Directorio de intermediarios del build de skills (default `.build`, gitignored). Escrito por el stack de build del proyecto consumidor. |
| `paths.skills_dist` | Directorio de entrega final de skills empaquetados (default `.dist`, committed). Validado por `lex-skill-package-structure`. |
| `pr_cost_tracking.enabled` | Cuando es `true`, activar el stamp de costo de tokens (Claude Code) en el body de los PRs vía `kata-pr-cost-stamp`. Default `false`. Ver `codex-pr-cost-tracking`. |
| `pr_cost_tracking.currency` | Moneda exhibida en el bloque. Default `USD`. |
| `pr_cost_tracking.include_cache_breakdown` | Mostrar cache reads/writes por separado en el bloque. Default `true`. |
| `pr_cost_tracking.window_override_days` | (Opcional) Override de la ventana `[branch_creation_date, now]` en días. |

Manuales complementarios para interpretación de las secciones: `codex-directives` (visión general del archivo), `codex-paths` (rutas canónicas), `codex-naming` (convenciones de nomenclatura).

### 5. Extensibilidad

Nuevas secciones pueden añadirse al `.directives` en cualquier momento. El agente **DEBE** interpretar secciones desconocidas con base en el nombre y la estructura de la clave, aplicando la directiva de forma razonable. En caso de ambigüedad, el agente **DEBE** preguntar al usuario.

### 6. No modificación sin autorización

El agente **NO PUEDE** modificar el archivo `.directives` sin solicitud explícita del usuario. Las directivas son canónicas y están gobernadas por el mantenedor del framework.

## Alcance

- **Se aplica a:** todas las sesiones de trabajo con agentes IA, en cualquier Clade y Subclade
- **Agentes vinculados:** todos los Warriors y agentes genéricos
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Inconsistencia de artefactos:** artefactos producidos sin consultar las directivas pueden tener idioma, nomenclatura o direccionamiento incorrectos.
2. **Retrabajo:** artefactos fuera de las directivas deben corregirse para conformidad antes de ser aceptados.
3. **Remediación:** el agente debe releer el `.ahrena/.directives`, identificar las divergencias y corregir los artefactos producidos.

## Ejemplos

### Correcto

```
Agente: [Inicio de sesión]
1. Localiza .ahrena/ en la raíz del repositorio
2. Lee .ahrena/.directives
3. Identifica:
   - Idioma predeterminado: pt-BR
   - Idiomas obligatorios: pt-BR, es, en
   - Casing: kebab-case
   - Prefijo para Lexis: lex-
4. Produce artefacto en pt-BR, nombra como lex-code-review.md,
   guarda en engineering/quality/lexis/

Usuario: Crea la documentación de esa feature.

Agente: Documentación creada en pt-BR (predeterminado).
¿Desea que genere también las versiones en español e inglés,
conforme a las directivas del framework?
```

### Incorrecto

```
Agente: [Inicio de sesión — ignora .ahrena/.directives]

Usuario: Crea una nueva Lexis sobre logging.

Agente: Here's your new Lexis:
# Lexis: Logging
...

# ❌ El agente no localizó .ahrena/ ni leyó el .directives.
# ❌ Ignoró el idioma predeterminado (pt-BR) definido en las directivas.
# ❌ No consultó paths.samples para localizar la plantilla correcta.
# ❌ No ofreció versiones en los idiomas obligatorios.
```

## Validación Automatizada

- **Herramienta:** verificación por el propio agente al inicio de cada sesión
- **Momento:** antes de cualquier producción de artefacto o comunicación formal
- **Métrica:** 100 % de las sesiones deben tener el `.ahrena/.directives` consultado y aplicado
