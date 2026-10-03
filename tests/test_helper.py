import unittest

from sqlglot.helper import merge_ranges, name_sequence, truncate_sql_comment, tsort


class TestHelper(unittest.TestCase):
    def test_tsort(self):
        self.assertEqual(tsort({"a": set()}), ["a"])
        self.assertEqual(tsort({"a": {"b"}}), ["b", "a"])
        self.assertEqual(tsort({"a": {"c"}, "b": set(), "c": set()}), ["b", "c", "a"])
        self.assertEqual(
            tsort(
                {
                    "a": {"b", "c"},
                    "b": {"c"},
                    "c": set(),
                    "d": {"a"},
                }
            ),
            ["c", "b", "a", "d"],
        )

        with self.assertRaises(ValueError):
            tsort(
                {
                    "a": {"b", "c"},
                    "b": {"a"},
                    "c": set(),
                }
            )

    def test_name_sequence(self):
        s1 = name_sequence("a")
        s2 = name_sequence("b")

        self.assertEqual(s1(), "a0")
        self.assertEqual(s1(), "a1")
        self.assertEqual(s2(), "b0")
        self.assertEqual(s1(), "a2")
        self.assertEqual(s2(), "b1")
        self.assertEqual(s2(), "b2")

    def test_merge_ranges(self):
        self.assertEqual([], merge_ranges([]))
        self.assertEqual([(0, 1)], merge_ranges([(0, 1)]))
        self.assertEqual([(0, 1), (2, 3)], merge_ranges([(0, 1), (2, 3)]))
        self.assertEqual([(0, 3)], merge_ranges([(0, 1), (1, 3)]))
        self.assertEqual([(0, 1), (2, 4)], merge_ranges([(2, 3), (0, 1), (3, 4)]))

    def test_truncate_sql_comment(self):
        # Short strings
        self.assertEqual(truncate_sql_comment(""), "")
        self.assertEqual(truncate_sql_comment("hello world"), "hello world")
        self.assertEqual(truncate_sql_comment("  hello world  "), "hello world")
        self.assertEqual(truncate_sql_comment("\t hello world \t"), "hello world")

        # Multiline strings and whitespace
        self.assertEqual(truncate_sql_comment("line1\nline2"), "line1 line2")
        self.assertEqual(truncate_sql_comment("line1\r\nline2"), "line1 line2")
        self.assertEqual(truncate_sql_comment("line1\rline2"), "line1 line2")
        self.assertEqual(truncate_sql_comment("line1\n\nline2"), "line1 line2")
        self.assertEqual(truncate_sql_comment("line1\r\n\r\nline2"), "line1 line2")
        self.assertEqual(truncate_sql_comment("  \n  line1\nline2  \n  "), "line1 line2")

        # Truncation
        self.assertEqual(truncate_sql_comment("a" * 64), "a" * 64)
        self.assertEqual(truncate_sql_comment("a" * 65), f"{'a' * 61}...")
        self.assertEqual(len(truncate_sql_comment("a" * 65)), 64)
        self.assertEqual(truncate_sql_comment("hello beautiful world", max_len=10), "hello b...")
        self.assertEqual(len(truncate_sql_comment("hello beautiful world", max_len=10)), 10)
        self.assertEqual(
            truncate_sql_comment(
                "this is a very long multiline\nsql comment that needs truncation", max_len=20
            ),
            "this is a very lo...",
        )
        self.assertEqual(truncate_sql_comment("hello", max_len=3), "...")
