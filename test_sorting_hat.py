import random
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from sorting_hat import BANNER, assign_groups, main, read_students


class ReadStudentsTests(unittest.TestCase):
    def test_ignores_blank_lines_and_whitespace(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "students.txt"
            path.write_text(" Ada \n\nGrace\n  Linus  \n", encoding="utf-8")

            self.assertEqual(read_students(path), ["Ada", "Grace", "Linus"])

    def test_rejects_empty_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "students.txt"
            path.write_text("\n  \n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "contains no student names"):
                read_students(path)


class AssignGroupsTests(unittest.TestCase):
    def test_assigns_each_student_once_in_balanced_groups(self):
        students = ["Ada", "Grace", "Linus", "Alan", "Katherine", "Edsger", "Annie"]

        groups = assign_groups(students, 3, random.Random(10))

        self.assertEqual(sorted(student for group in groups for student in group), sorted(students))
        self.assertEqual([len(group) for group in groups], [3, 2, 2])

    def test_seeded_assignment_is_reproducible(self):
        students = ["Ada", "Grace", "Linus", "Alan"]

        self.assertEqual(
            assign_groups(students, 2, random.Random(7)),
            assign_groups(students, 2, random.Random(7)),
        )

    def test_rejects_invalid_group_counts(self):
        with self.assertRaisesRegex(ValueError, "at least 1"):
            assign_groups(["Ada"], 0)
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            assign_groups(["Ada"], 2)


class CommandLineTests(unittest.TestCase):
    def test_main_prints_banner_and_groups(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "students.txt"
            path.write_text("Ada\nGrace\nLinus\nAlan\n", encoding="utf-8")
            output = StringIO()

            with redirect_stdout(output):
                result = main([str(path), "2", "--seed", "4"])

        self.assertEqual(result, 0)
        self.assertIn(BANNER.strip(), output.getvalue())
        self.assertIn("Group 1", output.getvalue())
        self.assertIn("Group 2", output.getvalue())

    def test_main_reports_validation_error(self):
        error = StringIO()
        with redirect_stderr(error):
            result = main(["missing-students.txt", "2"])

        self.assertEqual(result, 1)
        self.assertIn("Could not read student file", error.getvalue())


if __name__ == "__main__":
    unittest.main()
