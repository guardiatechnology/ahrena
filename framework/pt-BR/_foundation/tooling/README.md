# Tooling — Automação e Ferramentas

> Documentação das ferramentas de automação do repositório Ahrena.

## Visão Geral

O subclade `tooling` contém artefatos que automatizam tarefas de desenvolvimento e manutenção do framework. São ferramentas específicas do repositório Ahrena (não genéricas do framework) que facilitam instalação, build e operações do dia a dia.

## Inventário de Artefatos

### Cries (atalhos)

| Artefato | Descrição |
|----------|-----------|
| `cry-make` | Executa targets do Makefile do repositório |

## Como Usar

### Executar o Makefile

```
/cry-make <target> [variáveis]
```

Exemplos:

```
/cry-make dev-install PLATFORM=cursor    # Instala usando fontes locais
/cry-make bootstrap PLATFORM=cursor      # Primeira instalação
/cry-make clean                          # Limpa artefatos temporários
```

### Targets Disponíveis

| Target | Descrição |
|--------|-----------|
| `dev-install` | Instala usando fontes locais (`framework/`) |
| `bootstrap` | Primeira instalação (baixa do GitHub) |
| `install` | Reinstala a partir de `.ahrena/install.py` |
| `update` | Atualiza para a última versão |
| `uninstall` | Remove a instalação do framework |
| `clean` | Remove artefatos temporários |

## Referências

- `Makefile` — Arquivo de automação na raiz do repositório
- `scripts/install.py` — Script de instalação do framework
