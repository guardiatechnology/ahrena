# Codex: Guia para Traduzir para Português Brasileiro

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Convenções e orientações para tradução técnica para pt-BR

## Conteúdo

### Convenções de Escrita Técnica em pt-BR

1. **Voz ativa** é preferível à voz passiva, mas ambas são aceitas em contexto técnico
2. **Frases objetivas** — evitar rodeios e construções rebuscadas
3. **Parágrafos curtos** — facilitar a leitura em tela
4. **Consistência terminológica** — manter o mesmo termo para o mesmo conceito ao longo do documento

### Tabela de Termos Técnicos

| Termo em inglês | Ação | Forma em pt-BR |
|-----------------|------|----------------|
| deploy | Manter ou traduzir | deploy / implantar |
| commit | Manter | commit |
| merge | Manter | merge |
| branch | Manter | branch |
| pull request | Manter | pull request |
| push | Manter | push |
| framework | Manter | framework |
| template | Contextual | template / modelo |
| workflow | Traduzir | fluxo de trabalho |
| feedback | Traduzir | retorno / resposta |
| output | Traduzir | saída |
| input | Traduzir | entrada |
| bug | Traduzir | defeito / erro |
| feature | Traduzir | funcionalidade / recurso |
| middleware | Manter | middleware |
| API | Manter | API |
| SDK | Manter | SDK |
| CLI | Manter | CLI |
| script | Manter | script |
| log | Manter | log |
| cache | Manter | cache |
| token | Manter | token |
| endpoint | Manter | endpoint |
| payload | Manter | payload |

### Padrões de Formalização

| Contexto | Padrão correto | Padrão incorreto |
|----------|----------------|------------------|
| Obrigatoriedade | "O agente **DEVE**..." | "O agente tem que..." |
| Necessidade | "É necessário..." | "Precisa..." |
| Recomendação | "Recomenda-se..." | "É bom que..." |
| Proibição | "**NÃO DEVE**..." | "Não pode..." (coloquial) |
| Instrução direta | "Crie o arquivo..." | "Você poderia criar o arquivo..." |

### Exemplos de Traduções

#### Correto

**Original (en):**
> The agent **MUST** read `.ahrena/.directives` before performing any task.

**Tradução (pt-BR):**
> O agente **DEVE** ler o `.ahrena/.directives` antes de executar qualquer tarefa.

#### Incorreto

**Original (en):**
> The agent **MUST** read `.ahrena/.directives` before performing any task.

**Tradução (pt-BR):**
> O agente precisa checar as diretivas do Ahrena antes de fazer qualquer coisa.

**Problemas:**
- "MUST" rebaixado para "precisa" (perde força)
- ".ahrena/.directives" substituído por texto genérico
- "qualquer coisa" é coloquial demais

### Armadilhas Comuns

1. **"Deletar" vs "Excluir"** — Preferir "excluir" em contexto formal
2. **"Setar" vs "Configurar"** — Preferir "configurar"
3. **"Rodar" vs "Executar"** — Preferir "executar" em contexto formal
4. **"Checar" vs "Verificar"** — Preferir "verificar"
5. **Gerúndio excessivo** — Evitar "Estando o agente configurando..." → "Ao configurar, o agente..."
