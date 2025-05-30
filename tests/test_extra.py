#!/bin/env python3
from pathlib import Path
import tempfile
import unittest
import subprocess


class TestExtra(unittest.TestCase):
    def exec(self, cmd: "list[str]", capture_output=True, text=True, **kwargs):
        print(f"[COMMAND] {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
        if capture_output:
            print(f"[STDOUT]\n{result.stdout}")
            if result.stderr:
                print(f"[STDERR]\n{result.stderr}")
        return result

    def test_example(self):
        from os import environ

        if environ.get("RUNNER_OS") == "Windows":
            return
        with tempfile.TemporaryDirectory() as tmp:
            top = Path(tmp)
            vid = top.joinpath("the.matrix.[1999].1080p.[YTS.AM].BRRip.x264-[GloDLS].ExTrEmE.mKV")
            vid.touch()
            scr = top.joinpath("test.sh")
            scr.write_text(
                r"""python -m renx --act \
    -s '#(?:(YTS(?:.?\w+)|YIFY|GloDLS|RARBG|ExTrEmE|EZTVx.to|MeGusta|Lama))##ix' \
    -s '!(2160p|1080p|720p|x264|x265|HEVC|AAC|AC3)!!i' \
    -s '!(HDRip|BluRay|WEB-DL|DVDrip|BRrip|WEBRip|HDRip|DTS)!!i' \
    -s '!\[(|\w+)\]!\1!' \
    -s '/[\._-]+/./' \
    -s '/\.+/ /stem' \
    -s /.+//ext:lower \
    -s '/.+//stem:title' \
    --include "*.m*" \
    ."""
            )
            subprocess.run(["sh", scr], cwd=top)
            self.assertEqual(set(["The Matrix 1999.mkv", "test.sh"]), set([x.name for x in top.iterdir()]))

    def test_chain_trans(self):

        with tempfile.TemporaryDirectory() as tmp:
            top = Path(tmp)
            vid = top.joinpath("My Résumé.doc")
            vid.touch()
            scr = top.joinpath("test.sh")
            scr.write_text(
                r"""python -m renx --act \
    -s '/.+//stem:asciify:swapcase:slugify' \
    *.doc \
    """
            )
            cmds = ["sh", scr]
            cmds = ["python", "-m", "renx", "--act", "-s", "/.+//stem:asciify:swapcase:slugify", "--include", "*.doc", tmp]
            self.exec(cmds, cwd=top)
            self.assertEqual(set(["mY_rESUME.doc", "test.sh"]), set([x.name for x in top.iterdir()]))
            # print(set([x.name for x in top.iterdir()]))

    def test_path_from(self):
        test_files = [
            "MixedCase.txt",
            "lowercase.pdf",
            "UPPERCASE.JPG",
            "With Spaces.json",
            "Special_Chars@File.py",
            "numbers123.tmp",
        ]
        expected_files = [
            "MixedCase.txt",
            "lowercase.pdf",
            "uppercase.jpg",
            "with spaces.json",
            "Special_Chars@File.py",
            "numbers123.tmp",
        ]

        with tempfile.TemporaryDirectory() as tmp:
            for filename in test_files:
                Path(tmp).joinpath(filename).write_text("test content")
            src = Path(tmp) / "paths.txt"
            src.write_text(
                r"""
            lowercase.pdf
            UPPERCASE.JPG
            With Spaces.json
            """
            )
            self.exec(["python", "-m", "renx", "--lower", "--act", "--paths-from", str(src)], cwd=tmp)
            src.unlink()
            current_files = set(f.name for f in Path(tmp).iterdir())
            self.assertEqual(current_files, set(expected_files), "Some filenames should be lowercase")


if __name__ == "__main__":
    unittest.main()
