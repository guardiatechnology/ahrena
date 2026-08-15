# Ahrena — Catálogo de Lexis

Todas as **39** leis invioláveis do framework Ahrena.

> **Os links** apontam para a versão em inglês em `framework/en/`. Toda Lexis também existe em `framework/pt-BR/` e `framework/es/`.

---

## `_foundation / authoring`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-pilars` | Define os 5 Pilares, suas regras canônicas e a hierarquia de invocação (Lexis → Codex → Katas → Warriors → Cries) | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/authoring/lexis/lex-pilars.md) |

---

## `_foundation / contributing`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-commit-language` | O assunto do commit deve estar em inglês; o corpo pode incluir outros idiomas com a tag `[lang]` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/lexis/lex-commit-language.md) |
| `lex-conventional-commits` | Todo commit deve seguir o formato Conventional Commits `<type>[scope]: <description>` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/lexis/lex-conventional-commits.md) |
| `lex-git-branches` | Nomes de branches devem seguir o formato `{type}/{issue-number}-{kebab-slug}` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/lexis/lex-git-branches.md) |
| `lex-issue-first` | Toda alteração de código deve originar de uma GitHub Issue existente | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/lexis/lex-issue-first.md) |
| `lex-issue-quality` | Toda issue deve usar um template aprovado e responder explicitamente Por Quê / O Quê / Como | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/lexis/lex-issue-quality.md) |
| `lex-semantic-version` | Toda versão de release deve seguir SemVer 2.0 (MAJOR.MINOR.PATCH) | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/lexis/lex-semantic-version.md) |
| `lex-signed-commits` | Todo commit deve ser assinado com uma chave GPG e verificado pelo GitHub | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/lexis/lex-signed-commits.md) |
| `lex-small-commits` | Todo commit deve ser atômico — uma única mudança lógica por commit | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/contributing/lexis/lex-small-commits.md) |

---

## `_foundation / i18n`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-framework-language` | O idioma é o primeiro nível de navegação dentro de `framework/`; todo artefato deve existir em todos os idiomas obrigatórios | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/i18n/lexis/lex-framework-language.md) |

---

## `_foundation / process`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-checkpoint` | Agentes verificam `.checkpoint` antes de iniciar qualquer atividade e o salvam ao concluir | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/process/lexis/lex-checkpoint.md) |
| `lex-directives` | Agentes devem ler `.ahrena/.directives` antes de qualquer atividade que produza artefatos | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/process/lexis/lex-directives.md) |
| `lex-naming` | Artefatos seguem as convenções de nomenclatura definidas em `.ahrena/.directives` (prefixo, casing, endereçamento) | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/process/lexis/lex-naming.md) |
| `lex-platforms-rules` | Toda Lexis e Codex deve ter uma entrada com `description` em `framework/platforms.yaml` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/process/lexis/lex-platforms-rules.md) |

---

## `_foundation / quality`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-observability-required` | Todo novo endpoint, consumidor ou job deve emitir um trace distribuído, métrica de latência e log estruturado com correlation ID | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/quality/lexis/lex-observability-required.md) |
| `lex-template-usage` | Agentes usam o template oficial do Pilar como base estrutural ao criar qualquer novo artefato | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/quality/lexis/lex-template-usage.md) |
| `lex-tone` | Agentes aplicam o tom e estilo de escrita definidos em `.ahrena/.directives` em todos os artefatos e comunicações | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/quality/lexis/lex-tone.md) |

---

## `_foundation / tooling`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-mcp` | Use a ferramenta MCP disponível quando um servidor ativo oferecer a capacidade; credenciais exclusivamente via variáveis de ambiente | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/tooling/lexis/lex-mcp.md) |
| `lex-terminal-type` | Use o tipo de terminal (bash ou PowerShell) definido em `.ahrena/.directives`; inferir pelo SO se não configurado | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/_foundation/tooling/lexis/lex-terminal-type.md) |

---

