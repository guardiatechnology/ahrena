# Lexis: Minimum Parity Between Mobile Platforms

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Mobile features that must run on iOS and Android — rules of minimum functional parity, not aesthetic parity

## Purpose

Mobile apps that deliver features on iOS before Android (or vice versa) create two distinct user bases with different expectations, multiply platform-specific behavior bugs, and overload the team with "when is it coming to Android?". Minimum functional parity — same feature, same behavior, same version — avoids fragmentation.

**Aesthetic** parity (identical animation, pixel-perfect layout) is another thing: acceptable to diverge respecting iOS Human Interface Guidelines and Android Material Design. Requiring aesthetic parity is fighting against the platform.

This Lexis exists to ensure that **every new mobile feature ships on both platforms in the same release (or justifies deviation)**, that **functional behavior is equal**, and that **aesthetic difference respects native conventions**.

## Law

> **Every new mobile feature MUST enter iOS and Android in the same release (±3 business days). Functional behavior (accepted inputs, states, side effects, errors) MUST be identical between platforms. UI differences MUST follow HIG (iOS) and Material Design (Android) — do not force iOS-look in Android or vice versa. One platform MAY receive the feature first only with an explicit ADR justifying (e.g.: native API unavailable on the other).**

## Rules

### 1. Parity release by default

- If feature is React Native / Flutter / KMM: automatic (single codebase).
- If feature is native split (Swift + Kotlin): sprint planning includes both.
- Release PR checklist: confirms both binaries present.

### 2. Identical functional behavior

Same AC, same test, same response:

- Accepted and rejected inputs: same validation rules.
- States (loading, empty, error): same triggers and semantic messages.
- Side effects (analytics event, push registration, storage): same events with same payloads.
- Errors: same codes, messages may be localized.

### 3. UI follows native convention

Acceptable to diverge:

- Navigation: iOS bottom tab bar / Android bottom nav + FAB when applicable.
- Components: iOS `UIActionSheet` / Android `BottomSheet`; iOS native `UIDatePicker` / Android picker.
- Animations: curves and timings may differ (HIG vs Material).
- Typography: SF Pro vs Roboto (or system).

Not acceptable:
- Force iOS look on Android (`flat` without Material elevation) or vice versa.
- Copy widgets from one platform to the other.

### 4. Deviation requires ADR

One platform shipped first **only with ADR**:
- Reason: native API unavailable (e.g.: iOS App Clips); regulatory approval (e.g.: slower App Store review); beta by channel.
- ADR documents: which platform, expected deadline for parity, target customer of the deviation.
- No ADR = violation; PR blocked.

### 5. Cross-platform telemetry

Analytics events have the same schema in iOS and Android. Dashboards aggregate without transformation. Divergence in event names or fields causes confusion in analysis.

### 6. Parallel deprecations

When a feature is removed:
- Remove on both platforms in the same release.
- Deprecation period (warning to users) identical.

## Applicability

- **Applies to:** mobile apps produced by the project (iOS, Android, React Native, Flutter, KMM).
- **Linked agents:** `warrior-iris`; `warrior-athena` when orchestrating mobile feature.
- **Exceptions:** experimental single-platform apps (explicitly launched as such); PoCs; apps for exclusive niches (e.g.: Apple Watch app without Android equivalent).

## Consequences of Violation

1. **Base fragmentation**: iOS 2 versions ahead; Android users become "second class"; churn.
2. **Chaotic support**: "when does it come out on Android?" tickets dominate channel; team distracted.
3. **Bifurcated bug**: same bug fixed on different platforms with different strategies, without cross review.
4. **Remediation**:
   - Identify current unilateral features; catchup plan.
   - Sprint review checks parity as definition of done.
   - CI integrates build of both; release blocked if one missing.

## Automated Validation

- **Tool:**
  - Release checklist (scripted) verifies that version X exists in both stores.
  - Test mirror: parallel E2E test suite on iOS Simulator + Android Emulator; same test, same assertion.
- **Timing:** Release candidate; definition of done in sprint.
- **Metric:** 100% of features shipped on iOS and Android in the same release (±3 days); ADRs present in all deviations.

## References

- `codex-mobile-architecture`
- `warrior-iris`
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design](https://m3.material.io/)
