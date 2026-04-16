# Lexis: Mobile Opera Offline-First

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Apps mobile (iOS, Android, React Native, Flutter) — comportamiento en condiciones de red degradada, sync de datos, caché y resolución de conflicto

## Propósito

Mobile no es desktop conectado. Los usuarios en metro, ascensor, área rural o modo avión esperan que la app aún funcione — al menos para consultar datos recientes y poner acciones en cola. Apps que muestran "Error de conexión" en cada pantalla fracasan en el mundo real. Asumir red perfecta es asumir que el usuario solo está en casa con Wi-Fi.

Esta Lexis existe para garantizar que **toda app mobile producida sea diseñada offline-first**: las operaciones de lectura sirven desde caché cuando la red cae, las acciones de escritura son puestas en cola, la UI nunca se traba esperando red, y los conflictos de sync tienen estrategia explícita.

## Ley

> **Toda app mobile DEBE operar en tres estados de red: online (todo funciona), intermitente (caché sirve lectura, acciones de escritura van a cola), offline (caché sirve lectura, acciones de escritura van a cola sin trabar UI). Nunca la UI PUEDE quedarse bloqueada esperando respuesta de red por más de 5 segundos sin ofrecer alternativa (caché, cancelar, retry). Los conflictos de sync DEBEN tener estrategia declarada (last-write-wins, server-wins, manual resolution).**

## Reglas

### 1. Tres estados son diseñados

Para cada feature:

- **Online**: comportamiento normal; round-trip al servidor.
- **Intermitente** (timeout, 5xx): el caché local retorna; la action es puesta en cola; el usuario ve "enviando…" o "aguardando red".
- **Offline** (sin conectividad detectada): misma UX que intermitente + banner "Modo offline".

Las pantallas que funcionan solo online (ej.: web view externa) están explícitamente documentadas y señalan eso al usuario.

### 2. Caché de lectura con TTL

- Todo GET significativo tiene **caché local** (SQLite, Room, Core Data, MMKV).
- TTL explícito (ej.: lista de transacciones 5min; perfil del usuario 1h).
- Indicación visual cuando el caché está siendo servido y el dato puede estar stale (ej.: timestamp "actualizado hace 3min").

### 3. Mutations como cola

Acciones de escritura (POST, PUT, DELETE):

- Persistidas en cola local (DB + serialización).
- UI muestra optimísticamente el resultado ("Enviado").
- Worker en background hace sync; retry exponencial en fallo; límite de retries (ej.: 5) antes de señalar error al usuario.
- El usuario puede cancelar acción en cola antes del sync.

### 4. UI no se traba esperando red

Ninguna pantalla deja spinner corriendo >5s sin:

- Ofrecer cancelar.
- Mostrar caché disponible.
- Explicar lo que está pasando.
- Ofrecer retry.

### 5. Estrategia de conflicto declarada

Cuando mutation local diverge del estado servidor (user editó offline, alguien editó online):

| Estrategia | Cuándo usar |
|---|---|
| **Last-write-wins (timestamp)** | Datos simples sin consecuencia de pérdida (ej.: preferencias del usuario) |
| **Server-wins** | El cliente confía en el servidor (ej.: saldo, posición financiera) |
| **Client-wins** | El cliente es fuente de la verdad (ej.: draft local, nota personal) |
| **Manual resolution** | El conflicto significativo merece decisión del usuario (ej.: 2 edits en nota importante) |

Declarar estrategia por entidad; documentar en `docs/mobile-sync.md`.

### 6. Telemetría de offline

Métricas monitoreadas:

- % de sesiones con al menos 1 error de red.
- Tiempo medio en estado "intermitente" antes de recuperar.
- Tasa de mutations en cola que fallan sync tras N retries.
- Tamaño medio de la cola local.

Las anomalías alertan al on-call (`lex-runbook-for-every-alert`).

## Alcance

- **Aplica a:** todos los apps mobile producidos en el proyecto.
- **Agentes vinculados:** `warrior-iris`.
- **Excepciones:** features intrínsecamente online (ej.: pago vía NFC exige conectividad), documentadas explícitamente.

## Consecuencias de Violación

1. **UX catastrófica en metro**: la app se traba; el usuario la mata; impresión negativa permanente.
2. **Pérdida de acción del usuario**: el user escribió + el botón falló por red → pierde todo.
3. **Reviews negativos en la store**: "Lento", "No funciona sin Wi-Fi", "Se traba" → rating cae.
4. **Remediación:**
   - Auditar pantalla por pantalla: ¿cuál es el comportamiento en flight mode?
   - Implementar caché local + queue por feature.
   - Telemetría de red para monitorear.

## Validación Automatizada

- **Herramienta:**
  - Prueba E2E con Network Link Conditioner (iOS) / Android Emulator throttling: simula 3G lento, offline.
  - Verifica que las pantallas no muestran spinner >5s; que el caché sirve; que las mutations van a cola.
- **Momento:** sprint release candidate; en cada nueva feature significativa.
- **Métrica:** 100% de las pantallas principales pasan smoke test offline; <2% de sesiones en producción con error de red sin recovery.

## Referencias

- `codex-mobile-architecture`
- `lex-mobile-platform-parity`
- `warrior-iris`
