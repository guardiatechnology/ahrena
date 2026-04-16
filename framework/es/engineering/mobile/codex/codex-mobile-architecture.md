# Codex: Arquitectura Mobile

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Patrones arquitecturales para apps mobile (React Native, Flutter, Swift/SwiftUI, Kotlin/Compose) — estructura, state management, persistencia local, sync, navegación, pruebas

## Visión general

Este Codex es la referencia para **decisiones arquitecturales en mobile**: cuándo elegir React Native vs. nativo, cómo estructurar features, gestión de state, persistencia offline, sync, navegación, y pruebas. Consultado por `warrior-iris` al implementar o refactorizar mobile.

## Contexto

- **Dominio:** aplicaciones mobile iOS, Android, o multi-platform.
- **Público objetivo:** `warrior-iris`, agentes que implementan mobile.
- **Actualización:** cuando los frameworks evolucionan (Compose Multiplatform, SwiftUI nuevos APIs, RN 0.7x), o patrones de platform emergen.

## Contenido

### Elección de stack

| Stack | Cuándo preferir | Costos |
|---|---|---|
| **React Native** | Equipo fluido en TS/React; code sharing con web; features estándar mobile | Performance en animaciones pesadas; la integración con APIs nuevas del OS se atrasa |
| **Flutter** | Multi-platform (iOS, Android, web, desktop); UI compleja con control total | Curva de Dart; bundle más grande; la accesibilidad requiere atención extra |
| **Native (Swift + Kotlin)** | Performance crítica; uso extensivo de APIs nativas (ARKit, Health, etc.); 2 equipos | Duplicación de esfuerzo; la paridad funcional exige disciplina |
| **Kotlin Multiplatform (KMM)** | Lógica compartida (domain, networking) + UI nativa | El tooling aún en maduración; equipos experimentados en ambos |

Guardia default: **React Native** para apps cliente generales; **native** solo cuando la feature lo justifica.

### Estructura de directorios (React Native)

```
src/
├── app/                    # Entry point, providers globales
├── features/               # Features aisladas (~ frontend-architecture)
│   └── refund/
│       ├── screens/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       └── index.ts
├── components/             # UI kit reutilizable
├── navigation/             # React Navigation stack/tabs
├── hooks/                  # Hooks globales
├── services/               # API client, storage, analytics
├── state/                  # Global state (Zustand, Redux Toolkit)
├── i18n/                   # Localización
├── theme/                  # Tokens de design
└── types/                  # Tipos compartidos
```

Nativo Swift/Kotlin sigue convención de la plataforma (proyecto Xcode; Gradle modules por feature).

### State management

| Tipo | Herramienta React Native | Nativo iOS | Nativo Android |
|---|---|---|---|
| Server state | TanStack Query, SWR | Combine + URLSession | Flow + Retrofit |
| Client global | Zustand, Jotai, Redux Toolkit | SwiftUI @StateObject / EnvironmentObject | Compose ViewModel |
| Form | react-hook-form | Composable form state | Compose State |
| Persistente local | MMKV, AsyncStorage + encryption | Core Data, SwiftData | Room, DataStore |
| Caché offline | TanStack Query + persister | URLSession caché + Core Data | OkHttp caché + Room |

### Navegación

- **React Navigation**: stack (push/pop), tabs, drawer. Deep linking vía universal links.
- **iOS**: NavigationStack (SwiftUI) o UINavigationController (UIKit).
- **Android**: Navigation Compose o Jetpack Navigation.

Deep linking obligatorio para features compartibles (email, push, SMS).

### Persistencia local

- **Pequeño (config, flags, session tokens)**: MMKV (RN), UserDefaults (iOS), DataStore (Android). Siempre cifrado si contiene datos sensibles.
- **Estructurado (entidades, lista de transacciones)**: Core Data (iOS), Room (Android), WatermelonDB / Drizzle (RN).
- **Tokens de auth**: Keychain (iOS), Keystore (Android) — nunca en plain storage.

