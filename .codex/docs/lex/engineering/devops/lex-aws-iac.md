# Lexis: Infraestrutura como Código (IaC) em AWS

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Toda provisão e mudança de infraestrutura AWS através de código versionado (Terraform, AWS CDK, CloudFormation, Pulumi)

## Lei

> **Toda provisão ou modificação de recursos AWS DEVE ser feita via IaC versionado em Git, aplicada através de pipeline de CI/CD. Mudanças no console são permitidas apenas para (a) investigação sem escrita, (b) resposta a incidente crítico com registro retroativo em IaC dentro de 24h. Secrets e valores sensíveis NÃO DEVEM estar em texto claro em IaC versionado.**

## Regras

### 1. Uma ferramenta de IaC por projeto

O projeto **DEVE** adotar **uma** ferramenta IaC principal e mantê-la consistente. Escolhas válidas:

| Ferramenta | Quando preferir |
|---|---|
| **Terraform** | Multi-cloud; ecossistema de providers; teams familiares com HCL |
| **AWS CDK** | AWS-only; teams fortes em TS/Python; querem abstrações de alto nível |
| **Pulumi** | Multi-cloud; querem linguagem de programação full |
| **CloudFormation** | AWS-only; querem AWS-native sem dependência externa |

Misturar ferramentas sem isolamento claro (ex.: Terraform e CDK gerenciando os mesmos recursos) **é proibido**.

### 2. State remoto e com lock

O agente **DEVE**:

1. **Terraform:** state em S3 com DynamoDB lock; nunca em local filesystem em produção; S3 bucket com versionamento + encryption.
2. **CDK:** stacks com stack outputs no CloudFormation; state gerenciado pela AWS.
3. **Pulumi:** state em Pulumi Service ou S3 backend.
4. **Nenhum state em repositório Git** — states contêm dados sensíveis.

### 3. Ambientes separados por workspace/stack

Cada ambiente (dev, staging, prod) **DEVE** ter state isolado:

- **Terraform:** workspaces ou diretórios separados + backends distintos
- **CDK:** stacks distintas (`Stack-dev`, `Stack-prod`) ou accounts separadas
- **Pulumi:** stacks distintas por ambiente

**Nunca** compartilhar state entre ambientes.

### 4. Módulos reutilizáveis com versionamento

Para componentes comuns (VPC, ECS cluster, RDS, ALB):

1. Extrair em **módulos versionados** (tags semver).
2. Consumir por versão pinnable, não `HEAD`.
3. Documentar inputs/outputs e exemplos de uso.

```hcl
module "vpc" {
  source  = "git::https://github.com/guardia/terraform-modules.git//vpc?ref=v2.3.0"
  cidr    = "10.0.0.0/16"
  ...
}
```

### 5. Pipelines de CI/CD para aplicar mudanças

Toda mudança de IaC **DEVE** passar por:

1. **Plan** automático no PR (`terraform plan`, `cdk diff`, `pulumi preview`) — visível no PR para revisão.
2. **Linting e scanners de segurança** (tfsec, checkov, cdk-nag) — ver `lex-aws-security`.
3. **Aprovação humana** para apply em produção (`terraform apply` via pipeline após merge + approval manual).
4. **Apply em dev/staging automático** após merge (para iteração rápida).

### 6. Sem drift manual

1. **Drift detection** automatizado: rodar `terraform plan` diariamente em produção; alertar se há divergência.
2. **IAM policies restritivas** para humanos em produção: limitar `Update*`, `Delete*`, `Create*` via SCPs.
3. **Acesso break-glass**: role temporária com MFA + logging completo, para emergências.
4. Mudanças manuais feitas em emergência **DEVEM** ser registradas em IaC em até 24h.

### 7. Tagging consistente

Todo recurso **DEVE** receber tags padrão:

```hcl
tags = {
  Environment = "prod"         # dev | staging | prod
  Owner       = "platform-team"
  Project     = "ahrena"
  CostCenter  = "engineering"
  ManagedBy   = "terraform"
  Lifecycle   = "persistent"   # persistent | temporary
}
```

Tags são base para: cost allocation (`lex-aws-cost`), compliance, automação.

### 8. Segredos fora do IaC

O agente **NÃO PODE**:

1. Hardcoded secrets em arquivos `.tf`, `.ts`, `.py` do IaC.
2. Secrets em `terraform.tfvars` commitados.
3. Secrets em `CfnParameter` sem `NoEcho: true`.

O agente **DEVE**:

1. Criar o recurso `aws_secretsmanager_secret` via IaC; popular o **valor** fora do IaC (via CLI, pipeline step autorizado).
2. Referenciar segredos em runtime (`secretsmanager_secret_version.arn`); não retornar valor como output.

### 9. Recursos críticos com proteção de delete

Recursos stateful ou críticos **DEVEM** ter proteção:

```hcl
resource "aws_s3_bucket" "data" {
  # ...
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_db_instance" "main" {
  # ...
  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "guardia-prod-final-${formatdate("YYYY-MM-DD", timestamp())}"
}
```

## Validação Automatizada

- **Ferramenta:**
  - **Linting:** `terraform fmt`, `terraform validate`, `tflint`
  - **Plan em PRs:** `atlantis`, GitHub Actions, CodeBuild
  - **Drift:** cronjob com `terraform plan` em produção alertando diffs
  - **Policy:** OPA/Sentinel para regras organizacionais (ex.: "todo S3 deve ter encryption")
- **Momento:** cada PR; diário (drift); CI/CD pipeline
- **Métrica:** 100% dos recursos em IaC; 0 drift não resolvido em >24h
