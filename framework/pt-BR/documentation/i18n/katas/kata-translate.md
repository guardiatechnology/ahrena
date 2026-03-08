# Kata: Tradução de Documentação

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Tradução de qualquer documentação técnica

## Objetivo

Este Kata define o procedimento padronizado para traduzir documentação técnica de um idioma para outro. É genérico — funciona para documentação do Ahrena, documentação de projetos e qualquer outro conteúdo técnico em Markdown.

O diferencial deste Kata é a consulta obrigatória às regras e guias **específicos de cada idioma-alvo**, garantindo que cada tradução respeite as particularidades linguísticas do destino.

## Quando Usar

- Quando um documento precisa ser traduzido para um ou mais idiomas
- Quando um documento existente é atualizado e as traduções precisam ser sincronizadas
- Quando o usuário solicita explicitamente a tradução de um arquivo
- Quando invocado pelo `cry-translate` ou pelo `warrior-translator`

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Arquivo-fonte | Sim | Caminho do documento no idioma de origem |
| Idioma(s) alvo | Não | Código(s) BCP 47. Se omitido, traduzir para todos os idiomas de `language.i18n` exceto o de origem |

## Workflow

```
Progresso:
- [ ] 1. Leitura das diretivas e regras
- [ ] 2. Identificação do contexto
- [ ] 3. Consulta das regras do idioma-alvo
- [ ] 4. Tradução do conteúdo
- [ ] 5. Salvamento no caminho correto
- [ ] 6. Validação final
```

### Passo 1: Leitura das Diretivas e Regras

1. Ler `.ahrena/.directives` para obter:
   - `language.default` — idioma padrão (fonte da verdade)
   - `language.i18n` — lista de idiomas obrigatórios
   - `naming.addressing` — padrão de endereçamento
2. Confirmar que o(s) idioma(s) alvo estão na lista `language.i18n`

### Passo 2: Identificação do Contexto

1. Ler o arquivo-fonte integralmente
2. Identificar o idioma de origem (pelo caminho ou pelo conteúdo)
3. Determinar se o documento é do framework Ahrena (está em `framework/`) ou genérico
4. Se for do framework: verificar se `lex-framework-language` se aplica
5. Calcular o caminho de destino para cada idioma-alvo

**Exemplo (framework):**
- Fonte: `framework/pt-BR/documentation/i18n/lexis/lex-language.md`
- Destino (es): `framework/es/documentation/i18n/lexis/lex-language.md`
- Destino (en): `framework/en/documentation/i18n/lexis/lex-language.md`

### Passo 3: Consulta das Regras do Idioma-Alvo

Para **cada idioma-alvo**, consultar na seguinte ordem:

1. `lex-language` — regras transversais (sempre)
2. `lex-language-{lang}` — regras específicas do idioma-alvo
3. `codex-language` — guia transversal
4. `codex-language-{lang}` — guia específico do idioma-alvo

Internalizar as regras antes de iniciar a tradução.

### Passo 4: Tradução do Conteúdo

1. Traduzir o conteúdo aplicando as regras do idioma-alvo
2. **Preservar obrigatoriamente:**
   - Toda a estrutura de headings, formatação Markdown
   - Nomes próprios do Ahrena (Lexis, Codex, Katas, etc.)
   - Blocos de código, caminhos de arquivo, URLs
   - Metadados e referências
3. **Traduzir:**
   - Títulos, corpo de texto, descrições em tabelas
   - Cabeçalhos (Tipo, Escopo) para o equivalente no idioma-alvo
4. **Aplicar particularidades do idioma:**
   - Tom e formalidade conforme `lex-language-{lang}`
   - Termos técnicos conforme `codex-language-{lang}`
   - Falsos cognatos conforme tabelas de referência

### Passo 5: Salvamento no Caminho Correto

1. Criar os diretórios intermediários se não existirem
2. Salvar o arquivo traduzido no caminho calculado no Passo 2
3. O nome do arquivo permanece inalterado (prefixo + nome em kebab-case)

### Passo 6: Validação Final

- [ ] O arquivo traduzido existe no caminho correto
- [ ] Todas as seções do original estão presentes
- [ ] Os headings seguem a mesma hierarquia
- [ ] Termos canônicos do Ahrena não foram traduzidos
- [ ] Caminhos e referências estão preservados
- [ ] O idioma do conteúdo está correto (sem trechos no idioma de origem)
- [ ] A formatação Markdown está intacta
- [ ] As regras de `lex-language-{lang}` foram respeitadas

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Arquivo(s) traduzido(s) | Markdown (.md) | Caminho calculado conforme contexto |

## Restrições

- Nunca alterar o arquivo-fonte durante a tradução
- Nunca traduzir termos canônicos do Ahrena
- Nunca omitir ou fundir seções do original
- Sempre consultar as regras do idioma-alvo antes de traduzir
- Sempre usar o idioma padrão como fonte da verdade para traduções

## Referências

- `lex-language` — Regras transversais de tradução
- `lex-language-ptbr`, `lex-language-en`, `lex-language-es` — Regras por idioma
- `codex-language` — Guia transversal
- `codex-language-ptbr`, `codex-language-en`, `codex-language-es` — Guias por idioma
- `warrior-translator` — Agente que executa este Kata
- `cry-translate` — Comando que invoca este fluxo
