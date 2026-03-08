# Ahrena: AI-First Capability Framework

**Ahrena** es un Capability Framework AI-first que estructura conocimiento, procesos y comportamiento de agentes de IA a través de una **taxonomía unificada** aplicable a cualquier disciplina de negocio.

Leyes inquebrantables (Lexis), bases de conocimiento (Codex), procedimientos repetibles (Katas), agentes especializados (Warriors) y comandos recurrentes (Cries) se organizan por disciplina (Clade) y área de conocimiento (Subclade), creando un sistema extensible que orienta cómo humanos e IA colaboran en cualquier dominio.

### Principios

1. **IA como Copiloto, no Piloto:** Los humanos mantienen el control final sobre las decisiones críticas
2. **Proceso sobre Herramienta:** La estandarización de procesos tiene prioridad sobre la estandarización de herramientas
3. **Artefactos como Código:** Leyes, manuales, procedimientos y comandos son versionados, auditables y portables
4. **Agnóstico de Plataforma:** `framework/` es la fuente de verdad; `.cursor/` y otros IDEs son derivaciones

---

## Instalación

### Prerrequisitos

- **Python 3.8+** — necesario para ejecutar el instalador
- **Make** (opcional) — para bootstrap y actualizaciones vía Makefile
  - **Windows:** `choco install make` o `winget install GnuWin32.Make`
  - **macOS:** incluido con Xcode Command Line Tools (`xcode-select --install`)
  - **Linux:** incluido en la mayoría de las distribuciones (`sudo apt install make`)

### Primera instalación

El instalador descarga el framework de GitHub y configura el proyecto. No es necesario clonar el repositorio.

#### Vía Makefile (recomendado)

Descargue el `Makefile` en la raíz del proyecto y use `make bootstrap`. El Makefile puede ser commitado en el repositorio para que todo el equipo use el mismo flujo.

**macOS / Linux:**

```bash
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/Makefile -o Makefile
make bootstrap PLATFORM=cursor
```

**Windows (PowerShell):**

```powershell
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/Makefile -OutFile Makefile
make bootstrap PLATFORM=cursor
```

**Con opciones:**

```bash
make bootstrap PLATFORM=cursor VERSION=v0.1.0 LANGUAGE=en
make bootstrap PLATFORM=cursor CLADES=_foundation,documentation
make bootstrap  # solo framework, sin plataforma
```

#### Vía one-liner (sin Make)

**macOS / Linux:**

```bash
# Solo framework (.ahrena/)
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 -

# Framework + Cursor IDE
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 - --platform cursor

# Versión específica + idioma predeterminado
curl -sSL https://github.com/guardiafinance/ahrena/releases/download/v0.1.0/install.py | python3 - --version v0.1.0 --language en --platform cursor

# Solo clades específicos
curl -sSL https://github.com/guardiafinance/ahrena/releases/latest/download/install.py | python3 - --clades _foundation,documentation --platform cursor
```

**Windows (PowerShell):**

```powershell
# Solo framework (.ahrena/)
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py; Remove-Item install.py

# Framework + Cursor IDE
Invoke-WebRequest https://github.com/guardiafinance/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform cursor; Remove-Item install.py
```

### Actualización

El update detecta automáticamente la plataforma instalada y preserva el `.directives`:

**Vía Makefile (raíz del proyecto):**

```bash
make update
make update VERSION=v0.2.0
```

**Vía Makefile (.ahrena/):**

```bash
make -f .ahrena/Makefile update
```

**Vía script directo:**

```bash
# macOS / Linux
python3 .ahrena/update.py
python3 .ahrena/update.py --version v0.2.0

# Windows (PowerShell)
python .ahrena/update.py
python .ahrena/update.py --version v0.2.0
```

### Desinstalación

Elimina todos los archivos instalados por Ahrena (`.ahrena/` y archivos generados en `.cursor/` — rules, skills, commands y agents). Solicita confirmación antes de eliminar.

