import requests
import json
import time
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Set up logging
log_folder = 'log_info'
log_file = os.path.join(log_folder, 'log1.log')

# Create log folder if it doesn't exist
os.makedirs(log_folder, exist_ok=True)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

BASE_URL = "https://webservices14.autotask.net/ATServicesRest/V1.0/Tickets/query"
HEADERS = {
    "ApiIntegrationCode": os.getenv("API_INTEGERATION_CODE"),
    "UserName": os.getenv("USER_NAME"),
    "Secret": os.getenv("SECRET")
}

def fetch_tickets(priority, max_retries=3):
    all_tickets = []
    request_count = 0
    next_page_url = None
    retries = 0

    search_payload = {
        "filter": [{"op": "eq", "field": "priority", "value": priority}]
    }

    while True:
        url = next_page_url if next_page_url else BASE_URL
        params = {'search': json.dumps(search_payload)} if not next_page_url else {}

        try:
            logging.info(f"Fetching tickets for priority {priority} from {url}...")
            response = requests.get(url, headers=HEADERS, params=params, timeout=60)  # Increased timeout to 60 seconds
            request_count += 1
            logging.info(f"Request count for priority {priority}: {request_count}")
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx, 5xx)

            data = response.json()
            all_tickets.extend(data.get("items", []))

            next_page_url = data.get("pageDetails", {}).get("nextPageUrl")
            if not next_page_url:
                logging.info(f"No more pages for priority {priority}.")
                break

        except requests.exceptions.Timeout:
            logging.warning(f"Timeout occurred for priority {priority}. Retrying... ({retries+1}/{max_retries})")
            retries += 1
            if retries >= max_retries:
                logging.error(f"Max retries reached for priority {priority}. Skipping this priority.")
                break
            time.sleep(10 * retries)  # Exponential backoff

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for priority {priority}: {str(e)}. Skipping this priority.")
            break

    logging.info(f"Total tickets fetched for priority {priority}: {len(all_tickets)}")
    return all_tickets

def handler():
    all_tickets = []

    for priority in range(1, 5):
        logging.info(f"Fetching tickets for priority {priority}...")
        tickets = fetch_tickets(priority)
        all_tickets.extend(tickets)
        logging.info(f"Fetched {len(tickets)} tickets for priority {priority}.")

    result_file = os.path.join("json_files", "result1.json")
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    
    with open(result_file, "w") as f:
        json.dump(all_tickets, f, indent=4)

    logging.info(f"Total tickets fetched: {len(all_tickets)}")
    logging.info(f"Data saved to '{result_file}'.")

if __name__ == "__main__":
    handler()
