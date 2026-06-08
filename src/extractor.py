# src/extractor.py
"""
Weather Data Extractor
─────────────────────────────────────────────────────
Connects to Open-Meteo API and fetches weather data
for all configured cities. Saves raw data to S3.
"""

import os
import time
import json
import boto3
import requests
import pandas as pd
from datetime import datetime
from loguru import logger
from config.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
    S3_RAW_PREFIX,
    CITIES
)


class WeatherExtractor:
    """
    Fetches weather data from Open-Meteo API.
    Handles retries and saves raw data to S3.
    """

    def __init__(self):
        """
        Initialize S3 connection and API settings.
        __init__ runs automatically when you create the object.
        """
        # Create S3 connection
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.bucket      = S3_BUCKET_NAME
        self.raw_prefix  = S3_RAW_PREFIX
        self.api_url     = "https://api.open-meteo.com/v1/forecast"
        logger.info("WeatherExtractor ready")

    # ─────────────────────────────────────
    # FETCH ONE CITY
    # ─────────────────────────────────────
    def fetch_city(self, city: str, lat: float, lon: float) -> dict:
        """
        Fetch weather for one city.
        Retries up to 3 times if request fails.

        Args:
            city : City name
            lat  : Latitude
            lon  : Longitude

        Returns:
            Dictionary with weather data
        """
        params = {
            "latitude"  : lat,
            "longitude" : lon,
            "current"   : [
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m",
                "weather_code",
                "precipitation",
                "cloud_cover"
            ],
            "forecast_days" : 7,
            "timezone"      : "auto"
        }

        # Retry logic - try 3 times before giving up
        for attempt in range(1, 4):
            try:
                response = requests.get(
                    self.api_url,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()

                # Extract current weather values
                current = data["current"]

                return {
                    "city"                    : city,
                    "latitude"                : lat,
                    "longitude"               : lon,
                    "temperature_c"           : current["temperature_2m"],
                    "humidity_pct"            : current["relative_humidity_2m"],
                    "wind_speed_ms"           : current["wind_speed_10m"],
                    "weather_code"            : current["weather_code"],
                    "precipitation_mm"        : current["precipitation"],
                    "cloud_cover_pct"         : current["cloud_cover"],
                    "extraction_time_utc"     : datetime.utcnow().isoformat(),
                    "status"                  : "success"
                }

            except Exception as e:
                logger.warning(
                    f"  Attempt {attempt}/3 failed for {city}: {e}"
                )
                # Wait before retrying
                # Attempt 1 fail → wait 1 sec
                # Attempt 2 fail → wait 2 sec
                # Attempt 3 fail → give up
                if attempt < 3:
                    time.sleep(attempt)

        # All 3 attempts failed
        logger.error(f"  Failed to fetch {city} after 3 attempts")
        return {
            "city"                : city,
            "latitude"            : lat,
            "longitude"           : lon,
            "extraction_time_utc" : datetime.utcnow().isoformat(),
            "status"              : "failed",
            "error"               : "Max retries exceeded"
        }

    # ─────────────────────────────────────
    # FETCH ALL CITIES
    # ─────────────────────────────────────
    def fetch_all_cities(self, cities: dict) -> pd.DataFrame:
        """
        Fetch weather for all cities one by one.

        Args:
            cities: Dictionary of {city: {lat, lon}}

        Returns:
            pandas DataFrame with all results
        """
        logger.info(f"Fetching weather for {len(cities)} cities...")
        all_results = []

        for i, (city, coords) in enumerate(cities.items(), 1):
            logger.info(f"  [{i}/{len(cities)}] Fetching {city}...")

            result = self.fetch_city(
                city=city,
                lat=coords["lat"],
                lon=coords["lon"]
            )
            all_results.append(result)

            # Small delay between requests
            # Respects API rate limits
            time.sleep(0.3)

        # Convert list of dicts to DataFrame
        df = pd.DataFrame(all_results)

        # Count successes and failures
        success = len(df[df["status"] == "success"])
        failed  = len(df[df["status"] == "failed"])
        logger.info(f"Fetch complete: {success} success, {failed} failed")

        return df

    # ─────────────────────────────────────
    # SAVE RAW DATA TO S3
    # ─────────────────────────────────────
    def save_to_s3(self, df: pd.DataFrame) -> str:
        """
        Save raw DataFrame to S3 as JSON.

        Folder structure (Hive partitioning):
        raw/weather/year=2025/month=01/day=15/file.json

        Why save raw data?
        = Source of truth
        = Can reprocess later if needed
        = Never lose original data
        """
        now       = datetime.utcnow()
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        # Build S3 path with date partitions
        s3_key = (
            f"{self.raw_prefix}"
            f"year={now.year}/"
            f"month={now.month:02d}/"
            f"day={now.day:02d}/"
            f"weather_raw_{timestamp}.json"
        )

        # Convert DataFrame to JSON string
        json_body = df.to_json(orient="records", indent=2)

        # Upload to S3
        self.s3.put_object(
            Bucket=self.bucket,
            Key=s3_key,
            Body=json_body.encode("utf-8"),
            ContentType="application/json",
            Metadata={
                "records"        : str(len(df)),
                "extracted_at"   : now.isoformat(),
                "pipeline"       : "ai-weather-pipeline"
            }
        )

        s3_uri = f"s3://{self.bucket}/{s3_key}"
        logger.success(f"Raw data saved → {s3_uri}")
        return s3_uri

    # ─────────────────────────────────────
    # MAIN RUN METHOD
    # ─────────────────────────────────────
    def run(self) -> tuple:
        """
        Run complete extraction.
        Fetch all cities → Save to S3 → Return DataFrame.

        Returns:
            (DataFrame, s3_uri)
        """
        logger.info("=" * 50)
        logger.info("STEP 1: EXTRACTION STARTED")
        logger.info("=" * 50)

        df     = self.fetch_all_cities(CITIES)
        s3_uri = self.save_to_s3(df)

        logger.info("STEP 1: EXTRACTION COMPLETE ✅")
        return df, s3_uri