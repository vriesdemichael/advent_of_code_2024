import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pathlib import Path
import yaml
import typer
import os

# Load session token from .env file
load_dotenv()
SESSION_TOKEN = os.getenv("AOC_SESSION_TOKEN")

if not SESSION_TOKEN:
    raise ValueError(
        "Session token not found. Please set AOC_SESSION_TOKEN in your .env file."
    )

# Constants
STORAGE_FILE = Path("aoc_data.yaml")

# Create the CLI app
app = typer.Typer()


def fetch_input(year, day):
    """Fetch input data for a specific day."""
    response = client.get(f"/{year}/day/{day}/input")
    response.raise_for_status()
    return response.text.strip()


def fetch_puzzle(year, day):
    """Fetch the puzzle details: title, descriptions, and answers."""
    response = client.get(f"/{year}/day/{day}")

    # Stop processing if the page is not available yet
    if response.status_code == 404:
        raise FileNotFoundError(f"Day {day} is not yet available for year {year}.")

    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Title
    title_tag = soup.find("h2")
    if not title_tag:
        raise ValueError(f"Title not found for day {day}.")
    title = title_tag.text.strip()

    # Descriptions
    articles = soup.find_all("article", class_="day-desc")
    descriptions = [article.get_text(separator="\n").strip() for article in articles]

    # Handle parts
    parts = {
        "part1": descriptions[0] if len(descriptions) > 0 else "",
        "part2": "\n\n".join(descriptions) if len(descriptions) > 1 else "",
    }

    # Answers and progress
    answers = {
        "part1": {"correct": None, "wrong": []},
        "part2": {"correct": None, "wrong": []},
    }
    
    # Find all <p> tags containing "Your puzzle answer was"
    answer_tags = [p for p in soup.find_all("p") if "Your puzzle answer was" in p.get_text() and p.find("code")]
    for n, p_tag in enumerate(answer_tags, 1):
        code_tag = p_tag.find("code")
        if code_tag:
            answer = code_tag.text.strip()
            answers[f"part{n}"]["correct"] = answer

    

    return title, parts, answers


def load_or_initialize_storage():
    """Load or initialize the YAML storage file."""
    if STORAGE_FILE.exists():
        with STORAGE_FILE.open("r") as file:
            return yaml.safe_load(file) or {}
    return {}


def save_storage(data):
    """Save the YAML storage file."""
    with STORAGE_FILE.open("w") as file:
        yaml.safe_dump(data, file)


def update_storage(data, year, day, title, input_data, parts, answers):
    """Update the YAML storage with puzzle data."""
    if year not in data:
        data[year] = {}
    if day not in data[year]:
        data[year][day] = {
            "title": title,
            "input": input_data,
            "parts": {"part1": parts["part1"], "part2": parts["part2"]},
            "answers": answers,
        }
    else:
        # Update answers if missing or different
        for part in parts:
            if (
                answers[part]["correct"]
                and not data[year][day]["answers"][part]["correct"]
            ):
                data[year][day]["answers"][part]["correct"] = answers[part]["correct"]


def initialize_puzzle_day(storage_file: Path, year: int, day: int):
    """
    Initialize a puzzle day directory structure using data from the storage file.

    Args:
        storage_file (Path): Path to the storage file (YAML format).
        year (int): The puzzle year.
        day (int): The puzzle day.
    """
    # Load data from the storage file
    if not storage_file.exists():
        raise FileNotFoundError(f"Storage file {storage_file} does not exist.")

    with storage_file.open("r") as file:
        storage_data = yaml.safe_load(file)

    if not storage_data or year not in storage_data or day not in storage_data[year]:
        raise ValueError(
            f"No data found for Year {year}, Day {day} in the storage file."
        )

    day_data = storage_data[year][day]
    puzzle_input = day_data.get("input", "")
    parts = day_data.get("parts", {})

    # Define the directory path
    day_dir = Path(f"{year}/{day:02d}")
    day_dir.mkdir(parents=True, exist_ok=True)

    # Create input_text.txt if puzzle input is available
    if puzzle_input:
        input_path = day_dir / "input_text.txt"
        input_path.write_text(puzzle_input)

    # Define bootstrap content template
    bootstrap_template = """\
from pathlib import Path

import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from submit_answer import submit_answer


# Advent of Code {year} - Day {day}

YEAR = {year}
DAY = {day}
PART = {part}

URL = "https://adventofcode.com/{year}/day/{day}"


def main():
    data = (Path(__file__).parent / "input_text.txt").read_text().strip()
    ...


if __name__ == "__main__":
    answer = main()
    if answer:
        print(submit_answer(YEAR, DAY, PART, str(answer)))
        print(f"Part {part} asnwer = ")
"""

    # Create or update `part1.py`
    part1_path = day_dir / "part1.py"
    if not part1_path.exists():
        part1_content = bootstrap_template.format(year=year, day=day, part=1)
        part1_path.write_text(part1_content)

    # Create or update `part2.py`
    part2_path = day_dir / "part2.py"
    if not part2_path.exists():
        part2_content = bootstrap_template.format(year=year, day=day, part=2)
        part2_path.write_text(part2_content)

    # Create or update `description.md`
    description_path = day_dir / "description.md"
    description_content = ""
    if "part1" in parts and parts["part1"]:
        description_content += f"# PART 1\n\n{parts['part1']}\n\n"
    if "part2" in parts and parts["part2"]:
        description_content += f"# PART 2\n\n{parts['part2']}\n\n"
    description_path.write_text(description_content)

    print(f"Initialized {day_dir} with input, bootstrap files, and description.")


@app.command()
def fetch_data(year: int):
    """
    Fetch puzzle data, input, and answers for all days of Advent of Code for the given year.
    Only fetch pages without answers for both parts and stop if a day is not released yet.
    """
    storage = load_or_initialize_storage()

    for day in range(1, 26):
        try:
            # Check if both parts already have answers
            if year in storage and day in storage[year]:
                day_data = storage[year][day]
                if (
                    "part1" in day_data["answers"] and 
                    day_data["answers"]["part1"]["correct"] and "part2" in day_data["answers"]
                    and day_data["answers"]["part2"]["correct"]
                ):
                    print(
                        f"Skipping Year {year}, Day {day}: Both parts already completed."
                    )
                    continue

            # Fetch input data
            input_data = fetch_input(year, day)

            # Fetch puzzle data
            title, parts, answers = fetch_puzzle(year, day)

            # Update storage
            update_storage(storage, year, day, title, input_data, parts, answers)
            save_storage(storage)

            print(f"Data for Year {year}, Day {day} saved.")

        except FileNotFoundError as e:
            print(f"Stopping: {e}")
            break
        except httpx.HTTPStatusError as e:
            print(f"Failed to fetch data for Year {year}, Day {day}: {e}")
            break  # Do not continue for other days yet
        except Exception as e: 
            print(f"An error occurred for Year {year}, Day {day}: {e}")
            raise e

    for day in range(1, 26):
        try:
            initialize_puzzle_day(STORAGE_FILE, year, day)
        except (KeyError, ValueError) as _:
            pass  # Skip days that don't have data
            break  # no data yet means it won't be available for the rest of the days
        except Exception as e:
            print(f"An error occurred while initializing Day {day}: {e}")


if __name__ == "__main__":
    # Create an httpx client with the session cookie
    client = httpx.Client(
        base_url="https://adventofcode.com",
        cookies={"session": SESSION_TOKEN},
        timeout=10,
    )
    app()
