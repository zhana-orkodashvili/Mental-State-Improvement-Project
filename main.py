import logging
from image_fetcher import get_random_image
from quote_fetcher import get_random_quote
from teams_notifier import create_payload, send_to_teams

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Starting the process to fetch image and quote and send to Teams.")

    image_url, image_description = get_random_image()
    if not image_url or not image_description:
        logging.error("Failed to fetch a valid image.")
        return

    logging.info(f"Fetched image: {image_url} with description: {image_description}")

    quote, author = get_random_quote()
    if not quote or not author:
        logging.error("Failed to fetch a valid quote.")
        return

    logging.info(f"Fetched quote: '{quote}' by {author}")

    payload = create_payload(image_url, image_description, quote, author)

    # Sending to Teams channel
    send_to_teams(payload)

if __name__ == "__main__":
    main()
