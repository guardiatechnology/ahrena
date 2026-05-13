# Codex: Notificaciones Provider-Agnósticas vía MCP

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Envío de notificaciones por agentes (Athena, Argos, Janus, Eunomia) vía el servidor MCP de notificación configurado en `.ahrena/.directives`

## Visión General

Este Codex es el manual canónico de notificaciones en el framework Ahrena. Define el contrato entre los agentes que publican alertas (Athena en el PR review timeout, Janus en la release publicada, Eunomia en el digest de planes) y el provider concreto (Slack, Discord, Teams) — sin atar Lexis, Codex o Warriors a un vendor específico.

La regla es simple: los agentes referencian **claves abstractas** (`notifications.provider` + `notifications.channels.{evento}`) leídas de `.ahrena/.directives`; este Codex traduce esas claves a la tool MCP correspondiente, en tiempo de ejecución.

## Contexto

- **Dominio:** envío de notificaciones a canales de comunicación corporativa (Slack/Discord/Teams) por agentes IA del framework.
- **Público objetivo:** Athena, Argos, Janus, Eunomia, y cualquier agente que tenga un disparador de notificación en el flujo Issue-Driven.
- **Actualización:** cuando se agregue un nuevo provider al framework, o cuando se defina una nueva clave de canal lógico (`notifications.channels.*`).

## Contenido

### 1. Claves abstractas en `.ahrena/.directives`

La sección `notifications:` en `.directives` (per `lex-directives`) declara:

```yaml
notifications:
  provider: slack                # slack | discord | teams | none
  channels:
    pr_review_timeout: "notifications-gh-pull-request"
    release_notify:    "notifications-gh-releases"
    plans_status:      "notifications-plans-status"
  working_hours:
    start: "07:00"
    end:   "22:00"
    timezone: "America/Sao_Paulo"
```

| Clave | Consumidor | Cuándo dispara |
|---|---|---|
| `notifications.channels.pr_review_timeout` | `warrior-athena` | Agotamiento de los 3 ciclos de 15 min sin aprobación humana en PR `to review` |
| `notifications.channels.release_notify` | `warrior-janus` | Release publicada (tag empujada, `validate-tag.yml` pasó, GitHub Release creada) |
| `notifications.channels.plans_status` | `warrior-eunomia` | Digest periódico de planes activos en el loop PM |

### 2. Mapeo provider → tool MCP

Cada provider expone un conjunto propio de tools MCP. El agente lee `notifications.provider` y selecciona la tool correspondiente:

| `provider` | Tool MCP usada | Manual del provider |
|---|---|---|
| `slack` | `slack_send_message` | `codex-mcp-slack` |
| `discord` | (futuro — `discord_post_message`) | (futuro `codex-mcp-discord`) |
| `teams` | (futuro — `teams_post_message`) | (futuro `codex-mcp-teams`) |
| `none` | ninguna — el agente registra warning y prosigue | — |

Cuando entra un nuevo provider al framework, este Codex gana una fila; ningún Lex/Warrior/Kata cambia.

### 3. Resolución de canal lógico → canal real

La clave `notifications.channels.pr_review_timeout` carga el **nombre lógico** ("notifications-gh-pull-request" en el ejemplo). El agente pasa ese valor directamente al parámetro `channel` de la tool MCP correspondiente. Los mapeos provider-específicos (ej.: Slack acepta el nombre del canal sin `#`; Discord usa ID numérico) están documentados en `codex-mcp-{provider}`.

### 4. Flujo canónico de publicación

```
1. El agente decide notificar (Athena tras el 3er ciclo, Janus en la release, etc.)
2. El agente lee notifications.provider de .ahrena/.directives
3. Si provider == "none" → log warning + prosigue (sin fallar)
4. Verifica que el provider está en mcp.servers y MCP está activo
5. Lee notifications.channels.{evento} (canal lógico)
6. Invoca la tool MCP del provider con (channel=<lógico>, text=<msg>)
7. En caso de error del MCP: retry único (5s), luego log + prosigue
```

Principios:

- **Provider == none**: el agente NO falla el flujo principal por causa de la notificación. Registra warning estructurado y sigue.
- **MCP indisponible**: per `lex-mcp` §4, retry único; si sigue fallando, presenta las 3 opciones (fallback CLI cuando aplica, pausar, abortar). Para notificaciones, el default es "log + prosigue" porque el flujo principal ya completó.
- **Ventana útil**: `notifications.working_hours` aplica a digests no críticos (Eunomia). Notificaciones de evento (PR timeout, release) ignoran la ventana.

### 5. Contenido del mensaje

El payload mínimo incluye contexto suficiente para que el canal actúe sin necesidad de abrir GitHub:

**PR review timeout (Athena):**

```
🟡 PR esperando revisión hace 45min sin aprobación humana
Repo: {owner/repo}  •  PR: #{N}  •  Autor: @{login}
Reviewers solicitados: @{a}, @{b}
Status: {gh pr view --json reviewDecision}
Link: https://github.com/{owner/repo}/pull/{N}
```

**Release publicada (Janus):**

```
🚀 Release {tag} publicada en {repo}
Tipo: {patch|minor|major}
Highlights: {top 3 entries del CHANGELOG}
Link: https://github.com/{owner/repo}/releases/tag/{tag}
```

**Plans status digest (Eunomia):**

```
📋 Digest de planes activos — {date}
 stalled  ⚠️  3 planes sin heartbeat hace >4h
 healthy 🟢 12 planes en movimiento (last_activity < 30min)
 blocked 🚫 1 plan en changes-requested hace >24h
[ver detalles en el anexo / link]
```

Los mensajes deben ser **directos**, **accionables** y **autocontenidos** — per `lex-brand-voice`.

### 6. Cambiar de provider

Cambio de provider son **3 pasos** (cero edición de Lex/Codex/Warrior/Kata):

1. Agregar `framework/mcp/{nuevo}.json` per `lex-mcp` §5 (preferir HTTP > binario > npx).
2. Habilitar vía `make mcp-enable SERVER={nuevo}`.
3. Editar `notifications.provider` en `.ahrena/.directives` con el nuevo valor.

Los canales lógicos (`notifications.channels.*`) se pueden mantener o renombrar para corresponder a la convención del nuevo provider.

## Restricciones

- **No citar el provider concreto en Lexis/Warriors/Katas.** Solo `notifications.provider` y `notifications.channels.{key}`.
- **No almacenar credenciales en `.directives`.** Per `lex-mcp` §2, las credenciales van en variables de entorno.
- **No intentar notificaciones antes que el MCP esté listado en `mcp.servers`.** Per `lex-mcp` §3.

## Referencias

- `lex-mcp` — reglas de uso de MCP (preferencia de transporte, fallback, autenticación)
- `lex-directives` — schema de la sección `notifications:` en `.ahrena/.directives`
- `codex-mcp-common` — patrones compartidos de MCP
- `codex-mcp-slack` — provider inicial (Slack)
- `lex-agent-planning` — owners de las transiciones que disparan notificaciones
- `lex-brand-voice` — tono de los mensajes
- `warrior-athena`, `warrior-janus`, `warrior-eunomia` — consumidores de este Codex
