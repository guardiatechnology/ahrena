# Kata: Configurar Firma GPG de Commits

> **Prefijo:** `kata-` | **Tipo:** Habilidad Repetible | **Alcance:** Configurar firma GPG para commits y etiquetas git, según `lex-signed-commits`

## Objetivo

Este Kata define el procedimiento paso a paso para configurar la firma GPG de commits en la máquina del desarrollador, de modo que cada commit y etiqueta se marque como **Verified** en GitHub, satisfaciendo `lex-signed-commits`.

## Cuándo Usar

- Al configurar una nueva máquina de desarrollo por primera vez
- Cuando un desarrollador aún no ha configurado la firma GPG
- Cuando es invocado por un Warrior o como parte de un flujo de onboarding de contribuidor
- Cuando los commits aparecen como "Unverified" en GitHub

## Entradas

| Entrada | Requerida | Descripción |
|---------|:---------:|-------------|
| Correo electrónico de cuenta GitHub | Sí | Debe coincidir con el correo en la cuenta GitHub y en la clave GPG |
| Contraseña de la clave | No | Elegida durante la generación; se recomienda fuertemente |

## Flujo

```
Progreso:
- [ ] 1. Verificar instalación de GPG
- [ ] 2. Generar clave GPG
- [ ] 3. Configurar git
- [ ] 4. Exportar clave y añadir a GitHub
- [ ] 5. Verificar la firma
```

### Paso 1: Verificar Instalación de GPG

```bash
gpg --version
```

Si GPG no está instalado:

| SO | Comando |
|----|---------|
| macOS | `brew install gnupg` |
| Debian/Ubuntu | `sudo apt-get install gnupg` |
| Windows | Instale [Gpg4win](https://gpg4win.org/) |

### Paso 2: Generar Clave GPG

```bash
gpg --full-generate-key
```

Cuando se solicite:

1. Tipo de clave → **RSA and RSA** (opción 1)
2. Tamaño de clave → **4096**
3. Expiración → **0** (no expira) o una fecha preferida
4. Nombre y correo → use el correo asociado a su cuenta GitHub
5. Contraseña → elija una fuerte (se recomienda fuertemente)

Liste la clave generada para obtener el ID:

```bash
gpg --list-secret-keys --keyid-format=long
```

Ejemplo de salida:

```
sec   rsa4096/3AA5C34371567BD2 2024-01-01 [SC]
      D3E3F...
uid   [ultimate] Your Name <your@email.com>
```

Copie el ID de la clave — el segmento después de `rsa4096/` (ej.: `3AA5C34371567BD2`).

### Paso 3: Configurar Git

```bash
# Asociar la clave de firma con git
git config --global user.signingkey 3AA5C34371567BD2

# Firmar automáticamente todos los commits
git config --global commit.gpgsign true

# Firmar automáticamente todas las etiquetas
git config --global tag.gpgSign true

# Asegurar el uso del formato openpgp (eliminar cualquier override anterior)
git config --global --unset gpg.format 2>/dev/null || true
```

Verifique la configuración:

```bash
git config --global --list | grep -E "gpg|signing"
# Esperado:
# user.signingkey=3AA5C34371567BD2
# commit.gpgsign=true
# tag.gpgSign=true
```

### Paso 4: Exportar Clave y Añadir a GitHub

Exporte la clave pública:

```bash
gpg --export --armor 3AA5C34371567BD2
```

Copie toda la salida (desde `-----BEGIN PGP PUBLIC KEY BLOCK-----` hasta `-----END PGP PUBLIC KEY BLOCK-----`).

Añada a GitHub:

1. **GitHub → Settings → SSH and GPG keys**
2. Haga clic en **New GPG key**
3. Pegue la clave pública exportada
4. Haga clic en **Add GPG key**

### Paso 5: Verificar la Firma

Cree un commit de prueba en cualquier repositorio:

```bash
git commit --allow-empty -m "test: verify GPG signing configuration"
git log --show-signature -1
```

Salida esperada:

```
gpg: Signature made ...
gpg: Good signature from "Your Name <your@email.com>"
```

En GitHub, el commit debe mostrar el badge **Verified**.

## Entregable

Git está configurado para firmar automáticamente con GPG todos los commits y etiquetas. Los commits enviados a repositorios Guardia muestran el estado **Verified** en GitHub.

## Notas

- Para usar la misma clave en múltiples máquinas: exporte la clave privada (`gpg --export-secret-keys --armor <KEY-ID> > private.gpg`), transfiérala de forma segura e impórtela en la otra máquina (`gpg --import private.gpg`).
- Si los commits siguen apareciendo como "Unverified" tras la configuración: verifique que el correo en la clave GPG coincide con `git config --global user.email` y con el correo principal de su cuenta GitHub.
- Los prompts de contraseña en cada commit pueden evitarse configurando `gpg-agent` con un TTL largo — consulte la documentación de su SO.

## Referencias

- `lex-signed-commits` — Ley que requiere commits firmados con GPG en repositorios Guardia
- `codex-git-workflow` — Flujo completo de contribución git
- `codex-contributing` — Visión general del proceso de contribución
- [GitHub: Firmar commits](https://docs.github.com/es/authentication/managing-commit-signature-verification/signing-commits)
- [GitHub: Generar una nueva clave GPG](https://docs.github.com/es/authentication/managing-commit-signature-verification/generating-a-new-gpg-key)
