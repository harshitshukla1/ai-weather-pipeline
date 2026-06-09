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

# ═══════════════════════════════════════════════
# CSS STYLING - MUST BE INSIDE st.markdown()
# ═══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

* { 
    font-family: 'Rajdhani', sans-serif !important;
    box-sizing: border-box;
}

#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header {visibility: hidden !important;}
[data-testid="stToolbar"] {visibility: hidden !important;}
[data-testid="stDecoration"] {display: none !important;}
[data-testid="stStatusWidget"] {visibility: hidden !important;}

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

.block-container {
    padding: 1rem !important;
    max-width: 100% !important;
}

@media (min-width: 768px) {
    .block-container {
        padding: 2rem !important;
        padding-bottom: 4rem !important;
    }
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #000510 0%, #001020 100%) !important;
    border-right: 1px solid rgba(0,212,255,0.2) !important;
}

@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        width: 250px !important;
    }
}

[data-testid="collapsedControl"] {
    color: #00d4ff !important;
    background: rgba(0,212,255,0.1) !important;
    border-radius: 8px !important;
    padding: 8px !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(0,212,255,0.05), rgba(0,100,200,0.03));
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 12px;
    padding: 12px !important;
    transition: all 0.4s ease;
    overflow: hidden;
    margin-bottom: 8px;
}

[data-testid="stMetric"]:hover {
    border-color: rgba(0,212,255,0.6);
    box-shadow: 0 0 20px rgba(0,212,255,0.2);
    transform: translateY(-3px);
}

[data-testid="stMetricLabel"] {
    color: rgba(0,212,255,0.7) !important;
    font-size: 0.65rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

[data-testid="stMetricValue"] {
    color: #00d4ff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: clamp(1rem, 3vw, 1.6rem) !important;
    font-weight: 700 !important;
    text-shadow: 0 0 10px rgba(0,212,255,0.5);
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

@media (max-width: 480px) {
    [data-testid="stMetricLabel"] {
        font-size: 0.55rem !important;
        letter-spacing: 1px !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 0.9rem !important;
    }
    [data-testid="stMetric"] {
        padding: 8px !important;
    }
}

h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    color: #00d4ff !important;
    letter-spacing: 2px !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}

h1 { font-size: clamp(1.2rem, 4vw, 2.5rem) !important; }
h2 { font-size: clamp(1rem, 3vw, 2rem) !important; }
h3 { font-size: clamp(0.9rem, 2.5vw, 1.5rem) !important; }

h2, h3 {
    border-bottom: 1px solid rgba(0,212,255,0.2);
    padding-bottom: 8px;
    color: #e6f1ff !important;
}

@media (max-width: 480px) {
    h1, h2, h3 { letter-spacing: 1px !important; }
}

.stButton > button {
    background: transparent !important;
    color: #00d4ff !important;
    border: 1px solid rgba(0,212,255,0.5) !important;
    border-radius: 4px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: clamp(0.6rem, 1.5vw, 0.8rem) !important;
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
    font-size: clamp(0.75rem, 1.8vw, 0.85rem) !important;
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
    margin: 1rem 0 !important;
}

.stAlert {
    background: rgba(0,212,255,0.05) !important;
    border: 1px solid rgba(0,212,255,0.2) !important;
    border-radius: 8px !important;
    color: #e6f1ff !important;
    padding: 12px !important;
    font-size: clamp(0.8rem, 2vw, 0.95rem) !important;
}

.stAlert > div {
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}

.stDataFrame {
    border: 1px solid rgba(0,212,255,0.2) !important;
    border-radius: 8px !important;
    overflow-x: auto !important;
    max-width: 100% !important;
}

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
    padding: 12px 16px !important;
    font-size: clamp(0.7rem, 1.8vw, 0.85rem) !important;
    letter-spacing: 1px !important;
    word-wrap: break-word !important;
}

[data-testid="stExpander"] details[open] {
    border-color: rgba(0,212,255,0.4) !important;
    background: rgba(0,212,255,0.05) !important;
}

.stSelectbox > div > div {
    background: rgba(0,10,20,0.8) !important;
    border-color: rgba(0,212,255,0.3) !important;
    color: #e6f1ff !important;
    font-size: clamp(0.8rem, 2vw, 0.95rem) !important;
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #000510; }
::-webkit-scrollbar-thumb {
    background: rgba(0,212,255,0.3);
    border-radius: 2px;
}

.scifi-card {
    background: linear-gradient(135deg, rgba(0,212,255,0.05), rgba(0,50,100,0.03));
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 12px;
    padding: clamp(16px, 3vw, 24px);
    margin: 10px 0;
    transition: all 0.4s ease;
    position: relative;
    overflow: hidden;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
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
    font-size: clamp(1.2rem, 5vw, 2.8rem);
    font-weight: 900;
    color: #00d4ff;
    text-shadow: 0 0 10px rgba(0,212,255,0.8), 0 0 30px rgba(0,212,255,0.4);
    letter-spacing: clamp(1px, 0.5vw, 4px);
    text-align: center;
    animation: glow 3s ease-in-out infinite alternate;
    word-wrap: break-word !important;
    line-height: 1.3 !important;
}

@keyframes glow {
    from { text-shadow: 0 0 10px rgba(0,212,255,0.8); }
    to { text-shadow: 0 0 20px rgba(0,212,255,1), 0 0 40px rgba(0,212,255,0.6); }
}

.hero-sub {
    font-size: clamp(0.6rem, 1.5vw, 1rem);
    color: rgba(230,241,255,0.6);
    text-align: center;
    letter-spacing: clamp(1px, 0.3vw, 3px);
    text-transform: uppercase;
    margin-top: 10px;
    padding: 0 10px;
}

.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0,255,136,0.1);
    border: 1px solid rgba(0,255,136,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: clamp(0.6rem, 1.5vw, 0.75rem);
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
    padding: 5px 12px;
    border-radius: 3px;
    font-size: clamp(0.6rem, 1.5vw, 0.75rem);
    border: 1px solid rgba(0,212,255,0.25);
    letter-spacing: 1px;
    margin: 3px;
    font-family: 'Orbitron', monospace;
    transition: all 0.3s ease;
    word-break: break-word !important;
}

