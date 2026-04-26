# Codex: Tipografia da Guardia — Poppins, Lastica e Roboto

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Tipografia em comunicação corrente, logos e sistemas digitais

## Visão Geral

A Guardia adota **Poppins** como tipografia corrente, **Lastica** como exclusiva dos logotipos e **Roboto** como fallback nativo para ambientes restritos. Este Codex consolida hierarquia, uso por canal, instalação e declaração CSS.

## Contexto

- **Domínio:** identidade tipográfica em qualquer canal (UI, decks, documentos, redes sociais, e-mail, app).
- **Público-alvo:** designers, frontend, mobile, marketing, comercial, agentes de IA que produzem texto em peças visuais.
- **Atualização:** quando a página *Tipografia* no Notion for revisada.

## Conteúdo

### Poppins (corrente)

Sans-serif geométrica moderna da Indian Type Foundry, distribuída sob SIL Open Font License (Google Fonts).

- **Estrutura:** geométrica com curvas suaves e traço consistente.
- **Pesos:** 9 (Thin 100 → Black 900) com itálicos.
- **Suporte:** Latin, Latin Extended, Devanagari.
- **Por que Poppins:** coerência visual com a Lastica (geometria), versatilidade para hierarquias, distribuição livre via Google Fonts (sem barreiras de licença).

### Hierarquia tipográfica recomendada

| Elemento | Peso | Observação |
|----------|------|------------|
| Título principal (H1) | Bold (700) ou SemiBold (600) | Primeira hierarquia de leitura |
| Título secundário (H2) | SemiBold (600) | Seções dentro do documento |
| Subtítulo (H3/H4) | Medium (500) | Subdivisões e destaques |
| Corpo de texto | Regular (400) | Texto corrido padrão |
| Texto de apoio | Light (300) | Legendas, notas de rodapé, metadados |
| Ênfase | Itálico ou SemiBold (600) | Destaque pontual |

### Onde usar Poppins

Documentos internos (memos, relatórios, políticas, atas); apresentações comerciais e institucionais; propostas, contratos e materiais para clientes; e-mails formais e assinaturas; interfaces digitais e materiais de produto; posts em redes sociais e blog; materiais de marketing e eventos.

### Lastica (exclusiva dos logos)

Sans-serif geométrica criada por Alberto Fontense, escolhida para a construção dos logotipos da Guardia. Reservada a:

- Construção dos logotipos da Guardia
- Assinatura oficial da marca
- Aplicações em que a marca aparece como selo ou endosso

Use exclusivamente os arquivos oficiais dos logotipos. NÃO usar em corpos de texto, títulos editoriais ou peças que não sejam logotipo.

### Roboto (fallback)

Sans-serif desenhada por Christian Robertson para o Google, distribuída sob Apache License 2.0. Tipografia padrão do Android e Google Workspace, presente nativamente em praticamente qualquer dispositivo.

**Quando usar Roboto:**

- Sistemas ou plataformas restritos à importação de fontes externas
- Ambientes corporativos com restrição de instalação
- E-mails em que o cliente renderiza apenas fontes nativas
- Documentos compartilhados com terceiros que usam fontes nativas
- Fallback em CSS quando Poppins falha no carregamento

A hierarquia da Roboto segue o mesmo padrão de pesos da Poppins (substituição direta).

### Declaração em CSS

```css
font-family: 'Poppins', 'Roboto', sans-serif;
```

Garante priorização da Poppins e fallback automático na Roboto.

### Instalação

Poppins disponível em [Google Fonts](https://fonts.google.com/specimen/Poppins):

- **macOS:** `.ttf` aberto no Font Book.
- **Windows:** `.ttf` instalado em Configurações → Fontes.
- **Google Workspace:** disponível nativamente em Docs, Slides, Sheets.
- **Microsoft 365:** instalar no SO para uso em Word, PowerPoint, Excel.
- **Web:** importar via `<link>` ou `@import` do Google Fonts.
- **Figma e Canva:** disponível nativamente.

## Referências

- Notion — Branding / Tipografia
- Poppins (Google Fonts, SIL OFL); Roboto (Apache 2.0); Lastica (proprietária)
- Tokens tipográficos em `@guardia/design-system`
