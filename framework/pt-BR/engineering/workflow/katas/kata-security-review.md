# Kata: Revisão de Segurança

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Fase 5 do fluxo Issue-Driven — revisão de segurança do código implementado contra OWASP Top 10, padrões de autenticação/autorização, manipulação de dados sensíveis e dependências vulneráveis

## Objetivo

Executar revisão de segurança sobre o código implementado na Fase 4, identificando vulnerabilidades conhecidas (OWASP Top 10), problemas de autenticação/autorização, exposição de dados sensíveis, credenciais em código e dependências com CVEs conhecidos. Produz relatório em `docs/issues/issue-{n}/05-security-review.md` com severidade classificada; falhas críticas bloqueiam o Gate 2.

## Quando Usar

- Fase 5 do fluxo orquestrado por `warrior-athena`, após Apollo (ou warrior equivalente) concluir a implementação na Fase 4
- Quando é necessário auditar mudanças de código quanto a riscos de segurança antes de criar o PR

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Diff da implementação | Sim | `git diff` entre branch de trabalho e branch base |
| Requisitos Fase 2 | Sim | `docs/issues/issue-{n}/02-requirements.md` |
| Arquitetura Fase 3 | Sim | `docs/issues/issue-{n}/03-architecture.md` (inclui integrações externas) |

## Workflow

```
Progresso:
- [ ] 1. Coletar diff e contexto
- [ ] 2. OWASP Top 10 check
- [ ] 3. Autenticação e autorização
- [ ] 4. Dados sensíveis e credenciais
- [ ] 5. Dependências (CVE scan)
- [ ] 6. Consolidar relatório com severidade
- [ ] 7. Persistir em docs/issues/issue-{n}/05-security-review.md
- [ ] 8. Atualizar checkpoint
```

### Passo 1: Coletar diff e contexto

1. Executar `git diff {base-branch}...HEAD` ou equivalente.
2. Ler `03-architecture.md` para entender integrações externas envolvidas.
3. Ler `02-requirements.md` para identificar ACs com implicações de segurança (ex.: autenticação, autorização, dados sensíveis).

### Passo 2: OWASP Top 10 check

Para cada categoria, verificar explicitamente no diff:

| Categoria | Verificação |
|---|---|
| **A01 — Broken Access Control** | Endpoints novos têm verificação de autorização (RBAC, ABAC)? Ownership check quando aplicável? |
| **A02 — Cryptographic Failures** | Dados sensíveis em trânsito/repouso estão criptografados? Uso correto de algoritmos (não MD5/SHA1)? |
| **A03 — Injection** | Queries SQL parametrizadas? Inputs validados antes de uso em comandos/queries? |
| **A04 — Insecure Design** | Padrões inseguros (ex.: tokens previsíveis, timeouts excessivos)? |
| **A05 — Security Misconfiguration** | Headers de segurança configurados? Modo debug desabilitado? |
| **A06 — Vulnerable Components** | (ver Passo 5) |
| **A07 — Identification & Auth Failures** | Rate limiting em endpoints de auth? Brute-force protection? Session management correto? |
| **A08 — Software & Data Integrity Failures** | Assinaturas verificadas? Deserialização segura? |
| **A09 — Security Logging Failures** | Eventos relevantes (auth, acesso a dados sensíveis) são logados? Logs contêm dados sensíveis? |
| **A10 — SSRF** | URLs de entrada são validadas contra lista permitida? |

Registrar cada achado com: categoria OWASP, arquivo/linha, severidade (`crítica`/`alta`/`média`/`baixa`), recomendação.

### Passo 3: Autenticação e autorização

Se a issue envolve endpoints HTTP:

1. Cada endpoint novo tem verificação de auth? (bearer token, OAuth2, etc.)
2. Cada operação tem verificação de permissão (RBAC)?
3. Ownership check: usuário só pode operar em recursos que possui?
4. Informações em tokens não vazam dados sensíveis?

Se envolve consumo/publicação de eventos:

1. Eventos de alto privilégio exigem assinatura/verificação?
2. Eventos contêm apenas IDs e não dados sensíveis no payload?

