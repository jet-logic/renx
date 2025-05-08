import unittest
import tempfile
import subprocess
from pathlib import Path


class TestUrlsafeRenameEndToEnd(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory with test files
        self.test_dir = tempfile.mkdtemp()
        self.test_files = [
            "My Résumé.pdf",
            "Vacation Photos 2023.jpg",
            "Price List (v2).xlsx",
            "config~backup.json",
            "file--name__.txt",
            "-document-v1.pdf",
            "user@domain.com.png",
            "script#1.py",
        ]

        for filename in self.test_files:
            print(filename)
            Path(self.test_dir).joinpath(filename).write_text("test content")

    def tearDown(self):
        # Clean up the temporary directory
        for item in Path(self.test_dir).glob("*"):
            item.unlink()
        Path(self.test_dir).rmdir()

    def run_renx(self, *args):
        """Helper to run renx as subprocess"""
        result = subprocess.run(
            ["python", "-m", "renx"] + list(args) + [self.test_dir],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout + result.stderr

    def test_urlsafe_dry_run(self):
        # Run in dry-run mode (default)
        output = self.run_renx("--urlsafe")

        # Verify output contains expected renames
        expected_transforms = {
            "My Résumé.pdf": "My_Resume.pdf",
            "Vacation Photos 2023.jpg": "Vacation_Photos_2023.jpg",
            "Price List (v2).xlsx": "Price_List_v2.xlsx",
            "config~backup.json": "config_backup.json",
            "file--name__.txt": "file-name.txt",
            "-document-v1.pdf": "document-v1.pdf",
            "user@domain.com.png": "user_domain.com.png",
            "script#1.py": "script_1.py",
        }

        for original, transformed in expected_transforms.items():
            self.assertIn(
                f"REN: {original!r} -> {transformed!r} ?",
                output,
                f"Dry-run should show {original} -> {transformed}",
            )

        # Verify no files were actually renamed
        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        self.assertTrue(
            current_files.issuperset(self.test_files),
            "Files should not be renamed in dry-run mode",
        )

    def test_urlsafe_actual_rename(self):
        # Run with --act to actually rename files
        self.run_renx("--urlsafe", "--act")

        # Expected filenames after transformation
        expected_files = [
            "My_Resume.pdf",
            "Vacation_Photos_2023.jpg",
            "Price_List_v2.xlsx",
            "config_backup.json",
            "file-name.txt",
            "document-v1.pdf",
            "user_domain.com.png",
            "script_1.py",
        ]

        # Verify the files were actually renamed
        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        self.assertEqual(
            current_files,
            set(expected_files),
            "Files should be renamed according to URL-safe rules",
        )

        # Verify original filenames no longer exist
        for original in self.test_files:
            self.assertFalse(
                Path(self.test_dir).joinpath(original).exists(),
                f"Original file {original} should be renamed",
            )

    def test_combined_options(self):
        # Test combining --urlsafe with --lower
        self.run_renx("--urlsafe", "--lower", "--act")

        # Verify combined transformation
        expected_files = [
            "my_resume.pdf",
            "vacation_photos_2023.jpg",
            "price_list_v2.xlsx",
            "config_backup.json",
            "file-name.txt",
            "document-v1.pdf",
            "user_domain.com.png",
            "script_1.py",
        ]

        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        self.assertEqual(
            current_files, set(expected_files), "Files should be URL-safe and lowercase"
        )


if __name__ == "__main__":
    unittest.main()
