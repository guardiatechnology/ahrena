# Lexis: Experiência AI-First por Padrão

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Plataforma e app da Guardia (interfaces voltadas ao usuário final)

## Lei

> **Toda interface usada por humanos na plataforma e no app da Guardia DEVE adotar o padrão AI-First: conversa com o Isac como superfície primária, workspace ao vivo reativo ao diálogo, transparência de raciocínio em tempo real (plano, fontes, decisões), controle graduado (pausar, intervir, aprovar) e auditabilidade nativa. É proibido construir arquitetura principal por menus laterais de features, modais bloqueantes pré-conversa, dashboards permanentes para o usuário monitorar ou esconder o que o agente está fazendo atrás de loaders genéricos.**

## Exemplos

### Correto

Tela inicial = chat com o Isac em primeiro plano; workspace renderiza, em tempo real, fontes consultadas e artefatos (tabelas, gráficos, documentos) como resposta da conversa; ações irreversíveis (envio, baixa contábil, liberação de valor) são pontos de confirmação explícita; usuário pode pausar, editar plano ou aprovar passos sensíveis.

### Incorreto

Tela inicial com sidebar (Conciliação, Relatórios, Regras, Integrações) e o Isac como botão flutuante; formulário com 12 campos para criar uma regra em vez de descrição em linguagem natural; loaders genéricos sem detalhe de plano ou fontes; resposta final reduzida a "Concluído. 127 transações conciliadas." sem rastro.

## Validação Automatizada

- **Ferramenta:** revisão de design (warrior-hephaestus + revisor humano de Brand) com checklist agêntico; testes E2E confirmando que toda jornada crítica parte da conversa; auditoria periódica da árvore de navegação.
- **Momento:** revisão de design (pré-implementação), revisão de PR de UI, auditoria trimestral de produto.
- **Métrica:** 0 telas principais com sidebar de features como arquitetura primária; 100% das ações irreversíveis com confirmação explícita; rastro completo de plano/fontes em 100% das execuções do Isac visíveis ao usuário.
