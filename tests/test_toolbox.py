import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load_script("install")
validator = load_script("validate")


class ToolboxTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="toolbox-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.dest = self.base / "skills"

    def test_preview_has_no_filesystem_side_effects(self):
        result = installer.install(ROOT, self.dest, ["research-design"])
        self.assertIn("Preview only", result[0])
        self.assertFalse(self.dest.exists())
        self.assertEqual(list(self.base.iterdir()), [])

    def test_selective_install_is_complete_and_standalone(self):
        installer.install(ROOT, self.dest, ["research-design"], apply=True)
        self.assertEqual([path.name for path in self.dest.iterdir()], ["research-design"])
        installed = self.dest / "research-design"
        self.assertEqual(validator.validate_skill(installed), [])
        source = ROOT / "skills" / "research-design"
        for path in source.rglob("*"):
            if path.is_file():
                self.assertEqual(path.read_bytes(), (installed / path.relative_to(source)).read_bytes())

    def test_preflight_conflict_preserves_every_target(self):
        installer.install(ROOT, self.dest, ["research-tune"], apply=True)
        sentinel = self.dest / "research-tune" / "local.txt"
        sentinel.write_text("local edits", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            installer.install(ROOT, self.dest, ["research-design", "research-tune"], apply=True)
        self.assertFalse((self.dest / "research-design").exists())
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "local edits")

    def test_update_preserves_previous_copy_outside_discovery(self):
        installer.install(ROOT, self.dest, ["research-code"], apply=True)
        old = self.dest / "research-code" / "local.txt"
        old.write_text("keep my edits", encoding="utf-8")
        installer.install(ROOT, self.dest, ["research-code"], apply=True, update=True)
        self.assertFalse(old.exists())
        backups = list((self.base / "skills-backups").rglob("local.txt"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "keep my edits")
        self.assertEqual([path.name for path in self.dest.iterdir()], ["research-code"])
        self.assertEqual(validator.validate_skill(self.dest / "research-code"), [])

    def test_failed_replacement_restores_previous_copy(self):
        installer.install(ROOT, self.dest, ["research-code"], apply=True)
        old = self.dest / "research-code" / "local.txt"
        old.write_text("original", encoding="utf-8")
        original_rename = Path.rename

        def fail_staging(path, target):
            if path.name == "research-code" and path.parent.name.startswith("research-toolbox-") and not path.parent.name.endswith("-saved"):
                raise OSError("injected replacement failure")
            return original_rename(path, target)

        with patch.object(Path, "rename", fail_staging):
            with self.assertRaises(OSError):
                installer.install(ROOT, self.dest, ["research-code"], apply=True, update=True)
        self.assertEqual(old.read_text(encoding="utf-8"), "original")

    def test_unknown_or_duplicate_selection_is_rejected(self):
        for names in [["../outside"], ["research-design", "research-design"]]:
            with self.subTest(names=names), self.assertRaises(ValueError):
                installer.install(ROOT, self.dest, names, apply=True)
        self.assertFalse(self.dest.exists())

    def test_checkout_overlap_is_rejected(self):
        with self.assertRaises(ValueError):
            installer.install(ROOT, ROOT / "skills", ["research-design"], apply=True)

    def test_linked_destination_is_rejected(self):
        actual = self.base / "actual"
        actual.mkdir()
        linked = self.base / "linked"
        try:
            linked.symlink_to(actual, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"Host does not allow symlink creation: {error}")
        with self.assertRaises(ValueError):
            installer.install(ROOT, linked, ["research-design"], apply=True)
        self.assertEqual(list(actual.iterdir()), [])

    def test_all_installed_skills_validate_without_checkout_references(self):
        installer.install(ROOT, self.dest, [], apply=True)
        for skill in self.dest.iterdir():
            with self.subTest(skill=skill.name):
                self.assertEqual(validator.validate_skill(skill), [])

    def test_validator_finds_missing_local_reference(self):
        installer.install(ROOT, self.dest, ["research-design"], apply=True)
        (self.dest / "research-design" / "references" / "framework.md").unlink()
        errors = validator.validate_skill(self.dest / "research-design")
        self.assertTrue(any("missing reference" in error for error in errors))

    def test_validator_rejects_nonportable_reference(self):
        installer.install(ROOT, self.dest, ["research-design"], apply=True)
        entry = self.dest / "research-design" / "SKILL.md"
        entry.write_text(entry.read_text(encoding="utf-8") + "\n[external](../../private.md)\n", encoding="utf-8")
        self.assertTrue(any("leaves package" in error for error in validator.validate_skill(entry.parent)))

    def test_validator_rejects_wrong_identity_and_malformed_yaml(self):
        installer.install(ROOT, self.dest, ["research-tune"], apply=True)
        entry = self.dest / "research-tune" / "SKILL.md"
        original = entry.read_text(encoding="utf-8")
        entry.write_text(original.replace("name: research-tune", "name: wrong-name", 1), encoding="utf-8")
        self.assertTrue(any("name must match" in error for error in validator.validate_skill(entry.parent)))
        entry.write_text("---\nname: [broken\n---\n", encoding="utf-8")
        self.assertTrue(validator.validate_skill(entry.parent))

    def test_catalog_and_all_repository_links(self):
        self.assertEqual(validator.validate(ROOT), [])


if __name__ == "__main__":
    unittest.main()
