from collections import Counter
from pathlib import Path

import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from submit_answer import submit_answer


# Advent of Code 2024 - Day 1

YEAR = 2024
DAY = 1
PART = 2

URL = "https://adventofcode.com/2024/day/1"




def main():
    data = (Path(__file__).parent / "input_text.txt").read_text().strip()
    first_numbers = []
    second_numbers = []

    for line in data.splitlines():
        first, second = line.split("   ")
        first_numbers.append(int(first))
        second_numbers.append(int(second))
        
    secound_list_counts = Counter(second_numbers)
    return sum(first * secound_list_counts[first] for first in first_numbers)



if __name__ == "__main__":
    answer = main()
    print(submit_answer(YEAR, DAY, PART, str(answer)))
    print(f"Part 2 answer = {main()}")
