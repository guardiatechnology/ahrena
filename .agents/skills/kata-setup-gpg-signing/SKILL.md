---
name: kata-setup-gpg-signing
description: "Configurar Assinatura GPG de Commits. Configurar assinatura GPG para commits e tags git, conforme lex-signed-commits"
---

# Kata: Configurar Assinatura GPG de Commits

> **Prefixo:** `kata-` | **Tipo:** Habilidade Repetível | **Escopo:** Configurar assinatura GPG para commits e tags git, conforme `lex-signed-commits`

## Entradas

| Entrada | Obrigatória | Descrição |
|---------|:-----------:|-----------|
| E-mail da conta GitHub | Sim | Deve corresponder ao e-mail na conta GitHub e na chave GPG |
| Senha da chave | Não | Escolhida durante a geração; fortemente recomendada |

## Fluxo

```
Progresso:
- [ ] 1. Verificar instalação do GPG
- [ ] 2. Gerar chave GPG
- [ ] 3. Configurar git
- [ ] 4. Exportar chave e adicionar ao GitHub
- [ ] 5. Verificar assinatura
```

### Etapa 1: Verificar Instalação do GPG

```bash
gpg --version
```

Se o GPG não estiver instalado:

| SO | Comando |
|----|---------|
| macOS | `brew install gnupg` |
| Debian/Ubuntu | `sudo apt-get install gnupg` |
| Windows | Instale o [Gpg4win](https://gpg4win.org/) |

### Etapa 2: Gerar Chave GPG

```bash
gpg --full-generate-key
```

Quando solicitado:

1. Tipo de chave → **RSA and RSA** (opção 1)
2. Tamanho da chave → **4096**
3. Expiração → **0** (não expira) ou uma data preferida
4. Nome e e-mail → use o e-mail associado à sua conta GitHub
5. Senha → escolha uma forte (fortemente recomendada)

Liste a chave gerada para obter o ID:

```bash
gpg --list-secret-keys --keyid-format=long
```

Exemplo de saída:

```
sec   rsa4096/3AA5C34371567BD2 2024-01-01 [SC]
      D3E3F...
uid   [ultimate] Your Name <your@email.com>
```

Copie o ID da chave — o segmento após `rsa4096/` (ex.: `3AA5C34371567BD2`).

### Etapa 3: Configurar Git

```bash
# Associar a chave de assinatura ao git
git config --global user.signingkey 3AA5C34371567BD2

# Assinar automaticamente todos os commits
git config --global commit.gpgsign true

# Assinar automaticamente todas as tags
git config --global tag.gpgSign true

# Garantir o uso do formato openpgp (remover qualquer override anterior)
git config --global --unset gpg.format 2>/dev/null || true
```

Verifique a configuração:

```bash
git config --global --list | grep -E "gpg|signing"
# Esperado:
# user.signingkey=3AA5C34371567BD2
# commit.gpgsign=true
# tag.gpgSign=true
```

### Etapa 4: Exportar Chave e Adicionar ao GitHub

Exporte a chave pública:

```bash
gpg --export --armor 3AA5C34371567BD2
```

Copie toda a saída (de `-----BEGIN PGP PUBLIC KEY BLOCK-----` até `-----END PGP PUBLIC KEY BLOCK-----`).

Adicione ao GitHub:

1. **GitHub → Settings → SSH and GPG keys**
2. Clique em **New GPG key**
3. Cole a chave pública exportada
4. Clique em **Add GPG key**

### Etapa 5: Verificar Assinatura

Crie um commit de teste em qualquer repositório:

```bash
git commit --allow-empty -m "test: verify GPG signing configuration"
git log --show-signature -1
```

Saída esperada:

```
gpg: Signature made ...
gpg: Good signature from "Your Name <your@email.com>"
```

No GitHub, o commit deve exibir o badge **Verified**.

## Entregável

Git está configurado para assinar automaticamente com GPG todos os commits e tags. Commits enviados para repositórios Guardia mostram status **Verified** no GitHub.

## Observações

- Para usar a mesma chave em múltiplas máquinas: exporte a chave privada (`gpg --export-secret-keys --armor <KEY-ID> > private.gpg`), transfira com segurança e importe na outra máquina (`gpg --import private.gpg`).
- Se os commits ainda aparecerem como "Unverified" após a configuração: verifique se o e-mail na chave GPG corresponde a `git config --global user.email` e ao e-mail principal da sua conta GitHub.
- Prompts de senha a cada commit podem ser evitados configurando o `gpg-agent` com um TTL longo — consulte a documentação do seu SO.
