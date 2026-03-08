# Lexis: Commits Firmados Obligatorios

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Todos los commits en repositorios Guardia

## Propósito

Los commits firmados con GPG garantizan la autenticidad y la integridad de cada cambio, permitiendo que revisores y la comunidad confíen en el origen del código. Sin firma, no es posible verificar criptográficamente quién realizó el cambio.

Esta Lexis garantiza que todo commit sea firmado y verificable, conforme lo exigido por el CONTRIBUTING de Guardia.

## Ley

> **Todo commit DEBE ser firmado con clave GPG y marcado como "Verified" por GitHub.**

## Reglas

### 1. Firma obligatoria

Todo commit enviado a repositorios Guardia DEBE contener una firma GPG válida que GitHub pueda verificar.

### 2. Estado aceptado

| Estado | Aceptado | Descripción |
|--------|:--------:|-------------|
| Verified | Sí | Commit firmado, firma verificada, committer es el autor |
| Partially verified | No | Commit firmado pero autor difiere del committer con modo vigilante |
| Unverified | No | Firma no pudo ser verificada |
| Sin estado | No | Commit no firmado |

### 3. Configuración recomendada

Se debe configurar Git para firmar commits automáticamente:

```
git config --global commit.gpgsign true
git config --global user.signingkey <GPG-KEY-ID>
```

### 4. Tags

Las tags de release también DEBEN ser firmadas con GPG.

## Alcance

- **Se aplica a:** todos los repositorios Guardia
- **Agentes vinculados:** todos
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Bloqueo automático:** PR rechazado — solo se aceptan PRs con todos los commits "Verified"
2. **Alerta:** PR marcado con estado de verificación insuficiente
3. **Remediación:** refirmar los commits con `git commit --amend -S` o `git rebase --exec 'git commit --amend -S --no-edit'`

## Ejemplos

### Correcto

```
$ git log --show-signature -1
commit abc123...
gpg: Signature made Mon Mar 08 10:00:00 2026 UTC
gpg: Good signature from "Developer <dev@guardia.finance>"
```

### Incorrecto

```
$ git log --show-signature -1
commit def456...
gpg: No signature found

# Commit sin firma — VIOLA LA LEY
# El PR será rechazado automáticamente
```

## Validación Automatizada

- **Herramienta:** GitHub branch protection rules (require signed commits)
- **Momento:** al abrir o actualizar PR
- **Métrica:** 100% de los commits deben tener estado "Verified"

## Referencias

- [Signing commits — GitHub Docs](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)
- [Firmando commits — Guardia](https://hub.guardia.finance/docs/tutorials/signing-commits/)
- [CONTRIBUTING de Guardia](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `codex-commit-standards` — Guía completa de estándares de commit
