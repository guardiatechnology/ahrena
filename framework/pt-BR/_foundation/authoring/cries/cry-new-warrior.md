# Cry: Criar Novo Warrior

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Criação de Warriors (agentes especializados)

## Descrição

Comando rápido para criar um novo Warrior no Ahrena. Invoca o `kata-create-warrior`, que consulta `codex-warriors` e o template oficial para produzir um agente especializado completo nos três idiomas obrigatórios.

## Uso

```
/cry-new-warrior <papel> [domínio] [--name nome] [--clade clade/subclade]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `papel` | Sim | Função que o Warrior desempenha | `"Arquiteto de Software"` |
| `domínio` | Não | Área de atuação. Se omitido, o agente infere do papel | `"decisões arquiteturais"` |
| `--name` | Não | Nome próprio do Warrior. Se omitido, o agente sugere um nome temático | `--name Athena` |
| `--clade` | Não | Clade/subclade na taxonomia. Se omitido, o agente infere do domínio | `--clade engineering/architecture` |

## O que o Comando Faz

1. Lê `.ahrena/.directives` para obter idiomas e convenções
2. Consulta `codex-warriors` para critérios de qualidade
3. Lê `templates/warrior-sample.md` como base estrutural
4. Executa `kata-create-warrior` com os parâmetros fornecidos
5. Cria o Warrior no idioma padrão e traduz para os demais idiomas
6. Reporta os arquivos criados

## Prompt Template

```
Contexto:
- Papel: {{papel}}
- Domínio: {{domínio}} (ou inferir do papel)
- Nome: {{name}} (ou sugerir nome temático)
- Clade/Subclade: {{clade}} (ou inferir do domínio)

Tarefa:
Execute o kata-create-warrior. Consulte .ahrena/.directives para obter os
idiomas obrigatórios. Consulte codex-warriors para critérios de qualidade.
Use templates/warrior-sample.md como base. Crie o Warrior no idioma padrão e
traduza para todos os idiomas de language.i18n.

Formato de saída:
Lista de arquivos criados com confirmação de que o Warrior tem identidade
completa, responsabilidades delimitadas e cadeia de consulta definida.
```

## Exemplo de Invocação

**Criar Warrior com papel:**

```
/cry-new-warrior "Arquiteto de Software"
```

**Output:**

```
Warrior criado com sucesso.

Identidade:
- Nome: Athena
- Papel: Arquiteto de Software
- Domínio: Decisões arquiteturais e qualidade estrutural
- Persona: Analítica, criteriosa, focada em trade-offs

Arquivos criados:
1. framework/pt-BR/engineering/architecture/warriors/warrior-athena.md ✓
2. framework/es/engineering/architecture/warriors/warrior-athena.md ✓
3. framework/en/engineering/architecture/warriors/warrior-athena.md ✓
```

**Com nome e clade explícitos:**

```
/cry-new-warrior "Revisor de Código" "qualidade de código" --name Linus --clade engineering/quality
```

## Restrições

- Não cria Warriors genéricos sem escopo delimitado
- Sempre executa `kata-create-warrior` (nunca cria diretamente)
- Sempre cria nos três idiomas obrigatórios

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Invocação rápida (1 comando) | Procedimento completo (7 passos) |
| **Complexidade** | Baixa (papel + domínio) | Alta (identidade, responsabilidades, consulta) |
| **Configura agente?** | Não | Sim (define comportamento) |
| **Exemplo** | `/cry-new-warrior "Arquiteto"` | Workflow de 7 passos com checklist |

## Referências

- `kata-create-warrior` — Procedimento executado por este Cry
- `codex-warriors` — Critérios de qualidade consultados
- `templates/warrior-sample.md` — Template base
