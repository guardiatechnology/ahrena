"""Ahrena skill tooling (validator + packager).

Public entry points:
    validate.run(skill_path) -> list[Violation]
    package.run(skill_path, build_dir, dist_dir) -> PackageReport

Both are also exposed as CLIs (`python -m scripts.skills.validate`, `python -m scripts.skills.package`).
"""
