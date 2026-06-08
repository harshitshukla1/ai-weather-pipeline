import os, boto3
from dotenv import load_dotenv
from src.extractor import WeatherExtractor
from src.transformer import WeatherTransformer

load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

# Extract raw data
extractor = WeatherExtractor(s3, os.getenv("S3_BUCKET_NAME"))
test_cities = {
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Delhi":     {"lat": 28.6139, "lon": 77.2090},
    "London":    {"lat": 51.5074, "lon": -0.1278}
}
df_raw, _ = extractor.run(test_cities)

# Transform
transformer = WeatherTransformer(s3, os.getenv("S3_BUCKET_NAME"))
df_final, s3_path = transformer.run(df_raw)

print("\n📊 TRANSFORMED DATA PREVIEW:")
print(df_final[["city", "current_temp_c", "weather_category", "comfort_level", "wind_severity"]].to_string(index=False))
print(f"\n💾 Saved to: {s3_path}")
