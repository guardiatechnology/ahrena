# Primeiros Passos

O Ahrena é um **framework de capacidades AI-first** — uma coleção de Lexis (leis), Codex (guias), Katas (skills) e Warriors (agentes) que transforma qualquer IDE com suporte a AI em um ambiente de engenharia padronizado e auditável.

Instalar o Ahrena em um projeto significa que todos os agentes de AI que atuam nele passam a compartilhar as mesmas regras, o mesmo vocabulário e os mesmos fluxos de trabalho.

---

## Pré-requisitos

| Requisito | Versão mínima |
|---|---|
| Python | 3.9+ |
| make | qualquer versão moderna |
| IDE com suporte a AI | Cursor ou Claude Code |

=== "macOS / Linux"

    ```bash
    python3 --version
    make --version
    ```

=== "Windows"

    ```powershell
    python --version
    # make via chocolatey ou winget
    winget install GnuWin32.Make
    ```

---

## Instalação

### Bootstrap (primeiro uso)

O comando `bootstrap` baixa o instalador diretamente da última release do GitHub e executa a instalação no projeto corrente.

=== "macOS / Linux"

    ```bash
    make bootstrap
    ```

=== "Windows"

    ```powershell
    make bootstrap
    ```

Isso cria a pasta `.ahrena/` na raiz do projeto com o framework instalado e gera os arquivos de configuração para a plataforma detectada (Cursor ou Claude Code).

### Plataforma explícita

Por padrão, o instalador detecta automaticamente qual IDE está presente. Para forçar uma plataforma:

```bash
# Cursor
make bootstrap PLATFORM=cursor

# Claude Code
make bootstrap PLATFORM=claude-code
```

### Idioma

O idioma padrão é `pt-BR`. Para instalar em outro idioma:

```bash
make bootstrap LANGUAGE=en
make bootstrap LANGUAGE=es
```

### Clades seletivos

Para instalar apenas os clades relevantes ao projeto (reduz ruído de regras irrelevantes):

```bash
# Apenas backend e platform
make bootstrap CLADES=engineering/backend,engineering/platform

# Apenas workflow e contributing
make bootstrap CLADES=_foundation/contributing,engineering/workflow
```

---

## Atualização

Após o bootstrap inicial, use `update` para buscar a versão mais recente do framework:

```bash
make update
```

Para atualizar para uma versão específica:

```bash
make update VERSION=v1.2.0
```

---

## Sincronização

Se você já tem o Ahrena instalado e quer apenas regenerar os arquivos de configuração da IDE (sem baixar nada):

```bash
# Regenera .cursor/
make sync-cursor

# Regenera .claude/ e CLAUDE.md
make sync-claude-code
```

Útil após editar manualmente os directives ou após um `git pull` que trouxe mudanças no framework.

---

## Remoção

```bash
# Com confirmação interativa
make uninstall

# Sem confirmação (CI, scripts)
make clean
```

---

## Modo Dev

O modo dev é para quem quer **contribuir com o próprio Ahrena** — testar mudanças locais no framework antes de submeter um PR.

### Por que existe

O `make bootstrap` e o `make install` sempre baixam o framework do GitHub. O `make dev-install` ignora a rede e usa o código local do repositório como fonte — permite iterar sem fazer commit/push.

### Configuração

Clone o repositório do Ahrena e, dentro dele, rode:

```bash
# Instala o framework a partir do código local no projeto corrente
make dev-install
```

Para instalar em outro projeto a partir desta cópia local:

```bash
make install-to TARGET=/caminho/para/o/projeto
```

### Fluxo típico de contribuição

```
1. fork + clone do guardiafinance/ahrena
2. crie a branch: feat/{issue}-{slug}
3. edite os artefatos em framework/
4. make dev-install           ← instala localmente para testar
5. teste nos IDEs configurados
6. make validate              ← valida estrutura e cobertura
7. commit (GPG-signed, Conventional Commits)
8. /cry-new-pr                ← abre o PR seguindo os padrões
```

### Variáveis disponíveis no dev

```bash
make dev-install PLATFORM=cursor LANGUAGE=en CLADES=engineering/backend
make dev-install TARGET=../meu-outro-projeto
```

---

## Referência de comandos

| Comando | O que faz |
|---|---|
| `make bootstrap` | Primeiro install (baixa o instalador do GitHub) |
| `make install` | Reinstala a partir do `.ahrena/install.py` |
| `make dev-install` | Instala a partir do código local (modo dev) |
| `make install-to TARGET=…` | Instala neste repo em outro projeto (offline) |
| `make update` | Atualiza para a versão mais recente |
| `make sync-cursor` | Regenera `.cursor/` sem baixar nada |
| `make sync-claude-code` | Regenera `.claude/` e `CLAUDE.md` |
| `make validate` | Valida estrutura e consistência do framework |
| `make uninstall` | Remove o Ahrena com confirmação |
| `make clean` | Remove os arquivos instalados sem confirmação |

---

## Próximos passos

- [Conceitos fundamentais](ahrena/concepts.md) — entenda Lexis, Codex, Katas, Warriors e Cries
- [Catálogo de Cries](ahrena/cries.md) — todos os comandos disponíveis nos IDEs
- [Catálogo de Katas](ahrena/katas.md) — todas as skills executáveis
- [Contribuindo](https://github.com/guardiafinance/ahrena/blob/main/CONTRIBUTING.md) — como contribuir com o framework
