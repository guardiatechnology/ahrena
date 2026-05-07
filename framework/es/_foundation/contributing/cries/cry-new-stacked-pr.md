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
2. La kata corre **Fase 0 — Decision Checklist** incluso en invocación explícita por el usuario, usando los criterios canónicos de `codex-stacked-prs` (≥ 3 señales altas AND 0 anti-señales).
3. **Si la checklist reprueba** (anti-señal presente o señales altas < 3), el agente avisa:
   ```
   Esta issue no atiende la checklist canónica para stacked PR:
     Señales altas: X (mínimo 3)
     Anti-señales detectadas: [lista]

   Propuesta: proseguir con PR único vía kata-contributing-pr.

   ¿Forzar la stack de todas formas? (s/n)
   ```
   - Si `n` (default), redirige a `kata-contributing-pr` (PR único)
   - Si `s` (override explícito del usuario), prosigue con la stack registrando la decisión de override
4. **Si la checklist aprueba**, la kata propone descomposición concreta en capas (ver kata para detalles), confirma con el usuario y crea la cadena: worktree compartido, N branches, N PRs encadenados, espejo de labels.
5. Lee `.ahrena/.directives` para `stacked_prs.tool`:
   - `vanilla` (default) → sigue el flujo de esta Kata
   - `gs` → sigue la sección "Variant: git-spice" de la Kata (disponible tras plan-005)

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
- `kata-contributing-pr` — Fallback para PR único
- `cry-new-pr` — Atajo equivalente para PR único
- `lex-issue-first`, `lex-issue-quality`, `lex-git-branches`, `lex-pr-quality` — Lexis aplicables
