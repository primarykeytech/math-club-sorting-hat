#!/usr/bin/env python3
"""Randomly assign students from a text file into balanced groups."""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
from typing import Sequence


PROGRAM_NAME = "The Hat that Sorts(TM)"
BANNER = r'''
                    .-"""""""""-.
                  .'            '.
                 /                \
                |                  |
                |                  |
                |                  |
                |                  |
                |                  |
             .-======================-.
            /__________________________\

              The Hat that Sorts(TM)
'''


def read_students(path: Path) -> list[str]:
    """Read non-empty student names, one per line, from *path*."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ValueError(f"Could not read student file '{path}': {error}") from error

    students = [line.strip() for line in lines if line.strip()]
    if not students:
        raise ValueError("The student file contains no student names.")
    return students


def assign_groups(
    students: Sequence[str], group_count: int, rng: random.Random | None = None
) -> list[list[str]]:
    """Shuffle *students* and return *group_count* groups with near-equal sizes."""
    if group_count < 1:
        raise ValueError("The number of groups must be at least 1.")
    if group_count > len(students):
        raise ValueError("The number of groups cannot exceed the number of students.")

    shuffled_students = list(students)
    (rng or random.Random()).shuffle(shuffled_students)
    return [shuffled_students[index::group_count] for index in range(group_count)]


def format_assignments(groups: Sequence[Sequence[str]]) -> str:
    """Format groups for display in the terminal."""
    lines = [BANNER.strip("\n"), "", "Your groups are:", ""]
    for number, group in enumerate(groups, start=1):
        lines.append(f"Group {number}")
        lines.extend(f"  - {student}" for student in group)
        lines.append("")
    return "\n".join(lines).rstrip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Randomly sort students from a text file into balanced groups."
    )
    parser.add_argument("students_file", type=Path, help="Text file containing one student name per line.")
    parser.add_argument("groups", type=int, help="Number of groups to create.")
    parser.add_argument(
        "--seed", type=int, help="Optional random seed for a reproducible assignment."
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        students = read_students(args.students_file)
        rng = random.Random(args.seed) if args.seed is not None else None
        groups = assign_groups(students, args.groups, rng)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(format_assignments(groups))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
