"""Check skill metadata, portable local references, and toolbox catalog."""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]


def local_links(document: Path, boundary: Path) -> list[str]:
    errors = []
    content = document.read_text(encoding="utf-8")
    # This repository uses inline Markdown links, without parenthesized filenames.
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
        parsed = urlsplit(target.strip().strip("<>"))
        if parsed.scheme or not parsed.path:
            continue
        path = (document.parent / unquote(parsed.path)).resolve()
        if not path.is_relative_to(boundary.resolve()):
            errors.append(f"{document}: reference leaves package: {target}")
        elif not path.exists():
            errors.append(f"{document}: missing reference: {target}")
    return errors


def validate_skill(skill: Path) -> list[str]:
    errors = []
    entry = skill / "SKILL.md"
    try:
        content = entry.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", content, re.S)
        if not match:
            return [f"{entry}: missing YAML frontmatter"]
        front = yaml.safe_load(match.group(1))
        if not isinstance(front, dict):
            return [f"{entry}: frontmatter must be a mapping"]
        name = front.get("name")
        if name != skill.name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(name)) or len(str(name)) > 64:
            errors.append(f"{entry}: name must match folder and use lowercase hyphens")
        description = front.get("description")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            errors.append(f"{entry}: invalid description")
        ui = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
        if not isinstance(ui, dict):
            return [*errors, f"{skill}: UI metadata must be a mapping"]
        interface = ui.get("interface", {})
        if not isinstance(interface, dict):
            return [*errors, f"{skill}: interface must be a mapping"]
        if not isinstance(interface.get("display_name"), str):
            errors.append(f"{skill}: display name is missing")
        short = interface.get("short_description", "")
        if not isinstance(short, str) or not 25 <= len(short) <= 64:
            errors.append(f"{skill}: short_description must be 25–64 characters")
        if f"${name}" not in str(interface.get("default_prompt", "")):
            errors.append(f"{skill}: default_prompt must invoke the canonical name")
        policy = ui.get("policy", {})
        if not isinstance(policy, dict) or policy.get("allow_implicit_invocation", True) is not True:
            errors.append(f"{skill}: preserve automatic discovery")
        for document in skill.rglob("*.md"):
            errors.extend(local_links(document, skill))
            if re.search(r"__[A-Z][A-Z_]*__|\[TODO:", document.read_text(encoding="utf-8")):
                errors.append(f"{document}: unresolved scaffold token")
        for item in skill.rglob("*"):
            if item.is_symlink() or item.is_junction():
                errors.append(f"{item}: linked content prevents standalone packaging")
    except (OSError, yaml.YAMLError) as error:
        errors.append(f"{skill}: {error}")
    return errors


def validate(root: Path) -> list[str]:
    errors = []
    catalog = json.loads((root / "toolbox.json").read_text(encoding="utf-8"))
    names = catalog["skills"]
    folders = sorted(path.name for path in (root / "skills").iterdir() if path.is_dir())
    if len(set(names)) != len(names) or sorted(names) != folders:
        errors.append("Catalog and skill directories disagree")
    for name in names:
        if not isinstance(name, str) or not re.fullmatch(r"research-[a-z0-9-]+", name):
            errors.append(f"Invalid catalog name: {name}")
            continue
        errors.extend(validate_skill(root / "skills" / name))
    if any(value not in names for value in catalog.get("migration", {}).values()):
        errors.append("Migration table points to an unknown skill")
    for document in [root / "README.md", *(root / "docs").rglob("*.md")]:
        errors.extend(local_links(document, root))
    cases = json.loads((root / "evaluations" / "cases.json").read_text(encoding="utf-8"))
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate evaluation IDs")
    for case in cases:
        if any(name not in names for name in case["expected_skills"]):
            errors.append(f"Unknown skill in evaluation: {case['id']}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--skill", type=Path, help="Validate one standalone installed skill")
    args = parser.parse_args()
    errors = validate_skill(args.skill) if args.skill else validate(args.root)
    if errors:
        print("\n".join(errors))
        return 1
    print("Validation passed: metadata, catalog, and local references are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
