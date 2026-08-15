# Codex: AWS Well-Architected Framework

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Seis pilares do AWS Well-Architected Framework — referência para projetar e revisar arquiteturas AWS

## Conteúdo

### Os 6 pilares

1. **Operational Excellence** — Executar e monitorar sistemas para entregar valor de negócio
2. **Security** — Proteger informações, sistemas e ativos
3. **Reliability** — Workloads executam conforme esperado, consistentemente e em escala
4. **Performance Efficiency** — Uso eficiente de recursos computacionais
5. **Cost Optimization** — Evitar custos desnecessários
6. **Sustainability** — Minimizar impacto ambiental

### Pilar 1 — Operational Excellence

**Princípios de design:**

- Operações como código (IaC, automação de runbooks)
- Fazer mudanças frequentes, pequenas e reversíveis
- Refinar procedimentos operacionais com frequência
- Antecipar falhas (game days, chaos engineering)
- Aprender com falhas (post-mortem sem blame)

**Perguntas-chave:**

1. Como a organização entende seu workload em produção? (métricas, logs, traces)
2. Como responde a eventos (alerts) e incidentes?
3. Como evolui procedimentos operacionais?

**Práticas essenciais:**

- **IaC** via Terraform/CDK (ver `lex-aws-iac`)
- **CI/CD** com pipelines automatizados, blue/green ou canary deploys
- **Observabilidade** completa: métricas (CloudWatch), logs (CloudWatch Logs), traces (X-Ray / OpenTelemetry)
- **Runbooks** versionados para incidents frequentes
- **Game days** quadrimestrais para exercitar failure scenarios

### Pilar 2 — Security

**Princípios de design:**

- Implementar identidade forte (MFA, least privilege)
- Habilitar rastreabilidade (CloudTrail, Config)
- Aplicar segurança em todas as camadas (defense in depth)
- Automatizar melhores práticas de segurança
- Proteger dados em trânsito e em repouso
- Manter pessoas afastadas de dados (acesso programático)
- Preparar-se para eventos de segurança (IR plan)

**Perguntas-chave:**

1. Como opera sua workload de forma segura?
2. Como gerencia identidades para pessoas e máquinas?
3. Como detecta e investiga eventos de segurança?
4. Como protege sua infraestrutura (rede, compute)?
5. Como classifica e protege dados?

**Práticas essenciais:**

- **AWS Organizations** com SCPs e OUs separadas
- **IAM** com roles + Identity Center (SSO) para humanos; IRSA para workloads Kubernetes
- **KMS** para chaves gerenciadas; rotação automática
- **Secrets Manager** / **Parameter Store SecureString** para segredos
- **VPC** com subnets privadas; Security Groups específicos; WAF para APIs públicas
- **CloudTrail + GuardDuty + Security Hub + Macie** — detecção e compliance

> Ver `lex-aws-security` para regras invioláveis.

### Pilar 3 — Reliability

**Princípios de design:**

- Automatizar recuperação de falhas
- Testar procedimentos de recuperação
- Escalar horizontalmente para aumentar disponibilidade
- Parar de adivinhar capacidade (auto-scaling)
- Gerenciar mudanças via automação

**Perguntas-chave:**

1. Como entende demanda e capacidade?
2. Como lida com falhas de componente?
3. Como recupera de desastres?

**Práticas essenciais:**

- **Multi-AZ** como padrão para produção (RDS, ElastiCache, ECS, EKS)
- **Multi-Region** para workloads tier-1 (RPO/RTO definidos explicitamente)
- **Auto-scaling** por métricas relevantes (CPU, custom metrics, target tracking)
- **Health checks** em ALB/NLB + Route 53; failover automático
- **Backup** via AWS Backup com RPO definido; testes de restore periódicos
- **Circuit breakers** e graceful degradation em camadas de serviço
- **Chaos engineering** (AWS Fault Injection Simulator) para validar resiliência

**RTO/RPO de referência por criticidade:**

| Tier | RTO | RPO | Arquitetura típica |
|---|---|---|---|
| Tier 1 (crítico, financeiro) | <1h | <5min | Multi-region active-active |
| Tier 2 (importante) | <4h | <1h | Multi-AZ + backup cross-region |
| Tier 3 (business-hours) | <24h | <24h | Multi-AZ; backup diário |
| Tier 4 (interno) | <72h | <24h | Single-AZ com backup |

