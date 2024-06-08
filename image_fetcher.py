from os import getenv
from requests import get
from json import dumps, JSONDecodeError
from logging import getLogger, INFO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = getLogger(__name__)
logger.setLevel(INFO)

UNSPLASH_ACCESS_KEY = getenv("UNSPLASH_ACCESS_KEY")

def get_random_image():
    """
    Fetches a random image from Unsplash.

    Returns:
        tuple: A tuple containing the URL of the image and its description.
               Returns (None, None) if there's an error or unexpected response.
    """
    url = f"https://api.unsplash.com/photos/random?client_id={UNSPLASH_ACCESS_KEY}"
    response = get(url)

    if response.status_code != 200:
        logger.error(f"Error fetching image: {response.status_code}")
        logger.error(response.text)
        return None, None

    try:
        data = response.json()

        # Check if the expected keys exist in the response
        if "urls" in data and "regular" in data["urls"]:
            image_url = data["urls"]["regular"]
        else:
            logger.error("Image URL not found in response:")
            logger.error(dumps(data, indent=4))
            return None, None

        if "alt_description" in data:
            image_description = data["alt_description"]
        else:
            logger.error("Image description not found in response:")
            logger.error(dumps(data, indent=4))
            return None, None

        logger.info("Image fetched successfully")
        return image_url, image_description

    except JSONDecodeError as e:
        logger.error("Failed to parse JSON response:")
        logger.error(e)
        return None, None
