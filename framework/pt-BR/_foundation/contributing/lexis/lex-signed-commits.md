# Lexis: Commits Assinados Obrigatórios

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Todos os commits em repositórios Guardia

## Propósito

Commits assinados garantem a autenticidade e a integridade de cada alteração, permitindo que revisores e a comunidade confiem na origem do código. Sem assinatura, não há como verificar criptograficamente quem fez a alteração.

Esta Lexis garante que todo commit seja assinado e verificável, conforme exigido pelo CONTRIBUTING da Guardia.

## Lei

> **Todo commit DEVE ser assinado (com chave GPG local OU pela assinatura server-side do GitHub via token de instalação do App `warriors_default` da Ahrena) e marcado como "Verified" pelo GitHub.**

## Regras

### 1. Assinatura obrigatória

Todo commit enviado a repositórios Guardia DEVE conter uma assinatura válida que o GitHub consiga verificar. A assinatura PODE vir de uma chave GPG local mantida pelo contribuidor OU da assinatura server-side feita pelo GitHub quando um token de instalação de App cria o commit via Git Data API.

### 2. Status aceito

| Status | Aceito | Descrição |
|--------|:------:|-----------|
| Verified | Sim | Commit assinado, assinatura verificada, committer é o autor |
| Partially verified | Não | Commit assinado mas autor difere do committer com modo vigilante |
| Unverified | Não | Assinatura não pôde ser verificada |
| Sem status | Não | Commit não assinado |

### 3. Configuração recomendada (caminho GPG local)

O contribuidor DEVE configurar o Git para assinar commits automaticamente:

```
git config --global commit.gpgsign true
git config --global user.signingkey <GPG-KEY-ID>
```

### 4. Tags

Tags de release também DEVEM ser assinadas com GPG (caminho de chave local; tags criadas pelo token de instalação do App seguem o mesmo fluxo de assinatura server-side dos commits).

### 5. Modalidades de assinatura

Dois caminhos satisfazem esta Lei, ambos produzindo o status "Verified" no GitHub:

| Modalidade | Quando | Como |
|------------|--------|------|
| **Assinatura GPG local** | Padrão para commits feitos por humano | O contribuidor configura `commit.gpgsign true` + chave de assinatura válida (`lex-signed-commits` Regra 3). A assinatura é produzida localmente antes do push. |
| **Assinatura via instalação de App** | Quando `warriors_default_author.enabled: true` e o warrior em execução está em `warriors_default_author.apply_to` | Warriors chamam `scripts/ahrena-auth.sh` + `scripts/ahrena-api-commit.sh`, que criam o commit pela GitHub Git Data API com o token de instalação do App. O GitHub assina o commit server-side; o selo "Verified" aparece na página do commit e nenhuma chave GPG local é envolvida. Veja `codex-git-workflow` ("Identidade do autor"). |

Ambas as modalidades produzem commits cujo status de verificação DEVE ser "Verified". Um commit que não passe por nenhum dos dois caminhos de assinatura (sem GPG local e sem caminho de commit via API) viola esta Lei.

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
