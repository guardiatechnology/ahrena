# Codex: Domain-Driven Design

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Modelagem estratégica e tática de domínios complexos

## Conteúdo

### Princípios

1. **Estratégico antes do tático:** Linguagem Ubíqua, subdomínios, bounded contexts e Context Map precedem Aggregate, Repository ou Domain Service.
2. **Modelo local:** o mesmo termo pode ter modelos diferentes em contextos diferentes; tradução explícita protege cada linguagem.
3. **Agregado por invariante:** a fronteira existe para garantir consistência transacional, não para reproduzir tabelas ou árvores de objetos.
4. **Complexidade conquistada:** CRUD simples não precisa fingir um domínio rico; evolua o modelo quando regras e conflitos aparecerem.
5. **Eventos com semântica:** Domain Event registra fato interno; Integration Event é contrato publicado e pode exigir outbox, versão e política de dados.

### Sequência de Decisão

| Gate | Pergunta | Evidência esperada |
|---|---|---|
| Linguagem | Os termos e conflitos de significado estão explícitos? | Glossário e exemplos aceitos pelo domínio |
| Fronteira | Quem decide e é dono dos dados/regras? | Bounded context e responsáveis |
| Relação | Como os contextos dependem e traduzem modelos? | Context Map e contrato publicado |
| Consistência | Quais regras precisam ser verdadeiras no mesmo commit? | Invariantes e limite do Aggregate |
| Persistência | Que concorrência e falha precisam ser tratadas? | Unidade de trabalho, versão e política de retry |
| Integração | Que fato pode sair e com qual garantia? | Evento versionado, outbox/inbox e idempotência quando necessárias |

### Patterns Táticos — Quando Não Usar

| Pattern | Use quando | Evite quando |
|---|---|---|
| Entity | Identidade e ciclo de vida importam | O valor é definido apenas por seus atributos |
| Value Object | Conceito imutável com invariantes | É apenas um saco de dados sem semântica |
| Aggregate | Invariantes exigem consistência conjunta | Objetos só precisam de consulta/join |
| Repository | O domínio precisa de uma coleção abstrata | Um handler CRUD direto é suficiente e claro |
| Domain Service | Regra do domínio não pertence naturalmente a uma Entity/VO | É apenas orquestração de IO |
| CQRS | Modelos de leitura e escrita têm pressões realmente diferentes | CRUD comum sem assimetria comprovada |
| Event Sourcing | Histórico é o modelo primário e há capacidade operacional | Auditoria simples resolvida por log/histórico |

### Fronteiras Operacionais

- Uma transação local não abrange HTTP, fila ou provedor externo.
- Commit com resultado incerto exige reconciliação; retry cego pode duplicar efeito financeiro.
- Consistência eventual deve declarar janela, indicador de atraso, reprocessamento e responsável.
- Integrações externas usam Adapter/ACL quando o vocabulário externo diverge.

### Decisões Vigentes

| Decisão | Status | Consequência |
|---|---|---|
| DDD-first começa por entendimento do domínio | Confirmada | Documento não é um formulário de Aggregate |
| Layout físico é orientação arquitetural, não definição de DDD | Confirmada | Validadores estruturais não substituem validação semântica humana |
| Dicionário consultável de patterns | Proposta para o Ahrena v2 | Este Codex fornece os critérios que o catálogo deve preservar |

### Restrições Técnicas

- Não derivar bounded contexts diretamente de tabelas, times ou endpoints sem evidência de linguagem e ownership.
- Não permitir acesso externo direto a membros internos do Aggregate.
- Não confundir Domain Event com Integration Event nem publicar dados sensíveis por conveniência.
- Não impor arquitetura em camadas ou pasta única a todas as stacks.
