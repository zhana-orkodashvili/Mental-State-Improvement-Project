import os
import json
import requests
import logging
from utils import load_env_vars

# Load environment variables
load_env_vars()

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TEAMS_WEBHOOK_URL = os.getenv('TEAMS_WEBHOOK_URL')

def create_payload(image_url, image_description, quote, author):
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.hero",
                "content": {
                    "title": "Daily Inspiration from Zhana Orkodashvili",
                    "text": f"'{quote}' - {author}",
                    "images": [
                        {
                            "url": image_url,
                            "alt": image_description
                        }
                    ]
                }
            }
        ]
    }
    logger.debug(f"Created payload: {json.dumps(payload, indent=4)}")
    return payload

def send_to_teams(payload):
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(TEAMS_WEBHOOK_URL, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        logger.info("Message sent successfully!")
    else:
        logger.error(f"Failed to send message. Status code: {response.status_code}")
    return response.status_code