**Vía Makefile:**

```bash
make uninstall
```

**Vía script directo:**

```bash
# macOS / Linux
python3 .ahrena/uninstall.py
python3 .ahrena/uninstall.py --force    # sin confirmación

# Windows (PowerShell)
python .ahrena/uninstall.py
python .ahrena/uninstall.py --force
```

### Desarrollo local (para contribuidores de Ahrena)

Para quienes trabajan en el repositorio de Ahrena y desean probar cambios en el framework localmente:

```bash
make dev-install PLATFORM=cursor
```

Esto usa las fuentes locales de `framework/` en lugar de descargar de GitHub. Los directorios `.ahrena/` y `.cursor/` se regeneran a partir del estado actual del repositorio.

### Opciones

| Flag | Descripción |
|------|-------------|
| `--platform cursor` | Generar `.cursor/` (rules, skills, commands, agents) |
| `--local` | Usar fuentes locales (para desarrollo del framework) |
| `--clades X,Y` | Instalar solo los clades especificados (ej: `_foundation,documentation`) |
| `--version v0.1.0` | Versión específica (tag o branch) |
| `--language en` | Sobrescribir el idioma predeterminado en `.directives` |
| `--directives PATH` | Usar `.directives` personalizado (ruta local o URL) |
| `--target PATH` | Instalar en otro directorio |
| `--dry-run` | Mostrar lo que se haría sin alterar nada |
| `--clean` | Eliminar archivos instalados por Ahrena |

> **Nota:** cuando se usa `--clades`, la selección se guarda en `.ahrena/.installed-clades` y es respetada automáticamente por `update.py`. Para cambiar los clades en una actualización, pase `--clades` nuevamente.

### Qué se instala

| Comando | `.ahrena/` | `.cursor/` |
|---------|------------|------------|
| Sin `--platform` | framework + directives + scripts + Makefile | — |
| `--platform cursor` | framework + directives + scripts + Makefile | rules, skills, commands, agents |

---

## Taxonomía

Ahrena organiza el conocimiento en **tres niveles**:

```
Clade (disciplina) → Subclade (área) → Pilar (tipo de capacidad) → Capability (capacidad)
```

### Pilares

Los Pilares definen el **tipo** de cada capacidad. Son cinco:

#### Lexis — Leyes Inquebrantables

Restricciones absolutas de seguridad, calidad o proceso que **ningún agente (humano o IA) puede violar**.

| Aspecto | Detalle |
|---------|---------|
| **Naturaleza** | Restrictiva e imperativa — define lo que **nunca** puede ocurrir o lo que **siempre** debe ocurrir |
| **Prefijo** | `lex-` |
| **Cuándo usar** | Cuando existe riesgo de violación de seguridad, calidad o proceso crítico |
| **Gobernanza** | Sin excepciones; validación automatizada siempre que sea posible |
| **Plantilla** | [`framework/templates/lex-sample.md`](framework/templates/lex-sample.md) |

#### Codex — Manuales de Referencia

Base de conocimiento estructurada que la IA consulta para tomar decisiones contextualizadas.

| Aspecto | Detalle |
|---------|---------|
| **Naturaleza** | Informativa y orientadora — define **cómo** funciona el sistema |
| **Prefijo** | `codex-` |
| **Cuándo usar** | Cuando una decisión, estándar o convención relevante necesita ser documentada |
| **Gobernanza** | Actualizado con cada decisión relevante o cambio estructural; consultado por el equipo y la IA |
| **Plantilla** | [`framework/templates/codex-sample.md`](framework/templates/codex-sample.md) |

#### Katas — Skills Repetibles

Procedimientos que definen cómo los agentes ejecutan tareas recurrentes de forma estandarizada, con inputs, outputs y criterios de validación.

