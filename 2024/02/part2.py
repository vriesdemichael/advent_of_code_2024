from itertools import pairwise
from pathlib import Path

import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from submit_answer import submit_answer


# Advent of Code 2024 - Day 2

YEAR = 2024
DAY = 2
PART = 2

URL = "https://adventofcode.com/2024/day/2"


def test_list(int_list):
    diffs = [b - a for a, b in pairwise(int_list)]
    all_increasing_or_decreasing = all(x >= 0 for x in diffs) or all(
        x <= 0 for x in diffs
    )
    if not all_increasing_or_decreasing:
        return False

    return all(1 <= abs(x) <= 3 for x in diffs)


def main():
    data = (Path(__file__).parent / "input_text.txt").read_text().strip()
    total = 0
    for line in data.splitlines():
        int_list = [int(x) for x in line.split()]
        int_lists_with_one_missing = [
            int_list[:i] + int_list[i + 1 :] for i in range(len(int_list))
        ]
        for li in [int_list, *int_lists_with_one_missing]:
            if test_list(li):
                total += 1
                break

    return total


if __name__ == "__main__":
    answer = main()
    if answer:
        print(submit_answer(YEAR, DAY, PART, str(answer)))
        print(f"Part 2 answer = {answer}")
