# Cry: Criar Novo Codex

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Criação de Codex (manuais de referência)

## Descrição

Comando rápido para criar um novo Codex no Ahrena. Invoca o `kata-create-codex`, que consulta `codex-codex` e o template oficial para produzir um manual de referência completo nos três idiomas obrigatórios.

## Uso

```
/cry-new-codex <domínio> [público] [--clade clade/subclade]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `domínio` | Sim | Área de conhecimento a documentar | `"arquitetura do sistema"` |
| `público` | Não | Quem consultará o Codex. Se omitido, assume "agentes de IA e desenvolvedores" | `"backend team"` |
| `--clade` | Não | Clade/subclade na taxonomia. Se omitido, o agente infere do domínio | `--clade engineering/architecture` |

## O que o Comando Faz

1. Lê `.ahrena/.directives` para obter idiomas e convenções
2. Invoca `kata-create-codex` com os parâmetros fornecidos; o Kata consulta `codex-codex` e o template oficial e produz o Codex
3. (O Kata) Cria o Codex no idioma padrão e traduz para os demais idiomas
4. Reporta os arquivos criados

## Prompt Template

```
Contexto:
- Domínio: {{domínio}}
- Público-alvo: {{público}} (ou "agentes de IA e desenvolvedores")
- Clade/Subclade: {{clade}} (ou inferir do domínio)

Tarefa:
Execute o kata-create-codex. O Kata consulta .ahrena/.directives, codex-codex
e templates/codex-sample.md. Crie o Codex no idioma padrão e traduza para
todos os idiomas de language.i18n.

Formato de saída:
Lista de arquivos criados com confirmação de que o Codex tem escopo
delimitado, princípios acionáveis e gatilho de atualização.
```

## Exemplo de Invocação

**Criar Codex com domínio:**

```
/cry-new-codex "padrões de API REST"
```

**Output:**

```
Codex criado com sucesso.

Domínio: Padrões de API REST
Princípios: 4 princípios definidos
Gatilho de atualização: a cada nova versão da API

Arquivos criados:
1. framework/pt-BR/engineering/backend/codex/codex-api-patterns.md ✓
2. framework/es/engineering/backend/codex/codex-api-patterns.md ✓
3. framework/en/engineering/backend/codex/codex-api-patterns.md ✓
```

## Restrições

- Não cria Codex enciclopédicos — sugere dividir se o escopo for muito amplo
- Sempre executa `kata-create-codex` (nunca cria diretamente)
- Sempre cria nos três idiomas obrigatórios

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Invocação rápida (1 comando) | Procedimento completo (6 passos) |
| **Complexidade** | Baixa (domínio + público) | Alta (estruturação, redação, validação) |
| **Configura agente?** | Não | Sim (define comportamento) |
| **Exemplo** | `/cry-new-codex "padrões de API"` | Workflow de 6 passos com checklist |

## Referências

- `kata-create-codex` — Procedimento executado por este Cry (o Kata consulta os critérios de qualidade aplicáveis; ver documentação do Kata)
- `templates/codex-sample.md` — Template base
