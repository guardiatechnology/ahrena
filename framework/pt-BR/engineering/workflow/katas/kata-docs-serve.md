# Kata: Servidor Local de Documentação (MkDocs)

> **Prefixo:** `kata-` | **Tipo:** Habilidade Repetível | **Escopo:** Servidor local de documentação Markdown para o diretório `docs/` usando MkDocs

## Objetivo

Este Kata define o procedimento para **iniciar um servidor local de documentação** que serve todos os arquivos `.md` em `docs/` (modelos de domínio, documentos de API, eventos) como um site navegável em `http://localhost:8000`, usando MkDocs. O servidor recarrega automaticamente ao detectar alterações nos arquivos, sendo útil durante sessões ativas de design.

## Quando Usar

- Quando um desenvolvedor ou agente quiser navegar pela documentação gerada localmente (após executar `cry-feature-design`, `cry-api-design` ou `cry-event-storm`)
- Quando estiver revisando ou validando modelos de domínio, docs de API e docs de eventos como um site unificado antes de commitar
- Quando invocado por um Warrior ou diretamente do CLI como utilitário de desenvolvimento

## Entradas

| Entrada | Obrigatória | Descrição |
|---------|:-----------:|-----------|
| Raiz do projeto | Sim | Diretório onde `.ahrena/.directives` e `mkdocs.yml` residem (diretório de trabalho atual por padrão) |
| Porta | Não | Porta para o servidor. Padrão: `8000` |

## Fluxo de Trabalho

```
Progresso:
- [ ] 1. Ler diretivas
- [ ] 2. Verificar instalação do MkDocs
- [ ] 3. Resolver docs_dir
- [ ] 4. Verificar ou gerar mkdocs.yml
- [ ] 5. Iniciar servidor
```

### Passo 1: Ler Diretivas

1. Ler `.ahrena/.directives` para obter:
   - `paths.domain` — documentos de modelo de domínio (ex.: `docs/domain`)
   - `paths.oas` — especificação e documentos de API (ex.: `docs/oas`)
   - `paths.events` — documentos de eventos (ex.: `docs/events`)
2. Derivar `docs_dir` como o diretório pai comum dos três paths (ex.: `docs/` quando todos os paths são `docs/{seção}`)
3. Se os paths divergirem e não houver pai comum, usar `docs/` como padrão e avisar o usuário

### Passo 2: Verificar Instalação do MkDocs

1. Executar `mkdocs --version`
2. Se o MkDocs não for encontrado:
   - Executar `pip install mkdocs mkdocs-material`
   - Se o pip estiver indisponível, informar o usuário e parar com uma mensagem clara: "Instale Python e pip primeiro, depois execute `pip install mkdocs mkdocs-material`"
3. Verificar se o tema Material está disponível: `python -c "import material"` (opcional; usado no Passo 4)

### Passo 3: Resolver docs_dir

1. Confirmar que `docs_dir` é um diretório que existe na raiz do projeto
2. Se não existir, criá-lo: `mkdir -p {docs_dir}`
3. Se `docs_dir` estiver vazio, criar um `index.md` mínimo:
   ```markdown
   # Guardia Platform Docs

   Documentação gerada pelo framework Ahrena.
   Navegue usando a barra lateral.
   ```

### Passo 4: Verificar ou Gerar mkdocs.yml

1. Verificar se `mkdocs.yml` existe na raiz do projeto
2. **Se existir:** usar como está — não sobrescrever; prosseguir para o Passo 5
3. **Se não existir:** gerar um `mkdocs.yml` mínimo:

```yaml
site_name: Guardia Platform Docs
docs_dir: {docs_dir}
theme:
  name: material   # usa 'mkdocs' se mkdocs-material não estiver instalado
```

   - Se o tema Material não estiver instalado (verificação do Passo 2 falhou), usar `name: mkdocs`
   - Gravar o arquivo na raiz do projeto como `mkdocs.yml`
   - Informar o usuário: "`mkdocs.yml` gerado na raiz do projeto. Edite-o para personalizar navegação, tema ou nome do site."

### Passo 5: Iniciar Servidor

1. Executar `mkdocs serve --dev-addr 127.0.0.1:{porta}` (porta padrão: `8000`)
2. Informar ao usuário:
   - URL: `http://127.0.0.1:8000` (ou a porta configurada)
   - Diretório de docs sendo servido: `{docs_dir}/`
   - Hot-reload: ativo (alterações em arquivos `.md` atualizam automaticamente)
3. O servidor roda em primeiro plano; o usuário para com `Ctrl+C`

## Entregável

Um servidor MkDocs rodando em `http://127.0.0.1:8000` servindo todos os arquivos `.md` em `docs/` como um site navegável com recarga automática ao detectar alterações.

## Observações

- O MkDocs descobre automaticamente todos os arquivos `.md` em `docs_dir` quando nenhuma chave `nav` está definida em `mkdocs.yml`. Para personalizar a ordem de navegação, adicione uma seção `nav:` manualmente.
- O tema Material (`mkdocs-material`) oferece busca, modo escuro e navegação melhorada. Instale com `pip install mkdocs-material`.
- O servidor é apenas para desenvolvimento local — não exponha publicamente sem autenticação.

## Referências

- `lex-directives` — paths canônicos lidos no Passo 1
- `kata-domain-model`, `kata-api-design-doc`, `kata-events-doc` — katas que produzem os arquivos `.md` servidos por este kata
