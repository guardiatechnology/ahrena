# Lexis: Commits Assinados Obrigatórios

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Todos os commits em repositórios Guardia

## Propósito

Commits assinados com GPG garantem a autenticidade e a integridade de cada alteração, permitindo que revisores e a comunidade confiem na origem do código. Sem assinatura, não há como verificar criptograficamente quem fez a alteração.

Esta Lexis garante que todo commit seja assinado e verificável, conforme exigido pelo CONTRIBUTING da Guardia.

## Lei

> **Todo commit DEVE ser assinado com chave GPG e marcado como "Verified" pelo GitHub.**

## Regras

### 1. Assinatura obrigatória

Todo commit enviado a repositórios Guardia DEVE conter uma assinatura GPG válida que o GitHub consiga verificar.

### 2. Status aceito

| Status | Aceito | Descrição |
|--------|:------:|-----------|
| Verified | Sim | Commit assinado, assinatura verificada, committer é o autor |
| Partially verified | Não | Commit assinado mas autor difere do committer com modo vigilante |
| Unverified | Não | Assinatura não pôde ser verificada |
| Sem status | Não | Commit não assinado |

### 3. Configuração recomendada

O contribuidor DEVE configurar o Git para assinar commits automaticamente:

```
git config --global commit.gpgsign true
git config --global user.signingkey <GPG-KEY-ID>
```

### 4. Tags

Tags de release também DEVEM ser assinadas com GPG.

## Abrangência

- **Aplica-se a:** todos os repositórios Guardia
- **Agentes vinculados:** todos
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Bloqueio automático:** PR rejeitado — apenas PRs com todos os commits "Verified" são aceitos
2. **Alerta:** PR marcado com status de verificação insuficiente
3. **Remediação:** reassinar os commits com `git commit --amend -S` ou `git rebase --exec 'git commit --amend -S --no-edit'`

## Exemplos

### Correto

```
$ git log --show-signature -1
commit abc123...
gpg: Signature made Mon Mar 08 10:00:00 2026 UTC
gpg: Good signature from "Developer <dev@guardia.finance>"
```

### Incorreto

```
$ git log --show-signature -1
commit def456...
gpg: No signature found

# Commit sem assinatura — VIOLA A LEI
# PR será rejeitado automaticamente
```

## Validação Automatizada

- **Ferramenta:** GitHub branch protection rules (require signed commits)
- **Momento:** ao abrir ou atualizar PR
- **Métrica:** 100% dos commits devem ter status "Verified"

## Referências

- [Signing commits — GitHub Docs](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)
- [Assinando commits — Guardia](https://hub.guardia.finance/docs/tutorials/signing-commits/)
- [CONTRIBUTING da Guardia](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `codex-commit-standards` — Guia completo de standards de commit
