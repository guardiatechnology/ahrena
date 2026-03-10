# Codex: Filosofia de Manutenção Open Source em Rust

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Manutenção de Crates Rust, Gestão de Contribuições e Sustentabilidade de Projetos Open Source

## Visão Geral

Este Codex documenta os princípios e práticas para manutenção sustentável de projetos Rust open source. É baseado na experiência de Andrew Gallant (BurntSushi) ao longo de mais de uma década mantendo crates amplamente usados como `regex`, `ripgrep`, `bstr`, `csv`, `walkdir` e outros. O objetivo é guiar agentes e desenvolvedores na tomada de decisões sobre contribuições, feature requests, gestão de issues e limites saudáveis de manutenção.

## Contexto

- **Domínio:** Sustentabilidade de projetos open source, gestão de contribuições, comunicação com usuários, decisões de escopo.
- **Público-alvo:** Agentes de IA (Warriors) que mantêm ou contribuem para crates Rust, desenvolvedores mantenedores.
- **Atualização:** Quando novas práticas de sustentabilidade open source emergirem na comunidade Rust.

## Conteúdo

### Princípios

1. **Código é compartilhado por prazer, não por obrigação:** A motivação intrínseca de um mantenedor é o ato de compartilhar código que ajuda outros a resolver problemas. Quando essa motivação se esgota, a qualidade do projeto sofre. Preservar a motivação é uma responsabilidade do mantenedor.
2. **Estabeleça limites explícitos:** Dizer "não" a uma feature request é uma decisão legítima de manutenção, especialmente quando o custo de manutenção futuro supera o benefício. Limites claros protegem tanto o mantenedor quanto o projeto.
3. **A assimetria mantenedor-usuário é real:** Um usuário faz uma única issue. O mantenedor lida com centenas. Empatia funciona nos dois sentidos: o mantenedor deve ter empatia com o usuário; o usuário deve ter empatia com o mantenedor.
4. **Qualidade de issue é responsabilidade do reporter:** Issues sem reprodução mínima, sem versão afetada, sem contexto de uso são difíceis de tornar acionáveis. Templates de issue existem para reduzir esse atrito.
5. **Emoções são combustível, não fraqueza:** A motivação para refatorar código ruim, para melhorar documentação, para corrigir um bug difícil frequentemente vem de uma resposta emocional ao problema. Isso é válido e produtivo.

### Padrões e Convenções

| Aspecto | Padrão | Justificativa |
|---------|--------|---------------|
| Feature requests | Avaliar custo de manutenção futura, não apenas o benefício imediato | Features adicionam superfície de API que deve ser mantida para sempre |
| Issues sem reprodução | Solicitar reprodução mínima antes de investigar | Sem reprodução, o tempo do mantenedor é desperdiçado |
| Pull requests grandes | Discutir o design antes de implementar | Evita rejeição de PRs com muito trabalho investido |
| Backlog crescente | Estabelecer limites de tempo de resposta realistas | Expectativas claras reduzem frustração de ambos os lados |
| Decisões de escopo | Documentar o que o projeto faz e não faz no README | Previne feature requests fora do escopo |

### Decisões Vigentes

| Decisão | Descrição | Status |
|---------|---------|--------|
| Template de issue obrigatório | Todo repositório DEVE ter template de issue com campos: versão afetada, reprodução mínima, comportamento esperado vs observado. | Ativa |
| CHANGELOG mantido | Todo repositório DEVE manter um CHANGELOG.md atualizado a cada release seguindo o formato Keep a Changelog. | Ativa |
| SemVer estrito | Versões seguem SemVer. Breaking changes incrementam MAJOR. Adições incrementam MINOR. Correções incrementam PATCH. | Ativa |
| Documentação de escopo no README | O README DEVE incluir uma seção explícita sobre o que o projeto faz e o que está fora do escopo. | Ativa |
| Benchmarks como documentação | Crates de performance DEVEM incluir benchmarks públicos e reproduzíveis como parte da documentação. | Ativa |

### Restrições Técnicas

- Todo crate publicado no crates.io DEVE ter documentação completa de API (`cargo doc` sem warnings).
- Todo crate DEVE ter CI configurado com `cargo test`, `cargo clippy` e `cargo fmt --check`.
- Breaking changes NUNCA devem ser publicados em versões MINOR ou PATCH.
- Crates DEVEM ter um arquivo `LICENSE` explícito (MIT e/ou Apache-2.0 são os padrões do ecossistema Rust).

## Diagrama de Referência

```
Ciclo de Vida de uma Contribuição:

Issue/PR aberto
      │
      ▼
┌─────────────────────────┐
│ Tem reprodução mínima?  │──── Não ──► Solicitar reprodução
└─────────────────────────┘
      │ Sim
      ▼
┌─────────────────────────┐
│ Está no escopo?         │──── Não ──► Fechar com explicação de escopo
└─────────────────────────┘
      │ Sim
      ▼
┌─────────────────────────┐
│ Custo de manutenção     │──── Alto ──► Discutir design antes de implementar
│ é aceitável?            │
└─────────────────────────┘
      │ Baixo/Médio
      ▼
┌─────────────────────────┐
│ Implementar / Revisar   │
│ e fazer merge           │
└─────────────────────────┘

Saúde do Projeto:
  Motivação do mantenedor ──► Qualidade do código ──► Confiança dos usuários
  (preservar com limites)     (refatorar com prazer)   (construída com tempo)
```

## Glossário

| Termo | Definição |
|-------|-----------|
| **Reprodução mínima** | O menor programa ou conjunto de passos que demonstra o problema reportado. Essencial para que o mantenedor possa investigar. |
| **Escopo do projeto** | Conjunto de funcionalidades que o projeto se propõe a oferecer e manter. Feature requests fora do escopo podem ser recusadas sem justificativa técnica. |
| **Custo de manutenção** | O esforço contínuo necessário para manter uma feature funcionando ao longo do tempo, incluindo testes, documentação, compatibilidade e suporte. |
| **SemVer** | Versionamento Semântico (MAJOR.MINOR.PATCH). Contrato público sobre compatibilidade entre versões. |
| **CHANGELOG** | Arquivo que documenta mudanças entre versões de forma legível por humanos. Formato recomendado: Keep a Changelog (keepachangelog.com). |
| **Breaking change** | Mudança que quebra compatibilidade com código que usa a versão anterior da API. Requer incremento de versão MAJOR. |
| **Assimetria mantenedor-usuário** | Fenômeno onde cada usuário faz poucas interações, mas o mantenedor acumula interações de todos os usuários. Cria desequilíbrio de carga emocional e cognitiva. |

## Referências

- [My FOSS Story (BurntSushi)](https://burntsushi.net/foss/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- `codex-rust-api-design` — Design de APIs e bibliotecas em Rust

---

**Gerado com base nos ensinamentos de Andrew Gallant (BurntSushi) sobre sustentabilidade open source.**
