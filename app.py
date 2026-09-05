import os
from io import BytesIO
import base64
from datetime import date, timedelta
import json
import re
import time
from typing import Dict, Any, Optional, List, Tuple

import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="SEO DASHBOARD - Juan365 vs Competitors",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# =========================
# CSS (COMPLETE)
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #1a1f36 50%, #0d1117 100%);
    color: #ffffff;
}

.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1440px;
    margin: 0 auto;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1524 0%, #1a2035 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.06);
    padding: 1.5rem 0.5rem;
}

h1, h2, h3, h4, h5, h6, p, label, div {
    color: #2ed070 !important;
    font-family: 'Inter', sans-serif !important;
}

.stSelectbox {
    margin-bottom: 0.5rem;
}

.stSelectbox > div {
    background: #1a2035 !important;
    border-radius: 8px !important;
    border: 1px solid rgba(34, 197, 94, 0.3) !important;
}

.stSelectbox > div:hover {
    border-color: rgba(34, 197, 94, 0.6) !important;
}

.stSelectbox > div > div {
    color: #22c55e !important;
}

.stSelectbox > div > div > div {
    color: #22c55e !important;
}

.stSelectbox > div > div > div > div {
    color: #22c55e !important;
}

.stSelectbox [data-testid="stMarkdownContainer"] {
    color: #22c55e !important;
}

.stSelectbox [data-baseweb="select"] {
    color: #22c55e !important;
    background: transparent !important;
}

.stSelectbox [data-baseweb="select"] > div {
    color: #22c55e !important;
    background: transparent !important;
}

.stSelectbox * {
    color: #22c55e !important;
}

.stSelectbox > div > div:last-child {
    background: #0f1524 !important;
    border: 1px solid rgba(34, 197, 94, 0.2) !important;
    border-radius: 8px !important;
    max-height: 300px !important;
    overflow-y: auto !important;
}

.stSelectbox > div > div:last-child div {
    color: #22c55e !important;
    padding: 8px 12px !important;
    background: transparent !important;
}

.stSelectbox > div > div:last-child div:hover {
    background: rgba(34, 197, 94, 0.15) !important;
    color: #4ade80 !important;
}

.stSelectbox > div > div:last-child div[aria-selected="true"] {
    background: rgba(34, 197, 94, 0.25) !important;
    color: #4ade80 !important;
}

.stSelectbox > div > div:last-child::-webkit-scrollbar {
    width: 4px;
}
.stSelectbox > div > div:last-child::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
}
.stSelectbox > div > div:last-child::-webkit-scrollbar-thumb {
    background: rgba(34, 197, 94, 0.3);
    border-radius: 4px;
}

.stDateInput {
    margin-bottom: 0.5rem;
}

.stDateInput > div {
    background: #1a2035 !important;
    border-radius: 8px !important;
    border: 1px solid rgba(34, 197, 94, 0.3) !important;
}

.stDateInput > div:hover {
    border-color: rgba(34, 197, 94, 0.6) !important;
}

.stDateInput > div > div {
    background: transparent !important;
}

.stDateInput > div input {
    color: #22c55e !important;
    background: transparent !important;
    font-weight: 500 !important;
}

.stDateInput label {
    color: #94a3b8 !important;
}

.stDateInput [data-baseweb="popover"] {
    background: #0f1524 !important;
    border: 1px solid rgba(34, 197, 94, 0.2) !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5) !important;
}

.stDateInput [data-baseweb="calendar"] {
    background: #0f1524 !important;
    border: none !important;
    border-radius: 8px !important;
}

.stDateInput [data-baseweb="calendar"] * {
    color: #22c55e !important;
    background: transparent !important;
}

.stDateInput [data-baseweb="calendar"] [role="button"] {
    color: #22c55e !important;
}

.stDateInput [data-baseweb="calendar"] [role="button"]:hover {
    color: #4ade80 !important;
    background: rgba(34, 197, 94, 0.1) !important;
}

.stDateInput [data-baseweb="calendar"] div[role="gridcell"] {
    color: #22c55e !important;
    background: transparent !important;
}

.stDateInput [data-baseweb="calendar"] div[role="gridcell"]:hover {
    background: rgba(34, 197, 94, 0.15) !important;
    border-radius: 4px !important;
}

.stDateInput [data-baseweb="calendar"] div[aria-selected="true"] {
    background: rgba(34, 197, 94, 0.25) !important;
    color: #4ade80 !important;
    border-radius: 4px !important;
}

.stDateInput [data-baseweb="calendar"] div[aria-current="date"] {
    border: 1px solid #22c55e !important;
    border-radius: 4px !important;
}

.stDateInput [data-baseweb="calendar"] [role="columnheader"] {
    color: #4ade80 !important;
    font-weight: 600 !important;
}

.stDateInput [data-baseweb="calendar"] [aria-label*="previous"] {
    color: #22c55e !important;
}

.stDateInput [data-baseweb="calendar"] [aria-label*="next"] {
    color: #22c55e !important;
}

.stDateInput [data-baseweb="calendar"] [aria-label*="previous"]:hover,
.stDateInput [data-baseweb="calendar"] [aria-label*="next"]:hover {
    background: rgba(34, 197, 94, 0.1) !important;
    border-radius: 4px !important;
}

.stDateInput [data-baseweb="calendar"] select {
    background: #1a2035 !important;
    color: #22c55e !important;
    border: 1px solid rgba(34, 197, 94, 0.2) !important;
    border-radius: 4px !important;
}

.stDateInput [data-baseweb="calendar"] select option {
    background: #0f1524 !important;
    color: #22c55e !important;
}

.stDateInput [data-baseweb="popover"] * {
    color: #22c55e !important;
}

.stDateInput [data-baseweb="timepicker"] {
    background: #0f1524 !important;
}

.stDateInput [data-baseweb="timepicker"] * {
    color: #22c55e !important;
}

.stRadio {
    margin-bottom: 0.5rem;
}

.stRadio > div {
    background: rgba(255, 255, 255, 0.05) !important;
    border-radius: 8px !important;
    padding: 0.5rem !important;
}

.stRadio label {
    color: #e2e8f0 !important;
    font-weight: 500 !important;
}

.stRadio label:hover {
    color: #22c55e !important;
}

.sidebar-label {
    font-size: 0.7rem;
    color: #94a3b8 !important;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
    margin-top: 0.5rem;
}

.dashboard-header {
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 24px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
}

.dashboard-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(34, 197, 94, 0.08) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.dashboard-title {
    font-size: 2.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}

.dashboard-subtitle {
    color: #94a3b8 !important;
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 0.02em;
}

.dashboard-badge {
    display: inline-block;
    background: rgba(34, 197, 94, 0.15);
    color: #22c55e;
    padding: 0.25rem 1rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    border: 1px solid rgba(34, 197, 94, 0.2);
    margin-top: 0.5rem;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    margin-top: 2.5rem;
    margin-bottom: 1.25rem;
    padding: 0.75rem 1.25rem;
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.08) 0%, rgba(34, 197, 94, 0.02) 100%);
    border-left: 4px solid #22c55e;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.section-title::before {
    content: '▸';
    color: #22c55e;
    font-size: 1.5rem;
    font-weight: 300;
}

.section-title-ai {
    font-size: 1.3rem;
    font-weight: 700;
    margin-top: 2.5rem;
    margin-bottom: 1.25rem;
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(59, 130, 246, 0.15));
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    backdrop-filter: blur(10px);
}

.section-title-ai::before {
    content: '🤖';
    font-size: 1.5rem;
}

.kpi-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    min-height: 120px;
}

.kpi-card:hover {
    transform: translateY(-2px);
    border-color: rgba(255, 255, 255, 0.12);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.kpi-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-color, #22c55e), var(--accent-color-secondary, #16a34a));
    opacity: 0.8;
}

.kpi-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: #94a3b8;
    margin-bottom: 0.5rem;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}

.kpi-delta {
    font-size: 0.75rem;
    color: #94a3b8;
    font-weight: 500;
}

.kpi-icon {
    position: absolute;
    right: 1rem;
    top: 1rem;
    font-size: 1.5rem;
    opacity: 0.2;
}

.ai-card {
    background: linear-gradient(145deg, rgba(139, 92, 246, 0.08), rgba(59, 130, 246, 0.05));
    border: 1px solid rgba(139, 92, 246, 0.15);
    border-radius: 20px;
    padding: 1.5rem;
    backdrop-filter: blur(20px);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    min-height: 140px;
}

.ai-card:hover {
    transform: translateY(-6px) scale(1.02);
    border-color: rgba(139, 92, 246, 0.3);
    box-shadow: 0 20px 60px rgba(139, 92, 246, 0.2);
}

.ai-card::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.08), transparent 70%);
    pointer-events: none;
}

.ai-card .value {
    font-size: 2.2rem;
    font-weight: 900;
    background: linear-gradient(135deg, #c4b5fd, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}

.ai-card .label {
    font-size: 0.7rem;
    color: #94a3b8;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.08em;
}

.ai-card .icon {
    font-size: 2rem;
    opacity: 0.6;
    position: absolute;
    right: 1.2rem;
    top: 1.2rem;
}

.ai-insight-card {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.9));
    border: 1px solid rgba(139, 92, 246, 0.12);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    backdrop-filter: blur(20px);
    transition: all 0.3s ease;
}

.ai-insight-card:hover {
    border-color: rgba(139, 92, 246, 0.25);
    transform: translateX(4px);
}

.badge {
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.badge-positive {
    background: rgba(34, 197, 94, 0.15);
    color: #22c55e;
    border: 1px solid rgba(34, 197, 94, 0.2);
}

.badge-negative {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.2);
}

.badge-neutral {
    background: rgba(251, 146, 60, 0.15);
    color: #fb923c;
    border: 1px solid rgba(251, 146, 60, 0.2);
}

.badge-info {
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.2);
}

.alert-card {
    background: rgba(15, 23, 42, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-left: 5px solid #22c55e;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    transition: all 0.3s ease;
}

.alert-card:hover {
    border-color: rgba(255, 255, 255, 0.12);
    transform: translateX(4px);
}

.alert-warning {
    border-left-color: #f59e0b;
}

.alert-danger {
    border-left-color: #ef4444;
}

.alert-success {
    border-left-color: #22c55e;
}

.alert-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.25rem;
}

.alert-body {
    font-size: 0.85rem;
    color: #94a3b8;
    line-height: 1.5;
}

.glass-card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.glass-card:hover {
    border-color: rgba(255, 255, 255, 0.12);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
}

.top-page-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    transition: all 0.3s ease;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.top-page-card:hover {
    border-color: rgba(255, 255, 255, 0.12);
    transform: translateX(4px);
    background: rgba(255, 255, 255, 0.06);
}

.top-page-rank {
    font-weight: 700;
    color: #22c55e;
    font-size: 0.9rem;
    min-width: 30px;
}

