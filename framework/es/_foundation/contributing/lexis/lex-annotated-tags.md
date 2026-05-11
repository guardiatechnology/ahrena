# Lexis: Tags Anotados y Firmados

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Tags Git en repositorios Guardia

## Ley

> **Todo tag empujado a un remoto Guardia DEBE ser un tag anotado (`git tag -a`) firmado con clave GPG (`git tag -s`). Empujar un tag lightweight (creado sin `-a`/`-s`/`-m`) a `origin` está PROHIBIDO. El tag DEBE seguir Semantic Versioning conforme `lex-semantic-version` y la firma DEBE ser verificable conforme `lex-signed-commits`.**

## Alcance

- **Se aplica a:** todos los tags Git empujados a cualquier remoto Guardia (release, pre-release, internos). Los tags locales no publicados están fuera del alcance de la regla, pero quedarán sujetos a ella al ser empujados.
- **Agentes vinculados:** todos los contribuyentes (humanos e IA) — incluyendo `warrior-janus`, `warrior-athena`, y cualquier Kata que cree un tag (`kata-tag`, `kata-release-publish`).
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones. Los tags lightweight preexistentes en el historial del remoto permanecen (la regla es forward-looking) — no hay migración retroactiva.

## Reglas

### 1. Tag anotado con mensaje

Todo tag DEBE ser creado con `git tag -a` (o `-s`, que implica `-a`) y un mensaje explícito vía `-m` o el editor. Los tags lightweight (`git tag NOMBRE`) carecen de autor, fecha, mensaje y firma — no satisfacen esta Lex.

```bash
# Correcto
git tag -a v1.2.3 -m "Release v1.2.3"

# Correcto (firmado, implica anotado)
git tag -s v1.2.3 -m "Release v1.2.3"

# INCORRECTO — lightweight
git tag v1.2.3
```

### 2. Firma GPG obligatoria

Todo tag empujado DEBE ser firmado con GPG (`git tag -s`). Un tag lightweight es técnicamente incapaz de portar firma — solamente los tags anotados soportan GPG. La firma DEBE ser verificable vía `git tag -v <tag>`.

Configuración recomendada para firma automática:

```bash
git config --global tag.gpgSign true
git config --global user.signingkey <GPG-KEY-ID>
```

### 3. Versionado Semántico

El nombre del tag DEBE seguir el formato definido en `lex-semantic-version` (`vMAJOR.MINOR.PATCH`, con pre-release y metadatos de build opcionales). Los tags fuera del formato SemVer son rechazados por la validación combinada de las dos Lexis.

### 4. Validación server-side

El flujo de trabajo `.github/workflows/validate-tag.yml` DEBE estar configurado en todo repositorio Guardia que adopte Ahrena. Ese flujo de trabajo:

- Se dispara en `on: push: tags: ['*']`.
- Ejecuta `git cat-file -t $TAG`; falla cuando el tipo retornado no es `tag` (lightweight retorna `commit`).
- Ejecuta `git tag -v $TAG`; falla cuando la firma no verifica.
- Elimina el tag remoto (`gh api -X DELETE refs/tags/$TAG`) antes de finalizar con error, evitando que otros flujos de trabajo reactivos consuman un tag inválido.

### 5. Sin creación directa en el remoto

La creación de tag vía UI/API de GitHub (que produce lightweight tag automáticamente) está PROHIBIDA. Los tags DEBEN nacer localmente, con `git tag -a -s`, y ser empujados vía `git push origin <tag>`.

## HARD-GATE

Conforme [`lex-hard-gate-pattern`](../../quality/lexis/lex-hard-gate-pattern.md), el bloqueo textual de esta Lex se expresa canónicamente como:

```
<HARD-GATE>
warrior-janus, warrior-athena y cualquier otro agente (humano o IA)
NO DEBE empujar tag a remoto Guardia sin que satisfaga TODOS los
criterios:

  (a) Fue creado con `git tag -a` (anotado)
  (b) Fue firmado con `git tag -s` (GPG)
  (c) `git tag -v <tag>` confirma firma válida
  (d) El nombre sigue Semantic Versioning (lex-semantic-version)
  (e) El repositorio destino tiene `.github/workflows/validate-tag.yml` activo

Esta regla se aplica a TODO tag, independientemente de:
  - propósito declarado ("es solo un tag de debug")
  - urgencia ("necesito publicar ahora")
  - tipo de release (major, minor, patch, pre-release)
  - tamaño percibido del cambio

Excepción única declarada: Ninguna. Los tags lightweight preexistentes
en el historial permanecen (regla forward-looking); no hay migración
retroactiva, pero ningún tag lightweight nuevo puede ser empujado.
</HARD-GATE>
```

## Consecuencias de Violación

1. **Bloqueo automático:** el flujo de trabajo `validate-tag.yml` elimina el tag remoto y falla la ejecución.
2. **Alerta:** el autor del push recibe notificación del Action en falla; el release que dependería del tag no ocurre.
3. **Remediación:** recrear el tag localmente con `git tag -a -s -m`, validar con `git tag -v`, y empujar nuevamente.

## Ejemplos

### Correcto

```bash
# Maintainer crea tag anotado y firmado
git tag -a v1.2.3 -s -m "Release v1.2.3: warrior-janus orchestrator"
git tag -v v1.2.3   # confirma firma
git push origin v1.2.3

# validate-tag.yml se dispara, valida, concluye con éxito
# release.yml se dispara después, crea GitHub Release
```

### Incorrecto

```bash
# Lightweight tag — VIOLA LA LEY
git tag v1.2.3
git push origin v1.2.3
# → validate-tag.yml: `git cat-file -t v1.2.3` retorna `commit` (no `tag`)
# → tag eliminado del remoto, flujo de trabajo falla

# Tag anotado pero no firmado — VIOLA LA LEY
git tag -a v1.2.3 -m "Release"
git push origin v1.2.3
# → validate-tag.yml: `git tag -v v1.2.3` falla (sin firma)
# → tag eliminado del remoto, flujo de trabajo falla

# Tag creado vía UI de GitHub — VIOLA LA LEY
# (la UI siempre genera lightweight tag, sin firma local)
```

## Validación Automatizada

- **Herramienta:** flujo de trabajo `.github/workflows/validate-tag.yml` (server-side, autoritativo) + `kata-release-publish` (client-side, preventivo).
- **Momento:** al empujar tag a `origin` (server-side); al orquestar release (client-side).
- **Métrica:** 0 tags lightweight en `origin` después de que esta Lex entre en vigor; 100% de los tags con firma GPG verificable.

## Referencias

- `lex-semantic-version` — formato MAJOR.MINOR.PATCH para el nombre del tag
- `lex-signed-commits` — firma GPG (misma raíz; los tags refuerzan el mismo principio)
- `kata-tag` — procedimiento de creación de tag (usa `git tag -a -s`)
- `kata-release-publish` — Kata orquestrador de Janus que invoca `kata-tag`
- `warrior-janus` — Warrior orquestrador del ciclo de release
- [Git Tag — git-scm.com](https://git-scm.com/docs/git-tag)
