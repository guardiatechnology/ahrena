# Codex: Arquitetura Mobile

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Padrões arquiteturais para apps mobile (React Native, Flutter, Swift/SwiftUI, Kotlin/Compose) — estrutura, state management, persistência local, sync, navegação, testes

## Conteúdo

### Escolha de stack

| Stack | Quando preferir | Custos |
|---|---|---|
| **React Native** | Time fluente em TS/React; code sharing com web; features padrão mobile | Performance em animações pesadas; integração com APIs novas do OS atrasa |
| **Flutter** | Multi-platform (iOS, Android, web, desktop); UI complexa com controle total | Curva de Dart; bundle maior; acessibilidade requer atenção extra |
| **Native (Swift + Kotlin)** | Performance crítica; uso extensivo de APIs nativas (ARKit, Health, etc.); 2 times | Duplicação de esforço; paridade funcional exige disciplina |
| **Kotlin Multiplatform (KMM)** | Lógica compartilhada (domain, networking) + UI nativa | Tooling ainda em maturação; times experientes em ambos |

Guardia default: **React Native** para apps cliente gerais; **native** apenas quando feature justifica.

### Estrutura de diretórios (React Native)

```
src/
├── app/                    # Entry point, providers globais
├── features/               # Features isoladas (~ frontend-architecture)
│   └── refund/
│       ├── screens/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       └── index.ts
├── components/             # UI kit reutilizável
├── navigation/             # React Navigation stack/tabs
├── hooks/                  # Hooks globais
├── services/               # API client, storage, analytics
├── state/                  # Global state (Zustand, Redux Toolkit)
├── i18n/                   # Localização
├── theme/                  # Tokens de design
└── types/                  # Tipos compartilhados
```

Nativo Swift/Kotlin segue convenção da plataforma (Xcode projeto; Gradle modules por feature).

### State management

| Tipo | Ferramenta React Native | Nativo iOS | Nativo Android |
|---|---|---|---|
| Server state | TanStack Query, SWR | Combine + URLSession | Flow + Retrofit |
| Client global | Zustand, Jotai, Redux Toolkit | SwiftUI @StateObject / EnvironmentObject | Compose ViewModel |
| Form | react-hook-form | Composable form state | Compose State |
| Persistente local | MMKV, AsyncStorage + encryption | Core Data, SwiftData | Room, DataStore |
| Cache offline | TanStack Query + persister | URLSession cache + Core Data | OkHttp cache + Room |

### Navegação

- **React Navigation**: stack (push/pop), tabs, drawer. Deep linking via universal links.
- **iOS**: NavigationStack (SwiftUI) ou UINavigationController (UIKit).
- **Android**: Navigation Compose ou Jetpack Navigation.

Deep linking obrigatório para features compartilháveis (email, push, SMS).

### Persistência local

- **Pequeno (config, flags, session tokens)**: MMKV (RN), UserDefaults (iOS), DataStore (Android). Sempre criptografado se contém dados sensíveis.
- **Estruturado (entidades, lista de transações)**: Core Data (iOS), Room (Android), WatermelonDB / Drizzle (RN).
- **Tokens de auth**: Keychain (iOS), Keystore (Android) — nunca em plain storage.

### Sync offline (ver `lex-mobile-offline-first`)

Três camadas:
1. **Cache de leitura** com TTL (TanStack Query + persister).
2. **Queue de mutations** persistida; worker faz sync; retry exponencial.
3. **Conflict resolution** estratégia declarada por entidade.

### Networking

- HTTPS 100% dos casos; certificate pinning para endpoints críticos.
- Timeout explícito (5-10s request; 30s upload).
- Retry com backoff em 5xx e timeout.
- Cancel em tela desmontada (AbortController / Combine cancellables).

### Acessibilidade

- **iOS**: VoiceOver — labels em todos controles; traits corretos.
- **Android**: TalkBack — contentDescription; semantics modifier em Compose.
- **React Native**: `accessibilityLabel`, `accessibilityRole`; testar com screen reader real.
- **Contraste**: WCAG AA (4.5:1 texto normal); Dynamic Type (iOS) e Font Scale (Android) respeitados.

### Performance

- **Startup time**: < 2s até primeira tela interativa (cold).
- **Janky animations**: medir com Xcode Instruments, Android Profiler; 60 FPS mínimo.
- **Lista grande**: FlatList (RN) com `keyExtractor`, `getItemLayout`; LazyVStack (SwiftUI); LazyColumn (Compose).
- **Imagens**: lazy load, cache, formatos modernos (WebP, HEIF).
- **Bundle size**: proguard/R8 (Android), App Thinning (iOS), bundle splitting (RN).

### Push notifications

- **iOS**: APNs via FCM ou direto.
- **Android**: FCM.
- **Unificado**: Amazon SNS, OneSignal quando multi-platform.

Payload inclui `notification_id` para dedup e analytics.

### Observabilidade (conforme `lex-observability-required`)

- **Crash reporting**: Firebase Crashlytics, Sentry, Bugsnag.
- **Analytics**: eventos estruturados (nome + props) — mesma schema iOS e Android (`lex-mobile-platform-parity`).
- **Performance traces**: Firebase Performance, New Relic Mobile.
- **Logs**: estruturados; sem PII; enviar para backend em erro crítico.

### Testes

| Nível | RN | iOS | Android |
|---|---|---|---|
| Unit | Jest / Vitest | XCTest | JUnit + Kotest |
| Component | React Native Testing Library | ViewInspector (SwiftUI) | Compose UI Testing |
| Integration | Detox | XCUITest | Espresso |
| E2E | Detox, Maestro | XCUITest (simulator/device) | Espresso + UI Automator |
| Snapshot (visual) | Chromatic + RN | iOSSnapshotTestCase | Paparazzi |

`lex-test-pyramid` aplica: 70% unit / 20% integration / 10% E2E.

### CI/CD

- **iOS**: Fastlane + Xcode Cloud ou Bitrise; TestFlight para beta.
- **Android**: Fastlane + Gradle; Play Console Internal Track para beta.
- **RN/Flutter**: CodePush / EAS Update para hotfix de JS sem review da store.

### Segurança

- Secrets nunca em bundle (`lex-frontend-security` equivalente).
- Jailbreak / root detection em features sensíveis (pagamento).
- App Transport Security (iOS) strict; Network Security Config (Android) sem cleartext.
- Biometria via LocalAuthentication (iOS), BiometricPrompt (Android) para auth crítica.
