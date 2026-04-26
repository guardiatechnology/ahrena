Automatic commit — agent analyzes the diff and suggests. Shortcut for creating standardized commits

# Cry: Create Commit

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut for creating standardized commits

## Invocation

```
/cry-commit [type] [scope] [description]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `type` | No | Conventional Commits type | `feat`, `fix`, `docs` |
| `scope` | No | Module or domain | `auth`, `api`, `payments` |
| `description` | No | Subject text in English | `"implement OAuth2"` |

If parameters are omitted, the agent analyzes `git diff --staged` and suggests automatically.

## Usage Examples

```
# Commit with all parameters
/cry-commit feat auth "implement OAuth2 authentication"

# Commit with type and description (no scope)
/cry-commit fix "resolve null pointer in transaction"

# Automatic commit — agent analyzes the diff and suggests
/cry-commit
```

## Behavior

1. Invokes `kata-commit` passing the provided parameters
2. If parameters are omitted, the agent:
   - Runs `git diff --staged`
   - Infers type, scope, and description
   - Presents the suggestion for confirmation
3. Validates against all 4 commit Lexis
4. Executes the signed commit

## Associated Kata

`kata-commit` — Complete commit creation procedure
