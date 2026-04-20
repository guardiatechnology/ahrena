# Kata: Implement Mobile Feature

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Mobile feature implementation on iOS and Android (parity), with offline-first, accessibility, tests, and observability

## Objective

Given a feature with requirements (numbered ACs) and architectural design, produce a complete mobile implementation on iOS and Android (or single codebase RN/Flutter) with: functional parity, offline-first (cache + queue), accessibility, tests at three levels (unit, integration, E2E), observability (crash + analytics + performance), and release prepared for TestFlight + Play Console Internal Track.

## When to Use

- New mobile feature or significant evolution
- Invoked by `warrior-iris` directly or via delegation of `warrior-athena` in Phase 4 when target includes mobile

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Description + ACs | Yes | Numbered functional requirements |
| API contract | No | Backend OAS (produced by Daedalus) |
| Design | No | Figma, wireframes, mocks |
| Target stack | Yes | React Native / Flutter / Native / Mixed |

## Workflow

```
Progress:
- [ ] 1. Clarify requirements (includes offline behavior)
- [ ] 2. Consult codebase patterns and design system
- [ ] 3. Define offline strategy per feature
- [ ] 4. Implement layers (service, hook, screen, component)
- [ ] 5. Cover accessibility (VoiceOver + TalkBack)
- [ ] 6. Write tests (unit + integration + E2E)
- [ ] 7. Add telemetry (crash, analytics, performance)
- [ ] 8. Build and smoke test on iOS + Android
- [ ] 9. Prepare release notes and parity checklist
```

### Step 1: Clarify requirements

Batch questions (up to 5 per round):

1. **Offline**: what behavior in flight mode? Cache allowed?
2. **Parity**: simultaneous iOS and Android release? (assume yes, deviations need ADR)
3. **Authentication**: does feature require logged-in user? biometrics?
4. **Push notifications**: does feature send? receive?
5. **Deep link**: does feature have a shareable URL?

### Step 2: Consult codebase and design system

- Identify structure pattern (`features/` vs. folders per screen).
- Use existing UI kit (don't invent a new `<Button>`).
- Respect design tokens (colors, spacing, typography).

### Step 3: Offline strategy

For each action:

| Action | Behavior |
|---|---|
| Reading data from server | Cache with TTL; serve cache on open; refetch in background |
| Creation/editing | Optimistic + local queue + sync |
| Destructive action without network | Queue but make it explicit to user |

Document decision per screen or feature.

### Step 4: Implement layers

Following `codex-mobile-architecture`:

1. **Service** (API client + local storage): typed contracts, cache, queue.
2. **Hook / ViewModel**: state logic, service calls.
3. **Screen**: composition of components; lifecycle; navigation.
4. **Components**: reusable, without business logic.

Incremental: start with service (testable), then hook, then UI.

### Step 5: Accessibility

For each control:

- **Label** (VoiceOver + TalkBack announce).
- **Role** correct (button, link, heading).
- **State** exposed (disabled, selected, expanded).
- **Hints** when action is not obvious.
- **Focus order** logical.

Test with real screen reader before considering it done.

### Step 6: Tests

According to `codex-mobile-architecture`:

- **Unit**: pure hooks, utilities, reducers.
- **Component**: rendering, basic interaction.
- **Integration**: complete flow with API mock (MSW or fixture).
- **E2E**: 1-2 critical feature journeys (Detox, Maestro, XCUITest).

Each test marks corresponding AC (`AC-N` convention).

### Step 7: Telemetry

- **Crash**: does feature involve new code that can crash? — already covered by SDK (Crashlytics/Sentry).
- **Analytics**: success/failure events of key actions; unified schema iOS + Android.
- **Performance**: trace on network calls and heavy operations.
- **Logs**: without PII, structured.

### Step 8: Build + smoke test

- Release build on iOS (Xcode, `.ipa`) and Android (`.aab`).
- Install on real device (at least one of each platform).
- Smoke test: happy case + offline scenario + quick accessibility.
- Screenshots for release notes.

### Step 9: Release notes + parity checklist

- Notes per platform in the app's language (pt-BR).
- Checklist (`lex-mobile-platform-parity`):
  - [ ] iOS build submitted TestFlight
  - [ ] Android build submitted Play Console Internal
  - [ ] Feature compared side-by-side; identical behavior
  - [ ] Analytics events present in both
  - [ ] Deep link tested in both (if applicable)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Feature code | files per stack | `src/features/{feature}/` |
| Tests | per stack | alongside or in `__tests__/` |
| Release builds | `.ipa` + `.aab` | TestFlight + Play Console Internal |
| Release notes | Markdown | `docs/releases/vX.Y.Z.md` |
| Parity checklist | Markdown | In the PR |

## Restrictions

- **Mandatory parity**: ship on both platforms in the same release or ADR justifying.
- **Offline-first**: every feature has defined behavior in 3 network states.
- **Accessibility is not optional**: VoiceOver + TalkBack work before ship.
- **Tests cover ACs**: `AC-N` traceability.

## References

- `lex-mobile-platform-parity`, `lex-mobile-offline-first`
- `codex-mobile-architecture`
- `lex-frontend-accessibility` — transverse a11y principles
- `warrior-iris`
