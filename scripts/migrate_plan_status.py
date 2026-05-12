#!/usr/bin/env python3
"""
migrate_plan_status.py — one-shot migration from the legacy plan status enum to
the unified enum introduced by plan-043 / ADR-001.

Mapping (per lex-agent-planning new enum):

  legacy            → new
  -----------------   -----------------
  pending           → todo
  in-progress       → development
  archived          → done         (archived was semantically "done + filed";
                                    the new model keeps `done` and treats
                                    `archived/` as a filesystem convention)
  done              → done         (unchanged)
  abandoned         → abandoned    (unchanged; terminal alternative)

Scope: every `*.md` under `.claude/plans/` (or the path defined in
paths.plans in .ahrena/.directives). Each migrated file gets a fresh
`updated_at` (UTC, ISO 8601). The script is idempotent — re-runs leave
already-migrated files untouched.

Usage:
    scripts/migrate_plan_status.py [--dry-run] [--plans-dir DIR]
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

LEGACY_TO_NEW = {
    "pending": "todo",
    "in-progress": "development",
    "archived": "done",
}

STATUS_LINE = re.compile(r"^(status:\s*)([a-zA-Z-]+)\s*$", re.MULTILINE)
UPDATED_AT_LINE = re.compile(r"^(updated_at:\s*)\"?[^\"\n]+\"?\s*$", re.MULTILINE)


def migrate_file(path: Path, now_iso: str, dry_run: bool) -> tuple[str, str] | None:
    text = path.read_text(encoding="utf-8")
    # Front-matter only — first --- block
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    head = text[: end + 4]
    tail = text[end + 4 :]

    m = STATUS_LINE.search(head)
    if not m:
        return None
    current = m.group(2)
    new = LEGACY_TO_NEW.get(current)
    if new is None:
        return None  # already migrated or unknown — skip

    new_head = STATUS_LINE.sub(lambda match: f"{match.group(1)}{new}", head, count=1)
    if UPDATED_AT_LINE.search(new_head):
        new_head = UPDATED_AT_LINE.sub(lambda match: f'{match.group(1)}"{now_iso}"', new_head, count=1)
    new_text = new_head + tail

    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return (current, new)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="report changes without writing")
    ap.add_argument(
        "--plans-dir",
        default=".claude/plans",
        help="path to plans directory (default: .claude/plans)",
    )
    args = ap.parse_args()

    plans_dir = Path(args.plans_dir)
    if not plans_dir.is_dir():
        print(f"error: {plans_dir} is not a directory", file=sys.stderr)
        return 1

    now_iso = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    files = sorted(plans_dir.rglob("*.md"))
    migrated = 0
    skipped = 0
    for f in files:
        result = migrate_file(f, now_iso, args.dry_run)
        if result is None:
            skipped += 1
            continue
        current, new = result
        prefix = "[dry-run] " if args.dry_run else ""
        print(f"{prefix}{f.relative_to(plans_dir.parent)}: {current} → {new}")
        migrated += 1

    print()
    print(f"Done. Migrated: {migrated}; already-canonical or out-of-scope: {skipped}.")
    if args.dry_run:
        print("Re-run without --dry-run to write changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
