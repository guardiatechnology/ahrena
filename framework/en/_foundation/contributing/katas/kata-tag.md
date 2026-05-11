# Kata: Apply Semantic Versioning with Git Tag

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Creating release tags compliant with `lex-semantic-version`, `lex-signed-commits`, and `lex-annotated-tags`

## Objective

This Kata defines the standardized procedure for applying semantic versioning in the project using git tags: determine the next version (or use the one provided), validate against the Lexis, and create an **annotated, signed tag** (`git tag -a -s`). Lightweight tags (`git tag NAME` without `-a`/`-s`) are FORBIDDEN by `lex-annotated-tags` — only annotated tags can carry a GPG signature.

## When to Use

- When a release tag needs to be created following Semantic Versioning 2.0
- When the user asks for help marking a version in the repository
- When invoked by `cry-tag` to create a tag (not to list)

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Version | No | SemVer identifier (e.g. `1.2.3` or `v1.2.3`). If omitted, the agent suggests based on tag and commit history |
| Message | No | Tag annotation message. If omitted, use default (e.g. "Release X.Y.Z") |
| Commit | No | Commit ID (hash) or commit message (subject) to point the tag at. If omitted, use HEAD |

## Workflow

```
Progress:
- [ ] 1. Check repository state
- [ ] 2. Determine next version
- [ ] 3. Validate format against lex-semantic-version
- [ ] 4. Create annotated and signed tag
- [ ] 5. Final verification
```

### Step 1: Check Repository State and Resolve Target Commit

1. Run `git status` to confirm there are no uncommitted changes that should be part of the release (or that the user is aware)
2. Run `git tag -l` (or `git tag -l --sort=-v:refname`) to list existing tags and get the latest version
3. **Resolve the commit where the tag will be created:**
   - If the user provided **commit** (ID or message): resolve to a valid hash.
     - If it is a hash (or abbreviation): `git rev-parse <ref>` to get the commit.
     - If it is a message (subject): find the commit whose subject matches, e.g. `git log -1 --all --format=%H --grep="<message>"` or search by subject; if multiple matches, use the most recent or ask the user to confirm.
   - If **commit** was omitted: use HEAD (`git rev-parse HEAD`).
4. Optional: run `git log <last-tag>..<target-commit> --oneline` to see commits since the last tag (useful for suggesting version)

### Step 2: Determine Next Version

1. Consult `codex-semantic-version` for increment rules
2. If the user provided the version, use it (normalize to the project's adopted format, e.g. with or without `v`)
3. If the version was omitted:
   - Get the latest tag in SemVer format
   - Analyze commits since that tag (e.g. `git log <last-tag>..HEAD --pretty=format:'%s'`)
   - Apply the codex table: BREAKING CHANGE / feat! / fix! → MAJOR; feat → MINOR; fix/perf/etc. → PATCH
   - If there is no previous tag, suggest `v1.0.0` (or `1.0.0`) as the first version
4. Ensure the identifier is in MAJOR.MINOR.PATCH format (with or without `v` prefix)

### Step 3: Validate Against lex-semantic-version

Before creating the tag, verify:

- [ ] The identifier follows Semantic Versioning 2.0 (MAJOR.MINOR.PATCH)
- [ ] It is not an invalid format (e.g. `release-1.2`, `1.2`, `latest`)
- [ ] Pre-release or metadata (if used) follow the SemVer 2.0 specification
- [ ] The tag does not already exist in the repository (`git tag -l '<version>'` empty)

If any check fails, fix or guide the user before proceeding.

### Step 4: Create Annotated and Signed Tag

1. Verify GPG is configured for tag signing (`lex-signed-commits`): `git config --get user.signingkey`
2. If not configured, alert the user and guide configuration; do not create a tag without a signature
3. Set the tag message: use the user-provided message or default (e.g. "Release 1.2.3")
4. Use the **target commit** resolved in Step 1 (HEAD or the commit provided by the user).
5. Run:
   ```
   git tag -s <version> <target-commit> -m "<message>"
   ```
   Example (tag at HEAD): `git tag -s v1.2.3 -m "Release 1.2.3"` (equivalent to `git tag -s v1.2.3 HEAD -m "Release 1.2.3"`).
   Example (tag at specific commit): `git tag -s v1.2.3 abc123f -m "Release 1.2.3"`

### Step 5: Final Verification

- [ ] The tag exists: `git tag -l '<version>'` returns the version
- [ ] The tag is signed: `git tag -v <version>` (or `git show <version>`) shows GPG verification
- [ ] The format is correct per `lex-semantic-version`
- [ ] Inform the user that to publish the tag they must run: `git push origin <version>`

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Tag created | Git tag (annotated and signed) | Local repository |
| Push instruction | Text | E.g. "To publish: git push origin v1.2.3" |

## Constraints

- Never create a release tag without compliance to `lex-semantic-version` (SemVer 2.0 format)
- Never create a release tag without a GPG signature; follow `lex-signed-commits`
- **Never use `git tag NAME` (lightweight)** — `lex-annotated-tags` forbids pushing lightweight tags; only `git tag -a -s` produces a valid tag
- If the user only asks to list tags (e.g. via `cry-tag --list`), do not run this creation Kata; only list with `git tag -l` (and optionally `-n` or sorting)
- Always reference `codex-semantic-version` and `lex-semantic-version` when suggesting or validating version

## Examples

### Correct

```bash
# Annotated and signed tag
git tag -s v1.2.3 -m "Release 1.2.3"
git tag -v v1.2.3   # verifies signature
git push origin v1.2.3
```

### Incorrect

```bash
# ❌ Lightweight tag — violates lex-annotated-tags
git tag v1.2.3
# (no -a/-s; no message; no signature)

# ❌ Annotated but unsigned tag — violates lex-signed-commits + lex-annotated-tags
git tag -a v1.2.3 -m "Release"
# (annotated but not signed)
```

## References

- `lex-semantic-version` — Mandatory SemVer format for releases
- `lex-signed-commits` — Mandatory GPG signature for release tags
- `lex-annotated-tags` — Tags pushed to a remote MUST be annotated + signed
- `codex-semantic-version` — Reference manual for SemVer and git tags
- `codex-annotated-tags` — Operational manual for annotated tags (GPG config, commands, verification, failure modes)
- `cry-tag` — Shortcut that invokes this Kata to create a tag (and list tags)
- `kata-release-publish` — Kata that invokes this one via `warrior-janus`
