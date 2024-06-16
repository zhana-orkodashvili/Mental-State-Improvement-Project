from dotenv import load_dotenv
from requests import HTTPError, get
from airflow.exceptions import AirflowException

load_dotenv()


def get_random_quote(**kwargs):
    """
    Fetches a random quote from Quotable.

    Returns:
        dict: A dictionary containing the quote content and author.
    """
    QUOTABLE_API_URL = 'https://api.quotable.io/random'
    try:
        response = get(QUOTABLE_API_URL)
        response.raise_for_status()
    except HTTPError as http_err:
        raise AirflowException(f"HTTP error occurred: {http_err}")
    except Exception as err:
        raise AirflowException(f"Error occurred: {err}")

    try:
        data = response.json()
        quote_content = data.get("content")
        if not quote_content:
            raise AirflowException("Quote content not found in response")

        author = data.get("author")
        if not author:
            raise AirflowException("Quote author not found in response")

        return {"quote_content": quote_content, "author": author}
    except ValueError as value_err:
        raise AirflowException(f"Failed to parse JSON response: {value_err}")
