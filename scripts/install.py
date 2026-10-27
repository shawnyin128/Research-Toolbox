"""Install standalone skills; preview by default, preserve replaced copies."""

import argparse
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def reject_links(path: Path) -> None:
    """Refuse symlinks/junctions in destinations or their existing parents."""
    for part in (path, *path.parents):
        if part.is_symlink() or part.is_junction():
            raise ValueError(f"Linked destination is not supported: {part}")


def install(root: Path, destination: Path, names: list[str], *, apply=False, update=False) -> list[str]:
    root = root.resolve()
    catalog = json.loads((root / "toolbox.json").read_text(encoding="utf-8"))["skills"]
    selected = names or catalog
    if len(set(selected)) != len(selected) or any(name not in catalog for name in selected):
        raise ValueError("Select unique skill names from toolbox.json")
    if any(not name.startswith("research-") or Path(name).name != name or "/" in name or "\\" in name for name in selected):
        raise ValueError("Invalid skill directory name")

    destination = destination.expanduser().absolute()
    reject_links(destination)
    destination = destination.resolve()
    if destination == root or destination.is_relative_to(root) or root.is_relative_to(destination):
        raise ValueError("Install destination must be separate from the toolbox checkout")
    if destination.exists() and not destination.is_dir():
        raise ValueError(f"Destination is not a directory: {destination}")

    # Preflight the entire selection before changing any installed skill.
    for name in selected:
        source = root / "skills" / name
        target = destination / name
        if not (source / "SKILL.md").is_file():
            raise ValueError(f"Missing source skill: {name}")
        for item in (source, *source.rglob("*")):
            if item.is_symlink() or item.is_junction():
                raise ValueError(f"Linked source is not supported: {item}")
        reject_links(target)
        if target.exists() and not target.is_dir():
            raise ValueError(f"Target is not a directory: {target}")
        if target.exists() and not update:
            raise FileExistsError(f"Already installed: {target}; use --update to preserve and replace it")

    messages = [f"{'Update' if (destination / name).exists() else 'Install'} {name} -> {destination / name}" for name in selected]
    if not apply:
        return ["Preview only; pass --apply to write files.", *messages]

    backup_root = destination.parent / f"{destination.name}-backups"
    reject_links(backup_root)
    backup_root.mkdir(parents=True, exist_ok=True)
    destination.mkdir(parents=True, exist_ok=True)
    for name in selected:
        target = destination / name
        # Staging/backups stay outside the discoverable skills directory.
        with tempfile.TemporaryDirectory(prefix="research-toolbox-", dir=backup_root) as temporary:
            staging = Path(temporary) / name
            shutil.copytree(root / "skills" / name, staging)
            backup = None
            if target.exists():
                backup = Path(temporary).with_name(Path(temporary).name + "-saved") / name
                backup.parent.mkdir()
                target.rename(backup)
            try:
                staging.rename(target)
            except OSError:
                if backup is not None:
                    backup.rename(target)
                raise
            if backup is not None:
                messages.append(f"Previous copy preserved: {backup}")
    return messages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, required=True, help="Skill installation directory")
    parser.add_argument("--skills", nargs="+", default=[], help="Selected canonical names; default: all")
    parser.add_argument("--apply", action="store_true", help="Apply the previewed installation")
    parser.add_argument("--update", action="store_true", help="Preserve existing copies outside --dest, then replace")
    args = parser.parse_args()
    try:
        messages = install(ROOT, args.dest, args.skills, apply=args.apply, update=args.update)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Install failed: {error}\n")
    print("\n".join(messages))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
