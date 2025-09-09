import os
import re
import boto3
import requests
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv
from datetime import date, datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Get variables from environment
API_KEY = os.getenv("API_KEY")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

URL = f"https://api.tomorrow.io/v4/weather/forecast?location=93312%20US&timesteps=1h&units=imperial&apikey={API_KEY}"

# Create S3 Client
s3_client = boto3.client(
    service_name="s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)


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

    # Create PST time column to filter data to single day
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df["time_pst"] = df["time"].dt.tz_convert("America/Los_Angeles")

    # Filter data to only get current day
    target_day = datetime.now().date()
    next_day = target_day + timedelta(days=1)
    df = df[
        (df["time_pst"].dt.date == target_day)
        | ((df["time_pst"].dt.date == next_day) & (df["time_pst"].dt.hour == 0))
    ]

    # Drop PST column to help with conversion in Athena
    df = df.drop(columns=["time_pst"])

    # Rename coloumns
    column_names = {"time": "time_unix"}
    for col in df.columns:
        new_name = col
        if col[:7] == "values.":
            new_name = col[7:]

        # Regex to convert camel case to snake case
        new_name = re.sub(r"(?<!^)(?=[A-Z])", "_", new_name).lower()
        column_names[col] = new_name

    df = df.rename(columns=column_names)

    # Split location data and add it to each row
    city, county, state, postal_code, country = location_data["name"].split(", ")
    df["city"] = city
    df["county"] = county
    df["state"] = state
    df["postal_code"] = postal_code
    df["country"] = country
    df["lat"] = location_data["lat"]
    df["lon"] = location_data["lon"]

    # Create buffer to save parquet to memory
    buffer = BytesIO()
    df.to_parquet(buffer, engine="pyarrow", index=False, compression="snappy")

    # Change stream position to start
    buffer.seek(0)

    return buffer


def upload_to_s3_bucket(buffer, file_name):
    """Uploads JSON data to S3 bucket."""

    try:
        s3_client.upload_fileobj(
            buffer, Bucket=AWS_S3_BUCKET_NAME, Key=f"raw/{file_name}.parquet"
        )

        return True
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False


# Run if script is executed
if __name__ == "__main__":
    headers = {"accept": "application/json", "accept-encoding": "deflate, gzip, br"}
    json_data = fetch_weather_data(URL, headers)
    buffer = flatten_convert_json(json_data)
    # file_name = formatted_date = date.today().strftime("%m-%d-%Y")
    # print(formatted_date)
    # response = upload_to_s3_bucket(buffer, file_name)
    # print(response)
