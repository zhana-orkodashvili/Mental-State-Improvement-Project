from os import getenv
from json import dumps, JSONDecodeError
from logging import error, info

from requests import get
from airflow.exceptions import AirflowException
from airflow.models import Variable
from dotenv import load_dotenv

load_dotenv()


def get_random_image(**kwargs):
    """
    Fetches a random image from Unsplash.

    Returns:
        dict: A dictionary containing the URL of the image and its description.
    """
    UNSPLASH_ACCESS_KEY = getenv("UNSPLASH_ACCESS_KEY")
    unsplash_base_url = Variable.get("unsplash_base_url")
    url = f"{unsplash_base_url}{UNSPLASH_ACCESS_KEY}"
    response = get(url)

    if response.status_code != 200:
        error(f"Error fetching image: {response.status_code}")
        error(response.text)
        raise AirflowException(f"Error fetching image: {response.status_code}")

    try:
        data = response.json()

        image_url = data.get("urls", {}).get("regular")
        if not image_url:
            error("Image URL not found in response:")
            error(dumps(data, indent=4))
            raise AirflowException("Image URL not found in response")

        image_description = data.get("alt_description")
        if not image_description:
            error("Image description not found in response:")
            error(dumps(data, indent=4))
            raise AirflowException("Image description not found in response")

        info("Image fetched successfully")
        return {"image_url": image_url, "image_description": image_description}

    except JSONDecodeError as e:
        error("Failed to parse JSON response:")
        error(e)
        raise AirflowException("Failed to parse JSON response")
