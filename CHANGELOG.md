# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
per `lex-semantic-version`.

## [0.15.1] - 2026-05-25

3 PRs merged since v0.15.0 (#254, #257, #260) plus one maintenance commit.

### Chore

- **framework:** rename `guardiafinance` → `guardiatechnology` across canonical sources (pt-BR, es, en), READMEs, mkdocs config, public docs, GitHub issue templates, `.directives.sample`, and templates; regenerate `.claude/` and `.cursor/` derivatives (#260, f4d61a7)
- **discovery:** capture Rust framework support PRs as 2 Insights (status approved) and 2 Ideas (status promoted) under topic `rust-framework-support` (#257, 97e42a8)
- **skills:** drop legacy `hello-skill` experiment (#254, 946e0d8)
- **build:** add `.DS_Store` to `.gitignore`; make `scripts/install.py` executable (9166d7c)

[0.15.1]: https://github.com/guardiatechnology/ahrena/compare/v0.15.0...v0.15.1

## [0.15.0] - 2026-05-21

13 PRs merged since v0.14.1 (#219, #220, #223, #225, #228, #230, #232, #235, #239, #242, #246, #249, #251).

### Features

- **install:** bundle RTK PreToolUse hook into Claude Code projects (#219, 181be6a)
- **install:** gate binary install on `rtk.auto_install_binary` directive (#219, 600f7d0)
- **install:** write `.ahrena/.version` manifest at install time (#225, ab02a21)
- **framework:** add `warrior-claudiomiro` (Anthropic Assembly Coordinator) (#220, 6e6b575)
- **framework:** codify multi-reviewer sweep in `lex-pr-quality` and `warrior-argos` (#223, 70d43b9)
- **framework:** add `kata-ahrena-version` with `.version` → `git describe` fallback (#225, 30e0968)
- **framework:** add `cry-ahrena-version` shortcut (#225, fb5df9b)
- **framework:** codify `warrior-argos` identity self-verify + HARD-GATE (#228, e93b767)

### Fixes

- **scripts:** resolve `auth.sh` `.env.local` + token cache from main repo when invoked from worktree (#249, f91d08e)
- **framework:** address Gemini i18n findings on `warrior-argos` worktree-aware note (#249, 14dd60e)
- **framework/argos:** pt-BR translation typo `minta` → `cunha` (#246, 0700bf2)
- **framework/argos:** harden identity self-verify against null body + escape regex metacharacters (#246, 4768e48)
- **framework/argos:** POSIX-portable test operator + Markdown anchor fixes (#246, 52996e5)
- **framework/codex:** comprehensive `lex-entity-naming` cleanup in codex examples (#242, 3a75146)
- **framework/codex:** translate "per" and "Module" in pt-BR/es CloudEvents docs (#242, 1c69d4e)
- **framework/es:** replace false cognate `decomisar` with `retirar` in `lex-entity-naming` (#235, 531ccb0)
- **framework:** wrap HARD-GATE in fenced code block in `lex-agent-design-doc` (#239, 345cf63)
- **framework:** strengthen rule 8 (plural kebab-case URL) with derivation examples (#232, 8df0314)
- **framework:** sweep `event.guardia.platform` → `event.guardia.financial` (#232, 2780f9b)
- **framework:** use canonical Guardia contexts (`financial`/`records`) (#232, 602cdcf)
- **framework:** URL plural+version and coherent CloudEvents example (#232, 04d7753)
- **framework:** CloudEvents `id` carries the entity prefix (#232, 325f594)
- **framework:** remove `entity_id_prefix` redundancy and correct CloudEvents shape (#232, cd2c4a5)
- **framework:** align `engineering/platform` Lexis/Codex with Guardia spec (#232, 26aab30)
- **framework:** address Argos + Gemini review on multi-reviewer sweep PR (#223, ad55dc9)
- **framework:** address Gemini review — anglicisms in pt-BR/es warrior-claudiomiro (#220, 583eb4f)

### Refactors

- **framework/argos:** harden identity HARD-GATE with anti-pretext clause (#246, a49d06e)
- **framework:** STRICT fence retrofit + warrior placement in `lex-hard-gate-pattern` (#239, 9a047cb)

### Docs

- **framework:** apply `lex-entity-naming` Rule 7 to CloudEvents subject example (#251, e22c6dc)
- **framework:** normalize identifier UUIDs in CloudEvents example (#251, db50ddc)
- **framework:** translate `lex-system-prompt` and `lex-agent-design-doc` to pt-BR/es (#230, b1dc7cf)
- **readme:** document RTK bundling for `--platform claude-code` (#219, 0345629)
- **directives:** document `rtk.*` keys in `lex-directives` (3 langs) (#219, db8669a)

### Chore

- **sync:** regenerate `.claude/` and `.cursor/` for review fixes (#242, 7376ee6)
- **sync:** regenerate `.claude/` and `.cursor/` for translated lexis (#230, 0906cfd)
- **framework:** regenerate `.cursor/` and `.claude/` for new `ahrena-version` artifacts (#225, 4cc3a93)
- **framework:** regenerate `.cursor/` `lex-directives` derivative — rtk keys (#223, 756a44c)
- **install:** drop redundant local imports in `_install_rtk_binary` / helpers (#219, 72115f7)
- **self:** sync `.claude/` + `.rtk/` to RTK bundle on this Ahrena checkout (#219, ec91313)

[0.15.0]: https://github.com/guardiatechnology/ahrena/compare/v0.14.1...v0.15.0
