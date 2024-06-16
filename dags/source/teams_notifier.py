from os import getenv
from json import dumps
from logging import info, debug

from requests import post
from airflow.exceptions import AirflowException
from dotenv import load_dotenv

load_dotenv()


def create_payload(ti):
    """
    Creates the payload for the Microsoft Teams message.

    Args:
        ti (TaskInstance): Airflow's TaskInstance object to pull XCom values.

    Returns:
        dict: The payload to send to Microsoft Teams.
    """
    try:
        image_data = ti.xcom_pull(task_ids='get_random_image')
        quote_data = ti.xcom_pull(task_ids='get_random_quote')

        if not image_data or not quote_data:
            raise AirflowException("Failed to retrieve image or quote data from XCom.")

        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.hero",
                    "content": {
                        "title": "Daily Inspiration from Zhana Orkodashvili",
                        "text": f"{quote_data['quote_content']} \n\n- {quote_data['author']}",
                        "images": [
                            {
                                "url": image_data["image_url"],
                                "alt": image_data["image_description"]
                            }
                        ]
                    }
                }
            ]
        }
        debug(f"Created payload: {dumps(payload, indent=4)}")
        return payload
    except Exception as e:
        raise AirflowException(f"Error creating payload: {e}")


def send_to_teams(ti):
    """
    Sends the payload to the Microsoft Teams channel.

    Args:
        ti (TaskInstance): Airflow's TaskInstance object to pull XCom values.

    Returns:
        int: The status code of the response.
    """
    try:
        payload = ti.xcom_pull(task_ids='create_payload')

        if not payload:
            raise AirflowException("Failed to retrieve payload from XCom.")

        TEAMS_WEBHOOK_URL = getenv("TEAMS_WEBHOOK_URL")
        headers = {
            'Content-Type': 'application/json'
        }
        response = post(TEAMS_WEBHOOK_URL, headers=headers, data=dumps(payload))
        if response.status_code == 200:
            info("Message sent successfully!")
        else:
            raise AirflowException(f"Failed to send message. Status code: {response.status_code}")

        return response.status_code
    except Exception as e:
        raise AirflowException(f"Error sending message to Teams: {e}")
