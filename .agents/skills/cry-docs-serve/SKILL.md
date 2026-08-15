---
name: cry-docs-serve
description: "cry-docs-serve. Servidor local MkDocs de documentação para qualquer diretório Markdown"
---

# Cry: cry-docs-serve

> **Prefixo:** `cry-` | **Tipo:** Comando de Execução | **Escopo:** Servidor local MkDocs de documentação para qualquer diretório Markdown

## Quando Usar

- Após executar `cry-feature-design`, `cry-api-design` ou `cry-event-storm`, para revisar os documentos gerados como um site unificado
- Quando quiser navegar por modelos de domínio, especificações de API e documentos de eventos localmente antes de commitar
- Quando a documentação do projeto está fora de `docs/` (ex.: `framework/` no Ahrena)

## Sintaxe

```
/cry-docs-serve [docs-path] [port]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição |
|-----------|:-----------:|-----------|
| `docs-path` | Não | Caminho do diretório a servir (ex.: `framework/`, `docs/`). Se omitido, o caminho é derivado de `.directives` (`paths.domain`, `paths.oas`, `paths.events`). |
| `port` | Não | Porta para o servidor. Padrão: `8000`. |

## Invoca

| Kata | Descrição |
|------|-----------|
| `kata-docs-serve` | Verifica a instalação do MkDocs, resolve `docs_dir`, gera `mkdocs.yml` se ausente e inicia o servidor |

## Exemplos

```
/cry-docs-serve
```
Deriva o diretório de documentação de `.directives` e o serve em `http://127.0.0.1:8000`.

---

```
/cry-docs-serve framework/
```
Serve o diretório `framework/` em `http://127.0.0.1:8000`. Use este comando no repositório Ahrena, onde o próprio framework é a documentação.

---

```
/cry-docs-serve docs/
```
Serve explicitamente `docs/` em `http://127.0.0.1:8000`.

---

```
/cry-docs-serve framework/ 8080
```
Serve `framework/` em `http://127.0.0.1:8080`.

## Entregável

Um servidor MkDocs rodando em `http://127.0.0.1:{port}` servindo todos os arquivos `.md` no diretório especificado ou derivado, com hot-reload ao detectar alterações nos arquivos.

## Observações

- O servidor roda em primeiro plano; pare-o com `Ctrl+C`.
- Quando `docs-path` é omitido, o diretório pai comum de `paths.domain`, `paths.oas` e `paths.events` em `.directives` é utilizado.
- Se `mkdocs.yml` não existir na raiz do projeto, um arquivo mínimo é gerado automaticamente (nunca sobrescreve um arquivo existente).
- O tema Material (`mkdocs-material`) é utilizado quando disponível; caso contrário, o tema padrão do MkDocs é aplicado.
