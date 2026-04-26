# Codex: Semantic Versioning

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Release versioning and tags in Guardia repositories

## Content

### Principles

1. **MAJOR (X):** incremented when there are changes incompatible with previous versions (breaking changes). Consumers depending on the previous version may need to change.
2. **MINOR (Y):** incremented when new backward-compatible functionality is added. Existing code keeps working.
3. **PATCH (Z):** incremented when backward-compatible bug fixes or adjustments are made. Public behavior does not change in an incompatible way.

### Version Format

```
MAJOR.MINOR.PATCH[-pre-release][+metadata]
```

| Part | Required | Example |
|------|:--------:|---------|
| MAJOR.MINOR.PATCH | Yes | `1.2.3` |
| Pre-release | No | `1.2.3-alpha.1`, `1.0.0-rc.2` |
| Build metadata | No | `1.2.3+build.42` |

The `v` prefix on the tag (e.g. `v1.2.3`) is recommended for tool compatibility and common convention. The project MUST adopt one form (`v` or without `v`) and keep it consistent.

### Relation to Conventional Commits

The commit history in Conventional Commits format allows inferring the type of bump for the next version:

| Situation in commits since last tag | Recommended increment |
|-------------------------------------|------------------------|
| At least one commit with `BREAKING CHANGE:` or type `feat!` / `fix!` | MAJOR |
| At least one `feat` (no breaking) | MINOR |
| Only `fix`, `perf`, `docs`, `chore`, `style`, `refactor`, `test`, `ci`, `build` | PATCH |
| No commits relevant for release | Do not create tag or use pre-release |

When the user does not provide the version in `cry-tag` or `kata-tag`, the agent may suggest the next version based on this table and the latest existing tag.

### When to Increment Each Number

| Component | When to increment | Example |
|-----------|--------------------|---------|
| MAJOR | Public API removed or changed in an incompatible way; behavior change that breaks contracts | Removal of required parameter, return type change |
| MINOR | New backward-compatible functionality | New endpoint, new optional parameter |
| PATCH | Bug fix, documentation update, performance improvement without contract change | Bug fix, typo in message, internal optimization |

After incrementing MAJOR, MINOR and PATCH are reset to 0 (e.g. after `1.2.3`, the next MAJOR is `2.0.0`). After incrementing MINOR, PATCH is reset to 0 (e.g. `1.2.3` → `1.3.0`).

### Pre-release and Metadata

- **Pre-release:** identifiers such as `alpha`, `beta`, `rc` follow the SemVer 2.0 specification. E.g. `v1.2.3-alpha.1`, `v2.0.0-rc.1`. Useful for publishing test versions without changing the stable release number.
- **Build metadata:** suffix `+build.42` or `+20260308` does not change version precedence. Used to distinguish builds of the same version number.

### Applying to Git Tags

| Practice | Description |
|----------|-------------|
| Tag on release commit | Create the tag on the commit that represents that release state (usually the last commit of the release). |
| One tag per version | Each SemVer identifier (e.g. `v1.2.3`) must appear at most once in the repository. |
| Signed tags | Per `lex-signed-commits`, release tags MUST be signed with GPG (`git tag -s`). |
| Annotated tag | Use `git tag -a` (or `-s` which implies annotated) to include message and metadata; enables changelog and stable reference. |

Typical command to create a release tag:

```
git tag -s v1.2.3 -m "Release 1.2.3"
```

To push the tag to the remote:

```
git push origin v1.2.3
```

### Technical Constraints

- The format MUST comply with the [SemVer 2.0.0](https://semver.org/) specification.
- Release tags must not use non-SemVer names (e.g. `latest`, `release-1.2`).
- The project MUST document whether it uses the `v` prefix and keep it consistent.