.tech-badge:hover {
    background: rgba(0,212,255,0.2);
    transform: translateY(-2px);
}

.stat-number {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.5rem, 6vw, 3rem);
    font-weight: 900;
    color: #00d4ff;
    text-shadow: 0 0 20px rgba(0,212,255,0.5);
}

a {
    color: #00d4ff !important;
    text-decoration: none !important;
    word-break: break-word !important;
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
    padding: clamp(12px, 2vw, 16px) clamp(14px, 2.5vw, 20px);
    margin: 12px 0;
    transition: all 0.4s ease;
    animation: slideIn 0.6s ease-out;
    word-wrap: break-word !important;
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
    padding: clamp(12px, 2vw, 20px);
    text-align: center;
    transition: all 0.4s ease;
    height: 100%;
    min-height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    word-wrap: break-word !important;
}

.ai-cap-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 12px 40px rgba(0,212,255,0.25);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    flex-wrap: wrap !important;
    overflow-x: auto !important;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(0,212,255,0.05);
    border-radius: 8px;
    border: 1px solid rgba(0,212,255,0.15);
    color: #8892b0;
    font-family: 'Orbitron', monospace;
    letter-spacing: 1px;
    font-size: clamp(0.65rem, 1.5vw, 0.85rem) !important;
    padding: 8px 12px !important;
    white-space: nowrap !important;
}

.stTabs [aria-selected="true"] {
    background: rgba(0,212,255,0.15) !important;
    border-color: #00d4ff !important;
    color: #00d4ff !important;
}

.js-plotly-plot {
    max-width: 100% !important;
    overflow: hidden !important;
}

.plotly {
    max-width: 100% !important;
}

@media (max-width: 640px) {
    [data-testid="column"] {
        width: 100% !important;
        flex: 0 0 100% !important;
        max-width: 100% !important;
        margin-bottom: 8px;
    }
}

table {
    width: 100% !important;
    overflow-x: auto !important;
    display: block !important;
    white-space: nowrap !important;
}

@media (max-width: 768px) {
    table {
        font-size: 0.8rem !important;
    }
    th, td {
        padding: 6px !important;
    }
}

pre, code {
    overflow-x: auto !important;
    max-width: 100% !important;
    font-size: clamp(0.7rem, 1.5vw, 0.85rem) !important;
    word-wrap: break-word !important;
}

img {
    max-width: 100% !important;
    height: auto !important;
}

@media (max-width: 480px) {
    .block-container { padding: 0.5rem !important; }
    .scifi-card { margin: 8px 0 !important; }
    .workflow-step {
        padding: 10px 12px !important;
        margin: 8px 0 !important;
    }
    .ai-cap-card {
        padding: 12px !important;
        min-height: 80px;
    }
    .stMarkdown p {
        font-size: 0.85rem !important;
        line-height: 1.5 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: scroll !important;
        flex-wrap: nowrap !important;
    }
}

@media (min-width: 481px) and (max-width: 1024px) {
    .block-container { padding: 1.5rem !important; }
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.4rem !important; }
    h3 { font-size: 1.1rem !important; }
}

@media (min-width: 1920px) {
    .block-container {
        max-width: 1800px !important;
        margin: 0 auto !important;
    }
}

*:focus {
    outline: 2px solid rgba(0,212,255,0.5) !important;
    outline-offset: 2px !important;
}

button:focus, a:focus {
    outline: 2px solid #00d4ff !important;
    outline-offset: 2px !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# SECRETS HANDLER
# ═══════════════════════════════════════════════
def get_secret(key):
    """Get secret from Streamlit Cloud or local .env file"""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError, Exception):
        pass
    value = os.getenv(key)
    return value if value else None


