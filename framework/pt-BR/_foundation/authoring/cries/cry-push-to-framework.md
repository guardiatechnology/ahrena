# Cry: Push para o Framework

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Incorporação de artefatos de projeto ao framework

## Descrição

Comando rápido para incorporar ao framework canônico os artefatos criados no espaço do projeto (`.ahrena/artifacts/`). Invoca o `kata-push-to-framework`, que copia os arquivos para `framework/`, garante traduções nos idiomas obrigatórios e opcionalmente remove as cópias do projeto.

## Uso

```
/cry-push-to-framework [alvo] [--remove]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `alvo` | Não | Caminho(s) em `.ahrena/artifacts/` ou "todos". Se omitido, processa todos os artefatos encontrados | `pt-BR/engineering/quality/lexis/lex-foo.md` ou `todos` |
| `--remove` | Não | Se presente, remove os artefatos de `.ahrena/artifacts/` após copiar para o framework | `--remove` |

## O que o Comando Faz

1. Lê `.ahrena/.directives` para obter `paths.project_artifacts`, `paths.framework` e `language.i18n`
2. Identifica os artefatos em `.ahrena/artifacts/` (todos ou os indicados)
3. Executa `kata-push-to-framework` com os parâmetros fornecidos
4. Copia os artefatos para `framework/` e gera traduções faltantes
5. Opcionalmente remove os arquivos do projeto
6. Reporta os arquivos incorporados

## Prompt Template

```
Contexto:
- Alvo: {{alvo}} (ou todos os artefatos em .ahrena/artifacts/)
- Remover do projeto após Push: {{--remove}}

Tarefa:
Execute o kata-push-to-framework. Consulte .ahrena/.directives para
paths.project_artifacts e language.i18n. Incorpore os artefatos ao
framework e garanta versões em todos os idiomas obrigatórios.

Formato de saída:
Lista de arquivos copiados para framework/ e traduções criadas (se houver).
Se --remove foi usado, confirmação de remoção em .ahrena/artifacts/.
```

## Exemplo de Invocação

**Incorporar todos os artefatos do projeto:**

```
/cry-push-to-framework
```

**Incorporar um artefato específico:**

```
/cry-push-to-framework pt-BR/engineering/quality/lexis/lex-code-review.md
```

**Incorporar e remover do projeto:**

```
/cry-push-to-framework todos --remove
```

## Restrições

- Só incorpora artefatos que estejam sob `.ahrena/artifacts/` com estrutura válida (lang/clade/subclade/pilar)
- Sempre executa `kata-push-to-framework` (nunca faz a cópia diretamente sem o Kata)

## Referências

- `kata-push-to-framework` — Procedimento executado por este Cry
- `codex-pilars` — Fluxo recomendado (criar no projeto → validar → Push)
