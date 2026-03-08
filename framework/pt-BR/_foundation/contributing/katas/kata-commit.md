# Kata: Fazer Commit Padronizado

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação de commits conformes com as Lexis da Guardia

## Objetivo

Este Kata define o procedimento padronizado para criar um commit que respeite todas as Lexis de commit da Guardia — formato Conventional Commits, atomicidade, assinatura GPG e idioma.

## Quando Usar

- Quando é necessário fazer commit de alterações seguindo os padrões da Guardia
- Quando o usuário solicita ajuda para commitar mudanças
- Quando invocado pelo `cry-commit`
- Quando invocado internamente pelo `kata-contribute`

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Alterações | Sim | Arquivos staged ou indicação do que commitar |
| Tipo | Não | Tipo Conventional Commits (feat, fix, docs, etc.). Se omitido, o agente infere do diff |
| Escopo | Não | Módulo ou domínio afetado. Se omitido, o agente infere do diff |
| Descrição | Não | Texto do subject. Se omitido, o agente compõe a partir do diff |

## Workflow

```
Progresso:
- [ ] 1. Análise das mudanças
- [ ] 2. Classificação e composição da mensagem
- [ ] 3. Validação contra as Lexis
- [ ] 4. Execução do commit
- [ ] 5. Verificação final
```

### Passo 1: Análise das Mudanças

1. Executar `git status` para verificar arquivos staged
2. Se não há arquivos staged, analisar o diff e sugerir o que incluir com `git add`
3. Executar `git diff --staged` para entender o conteúdo das mudanças
4. Verificar se as mudanças são atômicas (`lex-small-commits`):
   - Todas as mudanças pertencem a um único propósito?
   - Se não, orientar o usuário a dividir em commits separados

### Passo 2: Classificação e Composição da Mensagem

1. Consultar `codex-commit-standards` para referência
2. **Identificar o tipo:** feat, fix, docs, build, chore, ci, style, refactor, perf, test
3. **Identificar o escopo:** módulo ou domínio principal afetado (opcional)
4. **Compor o subject:**
   - Imperativo presente em inglês (`lex-commit-language`)
   - Máximo 72 caracteres
   - Sem ponto final
   - Formato: `tipo(escopo): descrição`
5. **Compor o body (se necessário):**
   - Versão em inglês com tag `[en]`
   - Versão em idioma local com tag `[pt-BR]` ou `[es]` (se solicitado)
   - Detalhar o "porquê" da mudança
6. **Adicionar rodapés (se aplicável):**
   - `Closes #N` para fechar issues
   - `BREAKING CHANGE:` para mudanças incompatíveis
   - `Co-authored-by:` para pair programming

### Passo 3: Validação contra as Lexis

Verificar conformidade com cada Lexis antes de executar:

- [ ] `lex-conventional-commits`: formato `tipo(escopo): descrição` correto?
- [ ] `lex-small-commits`: mudanças atômicas (um único propósito)?
- [ ] `lex-commit-language`: subject em inglês? Tag de idioma no body?
- [ ] `lex-signed-commits`: GPG configurado? (`git config --get commit.gpgsign` = true)

Se alguma validação falhar, corrigir antes de prosseguir.

### Passo 4: Execução do Commit

1. Executar o commit com assinatura GPG:
   ```
   git commit -S -m "<mensagem>"
   ```
2. Para mensagem multiline (com body), usar:
   ```
   git commit -S -m "$(cat <<'EOF'
   tipo(escopo): descrição

   [en]
   Detailed description in English.

   [pt-BR]
   Descrição detalhada em português.

   Closes #123
   EOF
   )"
   ```

### Passo 5: Verificação Final

- [ ] `git log -1 --format='%s'` mostra o subject correto
- [ ] `git log -1 --show-signature` mostra assinatura GPG válida
- [ ] O commit contém apenas as mudanças pretendidas
- [ ] O subject está em inglês e segue Conventional Commits
- [ ] O commit é atômico (uma mudança lógica)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Commit assinado e formatado | Git commit | Repositório local |

## Restrições

- Nunca fazer commit sem verificar conformidade com as 4 Lexis
- Nunca misturar mudanças não relacionadas em um único commit
- Nunca fazer commit sem assinatura GPG configurada
- Se GPG não está configurado, alertar o usuário e orientar a configuração

## Referências

- `lex-conventional-commits` — Formato obrigatório
- `lex-signed-commits` — Assinatura GPG obrigatória
- `lex-small-commits` — Atomicidade obrigatória
- `lex-commit-language` — Idioma obrigatório
- `codex-commit-standards` — Guia completo de standards
- `cry-commit` — Atalho que invoca este Kata
