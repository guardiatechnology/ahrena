# Lexis: Uso Correto do Logotipo da Guardia

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Logotipo, símbolo e logo isolado da Guardia em qualquer aplicação

## Propósito

Preservar legibilidade e reconhecimento. O logotipo principal (símbolo violeta com G laranja + Lastica) tem versões para cada contexto cromático. Aplicar a versão errada (ex.: principal sobre fundo violeta) faz o símbolo se confundir com o fundo e quebra a identidade.

## Lei

> **Toda aplicação do logotipo da Guardia DEVE usar APENAS os arquivos oficiais e DEVE selecionar a variante correta conforme o fundo: (1) **Logotipo principal** (símbolo violeta + G laranja) sobre fundos claros e escuros fora do espectro do violeta; (2) **Logotipo secundário** (símbolo laranja + G violeta) sobre fundos no espectro do violeta; (3) **Monocromático preto** sobre fundos claros quando cor não estiver disponível; (4) **Monocromático branco** sobre fundos escuros quando cor não estiver disponível; (5) **Logo isolado** (sem o lettering "Guardia") apenas em aplicações reduzidas (favicon, avatar, assinatura compacta) ou onde a marca já está estabelecida no contexto. É PROIBIDO recolorir, distorcer, rotacionar, aplicar contornos, sombras, gradientes ou efeitos; substituir a Lastica por outra fonte; reduzir o logotipo abaixo da dimensão mínima documentada; ou aplicar a versão errada para o fundo (ex.: logotipo principal sobre violeta).**

## Abrangência

- **Aplica-se a:** UI (favicons, headers, tela de login), e-mails, decks, propostas, contratos, redes sociais, eventos, brindes, vídeos, parcerias.
- **Agentes vinculados:** designers, marketing, comercial, frontend/mobile (favicon, headers), agentes de IA que produzam peças com a marca.
- **Exceções:** parodias internas claramente marcadas (off-brand), comemorações sazonais aprovadas pelo Brand. Toda exceção pública exige aprovação do CEO ou responsável designado pelo Brand.

## Consequências de Violação

1. **Identidade:** logotipo distorcido ou recolorido enfraquece reconhecimento e cria sensação de descuido.
2. **Legibilidade:** versão errada para o fundo torna o símbolo invisível.
3. **Remediação:** substituir pelo arquivo oficial correspondente; restaurar dimensões originais; remover efeitos aplicados; revisar checklist de variante por fundo antes de republicar.

## Exemplos

### Correto

Site sobre fundo branco usando o logotipo principal; tela de login com fundo Violeta 500 usando o logotipo secundário; contrato em P&B usando o monocromático preto sobre página branca; favicon usando o logo violeta isolado; banner sobre Violeta Profundo usando logo laranja transparente; assinatura de e-mail com logotipo principal exportado dos arquivos oficiais.

### Incorreto

Logotipo principal sobre fundo Violeta 500 (símbolo violeta se funde com o fundo); logotipo recolorido em verde para "combinar com o tema do post"; logotipo com sombra "para ganhar destaque"; texto "Guardia" digitado em Helvetica simulando o logotipo; logo abaixo de 16px de altura em UI; logotipo distorcido em proporção 16:9 para preencher um banner.

## Validação Automatizada

- **Ferramenta:** revisão automatizada (warrior-hephaestus + revisor humano de Brand) detectando logotipos não-oficiais ou aplicações em fundo conflitante; biblioteca `@guardia/design-system` expondo um único componente `<Logo variant="..." />` que sempre escolhe a variante certa.
- **Momento:** revisão de PR de UI; revisão de Brand para peças comerciais e institucionais; auditoria trimestral de assets externos.
- **Métrica:** 0 logotipos recoloridos/distorcidos em peças publicadas; 100% das aplicações em produto consumindo `<Logo />` da biblioteca; 0 aplicações da versão principal sobre fundo no espectro do violeta.

## Referências

- [codex-brand-logo](../codex/codex-brand-logo.md)
- Notion — Branding / Logomarca e Logotipos
