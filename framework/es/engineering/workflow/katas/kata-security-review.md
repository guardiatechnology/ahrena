# Kata: Revisión de Seguridad

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Fase 5 del flujo Issue-Driven — revisión de seguridad del código implementado contra OWASP Top 10, patrones de autenticación/autorización, manejo de datos sensibles y dependencias vulnerables

## Objetivo

Ejecutar revisión de seguridad sobre el código implementado en la Fase 4, identificando vulnerabilidades conocidas (OWASP Top 10), problemas de autenticación/autorización, exposición de datos sensibles, credenciales en código y dependencias con CVEs conocidos. Produce informe en `.issues/{n}/05-security-review.md` con severidad clasificada; los hallazgos críticos bloquean el Gate 2.

## Cuándo Usar

- Fase 5 del flujo orquestado por `warrior-athena`, tras que Apollo (o warrior equivalente) concluya la implementación en la Fase 4
- Cuando es necesario auditar cambios de código por riesgos de seguridad antes de crear el PR

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| Diff de la implementación | Sí | `git diff` entre branch de trabajo y branch base |
| Requisitos Fase 2 | Sí | `.issues/{n}/02-requirements.md` |
| Arquitectura Fase 3 | Sí | `.issues/{n}/03-architecture.md` (incluye integraciones externas) |

## Workflow

```
Progreso:
- [ ] 1. Recolectar diff y contexto
- [ ] 2. OWASP Top 10 check
- [ ] 3. Autenticación y autorización
- [ ] 4. Datos sensibles y credenciales
- [ ] 5. Dependencias (CVE scan)
- [ ] 6. Consolidar informe con severidad
- [ ] 7. Persistir en .issues/{n}/05-security-review.md
- [ ] 8. Actualizar checkpoint
```

### Paso 1: Recolectar diff y contexto

1. Ejecutar `git diff {base-branch}...HEAD` o equivalente.
2. Leer `03-architecture.md` para entender las integraciones externas involucradas.
3. Leer `02-requirements.md` para identificar ACs con implicancias de seguridad (ej.: autenticación, autorización, datos sensibles).

### Paso 2: OWASP Top 10 check

Para cada categoría, verificar explícitamente en el diff:

| Categoría | Verificación |
|---|---|
| **A01 — Broken Access Control** | ¿Los endpoints nuevos tienen verificación de autorización (RBAC, ABAC)? ¿Ownership check cuando aplica? |
| **A02 — Cryptographic Failures** | ¿Datos sensibles en tránsito/reposo cifrados? ¿Uso correcto de algoritmos (no MD5/SHA1)? |
| **A03 — Injection** | ¿Queries SQL parametrizadas? ¿Inputs validados antes de uso en comandos/queries? |
| **A04 — Insecure Design** | ¿Patrones inseguros (ej.: tokens predecibles, timeouts excesivos)? |
| **A05 — Security Misconfiguration** | ¿Headers de seguridad configurados? ¿Modo debug deshabilitado? |
| **A06 — Vulnerable Components** | (ver Paso 5) |
| **A07 — Identification & Auth Failures** | ¿Rate limiting en endpoints de auth? ¿Protección brute-force? ¿Gestión de sesión correcta? |
| **A08 — Software & Data Integrity Failures** | ¿Firmas verificadas? ¿Deserialización segura? |
| **A09 — Security Logging Failures** | ¿Los eventos relevantes (auth, acceso a datos sensibles) se loguean? ¿Los logs contienen datos sensibles? |
| **A10 — SSRF** | ¿Las URLs de entrada se validan contra allowlist? |

Registrar cada hallazgo con: categoría OWASP, archivo/línea, severidad (`crítica`/`alta`/`media`/`baja`), recomendación.

### Paso 3: Autenticación y autorización

Si la issue involucra endpoints HTTP:

1. ¿Cada endpoint nuevo tiene verificación de auth? (bearer token, OAuth2, etc.)
2. ¿Cada operación tiene verificación de permiso (RBAC)?
3. Ownership check: ¿el usuario solo puede operar en recursos que posee?
4. ¿La información en tokens no filtra datos sensibles?

Si involucra consumo/publicación de eventos:

1. ¿Los eventos de alto privilegio exigen firma/verificación?
2. ¿Los eventos contienen solo IDs y no datos sensibles en el payload?

