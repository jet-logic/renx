import unittest

from renx.__main__ import split_subs, trans_map


class TestSplitSubs(unittest.TestCase):
    # ---- Valid Patterns ----
    def test_basic_substitution(self):
        self.assertEqual(split_subs("/search/replace/"), ("search", "replace", {}))

    def test_with_regex_flag(self):
        self.assertEqual(split_subs("/pattern/replace/i"), ("(?i)pattern", "replace", {}))

    def test_with_transformation(self):
        self.assertEqual(split_subs("|hello||upper"), ("hello", "", {"transform": trans_map["upper"]}))

    # def test_multiple_transforms(self):
    #     self.assertEqual(
    #         split_subs("#text##upper:slugify"), ("text", "", {"upper": trans_map["upper"], "slugify": trans_map["slugify"]})
    #     )

    def test_empty_replacement(self):
        self.assertEqual(split_subs("@pattern@@upper"), ("pattern", "", {"transform": trans_map["upper"]}))

    def test_different_separator(self):
        self.assertEqual(split_subs("~find~~i:lower"), ("(?i)find", "", {"transform": trans_map["lower"]}))

    # ---- Invalid Patterns ----
    def test_empty_string(self):
        with self.assertRaises(SyntaxError):
            split_subs("")

    def test_invalid_separator(self):
        with self.assertRaises(SyntaxError):
            split_subs("[not[valid[")

    def test_missing_separators(self):
        with self.assertRaises(SyntaxError):
            split_subs("/incomplete")

    def test_empty_search_pattern(self):
        with self.assertRaises(SyntaxError):
            split_subs("//replace/")

    def test_invalid_regex_flags(self):
        with self.assertRaises(SyntaxError):
            split_subs("/p/r/123")  # Numbers not allowed in flags

    def test_unknown_transform(self):
        with self.assertRaises(SyntaxError):
            split_subs("/a/b/unknown:x")

    # ---- Edge Cases ----
    # def test_max_splits_behavior(self):
    #     self.assertEqual(
    #         split_subs("/a//asciify:lower:upper"), ("a", "", {"asciify": True, "lower": True, "upper": True})
    #     )  # Only splits 3 times

    def test_flags_with_empty_tail(self):
        self.assertEqual(split_subs("/x/y/"), ("x", "y", {}))  # Note trailing separator


if __name__ == "__main__":
    unittest.main()
