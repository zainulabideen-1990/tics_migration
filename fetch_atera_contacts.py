import requests
import json
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://app.atera.com/api/v3/contacts"
API_KEY = os.getenv("ATERA_API_KEY")

log_folder = 'log_info'
log_file = os.path.join(log_folder, 'fetch_atera_contacts.log')
os.makedirs(log_folder, exist_ok=True)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fetch_contacts(max_retries=3):
    all_contacts = []
    retries = 0
    next_page_url = BASE_URL  # Start with the base URL for the first page

    headers = {
        'X-API-KEY': API_KEY,  # Use X-API-KEY instead of Authorization
        'Accept': 'application/json'
    }

    while next_page_url:
        try:
            logging.info(f"Fetching contacts from {next_page_url}")
            response = requests.get(next_page_url, headers=headers)
            response.raise_for_status()  # Raise exception for HTTP errors

            data = response.json()
            all_contacts.extend(data.get("items", []))

            next_page_url = data.get("nextLink")

        except requests.exceptions.Timeout:
            logging.warning(f"Timeout occurred. Retrying... ({retries + 1}/{max_retries})")
            retries += 1
            if retries >= max_retries:
                logging.error("Max retries reached!")
                break
            time.sleep(10 * retries)  # Exponential backoff

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Response status code: {e.response.status_code}")
                logging.error(f"Response body: {e.response.text}")
            break

    logging.info(f"Total contacts fetched: {len(all_contacts)}")
    return all_contacts

def save_contacts_to_file(contacts, filename=os.path.join("json_files", "atera_contacts.json")):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, "w") as f:
        json.dump(contacts, f, indent=4)
    logging.info(f"Data saved to '{filename}'.")

def handler():
    logging.info("Starting the fetch process for contacts...")
    contacts = fetch_contacts()
    if contacts:
        save_contacts_to_file(contacts)
    else:
        logging.warning("No contacts were fetched.")

if __name__ == "__main__":
    handler()
