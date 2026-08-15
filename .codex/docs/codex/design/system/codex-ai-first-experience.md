# Codex: AI-First Experience — Padrão Conversa + Workspace

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** UX agêntica da plataforma e do app da Guardia

## Conteúdo

### Princípios

1. **Conversa como interface primária.** A superfície principal é o diálogo com o Isac. Telas, painéis e visualizações nascem como resposta do agente ou contexto invocado pela conversa — não como destino de navegação.
2. **Intenção sobre funcionalidade.** O usuário expressa o resultado desejado (reconciliar, investigar, aprovar). O Isac decide ferramentas, fontes e passos. A UI não expõe features isoladas esperando que o usuário as combine.
3. **Transparência do raciocínio.** Toda execução é observável em tempo real (plano, passos, fontes consultadas, decisões tomadas). Nada acontece em caixa-preta.
4. **Controle graduado.** O usuário pode pausar, intervir, corrigir ou assumir qualquer etapa. Autonomia do Isac é um espectro ajustável, não um interruptor.
5. **Artefatos sob demanda.** Tabelas, gráficos, relatórios e dashboards são gerados quando servem à decisão em curso. Nenhum artefato vive como menu permanente aguardando o usuário abrir.
6. **Auditabilidade nativa.** Cada ação gera rastro versionado (input, contexto, decisão, resultado). A interface dá acesso direto a esse histórico.
7. **Memória estruturada.** O contexto da operação (clientes, conciliações em curso, regras, preferências) é externalizado e recuperado pelo agente, não empilhado em estados de tela.

### Padrão de layout

Conversa + workspace ao vivo, alinhado com referências do mercado (Claude da Anthropic e Manus AI da Meta).

| Região | Função | Conteúdo |
|--------|--------|----------|
| Esquerda (ou superior em mobile) | Conversa com o Isac | Entrada principal, histórico da sessão, plano de execução, status |
| Direita (ou inferior em mobile) | Workspace dinâmico | Renderiza o que o Isac está consultando ou produzindo (tabela de transações, visão de conciliação, documento, painel, fonte externa) |

O workspace é **reativo ao diálogo**. Quando a conversa muda de contexto, o workspace acompanha. O usuário não navega para encontrar uma tela.

### Regras de uso

#### Fazer

- Partir sempre da intenção do usuário e deixar o Isac decompor em passos.
- Exibir o plano antes da execução quando a tarefa tiver impacto relevante (escrita, aprovação, envio externo).
- Mostrar fontes consultadas e dados usados em cada decisão.
- Permitir editar o plano, bloquear passos ou aprovar etapas sensíveis antes da execução.
- Gerar artefatos como resultado do trabalho agêntico, com link direto para o contexto que os originou.
- Preservar memória de longo prazo fora da tela (arquivos, estado persistido, preferências), invocada quando relevante.
- Tratar ações irreversíveis (envio de mensagem, baixa contábil, liberação de valor) como pontos de confirmação explícita.

#### Não fazer

- Construir menus laterais com features empilhadas (Conciliação, Relatórios, Configurações) como arquitetura principal. Features são capacidades do Isac, não destinos.
- Abrir modais ou wizards que forcem o usuário a preencher campos antes de conversar.
- Esconder o que o agente está fazendo (loaders genéricos ou "processando..." sem detalhe).
- Duplicar o mesmo dado em múltiplas telas estáticas. Se é relevante, o Isac traz quando necessário.
- Criar dashboards permanentes que o usuário precise monitorar. Dashboards são materializados sob demanda ou disparados por regras.
- Delegar ao usuário a orquestração entre ferramentas. Se duas capacidades precisam ser combinadas, é o Isac quem combina.
- Tratar autonomia como binário (manual ou automático). Deve haver níveis configuráveis por tipo de tarefa e por perfil de usuário.

### Exemplos

#### Correto — conciliação

Usuário: *"Concilie as liquidações da Cielo de ontem e me avise o que ficou em aberto."*

- Isac exibe o plano: buscar extrato bancário → buscar arquivo EDI da Cielo → aplicar regras de matching → listar divergências.
- Workspace mostra, em tempo real, cada fonte sendo consultada e as linhas sendo conciliadas.
- Resultado aparece como artefato (tabela de divergências) com justificativa por linha.
- Usuário pode clicar em qualquer divergência, perguntar por que não bateu, e o Isac responde com rastro completo.

#### Correto — investigação

Usuário: *"Quero entender por que o fluxo de Pix do cliente X está com ruído."*

- Isac propõe investigação (períodos, contrapartes, padrões de valor).
- Workspace renderiza os cortes solicitados progressivamente.
- Nenhum relatório pré-construído é aberto. Tudo é gerado para essa pergunta específica.

#### Incorreto — sidebar de módulos

Tela inicial com sidebar (Conciliação, Relatórios, Regras, Integrações) e o chat do Isac como botão flutuante no canto.
**Motivo:** inverte a hierarquia. O Isac vira acessório de um SaaS clássico. O usuário volta a operar módulos em vez de delegar intenções.

#### Incorreto — ação invisível

Isac executa uma conciliação em segundo plano e devolve apenas "Concluído. 127 transações conciliadas."
**Motivo:** quebra transparência e auditabilidade. O usuário não tem como validar nem aprender com a operação.

#### Incorreto — formulário extenso

Formulário com 12 campos obrigatórios para criar uma regra de conciliação.
**Motivo:** o usuário deveria descrever a regra em linguagem natural ao Isac, que estrutura, valida e confirma antes de persistir.

### Implicações para o Design System

- **Componentes prioritários:** bolhas de conversa, blocos de plano de execução, trace de passos, cartões de fonte consultada, artefatos renderizáveis inline (tabela, gráfico, documento) e controles de aprovação/intervenção. Estes vivem em `@guardia/design-system` na família "Agêntico" (`ChatPanel`, `Workspace`, `PlanTrace`, `SourceCard`, `ApprovalGate`).
- **Navegação:** mínima. Histórico de sessões, memória do usuário e configurações. Nenhuma árvore de features.
- **Estados de loading:** substituídos por *streaming* de raciocínio e progresso do plano.
- **Tokens e padrões visuais:** seguem o Brand Kit; Figma traduz em componentes com paridade entre design e código.

### Referências externas

Claude (Anthropic) e Manus AI (Meta) como benchmarks do padrão agêntico. A diretriz se apoia no consenso emergente de que o layout dominante para agentes combina **conversa persistente + workspace ao vivo**, priorizando transparência sobre polimento visual.

### Governança

Qualquer exceção (tela com arquitetura tradicional, feature sem entrada agêntica) exige proposta formal no Notion, com justificativa, e aprovação do CEO ou responsável designado pelo Brand. Exceções alimentam evolução do sistema; não viram regra por omissão.
