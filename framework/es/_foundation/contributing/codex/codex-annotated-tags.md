# Codex: Tags Anotados y Firmados

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Operación de tags Git en repositorios Guardia — creación, firma, verificación y validación server-side

## Visión General

Este Codex es el manual operacional para crear, firmar y verificar tags Git en repositorios Guardia. Documenta los comandos, opciones, modos de falla y configuración GPG necesarios para satisfacer `lex-annotated-tags`. Es consultado por los Katas `kata-tag` y `kata-release-publish` y por el Warrior `warrior-janus`.

## Contexto

- **Dominio:** ciclo de vida de tags Git (creación local, firma, push, validación en el remoto)
- **Público-objetivo:** agentes de IA que crean tags (`kata-tag`, `kata-release-publish`), maintainers humanos preparando releases
- **Actualización:** cuando el flujo de creación/validación de tag cambia, o cuando la Action `validate-tag.yml` evoluciona

## Contenido

### Principios

1. **Anotado antes de firmado.** Un tag lightweight (`git tag NOMBRE`) no tiene objeto propio en Git — es solo un puntero a un commit. Sin objeto, no hay cuerpo para firmar. Por eso `git tag -s` implica `git tag -a`.
2. **Firma local, validación server-side best-effort.** La firma se genera en la máquina del contribuyente con su clave GPG. La validación en el runner de GitHub depende de que la clave pública esté disponible al runner — frecuentemente no lo está. El bloqueo server-side autoritativo es el tipo del objeto (anotado vs lightweight) + nombre SemVer; la firma se verifica localmente antes del push.
3. **Sin creación directa en el remoto.** La UI/API de GitHub que crea tags produce lightweight tags. Por eso, crear tag por la UI/API está prohibido por `lex-annotated-tags`.

### Configuración GPG para Tags

Para firmar tags automáticamente siempre que se use `git tag -a`:

```bash
git config --global tag.gpgSign true
git config --global user.signingkey <GPG-KEY-ID>
```

Verificar configuración:

```bash
git config --get tag.gpgSign      # esperado: true
git config --get user.signingkey  # esperado: ID de la clave GPG (16 o 40 caracteres hex)
```

Prerrequisitos: clave GPG generada y publicada en GitHub (ver `kata-setup-gpg-signing`).

### Comandos de Creación

| Forma | Resultado | Conformidad con Lex |
|------|-----------|:-------------------:|
| `git tag -s v1.2.3 -m "Release 1.2.3"` | Tag anotado + firmado (canónico) | ✅ |
| `git tag -a v1.2.3 -m "Release 1.2.3"` | Tag anotado sin firma | ❌ (viola `lex-annotated-tags` regla 2) |
| `git tag v1.2.3` | Tag lightweight | ❌ (viola `lex-annotated-tags` regla 1) |
| `git tag -s v1.2.3 <sha>` | Tag anotado + firmado apuntando a `<sha>` específico | ✅ |

Cuando `tag.gpgSign true` está configurado, `git tag -a` ya produce un tag firmado — `-s` se vuelve redundante pero inofensivo. El Kata siempre pasa `-s` explícitamente por defensa en profundidad.

### Verificación Local

Antes de empujar:

```bash
git tag -v v1.2.3
```

Salida esperada (firma válida):

```
object <sha>
type commit
tag v1.2.3
tagger <Author> <email> <timestamp>

Release 1.2.3
gpg: Signature made <date>
gpg: Good signature from "<Author> <email>"
```

Salida de tag lightweight (`git tag -v` falla):

```
error: <tag>: cannot verify a non-tag object of type commit.
```

Salida de tag anotado sin firma:

```
object <sha>
type commit
tag v1.2.3
...
error: no signature found
```

### Push

```bash
git push origin v1.2.3
```

El tag empujado dispara `validate-tag.yml` en GitHub. Para borrar un tag local que aún no fue empujado: `git tag -d v1.2.3`.

### Validación Server-side (`validate-tag.yml`)

El flujo de trabajo valida cada tag empujado a `origin`:

1. **Tipo del objeto** — `git cat-file -t $TAG`:
   - Anotado → retorna `tag` → prosigue
   - Lightweight → retorna `commit` → **falla + elimina el tag remoto**