## `design / brand`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-brand-colors` | Apenas a paleta oficial da Guardia; WCAG 2.1 AA obrigatório; combinação Yellow 500 + White é proibida | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/design/brand/lexis/lex-brand-colors.md) |
| `lex-brand-logo` | Use apenas arquivos oficiais do logo; selecione a variante correta (primária/secundária/mono) com base no fundo | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/design/brand/lexis/lex-brand-logo.md) |
| `lex-brand-typography` | Poppins como tipografia do dia a dia; Lastica exclusiva ao logo; Roboto somente como fallback CSS | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/design/brand/lexis/lex-brand-typography.md) |
| `lex-brand-voice` | Voz direta, estratégica, afirmativa e clara; sem buzzwords; posicionamento é "contabilidade agêntica" | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/design/brand/lexis/lex-brand-voice.md) |

---

## `design / system`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-ai-first-experience` | Toda interface humana da Guardia usa o padrão AI-First: conversa com Isac como superfície primária | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/design/system/lexis/lex-ai-first-experience.md) |
| `lex-design-system-library` | Todas as interfaces consomem componentes de `@guardia/design-system`; reimplementar primitivos é proibido | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/design/system/lexis/lex-design-system-library.md) |

---

## `documentation / i18n`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-language` | Regras de tradução entre idiomas: equivalência estrutural, fidelidade semântica, preservação de elementos técnicos | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/documentation/i18n/lexis/lex-language.md) |
| `lex-language-en` | Regras específicas para tradução para inglês americano — voz, concisão, verbos modais, falsos cognatos | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/documentation/i18n/lexis/lex-language-en.md) |
| `lex-language-es` | Regras específicas para tradução para espanhol neutro — formalidade, falsos cognatos com pt-BR | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/documentation/i18n/lexis/lex-language-es.md) |
| `lex-language-ptbr` | Regras específicas para tradução para português brasileiro — tratamento, anglicismos, tom | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/documentation/i18n/lexis/lex-language-ptbr.md) |

---

## `engineering / backend`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-python-error-handling` | Sem `except` genérico; exceções devem ser específicas; sem dados sensíveis em mensagens de erro | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/backend/python/lexis/lex-python-error-handling.md) |
| `lex-python-immutability` | Dataclasses usam `frozen=True` por padrão; sem argumentos padrão mutáveis em funções | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/backend/python/lexis/lex-python-immutability.md) |
| `lex-python-security` | Sem segredos no código; SQL deve ser parametrizado; toda entrada validada via Pydantic nas fronteiras do sistema | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/backend/python/lexis/lex-python-security.md) |
| `lex-python-testing` | Toda mudança de comportamento tem testes; mocks apenas nas fronteiras do sistema (HTTP, DB, filesystem) | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/backend/python/lexis/lex-python-testing.md) |
| `lex-python-typing` | Type hints completos em todo lugar; mypy strict passa com zero erros; sem `Any` sem comentário justificativo | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/backend/python/lexis/lex-python-typing.md) |

---

## `engineering / data`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-data-retention` | Toda classe de dados tem uma política de retenção declarada em `docs/data-retention.yaml` com enforcement automatizado | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/data/lexis/lex-data-retention.md) |
| `lex-migrations-reversible` | Toda migração de schema é automaticamente reversível ou tem um plano de rollback documentado e testado | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/data/lexis/lex-migrations-reversible.md) |

---

## `engineering / devops`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-aws-cost` | Tags de alocação de custo obrigatórias em todos os recursos AWS; budgets com alertas por ambiente; escolhas >$100/mês documentadas | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/devops/lexis/lex-aws-cost.md) |
| `lex-aws-iac` | Todos os recursos AWS devem ser provisionados via IaC versionada em Git, aplicada por pipeline CI/CD | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/devops/lexis/lex-aws-iac.md) |
| `lex-aws-security` | IAM com menor privilégio; TLS 1.2+ em trânsito; criptografia em repouso; CloudTrail multi-região habilitado | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/devops/lexis/lex-aws-security.md) |

---

