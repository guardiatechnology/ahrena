# Lexis: Tags Anotados y Firmados

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Tags Git en repositorios Guardia

## Ley

> **Todo tag empujado a un remoto Guardia DEBE ser un tag anotado (no lightweight) firmado con clave GPG. Empujar un tag lightweight a `origin` está PROHIBIDO. El tag DEBE seguir Semantic Versioning conforme `lex-semantic-version` y la firma DEBE ser verificable localmente antes del push conforme `lex-signed-commits`.**

## Alcance

- **Se aplica a:** todos los tags Git empujados a cualquier remoto Guardia (release, pre-release, internos). Los tags locales no publicados están fuera del alcance de la regla, pero quedarán sujetos a ella al ser empujados.
- **Agentes vinculados:** todos los contribuyentes (humanos e IA) — incluyendo `warrior-janus`, `warrior-athena`, y cualquier Kata que cree un tag (`kata-tag`, `kata-release-publish`).
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones. Los tags lightweight preexistentes en el historial del remoto permanecen (la regla es forward-looking) — no hay migración retroactiva.

## Reglas

### 1. Tipo del objeto: anotado

Todo tag empujado DEBE ser del tipo `tag` en Git (objeto propio, con autor, fecha, mensaje y firma). Los tags lightweight (solo puntero a un commit, sin objeto propio) no satisfacen esta Lex.

### 2. Firma GPG obligatoria

Todo tag empujado DEBE estar firmado con GPG. Los tags lightweight son técnicamente incapaces de cargar firma — solamente los tags anotados soportan GPG. La firma DEBE ser verificada localmente antes del push.

### 3. Versionado Semántico

El nombre del tag DEBE seguir el formato definido en `lex-semantic-version` (MAJOR.MINOR.PATCH, con pre-release y metadatos de build opcionales). Los tags fuera del formato SemVer son rechazados por la validación combinada de las dos Lexis.

### 4. Validación server-side obligatoria

Todo repositorio Guardia que adopte Ahrena DEBE tener el flujo de trabajo `.github/workflows/validate-tag.yml` activo. Ese flujo de trabajo:

- Bloquea tags lightweight (verifica el tipo del objeto en el remoto).
- Bloquea tags fuera del formato SemVer.
- Verifica la firma GPG en best-effort (sin fallar cuando la clave pública no está disponible al runner — la firma es regla local autoritativa).
- Elimina el tag remoto inválido antes de finalizar con error, evitando que los flujos de trabajo reactivos consuman un tag inválido.

### 5. Sin creación directa en el remoto

La creación de tag vía UI/API de GitHub (que produce lightweight tag automáticamente) está PROHIBIDA. Los tags DEBEN nacer localmente, ser firmados localmente, y ser empujados vía `git push`.

## HARD-GATE

Conforme [`lex-hard-gate-pattern`](../../quality/lexis/lex-hard-gate-pattern.md), el bloqueo textual de esta Lex se expresa canónicamente como:

```
<HARD-GATE>
warrior-janus, warrior-athena y cualquier otro agente (humano o IA)
NO DEBE empujar tag a remoto Guardia sin que satisfaga TODOS los
criterios:

  (a) El tag es del tipo `tag` en Git (anotado — no lightweight)
  (b) El tag está firmado con GPG y la firma fue verificada
      localmente antes del push
  (c) El nombre sigue Semantic Versioning (lex-semantic-version)
  (d) El repositorio destino tiene `.github/workflows/validate-tag.yml` activo

Esta regla se aplica a TODO tag, independientemente de:
  - propósito declarado ("es solo un tag de debug")
  - urgencia ("necesito publicar ahora")
  - tipo de release (major, minor, patch, pre-release)
  - tamaño percibido del cambio

Excepción única declarada: Ninguna. Los tags lightweight preexistentes
en el historial permanecen (regla forward-looking); no hay migración
retroactiva, pero ningún tag lightweight nuevo puede ser empujado.

Nota: la verificación server-side de firma GPG es best-effort
(depende de que la clave pública esté disponible al runner). El
bloqueo duro server-side queda en (a) "anotado" + (c) "SemVer-
válido"; la firma se exige localmente antes del push.
</HARD-GATE>
```

## Consecuencias de Violación

1. **Bloqueo automático:** el flujo de trabajo `validate-tag.yml` elimina el tag remoto y falla la ejecución.
2. **Alerta:** el autor del push recibe la notificación del Action en falla; el release que dependería del tag no ocurre.
3. **Remediación:** recrear el tag localmente como anotado + firmado, validar localmente, y empujar nuevamente.

## Validación Automatizada

- **Herramienta:** flujo de trabajo `.github/workflows/validate-tag.yml` (server-side, autoritativo) + verificación local antes del push por parte del agente/contribuyente.
- **Momento:** al empujar el tag a `origin` (server-side); antes del push (client-side).
- **Métrica:** 0 tags lightweight en `origin` después de que esta Lex entre en vigor; 100% de los tags con firma GPG verificable localmente.

## Referencias

- `lex-semantic-version` — formato MAJOR.MINOR.PATCH para el nombre del tag
- `lex-signed-commits` — firma GPG (misma raíz aplicada a commits)
- [Git Tag — git-scm.com](https://git-scm.com/docs/git-tag)
