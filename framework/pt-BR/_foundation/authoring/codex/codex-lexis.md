# Codex: Como Escrever Boas Lexis

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Criação de Lexis (leis inquebráveis)

## Visão Geral

Este Codex documenta o que torna uma Lexis eficaz: como redigir uma lei clara, como definir abrangência testável e como garantir que a lei seja aplicável na prática. É consultado pelo `kata-create-lexis` durante a criação de novas Lexis.

## Contexto

- **Domínio:** Design de leis inquebráveis para governança de agentes e processos
- **Público-alvo:** Agentes de IA executando `kata-create-lexis` e mantenedores do framework
- **Atualização:** Quando novos padrões de qualidade forem identificados para Lexis

## Conteúdo

### Princípios

1. **Univocidade:** Uma Lexis deve ter uma única interpretação possível. Se duas pessoas podem ler a lei e chegar a conclusões diferentes, ela precisa ser reescrita.
2. **Testabilidade:** Deve ser possível verificar automaticamente se a lei está sendo cumprida. Se não pode ser testada, não é uma boa Lexis.
3. **Necessidade:** Cada Lexis deve resolver um problema real. Leis desnecessárias geram burocracia sem valor.
4. **Imutabilidade:** Lexis não admitem exceções. Se a lei precisa de exceções, provavelmente deveria ser um Codex (recomendação) em vez de uma Lexis (obrigação).

### Anatomia de uma Boa Lexis

| Seção | Propósito | Critério de Qualidade |
|-------|-----------|----------------------|
| **Propósito** | Explica por que a lei existe | Deve conectar a lei a um risco ou problema real |
| **Lei** | Declaração imperativa da regra | Uma frase, clara, sem ambiguidade, usando "DEVE" ou "NÃO PODE" |
| **Abrangência** | Define onde e a quem se aplica | Específica o suficiente para não gerar dúvida |
| **Consequências** | O que acontece se violada | Ações concretas (bloqueio, alerta, remediação) |
| **Exemplos** | Correto vs incorreto | Casos reais, não hipotéticos |
| **Validação** | Como verificar conformidade | Ferramenta, momento e métrica específicos |

### Como Redigir a Declaração da Lei

A declaração da lei é o coração da Lexis. Deve ser:

**Boa declaração:**
> "Todo PR DEVE ter pelo menos um revisor aprovado antes do merge."

- Sujeito claro (todo PR)
- Verbo imperativo (DEVE)
- Ação específica (ter revisor aprovado)
- Condição temporal (antes do merge)

**Má declaração:**
> "Code reviews são importantes e devem ser feitos quando possível."

- Sem sujeito específico
- "Quando possível" cria brecha
- "São importantes" é opinião, não lei

### Padrões e Convenções

| Aspecto | Padrão | Exemplo |
|---------|--------|---------|
| Verbos imperativos | DEVE, NÃO PODE, NÃO DEVE | "Todo agente DEVE consultar o .directives" |
| Exceções | Nenhuma — Lexis são absolutas | "Exceções: Nenhuma. Lexis não admitem exceções." |
| Escopo | Sempre explícito | "Aplica-se a: todos os repositórios" |
| Validação | Sempre automatizável | "Ferramenta: gitleaks; Momento: pre-commit" |

### Armadilhas Comuns

| Armadilha | Problema | Solução |
|-----------|----------|---------|
| Lei vaga | "O código deve ser de qualidade" — o que é qualidade? | Definir critérios mensuráveis |
| Lei inviável | "Cobertura de testes deve ser 100%" — irrealista em muitos contextos | Calibrar com a realidade do projeto |
| Lei redundante | Repetir o que outra Lexis já cobre | Verificar Lexis existentes antes de criar |
| Lei opinativa | "Deve-se usar TypeScript" — é preferência, não segurança/qualidade | Mover para Codex como recomendação |
| Exceção embutida | "Exceto quando aprovado pelo Tech Lead" — invalida a lei | Se precisa de exceção, não é Lexis |

### Lexis vs Codex — Quando Usar Cada Um

| Característica | Lexis | Codex |
|---------------|-------|-------|
| Natureza | Obrigatório | Recomendado |
| Exceções | Nunca | Pode ter |
| Verificação | Automatizada | Manual ou automatizada |
| Exemplo | "Nenhum secret em repositório" | "Prefira PostgreSQL para dados transacionais" |

### Restrições Técnicas

- A seção "Lei" deve conter exatamente uma declaração imperativa em blockquote
- A seção "Exceções" deve sempre dizer "Nenhuma"
- A seção "Validação Automatizada" deve especificar ferramenta, momento e métrica
- O nome do arquivo deve seguir o padrão `lex-{nome-descritivo}.md`

## Glossário

| Termo | Definição |
|-------|-----------|
| Declaração da lei | Frase imperativa que define a regra absoluta |
| Univocidade | Propriedade de ter uma única interpretação |
| Testabilidade | Capacidade de verificar conformidade automaticamente |
| Validação automatizada | Mecanismo técnico que verifica o cumprimento da lei |

## Referências

- `codex-pilars` — Visão geral do sistema de Pilares
- `lex-template-usage` — Lei de uso obrigatório de templates
- `kata-create-lexis` — Procedimento para criar novas Lexis
- `templates/lex-sample.md` — Template oficial de Lexis
