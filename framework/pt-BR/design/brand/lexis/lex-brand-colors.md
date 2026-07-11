# Lexis: Paleta de Cores Aprovada e Combinações WCAG

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Identidade visual da Guardia em qualquer ponto de contato

## Propósito

Garantir reconhecimento e acessibilidade. A paleta da Guardia carrega significado (Confiança, Eficiência, Acolhimento, Excelência, Estabilidade). Cores fora da paleta diluem a marca; combinações sem contraste bloqueiam usuários e desrespeitam WCAG 2.1.

## Lei

> **Toda peça da Guardia (interface, material, documento, post, slide, e-mail) DEVE usar exclusivamente a paleta oficial — Amarelo Brilhante #FFC30A, Laranja Quente #F47720, Rosa Suave #DB6286, Violeta Profundo #552973, Cinza Báltico #3A3A44, Mono Branco #FDFDFD e Mono Preto #0E1016, com as escalas 100/200/500/700/900 — e DEVE atingir WCAG 2.1 AA (4.5:1 para texto normal, 3:1 para texto grande/UI). As combinações Branco sobre Amarelo 500 (1.61:1) e Branco sobre Laranja 500 (2.80:1) são PROIBIDAS — para texto/UI sobre Laranja, aprofundar para Laranja 700 (#AB5316, 5.28:1). Combinações no nível 3:1–4.5:1 ficam restritas a títulos, botões e badges. Cores de sinal (Verde #00BF63, Amarelo #FFDE59, Vermelho #FF3131, Azul #004AAD) são reservadas a data viz e estados críticos do sistema.**

## Abrangência

- **Aplica-se a:** UI (plataforma, site, app), materiais comerciais e institucionais, decks, documentos, e-mails, posts em redes sociais, ícones e ilustrações.
- **Agentes vinculados:** designers, frontend, mobile, marketing, suporte, agentes de IA que gerem peças visuais ou interfaces.
- **Exceções:** logos de parceiros e marcas de terceiros (apresentadas com cor original). Casos específicos exigem ADR ou registro de exceção no Notion.

## Consequências de Violação

1. **Identidade:** cor fora da paleta enfraquece reconhecimento e quebra coerência com Brand Kit.
2. **Acessibilidade:** combinação abaixo do mínimo WCAG bloqueia usuários com baixa visão; expõe a marca a passivo regulatório (LGPD, ADA, normas de acessibilidade).
3. **Remediação:** substituir pelo tom aprovado; em fundos saturados (laranja/rosa), aprofundar para o tom 700 da escala antes de aplicar branco; em fundos amarelos, substituir branco por Violeta 500 ou Cinza 500.

## Exemplos

### Correto

Texto preto sobre Amarelo 500 (13.06:1, AAA); texto Branco sobre Cinza 500 (11.24:1, AAA); botão Violeta 500 com label Branco (10.76:1, AAA); badge Laranja 500 com texto Violeta 500 reservado a botões/títulos (3.85:1, AA grande); gráfico de variação financeira usando Verde Sinal/Vermelho Sinal apenas no eixo de dados.

### Incorreto

Texto branco sobre Amarelo 500 (1.61:1, ilegível); cor "roxa aproximada" inventada para complementar o brand; verde institucional usado como cor de marca em hero; uso de #552973 fora da paleta tokenizada (hardcoded ao lado de cores não-aprovadas).

## Validação Automatizada

- **Ferramenta:** Stylelint com plugin de paleta, axe-core e Lighthouse a11y em CI; revisão visual automatizada (warrior-hephaestus) sinalizando combinações abaixo do mínimo WCAG; tokens centralizados em `@guardia/design-system`.
- **Momento:** pre-commit, CI de UI, revisão de design para materiais não-UI.
- **Métrica:** 0 valores cromáticos fora da paleta no `main`; 100% de combinações texto/fundo ≥ 4.5:1 (texto normal) e ≥ 3:1 (UI/grande); 0 ocorrências da combinação proibida Amarelo 500 + Branco.

## Referências

- [codex-brand-colors](../codex/codex-brand-colors.md)
- WCAG 2.1, níveis AA e AAA
- Notion — Branding / Cores
