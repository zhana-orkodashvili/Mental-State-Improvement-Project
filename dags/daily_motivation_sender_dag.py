from pendulum import today
from requests import get, post
from json import dumps, JSONDecodeError
from logging import error, info, debug
from os import getenv
from airflow import DAG
from airflow.operators.python import PythonOperator
from dotenv import load_dotenv

load_dotenv()


def get_random_image(**kwargs):
    """
    Fetches a random image from Unsplash.

    Returns:
        dict: A dictionary containing the URL of the image and its description.
              Returns None if there's an error or unexpected response.
    """
    UNSPLASH_ACCESS_KEY = getenv("UNSPLASH_ACCESS_KEY")
    url = f"https://api.unsplash.com/photos/random?client_id={UNSPLASH_ACCESS_KEY}"
    response = get(url)

    if response.status_code != 200:
        error(f"Error fetching image: {response.status_code}")
        error(response.text)
        return None

    try:
        data = response.json()

        image_url = data.get("urls", {}).get("regular")
        if not image_url:
            error("Image URL not found in response:")
            error(dumps(data, indent=4))
            return None

        image_description = data.get("alt_description")
        if not image_description:
            error("Image description not found in response:")
            error(dumps(data, indent=4))
            return None

        info("Image fetched successfully")
        return {"image_url": image_url, "image_description": image_description}

    except JSONDecodeError as e:
        error("Failed to parse JSON response:")
        error(e)
        return None


def get_random_quote(**kwargs):
    """
    Fetches a random quote from Quotable.

    Returns:
        dict: A dictionary containing the quote content and author.
              Returns None if there's an error or unexpected response.
    """
    QUOTABLE_API_URL = 'https://api.quotable.io/random'
    response = get(QUOTABLE_API_URL)
    if response.status_code != 200:
        error(f"Error fetching quote: {response.status_code}")
        error(response.text)
        return None

    try:
        data = response.json()
        quote_content = data.get("content")
        if not quote_content:
            error("Quote content not found in response:")
            error(dumps(data, indent=4))
            return None

        author = data.get("author")
        if not author:
            error("Quote author not found in response:")
            error(dumps(data, indent=4))
            return None

        info("Quote fetched successfully")
        return {"quote_content": quote_content, "author": author}
    except JSONDecodeError as e:
        error("Failed to parse JSON response:")
        error(e)
        return None


def create_payload(ti):
    """
    Creates the payload for the Microsoft Teams message.

    Args:
        ti (TaskInstance): Airflow's TaskInstance object to pull XCom values.

    Returns:
        dict: The payload to send to Microsoft Teams.
    """
    image_data = ti.xcom_pull(task_ids='get_random_image')
    quote_data = ti.xcom_pull(task_ids='get_random_quote')

    if not image_data or not quote_data:
        error("Failed to retrieve image or quote data from XCom.")
        return None

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


def send_to_teams(ti):
    """
    Sends the payload to the Microsoft Teams channel.

    Args:
        ti (TaskInstance): Airflow's TaskInstance object to pull XCom values.

    Returns:
        int: The status code of the response.
    """
    payload = ti.xcom_pull(task_ids='create_payload')
    if not payload:
        error("Failed to retrieve payload from XCom.")
        return 500

    TEAMS_WEBHOOK_URL = getenv("TEAMS_WEBHOOK_URL")
    headers = {
        'Content-Type': 'application/json'
    }
    response = post(TEAMS_WEBHOOK_URL, headers=headers, data=dumps(payload))
    if response.status_code == 200:
        info("Message sent successfully!")
    else:
        error(f"Failed to send message. Status code: {response.status_code}")
    return response.status_code


with DAG(
        dag_id='daily_notification_dag',
        start_date=today(),
        schedule_interval=None,
        tags=['notification', 'quote', 'image'],
        description='A DAG to send daily notifications with inspiring quotes and images',
        catchup=False

) as dag:
    get_image_task = PythonOperator(
        task_id='get_random_image',
        python_callable=get_random_image,
    )

    get_quote_task = PythonOperator(
        task_id='get_random_quote',
        python_callable=get_random_quote,
    )

    create_payload_task = PythonOperator(
        task_id='create_payload',
        python_callable=create_payload,
    )

    send_notification_task = PythonOperator(
        task_id='send_to_teams',
        python_callable=send_to_teams,
    )

    get_image_task >> get_quote_task >> create_payload_task >> send_notification_task
