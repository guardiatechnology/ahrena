# Lexis: Estrutura de Idiomas do Framework

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Estrutura de pastas e navegação por idioma dentro de `framework/`

## Propósito

O Ahrena adota uma abordagem de i18n baseada em pastas: o idioma é o **primeiro nível de navegação** dentro de `framework/`. Cada idioma possui sua própria árvore completa, espelhando a estrutura de clades, subclades e pilares.

Esta Lexis governa exclusivamente a **organização estrutural** de idiomas no framework — como as pastas são criadas, nomeadas e espelhadas. Para regras sobre **como traduzir conteúdo**, consulte `lex-language` e os artefatos por idioma em `documentation/i18n/`.

## Lei

> **O idioma DEVE ser o primeiro nível de navegação dentro de `framework/`, seguindo o endereçamento `{lang}/{clade}/{subclade}/{pilar}/{prefix}-{name}.{ext}`. Todo artefato DEVE existir em todos os idiomas definidos em `language.i18n`.**

## Regras

### 1. Idioma como raiz de navegação

Dentro de `framework/`, o primeiro nível de diretório é **sempre** o código do idioma conforme BCP 47 (ex: `pt-BR`, `es`, `en`). Toda a árvore de clades, subclades e pilares é replicada dentro de cada pasta de idioma:

```
framework/
├── pt-BR/
│   └── _foundation/process/lexis/lex-directives.md
├── es/
│   └── _foundation/process/lexis/lex-directives.md
└── en/
    └── _foundation/process/lexis/lex-directives.md
```

### 2. Completude obrigatória

Todo artefato criado no idioma padrão (`language.default`) **DEVE** ter versões correspondentes em todos os demais idiomas listados em `language.i18n`. Um artefato é considerado incompleto enquanto não existir em todos os idiomas obrigatórios.

### 3. Equivalência estrutural

As versões em diferentes idiomas **DEVEM** manter a mesma estrutura de diretórios. Se um artefato existe em `pt-BR/_foundation/process/lexis/lex-directives.md`, ele **DEVE** existir no mesmo caminho relativo em cada idioma.

### 4. Cursor em idioma único

Arquivos `.mdc` no diretório `.cursor/` **DEVEM** ser escritos exclusivamente no idioma definido em `language.cursor` no `.ahrena/.directives`. O Cursor **NÃO** utiliza pastas de idioma — apenas um idioma é mantido.

### 5. Propagação de alterações

Quando um artefato no idioma padrão é alterado, as versões nos demais idiomas **DEVEM** ser atualizadas. O agente que realiza a alteração **DEVE** sinalizar a necessidade de atualização das traduções.

### 6. Idioma padrão como fonte da verdade

O artefato no idioma definido em `language.default` é a **fonte da verdade**. Em caso de divergência entre versões, o conteúdo no idioma padrão prevalece.

### 7. Sem conteúdo solto na raiz

Nenhum artefato `.md` deve existir diretamente em `framework/` fora das pastas de idioma, exceto arquivos de meta-configuração como `.directives.sample`.

## Abrangência

- **Aplica-se a:** estrutura de diretórios dentro de `framework/`
- **Agentes vinculados:** todos os Warriors e agentes genéricos
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Artefato incompleto:** um artefato que não exista em todos os idiomas obrigatórios é considerado incompleto.
2. **Navegação quebrada:** artefatos fora da estrutura `{lang}/` quebram a navegabilidade do framework.
3. **Remediação:** o agente deve criar as pastas e versões faltantes, utilizando o `warrior-translator` de `documentation/i18n/`.

## Exemplos

### Correto

```
framework/pt-BR/_foundation/process/lexis/lex-directives.md
framework/es/_foundation/process/lexis/lex-directives.md
framework/en/_foundation/process/lexis/lex-directives.md
# Mesmo path relativo em cada idioma; artefato completo em language.i18n.
```

### Incorreto

```
framework/lex-directives.md
# ❌ Artefato fora da pasta de idioma; quebra o endereçamento {lang}/{clade}/...

framework/pt-BR/_foundation/process/lexis/lex-directives.md
# Existe só em pt-BR; faltam es e en.
# ❌ Artefato incompleto; viola completude obrigatória.
```

## Validação Automatizada

- **Ferramenta:** verificação pelo agente ou script que compare `framework/{lang}/` para cada `lang` em `language.i18n`
- **Momento:** na criação de artefato (kata-create-*), no push para o framework e na revisão de PR
- **Métrica:** 0 artefatos apenas em um idioma quando `language.i18n` exige todos; 0 artefatos fora de `{lang}/`

## Referências

- `codex-framework-language` — Manual estrutural complementar a esta Lexis
- `documentation/i18n/` — Artefatos de tradução (lex/codex por idioma, kata, warrior, cry)
- `.ahrena/.directives` — Fonte da verdade para configuração de idiomas
