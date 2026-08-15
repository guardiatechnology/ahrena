# Lexis: Mobile Opera Offline-First

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Apps mobile (iOS, Android, React Native, Flutter) — comportamento em condições de rede degradada, sync de dados, cache e resolução de conflito

## Lei

> **Todo app mobile DEVE operar em três estados de rede: online (tudo funciona), intermitente (cache serve leitura, ações escrita enfileiram), offline (cache serve leitura, ações escrita enfileiram sem travar UI). Nunca a UI PODE ficar bloqueada esperando resposta de rede por mais de 5 segundos sem oferecer alternativa (cache, cancelar, retry). Conflitos de sync DEVEM ter estratégia declarada (last-write-wins, server-wins, manual resolution).**

## Regras

### 1. Três estados são desenhados

Para cada feature:

- **Online**: comportamento normal; round-trip ao servidor.
- **Intermitente** (timeout, 5xx): cache local retorna; action é enfileirada; usuário vê "enviando…" ou "aguardando rede".
- **Offline** (sem conectividade detectada): mesma UX que intermitente + banner "Modo offline".

Telas que funcionam só online (ex.: web view externa) são explicitamente documentadas e sinalizam isso ao usuário.

### 2. Cache de leitura com TTL

- Todo GET significativo tem **cache local** (SQLite, Room, Core Data, MMKV).
- TTL explícito (ex.: lista de transações 5min; perfil do usuário 1h).
- Indicação visual quando cache está sendo servido e dado pode estar stale (ex.: timestamp "atualizado há 3min").

### 3. Mutations como fila

Ações de escrita (POST, PUT, DELETE):

- Persistidas em fila local (DB + serialização).
- UI mostra otimisticamente o resultado ("Enviado").
- Worker em background faz sync; retry exponencial em falha; limite de retries (ex.: 5) antes de sinalizar erro ao usuário.
- Usuário pode cancelar ação enfileirada antes de sync.

### 4. UI não trava esperando rede

Nenhuma tela deixa spinner rodando >5s sem:

- Oferecer cancelar.
- Mostrar cache disponível.
- Explicar o que está acontecendo.
- Oferecer retry.

### 5. Estratégia de conflito declarada

Quando mutation local diverge de estado servidor (user editou offline, alguém editou online):

| Estratégia | Quando usar |
|---|---|
| **Last-write-wins (timestamp)** | Dados simples sem consequência de perda (ex.: preferências do usuário) |
| **Server-wins** | Cliente confia no servidor (ex.: saldo, posição financeira) |
| **Client-wins** | Cliente é fonte da verdade (ex.: draft local, nota pessoal) |
| **Manual resolution** | Conflito significativo merece decisão do usuário (ex.: 2 edits em nota importante) |

Declarar estratégia por entidade; documentar em `docs/mobile-sync.md`.

### 6. Telemetria de offline

Métricas monitoradas:

- % de sessões com pelo menos 1 erro de rede.
- Tempo médio em estado "intermitente" antes de recuperar.
- Taxa de mutations enfileiradas que falham sync após N retries.
- Tamanho médio da fila local.

Anomalias alertam on-call (`lex-runbook-for-every-alert`).

## Validação Automatizada

- **Ferramenta:**
  - Teste E2E com Network Link Conditioner (iOS) / Android Emulator throttling: simula 3G lento, offline.
  - Verifica que telas não mostram spinner >5s; que cache serve; que mutations enfileiram.
- **Momento:** sprint release candidate; a cada nova feature significativa.
- **Métrica:** 100% das telas principais passam smoke test offline; <2% de sessões em produção com erro de rede sem recovery.
