# Cry: Nuevo Stacked Pull Request

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para iniciar una cadena de Pull Requests encadenados (stack) en el repositorio origin

## Invocación

```
/cry-new-stacked-pr [<issue-number>] [--draft]
```

## Parámetros

| Parámetro | Obligatorio | Descripción |
|-----------|:-----------:|-------------|
| `<issue-number>` | No | Número de la issue paraguas. Si se omite, el agente pregunta. |
| `--draft` | No | Crea todos los PRs de la stack como borrador. |

## Comportamiento

1. Invoca **kata-stacked-pr-create**.
2. La kata corre **Fase 0 — Decision Checklist** incluso en invocación explícita por el usuario, aplicando la checklist canónica definida en `codex-stacked-prs`.
3. **Si la checklist reprueba**, la kata avisa al usuario con las señales reales contadas, propone seguir con PR único vía `kata-contributing-pr`, y solo prosigue con la stack mediante override explícito del usuario (registrando la decisión).
4. **Si la checklist aprueba**, la kata propone descomposición concreta en capas (ver kata para detalles), confirma con el usuario y crea la cadena: worktree compartido, N branches, N PRs encadenados, espejo de labels.
5. La kata selecciona la herramienta operacional consultando la directiva `stacked_prs.tool` en `.ahrena/.directives`. Valores aceptados: `vanilla` (default — `git` + `gh`) y `gs` (git-spice — auto-restack documentado en `codex-git-spice`). Cada valor activa la sección correspondiente de la Kata (procedimiento principal vs. sección "Variant: git-spice"); el Cry no lee la directiva directamente.

## Kata Asociada

`kata-stacked-pr-create` — Procedimiento para descomponer una feature en stack y crear la cadena de PRs.

## Restricciones

- **Nunca** prosigue sin confirmación explícita del usuario sobre la descomposición en capas
- **Nunca** ignora anti-señales sin override consciente del usuario
- Si la issue paraguas no atiende `lex-issue-quality`, alerta y para — la issue debe corregirse antes
- Si `stacked_prs.tool` no está declarado en `.ahrena/.directives`, asume `vanilla`

## Referencias

- `kata-stacked-pr-create` — Kata invocada por este Cry
- `codex-stacked-prs` — Decision Checklist canónica y modelo conceptual
- `codex-git-spice` — Manual de la variante `gs` cuando el proyecto declara `stacked_prs.tool: gs`
- `kata-contributing-pr` — Fallback para PR único
- `cry-new-pr` — Atajo equivalente para PR único
- `lex-issue-first`, `lex-issue-quality`, `lex-git-branches`, `lex-pr-quality` — Lexis aplicables
