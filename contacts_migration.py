import os
import requests
import json
import time
import logging
from dotenv import load_dotenv

load_dotenv()

LOG_FOLDER = 'log_info'
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

logging.basicConfig(
    filename=os.path.join(LOG_FOLDER, 'contacts_migration.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

BASE_URL = "https://webservices14.autotask.net/ATServicesRest/V1.0/Contacts/query"
ATERA_API_URL = 'https://app.atera.com/api/v3/contacts'
HEADERS = {
    "ApiIntegrationCode": os.getenv("API_INTEGERATION_CODE"),
    "UserName": os.getenv("USER_NAME"),
    "Secret": os.getenv("SECRET")
}

ATERA_API_TOKEN = os.getenv("ATERA_API_KEY")

error_log = []

def post_to_atera(contact):
    """Uploads a single contact to Atera and logs any errors."""
    headers = {
        'X-API-KEY': ATERA_API_TOKEN,
        'Accept': 'application/json'
    }
    
    atera_contact = {
        "Email": contact.get("emailAddress"),
        "Firstname": contact.get("firstName"),
        "Lastname": contact.get("lastName"),
        "JobTitle": contact.get("title"),
        "Phone": contact.get("phone"),
        "MobilePhone": contact.get("mobilePhone"),
        "IsContactPerson": contact.get("primaryContact", False),
        "CreatedOn": contact.get("createDate"),
    }

    try:
        response = requests.post(ATERA_API_URL, headers=headers, json=atera_contact, timeout=60)
        response.raise_for_status()
        logging.info(f"Contact {contact.get('emailAddress')} uploaded successfully to Atera.")
    except requests.exceptions.RequestException as e:
        error_message = f"Failed to upload contact {contact.get('emailAddress')}: {str(e)}"
        logging.error(error_message)

        error_log.append({
            "contact_email": contact.get('emailAddress'),
            "contact_id": contact.get('id'),
            "error_message": str(e)
        })

def fetch_contacts(value, max_retries=3):
    all_contacts = []
    request_count = 0
    next_page_url = None
    retries = 0

    search_payload = {
        "filter": [{"op": "eq", "field": "isActive", "value": value}]
    }

    while True:
        url = next_page_url if next_page_url else BASE_URL
        params = {'search': json.dumps(search_payload)} if not next_page_url else {}

        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=60)
            request_count += 1
            logging.info(f"Request {request_count}: Sending request to {url} with params {params}.")
            response.raise_for_status()

            data = response.json()
            all_contacts.extend(data.get("items", []))

            for contact in data.get("items", []):
                post_to_atera(contact)

            next_page_url = data.get("pageDetails", {}).get("nextPageUrl")
            if not next_page_url:
                break

        except requests.exceptions.Timeout:
            retries += 1
            logging.warning(f"Timeout occurred for active status {value}. Retrying... ({retries}/{max_retries})")
            if retries >= max_retries:
                logging.error(f"Max retries reached for active status {value}. Skipping this active status.")
                break
            time.sleep(10 * retries)

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for active status {value}: {str(e)}. Skipping this active status.")
            break

    return all_contacts

def fetch_all_contacts():
    all_contacts = []

    for isActive in range(0, 2):
        logging.info(f"Fetching contacts for active status {isActive}...")
        contacts = fetch_contacts(isActive)
        all_contacts.extend(contacts)

    # Save all contacts to all_contacts.json
    try:
        with open(os.path.join("json_files", 'all_contacts.json'), "w") as contacts_file:
            json.dump(all_contacts, contacts_file, indent=4)
        logging.info("All contacts saved to 'all_contacts.json'.")
    except Exception as e:
        logging.error(f"Failed to save contacts to 'all_contacts.json': {str(e)}")

    if error_log:
        try:
            with open("error_log.json", "w") as error_file:
                json.dump(error_log, error_file, indent=4)
            logging.info("Errors logged in 'error_log.json'.")
        except Exception as e:
            logging.error(f"Failed to save error log: {str(e)}")
    else:
        logging.info("No errors occurred during the upload process.")

if __name__ == "__main__":
    logging.info("Starting the contact fetch process.")
    fetch_all_contacts()
    logging.info("Process completed.")