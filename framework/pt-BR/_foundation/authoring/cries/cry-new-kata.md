# Cry: Criar Novo Kata

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Criação de Katas (procedimentos repetíveis)

## Descrição

Comando rápido para criar um novo Kata no Ahrena. Invoca o `kata-create-kata`, que consulta `codex-katas` e o template oficial para produzir um procedimento padronizado completo nos três idiomas obrigatórios.

## Uso

```
/cry-new-kata <tarefa> [contexto] [--clade clade/subclade]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `tarefa` | Sim | Tarefa a ser padronizada em procedimento | `"criar ADR"` |
| `contexto` | Não | Informações adicionais sobre o domínio ou restrições | `"projetos com microsserviços"` |
| `--clade` | Não | Clade/subclade na taxonomia. Se omitido, o agente infere da tarefa | `--clade engineering/architecture` |

## O que o Comando Faz

1. Lê `.ahrena/.directives` para obter idiomas e convenções
2. Consulta `codex-katas` para critérios de qualidade
3. Lê `templates/kata-sample.md` como base estrutural
4. Executa `kata-create-kata` com os parâmetros fornecidos
5. Cria o Kata no idioma padrão e traduz para os demais idiomas
6. Reporta os arquivos criados

## Prompt Template

```
Contexto:
- Tarefa: {{tarefa}}
- Contexto adicional: {{contexto}} (ou nenhum)
- Clade/Subclade: {{clade}} (ou inferir da tarefa)

Tarefa:
Execute o kata-create-kata. Consulte .ahrena/.directives para obter os
idiomas obrigatórios. Consulte codex-katas para critérios de qualidade.
Use templates/kata-sample.md como base. Crie o Kata no idioma padrão e
traduza para todos os idiomas de language.i18n.

Formato de saída:
Lista de arquivos criados com confirmação de que o Kata tem inputs definidos,
passos atômicos e validação final.
```

## Exemplo de Invocação

**Criar Kata com tarefa:**

```
/cry-new-kata "criar ADR"
```

**Output:**

```
Kata criado com sucesso.

Tarefa: Criar ADR (Architecture Decision Record)
Passos: 6 passos definidos
Inputs: 3 (decisão, contexto, alternativas)

Arquivos criados:
1. framework/pt-BR/engineering/architecture/katas/kata-create-adr.md ✓
2. framework/es/engineering/architecture/katas/kata-create-adr.md ✓
3. framework/en/engineering/architecture/katas/kata-create-adr.md ✓
```

## Restrições

- Se a tarefa tem menos de 4 passos, sugere criar um Cry em vez de Kata
- Sempre executa `kata-create-kata` (nunca cria diretamente)
- Sempre cria nos três idiomas obrigatórios

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Invocação rápida (1 comando) | Procedimento completo (6 passos) |
| **Complexidade** | Baixa (tarefa + contexto) | Alta (decomposição, redação, validação) |
| **Configura agente?** | Não | Sim (define comportamento) |
| **Exemplo** | `/cry-new-kata "criar ADR"` | Workflow de 6 passos com checklist |

## Referências

- `kata-create-kata` — Procedimento executado por este Cry
- `codex-katas` — Critérios de qualidade consultados
- `templates/kata-sample.md` — Template base
