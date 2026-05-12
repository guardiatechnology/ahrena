# Cry: Ciclo de Skill (implement / validate / package)

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para invocar `warrior-claudionor` e conduzir o ciclo `implement → validate → package` de um projeto de skill Anthropic Agent Skills

## Descrição

Atalho para o ciclo de skill após o scaffold inicial (`cry-new-skill`). Invoca `warrior-claudionor`, que orquestra um dos três katas (ou todos em sequência), com Hephaestus/Apollo delegados conforme o gap.

> **Quando preferir `cry-pov`:** se o objetivo é **PoV de agent** (provar valor para o cliente via stack Anthropic — Skills, Subagents, Plugins — com observabilidade nativa e value-proof), use `cry-pov` como entry point preferencial. `cry-pov --kind skill` dispara o ciclo POV completo (7 katas POV + `kata-skill-implement`) e produz `docs/{context}/agents-pov/` consumível por Mêtis via `--from-pov`. `cry-skill` permanece como entry point quando o objetivo é **empacotar uma skill como artefato distribuível** isolado do ciclo POV.

## Invocação

```
/cry-skill --mode <implement|validate|package|all> --slug <name> [--dry-run]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `--mode` | Sim | Fase do ciclo a executar: `implement` (autoria com delegação), `validate` (verificação determinística), `package` (build → dist + manifest), ou `all` (encadeia os três) | `--mode all` |
| `--slug` | Sim | Nome do projeto (idêntico ao nome do diretório em `{paths.skills_root}/`) | `--slug scheduled-payments-skill` |
| `--dry-run` | Não | Apresenta o plano sem persistir alterações em `{paths.skills_build}/`, `{paths.skills_dist}/` ou no projeto | `--dry-run` |

Se `--dry-run` for fornecido em `--mode package`, o pacote final não é escrito — apenas o relatório do que seria produzido.

## O que o Comando Faz

1. Resolve `paths.skills_root/skills_build/skills_dist` em `.ahrena/.directives`
2. Confirma que o projeto existe em `{paths.skills_root}/{slug}/`
3. Invoca `warrior-claudionor` passando `mode`, `slug` e `dry_run`
4. Claudionor despacha para o(s) kata(s):
   - `--mode implement` → `kata-skill-implement` (delega widgets a Hephaestus, tools/scripts Python a Apollo, redige `SKILL.md`/`references/`)
   - `--mode validate` → `kata-skill-validate` (verifica `lex-skill-project-structure`)
   - `--mode package` → `kata-skill-validate` (pré-condição) + `kata-skill-package` (build → dist + manifest validado contra `lex-skill-package-structure`)
   - `--mode all` → encadeia os três; aborta no primeiro erro
5. Reporta resultado final (paths produzidos, contagem de arquivos, violações)

## Prompt Template

```
Contexto:
- mode: {{mode}}             # implement | validate | package | all
- slug: {{slug}}
- dry_run: {{dry_run}}        # default false

Tarefa:
Invoque warrior-claudionor com os parâmetros acima. O warrior:
1. Lê .ahrena/.directives (paths.skills_*) e valida que skills/{slug}/ existe
2. Despacha para o(s) kata(s) conforme `mode`
3. Em `package` e `all`, aborta se kata-skill-validate retornar `error`
4. Em `implement`, delega via Agent a warrior-hephaestus (widgets) e
   warrior-apollo (tools/scripts Python); redige SKILL.md e references/
   in-house
5. Reporta paths produzidos, contagem de arquivos, violações por severidade

Aborte se: slug não existe em paths.skills_root, mode inválido, ou
.ahrena/.directives ausente.

Formato de saída:
Relatório estruturado por fase (implement / validate / package), com
delegações nominadas e estado final. Em caso de erro, identificar o
kata + regra violada e instrução de remediação.
```

## Exemplos de Invocação

```
# Ciclo completo: identifica gaps, implementa, valida e empacota
/cry-skill --mode all --slug scheduled-payments-skill

# Só validação determinística (CI ou pre-commit)
/cry-skill --mode validate --slug scheduled-payments-skill

# Só empacotamento (após desenvolvimento manual)
/cry-skill --mode package --slug scheduled-payments-skill

# Preview do que seria empacotado, sem escrever em .dist/
/cry-skill --mode package --slug scheduled-payments-skill --dry-run

# Só implementação (continuar de onde parou)
/cry-skill --mode implement --slug scheduled-payments-skill
```

**Saída esperada (`--mode all` em sucesso):**

```
🛠  warrior-claudionor — ciclo completo para 'scheduled-payments-skill'

Fase 1/3 — kata-skill-implement
  Delegações: Hephaestus (widgets), Apollo (tools + scripts)
  Arquivos produzidos: 4 widgets, 2 handlers, 1 teste
  SKILL.md + references/ atualizados

Fase 2/3 — kata-skill-validate
  ✅ no violations

Fase 3/3 — kata-skill-package
  ✅ package: .dist/scheduled-payments-skill.skill (18 arquivos)
```

## Restrições

- O Cry **não modifica** `.ahrena/.directives` nem `framework/`
- O Cry **não atua** sem um projeto existente em `{paths.skills_root}/{slug}/`; para criar um novo, use `cry-new-skill`
- O Cry **não cria** branch, worktree ou commit — disciplina de versionamento permanece com o usuário (`lex-issue-first`, `lex-git-worktrees`, `lex-pr-quality`)
- Mensagens humanas no idioma de `language.default`; identificadores técnicos (slug, modes, paths) preservados

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Atalho que coleta `--mode` + `--slug` e despacha | Procedimento completo (validate/package/implement, individualmente) |
| **Validação** | Forma dos parâmetros | Lógica de cada fase, com delegações |
| **Efeito** | Invoca `warrior-claudionor` | Lê/escreve filesystem, delega ou roda script |

## Referências

- `warrior-claudionor` — Warrior invocado por este Cry
- `kata-skill-implement` — invocado em `--mode implement` ou `all`
- `kata-skill-validate` — invocado em `--mode validate`, `package` e `all`
- `kata-skill-package` — invocado em `--mode package` e `all`
- `cry-new-skill` — antecessor (scaffold antes do ciclo)
- `lex-skill-project-structure`, `lex-skill-package-structure` — leis verificadas
- `lex-directives` — leitura de `paths.skills_*`
