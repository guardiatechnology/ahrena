---
plan_id: "019"
title: "static-validator-consolidated"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-07T22:30:00Z"
updated_at: "2026-05-07T22:30:00Z"
---

# Plano: Validador estático consolidado em CI (`scripts/validate.py`)

## Objetivo

Consolidar em **um único script Python** (`scripts/validate.py`) todas as verificações estáticas que hoje rodam dispersas (parte em `scripts/install.py`, parte em revisão humana, parte ignorada). Plugá-lo em GitHub Actions como gate obrigatório de PR. Ataca dívida operacional acumulada: frontmatter inválido em Lexis/Codex, traduções incompletas em `language.i18n`, registro ausente em `platforms.yaml`, cross-refs quebrados, prefixes de Pilar incorretos, descrições de skill/rule com leak de exemplo (Gemini bot já apontou múltiplos casos). Regressão zero — script retorna não-zero apenas para problemas que hoje seriam detectados por revisão humana cuidadosa.

## Contexto

### Estado atual

- `scripts/install.py` valida algumas coisas (existência de paths, geração de frontmatter `.mdc`)
- `lex-template-usage`, `lex-platforms-rules`, `lex-framework-language`, `lex-naming` codificam regras mas **enforcement é manual** (revisão humana de PR)
- Bot `gemini-code-assist` apanhou em PR #47 três casos de "leak de exemplo" em SKILL.md — sintomático de gap de validação automatizada
- Sem CI gate, regras viram convenção opcional; com gate, viram contrato

### Categorias de validação a consolidar

