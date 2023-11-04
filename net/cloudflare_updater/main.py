# scripts/net/cloudflare_updater/main.py
import logging
import os
from typing import Any, Dict, Optional

import backoff
import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the directory where the script is located
script_directory = os.path.dirname(os.path.realpath(__file__))

# Construct the path to the .env file
env_path = os.path.join(script_directory, 'cloudflare.env')

# Load the .env file using its full path
load_dotenv(env_path)

# Read configuration from environment variables
API_TOKEN: Optional[str] = os.getenv('CLOUDFLARE_API_TOKEN')
ZONE_ID: Optional[str] = os.getenv('CLOUDFLARE_ZONE_ID')
RECORD_ID: Optional[str] = os.getenv('CLOUDFLARE_RECORD_ID')
DOMAIN: Optional[str] = os.getenv('CLOUDFLARE_DOMAIN')

class CloudflareAPI:
    """Handles interactions with the Cloudflare API."""

    def __init__(self, api_token: str) -> None:
        """
        Initialize the API with the given token.

        :param api_token: Cloudflare API token
        """
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        })

    @staticmethod
    def _get_url(zone_id: str, record_id: Optional[str] = "") -> str:
        """
        Generates and returns the URL for a given zone and record.

        :param zone_id: Cloudflare zone ID
        :param record_id: Cloudflare DNS record ID
        :return: Constructed URL
        """
        base_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}"
        return f"{base_url}/dns_records/{record_id}" if record_id else base_url

    @backoff.on_exception(backoff.expo, (ConnectionError, Timeout), max_tries=5)
    def get_dns_record(self, zone_id: str, record_id: str) -> Dict[str, Any]:
        """
        Fetches the DNS record for a given zone and record.

        :param zone_id: Cloudflare zone ID
        :param record_id: Cloudflare DNS record ID
        :return: DNS record data
        """
        url = self._get_url(zone_id, record_id)
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    @backoff.on_exception(backoff.expo, (ConnectionError, Timeout), max_tries=5)
    def update_dns_record(self, zone_id: str, record_id: str, ip: str) -> Dict[str, Any]:
        """
        Updates the DNS record for a given zone and record with a new IP.

        :param zone_id: Cloudflare zone ID
        :param record_id: Cloudflare DNS record ID
        :param ip: New IP address to update
        :return: Response from the API after updating the DNS record
        """
        url = self._get_url(zone_id, record_id)
        data = {
            "type": "A",
            "name": DOMAIN,
            "content": ip,
            "ttl": 120,
            "proxied": False
        }
        response = self.session.put(url, json=data)
        response.raise_for_status()
        return response.json()

def get_wan_ip() -> str:
    """
    Fetches and returns the WAN IP.

    :return: WAN IP address as a string
    """
    response = requests.get('http://ip.42.pl/raw')
    response.raise_for_status()
    return response.text

def main() -> None:
    """
    Main function to get WAN IP and update DNS record on Cloudflare if necessary.
    """
    if API_TOKEN is None or ZONE_ID is None or RECORD_ID is None or DOMAIN is None:
        logger.error("Environment variables not set correctly.")
        return

    cf_api = CloudflareAPI(API_TOKEN)

    try:
        wan_ip = get_wan_ip()
        logger.info(f"Current WAN IP: {wan_ip}")

        dns_record = cf_api.get_dns_record(ZONE_ID, RECORD_ID)
        subdomain_ip = dns_record['result']['content']
        logger.info(f"Current subdomain IP: {subdomain_ip}")

        if wan_ip != subdomain_ip:
            logger.info("The WAN IP and subdomain IP are different. Updating the DNS record...")
            cf_api.update_dns_record(ZONE_ID, RECORD_ID, wan_ip)
            logger.info("DNS record updated.")
        else:
            logger.info("The WAN IP and subdomain IP are the same. No need to update the DNS record.")
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error

if __name__ == '__main__':
    main()
