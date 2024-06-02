import requests
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

QUOTABLE_API_URL = 'https://api.quotable.io/random'

def get_random_quote():
    response = requests.get(QUOTABLE_API_URL)
    if response.status_code != 200:
        logger.error(f"Error fetching quote: {response.status_code}")
        logger.error(response.text)
        return None, None

    try:
        data = response.json()
        if 'content' in data and 'author' in data:
            logger.info("Quote fetched successfully")
            return data['content'], data['author']
        else:
            logger.error("Unexpected response format from Quotable:")
            logger.error(json.dumps(data, indent=4))
            return None, None
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON response:")
        logger.error(e)
        return None, None
