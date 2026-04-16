# Lexis: Mobile Operates Offline-First

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Mobile apps (iOS, Android, React Native, Flutter) — behavior in degraded network conditions, data sync, cache, and conflict resolution

## Purpose

Mobile is not connected desktop. Users in the subway, elevator, rural area, or airplane mode expect the app to still work — at least to consult recent data and queue actions. Apps that display "Connection error" on every screen fail in the real world. Assuming perfect network is assuming the user is only at home with Wi-Fi.

This Lexis exists to ensure that **every mobile app produced is designed offline-first**: read operations serve from cache when the network fails, write actions are queued, UI never freezes waiting for network, and sync conflicts have an explicit strategy.

## Law

> **Every mobile app MUST operate in three network states: online (everything works), intermittent (cache serves reads, write actions queue), offline (cache serves reads, write actions queue without freezing UI). Never MAY the UI be blocked waiting for network response for more than 5 seconds without offering an alternative (cache, cancel, retry). Sync conflicts MUST have a declared strategy (last-write-wins, server-wins, manual resolution).**

## Rules

### 1. Three states are designed

For each feature:

- **Online**: normal behavior; round-trip to server.
- **Intermittent** (timeout, 5xx): local cache returns; action is queued; user sees "sending…" or "waiting for network".
- **Offline** (no detected connectivity): same UX as intermittent + banner "Offline mode".

Screens that only work online (e.g.: external web view) are explicitly documented and signal this to the user.

### 2. Read cache with TTL

- Every significant GET has **local cache** (SQLite, Room, Core Data, MMKV).
- Explicit TTL (e.g.: transaction list 5min; user profile 1h).
- Visual indication when cache is being served and data may be stale (e.g.: timestamp "updated 3min ago").

### 3. Mutations as queue

Write actions (POST, PUT, DELETE):

- Persisted in local queue (DB + serialization).
- UI optimistically shows the result ("Sent").
- Background worker performs sync; exponential retry on failure; retry limit (e.g.: 5) before signaling error to user.
- User can cancel queued action before sync.

### 4. UI does not freeze waiting for network

No screen lets spinner run >5s without:

- Offering cancel.
- Showing available cache.
- Explaining what is happening.
- Offering retry.

### 5. Declared conflict strategy

When local mutation diverges from server state (user edited offline, someone edited online):

| Strategy | When to use |
|---|---|
| **Last-write-wins (timestamp)** | Simple data without consequence of loss (e.g.: user preferences) |
| **Server-wins** | Client trusts the server (e.g.: balance, financial position) |
| **Client-wins** | Client is source of truth (e.g.: local draft, personal note) |
| **Manual resolution** | Significant conflict deserves user decision (e.g.: 2 edits on important note) |

Declare strategy per entity; document in `docs/mobile-sync.md`.

### 6. Offline telemetry

Monitored metrics:

- % of sessions with at least 1 network error.
- Average time in "intermittent" state before recovering.
- Rate of queued mutations that fail sync after N retries.
- Average local queue size.

Anomalies alert on-call (`lex-runbook-for-every-alert`).

## Applicability

- **Applies to:** all mobile apps produced in the project.
- **Linked agents:** `warrior-iris`.
- **Exceptions:** intrinsically online features (e.g.: NFC payment requires connectivity), explicitly documented.

## Consequences of Violation

1. **Catastrophic UX in the subway**: app freezes; user kills it; permanent negative impression.
2. **Loss of user action**: user typed + button failed due to network → loses everything.
3. **Negative reviews on the store**: "Slow", "Doesn't work without Wi-Fi", "Freezes" → rating drops.
4. **Remediation:**
   - Audit screen by screen: what is the behavior in flight mode?
   - Implement local cache + queue per feature.
   - Network telemetry for monitoring.

## Automated Validation

- **Tool:**
  - E2E test with Network Link Conditioner (iOS) / Android Emulator throttling: simulates slow 3G, offline.
  - Verifies that screens do not show spinner >5s; that cache serves; that mutations queue.
- **Timing:** sprint release candidate; on each significant new feature.
- **Metric:** 100% of main screens pass offline smoke test; <2% of production sessions with network error without recovery.

## References

- `codex-mobile-architecture`
- `lex-mobile-platform-parity`
- `warrior-iris`
