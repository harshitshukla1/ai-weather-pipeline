# config/settings.py
"""
Project Settings
All configuration values live here.
Secrets are read from .env file.
"""

import os
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()


# ─────────────────────────────────────
# AWS SETTINGS
# ─────────────────────────────────────
AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION            = os.getenv("AWS_REGION", "ap-south-2")
S3_BUCKET_NAME        = os.getenv("S3_BUCKET_NAME")

# S3 folder paths
S3_RAW_PREFIX       = "raw/weather/"
S3_PROCESSED_PREFIX = "processed/weather/"
S3_ENRICHED_PREFIX  = "enriched/weather/"
S3_REPORTS_PREFIX   = "reports/"
S3_LOGS_PREFIX      = "logs/"


# ─────────────────────────────────────
# AI SETTINGS
# ─────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"


# ─────────────────────────────────────
# PIPELINE SETTINGS
# ─────────────────────────────────────
PIPELINE_NAME    = "ai-weather-pipeline"
PIPELINE_VERSION = "1.0.0"


# ─────────────────────────────────────
# CITIES TO TRACK
# lat = latitude  (north/south position)
# lon = longitude (east/west position)
# Together they pinpoint exact location
# ─────────────────────────────────────
CITIES = {
    # Indian Cities
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Mumbai":    {"lat": 19.0760, "lon": 72.8777},
    "Delhi":     {"lat": 28.6139, "lon": 77.2090},
    "Chennai":   {"lat": 13.0827, "lon": 80.2707},
    "Kolkata":   {"lat": 22.5726, "lon": 88.3639},

    # Global Cities (verified working)
    "London":    {"lat": 51.5074, "lon": -0.1278},
    "New York":  {"lat": 40.7128, "lon": -74.0060},
    "Tokyo":     {"lat": 35.6762, "lon": 139.6503},
    "Chicago":   {"lat": 41.8781, "lon": -87.6298},
    "Toronto":   {"lat": 43.6532, "lon": -79.3832},
}