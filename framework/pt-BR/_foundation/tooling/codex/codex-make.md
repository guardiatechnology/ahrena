# Codex: Makefile do repositório Ahrena

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Variáveis, targets e equivalência sem Make do Makefile na raiz do repositório Ahrena

## Visão Geral

Este Codex é a referência para executar targets do **Makefile** na raiz do repositório Ahrena. Define as variáveis disponíveis, os targets, exemplos de uso e a **equivalência sem Make** (comandos PowerShell/Python) para quando `make` não está disponível (ex.: Windows). É consultado pelos katas especializados de make (install, update, dev-install, bootstrap, sync-cursor, uninstall, clean) e pelo agente ao atender `/cry-make`.

## Contexto

- **Domínio:** Instalação, atualização, bootstrap e manutenção do framework Ahrena via Makefile ou scripts equivalentes.
- **Público-alvo:** Agentes de IA que executam `/cry-make` ou o Kata associado; desenvolvedores que rodam `make` ou os scripts em PowerShell.
- **Atualização:** Quando novos targets ou variáveis forem adicionados ao Makefile ou quando a equivalência sem Make mudar.

## Conteúdo

### Variáveis

| Variável | Descrição |
|----------|-----------|
| `PLATFORM` | Plataforma alvo (ex.: `cursor`) |
| `TARGET` | Diretório do projeto (default: `.`) |
| `VERSION` | Tag ou branch para instalação/update remoto (default: `main`) |
| `REPO` | URL do repositório GitHub |
| `SOURCE` | Caminho para clone local do Ahrena (instalar/atualizar a partir de local) |
| `LOCAL` | Se definido (ex.: `LOCAL=1`), instalar/atualizar a partir do diretório atual como fonte |
| `LANGUAGE` | Sobrescrever idioma padrão no `.directives` |
| `DIRECTIVES` | Caminho ou URL para arquivo `.directives` customizado |
| `CLADES` | Clades separados por vírgula (default: todos) |

**Padrão:** instalação e atualização são sempre do **remoto** (GitHub). Para usar fonte local, use `SOURCE=/caminho/ahrena` ou `LOCAL=1`.

### Targets disponíveis

| Target | Descrição |
|--------|-----------|
| `bootstrap` | Primeira instalação (baixa o instalador do GitHub) |
| `install` | Instala o framework (padrão: remoto). Com `LOCAL=1` ou `SOURCE=...`: local |
| `dev-install` | Instala a partir do diretório atual (executar na raiz do repo Ahrena) |
| `update` | Atualiza a instalação (padrão: remoto). Após dev-install use `update LOCAL=1` ou `SOURCE=...` para trazer o mais recente do ambiente de desenvolvimento |
| `sync-cursor` | Regenera `.cursor/` a partir de `.ahrena/framework/` e `.ahrena/artifacts/` (sem download) |
| `uninstall` | Remove a instalação do framework |
| `clean` | Remove arquivos instalados pelo Ahrena (sem confirmação) |

### Exemplos de uso

```powershell
# Instalação remota (padrão)
make install PLATFORM=cursor
make install PLATFORM=cursor VERSION=1.0.0

# Instalação a partir de clone local
make install PLATFORM=cursor SOURCE=../ahrena
make install PLATFORM=cursor LOCAL=1

# Bootstrap do ambiente
make bootstrap

# Atualização remota (padrão)
make update

# Atualização a partir de local (ex.: após dev-install)
make update LOCAL=1
make update SOURCE=../ahrena

# Limpar artefatos
make clean
```

### Instalação guiada por preferências

Na primeira instalação, `scripts/install.py` materializa o `.directives` a partir de uma seleção de preferências. Quando o stdin é TTY e `--non-interactive` não é passado, o instalador pergunta ao usuário quais MCPs, hooks e features opcionais ativar (pré-marcado = perfil Full). Para execuções não interativas (CI, scripts), escolha um perfil e ajuste:

```powershell
# Conhecer o catálogo (MCPs, hooks, features opcionais)
python scripts/install.py --list-catalog

# Default Full (sem flag, sem prompt): todos os MCPs, todos os hooks, todas as features
python scripts/install.py --self --target . --platform claude-code --non-interactive

# Perfil minimal (apenas MCP ahrena + hook rtk)
python scripts/install.py --self --target . --platform claude-code --non-interactive --profile=minimal

# Full menos MCPs específicos
python scripts/install.py --self --target . --platform claude-code --non-interactive --profile=full --without-mcp=notion,figma
```

Ordem de resolução: `--with-*` / `--without-*` explícitos sobrescrevem `--profile`, que sobrescreve o default Full. O MCP `ahrena` é sempre mantido (servidor do próprio framework). Arquivos `.directives` existentes são preservados em reinstalações.

### Equivalência sem Make (Windows)

Quando `make` não está disponível (ex.: PowerShell no Windows), use os scripts diretamente:

**Instalação remota:**
```powershell
python .ahrena/install.py --target . --version main --repo https://github.com/guardiatechnology/ahrena --platform cursor
```

**Instalação local (no repo Ahrena):**
```powershell
python scripts/install.py --local --target . --platform cursor
```

**Instalação local (path):**
```powershell
python .ahrena/install.py --target . --source C:\caminho\para\ahrena --platform cursor
```

**Atualização remota (padrão):**
```powershell
python .ahrena/update.py --target .
```

**Atualização local:**
```powershell
python .ahrena/update.py --target . --local
# ou
python .ahrena/update.py --target . --source C:\caminho\para\ahrena
```

**Bootstrap (primeira instalação):** baixar o instalador do GitHub e executar; em PowerShell, por exemplo:
```powershell
Invoke-WebRequest https://github.com/guardiatechnology/ahrena/releases/latest/download/install.py -OutFile install.py; python install.py --platform cursor; Remove-Item install.py
```

**Sync-cursor (regenerar .cursor/):**
```powershell
python .ahrena/update.py --target . --sync-cursor
```

**Uninstall (remover instalação):**
```powershell
python .ahrena/uninstall.py --target .
```

**Clean (remover arquivos sem confirmação):**
```powershell
python .ahrena/install.py --target . --clean
```

## Referências

- `Makefile` — Arquivo de automação na raiz do repositório
- Katas de make (`kata-make-install-framework`, `kata-make-update-framework`, etc.) — Procedimentos por target (consultam este Codex)
- `lex-terminal-type` — Tipo de terminal definido em `.ahrena/.directives`
- [GNU Make Manual](https://www.gnu.org/software/make/manual/)
