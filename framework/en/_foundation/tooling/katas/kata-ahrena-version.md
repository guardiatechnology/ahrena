# Kata: Resolve Ahrena Framework Version

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Resolving the installed Ahrena framework version on demand

## Objective

Resolve the version of the Ahrena framework currently in use on a deterministic, single-line SemVer string. The resolution chain falls back from a canonical install-time manifest (`.ahrena/.version` in the consumer project) to a `git describe` reading on the framework repository itself, so the kata works in both **consumer mode** (the typical case after `make install`) and **dev mode** (an agent or human running directly from a clone of the framework repo).

## When to Use

- When a user invokes `/cry-ahrena-version` and asks "which version of Ahrena is here?"
- When a warrior needs to record the framework version in an audit artifact (PR body, issue, release note)
- When troubleshooting compatibility issues and the framework version is not visible from the working tree

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| working directory | Yes | Implicit — the resolution chain reads files relative to the current directory |

The kata takes no parameters; the working directory is the only input.

## Workflow

```
Progress:
- [ ] 1. Read .ahrena/.version (consumer mode)
- [ ] 2. Fall back to git describe (dev mode)
- [ ] 3. Format and emit the version string
- [ ] 4. Final validation
```

### Step 1: Read `.ahrena/.version`

1. Look for `.ahrena/.version` relative to the current working directory
2. If the file exists: read it, strip whitespace and any trailing newline, and use the result as the version string
3. If the file is empty after stripping, treat it as missing and proceed to Step 2
4. If the file exists and contains a non-empty string: skip directly to Step 3

### Step 2: Fall back to `git describe`

1. Only reached when `.ahrena/.version` is absent or empty
2. Run `git describe --tags --abbrev=0` to read the most recent tag
3. If a tag is returned: strip a leading `v` if present and use the result as the version string. This is the **dev mode** path — running the kata inside the framework repository before any install has happened
4. Optional refinement: `git describe --tags` (without `--abbrev=0`) returns a richer string like `0.13.1-3-gabc1234` when HEAD is past the last tag. Either form is acceptable; the canonical fallback is `--abbrev=0` for stability, with the longer form available when the caller wants to know the exact distance from the tag
5. If `git` is unavailable, the directory is not a git repository, or no tags exist: proceed to Step 4 with an explicit error

### Step 3: Format and emit

1. The output is a single line containing only the SemVer string (no `v` prefix, no surrounding quotes, no metadata)
2. In dev mode the string MAY include a `-N-gSHORT` suffix per `git describe` semantics — that is correct (it indicates a development build N commits past the last tag); the kata does not strip the suffix
3. Print the string and return

### Step 4: Final validation

Before delivering the output, verify:

- [ ] The output is a single non-empty line
- [ ] The output does not begin with `v` (the prefix is stripped)
- [ ] When neither `.ahrena/.version` nor `git describe` could resolve a value: the kata MUST emit a structured error message — `framework version unknown; run \`make update\` in this project, or create a SemVer tag in the framework repo` — and exit with a non-zero status code

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| version string | Single-line plain text (e.g. `0.13.1` or `0.13.1-3-gabc1234`) | stdout |
| error message | Single-line plain text on stderr | stderr (non-zero exit) |

## Execution Example

### Consumer mode (typical)

```
$ cat .ahrena/.version
0.13.1

$ <kata-ahrena-version>
0.13.1
```

### Dev mode (framework repo, HEAD on tag)

```
$ git describe --tags --abbrev=0
v0.13.1

$ <kata-ahrena-version>
0.13.1
```

### Dev mode (framework repo, HEAD past last tag)

```
$ git describe --tags
v0.13.1-3-gabc1234

$ <kata-ahrena-version>
0.13.1-3-gabc1234
```

### Branch install (consumer ran `make install VERSION=main`)

```
$ cat .ahrena/.version
main

$ <kata-ahrena-version>
main
```

The output is the literal `main` (or the literal branch name) — the file is the source of truth and the kata does not reshape non-SemVer values.

### Failure path (no `.ahrena/.version`, no git tags)

```
$ <kata-ahrena-version>
framework version unknown; run `make update` in this project, or create a SemVer tag in the framework repo
$ echo $?
1
```

## Restrictions

- The kata MUST NOT consult the network. The two sources of truth are local (`.ahrena/.version` and `git describe`); no GitHub Releases query is allowed
- The kata MUST NOT reshape the value read from `.ahrena/.version`. If the file contains `main` or a branch name, that exact value is emitted; synthesizing `0.0.0-main+<sha>` or any other surrogate SemVer is FORBIDDEN
- The kata MUST NOT print extra context (banner, version label, decoration) — the output is the bare version string, intended to be consumed by other commands and warriors

## References

- `cry-ahrena-version` — entry point command that invokes this kata
- `lex-semantic-version` — SemVer rules respected by the manifest
