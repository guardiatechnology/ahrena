---
name: kata-contributing-discuss
description: "Abrir discussão no GitHub Discussions. Criação de discussão no repositório origin (Golden Circle; MCP do GitHub quando disponível)"
---

# Kata: Abrir discussão no GitHub Discussions

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação de discussão no repositório origin (Golden Circle; MCP do GitHub quando disponível)

## Workflow

```
Progresso:
- [ ] 1. Coletar O QUÊ, POR QUÊ, COMO (com o usuário)
- [ ] 2. Redigir o corpo da discussão (Golden Circle)
- [ ] 3. Criar discussão via MCP do GitHub (ou indicar passos manuais)
- [ ] 4. Verificação final
```

### Passo 1: Coletar O QUÊ, POR QUÊ, COMO

1. Perguntar ou inferir do contexto:
   - **O QUÊ:** resumo objetivo da proposta (ex.: "Permitir múltiplos webhooks por cliente")
   - **POR QUÊ:** motivação e benefício (ex.: "Reduzir risco de falha em ambientes segregados e facilitar integrações")
   - **COMO:** opcional — sugestão de implementação ou fluxo (ex.: "Novo modelo WebhookGroup; adaptar endpoint /webhooks")
2. Se o usuário já trouxer texto, estruturá-lo nos três eixos.

### Passo 2: Redigir o corpo da discussão

1. Montar o body em Markdown com seções claras:
   - **O QUÊ** — título e descrição curta da proposta
   - **POR QUÊ** — justificativa e impacto
   - **COMO** — sugestões (se houver)
2. Incluir categoria sugerida: em geral "Ideas" (conforme codex-contributing).
3. Título da discussão: frase que resume o O QUÊ.

### Passo 3: Criar discussão via MCP do GitHub

1. **Preferência:** usar MCP do GitHub se o servidor expuser criação de discussão (ex.: ferramenta de discussions). Indicar servidor e parâmetros (owner, repo, category, title, body).
2. **Fallback:** se o MCP não estiver disponível ou não houver ferramenta para discussions:
   - Apresentar ao usuário o título e o body prontos
   - Indicar que abra manualmente em: GitHub do repositório → Discussions → New discussion (categoria Ideas)
   - Ou usar `gh` CLI se houver suporte (ex.: extensão ou API)

### Passo 4: Verificação final

- [ ] A discussão foi criada (ou o conteúdo foi entregue para abertura manual)
- [ ] O texto segue o Golden Circle (O QUÊ, POR QUÊ, COMO)
- [ ] O link da discussão ou as instruções foram apresentados ao usuário

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Discussão | GitHub Discussion | Repositório origin (categoria Ideas) |
| URL da discussão ou instruções | Link / texto | Apresentado ao usuário |

## Restrições

- Não há template .md no framework para discussão; o conteúdo é livre dentro do Golden Circle.
- Sempre estruturar a proposta em O QUÊ, POR QUÊ e (quando aplicável) COMO.
- Se não for possível criar via MCP, não inventar comando `gh` para discussions — indicar abertura manual e fornecer título + body prontos.
