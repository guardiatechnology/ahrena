# Lexis: Consulta Obrigatória ao .directives

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Todas as sessões e atividades de agentes IA

## Propósito

O Ahrena centraliza suas configurações canônicas em um único arquivo declarativo: `.ahrena/.directives`. Esse arquivo reside no diretório `.ahrena/` — o ponto de entrada canônico do framework em qualquer projeto — e contém instruções transversais como idioma padrão, idiomas obrigatórios, convenções de nomenclatura, caminhos canônicos e outras diretivas que governam o comportamento de todo o framework.

Sem a consulta obrigatória a esse arquivo, agentes podem tomar decisões divergentes sobre idioma, casing, prefixos e endereçamento, gerando inconsistência entre artefatos e sessões.

Esta Lexis existe para garantir que **todo agente consulte e respeite as diretivas canônicas** definidas em `.ahrena/.directives` antes de produzir qualquer saída ou artefato.

## Lei

> **Todo agente DEVE ler e aplicar as instruções definidas em `.ahrena/.directives` antes de iniciar qualquer atividade que produza artefatos, documentação ou comunicação no contexto do Ahrena.**

## Regras

### 1. Localização canônica

O arquivo de diretivas **SEMPRE** reside em:

```
.ahrena/.directives
```

O diretório `.ahrena/` é o ponto de entrada canônico do framework em qualquer projeto que adota o Ahrena. O agente **DEVE** procurar esse diretório na raiz do repositório.

### 2. Leitura obrigatória ao iniciar

Ao iniciar uma sessão ou atividade, o agente **DEVE**:

1. Localizar o diretório `.ahrena/` na raiz do repositório.
2. Ler o arquivo `.ahrena/.directives` integralmente.
3. Internalizar as diretivas como restrições ativas para toda a sessão.

Se o diretório `.ahrena/` ou o arquivo `.directives` não existir, o agente **DEVE** alertar o usuário sobre a ausência e sugerir sua criação.

### 3. Diretivas como fonte da verdade

As diretivas definidas em `.ahrena/.directives` têm **precedência** sobre:

- Suposições do agente baseadas em treinamento ou contexto genérico.
- Preferências implícitas não documentadas.

Quando houver conflito entre uma diretiva e uma instrução do usuário na sessão, o agente **DEVE** seguir a instrução do usuário, mas **alertar** sobre a divergência em relação à diretiva canônica.

### 4. Aplicação por seção

O agente **DEVE** aplicar cada seção da diretiva ao comportamento correspondente:

| Seção | Aplicação |
|-------|-----------|
| `paths` | Usar os caminhos canônicos ao referenciar ou criar artefatos do framework |
| `language` | Produzir documentação e artefatos no idioma padrão (`default`) e garantir que os idiomas obrigatórios (`required`) sejam contemplados quando aplicável |
| `naming.prefixes` | Aplicar o prefixo correto ao nomear artefatos de cada Pilar |
| `naming.extensions` | Usar a extensão correta conforme o contexto (`.md` para framework, `.mdc` para Cursor) |
| `naming.casing` | Seguir a convenção de casing definida para arquivos e diretórios |
| `naming.addressing` | Seguir o padrão de endereçamento ao posicionar artefatos na taxonomia |
| `naming.reserved_clades` | Reconhecer Clades especiais e respeitar suas regras de uso |
| `terminal` | Consultar para comandos de shell; usar o tipo definido (bash ou PowerShell). Ver `lex-terminal-type`. |
| `naming.tone_and_writing_style` | Aplicar o tom e o estilo ao produzir artefatos e comunicação. Ver `lex-tone`. |
| `stacked_prs.tool` | Selecionar a ferramenta para operar Stacked Pull Requests quando aplicável: `vanilla` (default — `git` + `gh` puros) ou `gs` (git-spice). Ver `codex-stacked-prs`. |
| `paths.skills_root` | Diretório raiz dos projetos de skill externos (default `skills`). Ver `lex-skill-project-structure`. |
| `paths.skills_build` | Diretório de intermediários do build de skills (default `.build`, gitignored). Escrito pelo stack de build do projeto consumidor. |
| `paths.skills_dist` | Diretório de entrega final de skills empacotados (default `.dist`, committed). Validado por `lex-skill-package-structure`. |
| `pr_cost_tracking.enabled` | Quando `true`, ativar o stamp de tokens, custo USD e tempo de implementação (ativo + calendário) no body de PRs via `kata-pr-cost-stamp`. Default `false`. Ver `codex-pr-cost-tracking`. |
| `pr_cost_tracking.idle_gap_minutes` | Gap (em minutos) que separa janelas ativas dentro de uma sessão Claude Code para o cálculo de tempo ativo. Default `10`. Valor menor torna a contagem mais estrita; maior agrega pausas longas. |
| `pr_cost_tracking.attribution_mode` | `hook` (default) | `project` (legado). Em `hook`, o `pr-cost-attribution.sh` grava `~/.claude/projects/<hash>/branches.jsonl` por turno e o `pr-cost-stamp.sh` filtra por `--branch`/`--purpose`, separando Development e Review. Em `project`, comportamento legado (filtro só por project + since). |
| `pr_cost_tracking.branches_sidecar_max_mb` | Limite (em MB) acima do qual o stamp emite warning sobre o tamanho do `branches.jsonl`. Default `50`. Iteração futura adiciona rotação automática. |
| `pr_cost_tracking.known_ai_reviewers` | Lista de logins GitHub adicionais reconhecidos como revisores AI na subseção Review. Built-ins (gemini-code-assist[bot], claude[bot], coderabbitai[bot], qodo-merge-pro[bot]) são sempre reconhecidos; logins aqui estendem o conjunto. Subchaves `currency`, `include_cache_breakdown`, `window_override_days`, `mask_absolute_cost` permanecem declaradas em `.directives.sample` como reservadas para iterações futuras. |