| Aspecto | Detalle |
|---------|---------|
| **Naturaleza** | Procedimental — define **qué hacer** paso a paso |
| **Prefijo** | `kata-` |
| **Cuándo usar** | Cuando una tarea recurrente necesita ser ejecutada de forma estandarizada |
| **Gobernanza** | Criterios de validación verificados antes de la entrega |
| **Plantilla** | [`framework/templates/kata-sample.md`](framework/templates/kata-sample.md) |

#### Warriors — Agentes Especializados

Agentes de IA con identidad, alcance y responsabilidades definidos. Cada Warrior consulta Lexis, Codex y Katas relevantes.

| Aspecto | Detalle |
|---------|---------|
| **Naturaleza** | Persona — define **quién** es el agente y cómo se comporta |
| **Prefijo** | `warrior-` |
| **Cuándo usar** | Cuando se necesita un agente especializado con identidad y alcance definidos |
| **Gobernanza** | Vincula Lexis, Codex y Katas; criterios claros de escalación a humano |
| **Plantilla** | [`framework/templates/warrior-sample.md`](framework/templates/warrior-sample.md) |

#### Cries — Comandos Recurrentes

Atajos de productividad que automatizan tareas repetitivas. Se diferencian de los Katas por ser invocaciones rápidas, no procedimientos completos.

| Aspecto | Detalle |
|---------|---------|
| **Naturaleza** | Invocación — define un **atajo** rápido y reutilizable |
| **Prefijo** | `cry-` |
| **Cuándo usar** | Cuando una tarea simple y repetitiva puede ser automatizada mediante un comando rápido |
| **Gobernanza** | Baja complejidad (1-2 pasos); invocado vía `/cry-[nombre]` en el chat |
| **Plantilla** | [`framework/templates/cry-sample.md`](framework/templates/cry-sample.md) |

---

### Clades y Subclades

**Clade** — Disciplina de negocio. Agrupa todo el conocimiento relevante a una misma disciplina.

**Subclade** — Área de conocimiento dentro de la disciplina. Refina el alcance del Clade por especialidad.

#### Product

Gestión de producto, ciclo de vida y estrategia. Abarca desde el descubrimiento de oportunidades hasta la entrega continua de valor al usuario.

| Subclade | Foco |
|----------|------|
| Discovery | Investigación, validación de hipótesis y priorización |
| Strategy | Visión de producto, roadmap y métricas de éxito |
| Analytics | Datos de uso, experimentación e insights |
| Delivery | Planificación de releases, rollout y comunicación |

#### Engineering

Desarrollo, arquitectura e infraestructura. Abarca todo el ciclo técnico (del código al deploy) incluyendo calidad y seguridad.

| Subclade | Foco |
|----------|------|
| Backend | APIs, servicios, lógica de negocio e integraciones |
| Frontend | Interfaces, componentes y experiencia del desarrollador |
| DevOps | CI/CD, infraestructura como código y observabilidad |
| Security | Protección de datos, autenticación y conformidad técnica |
| Quality | Pruebas, revisión de código y estándares de calidad |

#### Finance

Gestión financiera, contable y contraloría. Estructura procesos que exigen precisión, trazabilidad y conformidad con normas fiscales y contables.

| Subclade | Foco |
|----------|------|
| Accounting | Asientos, conciliación y cierre contable |
| Treasury | Flujo de caja, pagos, cobros y gestión de liquidez |
| Controllership | Planificación financiera, presupuesto, informes gerenciales y KPIs |

#### Operations

Procesos operativos y soporte. Garantiza que los sistemas y equipos funcionen de forma estable y eficiente en el día a día.

| Subclade | Foco |
|----------|------|
| Support | Atención, escalamiento y base de conocimiento |
| Infrastructure | Servidores, redes, capacidad y disaster recovery |
| Monitoring | Alertas, dashboards y respuesta a incidentes |

#### Documentation

