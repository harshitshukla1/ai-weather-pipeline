# dashboard/app.py
"""
🚀 AI Weather Intelligence - Sci-Fi Data Engineering Dashboard
Built by Harshit Shukla | Production-Grade AI Pipeline
"""

import os
import json
import boto3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Weather Intelligence | Harshit Shukla",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

* { font-family: 'Rajdhani', sans-serif !important; }

/* HIDE HAMBURGER MENU & FOOTER */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header {visibility: hidden !important;}
[data-testid="stToolbar"] {visibility: hidden !important;}
[data-testid="stDecoration"] {display: none !important;}
[data-testid="stStatusWidget"] {visibility: hidden !important;}

/* FORCE DARK THEME */
.stApp {
    background: #000000 !important;
    background-image:
        radial-gradient(ellipse at 20% 50%, #0a0a2e 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, #001a3a 0%, transparent 50%),
        radial-gradient(ellipse at 50% 80%, #0a1628 0%, transparent 50%) !important;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none;
    z-index: 0;
    animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
    0% { background-position: 0 0; }
    100% { background-position: 50px 50px; }
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #000510 0%, #001020 100%) !important;
    border-right: 1px solid rgba(0,212,255,0.2) !important;
}

/* METRICS */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(0,212,255,0.05), rgba(0,100,200,0.03));
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 12px;
    padding: 15px !important;
    transition: all 0.4s ease;
    overflow: hidden;
}

[data-testid="stMetric"]:hover {
    border-color: rgba(0,212,255,0.6);
    box-shadow: 0 0 30px rgba(0,212,255,0.2);
    transform: translateY(-5px);
}

[data-testid="stMetricLabel"] {
    color: rgba(0,212,255,0.7) !important;
    font-size: 0.75rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

[data-testid="stMetricValue"] {
    color: #00d4ff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    text-shadow: 0 0 10px rgba(0,212,255,0.5);
}

h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    color: #00d4ff !important;
    letter-spacing: 2px !important;
}

h2, h3 {
    border-bottom: 1px solid rgba(0,212,255,0.2);
    padding-bottom: 8px;
    color: #e6f1ff !important;
}

.stButton > button {
    background: transparent !important;
    color: #00d4ff !important;
    border: 1px solid rgba(0,212,255,0.5) !important;
    border-radius: 4px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 10px 20px !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: rgba(0,212,255,0.1) !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.3) !important;
    transform: translateY(-2px) !important;
}

.stRadio > div > label {
    color: rgba(0,212,255,0.7) !important;
    border: 1px solid rgba(0,212,255,0.15) !important;
    border-radius: 6px !important;
    padding: 10px 14px !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
}

.stRadio > div > label:hover {
    border-color: rgba(0,212,255,0.5) !important;
    background: rgba(0,212,255,0.05) !important;
    transform: translateX(4px);
}

hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.4), transparent) !important;
}

.stAlert {
    background: rgba(0,212,255,0.05) !important;
    border: 1px solid rgba(0,212,255,0.2) !important;
    border-radius: 8px !important;
    color: #e6f1ff !important;
}

.stDataFrame {
    border: 1px solid rgba(0,212,255,0.2) !important;
    border-radius: 8px !important;
}

/* ════════════════════════════════════════════
   EXPANDER FIX — HIDE BROKEN MATERIAL ICONS
   ════════════════════════════════════════════ */

[data-testid="stExpander"] [data-testid="stIconMaterial"],
.streamlit-expanderHeader [data-testid="stIconMaterial"],
details summary span[data-testid="stIconMaterial"],
span[data-testid="stIconMaterial"] {
    display: none !important;
    visibility: hidden !important;
    font-size: 0 !important;
    width: 0 !important;
    height: 0 !important;
}

[data-testid="stExpander"] details summary::before {
    content: '▶' !important;
    color: #00d4ff !important;
    font-size: 0.8rem !important;
    margin-right: 12px !important;
    display: inline-block !important;
    transition: transform 0.3s ease !important;
}

[data-testid="stExpander"] details[open] summary::before {
    transform: rotate(90deg) !important;
}

[data-testid="stExpander"] summary::-webkit-details-marker,
[data-testid="stExpander"] summary::marker {
    display: none !important;
    content: '' !important;
}

[data-testid="stExpander"] summary {
    list-style: none !important;
    cursor: pointer !important;
}

[data-testid="stExpander"] details {
    background: rgba(0,212,255,0.03) !important;
    border: 1px solid rgba(0,212,255,0.15) !important;
    border-radius: 8px !important;
    margin: 6px 0 !important;
    transition: all 0.3s ease !important;
}

[data-testid="stExpander"] details:hover {
    border-color: rgba(0,212,255,0.4) !important;
    background: rgba(0,212,255,0.06) !important;
}

[data-testid="stExpander"] summary {
    color: #00d4ff !important;
    font-family: 'Orbitron', monospace !important;
    padding: 14px 18px !important;
    font-size: 0.85rem !important;
    letter-spacing: 1px !important;
}

[data-testid="stExpander"] details[open] {
    border-color: rgba(0,212,255,0.4) !important;
    background: rgba(0,212,255,0.05) !important;
}

.stSelectbox > div > div {
    background: rgba(0,10,20,0.8) !important;
    border-color: rgba(0,212,255,0.3) !important;
    color: #e6f1ff !important;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #000510; }
::-webkit-scrollbar-thumb {
    background: rgba(0,212,255,0.3);
    border-radius: 3px;
}

.scifi-card {
    background: linear-gradient(135deg, rgba(0,212,255,0.05), rgba(0,50,100,0.03));
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 12px;
    padding: 24px;
    margin: 10px 0;
    transition: all 0.4s ease;
    position: relative;
    overflow: hidden;
    word-wrap: break-word;
}

.scifi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, #00d4ff, transparent);
}

.scifi-card:hover {
    border-color: rgba(0,212,255,0.4);
    box-shadow: 0 8px 32px rgba(0,212,255,0.1);
    transform: translateY(-3px);
}

.hero-title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.5rem, 4vw, 2.8rem);
    font-weight: 900;
    color: #00d4ff;
    text-shadow: 0 0 10px rgba(0,212,255,0.8), 0 0 30px rgba(0,212,255,0.4);
    letter-spacing: 4px;
    text-align: center;
    animation: glow 3s ease-in-out infinite alternate;
}

@keyframes glow {
    from { text-shadow: 0 0 10px rgba(0,212,255,0.8); }
    to { text-shadow: 0 0 20px rgba(0,212,255,1), 0 0 40px rgba(0,212,255,0.6); }
}

.hero-sub {
    font-size: clamp(0.7rem, 1.5vw, 1rem);
    color: rgba(230,241,255,0.6);
    text-align: center;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 10px;
}

.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0,255,136,0.1);
    border: 1px solid rgba(0,255,136,0.3);
    border-radius: 20px;
    padding: 4px 16px;
    font-size: 0.75rem;
    color: #00ff88;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.pulse-dot {
    width: 8px; height: 8px;
    background: #00ff88;
    border-radius: 50%;
    display: inline-block;
    animation: pulse-anim 1.5s infinite;
}