@st.cache_resource
def get_s3_client():
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
    with st.expander("🔧 DEBUG INFORMATION"):
        st.markdown("### Secrets Status")
        secrets_to_check = [
            "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
            "AWS_REGION", "S3_BUCKET_NAME", "GROQ_API_KEY"
        ]
        for key in secrets_to_check:
            value = get_secret(key)
            if value:
                if key in ["AWS_SECRET_ACCESS_KEY", "GROQ_API_KEY", "AWS_ACCESS_KEY_ID"]:
                    masked = value[:6] + "****"
                    st.success(f"✅ **{key}**: {masked}")
                else:
                    st.success(f"✅ **{key}**: {value}")
            else:
                st.error(f"❌ **{key}**: NOT SET")


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

    # PAGE 1: COMMAND CENTER
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

    # PAGE 2: CITY INTELLIGENCE
    elif page == "◈ City Intelligence":
        st.markdown('<div class="hero-title" style="font-size:1.8rem;">◈ CITY INTELLIGENCE MODULE</div>', unsafe_allow_html=True)
        if df is None:
            st.error(f"❌ Data unavailable: {source}")
            show_debug_info()
            return
        st.divider()
        selected = st.selectbox("◈ SELECT TARGET CITY", df["city"].tolist())
        city = df[df["city"] == selected].iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("TEMPERATURE", f"{city['temperature_c']}°C")
        with c2: st.metric("HUMIDITY", f"{city['humidity_pct']}%")
        with c3: st.metric("WIND", f"{city.get('wind_speed_ms',0)} m/s")
        with c4: st.metric("CLOUDS", f"{city.get('cloud_cover_pct',0)}%")
        st.divider()
        st.markdown("### AI INSIGHTS")
        ca, cb, cc = st.columns(3)
        with ca: st.info(f"**TRAVEL**\n\n{city.get('travel_tip','N/A')}")
        with cb: st.success(f"**ACTIVITY**\n\n{city.get('activity','N/A')}")
        with cc: st.warning(f"**HEALTH**\n\n{city.get('health_tip','N/A')}")
        st.divider()
        cols = [c for c in ["city","temperature_c","humidity_pct","wind_speed_ms","weather_condition"] if c in df.columns]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)

    # PAGE 3: AI REPORTS
    elif page == "◈ AI Agent Reports":
        st.markdown('<div class="hero-title" style="font-size:1.8rem;">◈ AI AGENT REPORTS</div>', unsafe_allow_html=True)
        st.divider()
        if report:
            st.markdown("### LATEST AI REPORT")
            st.info(report.get('pipeline_report','No report'))
            anom = report.get("anomalies", {})
            if isinstance(anom, dict) and anom.get("count", 0) > 0:
                st.error(f"🚨 {anom['count']} anomalies detected")
                for a in anom.get("anomalies", []):
                    with st.expander(f"{a['city']} - {a['metric']}"):
                        st.metric("VALUE", a["value"])
                        st.metric("NORMAL", a["normal_range"])
            else:
                st.success("No anomalies detected")
        else:
            st.warning("No reports found")
            show_debug_info()

    # PAGE 4: PIPELINE
    elif page == "◈ Pipeline Operations":
        st.markdown('<div class="hero-title" style="font-size:1.8rem;">◈ PIPELINE OPERATIONS</div>', unsafe_allow_html=True)
        st.divider()
        if logs:
            latest = logs[0]
            if latest.get("status") == "success":
                st.success("✅ Last run successful")
            else:
                st.error("❌ Last run failed")
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("RUN ID", latest.get("run_id","N/A"))
            with c2: st.metric("DURATION", f"{latest.get('total_duration_sec',0)}s")
            with c3: st.metric("RECORDS", latest.get("final_record_count",0))
        else:
            st.warning("No logs found")

    # PAGE 5: ARCHITECTURE
    elif page == "◈ Project Architecture":
        st.markdown('<div class="hero-title" style="font-size:1.8rem;">◈ PROJECT ARCHITECTURE</div>', unsafe_allow_html=True)
        st.divider()
        st.error("**PROBLEM:** Businesses make weather-dependent decisions manually, wasting 45+ min/day with outdated data.")
        st.success("**SOLUTION:** Fully automated AI-powered pipeline with $0 cost, runs 2x daily, generates business insights.")

    # PAGE 6: PROFILE
    elif page == "◈ Engineer Profile":
        st.markdown('<div class="hero-title" style="font-size:1.8rem;">◈ ENGINEER PROFILE</div>', unsafe_allow_html=True)
        st.divider()
        st.markdown("""
        <div class="scifi-card" style="text-align:center; padding:40px;">
            <h2 style="color:#00d4ff;">HARSHIT SHUKLA</h2>
            <p style="color:#8892b0;">Data Engineer • AI Practitioner • Cloud Architect</p>
            <p style="color:#8892b0;">📍 Bengaluru, India • 4+ Years Experience</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("""**Harshit Shukla** is a Data Engineer with 4+ years experience building scalable ETL/ELT pipelines using AWS, Snowflake, Databricks, Apache Spark, Kafka, and Airflow.

Currently at **RM Private Limited** processing 1-2M order transactions daily from 5000+ vendors. Previously at **Wipro Limited** working on Nike Clickstream Platform (50M+ events/day).

Has **intermediate knowledge in AI** and expertise in **Agentic AI, LangChain, LangGraph, and Prompt Engineering**.""")


if __name__ == "__main__":
    main()