Manuais complementares para interpretação das seções: `codex-directives` (visão geral do arquivo), `codex-paths` (caminhos canônicos), `codex-naming` (convenções de nomenclatura).

### 5. Extensibilidade

Novas seções podem ser adicionadas ao `.directives` a qualquer momento. O agente **DEVE** interpretar seções desconhecidas com base no nome e estrutura da chave, aplicando a diretiva de forma razoável. Em caso de ambiguidade, o agente **DEVE** perguntar ao usuário.

### 6. Não modificação sem autorização

O agente **NÃO PODE** modificar o arquivo `.directives` sem solicitação explícita do usuário. As diretivas são canônicas e governadas pelo mantenedor do framework.

## Abrangência

- **Aplica-se a:** todas as sessões de trabalho com agentes IA, em qualquer Clade e Subclade
- **Agentes vinculados:** todos os Warriors e agentes genéricos
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Inconsistência de artefatos:** artefatos produzidos sem consultar as diretivas podem ter idioma, nomenclatura ou endereçamento incorretos.
2. **Retrabalho:** artefatos fora das diretivas devem ser corrigidos para conformidade antes de serem aceitos.
3. **Remediação:** o agente deve reler o `.ahrena/.directives`, identificar as divergências e corrigir os artefatos produzidos.

## Exemplos

### Correto

```
Agente: [Início de sessão]
1. Localiza .ahrena/ na raiz do repositório
2. Lê .ahrena/.directives
3. Identifica:
   - Idioma padrão: pt-BR
   - Idiomas obrigatórios: pt-BR, es, en
   - Casing: kebab-case
   - Prefixo para Lexis: lex-
4. Produz artefato em pt-BR, nomeia como lex-code-review.md,
   salva em engineering/quality/lexis/

Usuário: Crie a documentação dessa feature.

Agente: Documentação criada em pt-BR (padrão).
Deseja que eu gere também as versões em espanhol e inglês,
conforme as diretivas do framework?
```

### Incorreto

```
Agente: [Início de sessão — ignora .ahrena/.directives]

Usuário: Crie uma nova Lexis sobre logging.

Agente: Here's your new Lexis:
# Lexis: Logging
...

# ❌ O agente não localizou .ahrena/ nem leu o .directives.
# ❌ Ignorou o idioma padrão (pt-BR) definido nas diretivas.
# ❌ Não consultou paths.samples para localizar o template correto.
# ❌ Não ofereceu versões nos idiomas obrigatórios.
```

## Validação Automatizada

- **Ferramenta:** verificação pelo próprio agente no início de cada sessão
- **Momento:** antes de qualquer produção de artefato ou comunicação formal
- **Métrica:** 100% das sessões devem ter o `.ahrena/.directives` consultado e aplicado
