import json
import requests
from requests.auth import HTTPBasicAuth
import os
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

load_dotenv()

log_folder = 'log_info'
log_file = os.path.join(log_folder, 'log2.log')

os.makedirs(log_folder, exist_ok=True)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

API_URL = "https://webservices14.autotask.net/ATServicesRest/V1.0/TicketNotes/query"
API_INTEGRATION_CODE = os.getenv("API_INTEGERATION_CODE")
USER_NAME = os.getenv("USER_NAME")
SECRET = os.getenv("SECRET")

@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=60))
def get_ticket_notes(ticket_id):
    search_payload = {
        "filter": [
            {
                "op": "eq",
                "field": "ticketID",
                "value": ticket_id
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "ApiIntegrationCode": API_INTEGRATION_CODE,
        "UserName": USER_NAME,
        "Secret": SECRET
    }

    try:
        logging.info(f"Sending request for ticket ID {ticket_id}")
        logging.info(f"Request Payload: {search_payload}")
        response = requests.post(API_URL, json=search_payload, headers=headers, auth=HTTPBasicAuth(USER_NAME, SECRET), timeout=30)
        
        logging.info(f"Response Status Code: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("items", [])
        else:
            logging.error(f"Error fetching notes for ticket {ticket_id}: {response.status_code}")
            logging.error(f"Response Body: {response.text}")
            return []

    except requests.exceptions.Timeout as e:
        logging.error(f"Timeout error for ticket {ticket_id}: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error for ticket {ticket_id}: {e}")
        raise

def process_tickets(input_file, output_file):
    count = 0
    with open(input_file, "r") as f:
        all_tickets = json.load(f)

    for ticket in all_tickets:
        count += 1
        logging.info(f"Tickets Processed: {count}")
        ticket_id = ticket.get("id")
        if ticket_id:
            ticket_notes = get_ticket_notes(ticket_id)
            ticket["notes"] = ticket_notes

        time.sleep(0.5)

    with open(output_file, "w") as f:
        json.dump(all_tickets, f, indent=4)

    logging.info(f"Processed {len(all_tickets)} tickets and saved to {output_file}")

# Entry point
if __name__ == "__main__":
    input_file = os.path.join("json_files", "result1.json")
    output_file = os.path.join("json_files", "result2.json")
    process_tickets(input_file, output_file)
