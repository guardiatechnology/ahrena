# Codex: Paleta de Cores da Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Cor em qualquer ponto de contato da Guardia

## Visão Geral

Referência única da paleta da Guardia: cores base com significado de marca, escalas 100/200/500/700/900, tons mono (técnicos), cores de sinal (data viz) e combinações WCAG aprovadas, restritas e proibidas. Consultar antes de aplicar cor em UI, deck, documento ou material gráfico.

## Contexto

- **Domínio:** identidade cromática, tokens, acessibilidade.
- **Público-alvo:** designers, frontend, mobile, marketing, suporte, agentes de IA que gerem peças visuais.
- **Atualização:** quando a página *Cores* no Notion for revisada; tokens em `@guardia/design-system` espelham este Codex.

## Conteúdo

### Cores base e significado

| Cor | HEX | Significado |
|-----|-----|-------------|
| Amarelo Brilhante | `#FFC30A` | Confiança e Transparência — otimismo e clareza |
| Laranja Quente | `#F47720` | Eficiência e Agilidade — energia e dinamismo |
| Rosa Suave | `#DB6286` | Acolhimento e Inclusão — empatia, respeito |
| Violeta Profundo | `#552973` | Profundidade e Excelência — segurança, conformidade |
| Cinza Báltico | `#3A3A44` | Estabilidade e Integridade — profissionalismo |

### Escalas (100, 200, 500 base, 700, 900)

| Cor | 100 | 200 | 500 (base) | 700 | 900 |
|-----|-----|-----|------------|-----|-----|
| Amarelo Brilhante | `#FFF3CE` | `#FFE490` | `#FFC30A` | `#B28807` | `#664E04` |
| Laranja Quente | `#FDE3D1` | `#FAC29B` | `#F47720` | `#AB5316` | `#612F0D` |
| Rosa Suave | `#F7DFE6` | `#EEB8C8` | `#DB6286` | `#99445D` | `#572735` |
| Violeta Profundo | `#DCD3E2` | `#B29FC0` | `#552973` | `#3B1D50` | `#22102E` |
| Cinza Báltico | `#D7D7D9` | `#A6A6AA` | `#3A3A44` | `#28282F` | `#17171B` |

### Tons mono (técnicos)

| Cor | Uso | HEX |
|-----|-----|-----|
| Mono Branco | Fundos claros, superfícies, plot areas | `#FDFDFD` |
| Mono Preto | Tinta de texto, eixos, linhas de base | `#0E1016` |

Função técnica, fora da paleta cromática da marca.

### Cores de sinal (data viz e estados críticos)

| Cor | Semântica | HEX |
|-----|-----------|-----|
| Verde Sinal | Positivo, saúde, crescimento | `#00BF63` |
| Amarelo Sinal | Atenção, pendência, alerta | `#FFDE59` |
| Vermelho Sinal | Negativo, queda, exceção crítica | `#FF3131` |
| Azul Sinal | Informativo, baseline, referência | `#004AAD` |

Convenção universal (verde = positivo, amarelo = atenção, vermelho = negativo, azul = informativo). **Não substituem a paleta principal** — uso fora de gráficos, dashboards e alertas exige justificativa.

### Combinações WCAG aprovadas (qualquer uso)

| Fundo | Texto | Contraste | WCAG |
|-------|-------|-----------|------|
| Amarelo 500 (`#FFC30A`) | Preto | 13.06:1 | AAA em qualquer tamanho |
| Cinza 500 (`#3A3A44`) | Branco | 11.24:1 | AAA em qualquer tamanho |
| Violeta 500 (`#552973`) | Rosa 200 (`#EEB8C8`) | 6.32:1 | AA em qualquer tamanho |
| Rosa 500 (`#DB6286`) | Preto | 6.10:1 | AA qualquer tamanho, AAA texto grande |
| Cinza 500 (`#3A3A44`) | Cinza 200 (`#A6A6AA`) | 4.63:1 | AA texto normal (evitar em corpos longos) |

### Combinações restritas (títulos, botões, badges)

Atendem WCAG mínimo apenas para texto grande (18pt regular ou 14pt bold em diante):

| Fundo | Texto | Contraste |
|-------|-------|-----------|
| Laranja 500 (`#F47720`) | Violeta 500 (`#552973`) | 3.85:1 |
| Violeta 500 (`#552973`) | Laranja 500 (`#F47720`) | 3.85:1 |
| Rosa 500 (`#DB6286`) | Branco | 3.44:1 |

### Combinações proibidas

| Fundo | Texto | Contraste | Ação |
|-------|-------|-----------|------|
| Amarelo 500 (`#FFC30A`) | Branco | 1.61:1 | Remover; ilegível em qualquer tamanho |
| Laranja 500 (`#F47720`) | Branco | 2.80:1 | Abaixo do piso de 3:1; aprofundar para Laranja 700 (`#AB5316`, 5.28:1) para texto/UI sobre claro |

### Ajustes para liberar texto de corpo

- Texto branco sobre fundos saturados (laranja/rosa): aprofundar para o tom 700 (Laranja 700 + Branco = 5.28:1, AA; Rosa 700 + Branco = 6.9:1, AA completo).
- Texto claro sobre Amarelo: substituir branco por Violeta 500 (6.70:1) ou Cinza 500 (>8:1).
- Para identidade cromática com texto claro sobre laranja/rosa: usar Rosa 100 ou Amarelo 100 no lugar do branco.

## Referências

- Notion — Branding / Cores
- WCAG 2.1 (AA: 4.5:1 texto normal, 3:1 grande/UI; AAA: 7:1 texto normal, 4.5:1 grande)
- Tokens implementados em `@guardia/design-system`