Traducción, internacionalización y gestión de documentación técnica. Contiene artefactos genéricos que se aplican a cualquier tipo de documentación (del framework, de proyectos o de cualquier otro contenido técnico).

| Subclade | Foco |
|----------|------|
| i18n | Traducción multilingüe — reglas por idioma, procedimientos, agente traductor y comando |

> El Clade `documentation/i18n/` incluye al **Warrior Hermes** — un agente traductor especialista que consulta reglas y guías específicos de cada idioma objetivo (pt-BR, en, es) para garantizar traducciones precisas y consistentes. Para más detalles, consulte el [README del Sistema de Traducción](framework/pt-BR/documentation/i18n/README.md).

#### _Foundation — Clade Transversal

_Foundation es un **Clade especial** que no pertenece a una disciplina específica. Sus artefactos actúan de forma **transversal**, aplicándose a todos los demás Clades simultáneamente.

Mientras que Clades como Product o Engineering contienen conocimiento específico de sus disciplinas, _Foundation define las **reglas, procesos y estándares que atraviesan todas ellas** — seguridad global, calidad mínima y procesos comunes que todo agente y todo artefacto deben respetar, independientemente del dominio.

| Subclade | Foco |
|----------|------|
| Authoring | Guías de creación de artefactos (cómo crear Lexis, Codex, Katas, Warriors y Cries) |
| Contributing | Flujo unificado de contribución, estándares de commit y creación de PRs |
| Process | SDLC, flujos de trabajo y convenciones comunes a todas las disciplinas |
| Quality | Estándares mínimos de calidad válidos para cualquier artefacto |
| Security | Políticas de seguridad aplicables a todo el sistema |
| Tooling | Automatización y herramientas de desarrollo (Makefile, instalador) |
| i18n | Estructura de carpetas por idioma dentro de `framework/` — reglas de navegación y espejamiento |

> En la práctica: una Lexis en `_foundation/security/` se aplica a **todos** los Clades, no solo a Engineering. Al crear un artefacto en cualquier Clade, el agente debe consultar _Foundation primero para garantizar la conformidad con las reglas transversales.

---

> Los Clades y Subclades son **extensibles**: cada organización crea los que tengan sentido para su contexto.

### Warriors Disponibles

Los Warriors son agentes especializados listos para usar. Ahrena incluye los siguientes Warriors built-in:

| Warrior | Nombre | Clade | Descripción |
|---------|--------|-------|-------------|
| `warrior-translator` | **Hermes** | `documentation/i18n` | Traductor de documentación técnica. Consulta reglas y guías específicos por idioma objetivo (pt-BR, en, es) para garantizar traducciones precisas. Invocable vía `/cry-translate`. [Documentación completa](framework/pt-BR/documentation/i18n/README.md) |

#### Direccionamiento

El idioma es siempre el primer segmento de la ruta en el framework:

```
{lang}/{clade}/{subclade}/{pilar}/{prefijo}-{nombre}.md
```

| Ruta | Lectura |
|------|---------|
| `pt-BR/_foundation/security/lexis/lex-security.md` | Ley de seguridad transversal en pt-BR |
| `en/product/discovery/codex/codex-prioritization.md` | Manual sobre priorización en inglés |
| `es/engineering/security/lexis/lex-no-secrets.md` | Ley sobre secrets en español |
| `pt-BR/documentation/i18n/warriors/warrior-translator.md` | Agente Hermes (traductor) en pt-BR |
| `en/engineering/quality/warriors/warrior-spartacus.md` | Agente Spartacus en inglés |

#### Visualización