2. **Formato SemVer** — regex `^v?[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$`. Tag fuera del patrón → **falla + elimina**.
3. **Firma GPG** — `git tag -v $TAG` en best-effort:
   - Buena firma → log `✓ GPG signature verified`
   - Clave pública ausente en el runner → log `WARNING` (no falla — la firma se valida localmente)
   - Sin firma → log `WARNING` (la firma es regla local; ver Principio 2)

### Eliminar Tag Remoto Inválido

Cuando la Action detecta un tag inválido (lightweight o nombre inválido), elimina la referencia remota antes de fallar. Comando:

```bash
gh api -X DELETE repos/:owner/:repo/git/refs/tags/$TAG
```

El prefijo `repos/:owner/:repo/git/` es **obligatorio** — sin él la llamada retorna HTTP 404. En GitHub Actions, `${{ github.repository }}` reemplaza `:owner/:repo`.

### Modos de Falla y Remediación

| Síntoma | Causa | Remediación |
|---------|-------|-------------|
| Action `validate-tag.yml` falla con `Lightweight tag rejected` | El tag fue creado con `git tag NOMBRE` | Borrar local (`git tag -d`), recrear con `git tag -s NOMBRE -m`, empujar |
| `git tag -v` falla con `no signature found` | `tag.gpgSign` no está en `true`; clave GPG no configurada | Configurar `tag.gpgSign` + `user.signingkey` (ver arriba); recrear el tag |
| Push aceptado pero el Release no aparece | `validate-tag.yml` rechazó; el tag fue eliminado del remoto | Verificar el log de la Action; recrear el tag respetando las 3 reglas |
| `gh api -X DELETE refs/tags/$TAG` retorna 404 | Path incompleto (faltó `repos/:owner/:repo/git/`) | Usar el path completo |
| `git tag -v` en el runner emite `WARNING` sobre clave ausente | La clave pública del firmante no está en el runner; la firma fue validada localmente | Aceptar — la verificación en el runner es best-effort por diseño |

### Ejemplos Operacionales

**Flujo canónico — release minor:**

```bash
# 1. Confirmar HEAD del trunk y CI verde
git fetch origin
git checkout main && git pull
gh run list --commit "$(git rev-parse HEAD)" --limit 5 --json status,conclusion

# 2. Crear tag anotado + firmado
git tag -s v1.3.0 -m "Release v1.3.0: warrior-janus orchestrator"

# 3. Validar localmente antes del push
git tag -v v1.3.0

# 4. Empujar
git push origin v1.3.0

# 5. Aguardar validate-tag.yml + flujo de trabajo de release
gh run watch "$(gh run list --workflow validate-tag.yml --commit $(git rev-parse v1.3.0) \
                 --limit 1 --json databaseId --jq '.[0].databaseId')"
```

**Apuntando a un commit específico (no HEAD):**

```bash
git tag -s v1.3.0 -m "Release v1.3.0" abc123f
```

**Recuperación tras push de tag inválido:**

```bash
# Escenario: un tag lightweight llegó al remoto; la Action lo eliminó y falló
git tag -d v1.3.0                            # borra local (estaba lightweight)
git tag -s v1.3.0 -m "Release v1.3.0"        # recrea correctamente
git tag -v v1.3.0                            # confirma la firma local
git push origin v1.3.0                       # nuevo intento
```

### Restricciones Técnicas

- El tag **DEBE** ser creado localmente — la UI/API de GitHub no soportan tag anotado + firmado de forma nativa.
- `tag.gpgSign true` en Git **DEBE** estar configurado en el ambiente del agente/contribuyente antes del primer release.
- La Action `validate-tag.yml` **DEBE** estar presente en todo repositorio Guardia que adopte Ahrena — de lo contrario la regla es solo client-side y puede ser eludida.

## Referencias

- `lex-annotated-tags` — Ley que este Codex operacionaliza
- `lex-semantic-version` — Formato del nombre del tag
- `lex-signed-commits` — Misma raíz de firma GPG aplicada a commits
- `codex-semantic-version` — Manual de SemVer (companion de este Codex)
- `kata-tag` — Habilidad que aplica este manual para crear un tag
- `kata-release-publish` — Habilidad que empuja el tag y aguarda la validación
- [Git Tag — git-scm.com](https://git-scm.com/docs/git-tag)
- [`git tag -v` reference](https://git-scm.com/docs/git-tag#Documentation/git-tag.txt--v)
