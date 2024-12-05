import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from submit_answer import submit_answer

# Advent of Code 2024 - Day 3

YEAR = 2024
DAY = 3
PART = 2

URL = "https://adventofcode.com/2024/day/3"


def main():
    data = (Path(__file__).parent / "input_text.txt").read_text().strip()
    total = 0

    # find active parts
    active = ""
    remainder = data
    while len(remainder):
        try:
            do_part, dont_part = remainder.split("don't()", maxsplit=1)
            active += do_part
            print(f"first split {len(do_part)} {len(dont_part)}")
            try:
                dont_part, do_part = dont_part.split("do()", maxsplit=1)
                print(f"second split {len(do_part)} {len(dont_part)}")
                remainder = do_part
            except ValueError:
                break  # no more valid parts

        except ValueError:
            active += f"-{remainder}"
            print(len(active))
            break

    print("active = " + active)
    print(f"{len(active)=} {len(data)=}")
    for match in re.findall(
        pattern=r"mul\((?P<first>\d{1,3}),(?P<second>\d{1,3})\)", string=active
    ):
        total += int(match[0]) * int(match[1])
    print(total)
    if total > 0:
        return total


if __name__ == "__main__":
    answer = main()
    if answer:
        print(submit_answer(YEAR, DAY, PART, str(answer)))
        print(f"Part 2 asnwer = ")