| Categoria | O que valida | Lex/Codex de referência | Detectável hoje? |
|---|---|---|---|
| **Frontmatter** | Lexis/Codex/Kata/Warrior/Cry com frontmatter válido (campos obrigatórios, valores válidos, `description` curta sem leak de exemplo, `name`, `globs` quando aplicável) | `lex-template-usage` § 5 | Não (manual) |
| **Tradução completa** | Cada artefato em `framework/{lang}/...` existe em todas as línguas listadas em `language.i18n` | `lex-framework-language` rule 2 | Não |
| **Estrutura de path** | Todo artefato segue `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.{ext}` | `lex-naming` rule 4, `lex-framework-language` rule 1 | Não |
| **Prefix correto** | Lexis com `lex-`, Codex com `codex-`, etc. (lookup em `naming.prefixes`) | `lex-naming` rule 1 | Não |
| **Casing** | Files e directories em kebab-case (lookup em `naming.casing`) | `lex-naming` rule 3 | Não |
| **Registro em platforms.yaml** | Cada Lex e Codex tem entry em `cursor.rules` ou `claude-code.rules`/`docs` com pelo menos `description` | `lex-platforms-rules` | Parcial (install.py reclama mas não bloqueia) |
| **Cross-refs** | Referências `lex-X`, `codex-X`, `kata-X`, `warrior-X`, `cry-X` em corpo de artefatos apontam para artefatos existentes | (implícito) | Não |
| **Sample text leak** | `description` em `.mdc` não contém nome de entity/file específico (leak de execução prévia) | (gap detectado pela bot Gemini em PR #47) | Não |
| **HARD-GATE em Lex bloqueante** | Lex que descreve bloqueio efetivo tem bloco `<HARD-GATE>` literal | `lex-hard-gate-pattern` | Não |
| **Allow-list cumprida em decorator Lexis** | `lex-logging-decorator` (e futuras `lex-metrics/idempotency/resilience/transactional-decorator`) têm allow-list em `pyproject.toml` declarada — apenas check de existência da diretiva | `lex-logging-decorator` § validation | Não |

### Decisões fechadas

| Decisão | Valor | Por quê |
|---|---|---|
| Linguagem do script | Python 3.10+ (já usado em `scripts/install.py`) | Continuidade |
| Empacotamento | Standalone `scripts/validate.py` + módulos auxiliares em `scripts/_validate/` | Manutenibilidade |
| Output | Texto colorido para humano + `--format=json` para CI parsing | Cobre dois consumidores |
| Severidades | `error` (bloqueia) e `warning` (avisa, não bloqueia) | Adoção gradual: novas regras entram primeiro como warning |
| CI integration | GitHub Actions workflow `validate-framework.yml` rodando em `pull_request` | Gate obrigatório via Branch Protection (já configurado) |
| Local invocation | `python3 scripts/validate.py [path...]` | Roda offline antes do push |
| Pre-commit | Opcional; instala via `pre-commit-config.yaml` se projeto quiser | Não obrigatório (rodar no CI já basta) |
| Performance budget | < 10s para validar todo o framework | Roda em cada PR |
| Categorias ativas no merge inicial | Frontmatter, prefix, casing, path structure, registro em `platforms.yaml`, sample text leak | Esses são os mais fáceis e mais óbvios primeiro |
| Categorias em warning-only inicial | Tradução completa, cross-refs, HARD-GATE | Existem regressões legacy; promove para `error` em PR de cleanup |
| Estende `install.py` ou substitui? | **Estende** — `install.py` continua dono de geração; `validate.py` foca em validação | Separação de responsabilidades |
| Test suite | Pytest com fixtures de framework "saudável" e "quebrado" | Garante que regras funcionam |

## Escopo

### Artefatos a criar

| Caminho | Conteúdo |
|---|---|
| `scripts/validate.py` | Entrypoint CLI; argparse com `--format`, `--severity`, `--paths`; orquestra os módulos `_validate/*` |
| `scripts/_validate/__init__.py` | Pacote |
| `scripts/_validate/frontmatter.py` | Validação de frontmatter Lexis/Codex/Kata/Warrior/Cry |
| `scripts/_validate/translation.py` | Comparação de paths entre línguas |
| `scripts/_validate/path_structure.py` | Validação `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.{ext}` |
| `scripts/_validate/naming.py` | Prefix + casing |
| `scripts/_validate/platforms_yaml.py` | Cross-check com `framework/platforms.yaml` |
| `scripts/_validate/cross_refs.py` | Resolve `lex-X` / `codex-X` etc. no corpo |
| `scripts/_validate/sample_leak.py` | Heurística de leak: nomes específicos em descriptions (anti-padrão da PR #47) |
| `scripts/_validate/hard_gate.py` | Procura `<HARD-GATE>` em Lexis bloqueantes |
| `scripts/_validate/decorator_directives.py` | Verifica que cada `lex-*-decorator` tem diretiva `ahrena.{x}.allowed_modules` no `.directives.sample` |
| `tests/validate/test_frontmatter.py` | Testes unitários por categoria |
| `tests/validate/test_translation.py` | etc. |
| `tests/validate/fixtures/` | Framework sandbox saudável/quebrado |
| `.github/workflows/validate-framework.yml` | CI workflow |
| `docs/internal/validator-rules.md` | Documentação interna (pt-BR) listando cada regra, severidade e como corrigir |

### Atualizações em artefatos existentes

| Arquivo | Mudança |
|---|---|
| `scripts/install.py` | Acrescentar nota: "validação completa em `validate.py`" — install.py continua focado em geração |
| `Makefile` | Adicionar target `make validate` que invoca `scripts/validate.py` |
| `framework/.directives.sample` | Adicionar bloco comentado `validation.severity_overrides` permitindo projeto downgradear regras específicas para warning (escape hatch para legacy) |
| `lex-template-usage`, `lex-platforms-rules`, `lex-framework-language`, `lex-naming` | Acrescentar nota em cada "Automated Validation" apontando para `scripts/validate.py` como ferramenta canônica |

## Fora de escopo

- **Lint de código aplicação** (Ruff, ESLint, mypy) — fora; `validate.py` é só para artefatos do framework
- **Auto-fix** de problemas detectados — script só relata; correção é manual ou em iteração futura
- **Validação de qualidade de tradução** (semantic equivalence entre línguas) — fora; só checa estrutura
- **Validação de SLAs ou métricas de produção** — fora; CI-only; runtime fica com `lex-observability-required`
- **Migração de validação existente em `install.py`** — `install.py` mantém o que faz; `validate.py` adiciona, não substitui

## Steps

- [ ] 1. Abrir issue com template `feature-request`, Issue Type `Feature`, label `ci 🏗️`, título "feat(scripts): consolidated static validator (validate.py) + CI workflow"
- [ ] 2. Criar branch `feat/{N}-static-validator` e worktree
- [ ] 3. Atualizar status deste plan para `in-progress`
- [ ] 4. Esboçar arquitetura em `scripts/_validate/__init__.py` (interface comum: cada módulo expõe `validate(framework_path, config) -> list[Finding]`)
- [ ] 5. Implementar `frontmatter.py` + tests
- [ ] 6. Implementar `translation.py` + tests
- [ ] 7. Implementar `path_structure.py` + tests
- [ ] 8. Implementar `naming.py` + tests
- [ ] 9. Implementar `platforms_yaml.py` + tests
- [ ] 10. Implementar `cross_refs.py` + tests
- [ ] 11. Implementar `sample_leak.py` + tests (regex contra nomes específicos comuns: `Entity:`, `lex-`, `kata-`, `feat/`, etc., dentro de field `description`)
- [ ] 12. Implementar `hard_gate.py` + tests
- [ ] 13. Implementar `decorator_directives.py` + tests
- [ ] 14. Escrever entrypoint `validate.py` orquestrando todos
- [ ] 15. Rodar `validate.py` no framework atual; coletar findings; categorizar em "fix agora" vs "warning-only legacy"
- [ ] 16. Corrigir os findings de severidade `error` que aparecerem no estado atual (cleanup de dívida acumulada — pode virar sub-PRs separados)
- [ ] 17. Adicionar bloco `validation.severity_overrides` em `framework/.directives.sample`
- [ ] 18. Adicionar nota em "Automated Validation" das 4 Lexis listadas
- [ ] 19. Adicionar target `validate` no `Makefile`
- [ ] 20. Adicionar comentário em `scripts/install.py` apontando para `validate.py`
- [ ] 21. Criar `.github/workflows/validate-framework.yml`: roda em `pull_request`, instala Python 3.11, executa `validate.py --format=json`, falha se houver `error`
- [ ] 22. Redigir `docs/internal/validator-rules.md` (pt-BR) com lista canônica de regras
- [ ] 23. **Smoke test local**: rodar `make validate` no estado limpo do main; deve passar (ou listar warnings esperadas)
- [ ] 24. **Smoke test CI**: abrir PR de teste com violação proposital (e.g., novo Lex sem entry em `platforms.yaml`); verificar que CI bloqueia
- [ ] 25. Commits atômicos por módulo (`_validate/frontmatter.py` + tests = 1 commit, etc.); 1 commit final para workflow + Makefile
- [ ] 26. Push e abrir PR via `kata-contributing-pr`
- [ ] 27. Após merge: arquivar plan e remover worktree

## Dependências

- Python 3.10+ no ambiente (já requirement do `install.py`)
- `pyyaml` para parsing de `platforms.yaml` (já dependência indireta)
- `gh` CLI para gh-actions sanity check (opcional)
- **Independente** de todos os outros plans — pode rodar em qualquer ordem
- **Sinérgico** com plan-020 (ADR automation) — plan-020 adiciona regra ao mesmo `validate.py`

## Riscos

- **Findings legacy bloqueiam CI imediatamente após merge.** Mitigação: cleanup pré-merge (step 16); regras novas começam em `warning-only` até cleanup completo
- **Performance > 10s no framework grande.** Mitigação: budget orçamento de 10s no step 23; se exceder, paralelizar por módulo (multiprocessing)
- **Falsos positivos no sample-leak detector** (e.g., `description: "Configure GPG signing"` é legítimo, não leak). Mitigação: heurística conservadora (procura padrões específicos como `Entity: X`, `lex-X`, branch names); tests cobrem ambos true/false positives; severity `warning` no início, promove para `error` após validação real
- **Cross-ref resolver não cobre todos os formatos** (markdown link vs backtick mention vs frontmatter). Mitigação: documentar formatos suportados; outros viram TODO em iteração futura
- **CI workflow YAML errado.** Mitigação: testar localmente com `act` ou em branch antes de mergear
- **Conflito com `install.py` em validações duplicadas.** Mitigação: `install.py` continua o que faz; `validate.py` é aditivo; ambos podem rodar; documentação clara
- **Diretiva `validation.severity_overrides` vira escape hatch abusado.** Mitigação: codex docs limitam uso ("legacy debt only"); auditoria periódica do override list

## Verificação

1. `scripts/validate.py` + 9 módulos `_validate/*.py` + tests + fixtures
2. `.github/workflows/validate-framework.yml` rodando em `pull_request`
3. `Makefile` tem target `validate`
4. `docs/internal/validator-rules.md` lista cada regra com severidade e fix
5. Estado limpo do `main` passa `make validate` (após cleanup de dívida)
6. PR de teste com violação **bloqueia** no CI
7. `framework/.directives.sample` tem `validation.severity_overrides` documentado
8. 4 Lexis estruturais (template-usage, platforms-rules, framework-language, naming) referenciam `scripts/validate.py` como ferramenta de validação
9. Performance < 10s em todo o framework
10. PR final passa HARD-GATE de `lex-pr-quality`
