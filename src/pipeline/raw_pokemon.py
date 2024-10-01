import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import boto3
from loguru import logger
import json
from tqdm import tqdm
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from resources.s3_manager import create_s3_client


def get_data(base_url: str, params: dict) -> dict:
    
    # Make an initial request to get the total number of Pokemon
    response = requests.get(base_url, params=params)
    data = response.json()
    total_count = data['count']  # total number of Pokemon available
    all_data = []

    # Use tqdm to display the progress
    with tqdm(total=total_count, desc="Fetching Pokémon data") as pbar:
        while True:
            # Add current page's results to the list
            all_data.extend(data['results'])
            
            # Update the progress bar
            pbar.update(len(data['results']))

            # Check if there's a next page
            if data['next']:
                # Get the next URL and fetch the next page
                next_url = data['next']
                params['offset'] = int(next_url.split('offset=')[1].split('&')[0])
                response = requests.get(base_url, params=params)
                data = response.json()
            else:
                break

    return all_data


def save_data(data: dict, s3_client: boto3.client, bucket: str) -> None:
    try:
        logger.info(f"Saving data to S3 bucket")
        now = datetime.now().strftime("%Y%m%d_%H%M%S")

        json_bytes = json.dumps(data).encode("utf-8")

        s3_client.put_object(
            Bucket=bucket,
            Key=f"pokemons_raw/pokemons_list/{now}.json",
            Body=json_bytes,
        )

        logger.success(f"Data saved to S3 bucket")
    except Exception as e:
        logger.error(f"Error saving data to S3 bucket: {e}")


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get the S3 credentials and bucket name
    access_key = os.getenv("ACCESS_KEY")
    secret_key = os.getenv("SECRET_KEY")
    bucket = os.getenv("RAW_BUCKET")

    # Define the S3 endpoint URL
    s3_endpoint_url = "http://s3service:9000"

    # Define the base URL and query parameters
    base_url = "https://pokeapi.co/api/v2/pokemon/"
    params = {'limit': 100, 'offset': 0}

    # Create an S3 client
    s3_conn = create_s3_client(access_key, secret_key, s3_endpoint_url)
    
    # Get the data
    data = get_data(base_url, params)
    
    # Save the data to S3
    save_data(data, s3_conn, bucket)