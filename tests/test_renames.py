import unittest
import tempfile
import subprocess
from pathlib import Path


class TestCaseTransformationsAndInvalidRegex(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory with test files
        self.test_dir = tempfile.mkdtemp()
        self.test_files = [
            "MixedCase.txt",
            "lowercase.pdf",
            "UPPERCASE.JPG",
            "With Spaces.json",
            "Special_Chars@File.py",
            "numbers123.tmp",
        ]

        for filename in self.test_files:
            Path(self.test_dir).joinpath(filename).write_text("test content")

    def tearDown(self):
        # Clean up the temporary directory
        for item in Path(self.test_dir).glob("*"):
            item.unlink()
        Path(self.test_dir).rmdir()

    def run_renx(self, *args):
        """Helper to run renx as subprocess"""
        cmd = ["python", "-m", "renx"] + list(args) + [self.test_dir]
        print(f"[COMMAND] {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if 1:
            print(f"[STDOUT]\n{result.stdout}")
            if result.stderr:
                print(f"[STDERR]\n{result.stderr}")
        return result

    def test_upper_case_transformation(self):
        # Test --upper flag
        result = self.run_renx("--upper", "--act")

        expected_files = [
            "MIXEDCASE.TXT",
            "LOWERCASE.PDF",
            "UPPERCASE.JPG",
            "WITH SPACES.JSON",
            "SPECIAL_CHARS@FILE.PY",
            "NUMBERS123.TMP",
        ]

        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        self.assertEqual(current_files, set(expected_files), "All filenames should be uppercase")

        # Verify return code is success
        self.assertEqual(result.returncode, 0, "Should exit successfully")

    def test_lower_case_transformation(self):
        # Test --lower flag
        result = self.run_renx("--lower", "--act")

        expected_files = [
            "mixedcase.txt",
            "lowercase.pdf",
            "uppercase.jpg",
            "with spaces.json",
            "special_chars@file.py",
            "numbers123.tmp",
        ]

        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        self.assertEqual(current_files, set(expected_files), "All filenames should be lowercase")

        # Verify extensions are also lowercased
        self.assertIn("uppercase.jpg", current_files, "Extensions should be lowercased too")

    def test_conflicting_case_flags(self):
        # Test both --upper and --lower (should error)
        result = self.run_renx("--upper", "--lower")

        # Verify error message and non-zero exit code
        self.assertNotEqual(result.returncode, 0, "Conflicting flags should cause error")
        self.assertIn("error", result.stderr.lower(), "Should show error about conflicting flags")

    def test_invalid_regex_syntax(self):
        # Test malformed regex pattern
        invalid_patterns = [
            # "/unclosed/pattern",  # Missing closing delimiter
            "/*invalid*/",  # Invalid regex syntax
            "/[/",  # Unclosed character class
            "/\\",  # Trailing backslash
            "//",  # Empty pattern
            "/a/b/c/d/e/f/",  # Too many delimiters
        ]

        for pattern in invalid_patterns:
            with self.subTest(pattern=pattern):
                result = self.run_renx("-s", pattern)
                self.assertNotEqual(result.returncode, 0, f"Invalid pattern '{pattern}' should fail")
                self.assertIn(
                    "error",
                    result.stderr.lower(),
                    f"Should show error for pattern '{pattern}'",
                )

    def test_case_with_regex_subs(self):
        # Test combination of case transform and regex substitution
        result = self.run_renx(
            "--lower",
            "-s",
            "/ /_/",  # Replace spaces with underscores
            "-s",
            "/@//",  # Remove @ symbols
            "--act",
        )

        expected_files = [
            "mixedcase.txt",
            "lowercase.pdf",
            "uppercase.jpg",
            "with_spaces.json",
            "special_charsfile.py",
            "numbers123.tmp",
        ]

        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        self.assertEqual(
            current_files,
            set(expected_files),
            "Should apply both case and regex transformations",
        )

        # Verify transformations were applied in correct order
        self.assertIn(
            "special_charsfile.py",
            current_files,
            "@ symbol should be removed after case conversion",
        )

    def test_dry_run_output_for_case(self):
        # Verify dry-run shows case transformations
        result = self.run_renx("--upper")

        # Check output contains expected uppercase operations
        output = result.stdout
        self.assertIn("REN: 'MixedCase.txt' -> 'MIXEDCASE.TXT' ?", output)
        self.assertIn("REN: 'lowercase.pdf' -> 'LOWERCASE.PDF' ?", output)

        # Verify no files were actually renamed
        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        self.assertTrue(
            current_files.issuperset(self.test_files),
            "Files should not be renamed in dry-run mode",
        )


if __name__ == "__main__":
    unittest.main()
