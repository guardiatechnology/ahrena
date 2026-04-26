# Codex: Design System da Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Camada de execução do Brand Kit em qualquer interface ou material

## Visão Geral

O Design System é a camada de execução do Brand Kit. Enquanto o Brand Kit responde *o que* a marca é, o Design System responde *como* a marca se materializa em cada ponto de contato. Este Codex consolida princípios, escopo, governança, fontes de referência e stack de implementação. É a porta de entrada antes de construir telas, materiais, dashboards ou peças.

## Contexto

- **Domínio:** governança e execução visual da marca em produto, site, app e canais digitais.
- **Público-alvo:** designers, frontend, mobile, agentes de IA que produzem UI (warrior-hephaestus, warrior-iris).
- **Atualização:** quando a página *Design System* no Notion for revisada ou quando houver mudança na stack/governança.

## Conteúdo

### Relação com o Brand Kit

| Brand Kit | Design System |
|-----------|---------------|
| Logomarca e Logotipos | Como logos aparecem em interfaces, materiais e assinaturas |
| Cores | Tokens aplicados em componentes, estados e categorias de dados |
| Tipografia | Escalas hierárquicas em botões, cards, tabelas e dashboards |
| Voz da marca | Microcopy, rótulos, mensagens de erro e confirmação |
| Fotografia | Tratamento de imagens em banners, cards e materiais promocionais |

A coerência entre identidade e execução é o que faz a marca ser **reconhecível**, não apenas bonita.

### Escopo

| Área | Conteúdo |
|------|----------|
| AI-First Experience | Diretriz estrutural de UX agêntica: conversa primária, workspace ao vivo, transparência, controle graduado |
| Componentes | Padrões reutilizáveis (botões, cards, alertas, formulários, badges, blocos de conteúdo) |
| Elementos gráficos | Texturas, padrões, formas auxiliares e recursos decorativos |
| Ícones | Biblioteca de símbolos para ações, navegação, estados, categorias |
| Gráficos | Padrões para data viz, dashboards e infográficos |

### Onde se aplica

1. **Plataforma** — telas de reconciliação, dashboards, fluxos operacionais, relatórios.
2. **Site e materiais comerciais** — landing pages, one-pagers, decks, propostas.
3. **App** — interfaces mobile com adaptações de densidade e toque.
4. **Canais de mensageria** — WhatsApp, Telegram, Slack (stickers, cards interativos, templates).
5. **Documentos técnicos** — contratos, relatórios operacionais, comunicações formais.

Adaptações são permitidas em dimensão e densidade. **Identidade nunca muda.**

### Princípios

1. **AI-First por padrão.** Experiência agêntica; o Isac é o centro da interação. Features são capacidades do agente, não destinos de navegação. Detalhes em [codex-ai-first-experience](codex-ai-first-experience.md).
2. **Token antes de valor bruto.** Componentes consomem tokens (cor, tipografia, espaçamento), nunca valores hardcoded. Mudança no token propaga em todo o sistema.
3. **Composição sobre customização.** Combinar componentes existentes antes de criar novos. Customização gera divergência; divergência gera retrabalho.
4. **Acessibilidade é requisito.** WCAG 2.1 AA é piso, não meta. Foco, screen reader e teclado fazem parte do componente.
5. **Densidade serve ao contexto.** Dashboards densos e formulários amplos coexistem; o que muda é a aplicação dos tokens de espaçamento.
6. **Documentar a exceção.** Toda fuga do padrão precisa de justificativa registrada (alimenta a evolução do sistema).

### Fontes de referência

| Fonte | O que mora lá |
|-------|---------------|
| Notion | Intenção, regras de uso, princípios e governança (fonte conceitual) |
| Código (`@guardia/design-system`) | Implementação oficial — fonte da verdade para comportamento |
| Chromatic | Catálogo visual versionado (todos os estados de cada componente) |
| Figma | Biblioteca de design com variantes e tokens espelhados |

**Divergências são tratadas como bug.** A correção começa pela origem da divergência e propaga para os demais pontos.

### Stack de implementação

- **Componentes:** [shadcn/ui](https://ui.shadcn.com/) como base, [Tailwind CSS](https://tailwindcss.com/) para estilo, [CopilotKit](https://www.copilotkit.ai/) para interações agênticas. Hoje Tailwind v3; migração para v4 condicionada à compatibilidade.
- **Ícones:** [Lucide](https://lucide.dev/).
- **Gráficos:** [shadcn/ui Charts](https://ui.shadcn.com/charts), respeitando o schema de cores de data viz.
- **Distribuição:** biblioteca `@guardia/design-system` (consumo obrigatório, ver [lex-design-system-library](../lexis/lex-design-system-library.md)).

### Governança

Propostas de novos componentes, padrões, ícones ou tipos de gráfico passam pelo fluxo de governança. Antes de criar algo novo, verificar se o problema não é resolvido por um padrão existente. Lacunas reais viram issues no repositório de `@guardia/design-system` com contexto, caso de uso e proposta de solução.

O sistema evolui com uso. Cada ativo precisa resistir à pergunta: **isso vai ser reutilizado ou é específico de um caso?**

### Links úteis

- Repositório: [github.com/guardiatechnology/design-system](https://github.com/guardiatechnology/design-system) (em revisão)
- Chromatic catálogo: [69e15f3b0534f646ac88774b-cpmytvatdp.chromatic.com](https://69e15f3b0534f646ac88774b-cpmytvatdp.chromatic.com/) (em revisão)
- Chromatic library: [chromatic.com/library?appId=69e15f3b0534f646ac88774b](https://www.chromatic.com/library?appId=69e15f3b0534f646ac88774b)
- Figma: [figma.com/design/F0TkqO6HigGa3C0P8XK9zL/Design-System](https://www.figma.com/design/F0TkqO6HigGa3C0P8XK9zL/Design-System) (despriorizado)

## Referências

- Notion — Branding / Design System
- [codex-design-system-components](codex-design-system-components.md), [codex-ai-first-experience](codex-ai-first-experience.md)
- [lex-design-system-library](../lexis/lex-design-system-library.md), [lex-ai-first-experience](../lexis/lex-ai-first-experience.md)
