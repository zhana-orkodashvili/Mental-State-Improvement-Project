from os import getenv
from requests import post
from json import dumps
from logging import getLogger, INFO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = getLogger(__name__)
logger.setLevel(INFO)

TEAMS_WEBHOOK_URL = getenv('TEAMS_WEBHOOK_URL')

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
    logger.debug(f"Created payload: {dumps(payload, indent=4)}")
    return payload

def send_to_teams(payload):
    headers = {
        'Content-Type': 'application/json'
    }
    response = post(TEAMS_WEBHOOK_URL, headers=headers, data=dumps(payload))
    if response.status_code == 200:
        logger.info("Message sent successfully!")
    else:
        logger.error(f"Failed to send message. Status code: {response.status_code}")
    return response.status_code

