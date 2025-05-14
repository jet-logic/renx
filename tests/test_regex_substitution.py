import unittest
import tempfile
import subprocess
from pathlib import Path


class TestRegexSubstitution(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory with test files
        self.test_dir = tempfile.mkdtemp()
        self.test_files = [
            "file1.txt",
            "document-2023.pdf",
            "image001.jpg",
            "data_file.json",
            "my script.py",
            "backup~temp.tmp",
            "photo (1).png",
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
        c = ["python", "-m", "renx"] + list(args) + [self.test_dir]
        result = subprocess.run(c, capture_output=True, text=True, check=True)
        o = result.stdout + result.stderr
        print(*c)
        print(o)
        return o

    def test_basic_substitution(self):
        # Replace spaces with underscores
        output = self.run_renx("-s", "/ /_/", "--act")
        print(output)

        expected_files = [
            "file1.txt",
            "document-2023.pdf",
            "image001.jpg",
            "data_file.json",
            "my_script.py",
            "backup~temp.tmp",
            "photo_(1).png",
        ]

        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        self.assertEqual(
            current_files,
            set(expected_files),
            "Spaces should be replaced with underscores",
        )

    def test_complex_substitution(self):
        # Multiple substitutions: remove ~temp, add prefix, clean parentheses
        output = self.run_renx(
            "-s",
            "/~temp//",  # Remove ~temp
            "-s",
            "/^/processed_/",  # Add prefix
            "-s",
            "/[()]//",  # Remove parentheses
            "--act",
        )

        expected_files = [
            "processed_file1.txt",
            "processed_document-2023.pdf",
            "processed_image001.jpg",
            "processed_data_file.json",
            "processed_my script.py",
            "processed_backup.tmp",
            "processed_photo 1.png",
        ]

        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        self.assertEqual(
            current_files,
            set(expected_files),
            "Complex substitutions should be applied in order",
        )

    def test_case_insensitive_substitution(self):
        # Case-insensitive replacement of file extensions
        output = self.run_renx("-s", r"/\.jpe?g$/.jpg/i", "--act")  # Normalize .jpeg/.JPG to .jpg

        # Create a test file with mixed case extension
        Path(self.test_dir).joinpath("picture.JPEG").write_text("test")

        output = self.run_renx("-s", r"/\.jpe?g$/.jpg/i", "--act")

        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        self.assertIn(
            "picture.jpg",
            current_files,
            "Case-insensitive extension replacement should work",
        )
        self.assertNotIn("picture.JPEG", current_files, "Original case variant should be replaced")

    def test_capture_groups(self):
        # Use capture groups to reorganize filename parts
        output = self.run_renx(
            "-s",
            r"/^(\w+)(\d{3})\.(\w+)/\2_\1.\3/",  # image001.jpg -> 001_image.jpg
            "--act",
        )
        # print(output)

        expected_files = [
            "file1.txt",
            "document-2023.pdf",
            "001_image.jpg",  # Transformed from image001.jpg
            "data_file.json",
            "my script.py",
            "backup~temp.tmp",
            "photo (1).png",
        ]

        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        # print(current_files)
        self.assertSetEqual(current_files, set(expected_files), "Capture groups should work correctly")

    def test_dry_run_output(self):
        # Verify dry-run shows correct substitutions without executing
        output = self.run_renx("-s", "/file/data/", "-s", "/ /_/")
        print(output)

        # Check output contains expected rename operations
        self.assertIn("REN: 'data_file.json' -> 'data_data.json' ?", output)
        self.assertIn("REN: 'my script.py' -> 'my_script.py' ?", output)

        # Verify no files were actually renamed
        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        self.assertTrue(
            current_files.issuperset(self.test_files),
            "Files should not be renamed in dry-run mode",
        )

    def test_multiple_subs_flags(self):
        # Test multiple -s flags with different delimiters
        output = self.run_renx(
            "-s",
            "# #_#",  # Using # as delimiter
            "-s",
            "|~temp||",  # Using | as delimiter
            "--act",
        )

        expected_files = [
            "file1.txt",
            "document-2023.pdf",
            "image001.jpg",
            "data_file.json",
            "my_script.py",
            "backup.tmp",  # ~temp removed
            "photo_(1).png",  # space replaced
        ]

        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        self.assertEqual(
            current_files,
            set(expected_files),
            "Multiple substitution patterns should work",
        )

    def test_Simple_Transformation_ext(self):
        self.run_renx("-s", "ext:upper", "--act")  # Using # as delimiter

        expected_files = [
            "file1.TXT",
            "document-2023.PDF",
            "image001.JPG",
            "data_file.JSON",
            "my script.PY",
            "backup~temp.TMP",
            "photo (1).PNG",
        ]

        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        self.assertEqual(
            current_files,
            set(expected_files),
            "Multiple substitution patterns should work",
        )

    def test_000(self):
        # Test multiple -s flagms with different delimiters
        output = self.run_renx("-s", "@backup@@stem:upper", "--act")

        expected_files = [
            "file1.txt",
            "document-2023.pdf",
            "image001.jpg",
            "data_file.json",
            "my script.py",
            "BACKUP~temp.tmp",
            "photo (1).png",
        ]

        current_files = set(f.name for f in Path(self.test_dir).iterdir())
        self.assertEqual(
            current_files,
            set(expected_files),
            "Multiple substitution patterns should work",
        )

        # self.test_files = [
        #     "file1.txt",
        #     "document-2023.pdf",
        #     "image001.jpg",
        #     "data_file.json",
        #     "my script.py",
        #     "backup~temp.tmp",
        #     "photo (1).png",
        # ]


if __name__ == "__main__":
    unittest.main()
