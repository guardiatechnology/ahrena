# Lexis: Uso Correto do Logotipo da Guardia

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Logotipo, símbolo e logo isolado da Guardia em qualquer aplicação

## Lei

> **Toda aplicação do logotipo da Guardia DEVE usar APENAS os arquivos oficiais e DEVE selecionar a variante correta conforme o fundo: (1) **Logotipo principal** (símbolo violeta + G laranja) sobre fundos claros e escuros fora do espectro do violeta; (2) **Logotipo secundário** (símbolo laranja + G violeta) sobre fundos no espectro do violeta; (3) **Monocromático preto** sobre fundos claros quando cor não estiver disponível; (4) **Monocromático branco** sobre fundos escuros quando cor não estiver disponível; (5) **Logo isolado** (sem o lettering "Guardia") apenas em aplicações reduzidas (favicon, avatar, assinatura compacta) ou onde a marca já está estabelecida no contexto. É PROIBIDO recolorir, distorcer, rotacionar, aplicar contornos, sombras, gradientes ou efeitos; substituir a Lastica por outra fonte; reduzir o logotipo abaixo da dimensão mínima documentada; ou aplicar a versão errada para o fundo (ex.: logotipo principal sobre violeta).**

## Exemplos

### Correto

Site sobre fundo branco usando o logotipo principal; tela de login com fundo Violeta 500 usando o logotipo secundário; contrato em P&B usando o monocromático preto sobre página branca; favicon usando o logo violeta isolado; banner sobre Violeta Profundo usando logo laranja transparente; assinatura de e-mail com logotipo principal exportado dos arquivos oficiais.

### Incorreto

Logotipo principal sobre fundo Violeta 500 (símbolo violeta se funde com o fundo); logotipo recolorido em verde para "combinar com o tema do post"; logotipo com sombra "para ganhar destaque"; texto "Guardia" digitado em Helvetica simulando o logotipo; logo abaixo de 16px de altura em UI; logotipo distorcido em proporção 16:9 para preencher um banner.

## Validação Automatizada

- **Ferramenta:** revisão automatizada (warrior-hephaestus + revisor humano de Brand) detectando logotipos não-oficiais ou aplicações em fundo conflitante; biblioteca `@guardia/design-system` expondo um único componente `<Logo variant="..." />` que sempre escolhe a variante certa.
- **Momento:** revisão de PR de UI; revisão de Brand para peças comerciais e institucionais; auditoria trimestral de assets externos.
- **Métrica:** 0 logotipos recoloridos/distorcidos em peças publicadas; 100% das aplicações em produto consumindo `<Logo />` da biblioteca; 0 aplicações da versão principal sobre fundo no espectro do violeta.
