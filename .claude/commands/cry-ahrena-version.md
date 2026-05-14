Show Ahrena Framework Version. On-demand lookup of the installed Ahrena framework version

# Cry: Show Ahrena Framework Version

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** On-demand lookup of the installed Ahrena framework version

## Usage

```
/cry-ahrena-version
```

## Parameters

None. The Cry takes no arguments.

## What the Command Does

1. Invokes `kata-ahrena-version` against the current working directory
2. Prints the resolved version string on a single line
3. On failure (no `.ahrena/.version` and no readable git tag), prints the structured error from the kata and exits with a non-zero status

## Prompt Template

```
Context:
- Working directory: current

Task:
Run kata-ahrena-version. Emit only the single-line version string the kata
returns. Do not add prefixes, suffixes, decorations, or explanations. If the
kata fails, emit the kata's error message verbatim.

Output format:
Single-line plain text (e.g. `0.13.1`, `0.13.1-3-gabc1234`, `main`) on stdout,
or the kata's structured error message on stderr.
```

## Invocation Example

**Consumer project after install:**

```
$ /cry-ahrena-version
0.13.1
```

**Framework repository before install (dev mode, HEAD past last tag):**

```
$ /cry-ahrena-version
0.13.1-3-gabc1234
```

**Project installed from a branch:**

```
$ /cry-ahrena-version
main
```

## Restrictions

- The Cry MUST NOT add any output beyond what the kata returns — no banner, no version label, no metadata
- The Cry MUST NOT consult the network. The kata it invokes is local-only by design
- The Cry MUST NOT modify any file. It is a read-only lookup