.top-page-url {
    color: #e2e8f0;
    font-size: 0.85rem;
    flex: 1;
    margin: 0 1rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.top-page-clicks {
    font-weight: 700;
    color: #facc15;
    font-size: 0.9rem;
    min-width: 60px;
    text-align: right;
}

.top-page-position {
    font-weight: 700;
    color: #34d399;
    font-size: 0.9rem;
    min-width: 50px;
    text-align: right;
}

.data-loaded-badge {
    display: inline-block;
    padding: 0.1rem 0.6rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 700;
    margin-left: 0.5rem;
}

.data-loaded-badge.success {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
}

.data-loaded-badge.error {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
}

.data-loaded-badge.warning {
    background: rgba(251, 146, 60, 0.2);
    color: #fb923c;
}

.download-container {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 1rem;
    transition: all 0.3s ease;
    text-align: center;
    height: 100%;
}

.download-container:hover {
    border-color: rgba(255, 255, 255, 0.12);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.download-btn {
    width: 100%;
    padding: 0.75rem !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    cursor: pointer;
    transition: all 0.3s ease !important;
    text-align: center;
    display: inline-block;
    text-decoration: none;
    color: white !important;
    letter-spacing: 0.02em;
}

.download-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
}

.download-btn-gsc {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.download-btn-ahrefs {
    background: linear-gradient(135deg, #f97316, #c2410c);
}

.download-btn-combined {
    background: linear-gradient(135deg, #22c55e, #16a34a);
}

.download-btn-metrics {
    background: linear-gradient(135deg, #8b5cf6, #6d28d9);
}

.download-btn-ahrefs-empty {
    background: linear-gradient(135deg, #4a5568, #2d3748);
    opacity: 0.7;
    cursor: not-allowed;
}

.warning-text {
    color: #94a3b8;
    font-size: 0.8rem;
    padding: 0.5rem;
    text-align: center;
}

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

[data-testid="stDataFrame"] thead tr th {
    background: rgba(255, 255, 255, 0.05) !important;
    color: #e2e8f0 !important;
    font-weight: 600 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0.75rem 1rem !important;
}

[data-testid="stDataFrame"] tbody tr td {
    padding: 0.75rem 1rem !important;
    color: #cbd5e1 !important;
    font-size: 0.85rem !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
}

[data-testid="stDataFrame"] tbody tr:hover {
    background: rgba(255, 255, 255, 0.03) !important;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.live-indicator {
    animation: pulse 2s infinite;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .dashboard-title {
        font-size: 1.8rem;
    }
    
    .kpi-value {
        font-size: 1.5rem;
    }
}

.stButton button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.02em;
    width: 100%;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.stButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3) !important;
}

.stDownloadButton button {
    background: linear-gradient(135deg, #22c55e, #16a34a) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.02em;
    width: 100%;
    box-shadow: 0 4px 12px rgba(34, 197, 94, 0.2);
}

.stDownloadButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(34, 197, 94, 0.3) !important;
}

::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.25);
}
</style>
""", unsafe_allow_html=True)

# =========================
# CONFIG - API KEYS (READ FROM SECRETS)
# =========================
# Try to get API keys from secrets first, fallback to hardcoded
try:
    AHREFS_API_KEY = st.secrets.get("AHREFS_API_KEY", "TK4LhJ3T06H_Zy6ghG9b4n7lz82PFZVvhR3Fp3yd")
    SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", "sk_mW3LukviteitbSKMrzFT0Zdwv2MHfO1Fe7KCaK5B")
except:
    AHREFS_API_KEY = "TK4LhJ3T06H_Zy6ghG9b4n7lz82PFZVvhR3Fp3yd"
    SERPAPI_KEY = "sk_mW3LukviteitbSKMrzFT0Zdwv2MHfO1Fe7KCaK5B"

SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/analytics.readonly"
]

# =========================
# SITE CONFIGURATION (COMPLETE)
# =========================
SITES = {
    # ===== JUAN365 CATEGORY =====
    "juan365.org": {
        "gsc_url": "https://juan365.org/",
        "ga4_property_id": "520509948",
        "category": "Juan365",
        "ahrefs_target": "juan365.org",
        "display_name": "juan365.org",
        "priority": True
    },
    "juan365.live": {
        "gsc_url": "https://juan365.live/",
        "ga4_property_id": "520509948",
        "category": "Juan365",
        "ahrefs_target": "juan365.live",
        "display_name": "juan365.live",
        "priority": True
    },
    "juan-365.com.ph": {
        "gsc_url": "https://juan-365.com.ph/",
        "ga4_property_id": "520509948",
        "category": "Juan365",
        "ahrefs_target": "juan-365.com.ph",
        "display_name": "juan-365.com.ph",
        "priority": True
    },
    "juan365philippines.com": {
        "gsc_url": "https://juan365philippines.com/",
        "ga4_property_id": "520509948",
        "category": "Juan365",
        "ahrefs_target": "juan365philippines.com",
        "display_name": "juan365philippines.com",
        "priority": False
    },
    "juan-365.ph": {
        "gsc_url": "https://juan-365.ph/",
        "ga4_property_id": "520509948",
        "category": "Juan365",
        "ahrefs_target": "juan-365.ph",
        "display_name": "juan-365.ph",
        "priority": False
    },
    "juan365.net.ph": {
        "gsc_url": "https://juan365.net.ph/",
        "ga4_property_id": "508243783",
        "category": "Juan365",
        "ahrefs_target": "juan365.net.ph",
        "display_name": "juan365.net.ph",
        "priority": False
    },
    "playjuan365.com": {
        "gsc_url": "https://playjuan365.com/",
        "ga4_property_id": "520509948",
        "category": "Juan365",
        "ahrefs_target": "playjuan365.com",
        "display_name": "playjuan365.com",
        "priority": True
    },
    "juan365player.com": {
        "gsc_url": "https://juan365player.com/",
        "ga4_property_id": "520509948",
        "category": "Juan365",
        "ahrefs_target": "juan365player.com",
        "display_name": "juan365player.com",
        "priority": False
    },
    "juan365casino.com": {
        "gsc_url": "https://juan365casino.com/",
        "ga4_property_id": "520509948",
        "category": "Juan365",
        "ahrefs_target": "juan365casino.com",
        "display_name": "juan365casino.com",
        "priority": True
    },
    "juan365.site": {
        "gsc_url": "https://juan365.site/",
        "ga4_property_id": "520509948",
        "category": "Juan365",
        "ahrefs_target": "juan365.site",
        "display_name": "juan365.site",
        "priority": False
    },
    "juan365slots.com": {
        "gsc_url": "https://juan365slots.com/",
        "ga4_property_id": "543090329",
        "category": "Juan365",
        "ahrefs_target": "juan365slots.com",
        "display_name": "juan365slots.com",
        "priority": False
    },
    "juan365casino.ph": {
        "gsc_url": "https://juan365casino.ph/",
        "ga4_property_id": "520509948",
        "category": "Juan365",
        "ahrefs_target": "juan365casino.ph",
        "display_name": "juan365casino.ph",
        "priority": False
    },
    "juan365sports.ph": {
        "gsc_url": "https://juan365sports.ph/",
        "ga4_property_id": "520509948",
        "category": "Juan365",
        "ahrefs_target": "juan365sports.ph",
        "display_name": "juan365sports.ph",
        "priority": False
    },
    "juanzoneph.org": {
        "gsc_url": "https://juanzoneph.org/",
        "ga4_property_id": "520509948",
        "category": "Juan365",
        "ahrefs_target": "juanzoneph.org",
        "display_name": "juanzoneph.org",
        "priority": False
    },
    "1365ph.org": {
        "gsc_url": "https://1365ph.org/",
        "ga4_property_id": "520509948",
        "category": "Juan365",
        "ahrefs_target": "1365ph.org",
        "display_name": "1365ph.org",
        "priority": False
    },
    "huan247.com": {
        "gsc_url": "https://huan247.com/",
        "ga4_property_id": "520509948",
        "category": "Juan365",
        "ahrefs_target": "huan247.com",
        "display_name": "huan247.com",
        "priority": False
    },
    
    # ===== COMPETITOR LEGAL CATEGORY =====
    "fbm-emotion.org": {
        "gsc_url": "https://fbm-emotion.org/",
        "ga4_property_id": "525616807",
        "category": "Competitor Legal",
        "ahrefs_target": "fbm-emotion.org",
        "display_name": "fbm-emotion.org",
        "priority": False
    },
    "patokbetcasino.org": {
        "gsc_url": "https://patokbetcasino.org/",
        "ga4_property_id": "520509948",
        "category": "Competitor Legal",
        "ahrefs_target": "patokbetcasino.org",
        "display_name": "patokbetcasino.org",
        "priority": False
    },
    "gamexph.com": {
        "gsc_url": "https://gamexph.com/",
        "ga4_property_id": "547730498",
        "category": "Competitor Legal",
        "ahrefs_target": "gamexph.com",
        "display_name": "gamexph.com",
        "priority": False
    },
    "lakiwinph.org": {
        "gsc_url": "https://lakiwinph.org/",
        "ga4_property_id": "524887603",
        "category": "Competitor Legal",
        "ahrefs_target": "lakiwinph.org",
        "display_name": "lakiwinph.org",
        "priority": False
    },
    "nustargameph.org": {
        "gsc_url": "https://nustargameph.org/",
        "ga4_property_id": "520490172",
        "category": "Competitor Legal",
        "ahrefs_target": "nustargameph.org",
        "display_name": "nustargameph.org",
        "priority": False
    },
    "gzoneph.org": {
        "gsc_url": "https://gzoneph.org/",
        "ga4_property_id": "543856091",
        "category": "Competitor Legal",
        "ahrefs_target": "gzoneph.org",
        "display_name": "gzoneph.org",
        "priority": False
    },
    "bigwin29-ph.org": {
        "gsc_url": "https://bigwin29-ph.org/",
        "ga4_property_id": "543856543",
        "category": "Competitor Legal",
        "ahrefs_target": "bigwin29-ph.org",
        "display_name": "bigwin29-ph.org",
        "priority": False
    },
    "123gogames.org": {
        "gsc_url": "https://123gogames.org/",
        "ga4_property_id": "",
        "category": "Competitor Legal",
        "ahrefs_target": "123gogames.org",
        "display_name": "123gogames.org",
        "priority": False
    },
    "789bingo.org": {
        "gsc_url": "https://789bingo.org/",
        "ga4_property_id": "",
        "category": "Competitor Legal",
        "ahrefs_target": "789bingo.org",
        "display_name": "789bingo.org",
        "priority": False
    },
    "mobilecasinoplay88.org": {
        "gsc_url": "https://mobilecasinoplay88.org/",
        "ga4_property_id": "520509945",
        "category": "Competitor Legal",
        "ahrefs_target": "mobilecasinoplay88.org",
        "display_name": "mobilecasinoplay88.org",
        "priority": False
    },
    "gg-panalo.org": {
        "gsc_url": "https://gg-panalo.org/",
        "ga4_property_id": "",
        "category": "Competitor Legal",
        "ahrefs_target": "gg-panalo.org",
        "display_name": "gg-panalo.org",
        "priority": False
    },
    "playtimephl.org": {
        "gsc_url": "https://playtimephl.org/",
        "ga4_property_id": "543858717",
        "category": "Competitor Legal",
        "ahrefs_target": "playtimephl.org",
        "display_name": "playtimephl.org",
        "priority": False
    },
    "arionplaygcash.org": {
        "gsc_url": "https://arionplaygcash.org/",
        "ga4_property_id": "514555630",
        "category": "Competitor Legal",
        "ahrefs_target": "arionplaygcash.org",
        "display_name": "arionplaygcash.org",
        "priority": False
    },
    "megasportsworld.org": {
        "gsc_url": "https://megasportsworld.org/",
        "ga4_property_id": "545350411",
        "category": "Competitor Legal",
        "ahrefs_target": "megasportsworld.org",
        "display_name": "megasportsworld.org",
        "priority": False
    },
    "s5arena.org": {
        "gsc_url": "https://s5arena.org/",
        "ga4_property_id": "",
        "category": "Competitor Legal",
        "ahrefs_target": "s5arena.org",
        "display_name": "s5arena.org",
        "priority": False
    },
}

CATEGORIES = {
    "Juan365": {
        "icon": "🎰",
        "color": "#22c55e",
        "description": "Juan365 Casino & Gaming Sites",
        "sites": [site for site, config in SITES.items() if config["category"] == "Juan365"]
    },
    "Competitor Legal": {
        "icon": "⚖️",
        "color": "#f59e0b",
        "description": "Legal Competitor Sites",
        "sites": [site for site, config in SITES.items() if config["category"] == "Competitor Legal"]
    }
}

SITE_METRICS_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ2lub4F_fMu-V_F6EMlqJOHpPIpRWhsKxgpjQOBkkTsppku31ZIIu-0yfWGFo7WVSek2xMYMd_lsop/pub?output=csv"

# =========================
# AHREFS API FUNCTIONS - FIXED ENDPOINTS
# =========================
@st.cache_data(ttl=86400)
def ahrefs_api_request(endpoint, params):
    """Ahrefs API v3 request with caching"""
    if not AHREFS_API_KEY:
        return None, "Missing AHREFS_API_KEY"
    
    try:
        base_url = "https://api.ahrefs.com/v3"
        url = f"{base_url}/{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {AHREFS_API_KEY}",
            "Accept": "application/json"
        }
        
        all_params = {**params}
        if 'output' in all_params:
            del all_params['output']
        
        response = requests.get(url, headers=headers, params=all_params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data, None
        elif response.status_code == 403:
            error_text = response.text
            if "API units limit reached" in error_text or "quota" in error_text.lower():
                return None, "QUOTA_EXHAUSTED: Ahrefs API quota exhausted. Please upgrade your plan or wait for reset."
            else:
                return None, f"Ahrefs API Error 403: {error_text[:200]}"
        elif response.status_code == 429:
            return None, "Ahrefs API rate limit exceeded. Please wait and try again."
        elif response.status_code == 401:
            return None, "Ahrefs API Error: Invalid API key. Please check your credentials."
        else:
            return None, f"Ahrefs API Error {response.status_code}: {response.text[:200]}"
            
    except requests.exceptions.Timeout:
        return None, "Ahrefs API Error: Request timeout"
    except requests.exceptions.ConnectionError:
        return None, "Ahrefs API Error: Connection error"
    except Exception as e:
        return None, f"Ahrefs API Exception: {str(e)}"

@st.cache_data(ttl=86400)
def get_ahrefs_domain_rating(target):
    """Get Domain Rating (DR) for a target"""
    params = {
        "target": target,
        "date": date.today().strftime("%Y-%m-%d")
    }
    return ahrefs_api_request("site-explorer/domain-rating", params)

@st.cache_data(ttl=86400)
def get_ahrefs_backlinks(target):
    """Get backlinks for a target"""
    params = {
        "target": target,
        "mode": "domain",
        "limit": 100,
        "select": "url_from,url_to,domain_rating_source,traffic"
    }
    return ahrefs_api_request("site-explorer/all-backlinks", params)

@st.cache_data(ttl=86400)
def get_ahrefs_refdomains(target):
    """Get referring domains for a target"""
    params = {
        "target": target,
        "mode": "domain",
        "limit": 100,
        "select": "domain_from,domain_rating,total_backlinks"
    }
    return ahrefs_api_request("site-explorer/refdomains", params)

@st.cache_data(ttl=86400)
def get_ahrefs_organic_keywords(target):
    """Get organic keywords for a target"""
    params = {
        "target": target,
        "mode": "domain",
        "date": date.today().strftime("%Y-%m-%d"),
        "country": "ph",
        "limit": 100,
        "select": "keyword,keyword_country,best_position,volume,sum_traffic,best_position_url"
    }
    return ahrefs_api_request("site-explorer/organic-keywords", params)

# =========================
# AUTH - FIXED TO READ FROM SECRETS
# =========================
@st.cache_resource
def google_login():
    try:
        # Check if secrets exist
        if "gcp_service_account" not in st.secrets:
            st.sidebar.error("❌ GCP Service Account not found in secrets. Please check your secrets.toml file.")
            st.sidebar.info("📝 Make sure secrets.toml has a [gcp_service_account] section with all required fields.")
            return None
        
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=SCOPES
        )
        st.sidebar.success("✅ GCP Authentication Successful!")
        return creds
    except KeyError as e:
        st.sidebar.error(f"❌ GCP Auth Error: Missing secret key: {str(e)}")
        st.sidebar.info("📝 Check your secrets.toml file has all required fields for gcp_service_account")
        return None
    except Exception as e:
        st.sidebar.error(f"❌ GCP Auth Error: {str(e)}")
        st.sidebar.info("📝 Make sure your service account has the correct permissions")
        return None

creds = google_login()

# =========================
# HELPER FUNCTIONS
# =========================
def safe_number(value, default=0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default

def safe_dataframe(data, default=pd.DataFrame()):
    if data is None:
        return default
    try:
        if isinstance(data, pd.DataFrame) and not data.empty:
            return data
        return default
    except:
        return default

def safe_get_value(data, key, default=0):
    try:
        if data is None:
            return default
        return data.get(key, default)
    except:
        return default

def flatten_dict(data, parent_key="", sep="_"):
    items = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                items.extend(flatten_dict(value, new_key, sep=sep).items())
            else:
                items.append((new_key, value))
    return dict(items)

def get_value_by_possible_keys(data, possible_keys, default="N/A"):
    if not isinstance(data, dict):
        return default
    flat = flatten_dict(data)
    for key in possible_keys:
        if key in flat:
            return flat[key]
    lowered = {str(k).lower(): v for k, v in flat.items()}
    for key in possible_keys:
        if str(key).lower() in lowered:
            return lowered[str(key).lower()]
    return default

def clean_number(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace('₱', '').replace('$', '').replace(',', '').replace(' ', '').strip()
        try:
            return float(cleaned)
        except:
            return 0
    return 0

def json_to_dataframe(data):
    """Improved JSON to DataFrame conversion for Ahrefs API responses"""
    if not data:
        return pd.DataFrame()
    
    if isinstance(data, dict):
        if 'data' in data:
            data = data['data']
        
        for key in ['backlinks', 'refdomains', 'keywords', 'metrics', 'organic_keywords']:
            if key in data and isinstance(data[key], list):
                return pd.DataFrame(data[key])
            elif key in data and isinstance(data[key], dict):
                flat_dict = flatten_dict(data[key])
                return pd.DataFrame([flat_dict])
        
        if all(not isinstance(v, (dict, list)) for v in data.values()):
            return pd.DataFrame([data])
    
    if isinstance(data, list):
        return pd.DataFrame(data)
    
    if isinstance(data, pd.DataFrame):
        return data
    
    return pd.DataFrame()

def check_ahrefs_quota_error(error_message):
    """Check if error is due to quota exhaustion"""
    if not error_message:
        return False
    quota_indicators = [
        "quota",
        "units limit",
        "exhausted",
        "no units",
        "insufficient units",
        "403",
        "QUOTA_EXHAUSTED",
        "QUOTA_BLOCKED"
    ]
    error_lower = error_message.lower()
    return any(indicator in error_lower for indicator in quota_indicators)

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("""
<div style="text-align: center; padding: 0.5rem 0 1.5rem 0;">
    <div style="font-size: 2.2rem; font-weight: 900; background: linear-gradient(135deg, #22c55e, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.02em;">Juan365</div>
    <div style="font-size: 0.65rem; color: #94a3b8; letter-spacing: 0.15em; text-transform: uppercase; margin-top: 0.25rem;">vs Competitors Dashboard</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-label">📊 View Mode</div>', unsafe_allow_html=True)

view_mode = st.sidebar.selectbox(
    "",
    ["View All Sites", "View by Category", "View Individual Site", "Category Comparison"],
    label_visibility="collapsed",
    key="view_mode"
)

selected_site = None
selected_category = None
site_config = None
view_all_sites = False
category_sites = []

if view_mode == "View All Sites":
    view_all_sites = True
    selected_site = "all"
    st.sidebar.info("📊 Showing all sites across all categories")
    
elif view_mode == "View by Category":
    st.sidebar.markdown('<div class="sidebar-label">🏷️ Select Category</div>', unsafe_allow_html=True)
    category_list = list(CATEGORIES.keys())
    selected_category = st.sidebar.selectbox(
        "",
        category_list,
        format_func=lambda x: f"{CATEGORIES[x]['icon']} {x} ({len(CATEGORIES[x]['sites'])} sites)",
        label_visibility="collapsed",
        key="category_selector"
    )
    category_sites = CATEGORIES[selected_category]["sites"]
    st.sidebar.info(f"📊 Showing {len(category_sites)} sites in {selected_category}")
    
elif view_mode == "View Individual Site":
    st.sidebar.markdown('<div class="sidebar-label">🌐 Select Site</div>', unsafe_allow_html=True)
    
    site_options = []
    site_mapping = {}
    
    for category, cat_data in CATEGORIES.items():
        for site in cat_data["sites"]:
            display = f"{cat_data['icon']} {category} | {SITES[site]['display_name']}"
            site_options.append(display)
            site_mapping[display] = site
    
    selected_option = st.sidebar.selectbox(
        "",
        site_options,
        label_visibility="collapsed",
        key="site_selector"
    )
    
    selected_site = site_mapping.get(selected_option)
    if selected_site:
        site_config = SITES.get(selected_site)
        st.sidebar.info(f"📊 Showing data for {site_config['display_name'] if site_config else selected_site}")

elif view_mode == "Category Comparison":
    st.sidebar.info("📊 Comparing Juan365 vs Competitors")
    view_all_sites = True

st.sidebar.markdown("---")

# Time Period
st.sidebar.markdown('<div class="sidebar-label">⏱️ Time Period</div>', unsafe_allow_html=True)

period = st.sidebar.radio(
    "",
    ["30 Days", "90 Days", "6 Months", "12 Months"],
    label_visibility="collapsed"
)

today = date.today()

if period == "30 Days":
    default_start = today - timedelta(days=30)
elif period == "90 Days":
    default_start = today - timedelta(days=90)
elif period == "6 Months":
    default_start = today - timedelta(days=180)
else:
    default_start = today - timedelta(days=365)

# Date Range
st.sidebar.markdown('<div class="sidebar-label">📅 Date Range</div>', unsafe_allow_html=True)

col1, col2 = st.sidebar.columns(2)

with col1:
    gsc_end = st.date_input("End", today, key=f"end_{period}", label_visibility="collapsed")

with col2:
    gsc_start = st.date_input("Start", default_start, key=f"start_{period}", label_visibility="collapsed")

GSC_START_DATE = str(gsc_start)
GSC_END_DATE = str(gsc_end)

previous_start = pd.to_datetime(gsc_start) - pd.Timedelta(days=7)
previous_end = pd.to_datetime(gsc_end) - pd.Timedelta(days=7)

PREVIOUS_START_DATE = str(previous_start.date())
PREVIOUS_END_DATE = str(previous_end.date())

GA4_START_DATE = "30daysAgo"
GA4_END_DATE = "today"

st.sidebar.markdown("---")

# API Status
st.sidebar.markdown('<div class="sidebar-label">🔑 API Status</div>', unsafe_allow_html=True)

if AHREFS_API_KEY:
    st.sidebar.success(f"✅ Ahrefs API Key configured (length: {len(AHREFS_API_KEY)})")
else:
    st.sidebar.error("🚫 Ahrefs API Key missing")

# Debug button for API testing
if st.sidebar.button("🧪 Test Ahrefs API", use_container_width=True):
    st.sidebar.info("Testing Ahrefs API with CORRECT endpoints...")
    
    test_domain = "megasportsworld.org"
    st.sidebar.markdown(f"**Testing with:** {test_domain}")
    
    # Test Domain Rating
    st.sidebar.markdown("**1. Testing Domain Rating...**")
    data, error = get_ahrefs_domain_rating(test_domain)
    if data:
        st.sidebar.success("✅ Domain Rating API: Success")
        st.sidebar.json(data)
        dr = data.get('domain_rating', 'N/A')
        st.sidebar.info(f"Domain Rating: {dr}")
    else:
        st.sidebar.error(f"❌ Domain Rating API: {error}")
    
    # Test Organic Keywords
    st.sidebar.markdown("**2. Testing Organic Keywords...**")
    data, error = get_ahrefs_organic_keywords(test_domain)
    if data:
        st.sidebar.success("✅ Organic Keywords API: Success")
        keywords = data.get('keywords', [])
        st.sidebar.info(f"Found {len(keywords)} organic keywords")
        if keywords:
            st.sidebar.json(keywords[:3])
    else:
        st.sidebar.error(f"❌ Organic Keywords API: {error}")
    
    # Test Backlinks
    st.sidebar.markdown("**3. Testing Backlinks...**")
    data, error = get_ahrefs_backlinks(test_domain)
    if data:
        st.sidebar.success("✅ Backlinks API: Success")
        backlinks = data.get('backlinks', [])
        st.sidebar.info(f"Found {len(backlinks)} backlinks")
    else:
        st.sidebar.error(f"❌ Backlinks API: {error}")

if st.sidebar.button("🔄 Refresh All Data", use_container_width=True):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

# =========================
# DATA FUNCTIONS (GSC & GA4)
# =========================
@st.cache_data(ttl=300)
def get_gsc_data(site_url, start_date, end_date):
    try:
        if not creds:
            return pd.DataFrame()
        service = build("searchconsole", "v1", credentials=creds)
        
        urls_to_try = [
            site_url,
            site_url.rstrip('/'),
            site_url.replace('https://', 'sc_domain:'),
            site_url.replace('https://', '').rstrip('/')
        ]
        
        gsc_df = pd.DataFrame()
        for url in urls_to_try:
            try:
                request = {
                    "startDate": start_date,
                    "endDate": end_date,
                    "dimensions": ["date"],
                    "rowLimit": 1000
                }
                response = service.searchanalytics().query(
                    siteUrl=url,
                    body=request
                ).execute()
                rows = []
                for row in response.get("rows", []):
                    rows.append({
                        "Date": row["keys"][0],
                        "Clicks": row.get("clicks", 0),
                        "Impressions": row.get("impressions", 0),
                        "CTR": round(row.get("ctr", 0) * 100, 2),
                        "Position": round(row.get("position", 0), 2)
                    })
                gsc_df = pd.DataFrame(rows)
                if not gsc_df.empty:
                    break
            except:
                continue
        
        return gsc_df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_gsc_queries(site_url, start_date, end_date):
    try:
        if not creds:
            return pd.DataFrame()
        service = build("searchconsole", "v1", credentials=creds)
        
        urls_to_try = [
            site_url, site_url.rstrip('/'), 
            site_url.replace('https://', 'sc_domain:'), 
            site_url.replace('https://', '').rstrip('/')
        ]
        
        for url in urls_to_try:
            try:
                request = {
                    "startDate": start_date,
                    "endDate": end_date,
                    "dimensions": ["query"],
                    "rowLimit": 250
                }
                response = service.searchanalytics().query(
                    siteUrl=url,
                    body=request
                ).execute()
                rows = []
                for row in response.get("rows", []):
                    rows.append({
                        "Keyword": row["keys"][0],
                        "Clicks": row.get("clicks", 0),
                        "Impressions": row.get("impressions", 0),
                        "CTR": round(row.get("ctr", 0) * 100, 2),
                        "Position": round(row.get("position", 0), 2)
                    })
                return pd.DataFrame(rows)
            except:
                continue
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_gsc_pages(site_url, start_date, end_date):
    try:
        if not creds:
            return pd.DataFrame()
        service = build("searchconsole", "v1", credentials=creds)
        
        urls_to_try = [
            site_url, site_url.rstrip('/'), 
            site_url.replace('https://', 'sc_domain:'), 
            site_url.replace('https://', '').rstrip('/')
        ]
        
        for url in urls_to_try:
            try:
                request = {
                    "startDate": start_date,
                    "endDate": end_date,
                    "dimensions": ["page"],
                    "rowLimit": 250
                }
                response = service.searchanalytics().query(
                    siteUrl=url,
                    body=request
                ).execute()
                rows = []
                for row in response.get("rows", []):
                    rows.append({
                        "Page": row["keys"][0],
                        "Clicks": row.get("clicks", 0),
                        "Impressions": row.get("impressions", 0),
                        "CTR": round(row.get("ctr", 0) * 100, 2),
                        "Position": round(row.get("position", 0), 2)
                    })
                return pd.DataFrame(rows)
            except:
                continue
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_ga4_data(property_id):
    try:
        if not property_id or not creds:
            return {"sessions": 0, "active_users": 0, "total_users": 0, "pageviews": 0}
        client = BetaAnalyticsDataClient(credentials=creds)
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[
                DateRange(start_date=GA4_START_DATE, end_date=GA4_END_DATE)
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
                Metric(name="totalUsers"),
                Metric(name="screenPageViews")
            ]
        )
        response = client.run_report(request)
        if not response.rows:
            return {
                "sessions": 0,
                "active_users": 0,
                "total_users": 0,
                "pageviews": 0
            }
        row = response.rows[0]
        return {
            "sessions": int(row.metric_values[0].value),
            "active_users": int(row.metric_values[1].value),
            "total_users": int(row.metric_values[2].value),
            "pageviews": int(row.metric_values[3].value)
        }
    except Exception as e:
        return {"sessions": 0, "active_users": 0, "total_users": 0, "pageviews": 0}

@st.cache_data(ttl=60)
def get_metrics_data():
    try:
        df = pd.read_csv(SITE_METRICS_URL)
        if df.empty:
            return pd.DataFrame()
        
        df.columns = df.columns.str.strip()
        
        month_col = None
        reg_col = None
        ftd_col = None
        pl_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'month' in col_lower or 'date' in col_lower:
                month_col = col
            elif 'regist' in col_lower or 'reg' in col_lower:
                reg_col = col
            elif 'ftd' in col_lower:
                ftd_col = col
            elif 'profit' in col_lower or 'loss' in col_lower or 'pl' in col_lower:
                pl_col = col
        
        if month_col:
            df = df.rename(columns={month_col: 'Month'})
        if reg_col:
            df = df.rename(columns={reg_col: 'Registrations'})
        if ftd_col:
            df = df.rename(columns={ftd_col: 'FTD'})
        if pl_col:
            df = df.rename(columns={pl_col: 'Profit/Loss'})
        
        required_cols = ['Month', 'Registrations', 'FTD', 'Profit/Loss']
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0
        
        for col in ['Registrations', 'FTD', 'Profit/Loss']:
            if col in df.columns:
                df[col] = df[col].apply(clean_number)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df = df.dropna(subset=['Month'], how='all')
        df = df[df['Month'].astype(str).str.strip() != '']
        
        if df.empty:
            return pd.DataFrame()
        
        return df
        
    except Exception as e:
        return pd.DataFrame()

# =========================
# LOAD DATA FOR SITES
# =========================
def load_site_data(site_key, site_config, load_ahrefs=True):
    """Load all data for a single site with optional Ahrefs data"""
    gsc_url = site_config["gsc_url"]
    ga4_property_id = site_config.get("ga4_property_id", "")
    ahrefs_target = site_config.get("ahrefs_target", site_key)
    is_priority = site_config.get("priority", False)
    
    data = {
        "site_key": site_key,
        "display_name": site_config.get("display_name", site_key),
        "category": site_config.get("category", "Uncategorized"),
        "site_config": site_config,
        "gsc_df": pd.DataFrame(),
        "queries_df": pd.DataFrame(),
        "pages_df": pd.DataFrame(),
        "ga4_data": {"sessions": 0, "active_users": 0, "total_users": 0, "pageviews": 0},
        "ahrefs_dr_data": None,
        "ahrefs_backlinks_df": pd.DataFrame(),
        "ahrefs_refdomains_df": pd.DataFrame(),
        "ahrefs_keywords_df": pd.DataFrame(),
        "has_data": False,
        "ga4_error": False,
        "ahrefs_error": False,
        "ahrefs_error_message": "",
        "is_priority": is_priority
    }
    
    # GSC Data - Always load
    try:
        gsc_df = get_gsc_data(gsc_url, GSC_START_DATE, GSC_END_DATE)
        if not gsc_df.empty:
            data["gsc_df"] = gsc_df
            data["has_data"] = True
    except Exception as e:
        pass
    
    try:
        queries_df = get_gsc_queries(gsc_url, GSC_START_DATE, GSC_END_DATE)
        if not queries_df.empty:
            data["queries_df"] = queries_df
            data["has_data"] = True
    except Exception as e:
        pass
    
    try:
        pages_df = get_gsc_pages(gsc_url, GSC_START_DATE, GSC_END_DATE)
        if not pages_df.empty:
            data["pages_df"] = pages_df
            data["has_data"] = True
    except Exception as e:
        pass
    
    # GA4 Data
    try:
        if ga4_property_id:
            ga4_data = get_ga4_data(ga4_property_id)
            if ga4_data["sessions"] > 0:
                data["ga4_data"] = ga4_data
                data["has_data"] = True
        else:
            data["ga4_error"] = True
    except Exception as e:
        data["ga4_error"] = True
    
    # Ahrefs Data
    if load_ahrefs and AHREFS_API_KEY:
        # Domain Rating
        ahrefs_dr_data, dr_error = get_ahrefs_domain_rating(ahrefs_target)
        if ahrefs_dr_data:
            if isinstance(ahrefs_dr_data, dict):
                if 'domain_rating' in ahrefs_dr_data:
                    data["ahrefs_dr_data"] = {
                        'domain_rating': ahrefs_dr_data.get('domain_rating'),
                        'ahrefs_rank': ahrefs_dr_data.get('ahrefs_rank')
                    }
                    data["has_data"] = True
                elif 'data' in ahrefs_dr_data:
                    inner_data = ahrefs_dr_data['data']
                    if isinstance(inner_data, dict):
                        data["ahrefs_dr_data"] = {
                            'domain_rating': inner_data.get('domain_rating'),
                            'ahrefs_rank': inner_data.get('ahrefs_rank')
                        }
                        data["has_data"] = True
                else:
                    data["ahrefs_dr_data"] = ahrefs_dr_data
                    data["has_data"] = True
        elif dr_error:
            data["ahrefs_error"] = True
            if check_ahrefs_quota_error(dr_error):
                data["ahrefs_error_message"] = "QUOTA_EXHAUSTED"
            else:
                data["ahrefs_error_message"] = dr_error[:100]
        
        # Backlinks
        ahrefs_backlinks_data, bl_error = get_ahrefs_backlinks(ahrefs_target)
        if ahrefs_backlinks_data:
            if isinstance(ahrefs_backlinks_data, dict):
                if 'backlinks' in ahrefs_backlinks_data:
                    backlinks = ahrefs_backlinks_data['backlinks']
                    if backlinks:
                        data["ahrefs_backlinks_df"] = pd.DataFrame(backlinks)
                        data["has_data"] = True
                elif 'data' in ahrefs_backlinks_data:
                    inner_data = ahrefs_backlinks_data['data']
                    if isinstance(inner_data, dict) and 'backlinks' in inner_data:
                        backlinks = inner_data['backlinks']
                        if backlinks:
                            data["ahrefs_backlinks_df"] = pd.DataFrame(backlinks)
                            data["has_data"] = True
                    elif isinstance(inner_data, list):
                        data["ahrefs_backlinks_df"] = pd.DataFrame(inner_data)
                        data["has_data"] = True
        elif bl_error:
            data["ahrefs_error"] = True
            if check_ahrefs_quota_error(bl_error):
                data["ahrefs_error_message"] = "QUOTA_EXHAUSTED"
            else:
                data["ahrefs_error_message"] += f" BL: {bl_error[:50]}"
        
        # Referring Domains
        ahrefs_refdomains_data, rd_error = get_ahrefs_refdomains(ahrefs_target)
        if ahrefs_refdomains_data:
            if isinstance(ahrefs_refdomains_data, dict):
                if 'refdomains' in ahrefs_refdomains_data:
                    refdomains = ahrefs_refdomains_data['refdomains']
                    if refdomains:
                        data["ahrefs_refdomains_df"] = pd.DataFrame(refdomains)
                        data["has_data"] = True
                elif 'data' in ahrefs_refdomains_data:
                    inner_data = ahrefs_refdomains_data['data']
                    if isinstance(inner_data, dict) and 'refdomains' in inner_data:
                        refdomains = inner_data['refdomains']
                        if refdomains:
                            data["ahrefs_refdomains_df"] = pd.DataFrame(refdomains)
                            data["has_data"] = True
                    elif isinstance(inner_data, list):
                        data["ahrefs_refdomains_df"] = pd.DataFrame(inner_data)
                        data["has_data"] = True
        elif rd_error:
            data["ahrefs_error"] = True
            if check_ahrefs_quota_error(rd_error):
                data["ahrefs_error_message"] = "QUOTA_EXHAUSTED"
            else:
                data["ahrefs_error_message"] += f" RD: {rd_error[:50]}"
        
        # Organic Keywords
        ahrefs_keywords_data, kw_error = get_ahrefs_organic_keywords(ahrefs_target)
        if ahrefs_keywords_data:
            if isinstance(ahrefs_keywords_data, dict):
                if 'keywords' in ahrefs_keywords_data:
                    keywords = ahrefs_keywords_data['keywords']
                    if keywords:
                        data["ahrefs_keywords_df"] = pd.DataFrame(keywords)
                        data["has_data"] = True
                elif 'data' in ahrefs_keywords_data:
                    inner_data = ahrefs_keywords_data['data']
                    if isinstance(inner_data, dict) and 'keywords' in inner_data:
                        keywords = inner_data['keywords']
                        if keywords:
                            data["ahrefs_keywords_df"] = pd.DataFrame(keywords)
                            data["has_data"] = True
                    elif isinstance(inner_data, list):
                        data["ahrefs_keywords_df"] = pd.DataFrame(inner_data)
                        data["has_data"] = True
        elif kw_error:
            data["ahrefs_error"] = True
            if check_ahrefs_quota_error(kw_error):
                data["ahrefs_error_message"] = "QUOTA_EXHAUSTED"
            else:
                data["ahrefs_error_message"] += f" KW: {kw_error[:50]}"
    elif not AHREFS_API_KEY:
        data["ahrefs_error"] = True
        data["ahrefs_error_message"] = "Missing AHREFS_API_KEY"
    
    return data

def aggregate_site_data(site_data_list):
    """Aggregate data from multiple sites"""
    if not site_data_list:
        return None
    
    all_gsc_dfs = []
    all_queries_dfs = []
    all_pages_dfs = []
    all_ahrefs_keywords = []
    all_ahrefs_backlinks = []
    all_ahrefs_refdomains = []
    
    total_clicks = 0
    total_impressions = 0
    total_sessions = 0
    total_users = 0
    total_pageviews = 0
    
    ga4_errors = []
    ahrefs_errors = []
    
    for data in site_data_list:
        if data.get("ga4_error"):
            ga4_errors.append(data["display_name"])
        if data.get("ahrefs_error"):
            ahrefs_errors.append(data["display_name"])
        
        if not data["gsc_df"].empty:
            all_gsc_dfs.append(data["gsc_df"])
            total_clicks += data["gsc_df"]["Clicks"].sum()
            total_impressions += data["gsc_df"]["Impressions"].sum()
        
        if not data["queries_df"].empty:
            all_queries_dfs.append(data["queries_df"])
        
        if not data["pages_df"].empty:
            all_pages_dfs.append(data["pages_df"])
        
        if not data["ahrefs_keywords_df"].empty:
            all_ahrefs_keywords.append(data["ahrefs_keywords_df"])
        
        if not data["ahrefs_backlinks_df"].empty:
            all_ahrefs_backlinks.append(data["ahrefs_backlinks_df"])
        
        if not data["ahrefs_refdomains_df"].empty:
            all_ahrefs_refdomains.append(data["ahrefs_refdomains_df"])
        
        ga4 = data["ga4_data"]
        total_sessions += ga4["sessions"]
        total_users += ga4["active_users"]
        total_pageviews += ga4["pageviews"]
    
    # Combine GSC data
    combined_gsc = pd.concat(all_gsc_dfs, ignore_index=True) if all_gsc_dfs else pd.DataFrame()
    combined_queries = pd.concat(all_queries_dfs, ignore_index=True) if all_queries_dfs else pd.DataFrame()
    combined_pages = pd.concat(all_pages_dfs, ignore_index=True) if all_pages_dfs else pd.DataFrame()
    
    # Aggregate combined GSC data
    if not combined_gsc.empty:
        combined_gsc = combined_gsc.groupby("Date").agg({
            "Clicks": "sum",
            "Impressions": "sum",
            "CTR": "mean",
            "Position": "mean"
        }).reset_index()
        combined_gsc["CTR"] = combined_gsc["CTR"].round(2)
        combined_gsc["Position"] = combined_gsc["Position"].round(2)
    
    if not combined_queries.empty:
        combined_queries = combined_queries.groupby("Keyword").agg({
            "Clicks": "sum",
            "Impressions": "sum",
            "CTR": "mean",
            "Position": "mean"
        }).reset_index()
        combined_queries["CTR"] = combined_queries["CTR"].round(2)
        combined_queries["Position"] = combined_queries["Position"].round(2)
        combined_queries = combined_queries.sort_values("Clicks", ascending=False)
    
    if not combined_pages.empty:
        combined_pages = combined_pages.groupby("Page").agg({
            "Clicks": "sum",
            "Impressions": "sum",
            "CTR": "mean",
            "Position": "mean"
        }).reset_index()
        combined_pages["CTR"] = combined_pages["CTR"].round(2)
        combined_pages["Position"] = combined_pages["Position"].round(2)
        combined_pages = combined_pages.sort_values("Clicks", ascending=False)
    
    # Combine Ahrefs data
    combined_ahrefs_keywords = pd.concat(all_ahrefs_keywords, ignore_index=True) if all_ahrefs_keywords else pd.DataFrame()
    combined_ahrefs_backlinks = pd.concat(all_ahrefs_backlinks, ignore_index=True) if all_ahrefs_backlinks else pd.DataFrame()
    combined_ahrefs_refdomains = pd.concat(all_ahrefs_refdomains, ignore_index=True) if all_ahrefs_refdomains else pd.DataFrame()
    
    # Get Ahrefs domain data from first site that has it
    ahrefs_dr_data = None
    for data in site_data_list:
        if data.get("ahrefs_dr_data"):
            ahrefs_dr_data = data["ahrefs_dr_data"]
            break
    
    # Get combined Ahrefs metrics
    ahrefs_refdomains = len(combined_ahrefs_refdomains) if not combined_ahrefs_refdomains.empty else 0
    ahrefs_backlinks_count = len(combined_ahrefs_backlinks) if not combined_ahrefs_backlinks.empty else 0
    ahrefs_keywords_count = len(combined_ahrefs_keywords) if not combined_ahrefs_keywords.empty else 0
    
    return {
        "gsc_df": combined_gsc,
        "queries_df": combined_queries,
        "pages_df": combined_pages,
        "ahrefs_keywords_df": combined_ahrefs_keywords,
        "ahrefs_backlinks_df": combined_ahrefs_backlinks,
        "ahrefs_refdomains_df": combined_ahrefs_refdomains,
        "ga4_data": {
            "sessions": total_sessions,
            "active_users": total_users,
            "total_users": total_users,
            "pageviews": total_pageviews
        },
        "ahrefs_dr_data": ahrefs_dr_data,
        "ahrefs_refdomains": ahrefs_refdomains,
        "ahrefs_backlinks_count": ahrefs_backlinks_count,
        "ahrefs_keywords_count": ahrefs_keywords_count,
        "total_clicks": total_clicks,
        "total_impressions": total_impressions,
        "total_sessions": total_sessions,
        "site_count": len(site_data_list),
        "ga4_errors": ga4_errors,
        "ahrefs_errors": ahrefs_errors
    }

def aggregate_by_category(site_data_list, category_name):
    """Aggregate data for a specific category"""
    category_data = [d for d in site_data_list if d.get("category") == category_name]
    if category_data:
        return aggregate_site_data(category_data)
    return None

# =========================
# DETERMINE WHICH SITES TO LOAD
# =========================
sites_to_load = []

if view_mode == "View All Sites" or view_mode == "Category Comparison":
    sites_to_load = list(SITES.items())
elif view_mode == "View by Category" and selected_category:
    sites_to_load = [(site, SITES[site]) for site in category_sites]
elif view_mode == "View Individual Site" and selected_site:
    sites_to_load = [(selected_site, site_config)]

# Load data for each site
site_data_list = []
for site_key, site_config in sites_to_load:
    # Always load Ahrefs data if API key is configured
    load_ahrefs = bool(AHREFS_API_KEY)
    
    data = load_site_data(site_key, site_config, load_ahrefs)
    site_data_list.append(data)

has_any_data = any(d["has_data"] for d in site_data_list) if site_data_list else False

# For Category Comparison mode
category_comparison_data = None
if view_mode == "Category Comparison":
    category_comparison_data = {}
    for category in CATEGORIES.keys():
        agg = aggregate_by_category(site_data_list, category)
        if agg:
            category_comparison_data[category] = agg

# Aggregate data if multiple sites
if len(site_data_list) > 1:
    aggregated_data = aggregate_site_data(site_data_list)
    if aggregated_data:
        gsc_df = aggregated_data["gsc_df"]
        queries_df = aggregated_data["queries_df"]
        pages_df = aggregated_data["pages_df"]
        ahrefs_keywords_df = aggregated_data["ahrefs_keywords_df"]
        ahrefs_backlinks_df = aggregated_data["ahrefs_backlinks_df"]
        ahrefs_refdomains_df = aggregated_data["ahrefs_refdomains_df"]
        ga4_data = aggregated_data["ga4_data"]
        ahrefs_dr_data = aggregated_data["ahrefs_dr_data"]
        ahrefs_refdomains = aggregated_data["ahrefs_refdomains"]
        ahrefs_backlinks_count = aggregated_data["ahrefs_backlinks_count"]
        ahrefs_keywords_count = aggregated_data["ahrefs_keywords_count"]
        total_clicks = aggregated_data["total_clicks"]
        total_impressions = aggregated_data["total_impressions"]
        site_count = aggregated_data["site_count"]
        ga4_errors = aggregated_data.get("ga4_errors", [])
        ahrefs_errors = aggregated_data.get("ahrefs_errors", [])
    else:
        gsc_df = pd.DataFrame()
        queries_df = pd.DataFrame()
        pages_df = pd.DataFrame()
        ahrefs_keywords_df = pd.DataFrame()
        ahrefs_backlinks_df = pd.DataFrame()
        ahrefs_refdomains_df = pd.DataFrame()
        ga4_data = {"sessions": 0, "active_users": 0, "total_users": 0, "pageviews": 0}
        ahrefs_dr_data = None
        ahrefs_refdomains = 0
        ahrefs_backlinks_count = 0
        ahrefs_keywords_count = 0
        total_clicks = 0
        total_impressions = 0
        site_count = 0
        ga4_errors = []
        ahrefs_errors = []
else:
    data = site_data_list[0] if site_data_list else None
    if data and data["has_data"]:
        gsc_df = data["gsc_df"]
        queries_df = data["queries_df"]
        pages_df = data["pages_df"]
        ahrefs_keywords_df = data["ahrefs_keywords_df"]
        ahrefs_backlinks_df = data["ahrefs_backlinks_df"]
        ahrefs_refdomains_df = data["ahrefs_refdomains_df"]
        ga4_data = data["ga4_data"]
        ahrefs_dr_data = data["ahrefs_dr_data"]
        ahrefs_refdomains = len(ahrefs_refdomains_df) if not ahrefs_refdomains_df.empty else 0
        ahrefs_backlinks_count = len(ahrefs_backlinks_df) if not ahrefs_backlinks_df.empty else 0
        ahrefs_keywords_count = len(ahrefs_keywords_df) if not ahrefs_keywords_df.empty else 0
        total_clicks = gsc_df["Clicks"].sum() if not gsc_df.empty else 0
        total_impressions = gsc_df["Impressions"].sum() if not gsc_df.empty else 0
        site_count = 1
        ga4_errors = [data["display_name"]] if data.get("ga4_error") else []
        ahrefs_errors = [data["display_name"]] if data.get("ahrefs_error") else []
    else:
        gsc_df = pd.DataFrame()
        queries_df = pd.DataFrame()
        pages_df = pd.DataFrame()
        ahrefs_keywords_df = pd.DataFrame()
        ahrefs_backlinks_df = pd.DataFrame()
        ahrefs_refdomains_df = pd.DataFrame()
        ga4_data = {"sessions": 0, "active_users": 0, "total_users": 0, "pageviews": 0}
        ahrefs_dr_data = None
        ahrefs_refdomains = 0
        ahrefs_backlinks_count = 0
        ahrefs_keywords_count = 0
        total_clicks = 0
        total_impressions = 0
        site_count = 0
        ga4_errors = []
        ahrefs_errors = []

# Load Metrics Data
try:
    metrics_df = get_metrics_data()
    if not metrics_df.empty:
        st.sidebar.markdown(f'<span class="data-loaded-badge success">✅ Metrics: {len(metrics_df)} rows</span>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<span class="data-loaded-badge warning">⚠️ Metrics: Empty</span>', unsafe_allow_html=True)
except:
    metrics_df = pd.DataFrame()
    st.sidebar.markdown('<span class="data-loaded-badge error">❌ Metrics Error</span>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="sidebar-label">🌐 Sites Loaded</div>', unsafe_allow_html=True)

if site_count > 1:
    st.sidebar.info(f"📊 {site_count} sites aggregated")
elif site_count == 1 and site_data_list:
    site_display = site_data_list[0]["display_name"]
    st.sidebar.info(f"📊 {site_display}")
else:
    st.sidebar.warning("⚠️ No sites loaded")

# Show API Errors with details
if ga4_errors:
    st.sidebar.warning(f"⚠️ GA4 Errors for: {', '.join(ga4_errors[:3])}")
if ahrefs_errors:
    st.sidebar.warning(f"⚠️ Ahrefs Errors for: {', '.join(ahrefs_errors[:3])}")
    if site_data_list:
        for data in site_data_list:
            if data.get("ahrefs_error") and data.get("ahrefs_error_message"):
                if "QUOTA_EXHAUSTED" in data["ahrefs_error_message"]:
                    st.sidebar.error("🚫 Ahrefs API Quota Exhausted")
                else:
                    st.sidebar.info(f"🔍 {data['display_name']}: {data['ahrefs_error_message'][:50]}")

# =========================
# CALCULATIONS
# =========================
if not gsc_df.empty:
    total_clicks = int(gsc_df["Clicks"].sum())
    total_impressions = int(gsc_df["Impressions"].sum())
    avg_ctr = round((total_clicks / total_impressions) * 100, 2) if total_impressions else 0
    avg_position = round(gsc_df["Position"].mean(), 2)
else:
    total_clicks = 0
    total_impressions = 0
    avg_ctr = 0
    avg_position = 0

unique_queries = len(queries_df) if not queries_df.empty else 0
unique_ahrefs_keywords = ahrefs_keywords_count

rank_position = str(avg_position) if avg_position > 0 else "N/A"

if not metrics_df.empty:
    latest_row = metrics_df.iloc[-1]
    latest_month = str(latest_row['Month']) if pd.notna(latest_row['Month']) else 'N/A'
    latest_registrations = int(latest_row['Registrations']) if pd.notna(latest_row['Registrations']) else 0
    latest_ftd = int(latest_row['FTD']) if pd.notna(latest_row['FTD']) else 0
    latest_profit_loss = float(latest_row['Profit/Loss']) if pd.notna(latest_row['Profit/Loss']) else 0
    
    total_registrations = int(metrics_df['Registrations'].sum()) if 'Registrations' in metrics_df.columns else 0
    total_ftd = int(metrics_df['FTD'].sum()) if 'FTD' in metrics_df.columns else 0
    total_profit_loss = float(metrics_df['Profit/Loss'].sum()) if 'Profit/Loss' in metrics_df.columns else 0
    ftd_rate = (total_ftd / total_registrations * 100) if total_registrations > 0 else 0
    metrics_count = len(metrics_df)
else:
    latest_month = 'N/A'
    latest_registrations = 0
    latest_ftd = 0
    latest_profit_loss = 0
    total_registrations = 0
    total_ftd = 0
    total_profit_loss = 0
    ftd_rate = 0
    metrics_count = 0

# Extract Ahrefs DR correctly
ahrefs_domain_rating = "N/A"
ahrefs_rank = "N/A"

if ahrefs_dr_data:
    if isinstance(ahrefs_dr_data, dict):
        if 'domain_rating' in ahrefs_dr_data:
            ahrefs_domain_rating = str(ahrefs_dr_data['domain_rating'])
        elif 'metrics' in ahrefs_dr_data and 'domain_rating' in ahrefs_dr_data['metrics']:
            ahrefs_domain_rating = str(ahrefs_dr_data['metrics']['domain_rating'])
        
        if 'ahrefs_rank' in ahrefs_dr_data:
            ahrefs_rank = str(ahrefs_dr_data['ahrefs_rank'])
        elif 'metrics' in ahrefs_dr_data and 'ahrefs_rank' in ahrefs_dr_data['metrics']:
            ahrefs_rank = str(ahrefs_dr_data['metrics']['ahrefs_rank'])

def calculate_seo_score(avg_ctr, avg_position, sessions):
    score = 0
    score += min(avg_ctr * 4, 30)
    if avg_position <= 3:
        score += 30
    elif avg_position <= 10:
        score += 22
    elif avg_position <= 20:
        score += 14
    else:
        score += 6
    if sessions >= 1000:
        score += 15
    elif sessions >= 500:
        score += 10
    elif sessions >= 100:
        score += 6
    else:
        score += 2
    return round(min(score, 100), 1)

seo_score = calculate_seo_score(avg_ctr, avg_position, ga4_data["sessions"])

# =========================
# HTML EXPORT FUNCTIONS
# =========================
def dataframe_to_html(df, title, include_index=False):
    if df.empty:
        return f"<p>No {title} data available.</p>"
    df_display = df.copy()
    for col in df_display.columns:
        if df_display[col].dtype in ['float64', 'float32']:
            df_display[col] = df_display[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A")
        elif df_display[col].dtype in ['int64', 'int32']:
            df_display[col] = df_display[col].apply(lambda x: f"{x:,}" if pd.notna(x) else "N/A")
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            h1 {{ color: #1a1a2e; border-bottom: 3px solid #22c55e; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; }}
            th {{ background: #1a1a2e; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; }}
            tr:hover {{ background: #f0f4ff; }}
            .section {{ margin: 20px 0; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; }}
            .badge {{ display: inline-block; padding: 4px 12px; background: #22c55e; color: white; border-radius: 20px; font-size: 12px; }}
            .footer {{ margin-top: 30px; padding: 20px; border-top: 1px solid #e5e7eb; text-align: center; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header" style="display: flex; justify-content: space-between; align-items: center;">
                <h1>{title}</h1>
                <span class="badge">Export Date: {date.today().strftime('%Y-%m-%d')}</span>
            </div>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #22c55e;">
                <strong>Site:</strong> {selected_site if selected_site else 'All Sites'}<br>
                <strong>Date Range:</strong> {GSC_START_DATE} to {GSC_END_DATE}
            </div>
    """
    
    html += f"""
            <div class="section">
                <h2>Data Overview</h2>
                <p><strong>Total Records:</strong> {len(df):,}</p>
                <p><strong>Columns:</strong> {', '.join(df.columns)}</p>
            </div>
            <div class="section">
                <h2>Data Table</h2>
                <div style="overflow-x: auto; max-height: 500px; overflow-y: auto;">
                {df_display.to_html(index=include_index, classes='table')}
                </div>
            </div>
            <div class="footer">
                <p>Generated by Juan365 SEO Dashboard • Data from Google Search Console & Ahrefs</p>
                <p>This report is for internal use only.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def create_html_download(df, title, filename_prefix):
    if df.empty:
        return None
    html_content = dataframe_to_html(df, title)
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'data:text/html;base64,{b64}'
    site_name = selected_site if selected_site else "all_sites"
    return href, f"{filename_prefix}_{site_name}_{date.today().strftime('%Y%m%d')}.html"

# =========================
# AI SEO ALERTS
# =========================
def generate_ai_alerts():
    alerts = []

    if avg_ctr < 3 and total_impressions > 1000:
        alerts.append({
            "level": "danger",
            "title": "⚠️ CTR Opportunity Detected",
            "body": "Your impressions are strong but CTR is low. Review title tags and meta descriptions for top pages."
        })

    if avg_position > 10:
        alerts.append({
            "level": "warning",
            "title": "📊 Ranking Needs Improvement",
            "body": "Average position is outside page one. Prioritize internal links, content refresh, and topical relevance."
        })

    if ga4_data["sessions"] < 100:
        alerts.append({
            "level": "warning",
            "title": "📉 GA4 Traffic Is Still Low",
            "body": "Sessions are below 100 for the selected GA4 range. Compare with GSC clicks to check tracking or engagement gaps."
        })

    if not metrics_df.empty:
        if latest_profit_loss < 0:
            alerts.append({
                "level": "danger",
                "title": f"💰 Negative Profit/Loss: ₱{abs(latest_profit_loss):,.2f}",
                "body": f"The latest month ({latest_month}) shows a loss. Review your financial performance."
            })
        elif latest_profit_loss > 10000:
            alerts.append({
                "level": "success",
                "title": f"💰 Strong Profit: ₱{latest_profit_loss:,.2f}",
                "body": f"Your latest month ({latest_month}) shows strong profitability!"
            })
        
        if latest_registrations < 100 and latest_registrations > 0:
            alerts.append({
                "level": "warning",
                "title": f"📊 Low Registrations: {latest_registrations}",
                "body": f"Latest month ({latest_month}) only had {latest_registrations:,} registrations. Consider increasing marketing."
            })

    if not alerts:
        alerts.append({
            "level": "success",
            "title": "✅ SEO Status Looks Stable",
            "body": "No major warning detected based on current data."
        })

    return alerts

alerts = generate_ai_alerts()

# =========================
# PDF REPORT
# =========================
def generate_pdf_report():
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    pdf.setFillColor(colors.HexColor("#0f172a"))
    pdf.rect(0, 0, width, height, fill=True, stroke=False)

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(40, y, "JUAN365 SEO PERFORMANCE REPORT")

    y -= 30
    pdf.setFont("Helvetica", 11)
    pdf.setFillColor(colors.HexColor("#cbd5e1"))
    
    if view_mode == "View All Sites" or view_mode == "Category Comparison":
        pdf.drawString(40, y, f"Website: ALL SITES ({site_count} sites)")
    elif view_mode == "View by Category":
        pdf.drawString(40, y, f"Category: {selected_category} ({site_count} sites)")
    else:
        pdf.drawString(40, y, f"Website: {selected_site}")
    
    y -= 18
    pdf.drawString(40, y, f"Date Range: {GSC_START_DATE} to {GSC_END_DATE}")
    y -= 18
    pdf.drawString(40, y, f"Previous Range: {PREVIOUS_START_DATE} to {PREVIOUS_END_DATE}")

    y -= 45
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(40, y, "Executive Summary")

    y -= 25
    pdf.setFont("Helvetica", 10)

    summary_items = [
        f"SEO Score: {seo_score}/100",
        f"Total Clicks: {total_clicks:,}",
        f"Total Impressions: {total_impressions:,}",
        f"Average CTR: {avg_ctr}%",
        f"Average Position: {avg_position}",
        f"GA4 Sessions: {ga4_data['sessions']:,}",
        f"Unique GSC Queries: {unique_queries:,}",
        f"Unique Ahrefs Keywords: {unique_ahrefs_keywords:,}",
        f"Latest Month: {latest_month}",
        f"Latest Registrations: {latest_registrations:,}",
        f"Latest FTD: {latest_ftd:,}",
        f"Latest Profit/Loss: ₱{latest_profit_loss:,.2f}",
        f"FTD Rate: {ftd_rate:.1f}%",
        f"Ahrefs DR: {ahrefs_domain_rating}",
        f"Ahrefs Rank: {ahrefs_rank}",
        f"Ahrefs Referring Domains: {ahrefs_refdomains}",
        f"Ahrefs Backlinks: {ahrefs_backlinks_count}",
    ]

    for item in summary_items:
        pdf.drawString(55, y, item)
        y -= 15

    y -= 15
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Recommended SEO Actions")
    y -= 18
    pdf.setFont("Helvetica", 9)

    actions = [
        "Review keywords with low CTR but high impressions.",
        "Improve internal links for keywords ranking between positions 4 and 20.",
        "Refresh pages with declining keyword positions.",
        "Review Ahrefs backlinks and referring domains for authority growth.",
        "Continue monitoring performance metrics."
    ]

    for i, action in enumerate(actions, 1):
        pdf.drawString(55, y, f"{i}. {action}")
        y -= 13

    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(colors.HexColor("#94a3b8"))
    pdf.drawRightString(width - 25, 20, "Generated by Juan365 SEO Dashboard")

    pdf.save()
    buffer.seek(0)
    return buffer

# =========================
# HEADER
# =========================
if view_mode == "View All Sites" or view_mode == "Category Comparison":
    header_title = "Juan365 vs Competitors Dashboard"
    header_subtitle = f"Performance intelligence across {site_count} sites"
    header_badges = [f"● {site_count} Sites", f"● {period}"]
    
elif view_mode == "View by Category":
    cat_icon = CATEGORIES[selected_category]["icon"]
    header_title = f"{cat_icon} {selected_category} Dashboard"
    header_subtitle = f"{CATEGORIES[selected_category]['description']} • {site_count} sites"
    header_badges = [f"● {selected_category}", f"● {period}"]
    
else:
    site_display = site_data_list[0]["display_name"] if site_data_list and site_data_list[0].get("display_name") else selected_site
    header_title = f"🌐 {site_display}"
    header_subtitle = f"Individual site performance"
    header_badges = [f"● {site_display}", f"● {period}"]

st.markdown(f"""
<div class="dashboard-header">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
        <div>
            <div class="dashboard-title">{header_title}</div>
            <div class="dashboard-subtitle">{header_subtitle}</div>
            <div style="display: flex; gap: 0.75rem; margin-top: 0.75rem; flex-wrap: wrap;">
                <span class="dashboard-badge live-indicator">● Live</span>
                {''.join([f'<span class="dashboard-badge" style="background: rgba(59, 130, 246, 0.15); color: #3b82f6; border-color: rgba(59, 130, 246, 0.2);">{badge}</span>' for badge in header_badges])}
            </div>
        </div>
        <div style="text-align: right; margin-top: 0.5rem;">
            <div style="font-size: 0.7rem; color: #94a3b8; letter-spacing: 0.05em; text-transform: uppercase;">Last Updated</div>
            <div style="font-size: 0.85rem; color: #e2e8f0; font-weight: 600;">{pd.Timestamp.now().strftime('%B %d, %Y • %H:%M')}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# CATEGORY OVERVIEW
# =========================
if view_mode == "View All Sites" or view_mode == "Category Comparison":
    st.markdown('<div class="section-title">📊 Category Overview</div>', unsafe_allow_html=True)
    
    cat_cols = st.columns(len(CATEGORIES))
    for idx, (category, cat_data) in enumerate(CATEGORIES.items()):
        with cat_cols[idx]:
            sites_with_data = 0
            total_clicks_cat = 0
            total_impressions_cat = 0
            total_sessions_cat = 0
            total_queries_cat = 0
            total_ahrefs_keywords_cat = 0
            
            for site in cat_data["sites"]:
                site_data = next((d for d in site_data_list if d.get("site_key") == site), None)
                if site_data and site_data.get("has_data"):
                    sites_with_data += 1
                    if not site_data["gsc_df"].empty:
                        total_clicks_cat += site_data["gsc_df"]["Clicks"].sum()
                        total_impressions_cat += site_data["gsc_df"]["Impressions"].sum()
                    if not site_data["queries_df"].empty:
                        total_queries_cat += len(site_data["queries_df"])
                    if not site_data["ahrefs_keywords_df"].empty:
                        total_ahrefs_keywords_cat += len(site_data["ahrefs_keywords_df"])
                    total_sessions_cat += site_data["ga4_data"]["sessions"]
            
            st.markdown(f"""
            <div class="kpi-card" style="--accent-color: {cat_data['color']};">
                <div class="kpi-icon">{cat_data['icon']}</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: {cat_data['color']}; margin-bottom: 0.25rem;">
                    {category}
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem; margin-top: 0.5rem;">
                    <div>
                        <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase;">Sites</div>
                        <div style="font-size: 1.2rem; font-weight: 700; color: #ffffff;">{sites_with_data}/{len(cat_data['sites'])}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase;">Clicks</div>
                        <div style="font-size: 1.2rem; font-weight: 700; color: #facc15;">{total_clicks_cat:,}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase;">Impressions</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #60a5fa;">{total_impressions_cat:,}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase;">Sessions</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #34d399;">{total_sessions_cat:,}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase;">GSC Queries</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #c084fc;">{total_queries_cat:,}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase;">Ahrefs Keywords</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #fb923c;">{total_ahrefs_keywords_cat:,}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# =========================
# CATEGORY COMPARISON
# =========================
if view_mode == "Category Comparison" and category_comparison_data:
    st.markdown('<div class="section-title">⚖️ Category Comparison</div>', unsafe_allow_html=True)
    
    comparison_metrics = []
    for category, data in category_comparison_data.items():
        if data:
            comparison_metrics.append({
                "Category": category,
                "Clicks": data["total_clicks"],
                "Impressions": data["total_impressions"],
                "Sessions": data["ga4_data"]["sessions"],
                "Sites": data["site_count"],
                "GSC Queries": len(data["queries_df"]) if not data["queries_df"].empty else 0,
                "Ahrefs Keywords": len(data["ahrefs_keywords_df"]) if not data["ahrefs_keywords_df"].empty else 0
            })
    
    if comparison_metrics:
        comp_df = pd.DataFrame(comparison_metrics)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_comp = go.Figure()
            
            fig_comp.add_trace(go.Bar(
                x=comp_df['Category'],
                y=comp_df['Clicks'],
                name='Clicks',
                marker_color=['#22c55e' if cat == 'Juan365' else '#f59e0b' for cat in comp_df['Category']],
                text=comp_df['Clicks'],
                textposition='outside',
                textfont=dict(color='#e5e7eb', size=12)
            ))
            
            fig_comp.add_trace(go.Bar(
                x=comp_df['Category'],
                y=comp_df['Impressions'],
                name='Impressions',
                marker_color=['#3b82f6' if cat == 'Juan365' else '#f97316' for cat in comp_df['Category']],
                text=comp_df['Impressions'],
                textposition='outside',
                textfont=dict(color='#e5e7eb', size=12)
            ))
            
            fig_comp.update_layout(
                height=350,
                title="<b>Performance Comparison</b>",
                paper_bgcolor="rgba(255,255,255,0.02)",
                plot_bgcolor="rgba(255,255,255,0.02)",
                font=dict(color="#e5e7eb", family="Inter"),
                margin=dict(l=40, r=40, t=50, b=40),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Count"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(color="#e5e7eb", size=12)),
                hovermode="x unified",
                barmode='group'
            )
            
            st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            fig_queries = go.Figure()
            
            fig_queries.add_trace(go.Bar(
                x=comp_df['Category'],
                y=comp_df['GSC Queries'],
                name='GSC Queries',
                marker_color=['#8b5cf6' if cat == 'Juan365' else '#ec4899' for cat in comp_df['Category']],
                text=comp_df['GSC Queries'],
                textposition='outside',
                textfont=dict(color='#e5e7eb', size=12)
            ))
            
            fig_queries.add_trace(go.Bar(
                x=comp_df['Category'],
                y=comp_df['Ahrefs Keywords'],
                name='Ahrefs Keywords',
                marker_color=['#f97316' if cat == 'Juan365' else '#f59e0b' for cat in comp_df['Category']],
                text=comp_df['Ahrefs Keywords'],
                textposition='outside',
                textfont=dict(color='#e5e7eb', size=12)
            ))
            
            fig_queries.update_layout(
                height=350,
                title="<b>Keywords & Queries Comparison</b>",
                paper_bgcolor="rgba(255,255,255,0.02)",
                plot_bgcolor="rgba(255,255,255,0.02)",
                font=dict(color="#e5e7eb", family="Inter"),
                margin=dict(l=40, r=40, t=50, b=40),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Count"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(color="#e5e7eb", size=12)),
                hovermode="x unified",
                barmode='group'
            )
            
            st.plotly_chart(fig_queries, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("### 📊 Comparison Table")
        st.dataframe(comp_df, use_container_width=True)

# =========================
# NO DATA WARNING
# =========================
if not has_any_data and site_data_list:
    st.warning("""
    ⚠️ **No data available for the selected view**
    
    Please check:
    - GSC/GA4 API permissions
    - Date range selection
    - Site configuration
    - Google Search Console property verification
    """)

# =========================
# GSC QUERIES SECTION
# =========================
st.markdown('<div class="section-title">🔍 GSC Queries - All Sites & Categories</div>', unsafe_allow_html=True)

if not queries_df.empty:
    st.markdown("### 🏆 Top 20 Queries (All Sites Combined)")
    top_queries = queries_df.head(20)
    
    fig_queries_top = go.Figure()
    fig_queries_top.add_trace(go.Bar(
        y=top_queries['Keyword'].apply(lambda x: x[:40] + '...' if len(x) > 40 else x),
        x=top_queries['Clicks'],
        orientation='h',
        marker=dict(
            color=top_queries['Clicks'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Clicks")
        ),
        text=top_queries['Clicks'],
        textposition='outside',
        textfont=dict(color='#e5e7eb', size=10)
    ))
    
    fig_queries_top.update_layout(
        height=500,
        title="<b>Top Queries by Clicks</b>",
        paper_bgcolor="rgba(255,255,255,0.02)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#e5e7eb", family="Inter"),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Clicks"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title=""),
        hovermode="y unified"
    )
    
    st.plotly_chart(fig_queries_top, use_container_width=True, config={'displayModeBar': False})
    
    with st.expander("📊 View All Queries Data", expanded=False):
        st.dataframe(queries_df, use_container_width=True)
else:
    st.warning("No GSC query data found.")

# =========================
# AHREFS KEYWORDS SECTION
# =========================
st.markdown('<div class="section-title">🔑 Ahrefs Keywords - All Sites & Categories</div>', unsafe_allow_html=True)

if not ahrefs_keywords_df.empty:
    st.markdown("### 🏆 Top 20 Ahrefs Keywords (All Sites Combined)")
    top_ahrefs = ahrefs_keywords_df.head(20)
    
    keyword_col = 'keyword' if 'keyword' in top_ahrefs.columns else top_ahrefs.columns[0] if len(top_ahrefs.columns) > 0 else None
    volume_col = 'volume' if 'volume' in top_ahrefs.columns else None
    position_col = 'best_position' if 'best_position' in top_ahrefs.columns else None
    
    if keyword_col:
        fig_ahrefs_top = go.Figure()
        fig_ahrefs_top.add_trace(go.Bar(
            y=top_ahrefs[keyword_col].apply(lambda x: str(x)[:40] + '...' if len(str(x)) > 40 else str(x)),
            x=top_ahrefs[volume_col] if volume_col else [0] * len(top_ahrefs),
            orientation='h',
            marker=dict(
                color=top_ahrefs[volume_col] if volume_col else [0] * len(top_ahrefs),
                colorscale='Oranges',
                showscale=True,
                colorbar=dict(title="Volume")
            ),
            text=top_ahrefs[position_col] if position_col else ['N/A'] * len(top_ahrefs),
            textposition='outside',
            textfont=dict(color='#e5e7eb', size=10)
        ))
        
        fig_ahrefs_top.update_layout(
            height=500,
            title="<b>Top Ahrefs Keywords by Search Volume</b>",
            paper_bgcolor="rgba(255,255,255,0.02)",
            plot_bgcolor="rgba(255,255,255,0.02)",
            font=dict(color="#e5e7eb", family="Inter"),
            margin=dict(l=40, r=40, t=50, b=40),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Search Volume"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title=""),
            hovermode="y unified"
        )
        
        st.plotly_chart(fig_ahrefs_top, use_container_width=True, config={'displayModeBar': False})
        
        with st.expander("📊 View All Ahrefs Keywords Data", expanded=False):
            st.dataframe(ahrefs_keywords_df, use_container_width=True)
    else:
        st.info("Ahrefs keywords data available but in unexpected format.")
else:
    if AHREFS_API_KEY:
        quota_exhausted = any("QUOTA_EXHAUSTED" in data.get("ahrefs_error_message", "") for data in site_data_list)
        invalid_key = any("Invalid API key" in data.get("ahrefs_error_message", "") for data in site_data_list)
        
        if invalid_key:
            st.warning("⚠️ **Invalid Ahrefs API Key**")
            st.info("🔑 Your Ahrefs API key appears to be invalid or in the wrong format.\n\n**Solution:** Get a valid 64-character API key from https://ahrefs.com/api")
        elif quota_exhausted:
            st.warning("⚠️ **Ahrefs API Quota Exhausted**")
            st.info("💡 Your Ahrefs API has no units left. Please upgrade your plan or wait for the monthly reset.\n\n**Solution:** Get a higher-tier Ahrefs plan or wait for your billing cycle to reset.")
        else:
            st.warning("⚠️ No Ahrefs keyword data found. Check API permissions.")
    else:
        st.warning("⚠️ **Ahrefs API Key not configured** in Streamlit secrets.\n\nAdd `AHREFS_API_KEY = \"your_key\"` to your `.streamlit/secrets.toml` file.")

# =========================
# INDIVIDUAL SITE QUERIES & KEYWORDS
# =========================
if view_mode == "View Individual Site" and site_data_list:
    st.markdown('<div class="section-title">📋 Individual Site Queries & Keywords</div>', unsafe_allow_html=True)
    
    site_data = site_data_list[0]
    
    col_q, col_k = st.columns(2)
    
    with col_q:
        st.markdown(f"### 🔍 GSC Queries for {site_data['display_name']}")
        if not site_data["queries_df"].empty:
            st.dataframe(site_data["queries_df"].head(50), use_container_width=True)
        else:
            st.info("No query data available for this site")
    
    with col_k:
        st.markdown(f"### 🔑 Ahrefs Keywords for {site_data['display_name']}")
        if not site_data["ahrefs_keywords_df"].empty:
            st.dataframe(site_data["ahrefs_keywords_df"].head(50), use_container_width=True)
        else:
            if site_data.get("ahrefs_error"):
                if "QUOTA_EXHAUSTED" in site_data.get("ahrefs_error_message", ""):
                    st.warning("⚠️ Ahrefs API quota exhausted. No keyword data available.")
                elif "Invalid API key" in site_data.get("ahrefs_error_message", ""):
                    st.warning("⚠️ Invalid Ahrefs API key. Please check your credentials.")
                else:
                    st.warning("⚠️ Ahrefs API error occurred")
            else:
                st.info("No Ahrefs keyword data available for this site")

# =========================
# BUSINESS INTELLIGENCE SECTION
# =========================
st.markdown('<div class="section-title-ai">🤖 Bert Bot</div>', unsafe_allow_html=True)

if not metrics_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_class = "badge-positive" if latest_registrations > 100 else "badge-negative" if latest_registrations < 50 else "badge-neutral"
        status_text = "🚀 GROWING" if latest_registrations > 100 else "📉 LOW" if latest_registrations < 50 else "📊 STEADY"
        st.markdown(f"""
        <div class="ai-card">
            <div class="icon">👤</div>
            <div style="margin-top: 0.5rem;">
                <div class="label">Registrations</div>
                <div class="value">{latest_registrations:,}</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                    <span style="font-size: 0.75rem; color: #94a3b8;">Total: {total_registrations:,}</span>
                    <span class="badge {status_class}">{status_text}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status_class = "badge-positive" if latest_ftd > 20 else "badge-negative" if latest_ftd < 10 else "badge-neutral"
        status_text = "HIGH" if latest_ftd > 20 else "📉 LOW" if latest_ftd < 10 else "📊 MODERATE"
        st.markdown(f"""
        <div class="ai-card">
            <div class="icon">💰</div>
            <div style="margin-top: 0.5rem;">
                <div class="label">First Time Deposits</div>
                <div class="value">{latest_ftd:,}</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                    <span style="font-size: 0.75rem; color: #94a3b8;">Rate: {ftd_rate:.1f}%</span>
                    <span class="badge {status_class}">{status_text}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if latest_profit_loss > 0:
            status_class = "badge-positive"
            status_text = "📈 PROFIT"
            icon = "💰"
        elif latest_profit_loss < 0:
            status_class = "badge-negative"
            status_text = "📉 LOSS"
            icon = "⚠️"
        else:
            status_class = "badge-neutral"
            status_text = "⚖️ BREAK-EVEN"
            icon = "📊"
        
        color = "#22c55e" if latest_profit_loss >= 0 else "#ef4444"
        st.markdown(f"""
        <div class="ai-card">
            <div class="icon">{icon}</div>
            <div style="margin-top: 0.5rem;">
                <div class="label">Profit / Loss</div>
                <div class="value" style="background: linear-gradient(135deg, {color}, {color}dd); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">₱{latest_profit_loss:,.2f}</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                    <span style="font-size: 0.75rem; color: #94a3b8;">Total: ₱{total_profit_loss:,.2f}</span>
                    <span class="badge {status_class}">{status_text}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="ai-card">
            <div class="icon">📅</div>
            <div style="margin-top: 0.5rem;">
                <div class="label">Latest Month</div>
                <div class="value">{latest_month}</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                    <span style="font-size: 0.75rem; color: #94a3b8;">{metrics_count} months tracked</span>
                    <span class="badge badge-info">📊 ACTIVE</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    insights = []
    if latest_registrations > 100:
        insights.append(f"🚀 <strong>Strong growth</strong> with {latest_registrations} new users this month")
    elif latest_registrations < 50 and latest_registrations > 0:
        insights.append(f"⚠️ <strong>Low registration volume</strong> ({latest_registrations}) - consider marketing boost")
    
    if latest_ftd > 20:
        insights.append(f"💰 <strong>Excellent conversion</strong> with {latest_ftd} first-time deposits")
    elif latest_ftd < 10 and latest_ftd > 0:
        insights.append(f"⚠️ <strong>Low FTD</strong> ({latest_ftd}) - review conversion funnel")
    
    if latest_profit_loss > 5000:
        insights.append(f"💎 <strong>Strong profitability</strong> of ₱{latest_profit_loss:,.2f}")
    elif latest_profit_loss < 0:
        insights.append(f"📉 <strong>Loss detected</strong> (₱{abs(latest_profit_loss):,.2f}) - review expenses")
    elif latest_profit_loss == 0:
        insights.append("⚖️ <strong>Break-even</strong> position - look for growth opportunities")
    
    if not insights:
        insights.append("📊 <strong>Stable performance</strong> - continue monitoring key metrics")
    
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin: 1rem 0;">
        {''.join([f'<div class="ai-insight-card"><span style="font-size: 1.2rem; margin-right: 0.75rem;">💡</span><span style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.6;">{insight}</span></div>' for insight in insights])}
    </div>
    """, unsafe_allow_html=True)
    
    if len(metrics_df) > 1:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig_reg = go.Figure()
            
            fig_reg.add_trace(go.Bar(
                x=metrics_df['Month'],
                y=metrics_df['Registrations'],
                name='Registrations',
                marker=dict(
                    color='#8b5cf6',
                    opacity=0.85,
                    line=dict(color='#8b5cf6', width=1)
                ),
                text=metrics_df['Registrations'],
                textposition='outside',
                textfont=dict(color='#c4b5fd', size=11)
            ))
            
            fig_reg.add_trace(go.Scatter(
                x=metrics_df['Month'],
                y=metrics_df['FTD'],
                name='FTD',
                mode='lines+markers',
                line=dict(color='#22c55e', width=3),
                marker=dict(size=10, color='#22c55e', symbol='diamond'),
                text=metrics_df['FTD'],
                textposition='top center',
                textfont=dict(color='#22c55e', size=11)
            ))
            
            fig_reg.update_layout(
                height=350,
                title="<b>Registrations vs FTD</b>",
                paper_bgcolor="rgba(255,255,255,0.02)",
                plot_bgcolor="rgba(255,255,255,0.02)",
                font=dict(color="#e5e7eb", family="Inter"),
                margin=dict(l=40, r=40, t=50, b=40),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Month"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Count"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(color="#e5e7eb", size=11)),
                hovermode="x unified"
            )
            
            st.plotly_chart(fig_reg, use_container_width=True, config={'displayModeBar': False})
        
        with col_chart2:
            colors_profit = ['#22c55e' if x >= 0 else '#ef4444' for x in metrics_df['Profit/Loss']]
            
            fig_profit = go.Figure()
            
            fig_profit.add_trace(go.Bar(
                x=metrics_df['Month'],
                y=metrics_df['Profit/Loss'],
                name='Profit/Loss',
                marker=dict(
                    color=colors_profit,
                    opacity=0.85,
                    line=dict(color=colors_profit, width=1)
                ),
                text=[f"₱{x:,.2f}" for x in metrics_df['Profit/Loss']],
                textposition='outside',
                textfont=dict(color='#e5e7eb', size=10)
            ))
            
            fig_profit.add_trace(go.Scatter(
                x=metrics_df['Month'],
                y=[0] * len(metrics_df),
                mode='lines',
                name='Break-even',
                line=dict(color='#94a3b8', width=2, dash='dash')
            ))
            
            fig_profit.update_layout(
                height=350,
                title="<b>Monthly Profit/Loss Trend</b>",
                paper_bgcolor="rgba(255,255,255,0.02)",
                plot_bgcolor="rgba(255,255,255,0.02)",
                font=dict(color="#e5e7eb", family="Inter"),
                margin=dict(l=40, r=40, t=50, b=40),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Month"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Amount (₱)", tickprefix="₱"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(color="#e5e7eb", size=11)),
                hovermode="x unified"
            )
            
            st.plotly_chart(fig_profit, use_container_width=True, config={'displayModeBar': False})

else:
    st.warning("⚠️ No monthly metrics data available. Please check your Google Sheet connection.")

st.markdown("---")

# =========================
# SEO KPI CARDS
# =========================
st.markdown('<div class="section-title">SEO Performance</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #22c55e;">
        <div class="kpi-icon">🎯</div>
        <div class="kpi-label">SEO Score</div>
        <div class="kpi-value">{seo_score}/100</div>
        <div class="kpi-delta">Overall health</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #10b981;">
        <div class="kpi-icon">👆</div>
        <div class="kpi-label">Clicks</div>
        <div class="kpi-value">{total_clicks:,}</div>
        <div class="kpi-delta">Organic search clicks</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #3b82f6;">
        <div class="kpi-icon">👁️</div>
        <div class="kpi-label">Impressions</div>
        <div class="kpi-value">{total_impressions:,}</div>
        <div class="kpi-delta">Search visibility</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #8b5cf6;">
        <div class="kpi-icon">📊</div>
        <div class="kpi-label">CTR</div>
        <div class="kpi-value">{avg_ctr}%</div>
        <div class="kpi-delta">Click-through rate</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #f59e0b;">
        <div class="kpi-icon">📈</div>
        <div class="kpi-label">Avg Position</div>
        <div class="kpi-value">{avg_position}</div>
        <div class="kpi-delta">Ranking average</div>
    </div>
    """, unsafe_allow_html=True)

with c6:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #06b6d4;">
        <div class="kpi-icon">🌐</div>
        <div class="kpi-label">Sessions</div>
        <div class="kpi-value">{ga4_data['sessions']:,}</div>
        <div class="kpi-delta">GA4 traffic</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# AHREFS KPI CARDS
# =========================
st.markdown('<div class="section-title">Authority & Keyword Metrics</div>', unsafe_allow_html=True)

ah1, ah2, ah3, ah4, ah5 = st.columns(5)

with ah1:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #f97316;">
        <div class="kpi-icon">🏆</div>
        <div class="kpi-label">Domain Rating</div>
        <div class="kpi-value">{ahrefs_domain_rating}</div>
        <div class="kpi-delta">Ahrefs authority</div>
    </div>
    """, unsafe_allow_html=True)

with ah2:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #ec4899;">
        <div class="kpi-icon">🌍</div>
        <div class="kpi-label">Ahrefs Rank</div>
        <div class="kpi-value">{ahrefs_rank}</div>
        <div class="kpi-delta">Global authority</div>
    </div>
    """, unsafe_allow_html=True)

with ah3:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #14b8a6;">
        <div class="kpi-icon">🔗</div>
        <div class="kpi-label">Referring Domains</div>
        <div class="kpi-value">{ahrefs_refdomains}</div>
        <div class="kpi-delta">Link authority</div>
    </div>
    """, unsafe_allow_html=True)

with ah4:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #6366f1;">
        <div class="kpi-icon">📎</div>
        <div class="kpi-label">Backlinks</div>
        <div class="kpi-value">{ahrefs_backlinks_count}</div>
        <div class="kpi-delta">Total backlink signal</div>
    </div>
    """, unsafe_allow_html=True)

with ah5:
    st.markdown(f"""
    <div class="kpi-card" style="--accent-color: #f59e0b;">
        <div class="kpi-icon">🔑</div>
        <div class="kpi-label">Ahrefs Keywords</div>
        <div class="kpi-value">{unique_ahrefs_keywords:,}</div>
        <div class="kpi-delta">Total unique keywords</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# AI ALERTS
# =========================
st.markdown('<div class="section-title">Intelligent Alerts</div>', unsafe_allow_html=True)

for alert in alerts:
    css_class = "alert-card"
    if alert["level"] == "warning":
        css_class += " alert-warning"
    elif alert["level"] == "danger":
        css_class += " alert-danger"
    elif alert["level"] == "success":
        css_class += " alert-success"

    st.markdown(f"""
    <div class="{css_class}">
        <div class="alert-title">{alert["title"]}</div>
        <div class="alert-body">{alert["body"]}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# PERFORMANCE CHART
# =========================
st.markdown('<div class="section-title">Performance Trend</div>', unsafe_allow_html=True)

if not gsc_df.empty:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=gsc_df["Date"],
        y=gsc_df["Clicks"],
        mode="lines+markers",
        name="Clicks",
        line=dict(width=3, color="#10b981"),
        fill="tozeroy",
        fillcolor="rgba(16, 185, 129, 0.15)",
        marker=dict(size=6, color="#10b981")
    ))

    fig.add_trace(go.Scatter(
        x=gsc_df["Date"],
        y=gsc_df["Impressions"],
        mode="lines+markers",
        name="Impressions",
        line=dict(width=3, color="#3b82f6"),
        yaxis="y2",
        marker=dict(size=6, color="#3b82f6")
    ))

    fig.update_layout(
        height=400,
        paper_bgcolor="rgba(255,255,255,0.03)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#e5e7eb", family="Inter"),
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title=dict(text="Date", font=dict(color="#94a3b8", size=12))),
        yaxis=dict(title=dict(text="Clicks", font=dict(color="#94a3b8", size=12)), gridcolor="rgba(255,255,255,0.06)"),
        yaxis2=dict(title=dict(text="Impressions", font=dict(color="#94a3b8", size=12)), overlaying="y", side="right", gridcolor="rgba(255,255,255,0.06)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0.2)", font=dict(color="#e5e7eb", size=12)),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.warning("No GSC trend data found.")

# =========================
# TOP PAGES
# =========================
st.markdown('<div class="section-title">🏆 Top Performing Pages</div>', unsafe_allow_html=True)

if not pages_df.empty:
    top_pages = pages_df.sort_values("Clicks", ascending=False).head(10)
    
    fig_pages = go.Figure()
    
    fig_pages.add_trace(go.Bar(
        y=top_pages['Page'].apply(lambda x: x.replace('https://', '').replace('http://', '').split('/')[0] + '/' + '/'.join(x.replace('https://', '').replace('http://', '').split('/')[1:])[:30] if '/' in x.replace('https://', '').replace('http://', '') else x.replace('https://', '').replace('http://', '')[:30]),
        x=top_pages['Clicks'],
        orientation='h',
        marker=dict(
            color=top_pages['Clicks'],
            colorscale='Greens',
            showscale=True,
            colorbar=dict(title="Clicks")
        ),
        text=top_pages['Clicks'],
        textposition='outside',
        textfont=dict(color='#e5e7eb', size=10)
    ))
    
    fig_pages.update_layout(
        height=400,
        title="<b>Pages by Click Volume</b>",
        paper_bgcolor="rgba(255,255,255,0.02)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#e5e7eb", family="Inter"),
        margin=dict(l=150, r=40, t=50, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Clicks"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title=""),
        hovermode="y unified"
    )
    
    st.plotly_chart(fig_pages, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("### 🔥 Top 5 Pages")
    for idx, row in top_pages.head(5).iterrows():
        page_name = row['Page'].replace('https://', '').replace('http://', '')
        if not page_name or page_name == '/':
            page_name = "🏠 Home"
        
        st.markdown(f"""
        <div class="top-page-card">
            <span class="top-page-rank">#{idx+1}</span>
            <span class="top-page-url">{page_name[:50]}</span>
            <span class="top-page-clicks">👆 {row['Clicks']}</span>
            <span class="top-page-position">📍 {row['Position']}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("No page data found.")

# =========================
# KEYWORD WINNERS / LOSERS
# =========================
if len(site_data_list) == 1:
    st.markdown('<div class="section-title">Keyword Movement Analysis</div>', unsafe_allow_html=True)
    
    try:
        current_site_config = site_data_list[0].get("site_config", {})
        current_site_url = current_site_config.get("gsc_url", "")
        
        if current_site_url:
            previous_queries_df = get_gsc_queries(
                current_site_url,
                PREVIOUS_START_DATE,
                PREVIOUS_END_DATE
            )
            
            if not queries_df.empty and not previous_queries_df.empty:
                keyword_compare_df = queries_df.merge(
                    previous_queries_df[["Keyword", "Position"]],
                    on="Keyword",
                    how="inner",
                    suffixes=("_Current", "_Previous")
                )
                keyword_compare_df["Position Change"] = (
                    keyword_compare_df["Position_Previous"] - keyword_compare_df["Position_Current"]
                ).round(2)
                top_gainers_df = keyword_compare_df[
                    keyword_compare_df["Position Change"] > 0
                ].sort_values("Position Change", ascending=False).head(10)
                top_losers_df = keyword_compare_df[
                    keyword_compare_df["Position Change"] < 0
                ].sort_values("Position Change", ascending=True).head(10)
            else:
                keyword_compare_df = pd.DataFrame()
                top_gainers_df = pd.DataFrame()
                top_losers_df = pd.DataFrame()
            
            kw1, kw2 = st.columns(2)
            
            with kw1:
                st.markdown("""
                <div style="background: rgba(34, 197, 94, 0.05); border-radius: 12px; padding: 1rem; border: 1px solid rgba(34, 197, 94, 0.1); margin-bottom: 0.5rem;">
                    <h4 style="color: #22c55e; margin: 0; font-size: 0.9rem;">📈 Top Gainers</h4>
                </div>
                """, unsafe_allow_html=True)
                
                if not top_gainers_df.empty:
                    fig_gainers = go.Figure()
                    fig_gainers.add_trace(go.Bar(
                        x=top_gainers_df['Keyword'][:7],
                        y=top_gainers_df['Position Change'][:7],
                        marker_color='#22c55e',
                        text=top_gainers_df['Position Change'][:7],
                        textposition='outside',
                        textfont=dict(color='#22c55e', size=10)
                    ))
                    fig_gainers.update_layout(
                        height=250,
                        title="Position Improvements",
                        paper_bgcolor="rgba(255,255,255,0.02)",
                        plot_bgcolor="rgba(255,255,255,0.02)",
                        font=dict(color="#e5e7eb", size=10),
                        margin=dict(l=20, r=20, t=40, b=20),
                        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickangle=45),
                        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Position Change")
                    )
                    st.plotly_chart(fig_gainers, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info("No keyword gainers found.")
            
            with kw2:
                st.markdown("""
                <div style="background: rgba(239, 68, 68, 0.05); border-radius: 12px; padding: 1rem; border: 1px solid rgba(239, 68, 68, 0.1); margin-bottom: 0.5rem;">
                    <h4 style="color: #ef4444; margin: 0; font-size: 0.9rem;">📉 Top Losers</h4>
                </div>
                """, unsafe_allow_html=True)
                
                if not top_losers_df.empty:
                    fig_losers = go.Figure()
                    fig_losers.add_trace(go.Bar(
                        x=top_losers_df['Keyword'][:7],
                        y=top_losers_df['Position Change'][:7],
                        marker_color='#ef4444',
                        text=top_losers_df['Position Change'][:7],
                        textposition='outside',
                        textfont=dict(color='#ef4444', size=10)
                    ))
                    fig_losers.update_layout(
                        height=250,
                        title="Position Declines",
                        paper_bgcolor="rgba(255,255,255,0.02)",
                        plot_bgcolor="rgba(255,255,255,0.02)",
                        font=dict(color="#e5e7eb", size=10),
                        margin=dict(l=20, r=20, t=40, b=20),
                        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickangle=45),
                        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Position Change")
                    )
                    st.plotly_chart(fig_losers, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info("No keyword losers found.")
        else:
            st.warning("No site URL available for keyword comparison")
    except Exception as e:
        st.warning(f"Keyword comparison not available: {str(e)}")
else:
    if site_count > 1:
        st.info("📊 Keyword movement analysis is available for individual sites only")
    else:
        st.warning("No data available for keyword analysis")

# =========================
# OPPORTUNITY SECTION
# =========================
st.markdown('<div class="section-title">🎯 Opportunities</div>', unsafe_allow_html=True)

op1, op2 = st.columns(2)

with op1:
    st.markdown("""
    <div style="background: rgba(251, 146, 60, 0.05); border-radius: 12px; padding: 1rem; border: 1px solid rgba(251, 146, 60, 0.1); margin-bottom: 0.5rem;">
        <h4 style="color: #fb923c; margin: 0; font-size: 0.9rem;">💡 CTR Opportunities</h4>
    </div>
    """, unsafe_allow_html=True)

    if not queries_df.empty:
        ctr_opportunity_df = queries_df[
            (queries_df["Impressions"] >= 100) &
            (queries_df["CTR"] < 3)
        ].sort_values("Impressions", ascending=False).head(10)

        if not ctr_opportunity_df.empty:
            fig_ctr = go.Figure()
            fig_ctr.add_trace(go.Scatter(
                x=ctr_opportunity_df['Impressions'],
                y=ctr_opportunity_df['CTR'],
                mode='markers+text',
                marker=dict(
                    size=ctr_opportunity_df['Impressions']/10,
                    color=ctr_opportunity_df['CTR'],
                    colorscale='Oranges',
                    showscale=True,
                    colorbar=dict(title="CTR %")
                ),
                text=ctr_opportunity_df['Keyword'].apply(lambda x: x[:20]),
                textposition='top center',
                textfont=dict(color='#e5e7eb', size=9)
            ))
            fig_ctr.update_layout(
                height=300,
                title="CTR Opportunities by Impressions",
                paper_bgcolor="rgba(255,255,255,0.02)",
                plot_bgcolor="rgba(255,255,255,0.02)",
                font=dict(color="#e5e7eb", size=10),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Impressions"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="CTR %")
            )
            st.plotly_chart(fig_ctr, use_container_width=True, config={'displayModeBar': False})
        else:
            st.success("✅ No major CTR opportunity found.")
    else:
        st.warning("No query data available.")

with op2:
    st.markdown("""
    <div style="background: rgba(16, 185, 129, 0.05); border-radius: 12px; padding: 1rem; border: 1px solid rgba(16, 185, 129, 0.1); margin-bottom: 0.5rem;">
        <h4 style="color: #10b981; margin: 0; font-size: 0.9rem;">🎯 Low-Hanging Keywords</h4>
    </div>
    """, unsafe_allow_html=True)

    if not queries_df.empty:
        low_hanging_df = queries_df[
            (queries_df["Position"] >= 4) &
            (queries_df["Position"] <= 20) &
            (queries_df["Impressions"] >= 50)
        ].sort_values("Position", ascending=True).head(10)

        if not low_hanging_df.empty:
            fig_low = go.Figure()
            fig_low.add_trace(go.Scatter(
                x=low_hanging_df['Position'],
                y=low_hanging_df['Impressions'],
                mode='markers+text',
                marker=dict(
                    size=low_hanging_df['Impressions']/5,
                    color=low_hanging_df['Position'],
                    colorscale='Tealgrn',
                    showscale=True,
                    colorbar=dict(title="Position")
                ),
                text=low_hanging_df['Keyword'].apply(lambda x: x[:20]),
                textposition='top center',
                textfont=dict(color='#e5e7eb', size=9)
            ))
            fig_low.update_layout(
                height=300,
                title="Low-Hanging Keywords (Position 4-20)",
                paper_bgcolor="rgba(255,255,255,0.02)",
                plot_bgcolor="rgba(255,255,255,0.02)",
                font=dict(color="#e5e7eb", size=10),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Current Position", range=[0, 25]),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Impressions")
            )
            st.plotly_chart(fig_low, use_container_width=True, config={'displayModeBar': False})
        else:
            st.success("✅ No low-hanging keywords found.")
    else:
        st.warning("No keyword data available.")

# =========================
# AHREFS TABLES
# =========================
st.markdown('<div class="section-title">🔗 Ahrefs Intelligence</div>', unsafe_allow_html=True)

ah_left, ah_right = st.columns(2)

with ah_left:
    st.markdown("""
    <div style="background: rgba(249, 115, 22, 0.05); border-radius: 12px; padding: 0.75rem 1rem; border: 1px solid rgba(249, 115, 22, 0.1); margin-bottom: 0.5rem;">
        <h4 style="color: #f97316; margin: 0; font-size: 0.85rem;">🔑 Top Organic Keywords</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if not ahrefs_keywords_df.empty:
        keyword_col = 'keyword' if 'keyword' in ahrefs_keywords_df.columns else ahrefs_keywords_df.columns[0]
        volume_col = 'volume' if 'volume' in ahrefs_keywords_df.columns else None
        position_col = 'best_position' if 'best_position' in ahrefs_keywords_df.columns else None
        
        for idx, row in ahrefs_keywords_df.head(10).iterrows():
            keyword = str(row.get(keyword_col, 'N/A'))
            volume = row.get(volume_col, 0) if volume_col else 0
            position = row.get(position_col, 'N/A') if position_col else 'N/A'
            st.markdown(f"""
            <div class="top-page-card">
                <span class="top-page-rank">#{idx+1}</span>
                <span class="top-page-url">{keyword[:30]}</span>
                <span style="color: #facc15; font-weight: 600; font-size: 0.8rem; min-width: 60px;">📊 {volume}</span>
                <span style="color: #34d399; font-weight: 600; font-size: 0.8rem; min-width: 50px;">📍 {position}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        if AHREFS_API_KEY:
            st.info("No Ahrefs organic keyword data returned. Check API permissions.")
        else:
            st.info("Ahrefs API key not configured.")

with ah_right:
    st.markdown("""
    <div style="background: rgba(99, 102, 241, 0.05); border-radius: 12px; padding: 0.75rem 1rem; border: 1px solid rgba(99, 102, 241, 0.1); margin-bottom: 0.5rem;">
        <h4 style="color: #6366f1; margin: 0; font-size: 0.85rem;">🔗 Top Backlinks</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if not ahrefs_backlinks_df.empty:
        url_col = 'url_from' if 'url_from' in ahrefs_backlinks_df.columns else ahrefs_backlinks_df.columns[0]
        
        for idx, row in ahrefs_backlinks_df.head(10).iterrows():
            url_from = str(row.get(url_col, 'N/A'))
            if isinstance(url_from, str):
                domain = url_from.replace('https://', '').replace('http://', '').split('/')[0][:30]
            else:
                domain = 'N/A'
            st.markdown(f"""
            <div class="top-page-card">
                <span class="top-page-rank">#{idx+1}</span>
                <span class="top-page-url">{domain}</span>
                <span style="color: #34d399; font-weight: 600; font-size: 0.8rem;">🔗</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        if AHREFS_API_KEY:
            st.info("No Ahrefs backlink data returned. Check API permissions.")
        else:
            st.info("Ahrefs API key not configured.")

# =========================
# DOWNLOAD SECTION
# =========================
st.markdown('<div class="section-title">📥 Data Export</div>', unsafe_allow_html=True)

st.markdown("""
<div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 1.5rem; margin: 1rem 0;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
            <h4 style="margin: 0; color: #e5e7eb;">Export Reports</h4>
            <p style="color: #94a3b8; margin: 0.25rem 0 0 0; font-size: 0.85rem;">Download your data as beautifully formatted HTML reports</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# GSC Data Downloads
st.markdown("""
<div style="display: flex; align-items: center; gap: 0.75rem; margin: 1.5rem 0 1rem 0;">
    <span style="font-size: 1.2rem;">📊</span>
    <span style="color: #e5e7eb; font-weight: 700; font-size: 1rem;">Google Search Console</span>
</div>
""", unsafe_allow_html=True)

gsc_col1, gsc_col2, gsc_col3, gsc_col4 = st.columns(4)

with gsc_col1:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if not gsc_df.empty:
            href, filename = create_html_download(gsc_df, "Google Search Console - Daily Performance", "gsc_daily")
            if href:
                st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-gsc">📊 Daily Data</button></a>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="warning-text">Could not create download</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warning-text">No GSC data available</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with gsc_col2:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if not queries_df.empty:
            href, filename = create_html_download(queries_df, "Google Search Console - All Queries", "gsc_queries")
            if href:
                st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-gsc">🔍 All Queries</button></a>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="warning-text">Could not create download</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warning-text">No query data available</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with gsc_col3:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if not pages_df.empty:
            href, filename = create_html_download(pages_df, "Google Search Console - Top Pages", "gsc_pages")
            if href:
                st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-gsc">📄 Pages</button></a>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="warning-text">Could not create download</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warning-text">No page data available</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with gsc_col4:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if not queries_df.empty:
            query_summary = queries_df.copy()
            query_summary['Category'] = 'All Sites'
            href, filename = create_html_download(query_summary, "Google Search Console - Query Summary", "gsc_query_summary")
            if href:
                st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-gsc">📊 Query Summary</button></a>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="warning-text">Could not create download</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warning-text">No query data available</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# AHREFS DATA DOWNLOADS
st.markdown("""
<div style="display: flex; align-items: center; gap: 0.75rem; margin: 2rem 0 1rem 0;">
    <span style="font-size: 1.2rem;">🔗</span>
    <span style="color: #e5e7eb; font-weight: 700; font-size: 1rem;">Ahrefs</span>
</div>
""", unsafe_allow_html=True)

ahrefs_col1, ahrefs_col2, ahrefs_col3, ahrefs_col4 = st.columns(4)

# Column 1 - Keywords
with ahrefs_col1:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if not ahrefs_keywords_df.empty:
            href, filename = create_html_download(ahrefs_keywords_df, "Ahrefs - All Organic Keywords", "ahrefs_keywords")
            if href:
                st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-ahrefs">🔑 All Keywords</button></a>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="warning-text">Could not create download</p>', unsafe_allow_html=True)
        else:
            dummy_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 40px; background: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
                    h1 {{ color: #1a1a2e; border-bottom: 3px solid #ff6b6b; padding-bottom: 10px; }}
                    .warning {{ color: #ff6b6b; font-weight: bold; font-size: 18px; }}
                    .info {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ff6b6b; }}
                    ul {{ line-height: 1.8; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔑 Ahrefs Keywords Report</h1>
                    <p class="warning">⚠️ No Ahrefs keyword data available</p>
                    <div class="info">
                        <p><strong>📅 Date:</strong> {date.today().strftime('%Y-%m-%d')}</p>
                        <p><strong>🌐 Site:</strong> {selected_site if selected_site else 'All Sites'}</p>
                        <p><strong>📊 Status:</strong> No data available</p>
                    </div>
                    <h3>Possible Reasons:</h3>
                    <ul>
                        <li>⚠️ Ahrefs API quota exhausted (0 units left)</li>
                        <li>🔑 Ahrefs API key not configured in secrets</li>
                        <li>🔍 No organic keywords found for this domain</li>
                        <li>📡 API connection error</li>
                    </ul>
                    <p style="margin-top: 30px; color: #666; font-size: 12px;">Generated by Juan365 SEO Dashboard</p>
                </div>
            </body>
            </html>
            """
            dummy_b64 = base64.b64encode(dummy_html.encode()).decode()
            dummy_href = f'data:text/html;base64,{dummy_b64}'
            site_name = selected_site if selected_site else "all_sites"
            dummy_filename = f"ahrefs_keywords_no_data_{site_name}_{date.today().strftime('%Y%m%d')}.html"
            
            st.markdown(f'''
            <div style="text-align: center;">
                <a href="{dummy_href}" download="{dummy_filename}" target="_blank">
                    <button class="download-btn" style="width: 100%; padding: 0.75rem; border-radius: 10px; border: none; color: white; background: linear-gradient(135deg, #4a5568, #2d3748); font-weight: 700; font-size: 0.85rem; cursor: pointer; transition: all 0.3s ease;">
                        📄 No Keywords Available
                    </button>
                </a>
                <p style="color: #94a3b8; font-size: 0.7rem; margin-top: 0.3rem;">
                    {'⚠️ Ahrefs API quota exhausted' if AHREFS_API_KEY else '🔑 Add AHREFS_API_KEY to secrets'}
                </p>
            </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Column 2 - Backlinks
with ahrefs_col2:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if not ahrefs_backlinks_df.empty:
            href, filename = create_html_download(ahrefs_backlinks_df, "Ahrefs - Backlinks", "ahrefs_backlinks")
            if href:
                st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-ahrefs">🔗 Backlinks</button></a>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="warning-text">Could not create download</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warning-text">No backlink data available</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Column 3 - Referring Domains
with ahrefs_col3:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if not ahrefs_refdomains_df.empty:
            href, filename = create_html_download(ahrefs_refdomains_df, "Ahrefs - Referring Domains", "ahrefs_refdomains")
            if href:
                st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-ahrefs">🌐 Ref Domains</button></a>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="warning-text">Could not create download</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warning-text">No referring domain data available</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Column 4 - Metrics Summary
with ahrefs_col4:
    with st.container():
        st.markdown('<div class="download-container">', unsafe_allow_html=True)
        if ahrefs_dr_data:
            metrics_summary = pd.DataFrame([{
                'Domain Rating': ahrefs_domain_rating,
                'Ahrefs Rank': ahrefs_rank,
                'Referring Domains': ahrefs_refdomains,
                'Backlinks': ahrefs_backlinks_count,
                'Organic Keywords': unique_ahrefs_keywords
            }])
            href, filename = create_html_download(metrics_summary, "Ahrefs - Metrics Summary", "ahrefs_metrics")
            if href:
                st.markdown(f'<a href="{href}" download="{filename}" target="_blank"><button class="download-btn download-btn-ahrefs">📊 Metrics Summary</button></a>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="warning-text">Could not create download</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warning-text">No metrics data available</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# WEEKLY SEO REPORT PDF
# =========================
st.markdown('<div class="section-title">📄 Weekly Report</div>', unsafe_allow_html=True)

col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
with col_pdf2:
    pdf_report = generate_pdf_report()
    st.download_button(
        label="📄 Download SEO Report PDF",
        data=pdf_report,
        file_name=f"{selected_site if selected_site else 'all_sites'}-weekly-seo-report.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# =========================
# SCORECARDS
# =========================
st.markdown('<div class="section-title">Performance Scorecard</div>', unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #8b5cf6;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em;">GSC Visibility</div>
                <div style="font-size: 2rem; font-weight: 800; color: #ffffff; margin: 0.5rem 0;">{total_impressions:,}</div>
            </div>
            <div style="font-size: 1.5rem; opacity: 0.3;">👁️</div>
        </div>
        <div style="display: flex; justify-content: space-between; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.06);">
            <div><span style="color: #94a3b8; font-size: 0.75rem;">CTR</span> <span style="color: #facc15; font-weight: 600; margin-left: 0.5rem;">{avg_ctr}%</span></div>
            <div><span style="color: #94a3b8; font-size: 0.75rem;">Position</span> <span style="color: #34d399; font-weight: 600; margin-left: 0.5rem;">{avg_position}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with s2:
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #3b82f6;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em;">GA4 Traffic</div>
                <div style="font-size: 2rem; font-weight: 800; color: #ffffff; margin: 0.5rem 0;">{ga4_data['sessions']:,}</div>
            </div>
            <div style="font-size: 1.5rem; opacity: 0.3;">🌐</div>
        </div>
        <div style="display: flex; justify-content: space-between; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.06);">
            <div><span style="color: #94a3b8; font-size: 0.75rem;">Users</span> <span style="color: #facc15; font-weight: 600; margin-left: 0.5rem;">{ga4_data['active_users']:,}</span></div>
            <div><span style="color: #94a3b8; font-size: 0.75rem;">Pageviews</span> <span style="color: #34d399; font-weight: 600; margin-left: 0.5rem;">{ga4_data['pageviews']:,}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with s3:
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #f59e0b;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em;">Keyword Demand</div>
                <div style="font-size: 2rem; font-weight: 800; color: #ffffff; margin: 0.5rem 0;">{unique_queries:,}</div>
            </div>
            <div style="font-size: 1.5rem; opacity: 0.3;">🔍</div>
        </div>
        <div style="display: flex; justify-content: space-between; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.06);">
            <div><span style="color: #94a3b8; font-size: 0.75rem;">Clicks</span> <span style="color: #facc15; font-weight: 600; margin-left: 0.5rem;">{total_clicks:,}</span></div>
            <div><span style="color: #94a3b8; font-size: 0.75rem;">Rank</span> <span style="color: #34d399; font-weight: 600; margin-left: 0.5rem;">{rank_position}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with s4:
    profit_color = "#22c55e" if latest_profit_loss >= 0 else "#ef4444"
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #22c55e;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em;">Latest Performance</div>
                <div style="font-size: 2rem; font-weight: 800; color: #ffffff; margin: 0.5rem 0;">{latest_registrations:,}</div>
            </div>
            <div style="font-size: 1.5rem; opacity: 0.3;">📊</div>
        </div>
        <div style="display: flex; justify-content: space-between; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.06);">
            <div><span style="color: #94a3b8; font-size: 0.75rem;">FTD</span> <span style="color: #facc15; font-weight: 600; margin-left: 0.5rem;">{latest_ftd:,}</span></div>
            <div><span style="color: #94a3b8; font-size: 0.75rem;">P/L</span> <span style="color: {profit_color}; font-weight: 600; margin-left: 0.5rem;">₱{latest_profit_loss:,.2f}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# HIDDEN DATA TABLES
# =========================
with st.expander("📊 View Raw Data Tables (Hidden by Default)", expanded=False):
    st.markdown("### Daily GSC Data")
    if not gsc_df.empty:
        st.dataframe(gsc_df, use_container_width=True)
    else:
        st.warning("No daily GSC data found.")
    
    st.markdown("### All GSC Queries")
    if not queries_df.empty:
        st.dataframe(queries_df, use_container_width=True)
    else:
        st.warning("No query data found.")
    
    st.markdown("### Top Pages")
    if not pages_df.empty:
        st.dataframe(pages_df, use_container_width=True)
    else:
        st.warning("No page data found.")
    
    st.markdown("### All Ahrefs Keywords")
    if not ahrefs_keywords_df.empty:
        st.dataframe(ahrefs_keywords_df, use_container_width=True)
    else:
        st.warning("No Ahrefs keyword data found.")
    
    st.markdown("### Ahrefs Backlinks")
    if not ahrefs_backlinks_df.empty:
        st.dataframe(ahrefs_backlinks_df.head(50), use_container_width=True)
    else:
        st.warning("No Ahrefs backlink data found.")
    
    st.markdown("### Ahrefs Referring Domains")
    if not ahrefs_refdomains_df.empty:
        st.dataframe(ahrefs_refdomains_df.head(50), use_container_width=True)
    else:
        st.warning("No Ahrefs referring domain data found.")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Built with Streamlit • Juan365 SEO Dashboard")
