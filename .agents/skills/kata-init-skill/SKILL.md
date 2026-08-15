---
name: kata-init-skill
description: "Inicializar projeto de skill (scaffold). Scaffold de um novo projeto de skill em {paths.skills_root}/{slug}/ a partir do template framework/templates/skill-project-sample/"
---

# Kata: Inicializar projeto de skill (scaffold)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Scaffold de um novo projeto de skill em `{paths.skills_root}/{slug}/` a partir do template `framework/templates/skill-project-sample/`

## Workflow

```
Progresso:
- [ ] 1. Validar slug e description
- [ ] 2. Resolver paths e destino
- [ ] 3. Verificar pré-condições (template existe, destino livre)
- [ ] 4. Copiar template e substituir placeholders
- [ ] 5. Aplicar opt-outs (with_widgets/tools/scripts)
- [ ] 6. Garantir .gitignore com .build/
- [ ] 7. Validar resultado
- [ ] 8. Reportar
```

### Passo 1: Validar slug e description

1. Aplicar regex `^[a-z0-9](?:(?:[a-z0-9]|-(?!-)){0,62}[a-z0-9])?$` ao slug (1-64 chars, sem hífen no início/fim, sem `--`)
2. Rejeitar slugs com palavras reservadas (`anthropic`, `claude`) per documentação Anthropic
3. Verificar que `description` tem 1-1024 chars; rejeitar vazio
4. Em caso de violação, abortar com mensagem indicando a regra (citar `codex-skill-anthropic-agent-skills`)

### Passo 2: Resolver paths e destino

1. Ler `.ahrena/.directives` (per `lex-directives`); usar `paths.skills_root` (default `skills`), `paths.skills_build` (default `.build`), `paths.skills_dist` (default `.dist`)
2. Resolver `language` ausente para `language.default`
3. Calcular destino: `{paths.skills_root}/{slug}/`

### Passo 3: Verificar pré-condições

1. Confirmar que `framework/templates/skill-project-sample/` existe (origem)
2. Confirmar que o destino **não existe** — se existir, abortar com instrução de remover ou escolher outro slug; nunca sobrescrever
3. Garantir que `paths.skills_root` existe (criar diretório se ausente)

### Passo 4: Copiar template e substituir placeholders

1. Copiar a árvore de `framework/templates/skill-project-sample/` para `{paths.skills_root}/{slug}/`, **omitindo** o `README.md` raiz do template (documentação interna do framework)
2. Substituir placeholders nos arquivos copiados:

| Placeholder | Valor |
|-------------|-------|
| `__SLUG__` | `slug` |
| `__BCP47__` | `language` resolvido |
| `__HUMAN_TITLE__` | `human_title` (default: capitalização legível do slug) |
| `__ONE_SENTENCE_DESCRIPTION_INCLUDING_WHEN_TO_USE__` | `description` |
| `__LICENSE_OR_REFERENCE__` | `license` quando informado; quando ausente, **remover a linha `license:`** do frontmatter |

3. Substituição é literal (string-match), em todos os arquivos textuais (`.md`, `.json`, `.tsx`, `.ts`, `.py`, `package.json`, etc.)

### Passo 5: Aplicar opt-outs

1. `with_widgets=false`: remover diretório `widgets/`; remover menção a widgets no `SKILL.md` (seção "Tools, scripts, and widgets")
2. `with_tools=false`: remover diretório `tools/`
3. `with_scripts=false`: remover diretório `scripts/`
4. `with_scripts=js`: trocar valor `runtimes.scripts` no `skill.config.json` para `node`; ajustar `scripts/README.md` removendo seção Python; manter `scripts/` vazio com `.gitkeep`
5. `with_scripts=python`: manter como está (default do template)

### Passo 6: Garantir `.gitignore`

1. Verificar `.gitignore` na raiz do repositório
2. Se a entrada `{paths.skills_build}/` (ou `.build/` quando default) não existir, **adicioná-la** com cabeçalho de comentário:

```
# External skill projects — build intermediates (per lex-skill-project-structure)
.build/
```

3. Se já existir, não duplicar

### Passo 7: Validar resultado

1. Confirmar que `{paths.skills_root}/{slug}/SKILL.md` existe
2. Confirmar que `{paths.skills_root}/{slug}/skill.config.json` existe
3. Confirmar que o frontmatter de `SKILL.md` tem `name: {slug}` (validar igualdade)
4. Confirmar que **nenhum** placeholder `__...__` remanesce nos arquivos do projeto criado

### Passo 8: Reportar

1. Exibir ao usuário:
   - Caminho do projeto criado
   - Slug, description, language, license aplicados
   - Subdiretórios incluídos (widgets/scripts/tools, conforme opt-outs)
   - Próximos passos: editar `SKILL.md` corpo, adicionar componentes em `widgets/src/`, etc.
   - Sugestão de orquestração: `cry-skill --mode implement --slug <slug>` para passar a fase de autoria a `warrior-claudionor`
2. Apontar para `codex-skill-project-architecture` para autoria.

## Saídas

| Saída | Formato |
|-------|---------|
| Sucesso | Diretório `{paths.skills_root}/{slug}/` populado; `.gitignore` atualizado se necessário |
| Falha (slug inválido) | Mensagem citando `codex-skill-anthropic-agent-skills`; nenhum arquivo criado |
| Falha (destino existe) | Mensagem instruindo remover ou trocar slug; nenhum arquivo modificado |
| Falha (template ausente) | Mensagem indicando que `framework/templates/skill-project-sample/` está faltando — possível corrupção da instalação |

## Exemplo de Execução

### Input

```
/cry-new-skill scheduled-payments-skill \
  description="Schedules and approves bank transfers using widgets connected to Python tools. Use when the user wants to create or approve a scheduled transfer." \
  license=Apache-2.0
```

### Output esperado

```
✅ Projeto criado: skills/scheduled-payments-skill/
   ├── SKILL.md                 (name: scheduled-payments-skill, language: pt-BR, license: Apache-2.0)
   ├── skill.config.json
   ├── .skill-manifest.json
   ├── references/REFERENCE.md
   ├── scripts/                 (Python — pyproject.toml a adicionar quando começar)
   ├── tools/                   (mcp.config.json placeholder)
   └── widgets/                 (React — package.json + tsconfig.json prontos)

.gitignore atualizado: .build/ adicionado.

Próximos passos:
- Edite skills/scheduled-payments-skill/SKILL.md (corpo)
- Adicione componentes em widgets/src/
- Adicione handlers em tools/handlers/
- Para orquestrar autoria + validação + empacotamento, invoque:
    /cry-skill --mode implement --slug scheduled-payments-skill
```

## Restrições

- Não sobrescrever projeto existente
- Não modificar `.directives`
- Não tocar em `.build/` ou `.dist/` (essas pastas pertencem ao build e packaging dos PRs futuros)
- Toda mensagem ao usuário em pt-BR, es ou en conforme `language.default`; nomes técnicos (slug, frontmatter, placeholder) preservados
- Slug inválido aborta o kata sem efeito colateral
