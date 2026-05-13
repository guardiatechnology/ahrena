# Codex: [Nome do Manual]

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** [Etapa do SDLC]

## Visão Geral

Descreva o domínio de conhecimento que este Codex cobre. Codex são bases de conhecimento estruturadas que a IA consulta para tomar decisões contextualizadas. Contêm documentação técnica, arquitetural e de processos.

## Contexto

- **Domínio:** [ex: arquitetura do sistema, padrões de API, fluxo de deploy]
- **Público-alvo:** [ex: desenvolvedores, Tech Lead, IA copiloto]
- **Atualização:** [ex: a cada ADR aprovado, a cada sprint]

## Conteúdo

### Princípios

Liste os princípios fundamentais do domínio:

1. **[Princípio 1]:** [Descrição e justificativa]
2. **[Princípio 2]:** [Descrição e justificativa]
3. **[Princípio 3]:** [Descrição e justificativa]

### Padrões e Convenções

| Aspecto | Padrão | Exemplo |
|---------|--------|---------|
| [Nomenclatura] | [camelCase / PascalCase / kebab-case] | `getUserById` |
| [Estrutura] | [padrão adotado] | `src/modules/<domain>/` |
| [Comunicação] | [REST / gRPC / eventos] | `POST /api/v2/transactions` |

### Decisões Vigentes

Referência às decisões arquiteturais ativas:

| ADR | Decisão | Status |
|-----|---------|--------|
| ADR-{N} | [Descrição da decisão] | Ativa |
| ADR-{N} | [Descrição da decisão] | Ativa |

### Restrições Técnicas

- **[Restrição 1]:** [ex: Banco de dados deve ser PostgreSQL 15+]
- **[Restrição 2]:** [ex: Todas as APIs devem ser versionadas via path]
- **[Restrição 3]:** [ex: Máximo de 3 níveis de profundidade em herança]

## Diagrama de Referência

```
[Insira diagrama ASCII, Mermaid ou referência a arquivo de diagrama]
```

## Glossário

| Termo | Definição |
|-------|-----------|
| [Termo 1] | [Definição no contexto deste domínio] |
| [Termo 2] | [Definição no contexto deste domínio] |

## Referências

- [Link para documentação externa relevante]
- [Link para ADRs relacionados]
- [Link para RFCs ou specs]

---

**Modelo:** Este arquivo é um template. Para criar um novo Codex, copie este arquivo e substitua os campos entre colchetes.
