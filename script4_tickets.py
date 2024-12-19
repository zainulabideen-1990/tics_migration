import requests
import json
import time
import logging
import os
from requests.exceptions import RequestException
from dotenv import load_dotenv

load_dotenv()

# Constants
ATERA_API_URL = "https://app.atera.com/api/v3/tickets"
ATERA_API_COMMENT_URL = "https://app.atera.com/api/v3/tickets/{id}/comments"
API_KEY = os.getenv("ATERA_API_KEY")
RESULT_FILE = os.path.join("json_files", "result3.json")
RETRY_LIMIT = 3
DELAY_SECONDS = 5

# Set up logging
logging.basicConfig(filename='error_log.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
success_logger = logging.getLogger('success_logger')
success_handler = logging.FileHandler('success_log.log')
success_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
success_logger.addHandler(success_handler)

# Helper Functions
def post_ticket(ticket_data):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(ATERA_API_URL, headers=headers, json=ticket_data)
        response.raise_for_status()

        response_data = response.json()
        ticket_id = response_data.get("id")
        if not ticket_id:
            raise ValueError("Ticket ID not found in the response")

        success_logger.info(f"Successfully posted ticket: {ticket_data['TicketTitle']} | Ticket ID: {ticket_id}")
        print(f"Successfully posted ticket: {ticket_data['TicketTitle']} | Ticket ID: {ticket_id}")

        return ticket_id

    except RequestException as e:
        logging.error(f"Error posting ticket {ticket_data['TicketTitle']} | Error: {e}")
        return None

def post_comment(ticket_id, comment):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    url = ATERA_API_COMMENT_URL.format(id=ticket_id)

    try:
        response = requests.post(url, headers=headers, json=comment)
        response.raise_for_status()

        success_logger.info(f"Successfully posted comment to ticket {ticket_id}: {comment['Text']}")
        print(f"Successfully posted comment to ticket {ticket_id}: {comment['Text']}")

    except RequestException as e:
        logging.error(f"Error posting comment to ticket {ticket_id} | Error: {e}")

def post_tickets_from_json():
    try:
        with open(RESULT_FILE, 'r') as file:
            tickets = json.load(file)

        for ticket in tickets:
            success = False
            retries = 0

            while retries < RETRY_LIMIT and not success:
                ticket_id = post_ticket(ticket)
                success = bool(ticket_id)

                if not success:
                    retries += 1
                    print(f"Retrying... ({retries}/{RETRY_LIMIT})")
                    time.sleep(DELAY_SECONDS)

            if success:
                # Post comments if available
                comments = ticket.get('comments', [])
                for comment in comments:
                    post_comment(ticket_id, comment)

            else:
                logging.error(f"Failed to post ticket after {RETRY_LIMIT} attempts: {ticket['TicketTitle']}")

    except Exception as e:
        logging.error(f"Error reading the file {RESULT_FILE}: {e}")

if __name__ == "__main__":
    post_tickets_from_json()