@keyframes pulse-anim {
    0% { box-shadow: 0 0 0 0 rgba(0,255,136,0.7); }
    70% { box-shadow: 0 0 0 8px rgba(0,255,136,0); }
    100% { box-shadow: 0 0 0 0 rgba(0,255,136,0); }
}

.tech-badge {
    display: inline-block;
    background: rgba(0,212,255,0.08);
    color: #00d4ff;
    padding: 6px 16px;
    border-radius: 3px;
    font-size: 0.75rem;
    border: 1px solid rgba(0,212,255,0.25);
    letter-spacing: 1px;
    margin: 4px;
    font-family: 'Orbitron', monospace;
    transition: all 0.3s ease;
}

.tech-badge:hover {
    background: rgba(0,212,255,0.2);
    transform: translateY(-2px);
}

.stat-number {
    font-family: 'Orbitron', monospace;
    font-size: clamp(2rem, 5vw, 3rem);
    font-weight: 900;
    color: #00d4ff;
    text-shadow: 0 0 20px rgba(0,212,255,0.5);
}

a {
    color: #00d4ff !important;
    text-decoration: none !important;
}

a:hover {
    color: #00ffff !important;
    text-shadow: 0 0 8px rgba(0,212,255,0.6);
}

.stProgress > div > div {
    background: linear-gradient(90deg, #00d4ff, #0066ff) !important;
}

.workflow-step {
    background: linear-gradient(135deg, rgba(0,212,255,0.05), rgba(0,50,100,0.02));
    border: 1px solid rgba(0,212,255,0.2);
    border-left: 4px solid #00d4ff;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 12px 0;
    transition: all 0.4s ease;
    animation: slideIn 0.6s ease-out;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

.workflow-step:hover {
    transform: translateX(8px);
    box-shadow: 0 4px 20px rgba(0,212,255,0.2);
}

.workflow-arrow {
    text-align: center;
    color: #00d4ff;
    font-size: 1.5rem;
    margin: -5px 0;
    animation: pulse-arrow 2s infinite;
}

@keyframes pulse-arrow {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; transform: translateY(4px); }
}

.ai-cap-card {
    background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(0,100,200,0.04));
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: all 0.4s ease;
    height: 100%;
}

.ai-cap-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 12px 40px rgba(0,212,255,0.25);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(0,212,255,0.05);
    border-radius: 8px;
    border: 1px solid rgba(0,212,255,0.15);
    color: #8892b0;
    font-family: 'Orbitron', monospace;
    letter-spacing: 1px;
}

.stTabs [aria-selected="true"] {
    background: rgba(0,212,255,0.15) !important;
    border-color: #00d4ff !important;
    color: #00d4ff !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 100% !important;
}

@media (max-width: 768px) {
    .hero-title { font-size: 1.5rem !important; letter-spacing: 2px !important; }
    .scifi-card { padding: 16px !important; }
    [data-testid="stMetric"] { padding: 10px !important; }
    [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# SECRETS HANDLER - Works for both local & cloud
# ═══════════════════════════════════════════════
def get_secret(key):
    """Get secret from Streamlit Cloud secrets OR local .env file"""
    try:
        # Try Streamlit Cloud secrets first
        return st.secrets[key]
    except (KeyError, FileNotFoundError, Exception):
        pass
    # Fall back to environment variable
    value = os.getenv(key)
    return value if value else None


@st.cache_resource
def get_s3_client():
    """Create S3 client using secrets from cloud or local env"""
    access_key = get_secret("AWS_ACCESS_KEY_ID")
    secret_key = get_secret("AWS_SECRET_ACCESS_KEY")
    region = get_secret("AWS_REGION")
    
    if not all([access_key, secret_key, region]):
        return None
    
    return boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )


@st.cache_data(ttl=1800)
def load_latest_data():
    """Load latest processed weather data from S3"""
    s3 = get_s3_client()
    bucket = get_secret("S3_BUCKET_NAME")
    
    if not s3:
        return None, "S3 client could not be created. Check AWS credentials."
    if not bucket:
        return None, "S3_BUCKET_NAME secret is missing"
    
    try:
        r = s3.list_objects_v2(Bucket=bucket, Prefix="processed/weather/")
        if "Contents" not in r:
            return None, f"No data found in s3://{bucket}/processed/weather/"
        files = sorted(r["Contents"], key=lambda x: x["LastModified"], reverse=True)
        obj = s3.get_object(Bucket=bucket, Key=files[0]["Key"])
        import io
        return pd.read_parquet(io.BytesIO(obj["Body"].read())), files[0]["Key"]
    except Exception as e:
        return None, str(e)


@st.cache_data(ttl=1800)
def load_latest_report():
    """Load latest AI report from S3"""
    s3 = get_s3_client()
    bucket = get_secret("S3_BUCKET_NAME")
    
    if not s3 or not bucket:
        return None
    
    try:
        r = s3.list_objects_v2(Bucket=bucket, Prefix="reports/")
        if "Contents" not in r:
            return None
        files = sorted(r["Contents"], key=lambda x: x["LastModified"], reverse=True)
        obj = s3.get_object(Bucket=bucket, Key=files[0]["Key"])
        return json.loads(obj["Body"].read().decode("utf-8"))
    except Exception:
        return None


@st.cache_data(ttl=1800)
def load_pipeline_logs():
    """Load pipeline run logs from S3"""
    s3 = get_s3_client()
    bucket = get_secret("S3_BUCKET_NAME")
    
    if not s3 or not bucket:
        return []
    
    try:
        r = s3.list_objects_v2(Bucket=bucket, Prefix="logs/")
        if "Contents" not in r:
            return []
        files = sorted(r["Contents"], key=lambda x: x["LastModified"], reverse=True)[:10]
        logs = []
        for f in files:
            obj = s3.get_object(Bucket=bucket, Key=f["Key"])
            logs.append(json.loads(obj["Body"].read().decode("utf-8")))
        return logs
    except Exception:
        return []


def show_debug_info():
    """Show debug info when data fails to load"""
    with st.expander("🔧 DEBUG INFORMATION — Click to expand"):
        st.markdown("### Secrets Status")
        secrets_to_check = [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_REGION",
            "S3_BUCKET_NAME",
            "GROQ_API_KEY"
        ]
        for key in secrets_to_check:
            value = get_secret(key)
            if value:
                # Show masked value
                if key in ["AWS_SECRET_ACCESS_KEY", "GROQ_API_KEY", "AWS_ACCESS_KEY_ID"]:
                    masked = value[:6] + "****" if len(value) > 6 else "****"
                    st.success(f"✅ **{key}**: {masked}")
                else:
                    st.success(f"✅ **{key}**: {value}")
            else:
                st.error(f"❌ **{key}**: NOT SET")
        
        st.markdown("---")
        st.markdown("### Common Fixes")
        st.markdown("""
        **1. If secrets show NOT SET:**
        - Go to Streamlit Cloud → Your app → Settings → Secrets
        - Paste secrets in TOML format:
        ```toml
        AWS_ACCESS_KEY_ID = "your_key_here"
        AWS_SECRET_ACCESS_KEY = "your_secret_here"
        AWS_REGION = "ap-south-2"
        S3_BUCKET_NAME = "weather-pipeline-harshit-2025"
        GROQ_API_KEY = "your_groq_key_here"
        ```
        - Click Save and wait for app restart
        
        **2. If secrets are set but data still missing:**
        - Run pipeline locally: `python src/pipeline.py`
        - Verify data exists in S3 bucket
        - Check AWS region matches bucket region
        
        **3. If bucket access denied:**
        - Verify IAM user has S3FullAccess permission
        - Check bucket name spelling exactly
        """)


def dark_layout(fig, height=400):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,5,15,0.5)",
        font=dict(color="#8892b0", family="Rajdhani"),
        xaxis=dict(gridcolor="rgba(0,212,255,0.08)", linecolor="rgba(0,212,255,0.2)"),
        yaxis=dict(gridcolor="rgba(0,212,255,0.08)", linecolor="rgba(0,212,255,0.2)"),
        margin=dict(l=10, r=10, t=30, b=10)
    )
    return fig


