# Codex: Slack MCP Server

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Herramientas y autenticación del servidor MCP de Slack para Cursor y Claude Code

## Visión General

Este Codex es la referencia para usar el **servidor MCP de Slack** en proyectos Ahrena. Ver `codex-mcp-common` para patrones MCP compartidos (autenticación, configuración, fallback) y `codex-notifications` para el contrato provider-agnóstico que mapea `notifications.provider: slack` a las herramientas listadas aquí. Este documento se enfoca en herramientas, parámetros y casos de uso específicos de Slack: enviar notificaciones de eventos del framework (PR timeout, release, digest de planes) y leer contexto de canales cuando sea relevante.

## Contexto

- **Dominio:** envío y lectura de mensajes, búsqueda, canvas y perfiles de usuario en Slack vía MCP.
- **Público objetivo:** agentes IA (Athena, Janus, Eunomia) que publican notificaciones; agentes que necesitan leer contexto puntual de discusiones en canales.
- **Actualización:** cuando Slack agregue nuevas herramientas al servidor MCP, o cuando el scope OAuth de la app cambie.
- **Fuente oficial:** [https://docs.slack.dev/ai/slack-mcp-server/](https://docs.slack.dev/ai/slack-mcp-server/)

## Contenido

### Configuración por plataforma

Las dos plataformas consumen el **servidor remoto oficial de Slack** en `https://mcp.slack.com/mcp` (escalón 1 de la preferencia de transporte definida en `lex-mcp` §5 — cero dependencia local). Auth es **OAuth 2.0 confidencial**: en la primera llamada, el usuario autentica vía browser usando el `client_id` + `client_secret` de la app Slack; el token lo gestiona la plataforma.

> Fuente: "Slack supports JSON-RPC 2.0 over Streamable HTTP. All requests should be sent to: `https://mcp.slack.com/mcp`" y "Slack supports confidential OAuth for MCP clients. You'll need to use your app's `client_id` and `client_secret`."

**Cursor (`.cursor/mcp.json`):**
```json
"slack": {
  "url": "https://mcp.slack.com/mcp"
}
```

**Claude Code (`.mcp.json`):**
```json
"slack": {
  "type": "http",
  "url": "https://mcp.slack.com/mcp"
}
```

No hay variables de entorno en `.directives` ni en el JSON. No hay fallback vía npx o binario porque Slack expone **solo** HTTP por ahora (oficial: "We do not support SSE-based connections or Dynamic Client Registration at this time"). Si el equipo necesita una ruta alternativa (CI sin browser, integración programática), abrir ADR registrando la excepción.

### Activación

```bash
# 1. Listar mcp.servers en .ahrena/.directives y descomentar "slack"
# 2. Habilitar vía make:
make mcp-enable SERVER=slack

# 3. Reabrir Cursor / Claude Code; en la primera invocación, el flujo OAuth se abre en el browser.
```

### Herramientas expuestas

Categorías documentadas en el overview oficial:

| Categoría | Tools (nombres representativos) | Uso típico en el framework |
|---|---|---|
| **Search** | `slack_search_messages`, `slack_search_files`, `slack_search_channels`, `slack_search_users` | Buscar discusión previa de un tema antes de notificar |
| **Messages** | `slack_send_message`, `slack_send_message_draft`, `slack_read_channel`, `slack_read_thread`, `slack_schedule_message` | Athena, Janus, Eunomia publican notificaciones vía `slack_send_message` |
| **Canvas** | `slack_create_canvas`, `slack_read_canvas`, `slack_update_canvas` | Eunomia publica digest periódico como canvas actualizado |
| **Profiles** | `slack_read_user_profile` | Resolver `@login` a nombre real en alertas |

> Los nombres exactos pueden variar según el cliente; el servidor MCP de Slack expone la lista vía `tools/list` en la primera conexión. Consulte siempre la doc oficial para el nombre canónico en uso.

### `slack_send_message` — invocación canónica

Herramienta primaria consumida por `codex-notifications`. Parámetros relevantes:

| Parámetro | Origen | Ejemplo |
|---|---|---|
| `channel` | `notifications.channels.{evento}` de `.ahrena/.directives` | `"notifications-gh-pull-request"` (sin `#`) |
| `text` | Construido por el agente per template de `codex-notifications` §5 | Multiline con link del PR/Release |
| `thread_ts` | (opcional) Para responder a un thread existente | — |

El agente lee el valor lógico de `.directives` y lo pasa **directamente** como `channel`. Los nombres en el workspace de Slack deben coincidir con los canales lógicos. Si el canal no existe, el MCP retorna error estructurado — per `lex-mcp` §4, retry único + log + prosigue.

### Resolución de canal lógico → canal real de Slack

La convención del framework Ahrena:

| Clave lógica en `.directives` | Nombre esperado en el workspace de Slack |
|---|---|
| `notifications.channels.pr_review_timeout` | `notifications-gh-pull-request` |
| `notifications.channels.release_notify` | `notifications-gh-releases` |
| `notifications.channels.plans_status` | `notifications-plans-status` |

Los equipos pueden renombrar los canales lógicos para coincidir con su nomenclatura interna (ej.: `eng-pr-alerts`), siempre que actualicen `.ahrena/.directives` en el mismo paso.

### Autenticación OAuth — primera ejecución

1. El agente invoca una tool de Slack por primera vez (ej.: `slack_send_message`).
2. Cursor / Claude Code abre el browser en el flujo OAuth de Slack.
3. El usuario autoriza la app en el workspace correspondiente (scopes: lectura de mensajes, envío en canales, lectura de perfiles — según app registrada).
4. Token almacenado por la plataforma (no toca `.directives`).
5. Próximas llamadas usan el token automáticamente.

Per `lex-mcp` §2, **ningún** token, `client_id` o `client_secret` va a `.ahrena/.directives` o a archivo versionado. La configuración de la app Slack se hace una vez en el workspace, por el admin.

### Fallback cuando MCP indisponible

Para notificaciones, `codex-notifications` §4 define el comportamiento:

1. Retry único (5s).
2. Si sigue fallando, log estructurado + prosigue. El flujo principal (Athena terminando el loop de revisión, Janus terminando la release, etc.) NO falla por eso.

Para lectura de contexto vía Slack (uso menos común), aplica `lex-mcp` §4 estándar: presentar 3 opciones al usuario (fallback CLI cuando aplica — no existe para Slack hoy; pausar; abortar).

## Restricciones

- **Sin stdio/npx**: el Slack MCP es HTTP-only por ahora. No intentar inventar fallback npx sin ADR.
- **Sin credenciales en código/.directives**: per `lex-mcp` §2.
- **No confundir canales lógicos con IDs**: el agente pasa **nombre** del canal (sin `#`), no ID `C0123...`. Slack MCP resuelve internamente.

## Referencias

- [https://docs.slack.dev/ai/slack-mcp-server/](https://docs.slack.dev/ai/slack-mcp-server/) — fuente oficial
- `lex-mcp` — reglas de uso de MCP (§5 preferencia de transporte HTTP > binario > npx)
- `codex-mcp-common` — patrones compartidos
- `codex-notifications` — contrato provider-agnóstico (consumidor primario)
- `framework/mcp/slack.json` — config consumida por el install
- `lex-directives` — sección `notifications:` en `.ahrena/.directives`
- `warrior-athena`, `warrior-janus`, `warrior-eunomia` — consumidores de las tools
