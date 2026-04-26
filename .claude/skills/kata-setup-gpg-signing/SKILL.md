---
name: kata-setup-gpg-signing
description: "tag.gpgSign=true. Configure GPG signing for git commits and tags, per lex-signed-commits"
---

# Kata: Configure GPG Commit Signing

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Configure GPG signing for git commits and tags, per `lex-signed-commits`

## Workflow

```
Progress:
- [ ] 1. Verify GPG installation
- [ ] 2. Generate GPG key
- [ ] 3. Configure git
- [ ] 4. Export key and add to GitHub
- [ ] 5. Verify signing
```

### Step 1: Verify GPG Installation

```bash
gpg --version
```

If GPG is not installed:

| OS | Command |
|----|---------|
| macOS | `brew install gnupg` |
| Debian/Ubuntu | `sudo apt-get install gnupg` |
| Windows | Install [Gpg4win](https://gpg4win.org/) |

### Step 2: Generate GPG Key

```bash
gpg --full-generate-key
```

When prompted:

1. Key type → **RSA and RSA** (option 1)
2. Key size → **4096**
3. Expiration → **0** (does not expire) or a preferred date
4. Name and email → use the email associated with your GitHub account
5. Passphrase → choose a strong one (strongly recommended)

List the generated key to obtain the key ID:

```bash
gpg --list-secret-keys --keyid-format=long
```

Example output:

```
sec   rsa4096/3AA5C34371567BD2 2024-01-01 [SC]
      D3E3F...
uid   [ultimate] Your Name <your@email.com>
```

Copy the key ID — the segment after `rsa4096/` (e.g., `3AA5C34371567BD2`).

### Step 3: Configure Git

```bash
# Associate the signing key with git
git config --global user.signingkey 3AA5C34371567BD2

# Auto-sign all commits
git config --global commit.gpgsign true

# Auto-sign all tags
git config --global tag.gpgSign true

# Ensure openpgp format is used (remove any previous override)
git config --global --unset gpg.format 2>/dev/null || true
```

Verify the configuration:

```bash
git config --global --list | grep -E "gpg|signing"
# Expected:
# user.signingkey=3AA5C34371567BD2
# commit.gpgsign=true
# tag.gpgSign=true
```

### Step 4: Export Key and Add to GitHub

Export the public key:

```bash
gpg --export --armor 3AA5C34371567BD2
```

Copy the full output (from `-----BEGIN PGP PUBLIC KEY BLOCK-----` to `-----END PGP PUBLIC KEY BLOCK-----`).

Add to GitHub:

1. **GitHub → Settings → SSH and GPG keys**
2. Click **New GPG key**
3. Paste the exported public key
4. Click **Add GPG key**

### Step 5: Verify Signing

Create a test commit in any repository:

```bash
git commit --allow-empty -m "test: verify GPG signing configuration"
git log --show-signature -1
```

Expected output:

```
gpg: Signature made ...
gpg: Good signature from "Your Name <your@email.com>"
```

On GitHub, the commit should display the **Verified** badge.

## Deliverable

Git is configured to automatically GPG-sign all commits and tags. Commits pushed to Guardia repositories show **Verified** status on GitHub.

## Notes

- To use the same key on multiple machines: export the private key (`gpg --export-secret-keys --armor <KEY-ID> > private.gpg`), transfer it securely, and import it on the other machine (`gpg --import private.gpg`).
- If commits still show "Unverified" after setup: verify that the email in the GPG key matches `git config --global user.email` and the primary email in your GitHub account.
- Passphrase prompts on every commit can be avoided by configuring `gpg-agent` with a long TTL — consult your OS documentation.
