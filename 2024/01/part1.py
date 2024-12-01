from pathlib import Path


# Advent of Code 2024 - Day 1

YEAR = 2024
DAY = 1
PART = 1

URL = "https://adventofcode.com/2024/day/1"



def main():
    data = (Path(__file__).parent / "input_text.txt").read_text().strip()
    first_numbers = []
    seconnd_numbers = []

    for line in data.splitlines():
        first, second = line.split("   ")
        first_numbers.append(int(first))
        seconnd_numbers.append(int(second))
    first_numbers.sort()
    seconnd_numbers.sort()
    answer = sum(abs(a - b) for a, b in zip(first_numbers, seconnd_numbers))
    return answer


if __name__ == "__main__":
    print(f"Part 1 answer = {main()}")
