import logging
import requests
from time import sleep

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

RETRY_LIMIT = 3  # Number of retries for failed requests
RETRY_DELAY = 5  # Delay between retries in seconds

def fetch_page(page_token=None, page_size=1000):
    """
    Fetch a page of results from the ClinicalTrials.gov API.
    Args:
        page_token (str): Token for the next page of studies.
        page_size (int): Number of studies to fetch in this request (max 1000).
    Returns:
        Tuple[List[dict], str]: A tuple containing a list of studies and the next page token.
    """
    params = {
        "query.term": "NSCLC",
        "pageToken": page_token,
        "pageSize": page_size,
        "format": "json"  # JSON format for response
    }
    logging.info(f"Fetching studies with page token: {page_token} and page size: {page_size}")
    for attempt in range(RETRY_LIMIT):
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            studies = data.get("studies", [])
            next_page_token = data.get("nextPageToken")
            return studies, next_page_token
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < RETRY_LIMIT - 1:
                sleep(RETRY_DELAY)
            else:
                logging.error("Max retry limit reached. Unable to fetch data.")
                raise

def ingest_data(batch_size=1000):
    """
    Fetch all results from the ClinicalTrials.gov API using pagination.
    Args:
        batch_size (int): Number of results to fetch per request (max 1000).
    Returns:
        List[dict]: All fetched study data.
    """
    all_studies = []
    page_token = None
    try:
        while True:
            studies, next_page_token = fetch_page(page_token, batch_size)
            if not studies:  # Break if no more studies are returned
                logging.info("No more results to fetch. Ingestion complete.")
                break
            all_studies.extend(studies)
            logging.info(f"Fetched {len(studies)} studies in this batch. Total so far: {len(all_studies)}.")
            page_token = next_page_token  # Use the nextPageToken for the next iteration
            if not page_token:  # No more pages
                break
    except Exception as e:
        logging.error(f"Ingestion failed: {e}", exc_info=True)
        raise

    logging.info(f"Fetched a total of {len(all_studies)} studies.")
    return all_studies
