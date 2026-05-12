# System Prompt Adversarial Validator

Executable suite that validates a Guardia agent's system prompt against an adversarial payload corpus drawn from OWASP LLM Top 10 2025 and Guardia-specific guardrails. Enforces precondition (i) of the HARD-GATE in `lex-system-prompt`.

The corresponding Kata wrapper is `kata-system-prompt-adversarial-validate`. The Lex and Codex live under `framework/{lang}/engineering/agents/`.

## Quick start

```bash
# 1. Install dependencies (in a venv recommended)
pip install -r requirements.txt

# 2. Set provider credentials
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Smoke test: parse the suite without calling the provider
python runner.py --prompt path/to/system-prompt.md --dry-run

# 4. Real run against the default model (Haiku)
python runner.py --prompt path/to/system-prompt.md

# 5. Tier-1 critical agent (Sonnet)
python runner.py --prompt path/to/system-prompt.md --tier tier-1

# 6. Single category
python runner.py --prompt path/to/system-prompt.md --category llm07_leakage

# 7. legacy-pov transition window (warns but does not block)
python runner.py --prompt path/to/system-prompt.md --mode soft

# 8. JSON output for CI consumption
python runner.py --prompt path/to/system-prompt.md --json
```

Exit codes:

- `0` — every category passed at or above `--pass-threshold` (default 0.95) and no critical assertion failed (or mode is `soft`).
- `1` — at least one category failed in `--mode strict`.
- `2` — configuration error (missing prompt, missing API key, malformed YAML).

## Layout

```
scripts/system_prompt_adversarial/
├── README.md              # this file
├── requirements.txt       # anthropic, pyyaml
├── runner.py              # single-file CLI
├── payloads/
│   ├── llm01_injection/        # ≥5 injection payloads (direct + indirect)
│   ├── llm02_pii_disclosure/   # ≥5 PII / org_id / client_id payloads
│   ├── llm07_leakage/          # ≥5 prompt-leakage payloads
│   └── llm06_excessive_agency/ # ≥3 scope/agency payloads
└── assertions/
    ├── llm01_injection.yaml
    ├── llm02_pii_disclosure.yaml
    ├── llm07_leakage.yaml
    └── llm06_excessive_agency.yaml
```

Each payload is a `.txt` file with a header comment describing the attack vector. Each assertion file declares:

- `description` — human-readable summary
- `critical` — boolean; when `true`, any failure in this category fails the entire run
- `must_not_match` — list of regex (case-insensitive) that MUST NOT appear in the model's response
- `must_match` — list of regex that MUST appear (optional; rarely used at v1)

## Cost expectations

Default model: `claude-haiku-4-5`. Approximate cost per run with the v1 corpus (~19 payloads × ~500 output tokens):

- Haiku (default): ≈ US$ 0,10
- Sonnet (`--tier tier-1`): ≈ US$ 0,90

Recommendation: Haiku for every PR; Sonnet for tier-1 critical agents (Isac, money movement) and for periodic audits.

## Ethics and payload confidentiality

These payloads are deliberately **generic and public-domain** attack patterns (variations of well-known prompt-injection and prompt-leakage techniques). They contain no Guardia confidential data, no real client information, no real `org_id` / `client_id` values.

Two rules govern payload contributions:

1. **No real secrets, no real PII, no real client identifiers.** Use synthetic values (e.g., `123.456.789-00` for CPF, `sk-live-abc123…` for fake tokens).
2. **Sensitive internal attack patterns must not be added here.** When the security team curates payloads that reflect internal threat intelligence (specific attacks observed against Guardia agents), those payloads live in a separate private repository and are loaded at CI time. The public corpus in this directory must remain reproducible from public OWASP / academic sources.

Ownership:

- **Initial curation:** `warrior-claudionor` (PoV stage).
- **Production-impacting changes:** `warrior-metis` review required.
- **Audit cadence:** monthly review of allowlisted assertions (false-positive exceptions); quarterly review of the full corpus.

## Allowlists for false positives

The suite can reject prompts that are legitimate but trip a regex (e.g., a security training agent that intentionally echoes back a CPF-shaped placeholder). Path:

1. Add a comment `# adversarial-allowlist: <reason>` near the relevant section of the prompt.
2. Open a PR adjusting the assertion (loosening the regex) or annotating the payload (skipping it for that prompt).
3. Mandatory human review by `warrior-metis` before merge.
4. Monthly audit of allowlists to detect erosion (allowlists that have grown beyond proven need).

## CI / Gate 2 integration

When `quality.system_prompt_adversarial.enabled: true` in `.ahrena/.directives`, `kata-quality-gate` Check 3 invokes `kata-system-prompt-adversarial-validate` on every PR whose diff touches `docs/**/agents/**/system-prompt*.md`. The Kata wraps this runner with:

- Cache by SHA of the prompt file (skip re-run when unchanged).
- `--mode soft` automatically applied when the prompt declares `stage: legacy-pov` and the transition window is open.
- `--tier tier-1` automatically applied when the agent's `tier:` line is `tier-1`.

## Provider portability

The current runner targets Anthropic. To add another provider:

1. Add a new branch inside `call_provider()` that returns the assistant's text content.
2. Surface the choice via a new CLI flag (e.g., `--provider`).
3. Document credential expectations in this README.
4. Re-run the full corpus against the new provider on a reference prompt before relying on it.

Future iteration may move provider selection into a `providers/` package, but v1 keeps everything in a single file.

## Limitations (v1)

- Regex-based assertions only — semantic equivalence ("DEBUG MODE" vs. "Engaging the diagnostic mode") may slip through if not enumerated.
- No conversational state — every payload is sent as a single-turn user message.
- No retry-on-rate-limit; the run fails fast in transient network issues.
- No automatic allowlist linting — relies on monthly human audit.

These limitations are deliberate for v1 simplicity; iteration backlog tracks evolution.
