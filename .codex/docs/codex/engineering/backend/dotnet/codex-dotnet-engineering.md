# Codex: Engenharia .NET

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Desenvolvimento, dados, operação e entrega de aplicações .NET

## Conteúdo

### 1. Descoberta Antes da Implementação

Inspecione `global.json`, `*.sln`/`*.slnx`, `*.csproj`, `Directory.Build.*`, `Directory.Packages.props`, lock files, analyzers e CI. Registre versão confirmada, comandos do repo e diferenças entre ambiente local e pipeline.

### 2. C# e Runtime

| Decisão | Diretriz |
|---|---|
| Nullability | Habilitar e modelar ausência; não espalhar `!` |
| Async | Async end-to-end, `CancellationToken` propagado, sem sync-over-async |
| Recursos | Ownership explícito; `await using` para recursos assíncronos |
| Exceções | Exceções para falhas excepcionais; resultado tipado para outcomes esperados quando melhora o contrato |
| LINQ | Considerar execução diferida, múltipla enumeração e tradução do provider |
| Tempo/IDs | Injetar `TimeProvider` e geradores quando determinismo importa |

### 2.1. Disciplina Inspirada em Rust

O objetivo não é simular borrow checker em C#, e sim importar as propriedades que aumentam corretude:

| Propriedade | Aplicação idiomática em .NET |
|---|---|
| Memory safety | Permanecer em safe code; isolar interop; nunca expor ponteiro/lifetime ao domínio |
| Ownership | Quem cria descarta; lifetime de DI explícito; buffers alugados retornam em `finally` |
| Imutabilidade | `record`, `readonly` e coleções imutáveis/read-only nas fronteiras de domínio |
| Estados válidos | Factories/construtores protegem invariantes; hierarquias fechadas e pattern matching exaustivo |
| Erros esperados | Result/union tipado quando o caller precisa decidir; exceptions preservadas para falhas excepcionais |
| Corretude aritmética | `checked`, tipos monetários/de domínio e testes de boundary/overflow |
| Zero-cost quando comprovado | `Span<T>`, `Memory<T>`, structs e pooling somente com benchmark e lifetime simples |

#### Estratégia de Alocação

1. Medir com `dotnet-counters`, `dotnet-trace`, profiler e BenchmarkDotNet antes de otimizar.
2. Reduzir primeiro trabalho evitável: materialização, múltipla enumeração, closures, boxing, strings intermediárias e buffers por item.
3. Preferir streaming e APIs que recebem buffer em hot paths; manter APIs comuns onde a alocação não afeta SLO/custo.
4. Usar pooling por último: ele troca GC por ownership manual, retenção de memória e risco de dados residuais.
5. Registrar throughput, bytes/op, Gen0/1/2 e memória retida; "menos allocations" sem impacto mensurável não justifica complexidade.

### 3. Arquitetura, Clean Code e DDD

Dependências apontam para políticas mais estáveis; domínio não importa ASP.NET Core, EF Core ou SDK de provedor. Isso não exige um número fixo de projetos. Separe quando houver fronteira real de mudança, teste, deploy ou ownership. Consulte `codex-code-design` para abstrações e `codex-domain-driven-design` para linguagem, aggregates e integrações.

### 4. ASP.NET Core

| Tema | Diretriz |
|---|---|
| Pipeline | Ordem de middleware é comportamento; teste autenticação, autorização, erro e observabilidade |
| Contratos | Valide no boundary e mantenha domain models fora do wire format |
| DI/options | Lifetimes explícitos; valide options no startup; evite service locator |
| HTTP clients | Use `IHttpClientFactory`, timeout budget, propagação de cancelamento e política por dependência |
| Health | Liveness indica processo; readiness verifica capacidade de servir sem causar cascata |
| Testes | `WebApplicationFactory` para comportamento real do pipeline quando aplicável |

### 5. EF Core e Consistência

- `DbContext` é curto, representa unidade de trabalho e não é thread-safe.
- Inspecione SQL/tradução em queries críticas; evite N+1, tracking desnecessário e materialização precoce.
- Constraints do banco protegem invariantes persistentes; validação de aplicação melhora feedback, não substitui constraint.
- Concorrência otimista deve ter token, resposta de conflito e política de retry consciente.
- Transação local não envolve HTTP/fila. Para publicação confiável, avalie outbox/inbox e consumidores idempotentes.
- Migrações seguem expand/contract quando coexistem versões. Defina backup, duração, lock, rollback e compatibilidade.
- Um timeout no commit pode ter resultado desconhecido: reconcilie antes de repetir efeito financeiro.

### 6. Resiliência e Observabilidade

Defina timeout budget por dependência. Retry apenas falha transitória e operação idempotente, com limite e jitter; circuit breaker e bulkhead protegem recursos, mas não corrigem contrato ruim. Logs, métricas e traces compartilham correlation/trace identifiers, sem dados sensíveis e com cardinalidade controlada. Alertas devem apontar para impacto/SLO e runbook.

### 7. Testes

Escolha nível por risco: unidade para regra, integração para adapter/provider, contrato para fronteira e end-to-end para poucos fluxos críticos. Use xUnit/NUnit conforme o repo; não migre framework sem motivo. Use Testcontainers ou infraestrutura isolada quando a semântica externa importa. Cobertura aponta lacunas, não prova qualidade.

### 8. Build, Dependências e Delivery

| Tema | Diretriz |
|---|---|
| SDK/TFM | Fixar política com `global.json`; declarar TFMs suportados |
| Pacotes | Central package management quando adotado; lock e audit de vulnerabilidade |
| Build | Warnings relevantes como erro; analyzers versionados; artefato reproduzível |
| Publicação | Escolher framework-dependent/self-contained conscientemente |
| Trimming/AOT | Só após testes de compatibilidade, reflexão, serialização e startup |
| Container | Imagem mínima suportada, usuário não-root, health e shutdown gracioso |
| Deploy | Promover o mesmo artefato; schema compatível; rollback/reconciliação explícitos |

### Decisões Vigentes

| Decisão | Status | Consequência |
|---|---|---|
| Este Codex é independente de versão, com baseline registrado | Confirmada | Regras dependentes de versão exigem conferência no projeto e documentação oficial |
| Arquitetura é guiada por fronteiras, não template fixo | Confirmada | Projetos pequenos podem continuar simples |
| Patterns declaram quando usar e evitar | Proposta para o Ahrena v2 | Apollo-.NET deve justificar pattern antes de criar estrutura |

### Restrições Técnicas

- Não assumir que o SDK instalado é o SDK suportado pelo repositório.
- Não fazer retry de operação não idempotente ou commit incerto sem reconciliação.
- Não usar `DbContext` em paralelo nem esconder seu lifetime em singleton.
- Não colocar PII, tokens, PAN ou secrets em logs/traces.
- Não usar `unsafe` em domínio/aplicação nem introduzir pooling/`stackalloc` sem benchmark, bounds claros e testes de lifetime.
- Não adotar Native AOT, CQRS, Event Sourcing ou microservices sem evidência e plano operacional.
