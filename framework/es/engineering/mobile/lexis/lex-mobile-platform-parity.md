# Lexis: Paridad Mínima entre Plataformas Mobile

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Features mobile que deben correr en iOS y Android — reglas de paridad funcional mínima, no paridad estética

## Propósito

Apps mobile que entregan features en iOS antes que Android (o viceversa) crean dos bases de usuario distintas con expectativas diferentes, multiplican bugs de comportamiento específicos y sobrecargan al equipo con "¿cuándo vendrá para Android?". La paridad funcional mínima — misma feature, mismo comportamiento, misma versión — evita fragmentación.

La paridad **estética** (animación idéntica, layout pixel-perfect) es otra cosa: aceptable divergir respetando las Human Interface Guidelines de iOS y Material Design de Android. Obligar a paridad estética es luchar contra la plataforma.

Esta Lexis existe para garantizar que **toda feature mobile nueva se envíe en ambas plataformas en la misma release (o justifique desviación)**, que **el comportamiento funcional sea igual** y que **la diferencia estética respete convenciones nativas**.

## Ley

> **Toda feature mobile nueva DEBE entrar en iOS y Android en la misma release (±3 días hábiles). El comportamiento funcional (inputs aceptados, estados, efectos colaterales, errors) DEBE ser idéntico entre plataformas. Las diferencias de UI DEBEN seguir HIG (iOS) y Material Design (Android) — no forzar iOS-look en Android o viceversa. Una plataforma PUEDE recibir la feature antes solo con ADR explícito justificando (ej.: API nativa no disponible en otra).**

## Reglas

### 1. Release paritaria por default

- Si la feature es React Native / Flutter / KMM: automático (single codebase).
- Si la feature es native split (Swift + Kotlin): el sprint planning incluye ambos.
- PR de release checklist: confirma ambos binarios presentes.

### 2. Comportamiento funcional idéntico

Mismo AC, misma prueba, misma respuesta:

- Inputs aceptados y rechazados: mismas reglas de validación.
- Estados (loading, empty, error): mismos triggers y mensajes semánticos.
- Side effects (analytics event, push registration, storage): mismos eventos con mismos payloads.
- Errores: mismos códigos, los mensajes pueden estar localizados.

### 3. UI sigue convención nativa

Aceptable divergir:

- Navegación: iOS tab bar inferior / Android bottom nav + FAB cuando aplique.
- Componentes: iOS `UIActionSheet` / Android `BottomSheet`; iOS `UIDatePicker` nativo / Android picker.
- Animaciones: curvas y timings pueden diferir (HIG vs Material).
- Tipografía: SF Pro vs Roboto (o system).

No aceptable:
- Forzar look iOS en Android (`flat` sin Material elevation) o viceversa.
- Copiar widgets de una plataforma en la otra.

### 4. Desviación exige ADR

Una plataforma ship antes **solo con ADR**:
- Motivo: API nativa no disponible (ej.: App Clips iOS); aprobación regulatoria (ej.: App Store review más lento); beta por canal.
- El ADR documenta: qué plataforma, plazo esperado para paridad, cliente objetivo de la desviación.
- Sin ADR = violación; PR bloqueado.

### 5. Telemetría cross-platform

Los analytics events tienen el mismo schema en iOS y Android. Los dashboards agregan sin transformación. La divergencia en nombres o campos de evento causa confusión en análisis.

### 6. Deprecations en paralelo

Cuando una feature es removida:
- Remover en ambas plataformas en la misma release.
- Período de deprecation (warning a los usuarios) idéntico.

## Alcance

- **Aplica a:** apps mobile producidos por el proyecto (iOS, Android, React Native, Flutter, KMM).
- **Agentes vinculados:** `warrior-iris`; `warrior-athena` cuando orquesta feature mobile.
- **Excepciones:** apps experimentales single-platform (explícitamente lanzados como tal); PoCs; apps para nichos exclusivos (ej.: Apple Watch app sin equivalente Android).

## Consecuencias de Violación

1. **Fragmentación de base**: iOS 2 versiones adelante; Android users se vuelven "segunda clase"; churn.
2. **Soporte caótico**: tickets "¿cuándo sale en Android?" dominan el canal; equipo distraído.
3. **Bug bifurcado**: el mismo bug se corrige en plataformas diferentes, con estrategias diferentes, sin review cruzado.
4. **Remediación**:
   - Identificar features unilaterales actuales; plan de catchup.
   - Sprint review verifica paridad como definition of done.
   - CI integra build de ambas; release bloqueada si falta una.

## Validación Automatizada

- **Herramienta:**
  - Release checklist (scripted) verifica que la versión X exista en ambas stores.
  - Test mirror: suite de pruebas E2E paralela en iOS Simulator + Android Emulator; misma prueba, misma assertion.
- **Momento:** Release candidate; definition of done en sprint.
- **Métrica:** 100% de features shipped en iOS y Android en la misma release (±3 días); ADRs presentes en todas las desviaciones.

## Referencias

- `codex-mobile-architecture`
- `warrior-iris`
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design](https://m3.material.io/)