### Pilar 4 — Performance Efficiency

**Princípios de design:**

- Democratizar tecnologias avançadas (usar serviços gerenciados)
- Globalizar em minutos (CloudFront, multi-region)
- Usar arquiteturas serverless para reduzir operação
- Experimentar com frequência
- Considerar a simpatia mecânica (escolher serviço certo para o problema)

**Perguntas-chave:**

1. Como seleciona a arquitetura de compute/storage/DB/network?
2. Como evolui conforme novas tecnologias surgem?
3. Como monitora recursos para garantir performance?

**Escolhas comuns por workload:**

| Workload | Escolha recomendada |
|---|---|
| API HTTP com tráfego variável | API Gateway + Lambda (serverless) ou ECS Fargate + ALB |
| API HTTP com tráfego alto sustained | ECS on EC2 (com RI) ou EKS |
| Processamento de eventos assíncrono | SQS + Lambda ou Kinesis + Lambda |
| Stream processing pesado | Kinesis Data Analytics, MSK (Kafka gerenciado), Glue Streaming |
| Batch processing | Batch, Step Functions + Lambda, EMR |
| ML training/inference | SageMaker |
| BD relacional transacional | Aurora (MySQL/PostgreSQL-compatible) > RDS > self-managed |
| BD NoSQL com padrões conhecidos | DynamoDB |
| Full-text search | OpenSearch; se pequeno, RDS com extensões |
| Cache | ElastiCache (Redis/Memcached) |
| Entrega global de assets | CloudFront + S3 |

### Pilar 5 — Cost Optimization

> Ver `lex-aws-cost` para regras invioláveis e práticas detalhadas.

**Princípios de design:**

- Implementar cloud financial management
- Adotar modelo de consumo (pay for what you use)
- Medir eficiência geral
- Parar de gastar em heavy lifting não diferenciado (usar serviços gerenciados)
- Analisar e atribuir despesas

**Práticas essenciais:**

- Tagging completo + Cost Explorer
- Budgets + Anomaly Detection
- Savings Plans e Reserved Instances para workload previsível
- Spot para cargas tolerantes
- Right-sizing trimestral via Compute Optimizer + Trusted Advisor
- Lifecycle policies em S3; retention em logs
- Auto-shutdown de dev/staging fora de horário

### Pilar 6 — Sustainability

**Princípios de design:**

- Compreender impacto
- Estabelecer metas de sustentabilidade
- Maximizar utilização (consolidar workloads)
- Antecipar e adotar ofertas mais eficientes
- Usar serviços gerenciados (operam com maior eficiência que equivalentes self-hosted)
- Reduzir impacto downstream (comprimir, pagainar, etc.)

**Práticas essenciais:**

- **Regiões com baixa intensidade de carbono:** preferir regiões AWS alimentadas por energia renovável (ver Customer Carbon Footprint Tool)
- **ARM (Graviton)** para instâncias EC2/Lambda/RDS — ~40% mais eficiente em energia
- **Serverless** reduz waste de compute ocioso
- **Dados:** lifecycle agressivo para arquivos antigos; remover dados não usados
- **Imagens e assets:** formatos modernos (WebP, AVIF); CDN para reduzir transferência

### Trade-offs comuns

Projetar é balancear pilares. Trade-offs típicos:

| Trade-off | Exemplo |
|---|---|
| Reliability ↔ Cost | Multi-region duplica custo; justificado só para workload crítico |
| Performance ↔ Cost | Instância maior é mais rápida mas custa mais; right-sizing procura o ponto ótimo |
| Security ↔ Operational simplicity | Mais camadas de security (WAF, Shield, GuardDuty) aumentam operação |
| Sustainability ↔ Performance | Graviton é mais eficiente mas pode requer compatibility testing |

A arquitetura **DEVE documentar o trade-off escolhido** — tipicamente via ADR quando estrutural (`kata-adr-write`).

### Well-Architected Tool

A AWS oferece a **Well-Architected Tool** (grátis) que guia a revisão de workloads respondendo às perguntas dos 6 pilares e gerando plano de melhoria. Recomendado:

1. Rodar review em workloads novos (após go-live) e tier-1 anualmente.
2. Executar **Well-Architected Lenses** específicos: Serverless, SaaS, Machine Learning, Financial Services.
3. Registrar high-risk issues (HRIs) e tratá-los como débito prioritário.