### Paso 4: Datos sensibles y credenciales

1. Scan por patrones de credenciales en el diff: `password`, `secret`, `api_key`, `token`, strings que parecen llaves.
2. Verificar `.env`, `.env.example`: solo placeholders, nunca valores reales.
3. ¿Datos sensibles (RUT, email, tarjeta) en logs? Deben estar enmascarados/redacted.
4. ¿Datos sensibles en mensajes de error retornados al cliente? No deben filtrarse.
5. ¿Datos sensibles en responses de API que el cliente no necesita? Remover.

### Paso 5: Dependencias (CVE scan)

1. Si hubo cambios en archivos de dependencias (`pyproject.toml`, `requirements.txt`, `package.json`, `Cargo.toml`, etc.), ejecutar scan:
   - Python: `pip-audit` o `safety check`
   - Node: `yarn audit` o `npm audit`
   - Rust: `cargo audit`
2. Clasificar CVEs encontrados por severidad (CVSS).
3. CVEs críticos (CVSS ≥ 9.0) en dependencias usadas en el código tocado → severidad crítica en el informe.

### Paso 6: Consolidar informe con severidad

Consolidar todos los hallazgos en una lista priorizada:

- **Críticos** — bloquean el Gate 2; deben resolverse antes de reabrir.
- **Altos** — deben resolverse antes del merge del PR.
- **Medios** — registrar como TODOs en el PR; puede resolverse en iteración futura.
- **Bajos** — nota informacional.

Si **cero hallazgos críticos o altos**, reportar `approved` para seguir al Gate 2.

### Paso 7: Persistir en `.issues/{n}/05-security-review.md`

Estructura:

```markdown
# Revisión de Seguridad — Issue #{n}: {título}

- **Referencia:** [Arquitectura](./03-architecture.md)
- **Fecha:** {YYYY-MM-DD}
- **Resultado global:** {approved | changes-required | blocked}

## Resumen

- Críticos: {n}
- Altos: {m}
- Medios: {k}
- Bajos: {j}

## Hallazgos Críticos

### S-1: {título}
- **Categoría:** OWASP A{nn} — {nombre}
- **Ubicación:** `{archivo}:{línea}`
- **Descripción:** {lo que hay}
- **Recomendación:** {cómo corregir}

## Hallazgos Altos

### S-2: ...

## Hallazgos Medios

### S-3: ...

## Hallazgos Bajos / Informacionales

### S-4: ...

## Dependencias

| Paquete | Versión | CVE | Severidad | Recomendación |
|---|---|---|---|---|
| ... | ... | CVE-XXXX-YYYY | {crítica/alta/...} | {upgrade a X} |

## Conclusión

{1-2 párrafos: status final, qué debe resolverse antes del Gate 2}
```

### Paso 8: Actualizar checkpoint

1. Actualizar `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - fase completada: 5
   - siguiente: 6 (Gate 2)
   - resultado: `approved`, `changes-required` o `blocked`
   - número de hallazgos por severidad
2. Informar a `warrior-athena`:
   - Si `approved`: seguir a la Fase 6
   - Si `changes-required` o `blocked`: regresar a la Fase 4 con el informe

## Salidas

| Salida | Formato | Destino |
|--------|---------|---------|
| Informe de seguridad | Markdown | `.issues/{n}/05-security-review.md` |
| Resultado | `approved` / `changes-required` / `blocked` | Retorno al orquestador |
| Checkpoint actualizado | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restricciones

- **No modificar código:** esta kata es solo de revisión; las correcciones se aplican en la Fase 4 en nueva iteración.
- **La severidad es bloqueante:** los hallazgos críticos siempre bloquean el Gate 2; no hay override automático.
- **Alcance limitado al diff:** no revisar código preexistente no tocado por el diff (sería tarea de auditoría separada).
- **Sin falsos positivos silenciosos:** si un hallazgo es falso positivo tras análisis, registrar explícitamente en el informe con justificación, no omitir.
- **Destino fijo:** `.issues/{n}/05-security-review.md` (según `lex-issue-driven`).

## Referencias

- `lex-issue-driven` — leyes del flujo
- `codex-issue-workflow` — posición de esta kata en el flujo
- `lex-python-security` — reglas de seguridad para código Python
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
