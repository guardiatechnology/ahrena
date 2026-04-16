# Codex: Mobile Architecture

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Architectural patterns for mobile apps (React Native, Flutter, Swift/SwiftUI, Kotlin/Compose) — structure, state management, local persistence, sync, navigation, tests

## Overview

This Codex is the reference for **architectural decisions in mobile**: when to choose React Native vs. native, how to structure features, state management, offline persistence, sync, navigation, and tests. Consulted by `warrior-iris` when implementing or refactoring mobile.

## Context

- **Domain:** iOS, Android, or multi-platform mobile applications.
- **Target audience:** `warrior-iris`, agents that implement mobile.
- **Update:** when frameworks evolve (Compose Multiplatform, SwiftUI new APIs, RN 0.7x), or platform patterns emerge.

## Content

### Stack choice

| Stack | When to prefer | Costs |
|---|---|---|
| **React Native** | Team fluent in TS/React; code sharing with web; standard mobile features | Performance in heavy animations; integration with new OS APIs lags |
| **Flutter** | Multi-platform (iOS, Android, web, desktop); complex UI with full control | Dart learning curve; larger bundle; accessibility requires extra attention |
| **Native (Swift + Kotlin)** | Critical performance; extensive use of native APIs (ARKit, Health, etc.); 2 teams | Duplication of effort; functional parity requires discipline |
| **Kotlin Multiplatform (KMM)** | Shared logic (domain, networking) + native UI | Tooling still maturing; teams experienced in both |

Guardia default: **React Native** for general client apps; **native** only when feature justifies.

### Directory structure (React Native)

```
src/
├── app/                    # Entry point, global providers
├── features/               # Isolated features (~ frontend-architecture)
│   └── refund/
│       ├── screens/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       └── index.ts
├── components/             # Reusable UI kit
├── navigation/             # React Navigation stack/tabs
├── hooks/                  # Global hooks
├── services/               # API client, storage, analytics
├── state/                  # Global state (Zustand, Redux Toolkit)
├── i18n/                   # Localization
├── theme/                  # Design tokens
└── types/                  # Shared types
```

Native Swift/Kotlin follows platform convention (Xcode project; Gradle modules per feature).

### State management

| Type | React Native Tool | Native iOS | Native Android |
|---|---|---|---|
| Server state | TanStack Query, SWR | Combine + URLSession | Flow + Retrofit |
| Client global | Zustand, Jotai, Redux Toolkit | SwiftUI @StateObject / EnvironmentObject | Compose ViewModel |
| Form | react-hook-form | Composable form state | Compose State |
| Local persistent | MMKV, AsyncStorage + encryption | Core Data, SwiftData | Room, DataStore |
| Offline cache | TanStack Query + persister | URLSession cache + Core Data | OkHttp cache + Room |

### Navigation

- **React Navigation**: stack (push/pop), tabs, drawer. Deep linking via universal links.
- **iOS**: NavigationStack (SwiftUI) or UINavigationController (UIKit).
- **Android**: Navigation Compose or Jetpack Navigation.

Deep linking mandatory for shareable features (email, push, SMS).

### Local persistence

- **Small (config, flags, session tokens)**: MMKV (RN), UserDefaults (iOS), DataStore (Android). Always encrypted if contains sensitive data.
- **Structured (entities, transaction list)**: Core Data (iOS), Room (Android), WatermelonDB / Drizzle (RN).
- **Auth tokens**: Keychain (iOS), Keystore (Android) — never in plain storage.

### Offline sync (see `lex-mobile-offline-first`)

Three layers:
1. **Read cache** with TTL (TanStack Query + persister).
2. **Mutations queue** persisted; worker performs sync; exponential retry.
3. **Conflict resolution** strategy declared per entity.

### Networking

- HTTPS 100% of cases; certificate pinning for critical endpoints.
- Explicit timeout (5-10s request; 30s upload).
- Retry with backoff on 5xx and timeout.
- Cancel on unmounted screen (AbortController / Combine cancellables).

### Accessibility

- **iOS**: VoiceOver — labels on all controls; correct traits.
- **Android**: TalkBack — contentDescription; semantics modifier in Compose.
- **React Native**: `accessibilityLabel`, `accessibilityRole`; test with real screen reader.
- **Contrast**: WCAG AA (4.5:1 normal text); Dynamic Type (iOS) and Font Scale (Android) respected.

### Performance

- **Startup time**: < 2s to first interactive screen (cold).
- **Janky animations**: measure with Xcode Instruments, Android Profiler; 60 FPS minimum.
- **Large list**: FlatList (RN) with `keyExtractor`, `getItemLayout`; LazyVStack (SwiftUI); LazyColumn (Compose).
- **Images**: lazy load, cache, modern formats (WebP, HEIF).
- **Bundle size**: proguard/R8 (Android), App Thinning (iOS), bundle splitting (RN).

### Push notifications

- **iOS**: APNs via FCM or direct.
- **Android**: FCM.
- **Unified**: Amazon SNS, OneSignal when multi-platform.

Payload includes `notification_id` for dedup and analytics.

### Observability (per `lex-observability-required`)

- **Crash reporting**: Firebase Crashlytics, Sentry, Bugsnag.
- **Analytics**: structured events (name + props) — same schema iOS and Android (`lex-mobile-platform-parity`).
- **Performance traces**: Firebase Performance, New Relic Mobile.
- **Logs**: structured; without PII; send to backend on critical error.

### Tests

| Level | RN | iOS | Android |
|---|---|---|---|
| Unit | Jest / Vitest | XCTest | JUnit + Kotest |
| Component | React Native Testing Library | ViewInspector (SwiftUI) | Compose UI Testing |
| Integration | Detox | XCUITest | Espresso |
| E2E | Detox, Maestro | XCUITest (simulator/device) | Espresso + UI Automator |
| Snapshot (visual) | Chromatic + RN | iOSSnapshotTestCase | Paparazzi |

`lex-test-pyramid` applies: 70% unit / 20% integration / 10% E2E.

### CI/CD

- **iOS**: Fastlane + Xcode Cloud or Bitrise; TestFlight for beta.
- **Android**: Fastlane + Gradle; Play Console Internal Track for beta.
- **RN/Flutter**: CodePush / EAS Update for hotfix of JS without store review.

### Security

- Secrets never in bundle (`lex-frontend-security` equivalent).
- Jailbreak / root detection in sensitive features (payment).
- App Transport Security (iOS) strict; Network Security Config (Android) without cleartext.
- Biometrics via LocalAuthentication (iOS), BiometricPrompt (Android) for critical auth.

## References

- `lex-mobile-platform-parity`, `lex-mobile-offline-first`
- `lex-frontend-testing`, `lex-frontend-accessibility` — analogous principles
- `codex-frontend-architecture` — parallel in web
- `warrior-iris`
- [React Native Docs](https://reactnative.dev/docs/getting-started)
- [Swift/SwiftUI Docs](https://developer.apple.com/documentation/swiftui)
- [Android/Compose Docs](https://developer.android.com/jetpack/compose/documentation)
