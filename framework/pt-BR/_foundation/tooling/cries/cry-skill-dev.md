# Cry: Dev server local de skill

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para levantar widgets HMR + script runner + tool stub em localhost para um projeto de skill

## Descrição

Atalho que invoca `kata-skill-dev-server` para levantar o ambiente de desenvolvimento local de um skill em `{paths.skills_root}/{slug}/`. Sobe somente os subservidores aplicáveis ao projeto (widgets/scripts/tools) conforme presença de cada subdiretório. Ports default são `5173` (widgets), `5174` (scripts), `5175` (tool stub), com override via parâmetros.

## Uso

```
/cry-skill-dev <slug> [opções]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `slug` | Sim | Projeto em `{paths.skills_root}/{slug}/` | `hello-skill` |
| `widgets_port=` | Não | Override (default `5173` ou `dev_server.widgets_port`) | `widgets_port=5180` |
| `scripts_port=` | Não | Override (default `5174`) | `scripts_port=5181` |
| `tools_stub_port=` | Não | Override (default `5175`) | `tools_stub_port=5182` |
| `only=` | Não | Subconjunto (`widgets`, `scripts`, `tools`); default todos | `only=widgets` |

## O que o Comando Faz

1. Resolve `paths.skills_root` em `.ahrena/.directives`
2. Confirma existência do projeto e leitura de `skill.config.json`
3. Invoca `kata-skill-dev-server` com os parâmetros recebidos
4. Mantém foreground com logs prefixados (`[widgets]`, `[scripts]`, `[tools]`) até Ctrl-C

## Prompt Template

```
Contexto:
- slug: {{slug}}
- widgets_port: {{widgets_port}} (opcional)
- scripts_port: {{scripts_port}} (opcional)
- tools_stub_port: {{tools_stub_port}} (opcional)
- only: {{only}} (opcional)

Tarefa:
Invoque kata-skill-dev-server com os parâmetros acima. O kata:
1. Resolve paths e config
2. Verifica pré-condições (manifestos, deps, ports)
3. Sobe widgets (Vite HMR), script runner e tool stub conforme aplicável
4. Reporta URLs e instruções
5. Mantém foreground até interrupção do usuário

Aborte se: projeto inexistente, manifest inválido, port ocupada sem override.

Formato de saída:
URLs ativas + foreground com logs até Ctrl-C. Em caso de erro, mensagem
específica e correção sugerida.
```

## Exemplo de Invocação

```
/cry-skill-dev hello-skill
```

**Saída esperada:**

```
✅ Dev server ativo para hello-skill:
   Widgets:      http://localhost:5173/        (HMR Vite)
   (sem scripts/ — pulado)
   (sem tools/ — pulado)

Pressione Ctrl-C para encerrar.
```

## Restrições

- O Cry **não modifica** `skills/{slug}/` (apenas leitura)
- O Cry **não escreve** em `.build/` ou `.dist/`
- Mensagens ao usuário em `language.default`; identificadores técnicos preservados
- `lex-terminal-type`: respeita o terminal definido em `.directives`

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Atalho 1:1 | Procedimento operacional (7 passos) |
| **Validação** | Forma dos parâmetros | Pré-condições, manifestos, ports |
| **Efeito** | Invoca o kata | Levanta processos, mantém foreground |

## Referências

- `kata-skill-dev-server` — procedimento invocado
- `codex-skill-build-pipeline` — defaults de tooling e ports
- `codex-skill-tools-and-widgets` — schemas validados antes de subir
- `cry-skill-build` — passo seguinte para gerar `.build/`
