# Cry: Run Git Tag

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to create or list release tags with semantic versioning

## Invocation

```
/cry-tag [version] [message] [commit]
/cry-tag --list
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `version` | No | SemVer identifier (with or without `v` prefix) | `1.2.3`, `v1.2.3` |
| `message` | No | Tag annotation message | `"Release 1.2.3"` |
| `commit` | No | Commit ID (hash) or commit message (subject) to point the tag at; if omitted, uses HEAD | `abc123f`, `"feat(auth): add OAuth2"` |
| `--list` | — | List existing tags (does not create a tag) | `/cry-tag --list` |

If `--list` is passed, the command only lists tags (e.g. `git tag -l --sort=-v:refname`). Otherwise, it invokes `kata-tag` to create a new tag.

If the version is omitted when creating a tag, the agent suggests the next version based on tag and commit history (consulting `codex-semantic-version`). If `commit` is provided, the agent resolves the ID or message to a valid commit and points the tag at it.

## Usage Examples

```
# Create tag with version and message
/cry-tag v1.2.3 "Release 1.2.3"

# Create tag pointing at a commit by hash
/cry-tag v1.2.3 "Release 1.2.3" abc123f

# Create tag pointing at a commit by message (subject)
/cry-tag v1.2.3 "Release 1.2.3" "feat(auth): add OAuth2"

# Create tag with version only (default message, HEAD)
/cry-tag v1.2.3

# Automatic suggestion — agent determines next version and confirms
/cry-tag

# List tags
/cry-tag --list
```

## Behavior

**When creating a tag (without `--list`):**

1. Invokes `kata-tag` passing version, message, and commit (if provided)
2. If the version is omitted, the agent analyzes history and suggests the next version per `codex-semantic-version`
3. Validates against `lex-semantic-version` and `lex-signed-commits`
4. Creates the annotated, signed tag and reports how to publish (`git push origin <version>`)

**When listing (`--list`):**

1. Runs `git tag -l` (optionally with version sorting, e.g. `--sort=-v:refname`)
2. Displays the tag list; does not run the creation Kata

## Associated Kata

`kata-tag` — Full procedure for applying semantic versioning with git tags

## References

- `kata-tag` — Procedure executed by this Cry when creating a tag (the Kata consults SemVer and signing Lexis and Codex; see Kata documentation)
