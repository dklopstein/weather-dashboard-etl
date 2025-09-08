import os
import requests
import json
import boto3
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get variables from environment
API_KEY = os.getenv("API_KEY")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

URL = f"https://api.tomorrow.io/v4/weather/forecast?location=93312%20US&timesteps=1h&units=imperial&apikey={API_KEY}"


def fetch_weather_data(api_url, headers):
    """Fetch weather data from API."""

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch weather data from {api_url}: {e}")
        raise


def flatten_convert_json(json_data):
    """Flatten and convert JSON file into a Parquet for uploading."""

    # Extract the hourly data and flatten it
    hourly_data = json_data["timelines"]["hourly"]
    location_data = json_data["location"]

    # Flatten the nested structure
    df = pd.json_normalize(hourly_data)

    # Convert time to PST for better readability
    df["time"] = pd.to_datetime(df["time"], utc=True).dt.tz_convert(
        "America/Los_Angeles"
    )

    # Rename coloumns
    column_names = {}
    for col in df.columns:
        if col[:7] == "values.":
            column_names[col] = col[7:]

    df = df.rename(columns=column_names)

    # Add location data to each row
    for k, v in location_data.items():
        df[k] = v

    return df.to_parquet()


# Run if script is executed
if __name__ == "__main__":
    headers = {"accept": "application/json", "accept-encoding": "deflate, gzip, br"}
    json_data = fetch_weather_data(URL, headers)

    df = flatten_convert_json(json_data)
    print(df)
