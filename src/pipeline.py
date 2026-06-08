# src/pipeline.py
"""
Main Pipeline Orchestrator
─────────────────────────────────────────────────────
Connects Extractor → Transformer → AI Agent
Runs everything in correct order.
Handles errors and saves run logs to S3.

This is what runs automatically via GitHub Actions.
"""

import json
import time
import boto3
from datetime import datetime, timezone
from loguru import logger
from config.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
    S3_LOGS_PREFIX,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    CITIES
)
from src.extractor import WeatherExtractor
from src.transformer import WeatherTransformer
from src.ai_agent import WeatherAIAgent


class WeatherPipeline:
    """
    Master pipeline that runs all steps in order.

    ORCHESTRATION PATTERN:
    ──────────────────────
    Like a project manager who:
    1. Tells each team what to do
    2. Passes results between teams
    3. Handles problems if they arise
    4. Reports final status
    """

    def __init__(self):
        """Initialize pipeline with unique run ID."""

        # Unique ID for this pipeline run
        # Used for tracking in S3 logs
        self.run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        # S3 client for saving logs
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.bucket     = S3_BUCKET_NAME
        self.logs_prefix = S3_LOGS_PREFIX

        # Track results of each step
        self.run_log = {
            "run_id"          : self.run_id,
            "pipeline_name"   : PIPELINE_NAME,
            "pipeline_version": PIPELINE_VERSION,
            "started_at_utc"  : datetime.now(timezone.utc).isoformat(),
            "status"          : "running",
            "steps"           : {}
        }

        logger.info(f"Pipeline initialized | Run ID: {self.run_id}")

    # ─────────────────────────────────────
    # SAVE RUN LOG TO S3
    # ─────────────────────────────────────
    def save_run_log(self):
        """
        Save pipeline run log to S3.
        This creates an audit trail.

        Audit trail = record of everything that happened
        Important for debugging and compliance.
        """
        s3_key = (
            f"{self.logs_prefix}"
            f"run_{self.run_id}.json"
        )

        self.s3.put_object(
            Bucket      = self.bucket,
            Key         = s3_key,
            Body        = json.dumps(self.run_log, indent=2).encode("utf-8"),
            ContentType = "application/json"
        )
        logger.info(f"Run log saved → s3://{self.bucket}/{s3_key}")

    # ─────────────────────────────────────
    # RUN STEP 1: EXTRACTION
    # ─────────────────────────────────────
    def run_extraction(self):
        """Run extraction step and track results."""
        logger.info("━" * 50)
        logger.info("STEP 1/3: EXTRACTION")
        logger.info("━" * 50)

        start = time.time()

        extractor      = WeatherExtractor()
        df_raw, s3_uri = extractor.run()

        duration = round(time.time() - start, 2)

        # Record step results
        self.run_log["steps"]["extraction"] = {
            "status"         : "success",
            "duration_sec"   : duration,
            "total_cities"   : len(df_raw),
            "success_cities" : int((df_raw["status"] == "success").sum()),
            "failed_cities"  : int((df_raw["status"] == "failed").sum()),
            "s3_uri"         : s3_uri
        }

        logger.info(f"Extraction done in {duration}s")
        return df_raw

    # ─────────────────────────────────────
    # RUN STEP 2: TRANSFORMATION
    # ─────────────────────────────────────
    def run_transformation(self, df_raw):
        """Run transformation step and track results."""
        logger.info("━" * 50)
        logger.info("STEP 2/3: TRANSFORMATION")
        logger.info("━" * 50)

        start = time.time()

        transformer         = WeatherTransformer()
        df_clean, s3_uri    = transformer.run(df_raw)

        duration = round(time.time() - start, 2)

        # Record step results
        self.run_log["steps"]["transformation"] = {
            "status"        : "success",
            "duration_sec"  : duration,
            "records_in"    : len(df_raw),
            "records_out"   : len(df_clean),
            "columns_added" : len(df_clean.columns) - len(df_raw.columns),
            "s3_uri"        : s3_uri
        }

        logger.info(f"Transformation done in {duration}s")
        return df_clean

    # ─────────────────────────────────────
    # RUN STEP 3: AI AGENT
    # ─────────────────────────────────────
    def run_ai_agent(self, df_clean):
        """Run AI agent step and track results."""
        logger.info("━" * 50)
        logger.info("STEP 3/3: AI AGENT")
        logger.info("━" * 50)

        start = time.time()

        agent                    = WeatherAIAgent()
        df_final, report, s3_uri = agent.run(df_clean, self.run_id)

        duration = round(time.time() - start, 2)

        # Record step results
        self.run_log["steps"]["ai_agent"] = {
            "status"      : "success",
            "duration_sec": duration,
            "cities"      : df_final["city"].tolist(),
            "s3_uri"      : s3_uri
        }

        logger.info(f"AI Agent done in {duration}s")
        return df_final, report

    # ─────────────────────────────────────
    # MAIN RUN METHOD
    # ─────────────────────────────────────
    def run(self):
        """
        Run complete pipeline.
        Extract → Transform → AI → Save logs

        Returns final DataFrame and status.
        """
        pipeline_start = time.time()

        logger.info("=" * 50)
        logger.info(f"PIPELINE STARTED | Run: {self.run_id}")
        logger.info("=" * 50)

        try:
            # Step 1: Extract
            df_raw = self.run_extraction()

            # Step 2: Transform
            df_clean = self.run_transformation(df_raw)

            # Step 3: AI Agent
            df_final, report = self.run_ai_agent(df_clean)

            # Pipeline succeeded
            total_duration = round(time.time() - pipeline_start, 2)

            self.run_log["status"]        = "success"
            self.run_log["completed_at"]  = datetime.now(timezone.utc).isoformat()
            self.run_log["total_duration_sec"] = total_duration
            self.run_log["final_record_count"] = len(df_final)

            # Save run log to S3
            self.save_run_log()

            # Print final summary
            logger.info("=" * 50)
            logger.info("✅ PIPELINE COMPLETE!")
            logger.info("=" * 50)
            logger.info(f"  Run ID      : {self.run_id}")
            logger.info(f"  Duration    : {total_duration}s")
            logger.info(f"  Cities      : {len(df_final)}")
            logger.info(f"  Status      : SUCCESS")
            logger.info("=" * 50)

            return {
                "status"    : "success",
                "run_id"    : self.run_id,
                "duration"  : total_duration,
                "records"   : len(df_final),
                "dataframe" : df_final
            }

        except Exception as e:
            # Something went wrong
            total_duration = round(time.time() - pipeline_start, 2)

            self.run_log["status"]       = "failed"
            self.run_log["error"]        = str(e)
            self.run_log["failed_at"]    = datetime.now(timezone.utc).isoformat()
            self.run_log["total_duration_sec"] = total_duration

            # Save failed log to S3
            self.save_run_log()

            logger.error("=" * 50)
            logger.error(f"❌ PIPELINE FAILED: {e}")
            logger.error("=" * 50)

            return {
                "status" : "failed",
                "run_id" : self.run_id,
                "error"  : str(e)
            }


# ─────────────────────────────────────
# ENTRY POINT
# Run this file directly to start pipeline
# ─────────────────────────────────────
if __name__ == "__main__":
    pipeline = WeatherPipeline()
    result   = pipeline.run()