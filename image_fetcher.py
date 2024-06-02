import os
import requests
import json
import logging
from utils import load_env_vars

# Load environment variables
load_env_vars()

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

def get_random_image():
    url = f'https://api.unsplash.com/photos/random?client_id={UNSPLASH_ACCESS_KEY}'
    response = requests.get(url)

    if response.status_code != 200:
        logger.error(f"Error fetching image: {response.status_code}")
        logger.error(response.text)
        return None, None

    try:
        data = response.json()
        if 'urls' in data and 'regular' in data['urls'] and 'alt_description' in data:
            logger.info("Image fetched successfully")
            return data['urls']['regular'], data['alt_description']
        else:
            logger.error("Unexpected response format from Unsplash:")
            logger.error(json.dumps(data, indent=4))
            return None, None
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON response:")
        logger.error(e)
        return None, None
