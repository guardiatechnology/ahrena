# Cry: Build de skill

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para invocar `kata-build-skill` e produzir `.build/{slug}/` + zip a partir da fonte versionada

## Descrição

Atalho que invoca `kata-build-skill` para um projeto em `{paths.skills_root}/{slug}/`, executando o pipeline determinístico (Validate → Build widgets → Freeze scripts → Resolve tools → Rewrite bindings → Emit) descrito em `codex-skill-build-pipeline`. O resultado é `{paths.skills_build}/{slug}/` + `{paths.skills_build}/{slug}.zip`, testáveis em outro agente Claude Code antes do empacotamento final em `.dist/` (PR 3).

## Uso

```
/cry-skill-build <slug> [opções]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `slug` | Sim | Projeto em `{paths.skills_root}/{slug}/` | `hello-skill` |
| `clean` | Não | `true` apaga `.build/{slug}/` antes; default `false` | `clean=true` |
| `skip_zip` | Não | `true` pula a emissão do zip; default `false` | `skip_zip=true` |

## O que o Comando Faz

1. Resolve `paths.skills_root`, `paths.skills_build` em `.ahrena/.directives`
2. Confirma existência do projeto fonte
3. Invoca `kata-build-skill` com os parâmetros
4. Reporta caminho de saída, hash sha256 e tamanho do zip
5. Sugere passo seguinte (carregar zip em outro agente para teste, ou aguardar `kata-package-skill` no PR 3)

## Prompt Template

```
Contexto:
- slug: {{slug}}
- clean: {{clean}} (opcional, default false)
- skip_zip: {{skip_zip}} (opcional, default false)

Tarefa:
Invoque kata-build-skill com os parâmetros acima. O kata:
1. Resolve paths e config
2. Phase 1 — Validate (frontmatter, skill.config, manifests)
3. Phase 2 — Build widgets (Vite production)
4. Phase 3 — Freeze scripts (lock preservado, sem instalação)
5. Phase 4 — Resolve tools (handler refs validadas)
6. Phase 5 — Rewrite bindings (called_via dev → called_via_prod)
7. Phase 6 — Emit (.build/ + .skill-manifest.json + zip)
8. Validar idempotência

Aborte na primeira falha de qualquer phase.

Formato de saída:
Caminho de .build/, hash sha256 do zip, tamanho. Em caso de erro,
mensagem específica indicando phase e regra violada.
```

## Exemplo de Invocação

```
/cry-skill-build hello-skill
```

**Saída esperada:**

```
✅ Build de hello-skill concluído.
   Saída: .build/hello-skill/
   Zip:   .build/hello-skill.zip   (124 KB)
   sha256: 7a8c…

Próximos passos:
- Carregar o zip em outro agente Claude Code para teste manual
- kata-package-skill (PR 3) entrega .dist/hello-skill.skill auditável
```

## Restrições

- O Cry **não modifica** `skills/{slug}/` (apenas leitura)
- O Cry **não toca** `.dist/`
- Mensagens ao usuário em `language.default`; identificadores técnicos preservados
- `lex-terminal-type`: comandos shell respeitam o terminal definido

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Atalho 1:1 | Pipeline em 9 passos (6 phases + validação + report) |
| **Validação** | Forma dos parâmetros | Frontmatter, manifests, refs, idempotência |
| **Efeito** | Invoca o kata | Escreve `.build/{slug}/` + zip + manifest |

## Referências

- `kata-build-skill` — procedimento invocado
- `codex-skill-build-pipeline` — contrato do pipeline
- `codex-skill-tools-and-widgets` — schemas dos manifestos
- `lex-skill-project-structure` — separação fonte/build/dist
- `cry-skill-dev` — passo anterior natural (validação manual)
- `kata-package-skill` (PR 3) — consumidor do `.build/` para `.dist/`
