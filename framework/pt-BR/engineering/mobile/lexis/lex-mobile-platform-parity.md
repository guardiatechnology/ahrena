# Lexis: Paridade Mínima entre Plataformas Mobile

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Features mobile que devem rodar em iOS e Android — regras de paridade funcional mínima, não paridade estética

## Propósito

Apps mobile que entregam features em iOS antes de Android (ou vice-versa) criam duas bases de usuário distintas com expectativas diferentes, multiplicam bugs de comportamento específicos e sobrecarregam o time com "quando vai vir para Android?". A paridade funcional mínima — mesma feature, mesmo comportamento, mesma versão — evita fragmentação.

Paridade **estética** (animação idêntica, layout pixel-perfect) é outra coisa: aceitável divergir respeitando Human Interface Guidelines do iOS e Material Design do Android. Obrigar paridade estética é lutar contra a plataforma.

Esta Lexis existe para garantir que **toda feature mobile novo envie em ambas as plataformas na mesma release (ou justifique desvio)**, que **comportamento funcional seja igual** e que **diferença estética respeite convenções nativas**.

## Lei

> **Toda feature mobile nova DEVE entrar em iOS e Android na mesma release (±3 dias úteis). Comportamento funcional (inputs aceitos, estados, efeitos colaterais, errors) DEVE ser idêntico entre plataformas. Diferenças de UI DEVEM seguir HIG (iOS) e Material Design (Android) — não forçar iOS-look em Android ou vice-versa. Uma plataforma PODE receber a feature antes apenas com ADR explícito justificando (ex.: API nativa indisponível em outra).**

## Regras

### 1. Release paritária por default

- Se feature é React Native / Flutter / KMM: automático (single codebase).
- Se feature é native split (Swift + Kotlin): sprint planning inclui ambos.
- PR de release checklist: confirma ambos os binários presentes.

### 2. Comportamento funcional idêntico

Mesmo AC, mesmo teste, mesma resposta:

- Inputs aceitos e rejeitados: mesmas regras de validação.
- Estados (loading, empty, error): mesmos triggers e mensagens semânticas.
- Side effects (analytics event, push registration, storage): mesmos eventos com mesmos payloads.
- Erros: mesmos códigos, mensagens podem ser localizadas.

### 3. UI segue convenção nativa

Aceitável divergir:

- Navegação: iOS tab bar inferior / Android bottom nav + FAB quando aplicável.
- Componentes: iOS `UIActionSheet` / Android `BottomSheet`; iOS `UIDatePicker` nativo / Android picker.
- Animações: curvas e timings podem diferir (HIG vs Material).
- Tipografia: SF Pro vs Roboto (ou system).

Não aceitável:
- Forçar look iOS em Android (`flat` sem Material elevation) ou vice-versa.
- Copiar widgets de uma plataforma na outra.

### 4. Desvio exige ADR

Uma plataforma ship antes **só com ADR**:
- Motivo: API nativa indisponível (ex.: App Clips iOS); aprovação regulatória (ex.: App Store review mais lento); beta por canal.
- ADR documenta: qual plataforma, prazo esperado para paridade, cliente-alvo do desvio.
- Sem ADR = violação; PR bloqueado.

### 5. Telemetria cross-platform

Analytics events têm mesma schema em iOS e Android. Dashboards agregam sem transformação. Divergência em nomes ou campos de evento causa confusão em análise.

### 6. Depreciações em paralelo

Quando uma feature é removida:
- Remover em ambas as plataformas na mesma release.
- Período de deprecation (warning aos usuários) idêntico.

## Abrangência

- **Aplica-se a:** apps mobile produzidos pelo projeto (iOS, Android, React Native, Flutter, KMM).
- **Agentes vinculados:** `warrior-iris`; `warrior-athena` quando orquestra feature mobile.
- **Exceções:** apps experimentais single-platform (explicitamente lançados como tal); PoCs; apps para nichos exclusivos (ex.: Apple Watch app sem equivalente Android).

## Consequências de Violação

1. **Fragmentação de base**: iOS 2 versões à frente; Android users viram "segunda classe"; churn.
2. **Suporte caótico**: tickets "quando sai no Android?" dominam canal; time distraído.
3. **Bug bifurcado**: mesmo bug corrige em plataforma diferentes, com estratégias diferentes, sem review cruzado.
4. **Remediação**:
   - Identificar features unilaterais atuais; plano de catchup.
   - Sprint review verifica paridade como definition of done.
   - CI integra build de ambas; release bloqueada se falta uma.

## Validação Automatizada

- **Ferramenta:**
  - Release checklist (scripted) verifica que versão X existe em ambas as stores.
  - Test mirror: suite de testes E2E paralela em iOS Simulator + Android Emulator; mesmo teste, mesma assertion.
- **Momento:** Release candidate; definition of done em sprint.
- **Métrica:** 100% de features shipped em iOS e Android na mesma release (±3 dias); ADRs presentes em todos os desvios.

## Referências

- `codex-mobile-architecture`
- `warrior-iris`
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design](https://m3.material.io/)
