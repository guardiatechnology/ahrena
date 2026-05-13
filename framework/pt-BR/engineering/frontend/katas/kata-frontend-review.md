# Kata: Revisar Código Frontend

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Revisão sistemática de código frontend por corretude, acessibilidade, tipos, testes, segurança e performance

## Objetivo

Executar revisão de código frontend (tipicamente em um PR ou diff), verificando aderência às Lexis aplicáveis e identificando melhorias. Produz relatório estruturado com achados categorizados por severidade (bloqueante, recomendação, nota), aplicável como revisão humana ou parte de `kata-quality-gate` do fluxo Issue-Driven.

## Quando Usar

- Revisão de PR frontend antes do merge
- Revisão periódica de qualidade em código existente
- Complemento ao `kata-quality-gate` quando o foco é frontend

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Diff a revisar | Sim | `git diff {base}..HEAD` ou PR específico |
| Contexto | Não | Issue, ACs, arquitetura esperada (vindo de `.ahrena/issues/{n}/` se aplicável) |
| Escopo | Não | Componentes específicos ou revisão completa do diff |

## Workflow

```
Progresso:
- [ ] 1. Coletar diff e contexto
- [ ] 2. Revisar tipagem (lex-frontend-typing)
- [ ] 3. Revisar testes (lex-frontend-testing)
- [ ] 4. Revisar acessibilidade (lex-frontend-accessibility)
- [ ] 5. Revisar segurança (lex-frontend-security)
- [ ] 6. Revisar arquitetura e composição
- [ ] 7. Revisar performance
- [ ] 8. Consolidar relatório por severidade
```

### Passo 1: Coletar diff e contexto

1. Obter o diff: `git diff {base}..HEAD`.
2. Listar arquivos tocados por tipo (`.tsx`, `.ts`, `.css`, testes, config).
3. Se há ACs (fluxo Issue-Driven), ler `.ahrena/issues/{n}/02-requirements.md`.

### Passo 2: Revisar tipagem

Contra `lex-frontend-typing`:

- [ ] `any` explícito? Justificado em comentário?
- [ ] Props de componentes tipadas?
- [ ] Hooks com estado tipado quando não inferível?
- [ ] Contratos de API tipados (OAS ou Zod)?
- [ ] `unknown` usado onde `any` seria preguiça?
- [ ] `tsc --noEmit` passa?

### Passo 3: Revisar testes

Contra `lex-frontend-testing`:

- [ ] Cada componente com lógica ou interação tem teste?
- [ ] Testes usam `getByRole`/`getByLabelText` em vez de `getByTestId`?
- [ ] Testes verificam comportamento, não implementação?
- [ ] Mocks só nas fronteiras (API, Date, storage)?
- [ ] Snapshots são pequenos e revisados?
- [ ] Caso feliz + erro + loading + vazio cobertos?
- [ ] Se fluxo Issue-Driven: cada teste marca AC-N correspondente?

### Passo 4: Revisar acessibilidade

Contra `lex-frontend-accessibility`:

- [ ] HTML semântico (sem `<div>` onde caberia `<button>`)?
- [ ] Imagens com `alt` apropriado?
- [ ] Formulários com labels associadas?
- [ ] Navegação por teclado funciona? (testar mentalmente ou com Tab)
- [ ] Foco visível?
- [ ] Contraste adequado (4.5:1 para texto normal)?
- [ ] Modais com focus trap + `aria-modal`?
- [ ] Conteúdo dinâmico anunciado (`role="status"`, `aria-live`)?
- [ ] Rodar `axe`/`jest-axe` nos componentes modificados.

### Passo 5: Revisar segurança

Contra `lex-frontend-security`:

- [ ] `dangerouslySetInnerHTML` / `innerHTML` sem sanitização?
- [ ] Segredos no bundle? (busca por API keys, tokens em código `.ts`/`.tsx`)
- [ ] Tokens em `localStorage` vs HttpOnly cookie?
- [ ] Validação de input em dois níveis (cliente + servidor)?
- [ ] `target="_blank"` com `rel="noopener noreferrer"`?
- [ ] Dependências auditadas (`yarn audit`)?

### Passo 6: Revisar arquitetura e composição

Contra `codex-frontend-architecture`:

- [ ] Componentes com responsabilidade única?
- [ ] Feature isolada em `features/` com barrel export?
- [ ] Presentational/container separação clara?
- [ ] Server state via TanStack Query (ou equivalente do projeto), não `useState` + `useEffect`?
- [ ] Sem duplicação óbvia de lógica (hooks extraídos quando cabível)?
- [ ] Sem `useEffect` fazendo data fetching manual quando query library existe?
- [ ] Tokens de design respeitados (sem valores mágicos de cor/espaçamento)?

### Passo 7: Revisar performance

- [ ] Listas grandes virtualizadas?
- [ ] Imagens com `next/image` ou srcset equivalente?
- [ ] Code splitting nas rotas?
- [ ] `useMemo`/`useCallback` usado com justificativa (não defensivamente)?
- [ ] Bundle size razoável? (rodar análise se mudança em deps)
- [ ] Sem re-renders desnecessários (verificar via React DevTools Profiler se houver suspeita)?

### Passo 8: Consolidar relatório por severidade

Estruturar achados:

```markdown
# Frontend Review — {PR ou issue} #{n}

- **Data:** {YYYY-MM-DD}
- **Arquivos revisados:** {n}
- **Achados:** {B} bloqueantes, {R} recomendações, {N} notas

## Bloqueantes (impedem merge)

### F-1: {título}
- **Categoria:** {Typing | Testing | A11y | Security | Architecture | Performance}
- **Local:** `src/features/refunds/RefundForm.tsx:42`
- **Problema:** {o que há}
- **Recomendação:** {correção proposta com exemplo de código}
- **Referência:** `lex-frontend-{...}`

## Recomendações (melhorias)

### F-2: ...

## Notas (informacional)

### F-3: ...

## Resumo Positivo

{2-3 pontos bem executados que valem destaque}
```

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Relatório de revisão | Markdown estruturado | Resposta ao usuário ou `docs/reviews/` |
| Comentários em PR | Comentários linha-a-linha via GitHub MCP | PR no GitHub (opcional) |

## Restrições

- **Revisão ≠ reescrita:** este kata aponta problemas; não modifica código diretamente.
- **Severidade objetiva:** bloqueante = viola Lexis; recomendação = melhoria de qualidade; nota = observação.
- **Sem achismo:** cada achado tem referência à Lexis ou Codex aplicável.
- **Tom construtivo:** apontar o problema com a solução sugerida, não apenas criticar.

## Referências

- `lex-frontend-typing`, `lex-frontend-testing`, `lex-frontend-accessibility`, `lex-frontend-security`
- `codex-frontend-architecture`
- `kata-quality-gate` — no fluxo Issue-Driven, integra os achados
- `kata-mcp-github-read` — para revisar diff em PR remoto