```
┌───────────────────────────────────────────────────────────────────┐
│                      TAXONOMÍA AHRENA                             │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Clade               Subclade              Pilar                  │
│  ─────               ────────              ─────                  │
│                                                                   │
│  product/ ──────┬── discovery/ ──────────┬── lexis/               │
│                 ├── strategy/            ├── codex/               │
│                 ├── analytics/           ├── katas/               │
│                 └── delivery/            ├── warriors/            │
│                                          └── cries/               │
│  engineering/ ──┬── backend/                                      │
│                 ├── frontend/                                     │
│                 ├── devops/                                       │
│                 ├── security/                                     │
│                 └── quality/                                      │
│                                                                   │
│  finance/ ──────┬── accounting/                                   │
│                 ├── compliance/                                   │
│                 └── reporting/                                    │
│                                                                   │
│  operations/ ───┬── support/                                      │
│                 ├── infrastructure/                               │
│                 └── monitoring/                                   │
│                                                                   │
│  documentation/ ──── i18n/           Hermes (traductor)           │
│                                                                   │
│  ═══════════════════════════════════════════════════════          │
│  _foundation/ ──┬── authoring/      ← se aplica a TODOS          │
│   (transversal) ├── contributing/     los Clades anteriores       │
│                 ├── process/                                      │
│                 ├── quality/                                      │
│                 ├── security/                                     │
│                 ├── tooling/                                      │
│                 └── i18n/                                         │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Estructura del Repositorio

### `.ahrena/`

Punto de entrada canónico del framework. Todo proyecto que adopta Ahrena **DEBE** tener este directorio en la raíz del repositorio. Contiene las directivas globales que gobiernan el comportamiento de todos los agentes.

```
.ahrena/
├── .directives          # Configuraciones canónicas (idioma, nomenclatura, paths)
```

### `framework/`

Plantillas y artefactos en `.md` puro, agnóstico de plataforma. El **idioma es el primer nivel de navegación** — cada carpeta de idioma contiene el árbol completo de Clades, Subclades y Pilares:

```
framework/
├── .directives.sample
│
├── templates/                          # Plantillas (modelos base de cada Pilar)
│   ├── lex-sample.md
│   ├── codex-sample.md
│   ├── kata-sample.md
│   ├── warrior-sample.md
│   └── cry-sample.md
│
├── pt-BR/                              # Idioma predeterminado (fuente de verdad)
│   │
│   │   # Artefactos por Clade → Subclade → Pilar
│   ├── _foundation/
│   │   ├── authoring/                 # Guías de creación de artefactos
│   │   │   ├── codex/codex-*.md
│   │   │   ├── katas/kata-create-*.md
│   │   │   └── cries/cry-new-*.md
│   │   ├── contributing/              # Flujo de contribución
│   │   │   ├── codex/codex-contributing.md, codex-commit-standards.md, codex-semantic-version.md
│   │   │   ├── lexis/lex-conventional-commits.md, lex-semantic-version.md, ...
│   │   │   ├── katas/kata-commit.md, kata-contribute.md, kata-tag.md
│   │   │   └── cries/cry-commit.md, cry-contribute.md, cry-tag.md
│   │   ├── process/lexis/lex-*.md
│   │   ├── quality/lexis/lex-*.md
│   │   ├── tooling/cries/cry-make.md
│   │   └── i18n/
│   │       ├── lexis/lex-framework-language.md
│   │       └── codex/codex-framework-language.md
│   │
│   └── documentation/i18n/             # Sistema de traducción
│       ├── README.md                   # Documentación completa
│       ├── lexis/
│       │   ├── lex-language.md         # Reglas transversales
│       │   ├── lex-language-ptbr.md    # Reglas para pt-BR
│       │   ├── lex-language-en.md      # Reglas para en
│       │   └── lex-language-es.md      # Reglas para es
│       ├── codex/
│       │   ├── codex-language.md       # Guía transversal
│       │   ├── codex-language-ptbr.md
│       │   ├── codex-language-en.md
│       │   └── codex-language-es.md
│       ├── katas/kata-translate.md     # Procedimiento (6 pasos)
│       ├── warriors/warrior-translator.md  # Hermes
│       └── cries/cry-translate.md      # Comando rápido
│
├── es/                                 # Español (misma estructura)
│   └── ...
└── en/                                 # Inglés (misma estructura)
    └── ...
