import requests
import json
import time
import os
import logging
from dotenv import load_dotenv

load_dotenv()

log_folder = 'log_info'
log_file = os.path.join(log_folder, 'fetch_resources.log')

os.makedirs(log_folder, exist_ok=True)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

BASE_URL = "https://webservices14.autotask.net/ATServicesRest/V1.0/Resources/query"
HEADERS = {
    "ApiIntegrationCode": os.getenv("API_INTEGERATION_CODE"),
    "UserName": os.getenv("USER_NAME"),
    "Secret": os.getenv("SECRET")
}

def fetch_resources(is_active, max_retries=3):
    all_resources = []
    request_count = 0
    next_page_url = None
    retries = 0

    search_payload = {
        "filter": [{"op": "eq", "field": "isActive", "value": is_active}]
    }

    while True:
        url = next_page_url if next_page_url else BASE_URL
        params = {'search': json.dumps(search_payload)} if not next_page_url else {}

        try:
            logging.info(f"Fetching resources for isActive {is_active} from {url}...")
            response = requests.get(url, headers=HEADERS, params=params, timeout=60)  # Increased timeout to 60 seconds
            request_count += 1
            logging.info(f"Request count for isActive {is_active}: {request_count}")
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx, 5xx)

            data = response.json()
            all_resources.extend(data.get("items", []))

            next_page_url = data.get("pageDetails", {}).get("nextPageUrl")
            if not next_page_url:
                logging.info(f"No more pages for isActive {is_active}.")
                break

        except requests.exceptions.Timeout:
            logging.warning(f"Timeout occurred for isActive {is_active}. Retrying... ({retries+1}/{max_retries})")
            retries += 1
            if retries >= max_retries:
                logging.error(f"Max retries reached for isActive {is_active}. Skipping this isActive value.")
                break
            time.sleep(10 * retries)  # Exponential backoff

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for isActive {is_active}: {str(e)}. Skipping this isActive value.")
            break

    logging.info(f"Total resources fetched for isActive {is_active}: {len(all_resources)}")
    return all_resources

def handler():
    all_resources = []

    for is_active in [0, 1]:
        logging.info(f"Fetching resources for isActive {is_active}...")
        resources = fetch_resources(is_active)
        all_resources.extend(resources)
        logging.info(f"Fetched {len(resources)} resources for isActive {is_active}.")

    result_file = os.path.join("json_files", "all_resources.json")
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    
    with open(result_file, "w") as f:
        json.dump(all_resources, f, indent=4)

    logging.info(f"Total resources fetched: {len(all_resources)}")
    logging.info(f"Data saved to '{result_file}'.")

if __name__ == "__main__":
    handler()
