import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

MODEL = "gemini-3.1-flash-lite"


def create_client():
    """Initialize the Gemini API client."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found in the .env file."
        )

    return genai.Client(api_key=api_key)


def test_connection():
    """Test the connection to the Gemini API."""

    client = create_client()

    prompt = (
        "Explain in one short sentence what "
        "Intelligent Document Processing means."
    )

    start_time = time.perf_counter()

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    elapsed_time = time.perf_counter() - start_time

    print("=" * 60)
    print("GEMINI API CONNECTION")
    print("=" * 60)

    print(f"Model: {MODEL}")
    print(f"Response time: {elapsed_time:.2f} seconds")

    print("\nAI RESPONSE:")
    print(response.text)

    if response.usage_metadata:

        usage = response.usage_metadata

        print("\nTOKEN USAGE:")
        print(f"Input tokens: {usage.prompt_token_count}")
        print(f"Output tokens: {usage.candidates_token_count}")
        print(f"Total tokens: {usage.total_token_count}")

    print("\nConnection successful!")


if __name__ == "__main__":
    test_connection()
