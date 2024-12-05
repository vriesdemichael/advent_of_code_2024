import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from submit_answer import submit_answer

# Advent of Code 2024 - Day 3

YEAR = 2024
DAY = 3
PART = 1

URL = "https://adventofcode.com/2024/day/3"


def main():
    data = (Path(__file__).parent / "input_text.txt").read_text().strip()
    total = 0
    for match in re.findall(
        pattern=r"mul\((?P<first>\d{1,3}),(?P<second>\d{1,3})\)", string=data
    ):
        total += int(match[0]) * int(match[1])

    if total > 0:
        return total


if __name__ == "__main__":
    answer = main()
    if answer is not None:
        print(f"Part 1 asnwer = {answer}")
        print(submit_answer(YEAR, DAY, PART, str(answer)))