```

Para crear un nuevo artefacto: copie la plantilla correspondiente de `framework/templates/` (ej: `lex-sample.md`), colóquela en el Clade/Subclade adecuado y complete los campos `[]`. El artefacto **DEBE** existir en todos los idiomas de `language.i18n` — use `/cry-translate` para generar las traducciones.

### De-Para: `framework/` → `.cursor/`

Al implementar en Cursor, cada Pilar se mapea al recurso nativo correspondiente. Cada recurso Cursor tiene su propio formato:

| Pilar | Recurso Cursor | Formato | Destino |
|-------|----------------|---------|---------|
| **Lexis** | Rules | `.mdc` | `.cursor/rules/<clade>/<subclade>/lex-*.mdc` |
| **Codex** | Rules | `.mdc` | `.cursor/rules/<clade>/<subclade>/codex-*.mdc` |
| **Katas** | Skills | `SKILL.md` | `.cursor/skills/kata-*/SKILL.md` |
| **Warriors** | Skills + Agents | `SKILL.md` + `.md` | `.cursor/skills/warrior-*/SKILL.md` + `.cursor/agents/warrior-*.md` |
| **Cries** | Commands | `.md` | `.cursor/commands/<clade>/<subclade>/cry-*.md` |

**Formatos nativos de Cursor:**

| Recurso | Extensión | Frontmatter | Descripción |
|---------|-----------|-------------|-------------|
| Rules | `.mdc` | `description` + `alwaysApply` | Contexto inyectado en el agente principal |
| Skills | `SKILL.md` | `name` + `description` | Capacidades que el agente adopta bajo demanda |
| Commands | `.md` | `description` | Slash commands invocables vía `/nombre` |
| Agents | `.md` | `name` + `description` | Subagentes aislados con system prompt propio |

> Los Warriors generan **dos artefactos**: un Skill (el agente principal adopta la persona) y un Agent (subagente aislado delegado vía Task). Esto permite tanto el uso inline como la delegación.

```
.cursor/
├── rules/                              # .mdc — Lexis + Codex
│   ├── samples/
│   │   ├── lex-sample.mdc
│   │   └── codex-sample.mdc
│   ├── _foundation/
│   │   ├── authoring/codex-*.mdc
│   │   ├── contributing/
│   │   │   ├── codex-contributing.mdc
│   │   │   ├── codex-commit-standards.mdc
│   │   │   ├── codex-semantic-version.mdc
│   │   │   └── lex-*.mdc
│   │   ├── process/lex-*.mdc
│   │   ├── quality/lex-*.mdc
│   │   └── i18n/
│   │       ├── lex-framework-language.mdc
│   │       └── codex-framework-language.mdc
│   └── documentation/i18n/
│       ├── lex-language.mdc, lex-language-{ptbr,en,es}.mdc
│       └── codex-language.mdc, codex-language-{ptbr,en,es}.mdc
│
├── skills/                             # SKILL.md — Katas + Warriors
│   ├── kata-sample/SKILL.md
│   ├── warrior-sample/SKILL.md
│   ├── kata-commit/SKILL.md
│   ├── kata-contribute/SKILL.md
│   ├── kata-tag/SKILL.md
│   ├── kata-create-*/SKILL.md
│   ├── kata-translate/SKILL.md
│   └── warrior-translator/SKILL.md
│
├── commands/                           # .md — Cries
│   ├── samples/cry-sample.md
│   ├── _foundation/
│   │   ├── authoring/cry-new-*.md
│   │   ├── contributing/cry-commit.md, cry-contribute.md, cry-tag.md
│   │   └── tooling/cry-make.md
│   └── documentation/i18n/cry-translate.md
│
└── agents/                             # .md — Warriors (subagentes)
    └── warrior-translator.md
```
