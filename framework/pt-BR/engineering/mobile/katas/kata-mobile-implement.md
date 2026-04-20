# Kata: Implementar Feature Mobile

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Implementação de feature mobile em iOS e Android (paridade), com offline-first, acessibilidade, testes e observabilidade

## Objetivo

Dada feature com requisitos (ACs numerados) e desenho arquitetural, produzir implementação mobile completa em iOS e Android (ou single codebase RN/Flutter) com: paridade funcional, offline-first (cache + queue), acessibilidade, testes em três níveis (unit, integration, E2E), observabilidade (crash + analytics + performance), e release preparada para TestFlight + Play Console Internal Track.

## Quando Usar

- Feature mobile nova ou evolução significativa
- Invocada por `warrior-iris` diretamente ou via delegação de `warrior-athena` na Fase 4 quando target inclui mobile

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Descrição + ACs | Sim | Requisitos funcionais numerados |
| Contrato de API | Não | OAS do backend (produzido por Daedalus) |
| Design | Não | Figma, wireframes, mocks |
| Stack alvo | Sim | React Native / Flutter / Native / Mixed |

## Workflow

```
Progresso:
- [ ] 1. Clarificar requisitos (inclui comportamento offline)
- [ ] 2. Consultar padrões do codebase e design system
- [ ] 3. Definir estratégia offline por feature
- [ ] 4. Implementar camadas (service, hook, screen, component)
- [ ] 5. Cobrir acessibilidade (VoiceOver + TalkBack)
- [ ] 6. Escrever testes (unit + integration + E2E)
- [ ] 7. Adicionar telemetria (crash, analytics, performance)
- [ ] 8. Build e smoke test em iOS + Android
- [ ] 9. Preparar release notes e checklist de paridade
```

### Passo 1: Clarificar requisitos

Perguntas em lote (até 5 por rodada):

1. **Offline**: qual comportamento em flight mode? Cache permitido?
2. **Paridade**: release iOS e Android simultâneo? (assumir sim, desvios precisam ADR)
3. **Autenticação**: feature exige user logado? biometria?
4. **Push notifications**: feature envia? recebe?
5. **Deep link**: feature tem URL compartilhável?

### Passo 2: Consultar codebase e design system

- Identificar padrão de estrutura (`features/` vs. folders por tela).
- Usar UI kit existente (não inventar `<Button>` novo).
- Respeitar tokens de design (cores, espaçamento, tipografia).

### Passo 3: Estratégia offline

Para cada ação:

| Ação | Comportamento |
|---|---|
| Leitura de dados do servidor | Cache com TTL; servir cache ao abrir; refetch em background |
| Criação/edição | Otimista + queue local + sync |
| Ação destrutiva sem rede | Enfileirar mas deixar explícito ao usuário |

Documentar decisão por tela ou feature.

### Passo 4: Implementar camadas

Seguindo `codex-mobile-architecture`:

1. **Service** (API client + local storage): contratos tipados, cache, queue.
2. **Hook / ViewModel**: lógica de estado, chamadas ao service.
3. **Screen**: composição de components; lifecycle; navegação.
4. **Components**: reutilizáveis, sem lógica de negócio.

Incremental: começar pelo service (testable), depois hook, depois UI.

### Passo 5: Acessibilidade

Para cada controle:

- **Label** (VoiceOver + TalkBack anunciam).
- **Role** correto (button, link, heading).
- **State** exposto (disabled, selected, expanded).
- **Hints** quando ação não óbvia.
- **Ordem de foco** lógica.

Testar com leitor de tela real antes de considerar pronto.

### Passo 6: Testes

Conforme `codex-mobile-architecture`:

- **Unit**: hooks puros, utilities, reducers.
- **Component**: renderização, interação básica.
- **Integration**: flow completo com mock de API (MSW ou fixture).
- **E2E**: 1-2 jornadas críticas da feature (Detox, Maestro, XCUITest).

Cada teste marca AC correspondente (`AC-N` convenção).

### Passo 7: Telemetria

- **Crash**: feature envolve código novo que pode crashar? — já coberto pelo SDK (Crashlytics/Sentry).
- **Analytics**: eventos de sucesso/falha de ações chave; schema unificada iOS + Android.
- **Performance**: trace em chamadas de rede e operações pesadas.
- **Logs**: sem PII, estruturados.

### Passo 8: Build + smoke test

- Build release em iOS (Xcode, `.ipa`) e Android (`.aab`).
- Instalar em device real (pelo menos um de cada platform).
- Smoke test: caso feliz + cenário offline + acessibilidade rápida.
- Screenshots para release notes.

### Passo 9: Release notes + checklist paridade

- Notes por plataforma na linguagem do app (pt-BR).
- Checklist (`lex-mobile-platform-parity`):
  - [ ] iOS build submetido TestFlight
  - [ ] Android build submetido Play Console Internal
  - [ ] Feature comparada lado-a-lado; comportamento idêntico
  - [ ] Analytics events presentes em ambos
  - [ ] Deep link testado em ambos (se aplicável)

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Código feature | arquivos conforme stack | `src/features/{feature}/` |
| Testes | conforme stack | ao lado ou em `__tests__/` |
| Builds release | `.ipa` + `.aab` | TestFlight + Play Console Internal |
| Release notes | Markdown | `docs/releases/vX.Y.Z.md` |
| Checklist paridade | Markdown | No PR |

## Restrições

- **Paridade obrigatória**: ship em ambas as plataformas na mesma release ou ADR justificando.
- **Offline-first**: toda feature tem comportamento definido em 3 estados de rede.
- **Acessibilidade não é opcional**: VoiceOver + TalkBack funcionam antes do ship.
- **Testes cobrem ACs**: rastreabilidade `AC-N`.

## Referências

- `lex-mobile-platform-parity`, `lex-mobile-offline-first`
- `codex-mobile-architecture`
- `lex-frontend-accessibility` — princípios de a11y transversais
- `warrior-iris`