### Sync offline (ver `lex-mobile-offline-first`)

Tres capas:
1. **Caché de lectura** con TTL (TanStack Query + persister).
2. **Queue de mutations** persistida; worker hace sync; retry exponencial.
3. **Conflict resolution** estrategia declarada por entidad.

### Networking

- HTTPS 100% de los casos; certificate pinning para endpoints críticos.
- Timeout explícito (5-10s request; 30s upload).
- Retry con backoff en 5xx y timeout.
- Cancel en pantalla desmontada (AbortController / Combine cancellables).

### Accesibilidad

- **iOS**: VoiceOver — labels en todos los controles; traits correctos.
- **Android**: TalkBack — contentDescription; semantics modifier en Compose.
- **React Native**: `accessibilityLabel`, `accessibilityRole`; probar con screen reader real.
- **Contraste**: WCAG AA (4.5:1 texto normal); Dynamic Type (iOS) y Font Scale (Android) respetados.

### Performance

- **Startup time**: < 2s hasta la primera pantalla interactiva (cold).
- **Janky animations**: medir con Xcode Instruments, Android Profiler; 60 FPS mínimo.
- **Lista grande**: FlatList (RN) con `keyExtractor`, `getItemLayout`; LazyVStack (SwiftUI); LazyColumn (Compose).
- **Imágenes**: lazy load, caché, formatos modernos (WebP, HEIF).
- **Bundle size**: proguard/R8 (Android), App Thinning (iOS), bundle splitting (RN).

### Push notifications

- **iOS**: APNs vía FCM o directo.
- **Android**: FCM.
- **Unificado**: Amazon SNS, OneSignal cuando multi-platform.

El payload incluye `notification_id` para dedup y analytics.

### Observabilidad (conforme `lex-observability-required`)

- **Crash reporting**: Firebase Crashlytics, Sentry, Bugsnag.
- **Analytics**: eventos estructurados (nombre + props) — mismo schema iOS y Android (`lex-mobile-platform-parity`).
- **Performance traces**: Firebase Performance, New Relic Mobile.
- **Logs**: estructurados; sin PII; enviar al backend en error crítico.

### Pruebas

| Nivel | RN | iOS | Android |
|---|---|---|---|
| Unit | Jest / Vitest | XCTest | JUnit + Kotest |
| Component | React Native Testing Library | ViewInspector (SwiftUI) | Compose UI Testing |
| Integration | Detox | XCUITest | Espresso |
| E2E | Detox, Maestro | XCUITest (simulator/device) | Espresso + UI Automator |
| Snapshot (visual) | Chromatic + RN | iOSSnapshotTestCase | Paparazzi |

`lex-test-pyramid` aplica: 70% unit / 20% integration / 10% E2E.

### CI/CD

- **iOS**: Fastlane + Xcode Cloud o Bitrise; TestFlight para beta.
- **Android**: Fastlane + Gradle; Play Console Internal Track para beta.
- **RN/Flutter**: CodePush / EAS Update para hotfix de JS sin review de la store.

### Seguridad

- Secrets nunca en bundle (`lex-frontend-security` equivalente).
- Jailbreak / root detection en features sensibles (pago).
- App Transport Security (iOS) strict; Network Security Config (Android) sin cleartext.
- Biometría vía LocalAuthentication (iOS), BiometricPrompt (Android) para auth crítica.

## Referencias

- `lex-mobile-platform-parity`, `lex-mobile-offline-first`
- `lex-frontend-testing`, `lex-frontend-accessibility` — principios análogos
- `codex-frontend-architecture` — paralelo en web
- `warrior-iris`
- [React Native Docs](https://reactnative.dev/docs/getting-started)
- [Swift/SwiftUI Docs](https://developer.apple.com/documentation/swiftui)
- [Android/Compose Docs](https://developer.android.com/jetpack/compose/documentation)