## `engineering / frontend`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-frontend-accessibility` | WCAG 2.1 AA mínimo; navegação por teclado; estados ARIA; contraste acessível; cor não é o único indicador de estado | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/frontend/lexis/lex-frontend-accessibility.md) |
| `lex-frontend-security` | Sem `innerHTML` não sanitizado; sem segredos no bundle client; CSP configurado; `rel="noopener"` em links externos | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/frontend/lexis/lex-frontend-security.md) |
| `lex-frontend-testing` | Testes comportamentais do ponto de vista do usuário; queries acessíveis preferidas (`getByRole`); mocks apenas nas fronteiras | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/frontend/lexis/lex-frontend-testing.md) |
| `lex-frontend-typing` | TypeScript `strict: true`; sem `any` implícito ou injustificado; contratos de API tipados por OAS ou schemas Zod | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/frontend/typescript/lexis/lex-frontend-typing.md) |

---

## `engineering / mobile`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-mobile-offline-first` | App opera em 3 estados de rede; UI nunca bloqueia >5s sem alternativa de cancelamento/cache; conflitos de sync têm estratégia declarada | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/mobile/lexis/lex-mobile-offline-first.md) |
| `lex-mobile-platform-parity` | Todo novo recurso mobile é lançado em iOS e Android no mesmo release (±3 dias úteis) | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/mobile/lexis/lex-mobile-platform-parity.md) |

---

## `engineering / platform`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-auth` | Acesso à API controlado por OAuth 2.0: Client Credentials + FAPI 2.0 (público); JWT de IdP confiável (privado) | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/lexis/lex-auth.md) |
| `lex-cloudevents` | Eventos distribuídos seguem a spec CloudEvents; JSON UTF-8; tamanho < 12KB; `idempotencykey` obrigatório | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/lexis/lex-cloudevents.md) |
| `lex-entities` | Entidades persistentes seguem a estrutura base: `entity_id` (UUIDv7), `entity_type`, timestamps, `version` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/lexis/lex-entities.md) |
| `lex-entity-naming` | Valores de `entity_type`, nomes de campos JSON e colunas de DB usam snake_case; camelCase é proibido | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/lexis/lex-entity-naming.md) |
| `lex-error-handling` | Respostas de erro usam estrutura padronizada: array `errors` com `code`, `reason`, `message` | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/lexis/lex-error-handling.md) |
| `lex-idempotency` | Operações que modificam estado são idempotentes; header `Idempotency-Key` obrigatório em POST/PATCH | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/lexis/lex-idempotency.md) |
| `lex-restful-apis` | Endpoints HTTP seguem a spec RESTful da plataforma: status codes, payload, headers, paginação, ordenação | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/platform/lexis/lex-restful-apis.md) |

---

## `engineering / quality`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-test-isolation` | Testes partem de estado conhecido; independentes de ordem; paralelizáveis; testes flaky são tratados como bugs críticos | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/quality/lexis/lex-test-isolation.md) |
| `lex-test-pyramid` | Distribuição de testes ~70% unit / 20% integration / 10% E2E; E2E apenas para jornadas críticas declaradas | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/quality/lexis/lex-test-pyramid.md) |

---

## `engineering / sre`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-runbook-for-every-alert` | Todo alerta que aciona um humano tem um runbook versionado em `docs/runbooks/` vinculado na anotação do alerta | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/sre/lexis/lex-runbook-for-every-alert.md) |
| `lex-slo-required` | Serviços Tier-1/2 têm um SLO declarado antes do primeiro deploy em produção; error budget monitorado em tempo real | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/sre/lexis/lex-slo-required.md) |

---

## `engineering / workflow`

| Artefato | Descrição | Framework |
|---|---|---|
| `lex-issue-driven` | Toda implementação origina de uma issue; passa pelos Gates 1 (Escopo) e 2 (Qualidade); rastreabilidade total AC↔teste | [en](https://github.com/guardiatechnology/ahrena/tree/main/framework/en/engineering/workflow/lexis/lex-issue-driven.md) |