def main():

    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:20px 0 10px;">
            <div style="font-family:'Orbitron',monospace; font-size:1.1rem; color:#00d4ff; letter-spacing:3px;">
                ◈ WEATHER AI
            </div>
            <div style="color:rgba(0,212,255,0.4); font-size:0.7rem; letter-spacing:3px; text-transform:uppercase;">
                Intelligence Dashboard v1.0
            </div>
            <br>
            <div class="live-badge"><span class="pulse-dot"></span> LIVE SYSTEM</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        page = st.radio("◈ NAVIGATE", [
            "◈ Command Center",
            "◈ City Intelligence",
            "◈ AI Agent Reports",
            "◈ Pipeline Operations",
            "◈ Project Architecture",
            "◈ Engineer Profile"
        ])

        st.divider()

        if st.button("⟳ SYNC DATA"):
            st.cache_data.clear()
            st.rerun()

        st.divider()

        st.markdown("""
        <div style="text-align:center;">
            <div style="color:rgba(0,212,255,0.4); font-size:0.65rem; letter-spacing:2px; margin-bottom:12px;">
                ◈ BUILT BY
            </div>
            <div style="font-family:'Orbitron',monospace; color:#00d4ff; font-size:0.9rem; font-weight:700;">
                HARSHIT SHUKLA
            </div>
            <div style="margin-top:14px; display:flex; flex-direction:column; gap:8px;">
                <a href="https://www.linkedin.com/in/harshit-shukla-data-engineer/" target="_blank" style="font-size:0.8rem;">⬡ LinkedIn</a>
                <a href="https://github.com/harshitshukla1" target="_blank" style="font-size:0.8rem;">⬡ GitHub</a>
                <a href="mailto:harshitshukla003@gmail.com" style="font-size:0.8rem;">⬡ Email</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown(f"""
        <div style="text-align:center; color:rgba(0,212,255,0.3); font-size:0.65rem;">
            © {datetime.now().year} HARSHIT SHUKLA<br>AI WEATHER INTELLIGENCE
        </div>
        """, unsafe_allow_html=True)

    df, source = load_latest_data()
    report = load_latest_report()
    logs = load_pipeline_logs()

    # ── PAGE 1: COMMAND CENTER ──
    if page == "◈ Command Center":
        st.markdown("""
        <div style="text-align:center; padding:30px 0 10px;">
            <div class="hero-title">◈ AI WEATHER INTELLIGENCE</div>
            <div class="hero-sub">Real-Time Global Monitoring • Agentic AI • AWS Cloud</div>
            <div style="margin-top:16px;"><div class="live-badge"><span class="pulse-dot"></span> PIPELINE ACTIVE</div></div>
        </div>
        """, unsafe_allow_html=True)

        if df is None:
            st.error(f"❌ Data unavailable: {source}")
            show_debug_info()
            return

        st.divider()
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: st.metric("◈ CITIES", len(df))
        with c2: st.metric("TEMP AVG", f"{round(df['temperature_c'].mean(),1)}°C")
        with c3: st.metric("HUMIDITY", f"{round(df['humidity_pct'].mean(),1)}%")
        with c4:
            rain = int(df["is_raining"].sum()) if "is_raining" in df.columns else 0
            st.metric("RAINING", f"{rain} CITIES")
        with c5:
            a = 0
            if report and isinstance(report.get("anomalies"), dict):
                a = report["anomalies"].get("count", 0)
            st.metric("ANOMALIES", a)
        with c6: st.metric("AI MODEL", "LLAMA 3.3")

        st.divider()
        st.markdown("### ◈ GLOBAL TEMPERATURE MAP")
        fig_map = px.scatter_geo(
            df, lat="latitude", lon="longitude", color="temperature_c",
            hover_name="city",
            hover_data={"temperature_c": True, "humidity_pct": True, "latitude": False, "longitude": False},
            size=[abs(t) + 15 for t in df["temperature_c"]],
            size_max=30, color_continuous_scale="plasma"
        )
        fig_map.update_layout(
            height=480, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=0, b=0),
            font=dict(color="#8892b0"),
            geo=dict(
                bgcolor="rgba(0,5,20,0.9)", landcolor="#0a1628", oceancolor="#000510",
                showocean=True, lakecolor="#000510", coastlinecolor="#00d4ff",
                countrycolor="rgba(0,212,255,0.15)", showland=True, showcoastlines=True, showcountries=True
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("### ◈ TEMPERATURE RANKING")
            df_sorted = df.sort_values("temperature_c", ascending=True)
            fig = go.Figure(go.Bar(
                x=df_sorted["temperature_c"], y=df_sorted["city"], orientation="h",
                marker=dict(color=df_sorted["temperature_c"], colorscale="plasma"),
                text=[f"{t}°C" for t in df_sorted["temperature_c"]], textposition="outside",
                textfont=dict(color="#8892b0", size=11)
            ))
            dark_layout(fig, 380)
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown("### ◈ HUMIDITY MATRIX")
            df_sorted2 = df.sort_values("humidity_pct", ascending=True)
            fig2 = go.Figure(go.Bar(
                x=df_sorted2["humidity_pct"], y=df_sorted2["city"], orientation="h",
                marker=dict(color=df_sorted2["humidity_pct"], colorscale="Blues"),
                text=[f"{h}%" for h in df_sorted2["humidity_pct"]], textposition="outside",
                textfont=dict(color="#8892b0", size=11)
            ))
            dark_layout(fig2, 380)
            st.plotly_chart(fig2, use_container_width=True)

        if all(c in df.columns for c in ["temperature_c", "humidity_pct"]):
            st.markdown("### ◈ TEMP vs HUMIDITY INTELLIGENCE MATRIX")
            fig3 = px.scatter(
                df, x="temperature_c", y="humidity_pct",
                color="comfort_level" if "comfort_level" in df.columns else "city",
                size="wind_speed_ms" if "wind_speed_ms" in df.columns else None,
                size_max=30, hover_name="city", text="city",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig3.update_traces(textposition="top center", textfont=dict(color="#8892b0", size=10))
            dark_layout(fig3, 420)
            st.plotly_chart(fig3, use_container_width=True)

    # ── PAGE 2: CITY INTELLIGENCE ──
    elif page == "◈ City Intelligence":
        st.markdown("""
        <div class="hero-title" style="font-size:1.8rem;">◈ CITY INTELLIGENCE MODULE</div>
        <div class="hero-sub">Deep analysis of individual city weather patterns</div>
        """, unsafe_allow_html=True)

        if df is None:
            st.error(f"❌ Data unavailable: {source}")
            show_debug_info()
            return

        st.divider()
        selected = st.selectbox("◈ SELECT TARGET CITY", df["city"].tolist())
        city = df[df["city"] == selected].iloc[0]

        st.markdown(f"### ◈ {selected.upper()} — MULTI-DIMENSIONAL ANALYSIS")
        categories = ["Temperature", "Humidity", "Wind Speed", "Cloud Cover"]
        max_vals = [60, 100, 30, 100]
        raw_vals = [float(city.get("temperature_c", 0)), float(city.get("humidity_pct", 0)),
                    float(city.get("wind_speed_ms", 0)), float(city.get("cloud_cover_pct", 0))]
        norm_vals = [min(v/m*100, 100) for v, m in zip(raw_vals, max_vals)]
        norm_vals.append(norm_vals[0])
        cats = categories + [categories[0]]

        fig_radar = go.Figure(go.Scatterpolar(
            r=norm_vals, theta=cats, fill="toself",
            fillcolor="rgba(0,212,255,0.1)", line=dict(color="#00d4ff", width=2),
            marker=dict(color="#00d4ff", size=6)
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(0,5,15,0.5)",
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#8892b0", size=9), gridcolor="rgba(0,212,255,0.1)"),
                angularaxis=dict(tickfont=dict(color="#00d4ff", size=11), gridcolor="rgba(0,212,255,0.1)")
            ),
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#8892b0"), height=380
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("◈ TEMPERATURE", f"{city['temperature_c']}°C")
        with c2: st.metric("◈ HUMIDITY", f"{city['humidity_pct']}%")
        with c3: st.metric("◈ WIND SPEED", f"{city.get('wind_speed_ms',0)} m/s")
        with c4: st.metric("◈ CLOUD COVER", f"{city.get('cloud_cover_pct',0)}%")

        c5, c6, c7, c8 = st.columns(4)
        with c5: st.metric("◈ CONDITION", str(city.get("weather_condition","N/A")))
        with c6: st.metric("◈ COMFORT", str(city.get("comfort_level","N/A")))
        with c7: st.metric("◈ CATEGORY", str(city.get("temp_category","N/A")))
        with c8: st.metric("◈ RAINING", "YES" if city.get("is_raining") else "NO")

        st.divider()
        st.markdown("### ◈ AI-GENERATED INTELLIGENCE")
        ca, cb, cc = st.columns(3)
        with ca: st.info(f"◈ **TRAVEL ADVISORY**\n\n{city.get('travel_tip','Run pipeline')}")
        with cb: st.success(f"◈ **ACTIVITY INTEL**\n\n{city.get('activity','Run pipeline')}")
        with cc: st.warning(f"◈ **HEALTH PROTOCOL**\n\n{city.get('health_tip','Run pipeline')}")

        st.divider()
        st.markdown("### ◈ CITY VS GLOBAL BENCHMARK")
        fig_cmp = go.Figure()
        metrics = ["Temperature", "Humidity", "Wind Speed", "Cloud Cover"]
        city_v = [city.get("temperature_c",0), city.get("humidity_pct",0), city.get("wind_speed_ms",0), city.get("cloud_cover_pct",0)]
        global_v = [df["temperature_c"].mean(), df["humidity_pct"].mean(), df["wind_speed_ms"].mean(), df["cloud_cover_pct"].mean()]
        fig_cmp.add_trace(go.Bar(name=selected, x=metrics, y=city_v, marker=dict(color="rgba(0,212,255,0.8)")))
        fig_cmp.add_trace(go.Bar(name="Global Avg", x=metrics, y=global_v, marker=dict(color="rgba(255,100,100,0.6)")))
        fig_cmp.update_layout(barmode="group")
        dark_layout(fig_cmp, 350)
        st.plotly_chart(fig_cmp, use_container_width=True)

        st.divider()
        st.markdown("### ◈ FULL DATA MATRIX")
        cols = [c for c in ["city","temperature_c","humidity_pct","wind_speed_ms","weather_condition","temp_category","comfort_level","is_raining"] if c in df.columns]
        st.dataframe(df[cols].sort_values("temperature_c", ascending=False), use_container_width=True, hide_index=True)

    # ── PAGE 3: AI AGENT REPORTS ──
    elif page == "◈ AI Agent Reports":
        st.markdown("""
        <div class="hero-title" style="font-size:1.8rem;">◈ AI AGENT OPERATIONS</div>
        <div class="hero-sub">Powered by Groq • Llama 3.3 70B • Agentic Intelligence</div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### ◈ ACTIVE AI CAPABILITIES")
        ca, cb, cc, cd = st.columns(4)
        with ca:
            st.markdown("""<div class="ai-cap-card"><div style="font-size:2rem;">🔍</div><div style="color:#00d4ff; font-size:0.75rem; letter-spacing:2px; margin:8px 0;">ANOMALY DETECTION</div><div style="color:#00ff88; font-size:0.7rem;">IQR Method</div></div>""", unsafe_allow_html=True)
        with cb:
            st.markdown("""<div class="ai-cap-card"><div style="font-size:2rem;">🧠</div><div style="color:#00d4ff; font-size:0.75rem; letter-spacing:2px; margin:8px 0;">CITY INSIGHTS</div><div style="color:#00ff88; font-size:0.7rem;">Natural Language</div></div>""", unsafe_allow_html=True)
        with cc:
            st.markdown("""<div class="ai-cap-card"><div style="font-size:2rem;">📋</div><div style="color:#00d4ff; font-size:0.75rem; letter-spacing:2px; margin:8px 0;">AUTO REPORTS</div><div style="color:#00ff88; font-size:0.7rem;">Zero Human Input</div></div>""", unsafe_allow_html=True)
        with cd:
            st.markdown("""<div class="ai-cap-card"><div style="font-size:2rem;">🔧</div><div style="color:#00d4ff; font-size:0.75rem; letter-spacing:2px; margin:8px 0;">SELF-HEALING</div><div style="color:#00ff88; font-size:0.7rem;">Error Diagnosis</div></div>""", unsafe_allow_html=True)

        st.divider()
        if report:
            st.markdown("### ◈ LATEST AI PIPELINE REPORT")
            st.info(report.get('pipeline_report','No report available'))

            st.divider()
            st.markdown("### ◈ ANOMALY SCAN RESULTS")
            anom = report.get("anomalies", {})
            if isinstance(anom, dict) and anom.get("count", 0) > 0:
                st.error(f"🚨 ALERT: {anom['count']} anomalies detected by AI Agent")
                for a in anom.get("anomalies", []):
                    with st.expander(f"{a['city'].upper()} — {a['metric'].upper()} — SEVERITY: {a['severity']}"):
                        c1, c2, c3 = st.columns(3)
                        with c1: st.metric("DETECTED VALUE", a["value"])
                        with c2: st.metric("NORMAL RANGE", a["normal_range"])
                        with c3: st.metric("SEVERITY", a["severity"])
                if anom.get("explanation"):
                    st.warning(f"◈ **AI EXPLANATION:**\n\n{anom['explanation']}")
            else:
                st.success("◈ SYSTEM NOMINAL — No anomalies detected")

            st.divider()
            stats = report.get("summary_stats", {})
            st.markdown("### ◈ INTELLIGENCE SUMMARY")
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("AVG TEMPERATURE", f"{stats.get('avg_temp_c','N/A')}°C")
            with c2: st.metric("AVG HUMIDITY", f"{stats.get('avg_humidity','N/A')}%")
            with c3: st.metric("RAINING CITIES", stats.get("raining_count",0))
        else:
            st.warning("◈ No AI reports found")
            show_debug_info()

    # ── PAGE 4: PIPELINE OPERATIONS ──
    elif page == "◈ Pipeline Operations":
        st.markdown("""
        <div class="hero-title" style="font-size:1.8rem;">◈ PIPELINE OPERATIONS CENTER</div>
        <div class="hero-sub">Real-time monitoring • CI/CD automation • AWS infrastructure</div>
        """, unsafe_allow_html=True)

        st.divider()
        if logs:
            latest = logs[0]
            status = latest.get("status","unknown")
            if status == "success":
                st.success("◈ ALL SYSTEMS OPERATIONAL — Last run completed successfully")
            else:
                st.error("◈ SYSTEM ALERT — Last run encountered errors")

            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("RUN ID", latest.get("run_id","N/A"))
            with c2: st.metric("DURATION", f"{latest.get('total_duration_sec',0)}s")
            with c3: st.metric("RECORDS", latest.get("final_record_count",0))
            with c4: st.metric("VERSION", latest.get("pipeline_version","1.0.0"))

            st.divider()
            st.markdown("### ◈ EXECUTION HISTORY")
            history = []
            for log in logs:
                history.append({
                    "RUN ID": log.get("run_id","N/A"),
                    "STATUS": "✅ SUCCESS" if log.get("status")=="success" else "❌ FAILED",
                    "DURATION": f"{log.get('total_duration_sec',0)}s",
                    "RECORDS": log.get("final_record_count",0),
                    "TIMESTAMP": log.get("started_at_utc","N/A")[:19]
                })
            st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("### ◈ S3 DATA LAKE STATUS")
            s3 = get_s3_client()
            bucket = get_secret("S3_BUCKET_NAME")
            
            if s3 and bucket:
                folders = {"raw/": ("◈ RAW DATA", "Source of truth"), "processed/": ("◈ PROCESSED", "Parquet format"),
                           "reports/": ("◈ AI REPORTS", "Intelligence layer"), "logs/": ("◈ AUDIT LOGS", "Run history")}
                cols = st.columns(4)
                for i, (prefix, (label, desc)) in enumerate(folders.items()):
                    with cols[i]:
                        try:
                            r = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
                            count = len(r.get("Contents", []))
                            size = sum(o["Size"] for o in r.get("Contents", [])) / 1024
                            st.metric(label, f"{count} FILES")
                            st.caption(f"{size:.1f} KB • {desc}")
                        except:
                            st.metric(label, "N/A")
            else:
                st.error("Could not connect to S3")
                show_debug_info()
        else:
            st.warning("◈ No pipeline logs detected")
            show_debug_info()

    # ── PAGE 5: PROJECT ARCHITECTURE ──
    elif page == "◈ Project Architecture":
        st.markdown("""
        <div class="hero-title" style="font-size:1.8rem;">◈ PROJECT ARCHITECTURE</div>
        <div class="hero-sub">What we built • Why it matters • How AI makes it different</div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### ◈ PROBLEM STATEMENT")
        st.error("""
**THE PROBLEM**

Logistics companies, event planners, agriculture firms, and travel businesses make critical decisions based on weather — yet most rely on **manual weather checks**, **outdated data**, and **gut-feeling decisions**.

A delivery operations manager manually checks 10-15 cities every morning. That is **45 minutes wasted daily**, **₹3L+ monthly losses** from weather-delayed deliveries.
        """)

        st.divider()
        st.markdown("### ◈ OUR SOLUTION")
        st.success("""
**AI-POWERED PIPELINE**

A **fully automated AI-powered data pipeline** that collects real-time weather data for 10+ cities every 12 hours, cleans and enriches it using production-grade transformation, runs it through an **Agentic AI (Llama 3.3 70B)**, stores everything in **AWS S3 data lake**, and presents live insights here — **all at $0/month, completely automated.**
        """)

        st.divider()
        st.markdown("### ◈ INTERACTIVE PIPELINE WORKFLOW")
        st.caption("See how data flows through the system in real-time")

        workflow_stages = [
            ("◈ STAGE 01 — TRIGGER", "GitHub Actions Scheduler fires at 6 AM & 6 PM IST daily — fully automated"),
            ("◈ STAGE 02 — EXTRACTION", "Python extractor hits Open-Meteo API for 10 cities • Retry logic • Raw JSON to AWS S3"),
            ("◈ STAGE 03 — TRANSFORMATION", "Pandas cleans data • 5 quality dimensions • Feature engineering • Parquet format"),
            ("◈ STAGE 04 — AI AGENT", "Groq Llama 3.3 70B detects anomalies • Generates insights • Writes reports"),
            ("◈ STAGE 05 — STORAGE", "All outputs saved to S3 with Hive partitioning • Audit logs • Versioning"),
            ("◈ STAGE 06 — VISUALIZATION", "This dashboard pulls latest data from S3 • Live charts • Auto-refreshes")
        ]

        for i, (title, desc) in enumerate(workflow_stages):
            st.markdown(f"""
            <div class="workflow-step">
                <div style="color:#00d4ff; font-family:'Orbitron',monospace; font-size:0.85rem; letter-spacing:2px;">{title}</div>
                <div style="color:#e6f1ff; margin-top:6px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if i < len(workflow_stages) - 1:
                st.markdown('<div class="workflow-arrow">▼</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("### ◈ WHAT AI IS DOING IN THIS PROJECT")
        st.caption("4 autonomous AI capabilities running per pipeline execution")

        tab1, tab2, tab3, tab4 = st.tabs(["◈ ANOMALY DETECTION", "◈ CITY INSIGHTS", "◈ AUTO REPORTS", "◈ SELF-HEALING"])

        with tab1:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("""
**AI Capability 01 — Anomaly Detection**

AI uses **IQR (Interquartile Range)** statistical method to identify cities with unusual weather patterns. Llama 3.3 70B explains the anomaly in plain English.

**How it works:**
- Calculate Q1, Q3, IQR for each metric
- Flag values outside Q1 - 1.5×IQR or Q3 + 1.5×IQR
- Send anomalies to AI for explanation
- AI assesses business impact and severity
                """)
            with c2:
                st.markdown("""<div class="ai-cap-card"><div style="font-size:3rem;">🔍</div><div style="color:#00d4ff; margin-top:10px;">PROACTIVE ALERTS</div><div style="color:#00ff88; font-size:0.85rem; margin-top:8px;">Before problems occur</div></div>""", unsafe_allow_html=True)

        with tab2:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("""
**AI Capability 02 — City Intelligence Generation**

For every city, Llama 3.3 70B generates contextual travel advisories, health recommendations, and activity suggestions based on actual live weather data.

**How it works:**
- Build batch prompt with all 10 cities
- Send single API call (cost-efficient)
- AI returns structured JSON with insights
- Parse and merge with main DataFrame
                """)
            with c2:
                st.markdown("""<div class="ai-cap-card"><div style="font-size:3rem;">🧠</div><div style="color:#00d4ff; margin-top:10px;">PERSONALIZED</div><div style="color:#00ff88; font-size:0.85rem; margin-top:8px;">10 cities, 1 API call</div></div>""", unsafe_allow_html=True)

        with tab3:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("""
**AI Capability 03 — Automated Pipeline Reports**

After every pipeline run, the AI agent writes a complete executive-level report in natural language — with zero human input.

**How it works:**
- Aggregate pipeline statistics
- Send context to Llama 3.3 70B
- AI generates structured markdown report
- Saved to S3 reports/ folder
                """)
            with c2:
                st.markdown("""<div class="ai-cap-card"><div style="font-size:3rem;">📋</div><div style="color:#00d4ff; margin-top:10px;">ZERO INPUT</div><div style="color:#00ff88; font-size:0.85rem; margin-top:8px;">Replaces manual reporting</div></div>""", unsafe_allow_html=True)

        with tab4:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("""
**AI Capability 04 — Self-Healing Error Diagnosis**

When the pipeline fails, the AI agent analyzes the error traceback and suggests specific fixes in plain English.

**How it works:**
- Catch exception in pipeline orchestrator
- Send traceback + context to AI
- AI diagnoses root cause
- Suggests specific code fixes
                """)
            with c2:
                st.markdown("""<div class="ai-cap-card"><div style="font-size:3rem;">🔧</div><div style="color:#00d4ff; margin-top:10px;">SMART DEBUG</div><div style="color:#00ff88; font-size:0.85rem; margin-top:8px;">Hours → seconds</div></div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown("### ◈ WHAT WE BYPASSED vs TRADITIONAL APPROACH")
        st.markdown("""
| Traditional Approach | ⚡ Our Approach | Time/Cost Saved |
|---------------------|----------------|-----------------|
| Local machine setup | GitHub Codespace (cloud IDE) | 2 hours |
| Buy server / EC2 | GitHub Actions (free CI/CD) | $50/month |
| AWS Redshift ($180/mo) | AWS Athena (~$0/query) | $180/month |
| Apache Airflow + Docker | GitHub Actions YAML | 8 hours setup |
| Manual API key management | GitHub Secrets (encrypted) | Security risk eliminated |
| CSV storage (slow) | Parquet columnar (10x faster) | Query cost reduced |
| No AI layer | Agentic Groq AI (free) | Unique differentiator |
| 3-4 weeks to build | Built in 1 session | Weeks saved |
        """)

        st.divider()
        st.markdown("### ◈ COMPLETE TECHNOLOGY ARSENAL")
        tech_categories = {
            "☁️ CLOUD": ["AWS S3", "AWS IAM", "AWS Athena", "AWS CloudWatch", "Snowflake"],
            "🐍 CORE": ["Python 3.11", "Pandas", "NumPy", "PyArrow"],
            "🤖 AI/ML": ["Groq API", "Llama 3.3 70B", "Prompt Engineering", "Agentic AI", "LangChain", "LangGraph"],
            "🔄 PIPELINE": ["GitHub Actions", "CI/CD", "Hive Partitioning", "Parquet"],
            "📊 DASHBOARD": ["Streamlit", "Plotly", "Streamlit Cloud"],
            "🔧 TOOLS": ["GitHub Codespace", "VS Code", "Loguru", "Boto3"]
        }
        for cat, tools in tech_categories.items():
            st.markdown(f"**{cat}**")
            badges = " ".join([f'<span class="tech-badge">{t}</span>' for t in tools])
            st.markdown(f"<div style='margin-bottom:12px;'>{badges}</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("### ◈ BUSINESS IMPACT & ROI")
        st.markdown("""
| Business Area | Before | After | Monthly Saving |
|---------------|--------|-------|----------------|
| Manual weather monitoring | 45 min/day | 0 minutes | ₹15,000 |
| Late delivery compensation | 20% late | 5% late | ₹2,25,000 |
| Driver safety incidents | Reactive | Proactive | ₹30,000 |
| Data-driven decisions | Gut feeling | AI recommendations | Immeasurable |
| **TOTAL** | **Wastage** | **Optimized** | **₹2,70,000/month** |
        """)

        st.markdown("""
        <div class="scifi-card" style="text-align:center; margin-top:20px;">
            <div style="font-size:0.75rem; color:rgba(0,212,255,0.5); letter-spacing:3px; margin-bottom:12px;">◈ PIPELINE TOTAL COST</div>
            <div class="stat-number">$0</div>
            <div style="color:rgba(0,212,255,0.5); font-size:0.8rem; letter-spacing:2px; margin-top:8px;">PER MONTH — FOREVER</div>
        </div>
        """, unsafe_allow_html=True)

    # ── PAGE 6: ENGINEER PROFILE ──
    elif page == "◈ Engineer Profile":
        st.markdown("""
        <div class="hero-title" style="font-size:1.8rem;">◈ ENGINEER PROFILE</div>
        <div class="hero-sub">The human behind the machine</div>
        """, unsafe_allow_html=True)

        st.divider()

        st.markdown("""
        <div class="scifi-card" style="text-align:center; padding:40px;">
            <div style="font-family:'Orbitron',monospace; font-size:2rem; font-weight:900; color:#00d4ff; text-shadow: 0 0 20px rgba(0,212,255,0.5); letter-spacing:4px;">
                HARSHIT SHUKLA
            </div>
            <div style="color:rgba(0,212,255,0.6); font-size:0.8rem; letter-spacing:3px; margin:10px 0;">
                DATA ENGINEER • AI PRACTITIONER • CLOUD ARCHITECT
            </div>
            <div style="color:#8892b0; font-size:0.85rem; margin:8px 0;">
                📍 Bengaluru, India • 4+ Years Experience
            </div>
            <div style="margin-top:16px; display:flex; justify-content:center; gap:20px; flex-wrap:wrap;">
                <a href="https://www.linkedin.com/in/harshit-shukla-data-engineer/" target="_blank">⬡ LinkedIn</a>
                <a href="https://github.com/harshitshukla1" target="_blank">⬡ GitHub</a>
                <a href="mailto:harshitshukla003@gmail.com">⬡ Email</a>
                <a href="tel:+917905862704">⬡ +91-7905862704</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # 1. PROFESSIONAL SUMMARY
        st.markdown("### ◈ PROFESSIONAL SUMMARY")
        st.info("""
**Harshit Shukla** is a seasoned **Data Engineer with 4+ years** of hands-on experience building **scalable ETL/ELT pipelines** and **cloud-based data platforms** using AWS, Snowflake, Databricks, Apache Spark, Kafka, Airflow, and Delta Lake.

Having worked at **Wipro Limited** (Nike Clickstream Platform — 50M+ events/day, Healthcare JNJ MDR) and currently at **RM Private Limited** (1-2M order transactions/day from 5000+ vendors), **Harshit** has proven ability to design and deliver production systems at scale.

**Harshit Shukla** has **intermediate knowledge in AI** and is actively expanding expertise in **Agentic AI, LangChain, LangGraph, and Prompt Engineering**. What sets **Harshit** apart is the ability to leverage **modern AI tools** (Cursor AI, ChatGPT, Claude, Gemini, NotebookLM, Perplexity, GitHub Copilot, v0.dev, Lovable, Replit AI) to dramatically accelerate development — building in hours what traditionally takes weeks.

This project itself is proof: a complete AI-enhanced data engineering pipeline built in a **single session, zero local machine, $0 cost**.
        """)

        st.divider()

        # 2. AI TOOLS MASTERY
        st.markdown("### ◈ AI TOOLS MASTERY — 10X PRODUCTIVITY")
        st.markdown("**Harshit Shukla** represents the next generation of data engineers who don't just *know* tools but *multiply* their output using AI.")

        st.success("""
**THIS PROJECT IS LIVE PROOF:**

✓ Built complete production pipeline **without a local machine**

✓ Used GitHub Codespace (cloud IDE) — no setup, no installs locally

✓ Integrated Agentic AI (Groq + Llama 3.3 70B) for intelligence layer

✓ CI/CD automated with GitHub Actions — pipeline runs itself

✓ Zero cost architecture on AWS free tier

✓ Production deployment in **1 session** vs traditional 3-4 weeks
        """)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""<div class="ai-cap-card"><div style="font-size:2.5rem;">⚡</div><div style="color:#00d4ff; margin-top:10px; font-size:0.85rem;">10X SPEED</div><div style="color:#00ff88; font-size:0.75rem; margin-top:6px;">vs traditional dev</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""<div class="ai-cap-card"><div style="font-size:2.5rem;">💰</div><div style="color:#00d4ff; margin-top:10px; font-size:0.85rem;">$0 COST</div><div style="color:#00ff88; font-size:0.75rem; margin-top:6px;">Free tier mastery</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""<div class="ai-cap-card"><div style="font-size:2.5rem;">🚀</div><div style="color:#00d4ff; margin-top:10px; font-size:0.85rem;">PRODUCTION READY</div><div style="color:#00ff88; font-size:0.75rem; margin-top:6px;">CI/CD automated</div></div>""", unsafe_allow_html=True)

        st.divider()

        # 3. TECHNICAL ARSENAL
        st.markdown("### ◈ TECHNICAL ARSENAL")
        skills = {
            "PROGRAMMING": {"skills": ["Python", "SQL", "PySpark", "Shell Scripting"], "level": 90},
            "BIG DATA & CLOUD": {"skills": ["Apache Spark", "AWS S3", "AWS Databricks", "Snowflake", "Delta Lake", "Kafka"], "level": 88},
            "ORCHESTRATION": {"skills": ["Apache Airflow", "GitHub Actions", "DAG Management", "CI/CD"], "level": 85},
            "DATA ARCHITECTURE": {"skills": ["Medallion Architecture", "ETL/ELT Design", "Data Warehousing", "Parquet", "Snowflake Schema"], "level": 87},
            "AI & AGENTIC SYSTEMS": {"skills": ["Groq AI", "Llama 3.3", "LangChain", "LangGraph", "Prompt Engineering", "Agentic AI", "RAG"], "level": 75},
            "AI PRODUCTIVITY TOOLS": {"skills": ["Cursor AI", "GitHub Copilot", "ChatGPT", "Claude", "Gemini", "NotebookLM", "Perplexity", "v0.dev", "Lovable"], "level": 95},
            "DATA QUALITY": {"skills": ["Schema Validation", "Deduplication", "Custom DQ Frameworks", "Great Expectations"], "level": 85}
        }
        for skill_cat, data in skills.items():
            with st.expander(skill_cat):
                badges = " ".join([f'<span class="tech-badge">{s}</span>' for s in data["skills"]])
                st.markdown(badges, unsafe_allow_html=True)
                st.progress(data["level"] / 100)
                st.caption(f"Proficiency: {data['level']}%")

        st.divider()

        # 4. PROFESSIONAL EXPERIENCE
        st.markdown("### ◈ PROFESSIONAL EXPERIENCE")
        with st.expander("RM PRIVATE LIMITED — Data Engineering Consultant (Aug 2024 – Present)"):
            st.markdown("""
- Designed end-to-end **Medallion Architecture** (Bronze, Silver, Gold) on AWS Databricks
- Built **Kafka and REST API ingestion pipelines** from vendor databases, APIs, purchase systems
- Processed **1-2 million order transactions daily from 5000+ vendors**
- Developed scalable PySpark transformations: schema validation, deduplication, JSON flattening
- Created Gold layer Delta tables for vendor performance analytics, sales reporting
- Orchestrated batch and near real-time ETL workflows using **Apache Airflow**
- Implemented data quality frameworks, Delta Lake optimization
- Configured CI/CD deployment workflows
- Developed **AI-powered support assistant** for pipeline failure analysis
- Supporting business operations with **INR 10-20 Crore revenue transactions**
            """)

        with st.expander("WIPRO LIMITED, BENGALURU — Data Engineer (Mar 2022 – Aug 2024)"):
            st.markdown("""
**Nike Clickstream Data Platform:**
- Designed Medallion Architecture pipelines processing **50M+ clickstream events daily**
- Built Kafka-based ingestion pipelines storing raw JSON in AWS S3 Bronze layer
- Developed optimized PySpark jobs **reducing processing time by 30%**
- Orchestrated ETL workflows using Apache Airflow achieving **99.9% pipeline reliability**

**Healthcare Data Platform (JNJ MDR):**
- Built ETL pipelines using PySpark on Databricks for healthcare regulatory datasets
- Integrated Kafka streaming and batch ingestion workflows
- Built validation frameworks achieving **99.9% data accuracy**
- Optimized SQL queries **improving performance by 25%**
            """)

        st.divider()

        # 5. AI IN DATA ENGINEERING
        st.markdown("### ◈ HOW I USE AI IN DATA ENGINEERING — END TO END")
        st.caption("Complete AI-augmented workflow across the entire data engineering lifecycle")

        de_workflow = [
            ("📋 REQUIREMENT GATHERING", "**ChatGPT + Claude** — Convert business requirements into technical specs"),
            ("🏗️ ARCHITECTURE DESIGN", "**Claude + Gemini** — Design medallion architecture, recommend tech stack"),
            ("📝 DOCUMENTATION", "**NotebookLM + Gemini** — Auto-generate technical docs, API references"),
            ("💻 CODE WRITING", "**Cursor AI + Copilot** — Write PySpark, Airflow DAGs, SQL queries 5x faster"),
            ("🐛 DEBUGGING", "**Claude + ChatGPT** — Paste error traceback, get specific fix suggestions"),
            ("🧪 TESTING", "**Cursor AI** — Auto-generate pytest cases, edge cases, integration tests"),
            ("🔍 CODE REVIEW", "**GitHub Copilot + Claude** — Review PRs, suggest optimizations"),
            ("📊 DATA ANALYSIS", "**Julius AI + ChatGPT** — Quick EDA, find patterns, generate charts"),
            ("🎓 LEARNING", "**Perplexity + NotebookLM** — Learn new tools fast with AI tutoring"),
            ("📹 KNOWLEDGE SHARING", "**Synthesia + Descript** — Create video tutorials, demos"),
            ("📑 PRESENTATIONS", "**Gamma AI + Beautiful.ai** — Generate stakeholder presentations"),
            ("🔄 PIPELINE MONITORING", "**Custom Agentic AI** — AI agents that monitor pipelines, alert on anomalies")
        ]

        for stage, desc in de_workflow:
            st.markdown(f"""
            <div class="workflow-step">
                <div style="color:#00d4ff; font-family:'Orbitron',monospace; font-size:0.8rem; letter-spacing:2px;">{stage}</div>
                <div style="color:#e6f1ff; margin-top:6px; font-size:0.95rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # 6. AGENTIC AI EXPERTISE
        st.markdown("### ◈ AGENTIC AI & LANGCHAIN EXPERTISE")
        st.warning("""
**Harshit** understands and implements **Agentic AI** patterns where AI doesn't just answer questions but **takes actions**:

**→ LangChain Framework** — Chaining multiple AI calls with memory and context

**→ LangGraph** — Building stateful, multi-step AI agent workflows with branching logic

**→ Prompt Engineering** — Crafting precise prompts for structured JSON output from LLMs

**→ Tool Use / Function Calling** — AI agents that call APIs, query databases, analyze data autonomously

**→ Multi-Agent Systems** — Orchestrating multiple specialized AI agents that collaborate

**→ RAG (Retrieval Augmented Generation)** — Connecting LLMs to vector databases

**→ Self-Healing Systems** — AI that diagnoses its own pipeline errors and suggests fixes

**→ Vector Databases** — Pinecone, ChromaDB, FAISS for semantic search and AI memory

In this project, the AI Agent performs **4 autonomous actions** per pipeline run without any human input.
        """)

        st.divider()

        # 7. AI TOOLS I USE DAILY
        st.markdown("### ◈ AI TOOLS I USE DAILY")
        st.caption("25+ AI tools across 6 categories powering my daily workflow")

        ai_tools = {
            "💻 CODE GENERATION": [
                ("Cursor AI", "AI-powered code editor — writes & refactors entire files"),
                ("GitHub Copilot", "Context-aware code generation"),
                ("Claude", "Complex code reasoning, debugging, architecture design"),
                ("ChatGPT", "Code review, problem solving, documentation"),
                ("Replit AI", "Browser-based AI coding for quick prototypes")
            ],
            "📚 RESEARCH & LEARNING": [
                ("Perplexity AI", "Real-time research with citations — replaces Google"),
                ("Google Gemini", "Multimodal AI for code, images, deep research"),
                ("NotebookLM", "Upload PDFs/docs → AI creates podcasts, summaries, Q&A"),
                ("Anthropic Claude", "Long-context analysis of large codebases")
            ],
            "🎨 CONTENT & DESIGN": [
                ("v0.dev", "Generate beautiful UI components from text prompts"),
                ("Lovable", "Build full-stack web apps with AI"),
                ("Canva AI", "Quick presentations, infographics, social media posts"),
                ("Gamma AI", "AI-generated presentations from one-line prompts"),
                ("Beautiful.ai", "Smart slides with auto-formatting")
            ],
            "🎬 VIDEO & AUDIO": [
                ("Synthesia", "AI avatar videos for tutorials & demos"),
                ("Descript", "Edit videos by editing text transcripts"),
                ("Eleven Labs", "Realistic AI voice generation for narration"),
                ("HeyGen", "AI-generated talking head videos"),
                ("Runway ML", "Video generation and editing with AI")
            ],
            "📊 DATA & ANALYSIS": [
                ("Julius AI", "Chat with your CSV/Excel data — instant analysis"),
                ("DataLab", "AI-powered notebooks for data exploration"),
                ("ChatGPT Code Interpreter", "Upload data, AI does analysis & charts"),
                ("Hex", "AI-augmented data notebooks for teams")
            ],
            "🤖 WORKFLOW AUTOMATION": [
                ("Zapier AI", "Connect apps with AI-powered automations"),
                ("Make.com", "Visual workflow automation with AI nodes"),
                ("n8n", "Self-hosted automation with AI integrations")
            ]
        }

        for category, tools in ai_tools.items():
            with st.expander(category):
                for tool, desc in tools:
                    st.markdown(f"**{tool}** — {desc}")

        st.divider()

        # EDUCATION
        st.markdown("### ◈ EDUCATION & CERTIFICATIONS")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="scifi-card">
                <div style="color:#00d4ff; font-size:0.75rem; letter-spacing:2px; margin-bottom:8px;">◈ EDUCATION</div>
                <div style="color:#e6f1ff;">
                    <strong>B.Tech Computer Science</strong><br>
                    APJ Abdul Kalam Technical University<br>
                    <span style="color:#00d4ff;">2016 – 2020 • Aggregate: 77.3%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="scifi-card">
                <div style="color:#00d4ff; font-size:0.75rem; letter-spacing:2px; margin-bottom:8px;">◈ CERTIFICATIONS</div>
                <div style="color:#e6f1ff; line-height:2;">
                    → SQL Certification — Coding Ninjas<br>
                    → Python Certified Developer — Protec<br>
                    → Skillit — IIT Hyderabad<br>
                    → Data Science Job Simulation — Commonwealth Bank
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        st.markdown("""
        <div style="text-align:center; padding:40px 20px;">
            <div style="font-family:'Orbitron',monospace; font-size:1.1rem; color:rgba(0,212,255,0.4); letter-spacing:2px; margin-bottom:16px;">
                ◈ PHILOSOPHY
            </div>
            <div style="font-size:1.3rem; color:#e6f1ff; line-height:1.8; font-style:italic; max-width:700px; margin:0 auto;">
                "I don't write code for the sake of writing code.
                I orchestrate AI to build systems that
                <span style="color:#00d4ff; font-weight:700;">think, act, and scale</span>
                — while I focus on architecture and strategy."
            </div>
            <div style="margin-top:20px; font-family:'Orbitron',monospace; color:#00d4ff; font-size:0.9rem; letter-spacing:3px;">
                — HARSHIT SHUKLA
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── FOOTER ──
    st.markdown(f"""
    <div style="text-align:center; padding:24px; margin-top:40px; border-top:1px solid rgba(0,212,255,0.15);">
        <div style="font-family:'Orbitron',monospace; color:rgba(0,212,255,0.4); font-size:0.65rem; letter-spacing:3px; margin-bottom:8px;">
            ◈ AI WEATHER INTELLIGENCE PIPELINE
        </div>
        <div style="color:rgba(230,241,255,0.4); font-size:0.8rem;">
            Built by <strong style="color:#00d4ff;">Harshit Shukla</strong> •
            <a href="https://www.linkedin.com/in/harshit-shukla-data-engineer/">LinkedIn</a> •
            <a href="https://github.com/harshitshukla1">GitHub</a> •
            <a href="mailto:harshitshukla003@gmail.com">Email</a>
        </div>
        <div style="color:rgba(0,212,255,0.2); font-size:0.7rem; margin-top:6px; letter-spacing:2px;">
            POWERED BY GROQ AI • AWS S3 • SNOWFLAKE • LANGCHAIN • STREAMLIT
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()