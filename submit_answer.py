import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import typer
import os

# Load session token from .env file
load_dotenv()
SESSION_TOKEN = os.getenv("AOC_SESSION_TOKEN")

if SESSION_TOKEN is None or not SESSION_TOKEN:
    raise ValueError(
        "Session token not found. Please set AOC_SESSION_TOKEN in your .env file."
    )

# Create the CLI app
app = typer.Typer()



def submit_answer(year: int, day: int, part: int, answer: str) -> str:
    """
    Submit an answer to Advent of Code.
    
    Args:
        year (int): The puzzle year.
        day (int): The puzzle day.
        part (int): The part of the puzzle (1 or 2).
        answer (str): The answer to submit.
    
    Returns:
        str: The server's response message.
    """
    url = f"https://adventofcode.com/{year}/day/{day}/answer"
    data = {"level": part, "answer": answer}
    
    client = httpx.Client(
        base_url="https://adventofcode.com",
        cookies={"session": str(SESSION_TOKEN)},
        timeout=10,
    )
    
    response = client.post(url, data=data)
    response.raise_for_status()  # Raise an error for HTTP issues
    
    # Parse response to check if the answer was correct
    soup = BeautifulSoup(response.text, "html.parser")
    article = soup.find("article")
    if article is None:
        raise ValueError("Response article not found.")
    message = article.text.strip()
    
    if "That's the right answer" in message:
        return "✅ Correct answer submitted!"
    elif "That's not the right answer" in message:
        return "❌ Incorrect answer."
    elif "You don't seem to be solving the right level" in message:
        return "⚠️ Already solved or incorrect part."
    else:
        return f"⚠️ Unexpected response: {message}"

