# src/transformer.py
"""
Weather Data Transformer
─────────────────────────────────────────────────────
Takes raw weather data, cleans it, enriches it,
and saves to S3 in Parquet format.

Key Concepts for Interview:
- Data Quality Dimensions
- Outlier Handling
- Feature Engineering
- Parquet vs CSV
- Hive Partitioning
"""

import io
import boto3
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger
from config.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
    S3_PROCESSED_PREFIX
)


class WeatherTransformer:
    """
    Cleans, validates, and enriches raw weather data.
    Saves processed data to S3 as Parquet.
    """

    def __init__(self):
        """Initialize S3 connection."""
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.bucket           = S3_BUCKET_NAME
        self.processed_prefix = S3_PROCESSED_PREFIX
        logger.info("WeatherTransformer ready")

    # ─────────────────────────────────────
    # STEP A: VALIDATE DATA QUALITY
    # ─────────────────────────────────────
    def validate(self, df: pd.DataFrame) -> dict:
        """
        Check data quality before processing.

        Data Quality Dimensions (important for interview):
        1. Completeness - are all fields filled?
        2. Accuracy     - are values in valid range?
        3. Consistency  - same format everywhere?

        Returns quality report dictionary.
        """
        total   = len(df)
        success = len(df[df["status"] == "success"])
        failed  = len(df[df["status"] != "success"])
        missing = int(df.isnull().sum().sum())

        report = {
            "total_records"    : total,
            "success_records"  : success,
            "failed_records"   : failed,
            "missing_values"   : missing,
            "completeness_pct" : round((1 - df.isnull().mean().mean()) * 100, 2),
            "success_rate_pct" : round((success / total) * 100, 2)
        }

        logger.info("📊 Data Quality Report:")
        logger.info(f"   Total Records    : {total}")
        logger.info(f"   Success Records  : {success}")
        logger.info(f"   Failed Records   : {failed}")
        logger.info(f"   Missing Values   : {missing}")
        logger.info(f"   Completeness     : {report['completeness_pct']}%")
        logger.info(f"   Success Rate     : {report['success_rate_pct']}%")

        return report

    # ─────────────────────────────────────
    # STEP B: CLEAN DATA
    # ─────────────────────────────────────
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean raw data:
        1. Keep only successful records
        2. Fix missing values
        3. Clip outliers to valid ranges
        4. Standardize text
        """
        logger.info("🧹 Cleaning data...")
        df = df.copy()

        # 1. Keep only successful extractions
        before = len(df)
        df     = df[df["status"] == "success"].copy()
        logger.info(f"   Removed {before - len(df)} failed records")

        # 2. Fill missing numeric values with median
        #    Why median not mean?
        #    Mean is affected by outliers
        #    Median is more robust
        numeric_cols = [
            "temperature_c",
            "humidity_pct",
            "wind_speed_ms",
            "precipitation_mm",
            "cloud_cover_pct"
        ]
        for col in numeric_cols:
            if col in df.columns:
                missing_count = df[col].isnull().sum()
                if missing_count > 0:
                    median_val = df[col].median()
                    df[col]    = df[col].fillna(median_val)
                    logger.info(f"   Filled {missing_count} missing {col} with median {median_val}")

        # 3. Clip values to physically possible ranges
        #    Example: humidity cannot be 150%
        #    We clip it to 100% maximum
        clip_ranges = {
            "temperature_c"    : (-50,  60),
            "humidity_pct"     : (  0, 100),
            "wind_speed_ms"    : (  0, 110),
            "precipitation_mm" : (  0, 500),
            "cloud_cover_pct"  : (  0, 100)
        }
        for col, (low, high) in clip_ranges.items():
            if col in df.columns:
                df[col] = df[col].clip(lower=low, upper=high)

        logger.info("   Outliers clipped to valid ranges")

        # 4. Standardize city names
        #    "bangalore" → "Bangalore"
        df["city"] = df["city"].str.strip().str.title()
        logger.info("   City names standardized")

        logger.info(f"   ✅ Clean records ready: {len(df)}")
        return df

    # ─────────────────────────────────────
    # STEP C: ENRICH DATA
    # ─────────────────────────────────────
    def enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add new columns that add business value.
        This is called Feature Engineering.

        New columns we add:
        - weather_condition  (human readable)
        - temp_category      (Cold/Mild/Hot)
        - comfort_level      (how comfortable is it?)
        - wind_category      (Calm/Breezy/Stormy)
        - is_raining         (True/False)
        - processed_at_utc   (when we processed)
        """
        logger.info("✨ Enriching data...")
        df = df.copy()

        # 1. Weather Condition from WMO code
        #    Open-Meteo gives a weather_code number
        #    We convert it to human readable text
        def get_weather_condition(code):
            if pd.isna(code):
                return "Unknown"
            code = int(code)
            if code == 0:
                return "Clear Sky"
            elif code in [1, 2, 3]:
                return "Partly Cloudy"
            elif code in [45, 48]:
                return "Foggy"
            elif code in [51, 53, 55]:
                return "Drizzle"
            elif code in [61, 63, 65]:
                return "Rain"
            elif code in [71, 73, 75]:
                return "Snow"
            elif code in [80, 81, 82]:
                return "Heavy Rain"
            elif code in [95, 96, 99]:
                return "Thunderstorm"
            else:
                return "Overcast"

        df["weather_condition"] = df["weather_code"].apply(
            get_weather_condition
        )

        # 2. Temperature Category
        df["temp_category"] = pd.cut(
            df["temperature_c"],
            bins   = [-50, 10, 20, 30, 60],
            labels = ["Cold", "Mild", "Warm", "Hot"]
        )

        # 3. Comfort Level
        #    Combination of temperature + humidity
        def get_comfort(row):
            temp     = row["temperature_c"]
            humidity = row["humidity_pct"]

            if temp < 10:
                return "Too Cold"
            elif temp > 35:
                return "Too Hot"
            elif 18 <= temp <= 28 and 30 <= humidity <= 70:
                return "Comfortable"
            elif humidity > 80:
                return "Humid"
            else:
                return "Moderate"

        df["comfort_level"] = df.apply(get_comfort, axis=1)

        # 4. Wind Category
        df["wind_category"] = pd.cut(
            df["wind_speed_ms"],
            bins   = [0, 3, 8, 15, 25, 110],
            labels = ["Calm", "Light", "Moderate", "Strong", "Extreme"]
        )

        # 5. Is it raining right now?
        df["is_raining"] = df["precipitation_mm"] > 0

        # 6. Processing metadata
        df["processed_at_utc"] = datetime.utcnow().isoformat()
        df["pipeline_version"] = "1.0.0"

        logger.info("   Added: weather_condition, temp_category, comfort_level")
        logger.info("   Added: wind_category, is_raining, processed_at_utc")
        logger.info(f"   ✅ Enrichment complete. Total columns: {len(df.columns)}")

        return df

    # ─────────────────────────────────────
    # STEP D: SAVE TO S3 AS PARQUET
    # ─────────────────────────────────────
    def save_to_s3(self, df: pd.DataFrame) -> str:
        """
        Save processed data to S3 as Parquet.

        Why Parquet?
        - 70% smaller than CSV
        - 10x faster to query
        - Industry standard for data lakes
        - Athena loves Parquet

        Folder structure:
        processed/weather/year=2025/month=01/day=15/file.parquet
        """
        now       = datetime.utcnow()
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        s3_key = (
            f"{self.processed_prefix}"
            f"year={now.year}/"
            f"month={now.month:02d}/"
            f"day={now.day:02d}/"
            f"weather_processed_{timestamp}.parquet"
        )

        # Convert category columns to string
        # Parquet needs this for compatibility
        for col in df.select_dtypes(["category"]).columns:
            df[col] = df[col].astype(str)

        # Write Parquet to memory buffer
        # (not to disk, directly to S3)
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False, engine="pyarrow")
        buffer.seek(0)

        # Upload buffer to S3
        self.s3.put_object(
            Bucket      = self.bucket,
            Key         = s3_key,
            Body        = buffer.getvalue(),
            ContentType = "application/octet-stream",
            Metadata    = {
                "records"      : str(len(df)),
                "processed_at" : now.isoformat(),
                "format"       : "parquet",
                "pipeline"     : "ai-weather-pipeline"
            }
        )

        s3_uri = f"s3://{self.bucket}/{s3_key}"
        logger.success(f"Processed data saved → {s3_uri}")
        return s3_uri

    # ─────────────────────────────────────
    # MAIN RUN METHOD
    # ─────────────────────────────────────
    def run(self, df_raw: pd.DataFrame) -> tuple:
        """
        Run complete transformation pipeline.
        validate → clean → enrich → save

        Args:
            df_raw: Raw DataFrame from Extractor

        Returns:
            (clean DataFrame, S3 URI)
        """
        logger.info("=" * 50)
        logger.info("STEP 2: TRANSFORMATION STARTED")
        logger.info("=" * 50)

        quality_report = self.validate(df_raw)
        df_clean       = self.clean(df_raw)
        df_enriched    = self.enrich(df_clean)
        s3_uri         = self.save_to_s3(df_enriched)

        logger.info("STEP 2: TRANSFORMATION COMPLETE ✅")
        return df_enriched, s3_uri