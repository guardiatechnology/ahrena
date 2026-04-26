# Ahrena — Framework de Capacidades AI-First

> **Producto:** Ahrena · **Responsable:** Guardia · **Estado:** Activo · **Tipo:** Plataforma Interna

## ¿Qué es Ahrena?

**Ahrena** es el Framework de Capacidades AI-First de Guardia. Estructura el conocimiento, los procesos y el comportamiento de los agentes de AI mediante una taxonomía unificada, permitiendo una colaboración consistente, auditable y reproducible entre humanos y AI en cualquier disciplina de ingeniería.

Ahrena define *cómo* los equipos y los agentes de AI de Guardia piensan, deciden y ejecutan — desde un mensaje de commit hasta el diseño completo de una feature de producto.

## Por qué creamos Ahrena

A medida que Guardia adoptó agentes de AI como participantes de primera clase en los flujos de trabajo de ingeniería, la necesidad de un modelo operativo estructurado, versionado y agnóstico de plataforma se volvió crítica. Sin él:

- Los agentes tomaban decisiones inconsistentes entre sesiones
- El conocimiento vivía en el historial de chat, no en artefactos versionados
- El onboarding de nuevos ingenieros o agentes requería transferencia de conocimiento tribal
- No existía una única fuente de verdad para procesos, convenciones y estándares

Ahrena resuelve esto al tratar las reglas de comportamiento de los agentes, el conocimiento de referencia, las skills ejecutables y los comandos como **código** — versionado, revisable e implementable.

## Principios fundamentales

| Principio | Qué significa |
|---|---|
| **AI como copiloto, no piloto** | Los humanos definen la dirección; los agentes ejecutan y proponen, nunca deciden solos |
| **Proceso sobre herramienta** | Las reglas y procedimientos son agnósticos de plataforma; las herramientas van y vienen |
| **Artefactos como código** | Toda convención, ley y skill es un archivo versionado en `framework/` |
| **`framework/` como fuente de verdad** | Una única fuente canónica; todas las configuraciones de plataforma (Cursor, Claude Code) se generan desde ella |

## Arquitectura en resumen

```
framework/
├── en/                  ← Artefactos en inglés (fuente de verdad)
├── pt-BR/               ← Artefactos en portugués brasileño
├── es/                  ← Artefactos en español
└── templates/           ← Templates oficiales por Pilar
```

El framework se organiza por **Clade → Subclade → Pilar**. Dentro de cada Pilar, los artefactos se nombran según el prefijo del tipo:

| Pilar | Prefijo | Papel |
|---|---|---|
| **Lexis** | `lex-` | Leyes inviolables — sin excepción |
| **Codex** | `codex-` | Manuales de referencia — conocimiento y orientación |
| **Katas** | `kata-` | Skills ejecutables — procedimientos reproducibles |
| **Warriors** | `warrior-` | Agentes especializados — orquestan Katas |
| **Cries** | `cry-` | Comandos de alto nivel — activan Warriors o Katas |

## Escala

| Dimensión | Cantidad |
|---|---|
| Total de artefactos en el framework | ~649 |
| Idiomas | 3 (en, pt-BR, es) |
| Lexis (leyes inviolables) | 39 |
| Codex (manuales de referencia) | 55 |
| Katas (skills ejecutables) | 53 |
| Warriors (agentes especializados) | 14 |
| Cries (comandos) | 31 |
| Clades | 4 |
| Subclades | 16 |

## Plataformas compatibles

Ahrena es agnóstico de plataforma. El instalador (`scripts/install.py`) genera configuraciones específicas para cada IDE desde `framework/`:

| Plataforma | Configuración generada | Notas |
|---|---|---|
| **Claude Code** | `.claude/` (skills, commands, agents, docs) + `CLAUDE.md` | Plataforma principal en Guardia |
| **Cursor** | `.cursor/` (rules, skills, commands, agents) | Integración completa con el IDE |

## Capacidades principales

### Issue-Driven Development

El Warrior `warrior-athena` orquesta un flujo de desarrollo completo en 7 fases — desde la lectura de una issue en GitHub hasta la apertura de un PR revisado — con 2 gates obligatorios (Scope y Quality), trazabilidad completa entre criterios de aceptación y pruebas, y creación de ADRs para decisiones arquitectónicas.

[→ lex-issue-driven](../../framework/en/engineering/workflow/lexis/lex-issue-driven.md)

### Ciclo de Diseño de Plataforma

Los Warriors `warrior-prometheus`, `warrior-theseus`, `warrior-daedalus` y `warrior-kronos` cubren el ciclo completo de diseño de feature: modelado de dominio (DDD), diseño de API (OAS) y documentación de eventos (CloudEvents).

### Experiencia de Producto AI-First

La Lexis `lex-ai-first-experience` establece que toda interfaz orientada al usuario en Guardia debe utilizar a Isac (el agente de AI) como superficie principal de interacción — no una barra lateral de funcionalidades.

[→ lex-ai-first-experience](../../framework/en/design/system/lexis/lex-ai-first-experience.md)

### Multilingüe por defecto

Todo artefato del framework existe en inglés, portugués brasileño y español. El `warrior-translator` y el `kata-translate` automatizan la traducción con reglas específicas por idioma, aplicadas por las leyes `lex-language-*`.

## Índice de documentación

| Documento | Descripción |
|---|---|
| [Conceptos](concepts.md) | Pilares, Clades, Subclades, taxonomía de direccionamiento |
| [Clades & Subclades](clades.md) | Catálogo completo con cobertura de pilares por subclade |
| [Catálogo de Lexis](lexis.md) | Las 39 leyes inviolables |
| [Catálogo de Codex](codex.md) | Los 55 manuales de referencia |
| [Catálogo de Katas](katas.md) | Las 53 skills ejecutables |
| [Catálogo de Warriors](warriors.md) | Los 14 agentes especializados |
| [Catálogo de Cries](cries.md) | Los 31 comandos de alto nivel |