### Passo 4: Dados sensíveis e credenciais

1. Scan por padrões de credenciais no diff: `password`, `secret`, `api_key`, `token`, strings que parecem chaves.
2. Verificar `.env`, `.env.example`: apenas placeholders, nunca valores reais.
3. Dados sensíveis (CPF, email, cartão) em logs? Devem ser mascarados/redacted.
4. Dados sensíveis em mensagens de erro retornadas ao cliente? Não devem vazar.
5. Dados sensíveis em responses de API que o cliente não precisa? Remover.

### Passo 5: Dependências (CVE scan)

1. Se houve mudança em arquivos de dependência (`pyproject.toml`, `requirements.txt`, `package.json`, `Cargo.toml`, etc.), executar scan:
   - Python: `pip-audit` ou `safety check`
   - Node: `yarn audit` ou `npm audit`
   - Rust: `cargo audit`
2. Classificar CVEs encontrados por severidade (CVSS).
3. CVEs críticos (CVSS ≥ 9.0) em dependências usadas no código tocado → severidade crítica no relatório.

### Passo 6: Consolidar relatório com severidade

Consolidar todos os achados em uma lista priorizada:

- **Críticas** — bloqueiam o Gate 2; devem ser resolvidas antes de reabrir.
- **Altas** — devem ser resolvidas antes do merge do PR.
- **Médias** — registrar como TODOs no PR; pode ser resolvido em iteração futura.
- **Baixas** — nota informacional.

Se **zero achados críticos ou altos**, reportar `approved` para seguir ao Gate 2.

### Passo 7: Persistir em `docs/issues/issue-{n}/05-security-review.md`

Estrutura:

```markdown
# Revisão de Segurança — Issue #{n}: {título}

- **Referência:** [Arquitetura](./03-architecture.md)
- **Data:** {YYYY-MM-DD}
- **Resultado global:** {approved | changes-required | blocked}

## Resumo

- Críticas: {n}
- Altas: {m}
- Médias: {k}
- Baixas: {j}

## Achados Críticos

### S-1: {título}
- **Categoria:** OWASP A{nn} — {nome}
- **Local:** `{arquivo}:{linha}`
- **Descrição:** {o que há}
- **Recomendação:** {como corrigir}

## Achados Altos

### S-2: ...

## Achados Médios

### S-3: ...

## Achados Baixos / Informacionais

### S-4: ...

## Dependências

| Pacote | Versão | CVE | Severidade | Recomendação |
|---|---|---|---|---|
| ... | ... | CVE-XXXX-YYYY | {crítica/alta/...} | {upgrade para X} |

## Conclusão

{1-2 parágrafos: status final, o que deve ser resolvido antes do Gate 2}
```

### Passo 8: Atualizar checkpoint

1. Atualizar `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - fase concluída: 5
   - próxima: 6 (Gate 2)
   - resultado: `approved`, `changes-required` ou `blocked`
   - número de achados por severidade
2. Informar ao `warrior-athena`:
   - Se `approved`: seguir para Fase 6
   - Se `changes-required` ou `blocked`: retornar à Fase 4 com relatório

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Relatório de segurança | Markdown | `docs/issues/issue-{n}/05-security-review.md` |
| Resultado | `approved` / `changes-required` / `blocked` | Retorno ao orquestrador |
| Checkpoint atualizado | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restrições

- **Não modificar código:** esta kata é apenas de revisão; correções são aplicadas pela Fase 4 em nova iteração.
- **Severidade é bloqueante:** achados críticos sempre bloqueiam o Gate 2; não há override automático.
- **Escopo limitado ao diff:** não revisar código pré-existente não tocado pelo diff (seria tarefa de auditoria separada).
- **Sem falsos positivos silenciosos:** se um achado é falso positivo após análise, registrar explicitamente no relatório com justificativa, não omitir.
- **Destino fixo:** `docs/issues/issue-{n}/05-security-review.md` (conforme `lex-issue-driven`).

## Referências

- `lex-issue-driven` — leis do fluxo
- `codex-issue-workflow` — posição desta kata no fluxo
- `lex-python-security` — regras de segurança para código Python
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
