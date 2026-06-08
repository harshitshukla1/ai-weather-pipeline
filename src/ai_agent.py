# src/ai_agent.py
"""
AI Agent - Groq/Llama3 Powered Intelligence
─────────────────────────────────────────────────────
Uses Groq AI to:
1. Detect anomalies in weather data
2. Generate city-level insights
3. Write pipeline execution report
4. Save everything to S3

This is what makes our pipeline unique!
Traditional pipelines just move data.
Ours THINKS about the data.
"""

import json
import boto3
import pandas as pd
from datetime import datetime
from groq import Groq
from loguru import logger
from config.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
    S3_REPORTS_PREFIX,
    GROQ_API_KEY,
    GROQ_MODEL
)


class WeatherAIAgent:
    """
    AI Agent that analyzes weather data
    and generates intelligent insights.
    """

    def __init__(self):
        """Initialize Groq AI client and S3 connection."""

        # Groq AI client
        self.groq = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL

        # S3 client
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.bucket         = S3_BUCKET_NAME
        self.reports_prefix = S3_REPORTS_PREFIX

        logger.info("WeatherAIAgent ready")

    # ─────────────────────────────────────
    # HELPER: ASK GROQ AI
    # ─────────────────────────────────────
    def _ask_ai(self, system_prompt: str, user_prompt: str) -> str:
        """
        Send a prompt to Groq AI and get response.

        system_prompt = Who the AI should be
                        Example: "You are a weather expert"

        user_prompt   = What you want it to do
                        Example: "Analyze this data..."

        temperature   = 0.3 means focused/precise response
                        0 = very precise
                        1 = very creative
        """
        try:
            response = self.groq.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1024
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Groq AI error: {e}")
            return f"AI unavailable: {str(e)}"

    # ─────────────────────────────────────
    # STEP A: DETECT ANOMALIES
    # ─────────────────────────────────────
    def detect_anomalies(self, df: pd.DataFrame) -> list:
        """
        Find unusual weather patterns using statistics.
        Then ask AI to explain what they mean.

        Method: IQR (Interquartile Range)
        ─────────────────────────────────
        Q1 = 25th percentile (lower quarter)
        Q3 = 75th percentile (upper quarter)
        IQR = Q3 - Q1

        Anything below Q1 - 1.5*IQR = anomaly
        Anything above Q3 + 1.5*IQR = anomaly

        Example:
        Temperatures: [22, 24, 23, 25, 24, 45]
        45 is an anomaly because it is too far
        from the rest of the values
        """
        logger.info("🔍 Detecting anomalies...")
        anomalies = []

        # Columns to check for anomalies
        check_cols = [
            "temperature_c",
            "humidity_pct",
            "wind_speed_ms",
            "cloud_cover_pct"
        ]

        for col in check_cols:
            if col not in df.columns:
                continue

            # Calculate IQR boundaries
            Q1  = df[col].quantile(0.25)
            Q3  = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR

            # Find rows outside boundaries
            outlier_rows = df[
                (df[col] < lower) | (df[col] > upper)
            ]

            for _, row in outlier_rows.iterrows():
                anomaly = {
                    "city"    : row["city"],
                    "metric"  : col,
                    "value"   : round(float(row[col]), 2),
                    "normal_range" : f"{round(lower, 1)} - {round(upper, 1)}",
                    "severity": "HIGH" if (
                        row[col] > upper + IQR or
                        row[col] < lower - IQR
                    ) else "MEDIUM"
                }
                anomalies.append(anomaly)
                logger.warning(
                    f"   ⚠️ Anomaly: {row['city']} {col}={row[col]} "
                    f"(normal: {round(lower,1)}-{round(upper,1)})"
                )

        if not anomalies:
            logger.info("   ✅ No anomalies detected")
            return anomalies

        # Ask AI to explain the anomalies
        logger.info(f"   Found {len(anomalies)} anomalies. Asking AI to explain...")

        ai_explanation = self._ask_ai(
            system_prompt="""You are a weather data analyst.
            Analyze these weather anomalies and explain:
            1. What each anomaly means in plain English
            2. Whether it could impact daily life or business
            3. Keep response concise and practical
            Format: one paragraph per anomaly.""",

            user_prompt=f"""Explain these weather anomalies:
            {json.dumps(anomalies, indent=2)}"""
        )

        logger.info(f"   AI Anomaly Explanation:\n{ai_explanation}")

        # Add AI explanation to result
        return {
            "anomalies"  : anomalies,
            "count"      : len(anomalies),
            "explanation": ai_explanation
        }

    # ─────────────────────────────────────
    # STEP B: GENERATE CITY INSIGHTS
    # ─────────────────────────────────────
    def generate_city_insights(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        For each city, ask AI to generate:
        - Travel advisory
        - Health tip
        - Activity recommendation

        This adds real business value!
        A logistics company can use this
        to make delivery decisions.
        """
        logger.info("🧠 Generating AI insights for each city...")

        # Build a summary of all cities for AI
        cities_summary = []
        for _, row in df.iterrows():
            cities_summary.append(
                f"{row['city']}: "
                f"{row['temperature_c']}°C, "
                f"humidity {row['humidity_pct']}%, "
                f"wind {row['wind_speed_ms']} m/s, "
                f"condition: {row['weather_condition']}, "
                f"comfort: {row['comfort_level']}"
            )

        # Ask AI for insights for all cities at once
        # (one API call = cheaper + faster)
        ai_response = self._ask_ai(
            system_prompt="""You are a weather intelligence assistant.
            For each city provided, give exactly 3 things:
            1. travel_tip: One sentence travel advice
            2. health_tip: One sentence health recommendation  
            3. activity: Best outdoor activity recommendation

            Respond ONLY in this JSON format:
            [
              {
                "city": "CityName",
                "travel_tip": "...",
                "health_tip": "...",
                "activity": "..."
              }
            ]
            No extra text. Only valid JSON array.""",

            user_prompt=f"""Generate insights for these cities:
            {chr(10).join(cities_summary)}"""
        )

        # Parse AI response
        try:
            # Clean response (remove markdown if AI added it)
            clean_response = ai_response.strip()
            if "```" in clean_response:
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]

            insights = json.loads(clean_response)
            insights_df = pd.DataFrame(insights)

            # Merge insights back into main DataFrame
            df = df.merge(insights_df, on="city", how="left")
            logger.info(f"   ✅ AI insights added for {len(insights)} cities")

        except json.JSONDecodeError as e:
            logger.warning(f"   AI returned invalid JSON: {e}")
            logger.warning(f"   Raw response: {ai_response[:200]}")
            # Add empty columns so pipeline doesnt break
            df["travel_tip"] = "Insights unavailable"
            df["health_tip"] = "Insights unavailable"
            df["activity"]   = "Insights unavailable"

        return df

    # ─────────────────────────────────────
    # STEP C: GENERATE PIPELINE REPORT
    # ─────────────────────────────────────
    def generate_report(
        self,
        df: pd.DataFrame,
        anomaly_results: dict,
        run_id: str
    ) -> str:
        """
        Ask AI to write a complete pipeline report.

        Instead of reading raw logs,
        you get a human-readable summary!
        """
        logger.info("📝 Generating AI pipeline report...")

        # Build stats summary for AI
        stats = {
            "run_id"           : run_id,
            "cities_processed" : len(df),
            "cities_list"      : df["city"].tolist(),
            "avg_temperature"  : round(df["temperature_c"].mean(), 1),
            "hottest_city"     : df.loc[df["temperature_c"].idxmax(), "city"],
            "coldest_city"     : df.loc[df["temperature_c"].idxmin(), "city"],
            "most_humid_city"  : df.loc[df["humidity_pct"].idxmax(), "city"],
            "raining_cities"   : df[df["is_raining"] == True]["city"].tolist(),
            "anomalies_found"  : anomaly_results.get("count", 0) if isinstance(anomaly_results, dict) else 0,
            "weather_breakdown": df["weather_condition"].value_counts().to_dict(),
            "comfort_breakdown": df["comfort_level"].value_counts().to_dict()
        }

        report = self._ask_ai(
            system_prompt="""You are a data engineering pipeline monitor.
            Write a clear, professional pipeline execution report.
            Include:
            1. Executive Summary (2-3 sentences)
            2. Key Weather Highlights
            3. Cities Needing Attention
            4. Data Quality Summary
            5. Recommendations for Operations Team
            Use emojis to make it readable.
            Keep it under 300 words.""",

            user_prompt=f"""Write a pipeline report for this run:
            {json.dumps(stats, indent=2)}

            Anomaly Details:
            {json.dumps(anomaly_results, indent=2) if isinstance(anomaly_results, dict) else 'None detected'}
            """
        )

        logger.info("   ✅ Pipeline report generated")
        return report

    # ─────────────────────────────────────
    # STEP D: SAVE RESULTS TO S3
    # ─────────────────────────────────────
    def save_to_s3(
        self,
        df: pd.DataFrame,
        report: str,
        anomalies: dict,
        run_id: str
    ) -> str:
        """Save AI results and report to S3."""

        now       = datetime.utcnow()
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        s3_key = (
            f"{self.reports_prefix}"
            f"year={now.year}/"
            f"month={now.month:02d}/"
            f"day={now.day:02d}/"
            f"report_{timestamp}.json"
        )

        # Build complete report object
        report_obj = {
            "run_id"           : run_id,
            "generated_at_utc" : now.isoformat(),
            "pipeline_report"  : report,
            "anomalies"        : anomalies if isinstance(anomalies, dict) else {"count": 0},
            "city_count"       : len(df),
            "cities"           : df["city"].tolist(),
            "summary_stats"    : {
                "avg_temp_c"   : round(df["temperature_c"].mean(), 1),
                "avg_humidity" : round(df["humidity_pct"].mean(), 1),
                "raining_count": int(df["is_raining"].sum())
            }
        }

        self.s3.put_object(
            Bucket      = self.bucket,
            Key         = s3_key,
            Body        = json.dumps(report_obj, indent=2).encode("utf-8"),
            ContentType = "application/json",
            Metadata    = {
                "run_id"   : run_id,
                "pipeline" : "ai-weather-pipeline"
            }
        )

        s3_uri = f"s3://{self.bucket}/{s3_key}"
        logger.success(f"AI report saved → {s3_uri}")
        return s3_uri

    # ─────────────────────────────────────
    # MAIN RUN METHOD
    # ─────────────────────────────────────
    def run(self, df: pd.DataFrame, run_id: str) -> tuple:
        """
        Run complete AI analysis.
        detect → insights → report → save

        Args:
            df     : Clean DataFrame from Transformer
            run_id : Unique ID for this pipeline run

        Returns:
            (enriched DataFrame, report string, S3 URI)
        """
        logger.info("=" * 50)
        logger.info("STEP 3: AI AGENT STARTED")
        logger.info("=" * 50)

        # Detect anomalies
        anomaly_results = self.detect_anomalies(df)

        # Generate city insights
        df = self.generate_city_insights(df)

        # Generate pipeline report
        report = self.generate_report(df, anomaly_results, run_id)

        # Save to S3
        s3_uri = self.save_to_s3(df, report, anomaly_results, run_id)

        # Print report to console
        logger.info("\n" + "=" * 50)
        logger.info("📋 AI PIPELINE REPORT:")
        logger.info("=" * 50)
        print(f"\n{report}\n")

        logger.info("STEP 3: AI AGENT COMPLETE ✅")
        return df, report, s3_uri