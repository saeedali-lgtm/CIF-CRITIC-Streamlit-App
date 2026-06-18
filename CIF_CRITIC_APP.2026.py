import os

# Prefer a light Streamlit theme when the app is launched.
os.environ.setdefault("STREAMLIT_THEME_BASE", "light")
os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

import html
import re
import sys
from io import BytesIO
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False


PORT = 8803
SERVER_ADDRESS = "0.0.0.0"
DISPLAY_URL = "http://192.168.0.100:8803/"  # Change this if your local IP is different.

PERSIAN_ARABIC_TEXT_PATTERN = re.compile(r"[؀-ۿ]")


# -----------------------------------------------------------------------------
# Display helpers
# -----------------------------------------------------------------------------

def display_criterion_label(value) -> str:
    """Return a clean English-safe label for charts/cards while preserving raw labels in calculations."""
    text = str(value).strip()
    if not PERSIAN_ARABIC_TEXT_PATTERN.search(text):
        return text
    parts = re.split(r"\s*[-–—|:]\s*", text, maxsplit=1)
    if parts and parts[0].strip() and not PERSIAN_ARABIC_TEXT_PATTERN.search(parts[0]):
        return parts[0].strip()
    latin_only = re.sub(r"[؀-ۿ‌‏‪-‮]+", "", text)
    latin_only = re.sub(r"\s+", " ", latin_only).strip(" -–—|:")
    return latin_only if latin_only else "Criterion"


def display_criterion_labels(values) -> List[str]:
    return [display_criterion_label(v) for v in values]


# -----------------------------------------------------------------------------
# Styling copied from the CIF-DEMATEL interface so the CRITIC tool has the same UI shell.
# -----------------------------------------------------------------------------

def apply_custom_style():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

        :root {
            /* User-selected palette: true soft emerald green + deep royal blue. */
            --cif-emerald: #2FA66A;
            --cif-emerald-dark: #247A50;
            --cif-forest: #164A34;
            --cif-lapis: #123B2A;
            --cif-ink: #102B20;
            --cif-text: #102018;
            --cif-muted: #496356;
            --cif-cream: #FBFFFC;
            --cif-card: rgba(255, 255, 255, 0.94);
            --cif-border: rgba(39, 138, 89, 0.20);
            --cif-gold: #C5962D;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 7%, rgba(47, 166, 106, 0.22), transparent 26%),
                radial-gradient(circle at 92% 10%, rgba(47, 166, 106, 0.20), transparent 28%),
                radial-gradient(circle at 76% 92%, rgba(197, 150, 45, 0.11), transparent 28%),
                linear-gradient(145deg, #FBFFFC 0%, #F6FFF9 32%, #F1FFF6 68%, #ffffff 100%);
            color: var(--cif-text);
        }

        .block-container {
            padding-top: 1.45rem;
            padding-bottom: 2rem;
            max-width: 1480px;
        }

        /* General readable text: fixes white/low-contrast native Streamlit headings and labels. */
        h1, h2, h3, h4, h5, h6,
        .stMarkdown, .stMarkdown p, .stMarkdown li,
        .stCaptionContainer, .stText, label,
        div[data-testid="stWidgetLabel"], div[data-testid="stWidgetLabel"] p,
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li,
        div[data-testid="stMetricLabel"], div[data-testid="stMetricDelta"],
        .caption-note, .muted {
            color: var(--cif-text) !important;
        }

        h1, h2, h3, h4 {
            color: var(--cif-ink) !important;
            letter-spacing: 0.15px;
        }

        p, li, td, th, span {
            text-rendering: optimizeLegibility;
        }

        /* Streamlit's native sidebar toggle is turned into a cleaner hamburger-style control. */
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapseButton"] {
            border-radius: 18px !important;
            background: linear-gradient(135deg, var(--cif-emerald-dark), var(--cif-emerald) 42%, var(--cif-forest)) !important;
            box-shadow: 0 18px 38px rgba(39, 138, 89, 0.24), 0 2px 0 rgba(255,255,255,0.34) inset !important;
            border: 1px solid rgba(255, 255, 255, 0.72) !important;
        }

        [data-testid="collapsedControl"] button,
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stSidebarCollapseButton"] svg {
            color: #ffffff !important;
            stroke-width: 2.8px !important;
        }

        .hamburger-shell {
            position: sticky;
            top: 0.75rem;
            z-index: 999;
            max-width: 430px;
            margin: 0 0 16px auto;
            border-radius: 22px;
            background:
                radial-gradient(circle at 10% 10%, rgba(255,255,255,0.45), transparent 28%),
                linear-gradient(135deg, var(--cif-emerald-dark) 0%, var(--cif-emerald) 42%, var(--cif-forest) 100%);
            border: 1px solid rgba(255, 255, 255, 0.62);
            box-shadow: 0 22px 46px rgba(39, 138, 89, 0.22), 0 4px 0 rgba(255,255,255,0.25) inset;
            backdrop-filter: blur(16px);
            overflow: hidden;
        }

        .hamburger-shell summary {
            list-style: none;
            cursor: pointer;
            user-select: none;
            padding: 13px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .hamburger-shell summary::-webkit-details-marker { display: none; }

        .hamburger-icon {
            width: 42px;
            height: 42px;
            display: inline-flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 5px;
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.20);
            box-shadow: 0 9px 20px rgba(7, 22, 63, 0.16), 0 2px 0 rgba(255,255,255,0.28) inset;
            transition: all 0.25s ease;
        }

        .hamburger-icon span {
            width: 20px;
            height: 2.5px;
            border-radius: 999px;
            background: #ffffff;
            box-shadow: 0 1px 4px rgba(7,22,63,0.18);
            transition: all 0.25s ease;
        }

        .hamburger-shell[open] .hamburger-icon span:nth-child(1) { transform: translateY(7.5px) rotate(45deg); }
        .hamburger-shell[open] .hamburger-icon span:nth-child(2) { opacity: 0; transform: scaleX(0.2); }
        .hamburger-shell[open] .hamburger-icon span:nth-child(3) { transform: translateY(-7.5px) rotate(-45deg); }

        .hamburger-title {
            color: #ffffff !important;
            font-size: 15px;
            font-weight: 950;
            letter-spacing: 0.4px;
            text-shadow: 0 2px 8px rgba(7, 22, 63, 0.28);
        }

        .hamburger-pill {
            margin-left: auto;
            padding: 7px 10px;
            border-radius: 999px;
            color: #ffffff !important;
            background: rgba(255,255,255,0.17);
            border: 1px solid rgba(255,255,255,0.30);
            font-size: 11px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.9px;
        }

        .hamburger-links {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 9px;
            padding: 0 14px 14px 14px;
        }

        .hamburger-links a {
            text-decoration: none !important;
            color: var(--cif-ink) !important;
            font-size: 13px;
            font-weight: 900;
            padding: 10px 12px;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid rgba(255,255,255,0.70);
            box-shadow: 0 8px 18px rgba(7,22,63,0.11);
            transition: all 0.22s ease;
        }

        .hamburger-links a:hover {
            transform: translateY(-2px);
            color: var(--cif-emerald-dark) !important;
            background: #ffffff;
            box-shadow: 0 12px 24px rgba(7,22,63,0.15);
        }

        @media (max-width: 760px) {
            .hamburger-shell {
                margin-left: 0;
                max-width: 100%;
            }
            .hamburger-links { grid-template-columns: 1fr; }
            .hero-title { font-size: 34px !important; }
        }

        .hero-card {
            position: relative;
            overflow: hidden;
            border-radius: 30px;
            padding: 34px 34px 28px 34px;
            margin-bottom: 20px;
            background:
                radial-gradient(circle at 8% 10%, rgba(255,255,255,0.78), transparent 25%),
                radial-gradient(circle at 92% 16%, rgba(47,166,106,0.22), transparent 30%),
                linear-gradient(135deg, #ffffff 0%, #F4FFF8 34%, #D6F5E2 72%, #FFF9EF 100%);
            border: 1px solid rgba(39, 138, 89, 0.22);
            box-shadow:
                0 30px 72px rgba(39, 138, 89, 0.16),
                0 10px 24px rgba(255, 255, 255, 0.94) inset,
                0 -14px 28px rgba(18, 74, 52, 0.07) inset;
        }

        .hero-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(120deg, transparent 0%, rgba(255,255,255,0.72) 38%, transparent 74%);
            transform: translateX(-100%);
            animation: shine 7s linear infinite;
            pointer-events: none;
        }

        @keyframes shine { 100% { transform: translateX(160%); } }

        .hero-topline {
            display: inline-block;
            padding: 8px 14px;
            border-radius: 999px;
            background: rgba(47, 166, 106, 0.13);
            border: 1px solid rgba(39, 138, 89, 0.25);
            color: var(--cif-emerald-dark) !important;
            font-size: 12px;
            font-weight: 900;
            letter-spacing: 1.35px;
            text-transform: uppercase;
            margin-bottom: 16px;
            box-shadow: 0 8px 20px rgba(39, 138, 89, 0.10), 0 2px 0 rgba(255,255,255,0.90) inset;
        }

        .hero-title {
            font-size: 46px;
            font-weight: 900;
            line-height: 1.05;
            margin: 0 0 10px 0;
            color: var(--cif-ink) !important;
            text-shadow: 0 2px 0 rgba(255,255,255,0.84);
        }

        .hero-subtitle {
            font-size: 16px;
            line-height: 1.72;
            color: var(--cif-lapis) !important;
            max-width: 1040px;
            margin-bottom: 0;
            font-weight: 550;
        }

        .three-d-divider {
            height: 10px;
            margin: 4px 0 18px 0;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(47,166,106,0.05), rgba(47,166,106,0.54), rgba(18,74,52,0.36), rgba(197,150,45,0.22), rgba(47,166,106,0.05));
            box-shadow: 0 10px 20px rgba(39,138,89,0.11), 0 2px 0 rgba(255,255,255,0.86) inset;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 16px;
            margin-bottom: 18px;
        }

        .mini-card, .glass-panel, .table-card, .brand-card, .sidebar-block {
            position: relative;
            overflow: hidden;
            border-radius: 22px;
            background:
                linear-gradient(145deg, rgba(255,255,255,0.97), rgba(246,255,249,0.88));
            border: 1px solid var(--cif-border);
            box-shadow: 0 18px 44px rgba(39, 138, 89, 0.11), 0 3px 0 rgba(255,255,255,0.95) inset;
            backdrop-filter: blur(12px);
        }

        .mini-card { padding: 18px 18px 16px 18px; }
        .glass-panel { padding: 20px 22px; margin-bottom: 18px; }
        .table-card { padding: 13px 15px 17px 15px; margin-bottom: 18px; }
        .brand-card { padding: 16px 18px; margin-bottom: 18px; }
        .sidebar-block { padding: 14px 16px; margin-bottom: 15px; }

        .mini-card:hover, .glass-panel:hover, .table-card:hover, .brand-card:hover, .sidebar-block:hover {
            transform: translateY(-3px) rotateX(0.8deg);
            box-shadow: 0 26px 58px rgba(39, 138, 89, 0.17), 0 3px 0 rgba(255,255,255,0.95) inset;
        }

        .mini-card h4, .sidebar-block h4 {
            font-size: 14px;
            color: var(--cif-emerald-dark) !important;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }

        .mini-card p, .mini-card li, .sidebar-block p, .sidebar-block li, .caption-note, .muted {
            color: var(--cif-muted) !important;
            font-size: 14px;
            line-height: 1.74;
            margin-bottom: 0;
        }

        .mini-card strong, .brand-card strong, .sidebar-block strong {
            color: var(--cif-lapis) !important;
        }

        .developer-card {
            background:
                radial-gradient(circle at 9% 12%, rgba(255,255,255,0.72), transparent 30%),
                linear-gradient(135deg, #FFF7DD 0%, #EEF9E7 42%, #DDF4E5 100%) !important;
            border: 1px solid rgba(197, 150, 45, 0.34) !important;
            box-shadow:
                0 22px 52px rgba(128, 95, 24, 0.13),
                0 8px 24px rgba(47, 166, 106, 0.11),
                0 3px 0 rgba(255,255,255,0.96) inset !important;
        }

        .developer-card::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 7px;
            background: linear-gradient(180deg, #C5962D 0%, #2FA66A 54%, #1F6F49 100%);
            box-shadow: 6px 0 18px rgba(197, 150, 45, 0.18);
        }

        .developer-card h4 {
            color: #7A5814 !important;
        }

        .developer-card strong {
            color: #1F6F49 !important;
            font-weight: 950 !important;
        }

        .developer-card p,
        .developer-card li {
            color: #3F513B !important;
        }

        .section-label {
            display: inline-block;
            margin-bottom: 12px;
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(47, 166, 106, 0.13);
            color: var(--cif-emerald-dark) !important;
            border: 1px solid rgba(39, 138, 89, 0.22);
            font-size: 12px;
            font-weight: 900;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        section[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 12% 5%, rgba(47,166,106,0.12), transparent 28%),
                linear-gradient(180deg, #ffffff 0%, #F6FFF9 48%, #F1FFF6 100%);
            border-right: 1px solid rgba(39, 138, 89, 0.16);
            box-shadow: 14px 0 36px rgba(39, 138, 89, 0.08);
        }

        section[data-testid="stSidebar"] * {
            color: var(--cif-text) !important;
        }

        .brand-card .name {
            color: var(--cif-lapis) !important;
            font-size: 20px;
            font-weight: 900;
            margin-top: 6px;
            margin-bottom: 8px;
        }

        div[data-testid="metric-container"] {
            background: linear-gradient(145deg, rgba(255,255,255,0.97), rgba(234,251,241,0.92));
            border: 1px solid rgba(39, 138, 89, 0.20);
            border-radius: 18px;
            padding: 15px;
            box-shadow: 0 14px 32px rgba(39, 138, 89, 0.12), 0 2px 0 rgba(255,255,255,0.95) inset;
        }

        div[data-testid="stMetricValue"] { color: var(--cif-emerald-dark) !important; font-weight: 900; }
        div[data-testid="stMetricLabel"] { color: var(--cif-lapis) !important; font-weight: 800; }

        div[data-testid="stDataFrame"] {
            background: rgba(255,255,255,0.92);
            border: 1px solid rgba(39, 138, 89, 0.16);
            border-radius: 18px;
            box-shadow: 0 16px 38px rgba(39, 138, 89, 0.10);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(47, 166, 106, 0.08);
            padding: 8px;
            border-radius: 18px;
            border: 1px solid rgba(39, 138, 89, 0.12);
            box-shadow: 0 8px 18px rgba(39, 138, 89, 0.07) inset;
        }

        .stTabs [data-baseweb="tab"] {
            height: 42px;
            border-radius: 12px;
            background: rgba(255,255,255,0.92);
            color: var(--cif-lapis) !important;
            font-weight: 900;
            padding: 0 18px;
            box-shadow: 0 6px 16px rgba(39, 138, 89, 0.08);
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--cif-emerald-dark) 0%, var(--cif-emerald) 42%, var(--cif-forest) 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 10px 28px rgba(39, 138, 89, 0.24), 0 2px 0 rgba(255,255,255,0.30) inset;
        }

        .stTabs [aria-selected="true"] p,
        .stTabs [aria-selected="true"] span,
        .stButton > button *, .stDownloadButton > button * {
            color: #ffffff !important;
        }

        .stButton > button, .stDownloadButton > button {
            background: linear-gradient(135deg, var(--cif-emerald-dark) 0%, var(--cif-emerald) 42%, var(--cif-forest) 100%);
            color: #ffffff !important;
            border: 1px solid rgba(255,255,255,0.62);
            border-radius: 16px;
            font-weight: 900;
            padding: 0.78rem 1.15rem;
            box-shadow: 0 16px 30px rgba(39, 138, 89, 0.22), 0 3px 0 rgba(255,255,255,0.34) inset;
            transition: all 0.25s ease;
        }

        .stButton > button:hover, .stDownloadButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 20px 40px rgba(39, 138, 89, 0.30), 0 3px 0 rgba(255,255,255,0.34) inset;
        }

        .upload-zone-card {
            position: relative;
            overflow: hidden;
            margin: 8px 0 14px 0;
            padding: 22px 24px;
            border-radius: 26px;
            background:
                radial-gradient(circle at 8% 16%, rgba(255,255,255,0.78), transparent 26%),
                linear-gradient(135deg, #ffffff 0%, #E5F8EE 42%, #D6F5E2 100%);
            border: 1px solid rgba(39,138,89,0.28);
            box-shadow: 0 24px 46px rgba(39, 138, 89, 0.16), 0 5px 0 rgba(255,255,255,0.88) inset;
        }

        .upload-zone-card h3 {
            color: var(--cif-ink) !important;
            font-size: 23px;
            font-weight: 900;
            margin: 0 0 7px 0;
            text-shadow: 0 2px 0 rgba(255,255,255,0.75);
        }

        .upload-zone-card p {
            color: var(--cif-lapis) !important;
            font-size: 14px;
            line-height: 1.65;
            margin: 0;
            font-weight: 650;
        }

        .upload-zone-badge {
            display: inline-block;
            margin-bottom: 10px;
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(255,255,255,0.72);
            color: var(--cif-emerald-dark) !important;
            border: 1px solid rgba(255,255,255,0.82);
            font-size: 12px;
            font-weight: 900;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .stFileUploader, div[data-testid="stFileUploader"] {
            background: linear-gradient(145deg, rgba(255,255,255,0.97), rgba(214,245,226,0.82));
            border: 2px dashed rgba(39, 138, 89, 0.58);
            padding: 14px;
            border-radius: 22px;
            box-shadow: 0 18px 36px rgba(39, 138, 89, 0.14), 0 10px 26px rgba(18, 74, 52, 0.07) inset;
        }

        .footer-note {
            margin-top: 28px;
            color: var(--cif-muted) !important;
            font-size: 13px;
            text-align: center;
            opacity: 0.95;
        }

        code {
            color: var(--cif-lapis) !important;
            background: rgba(47, 166, 106, 0.10) !important;
            border-radius: 8px;
            padding: 2px 5px;
        }


        /* ------------------------------------------------------------------
           Strong green soft emerald green override requested by user.
           Main visible color = #2FA66A; soft emerald, not neon and not blue/violet.
        ------------------------------------------------------------------ */
        :root {
            --cif-emerald: #2FA66A;
            --cif-emerald-dark: #1F6F49;
            --cif-emerald-deep: #164A34;
            --cif-emerald-soft: #EAFBF1;
            --cif-emerald-card: #F6FFF9;
            --cif-ink: #123B2A;
            --cif-text: #11251B;
            --cif-muted: #496356;
            --cif-border: rgba(47, 166, 106, 0.34);
            --cif-gold: #C5962D;
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 8%, rgba(47,166,106,0.34), transparent 27%),
                radial-gradient(circle at 92% 8%, rgba(31,111,73,0.22), transparent 30%),
                radial-gradient(circle at 78% 92%, rgba(47,166,106,0.20), transparent 32%),
                linear-gradient(145deg, #FAFFFC 0%, #EAFBF1 38%, #F6FFF9 70%, #FFFFFF 100%) !important;
            color: var(--cif-text) !important;
        }

        .hero-card {
            background:
                radial-gradient(circle at 10% 8%, rgba(255,255,255,0.40), transparent 28%),
                linear-gradient(135deg, #2FA66A 0%, #278A59 48%, #1F6F49 100%) !important;
            border: 1px solid rgba(255,255,255,0.58) !important;
            box-shadow: 0 32px 76px rgba(31, 111, 73, 0.28), 0 8px 0 rgba(255,255,255,0.18) inset !important;
        }

        .hero-title,
        .hero-subtitle,
        .hero-topline {
            color: #ffffff !important;
            text-shadow: 0 2px 12px rgba(18, 59, 42, 0.32) !important;
        }

        .hero-topline {
            background: rgba(255,255,255,0.18) !important;
            border: 1px solid rgba(255,255,255,0.38) !important;
            box-shadow: 0 8px 22px rgba(18,74,52,0.18), 0 2px 0 rgba(255,255,255,0.18) inset !important;
        }

        .mini-card, .glass-panel, .table-card, .brand-card, .sidebar-block,
        div[data-testid="metric-container"] {
            background: linear-gradient(145deg, #ffffff 0%, #F6FFF9 58%, #EAFBF1 100%) !important;
            border: 1px solid rgba(47, 166, 106, 0.34) !important;
            box-shadow: 0 18px 44px rgba(31, 111, 73, 0.13), 0 3px 0 rgba(255,255,255,0.96) inset !important;
        }

        .developer-card {
            background:
                radial-gradient(circle at 9% 12%, rgba(255,255,255,0.72), transparent 30%),
                linear-gradient(135deg, #FFF7DD 0%, #EEF9E7 42%, #DDF4E5 100%) !important;
            border: 1px solid rgba(197, 150, 45, 0.36) !important;
            box-shadow:
                0 22px 52px rgba(128, 95, 24, 0.13),
                0 8px 24px rgba(47, 166, 106, 0.11),
                0 3px 0 rgba(255,255,255,0.96) inset !important;
        }

        .developer-card::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 7px;
            background: linear-gradient(180deg, #C5962D 0%, #2FA66A 54%, #1F6F49 100%);
            box-shadow: 6px 0 18px rgba(197, 150, 45, 0.18);
        }

        .developer-card h4 {
            color: #7A5814 !important;
        }

        .developer-card strong {
            color: #1F6F49 !important;
            font-weight: 950 !important;
        }

        .developer-card p,
        .developer-card li {
            color: #3F513B !important;
        }

        h1, h2, h3, h4, h5, h6,
        .mini-card h4, .sidebar-block h4,
        .brand-card .name,
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricLabel"] {
            color: #123B2A !important;
        }

        .section-label,
        .upload-zone-badge {
            color: #123B2A !important;
            background: rgba(47, 166, 106, 0.18) !important;
            border-color: rgba(47, 166, 106, 0.40) !important;
        }

        .hamburger-shell,
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        .stTabs [aria-selected="true"],
        .stButton > button,
        .stDownloadButton > button {
            background: linear-gradient(135deg, #2FA66A 0%, #278A59 52%, #1F6F49 100%) !important;
            color: #ffffff !important;
            border-color: rgba(255,255,255,0.62) !important;
            box-shadow: 0 16px 34px rgba(31, 111, 73, 0.27), 0 3px 0 rgba(255,255,255,0.25) inset !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            background: rgba(47,166,106,0.13) !important;
            border-color: rgba(47,166,106,0.24) !important;
        }

        .stTabs [data-baseweb="tab"] {
            background: rgba(255,255,255,0.96) !important;
            color: #123B2A !important;
            border: 1px solid rgba(47,166,106,0.18) !important;
        }

        .stTabs [aria-selected="true"] p,
        .stTabs [aria-selected="true"] span,
        .stButton > button *,
        .stDownloadButton > button *,
        .hamburger-title,
        .hamburger-pill {
            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 16% 4%, rgba(47,166,106,0.23), transparent 30%),
                linear-gradient(180deg, #ffffff 0%, #F6FFF9 44%, #EAFBF1 100%) !important;
            border-right: 1px solid rgba(47,166,106,0.26) !important;
            box-shadow: 14px 0 36px rgba(31, 111, 73, 0.10) !important;
        }

        .upload-zone-card {
            background:
                radial-gradient(circle at 8% 16%, rgba(255,255,255,0.44), transparent 26%),
                linear-gradient(135deg, #2FA66A 0%, #3DBB78 50%, #1F6F49 100%) !important;
            border: 1px solid rgba(255,255,255,0.62) !important;
            box-shadow: 0 24px 48px rgba(31, 111, 73, 0.25), 0 5px 0 rgba(255,255,255,0.22) inset !important;
        }

        .upload-zone-card h3,
        .upload-zone-card p {
            color: #ffffff !important;
            text-shadow: 0 2px 10px rgba(18, 59, 42, 0.24) !important;
        }

        .upload-zone-badge {
            background: rgba(255,255,255,0.22) !important;
            color: #ffffff !important;
            border-color: rgba(255,255,255,0.42) !important;
        }

        .stFileUploader, div[data-testid="stFileUploader"] {
            background: linear-gradient(145deg, #ffffff 0%, #EAFBF1 100%) !important;
            border: 2px dashed #2FA66A !important;
        }

        .three-d-divider {
            background: linear-gradient(90deg, rgba(47,166,106,0.08), #2FA66A, #1F6F49, #2FA66A, rgba(47,166,106,0.08)) !important;
        }



        /* ------------------------------------------------------------------
           Final requested fix:
           1) Upload Zone is emerald green.
           2) Metric cards/headings after file upload are forced dark/readable.
        ------------------------------------------------------------------ */
        :root {
            --cif-emerald: #2FA66A;
            --cif-emerald-dark: #1F6F49;
            --cif-emerald-deep: #123B2A;
            --cif-emerald-soft: #EAFBF1;
        }

        .upload-zone-card {
            background:
                radial-gradient(circle at 9% 14%, rgba(255,255,255,0.52), transparent 28%),
                linear-gradient(135deg, #2FA66A 0%, #278A59 46%, #1F6F49 100%) !important;
            border: 1px solid rgba(255,255,255,0.66) !important;
            box-shadow:
                0 26px 54px rgba(31, 111, 73, 0.32),
                0 5px 0 rgba(255,255,255,0.24) inset !important;
        }

        .upload-zone-card .upload-zone-badge {
            background: rgba(255,255,255,0.24) !important;
            color: #ffffff !important;
            border-color: rgba(255,255,255,0.48) !important;
            box-shadow: 0 8px 20px rgba(0, 77, 50, 0.18) !important;
        }

        .upload-zone-card h3,
        .upload-zone-card p,
        .upload-zone-card span,
        .upload-zone-card b,
        .upload-zone-card strong {
            color: #ffffff !important;
            text-shadow: 0 2px 12px rgba(18, 59, 42, 0.34) !important;
        }

        /* Metric cards shown after upload: labels and values must never inherit white text. */
        div[data-testid="metric-container"] {
            background:
                linear-gradient(145deg, #ffffff 0%, #F4FFFA 54%, #EAFBF1 100%) !important;
            border: 1px solid rgba(31, 111, 73, 0.28) !important;
            box-shadow:
                0 16px 38px rgba(31, 111, 73, 0.14),
                0 3px 0 rgba(255,255,255,0.96) inset !important;
        }

        div[data-testid="metric-container"] *,
        div[data-testid="metric-container"] p,
        div[data-testid="metric-container"] span,
        div[data-testid="metric-container"] label,
        div[data-testid="metric-container"] div {
            color: #123B2A !important;
            text-shadow: none !important;
        }

        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] *,
        div[data-testid="stMetricLabel"] p,
        div[data-testid="stMetricLabel"] span {
            color: #123B2A !important;
            font-weight: 850 !important;
            opacity: 1 !important;
        }

        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] *,
        div[data-testid="stMetricValue"] p,
        div[data-testid="stMetricValue"] span {
            color: #247A50 !important;
            font-weight: 950 !important;
            opacity: 1 !important;
        }

        /* Native Streamlit success/info/subheader text after upload can also inherit light colors in some themes. */
        div[data-testid="stAlert"] *,
        div[data-testid="stMarkdownContainer"] h1,
        div[data-testid="stMarkdownContainer"] h2,
        div[data-testid="stMarkdownContainer"] h3,
        div[data-testid="stMarkdownContainer"] h4,
        div[data-testid="stMarkdownContainer"] h5,
        div[data-testid="stMarkdownContainer"] h6,
        .table-card h1,
        .table-card h2,
        .table-card h3,
        .table-card h4,
        .glass-panel h1,
        .glass-panel h2,
        .glass-panel h3,
        .glass-panel h4 {
            color: #123B2A !important;
            text-shadow: none !important;
            opacity: 1 !important;
        }

        /* Keep active tabs/buttons readable on dark green backgrounds. */
        .stTabs [aria-selected="true"],
        .stTabs [aria-selected="true"] *,
        .stButton > button,
        .stButton > button *,
        .stDownloadButton > button,
        .stDownloadButton > button * {
            color: #ffffff !important;
        }


        /* ------------------------------------------------------------------
           Vivid Developer card override: clearly different from emerald cards.
           Uses deep navy/petrol + gold accents while staying compatible with emerald theme.
        ------------------------------------------------------------------ */
        .info-grid > .mini-card.developer-card {
            isolation: isolate !important;
            position: relative !important;
            overflow: hidden !important;
            padding: 22px 22px 20px 24px !important;
            background:
                radial-gradient(circle at 12% 10%, rgba(255,255,255,0.24), transparent 27%),
                radial-gradient(circle at 92% 18%, rgba(255,215,122,0.24), transparent 28%),
                linear-gradient(135deg, #102A43 0%, #0B5D5A 50%, #113B5B 100%) !important;
            border: 2px solid rgba(255, 202, 88, 0.88) !important;
            box-shadow:
                0 26px 62px rgba(16, 42, 67, 0.30),
                0 10px 28px rgba(47, 166, 106, 0.20),
                0 0 0 4px rgba(255, 202, 88, 0.18),
                0 4px 0 rgba(255,255,255,0.18) inset !important;
            transform: translateY(-2px) !important;
        }

        .info-grid > .mini-card.developer-card::before {
            content: "" !important;
            position: absolute !important;
            inset: 0 auto 0 0 !important;
            width: 11px !important;
            background: linear-gradient(180deg, #FFD166 0%, #F6B73C 45%, #2FA66A 100%) !important;
            box-shadow: 8px 0 24px rgba(255, 209, 102, 0.38) !important;
            z-index: 0 !important;
        }

        .info-grid > .mini-card.developer-card::after {
            content: "Developer" !important;
            position: absolute !important;
            top: 14px !important;
            right: 16px !important;
            padding: 6px 11px !important;
            border-radius: 999px !important;
            background: rgba(255, 209, 102, 0.22) !important;
            color: #FFF5D6 !important;
            border: 1px solid rgba(255, 209, 102, 0.58) !important;
            font-size: 11px !important;
            font-weight: 950 !important;
            letter-spacing: 0.75px !important;
            text-transform: uppercase !important;
            z-index: 1 !important;
        }

        .info-grid > .mini-card.developer-card h4,
        .info-grid > .mini-card.developer-card h4 * {
            color: #FFD166 !important;
            text-shadow: 0 2px 12px rgba(0,0,0,0.36) !important;
            font-size: 15px !important;
            letter-spacing: 1.15px !important;
            margin-right: 112px !important;
            position: relative !important;
            z-index: 2 !important;
        }

        .info-grid > .mini-card.developer-card p,
        .info-grid > .mini-card.developer-card li,
        .info-grid > .mini-card.developer-card span {
            color: #E9FFF5 !important;
            text-shadow: 0 2px 10px rgba(0,0,0,0.28) !important;
            position: relative !important;
            z-index: 2 !important;
            opacity: 1 !important;
        }

        .info-grid > .mini-card.developer-card strong,
        .info-grid > .mini-card.developer-card b {
            display: inline-block !important;
            margin: 2px 0 4px 0 !important;
            padding: 7px 10px !important;
            border-radius: 12px !important;
            background: rgba(255, 255, 255, 0.14) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.22) !important;
            box-shadow: 0 8px 18px rgba(0,0,0,0.16) !important;
            font-weight: 950 !important;
            text-shadow: 0 2px 10px rgba(0,0,0,0.32) !important;
        }

        .info-grid > .mini-card.developer-card:hover {
            transform: translateY(-6px) scale(1.01) !important;
            box-shadow:
                0 34px 76px rgba(16, 42, 67, 0.38),
                0 12px 34px rgba(47, 166, 106, 0.24),
                0 0 0 5px rgba(255, 202, 88, 0.24),
                0 4px 0 rgba(255,255,255,0.20) inset !important;
        }



        /* ------------------------------------------------------------------
           Global visible theme refresh requested by user:
           Use the same vivid navy + gold combination across the whole UI,
           while keeping a soft emerald accent for harmony.
        ------------------------------------------------------------------ */
        :root {
            --cif-primary-navy: #102A43;
            --cif-primary-navy-2: #163A5B;
            --cif-primary-navy-3: #1E4C78;
            --cif-gold-bright: #FFC857;
            --cif-gold-soft: #F4D58D;
            --cif-emerald-accent: #2FA66A;
            --cif-emerald-accent-dark: #1F6F49;
            --cif-cream-bg: #FFF8EA;
            --cif-surface: #FFFDF8;
            --cif-surface-2: #FDF6E8;
            --cif-text-deep: #13273F;
            --cif-text-soft: #4A5B70;
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 7%, rgba(255, 200, 87, 0.16), transparent 24%),
                radial-gradient(circle at 92% 10%, rgba(47, 166, 106, 0.10), transparent 26%),
                radial-gradient(circle at 75% 88%, rgba(16, 42, 67, 0.08), transparent 28%),
                linear-gradient(145deg, #FFFDF8 0%, #FFF8EA 40%, #F9FBFC 72%, #FFFFFF 100%) !important;
            color: var(--cif-text-deep) !important;
        }

        h1, h2, h3, h4, h5, h6,
        .stMarkdown, .stMarkdown p, .stMarkdown li,
        .stCaptionContainer, .stText, label,
        div[data-testid="stWidgetLabel"], div[data-testid="stWidgetLabel"] p,
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li,
        .caption-note, .muted,
        td, th, span {
            color: var(--cif-text-deep) !important;
        }

        .hero-card,
        .upload-zone-card,
        .hamburger-shell,
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapseButton"] {
            background:
                radial-gradient(circle at 10% 12%, rgba(255,255,255,0.16), transparent 28%),
                linear-gradient(135deg, var(--cif-primary-navy) 0%, var(--cif-primary-navy-2) 52%, var(--cif-primary-navy-3) 100%) !important;
            border: 1px solid rgba(255, 200, 87, 0.68) !important;
            box-shadow:
                0 28px 60px rgba(16, 42, 67, 0.30),
                0 10px 30px rgba(255, 200, 87, 0.14),
                0 3px 0 rgba(255,255,255,0.10) inset !important;
        }

        .hero-card::after,
        .upload-zone-card::after,
        .hamburger-shell::after {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            border-radius: inherit;
            box-shadow: 0 0 0 1px rgba(255, 200, 87, 0.22) inset;
        }

        .hero-topline,
        .upload-zone-badge,
        .hamburger-pill {
            background: rgba(255, 200, 87, 0.16) !important;
            color: #FFF4D2 !important;
            border: 1px solid rgba(255, 200, 87, 0.40) !important;
            box-shadow: 0 10px 20px rgba(0,0,0,0.12) !important;
        }

        .hero-title,
        .hero-subtitle,
        .upload-zone-card h3,
        .upload-zone-card p,
        .upload-zone-card span,
        .upload-zone-card b,
        .upload-zone-card strong,
        .hamburger-title,
        .hamburger-shell summary,
        .hamburger-shell summary *,
        [data-testid="collapsedControl"] button,
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stSidebarCollapseButton"] svg {
            color: #FFFFFF !important;
        }

        .mini-card,
        .glass-panel,
        .table-card,
        .brand-card,
        .sidebar-block,
        div[data-testid="metric-container"],
        div[data-testid="stDataFrame"] {
            background:
                linear-gradient(145deg, rgba(255,253,248,0.98) 0%, rgba(253,246,232,0.96) 100%) !important;
            border: 1px solid rgba(255, 200, 87, 0.42) !important;
            box-shadow:
                0 18px 42px rgba(16, 42, 67, 0.08),
                0 6px 18px rgba(255, 200, 87, 0.12),
                0 3px 0 rgba(255,255,255,0.96) inset !important;
        }

        .mini-card:hover,
        .glass-panel:hover,
        .table-card:hover,
        .brand-card:hover,
        .sidebar-block:hover,
        div[data-testid="metric-container"]:hover {
            transform: translateY(-4px) !important;
            box-shadow:
                0 26px 58px rgba(16, 42, 67, 0.14),
                0 10px 24px rgba(255, 200, 87, 0.18),
                0 3px 0 rgba(255,255,255,0.96) inset !important;
        }

        .mini-card h4,
        .sidebar-block h4,
        .brand-card .name,
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] *,
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] *,
        .table-card h1, .table-card h2, .table-card h3, .table-card h4,
        .glass-panel h1, .glass-panel h2, .glass-panel h3, .glass-panel h4 {
            color: var(--cif-primary-navy) !important;
            text-shadow: none !important;
        }

        .mini-card p,
        .mini-card li,
        .sidebar-block p,
        .sidebar-block li,
        .caption-note,
        .muted,
        .brand-card p,
        .glass-panel p,
        .table-card p,
        div[data-testid="metric-container"] p,
        div[data-testid="metric-container"] span,
        div[data-testid="metric-container"] div {
            color: var(--cif-text-soft) !important;
        }

        .mini-card strong,
        .brand-card strong,
        .sidebar-block strong {
            color: var(--cif-primary-navy-2) !important;
        }

        .section-label {
            background: rgba(255, 200, 87, 0.18) !important;
            color: var(--cif-primary-navy) !important;
            border: 1px solid rgba(255, 200, 87, 0.48) !important;
        }

        section[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 12% 5%, rgba(255,200,87,0.16), transparent 28%),
                linear-gradient(180deg, #FFFDF8 0%, #FFF8EA 45%, #FDF1D8 100%) !important;
            border-right: 1px solid rgba(255, 200, 87, 0.34) !important;
            box-shadow: 14px 0 36px rgba(16, 42, 67, 0.08) !important;
        }
        section[data-testid="stSidebar"] * { color: var(--cif-text-deep) !important; }

        .stTabs [data-baseweb="tab-list"] {
            background: rgba(16, 42, 67, 0.08) !important;
            border: 1px solid rgba(255, 200, 87, 0.22) !important;
        }

        .stTabs [data-baseweb="tab"] {
            background: rgba(255,255,255,0.96) !important;
            color: var(--cif-primary-navy) !important;
            border: 1px solid rgba(255, 200, 87, 0.18) !important;
            box-shadow: 0 6px 16px rgba(16, 42, 67, 0.06) !important;
        }

        .stTabs [aria-selected="true"],
        .stButton > button,
        .stDownloadButton > button {
            background: linear-gradient(135deg, var(--cif-primary-navy) 0%, var(--cif-primary-navy-2) 58%, var(--cif-primary-navy-3) 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 200, 87, 0.62) !important;
            box-shadow: 0 18px 36px rgba(16, 42, 67, 0.22), 0 0 0 1px rgba(255, 200, 87, 0.18) inset !important;
        }

        .stTabs [aria-selected="true"] p,
        .stTabs [aria-selected="true"] span,
        .stButton > button *,
        .stDownloadButton > button * {
            color: #FFFFFF !important;
        }

        .hamburger-links a {
            color: var(--cif-primary-navy) !important;
            background: rgba(255, 250, 240, 0.98) !important;
            border: 1px solid rgba(255, 200, 87, 0.30) !important;
            box-shadow: 0 8px 18px rgba(16, 42, 67, 0.08) !important;
        }

        .hamburger-links a:hover {
            color: var(--cif-primary-navy-2) !important;
            border-color: rgba(47, 166, 106, 0.44) !important;
            box-shadow: 0 12px 24px rgba(16, 42, 67, 0.12), 0 0 0 3px rgba(47, 166, 106, 0.10) !important;
        }

        .stFileUploader, div[data-testid="stFileUploader"] {
            background: linear-gradient(145deg, #FFFEFB 0%, #FFF4DC 100%) !important;
            border: 2px dashed #FFC857 !important;
            box-shadow: 0 18px 36px rgba(16,42,67,0.08), 0 8px 18px rgba(255,200,87,0.10) inset !important;
        }

        code {
            color: var(--cif-primary-navy) !important;
            background: rgba(255, 200, 87, 0.12) !important;
            border-radius: 8px;
            padding: 2px 5px;
        }

        .three-d-divider {
            background: linear-gradient(90deg, rgba(255,200,87,0.05), #FFC857, #2FA66A, #163A5B, rgba(255,200,87,0.05)) !important;
        }

        /* Make the developer card match the same global language even more strongly. */
        .info-grid > .mini-card.developer-card {
            background:
                radial-gradient(circle at 10% 12%, rgba(255,255,255,0.14), transparent 30%),
                linear-gradient(135deg, var(--cif-primary-navy) 0%, var(--cif-primary-navy-2) 55%, var(--cif-primary-navy-3) 100%) !important;
            border: 1px solid rgba(255, 200, 87, 0.72) !important;
            box-shadow:
                0 34px 76px rgba(16, 42, 67, 0.34),
                0 12px 32px rgba(255, 200, 87, 0.15),
                0 0 0 4px rgba(255, 200, 87, 0.10),
                0 3px 0 rgba(255,255,255,0.10) inset !important;
        }

        .info-grid > .mini-card.developer-card h4 {
            color: #FFD778 !important;
            letter-spacing: 1px !important;
        }

        .info-grid > .mini-card.developer-card p,
        .info-grid > .mini-card.developer-card li,
        .info-grid > .mini-card.developer-card span {
            color: #EAF4FF !important;
        }

        .info-grid > .mini-card.developer-card strong,
        .info-grid > .mini-card.developer-card b {
            display: inline-block !important;
            background: rgba(255, 200, 87, 0.16) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 200, 87, 0.34) !important;
        }

        
        /* ================================================================
           CLEAN FINAL FIX
           1) Hero subtitle readable
           2) Upload component readable
           3) Sidebar brand card no longer shows raw HTML/code
        ================================================================ */

        .hero-card .hero-subtitle,
        .hero-card .hero-subtitle * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            opacity: 1 !important;
            font-weight: 800 !important;
            line-height: 1.75 !important;
            text-shadow: 0 2px 12px rgba(0,0,0,0.70) !important;
        }

        .sidebar-brand-card {
            background: linear-gradient(135deg, #102A43 0%, #163A5B 55%, #1E4C78 100%) !important;
            border: 1px solid rgba(255, 200, 87, 0.70) !important;
            box-shadow: 0 18px 42px rgba(16, 42, 67, 0.26), 0 0 0 3px rgba(255, 200, 87, 0.12) !important;
        }

        .sidebar-brand-card .brand-kicker {
            font-size: 12px !important;
            color: #FFC857 !important;
            -webkit-text-fill-color: #FFC857 !important;
            letter-spacing: 1.4px !important;
            text-transform: uppercase !important;
            font-weight: 900 !important;
            margin-bottom: 8px !important;
        }

        .sidebar-brand-card .name {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            font-weight: 950 !important;
            font-size: 19px !important;
            line-height: 1.35 !important;
            margin-bottom: 8px !important;
        }

        .sidebar-brand-card .muted {
            color: #EAF4FF !important;
            -webkit-text-fill-color: #EAF4FF !important;
            opacity: 1 !important;
            text-shadow: 0 2px 10px rgba(0,0,0,0.35) !important;
            line-height: 1.65 !important;
            font-weight: 600 !important;
        }

        /* File uploader */
        div[data-testid="stFileUploader"] {
            background: #FFF8EA !important;
            border: 2px dashed #FFC857 !important;
            border-radius: 22px !important;
            padding: 14px !important;
            box-shadow: 0 16px 34px rgba(16, 42, 67, 0.10) !important;
        }

        div[data-testid="stFileUploader"] > label,
        div[data-testid="stFileUploader"] > label *,
        div[data-testid="stFileUploader"] label,
        div[data-testid="stFileUploader"] label * {
            color: #102A43 !important;
            -webkit-text-fill-color: #102A43 !important;
            opacity: 1 !important;
            font-weight: 900 !important;
            text-shadow: none !important;
        }

        div[data-testid="stFileUploader"] section,
        section[data-testid="stFileUploaderDropzone"],
        div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
            background: #102A43 !important;
            border: 1px solid rgba(255,200,87,0.72) !important;
            border-radius: 14px !important;
        }

        div[data-testid="stFileUploader"] section *,
        section[data-testid="stFileUploaderDropzone"] *,
        div[data-testid="stFileUploader"] small,
        div[data-testid="stFileUploader"] span,
        div[data-testid="stFileUploader"] p {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            opacity: 1 !important;
            fill: #FFFFFF !important;
            stroke: #FFFFFF !important;
            font-weight: 700 !important;
            text-shadow: none !important;
        }

        div[data-testid="stFileUploader"] button,
        div[data-testid="stFileUploader"] button *,
        section[data-testid="stFileUploaderDropzone"] button,
        section[data-testid="stFileUploaderDropzone"] button * {
            background: #FFC857 !important;
            background-color: #FFC857 !important;
            color: #102A43 !important;
            -webkit-text-fill-color: #102A43 !important;
            border: 1px solid rgba(255,255,255,0.85) !important;
            opacity: 1 !important;
            font-weight: 900 !important;
            text-shadow: none !important;
        }



        /* ---------------------------------------------------------------
           Readable sheet-list cards: replaces dark JSON/code output after upload.
        --------------------------------------------------------------- */
        .sheet-list-box {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 10px !important;
            align-items: center !important;
            margin: 8px 0 14px 0 !important;
            padding: 14px 14px !important;
            border-radius: 18px !important;
            background: linear-gradient(145deg, #FFFEFB 0%, #FFF8EA 100%) !important;
            border: 1px solid rgba(255, 200, 87, 0.44) !important;
            box-shadow: 0 12px 28px rgba(16, 42, 67, 0.08), 0 2px 0 rgba(255,255,255,0.92) inset !important;
        }

        .sheet-pill {
            display: inline-flex !important;
            align-items: center !important;
            gap: 8px !important;
            padding: 9px 13px !important;
            border-radius: 999px !important;
            color: #102A43 !important;
            -webkit-text-fill-color: #102A43 !important;
            background: #FFFFFF !important;
            border: 1px solid rgba(16, 42, 67, 0.14) !important;
            box-shadow: 0 8px 18px rgba(16, 42, 67, 0.07) !important;
            font-weight: 900 !important;
            font-size: 13px !important;
            letter-spacing: 0.2px !important;
            text-shadow: none !important;
        }

        .sheet-pill::before {
            content: "" !important;
            width: 8px !important;
            height: 8px !important;
            border-radius: 999px !important;
            background: #2FA66A !important;
            box-shadow: 0 0 0 4px rgba(47, 166, 106, 0.13) !important;
        }

        .sheet-pill.skipped::before {
            background: #FFC857 !important;
            box-shadow: 0 0 0 4px rgba(255, 200, 87, 0.18) !important;
        }

        .sheet-pill.skipped {
            color: #4A5B70 !important;
            -webkit-text-fill-color: #4A5B70 !important;
            background: #FFFDF8 !important;
            border-color: rgba(255, 200, 87, 0.52) !important;
        }

        .sheet-list-note {
            margin: 8px 0 6px 0 !important;
            color: #4A5B70 !important;
            -webkit-text-fill-color: #4A5B70 !important;
            font-size: 14px !important;
            font-weight: 800 !important;
            text-shadow: none !important;
        }

        /* In case Streamlit JSON/code blocks remain anywhere, make them readable too. */
        div[data-testid="stJson"],
        div[data-testid="stJson"] *,
        pre, pre *, code, code * {
            color: #102A43 !important;
            -webkit-text-fill-color: #102A43 !important;
            text-shadow: none !important;
        }

        div[data-testid="stJson"], pre {
            background: #FFFDF8 !important;
            border: 1px solid rgba(255, 200, 87, 0.44) !important;
            border-radius: 16px !important;
        }



        /* ================================================================
           CIF_DEMATEL_16 - High-contrast uploaded workbook sheet summary
           Fixes unreadable dark JSON/code blocks after Excel upload.
        ================================================================ */
        .sheet-clean-panel,
        .sheet-clean-panel * {
            color: #102A43 !important;
            -webkit-text-fill-color: #102A43 !important;
            opacity: 1 !important;
            text-shadow: none !important;
            font-family: 'Inter', 'Segoe UI', sans-serif !important;
            box-sizing: border-box !important;
        }

        .sheet-clean-panel {
            width: 100% !important;
            margin: 0 0 18px 0 !important;
            padding: 22px 24px !important;
            border-radius: 24px !important;
            background: linear-gradient(145deg, #FFFFFF 0%, #FFF8EA 48%, #F4FFFA 100%) !important;
            border: 2px solid rgba(255, 200, 87, 0.72) !important;
            box-shadow:
                0 22px 52px rgba(16, 42, 67, 0.12),
                0 6px 16px rgba(255, 200, 87, 0.16),
                0 3px 0 rgba(255,255,255,0.98) inset !important;
            overflow: hidden !important;
        }

        .sheet-clean-header {
            display: flex !important;
            justify-content: space-between !important;
            gap: 14px !important;
            align-items: flex-start !important;
            margin-bottom: 18px !important;
            padding-bottom: 14px !important;
            border-bottom: 1px solid rgba(16, 42, 67, 0.10) !important;
        }

        .sheet-clean-title {
            margin: 0 !important;
            color: #102A43 !important;
            -webkit-text-fill-color: #102A43 !important;
            font-size: 26px !important;
            line-height: 1.25 !important;
            font-weight: 950 !important;
            letter-spacing: -0.3px !important;
        }

        .sheet-clean-subtitle {
            margin: 6px 0 0 0 !important;
            color: #4A5B70 !important;
            -webkit-text-fill-color: #4A5B70 !important;
            font-size: 14px !important;
            line-height: 1.65 !important;
            font-weight: 750 !important;
        }

        .sheet-clean-counts {
            display: flex !important;
            gap: 10px !important;
            flex-wrap: wrap !important;
            justify-content: flex-end !important;
        }

        .sheet-count-badge {
            min-width: 112px !important;
            padding: 10px 12px !important;
            border-radius: 16px !important;
            background: #FFFFFF !important;
            border: 1px solid rgba(16, 42, 67, 0.12) !important;
            box-shadow: 0 10px 22px rgba(16, 42, 67, 0.08) !important;
            text-align: center !important;
        }

        .sheet-count-badge .num {
            display: block !important;
            font-size: 22px !important;
            line-height: 1 !important;
            font-weight: 950 !important;
            color: #1F6F49 !important;
            -webkit-text-fill-color: #1F6F49 !important;
        }

        .sheet-count-badge.skipped .num {
            color: #9B6500 !important;
            -webkit-text-fill-color: #9B6500 !important;
        }

        .sheet-count-badge .lbl {
            display: block !important;
            margin-top: 5px !important;
            color: #4A5B70 !important;
            -webkit-text-fill-color: #4A5B70 !important;
            font-size: 11px !important;
            font-weight: 900 !important;
            letter-spacing: 0.75px !important;
            text-transform: uppercase !important;
        }

        .sheet-clean-grid {
            display: grid !important;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)) !important;
            gap: 12px !important;
            margin-top: 12px !important;
        }

        .sheet-clean-item {
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 12px !important;
            min-height: 58px !important;
            padding: 13px 14px !important;
            border-radius: 18px !important;
            background: #FFFFFF !important;
            border: 1px solid rgba(31, 111, 73, 0.22) !important;
            box-shadow: 0 10px 24px rgba(16, 42, 67, 0.07) !important;
        }

        .sheet-clean-item.skipped {
            background: #FFFDF8 !important;
            border-color: rgba(255, 200, 87, 0.60) !important;
        }

        .sheet-name-wrap {
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            min-width: 0 !important;
        }

        .sheet-dot {
            flex: 0 0 auto !important;
            width: 11px !important;
            height: 11px !important;
            border-radius: 999px !important;
            background: #2FA66A !important;
            box-shadow: 0 0 0 5px rgba(47, 166, 106, 0.14) !important;
        }

        .sheet-clean-item.skipped .sheet-dot {
            background: #FFC857 !important;
            box-shadow: 0 0 0 5px rgba(255, 200, 87, 0.18) !important;
        }

        .sheet-name {
            display: block !important;
            min-width: 0 !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
            color: #102A43 !important;
            -webkit-text-fill-color: #102A43 !important;
            font-size: 16px !important;
            line-height: 1.35 !important;
            font-weight: 950 !important;
        }

        .sheet-status {
            flex: 0 0 auto !important;
            padding: 6px 9px !important;
            border-radius: 999px !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            background: #1F6F49 !important;
            font-size: 10px !important;
            line-height: 1 !important;
            font-weight: 950 !important;
            letter-spacing: 0.65px !important;
            text-transform: uppercase !important;
        }

        .sheet-clean-item.skipped .sheet-status {
            color: #102A43 !important;
            -webkit-text-fill-color: #102A43 !important;
            background: #FFC857 !important;
        }

        .sheet-clean-section-label {
            display: inline-flex !important;
            align-items: center !important;
            margin: 18px 0 6px 0 !important;
            padding: 7px 11px !important;
            border-radius: 999px !important;
            background: rgba(16, 42, 67, 0.08) !important;
            color: #102A43 !important;
            -webkit-text-fill-color: #102A43 !important;
            font-size: 12px !important;
            font-weight: 950 !important;
            letter-spacing: 0.85px !important;
            text-transform: uppercase !important;
            border: 1px solid rgba(16, 42, 67, 0.10) !important;
        }

        @media (max-width: 760px) {
            .sheet-clean-header { flex-direction: column !important; }
            .sheet-clean-counts { justify-content: flex-start !important; }
            .sheet-clean-title { font-size: 22px !important; }
            .sheet-clean-grid { grid-template-columns: 1fr !important; }
        }



        /* ================================================================
           FINAL TOP BAR FIX - Heavy Gold Streamlit header / toolbar
           Makes the native Streamlit top bar readable instead of black.
        ================================================================ */
        header[data-testid="stHeader"],
        .stAppHeader {
            background:
                radial-gradient(circle at 4% 50%, rgba(255,255,255,0.28), transparent 24%),
                linear-gradient(135deg, #6F4E00 0%, #B8860B 28%, #D4AF37 54%, #8A6508 100%) !important;
            border-bottom: 1px solid rgba(255, 238, 178, 0.70) !important;
            box-shadow:
                0 14px 34px rgba(111, 78, 0, 0.35),
                0 2px 0 rgba(255,255,255,0.22) inset !important;
            color: #102A43 !important;
        }

        header[data-testid="stHeader"]::before,
        .stAppHeader::before {
            content: "" !important;
            position: absolute !important;
            inset: 0 !important;
            pointer-events: none !important;
            background: linear-gradient(90deg, rgba(255,255,255,0.18), transparent 35%, rgba(255,255,255,0.12)) !important;
        }

        /* Streamlit toolbar / deploy / menu icons */
        header[data-testid="stHeader"] *,
        .stAppHeader *,
        div[data-testid="stToolbar"],
        div[data-testid="stToolbar"] *,
        div[data-testid="stDeployButton"],
        div[data-testid="stDeployButton"] *,
        button[kind="header"],
        button[kind="header"] *,
        [data-testid="baseButton-header"],
        [data-testid="baseButton-header"] * {
            color: #102A43 !important;
            -webkit-text-fill-color: #102A43 !important;
            fill: #102A43 !important;
            stroke: #102A43 !important;
            opacity: 1 !important;
            text-shadow: none !important;
        }

        header[data-testid="stHeader"] button,
        .stAppHeader button,
        div[data-testid="stToolbar"] button,
        div[data-testid="stDeployButton"] button,
        button[kind="header"],
        [data-testid="baseButton-header"] {
            background: rgba(255, 253, 248, 0.34) !important;
            border: 1px solid rgba(16, 42, 67, 0.20) !important;
            border-radius: 12px !important;
            box-shadow: 0 8px 18px rgba(111, 78, 0, 0.18) !important;
        }

        header[data-testid="stHeader"] button:hover,
        .stAppHeader button:hover,
        div[data-testid="stToolbar"] button:hover,
        div[data-testid="stDeployButton"] button:hover,
        button[kind="header"]:hover,
        [data-testid="baseButton-header"]:hover {
            background: rgba(255, 255, 255, 0.58) !important;
            border-color: rgba(16, 42, 67, 0.34) !important;
            transform: translateY(-1px) !important;
        }

        /* The small top decoration line should match the gold header. */
        [data-testid="stDecoration"] {
            background: linear-gradient(90deg, #6F4E00 0%, #D4AF37 45%, #FFC857 65%, #8A6508 100%) !important;
            height: 4px !important;
        }

        /* In some Streamlit builds the top bar is rendered as these classes. */
        .st-emotion-cache-18ni7ap,
        .st-emotion-cache-h4xjwg,
        .st-emotion-cache-zq5wmm {
            background:
                radial-gradient(circle at 4% 50%, rgba(255,255,255,0.24), transparent 24%),
                linear-gradient(135deg, #6F4E00 0%, #B8860B 30%, #D4AF37 58%, #8A6508 100%) !important;
            color: #102A43 !important;
            border-bottom: 1px solid rgba(255, 238, 178, 0.65) !important;
        }


        /* ================================================================
           FINAL UPLOAD ZONE FIX - Heavy Gold box + white readable text
           Requested: make Upload Zone text white / make upload box gold.
        ================================================================ */
        .upload-zone-card {
            background:
                radial-gradient(circle at 8% 12%, rgba(255,255,255,0.34), transparent 28%),
                radial-gradient(circle at 92% 18%, rgba(255,255,255,0.18), transparent 30%),
                linear-gradient(135deg, #6F4E00 0%, #A87400 28%, #D4AF37 58%, #8A6508 100%) !important;
            border: 2px solid rgba(255, 238, 178, 0.92) !important;
            box-shadow:
                0 28px 64px rgba(111, 78, 0, 0.34),
                0 0 0 4px rgba(255, 200, 87, 0.14),
                0 5px 0 rgba(255,255,255,0.22) inset !important;
        }

        .upload-zone-card .upload-zone-badge {
            background: rgba(16, 42, 67, 0.30) !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            border: 1px solid rgba(255,255,255,0.42) !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.18) !important;
            opacity: 1 !important;
        }

        .upload-zone-card h1,
        .upload-zone-card h2,
        .upload-zone-card h3,
        .upload-zone-card h4,
        .upload-zone-card p,
        .upload-zone-card span,
        .upload-zone-card div,
        .upload-zone-card b,
        .upload-zone-card strong,
        .upload-zone-card * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            opacity: 1 !important;
            text-shadow: 0 3px 14px rgba(0,0,0,0.58) !important;
        }

        .upload-zone-card h3 {
            font-weight: 950 !important;
            letter-spacing: 0.2px !important;
        }

        .upload-zone-card p {
            font-weight: 750 !important;
            line-height: 1.75 !important;
        }




        /* ================================================================
           FINAL REQUEST 19 - keep everything else unchanged
           1) Force a light-looking default interface.
           2) Make the Upload Zone a clear premium gold box.
        ================================================================ */
        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"],
        .block-container {
            color-scheme: light !important;
        }

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background:
                radial-gradient(circle at 8% 7%, rgba(255, 209, 102, 0.14), transparent 25%),
                radial-gradient(circle at 94% 8%, rgba(47, 166, 106, 0.08), transparent 27%),
                linear-gradient(145deg, #FFFDF8 0%, #FFF8EA 42%, #FFFFFF 100%) !important;
            color: #102A43 !important;
        }

        .upload-zone-card {
            background:
                radial-gradient(circle at 9% 12%, rgba(255,255,255,0.42), transparent 28%),
                radial-gradient(circle at 88% 18%, rgba(255,244,210,0.30), transparent 32%),
                linear-gradient(135deg, #8A6508 0%, #B8860B 24%, #D4AF37 50%, #FFD166 72%, #A87400 100%) !important;
            border: 2px solid rgba(255, 244, 210, 0.96) !important;
            box-shadow:
                0 30px 68px rgba(111, 78, 0, 0.35),
                0 0 0 5px rgba(255, 209, 102, 0.18),
                0 6px 0 rgba(255,255,255,0.26) inset !important;
        }

        .upload-zone-card .upload-zone-badge {
            background: rgba(16, 42, 67, 0.34) !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            border: 1px solid rgba(255,255,255,0.52) !important;
            box-shadow: 0 10px 24px rgba(0,0,0,0.20) !important;
            opacity: 1 !important;
        }

        .upload-zone-card h1,
        .upload-zone-card h2,
        .upload-zone-card h3,
        .upload-zone-card h4,
        .upload-zone-card p,
        .upload-zone-card span,
        .upload-zone-card div,
        .upload-zone-card b,
        .upload-zone-card strong,
        .upload-zone-card * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            opacity: 1 !important;
            text-shadow: 0 3px 15px rgba(0,0,0,0.62) !important;
        }

        .upload-zone-card h3 {
            font-weight: 950 !important;
        }

        .upload-zone-card p {
            font-weight: 800 !important;
            line-height: 1.78 !important;
        }

        

        /* ================================================================
           FINAL REQUEST 20 - Upload Zone must be gold and all text white
           This is intentionally placed at the very end of the CSS.
        ================================================================ */
        .upload-zone-card.upload-zone-gold-final,
        div.upload-zone-card.upload-zone-gold-final {
            background:
                radial-gradient(circle at 9% 12%, rgba(255,255,255,0.45), transparent 28%),
                radial-gradient(circle at 88% 16%, rgba(255,244,210,0.38), transparent 32%),
                linear-gradient(135deg, #6F4E00 0%, #9B7208 23%, #D4AF37 52%, #FFD166 74%, #8A6508 100%) !important;
            border: 2px solid rgba(255,244,210,0.98) !important;
            box-shadow:
                0 30px 68px rgba(111,78,0,0.38),
                0 0 0 5px rgba(255,209,102,0.22),
                0 6px 0 rgba(255,255,255,0.28) inset !important;
        }

        .upload-zone-card.upload-zone-gold-final,
        .upload-zone-card.upload-zone-gold-final *,
        .upload-zone-card.upload-zone-gold-final .upload-zone-title,
        .upload-zone-card.upload-zone-gold-final .upload-zone-description,
        .upload-zone-card.upload-zone-gold-final .upload-zone-badge {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            opacity: 1 !important;
            text-shadow: 0 4px 16px rgba(0,0,0,0.72) !important;
        }

        .upload-zone-card.upload-zone-gold-final .upload-zone-description {
            font-size: 16px !important;
            font-weight: 850 !important;
            line-height: 1.85 !important;
        }


        /* FINAL FORCE: Upload Zone description text must stay pure white. */
        #force-upload-desc-white,
        #force-upload-desc-white *,
        div#force-upload-desc-white,
        div#force-upload-desc-white span {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            opacity: 1 !important;
            font-weight: 900 !important;
            text-shadow: 0 4px 18px rgba(0,0,0,0.78) !important;
        }



        /* ================================================================
           FINAL EXPORT DOWNLOAD BUTTON FIX
           Make the "Download Excel Results" button highly visible.
        ================================================================ */
        div[data-testid="stDownloadButton"] button,
        div[data-testid="stDownloadButton"] > button,
        .stDownloadButton > button {
            background: linear-gradient(135deg, #8A5A00 0%, #B8860B 28%, #D4AF37 58%, #F4D06F 100%) !important;
            background-color: #D4AF37 !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            border: 2px solid rgba(255, 244, 210, 0.95) !important;
            border-radius: 18px !important;
            font-weight: 950 !important;
            letter-spacing: 0.2px !important;
            text-shadow: 0 2px 10px rgba(0,0,0,0.55) !important;
            box-shadow:
                0 18px 38px rgba(138, 90, 0, 0.32),
                0 0 0 3px rgba(212, 175, 55, 0.18),
                0 3px 0 rgba(255,255,255,0.30) inset !important;
            opacity: 1 !important;
        }

        div[data-testid="stDownloadButton"] button *,
        div[data-testid="stDownloadButton"] button p,
        div[data-testid="stDownloadButton"] button span,
        div[data-testid="stDownloadButton"] button div,
        .stDownloadButton > button *,
        .stDownloadButton > button p,
        .stDownloadButton > button span,
        .stDownloadButton > button div {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            fill: #FFFFFF !important;
            stroke: #FFFFFF !important;
            opacity: 1 !important;
            font-weight: 950 !important;
            text-shadow: 0 2px 10px rgba(0,0,0,0.55) !important;
        }

        div[data-testid="stDownloadButton"] button:hover,
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #9A6600 0%, #C99612 30%, #E2BD43 62%, #FFE08A 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow:
                0 24px 48px rgba(138, 90, 0, 0.42),
                0 0 0 4px rgba(212, 175, 55, 0.24),
                0 3px 0 rgba(255,255,255,0.36) inset !important;
        }

</style>
        """,
        unsafe_allow_html=True,
    )



def hamburger_menu():
    st.markdown(
        """
        <details class="hamburger-shell">
            <summary>
                <span class="hamburger-icon"><span></span><span></span><span></span></span>
                <span class="hamburger-title">CIF-CRITIC Menu</span>
                <span class="hamburger-pill">Quick access</span>
            </summary>
            <div class="hamburger-links">
                <a href="#input-guide">Input Guide</a>
                <a href="#active-scale">Scales</a>
                <a href="#upload-workbook">Upload Workbook</a>
                <a href="#results-dashboard">Results</a>
                <a href="#download-results">Export</a>
                <a href="#">Back to Top</a>
            </div>
        </details>
        """,
        unsafe_allow_html=True,
    )


def hero_section():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-topline">Navy & Gold Decision Analytics</div>
            <div class="hero-title">CIF-CRITIC Calculator</div>
            <p class="hero-subtitle" style="color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; opacity:1 !important; font-weight:800 !important; line-height:1.75 !important; text-shadow:0 2px 12px rgba(0,0,0,0.70) !important;">
                A navy, gold, and soft emerald executive Streamlit interface for Circular Intuitionistic Fuzzy CRITIC.
                Upload expert decision matrices, aggregate circular intuitionistic fuzzy evaluations,
                build optimistic and pessimistic decision matrices, normalize benefit/cost criteria, evaluate inter-criteria correlations,
                and calculate the final objective criterion weights.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def header_panels():
    st.markdown(
        """
        <div class="info-grid">
            <div class="mini-card developer-card">
                <h4>Developer & Concept Designer</h4>
                <p><strong>Dr. Saeed Alinejad - Shiraz University, Iran</strong></p>
                <p>Advanced decision-making tool developer.</p>
            </div>
            <div class="mini-card">
                <h4>CIF-CRITIC Logic</h4>
                <p>Each evaluation is modeled by membership, non-membership, hesitation, and a circular radius. CRITIC then extracts objective criterion weights from contrast intensity and inter-criteria conflict.</p>
            </div>
            <div class="mini-card">
                <h4>Objective Weighting</h4>
                <p>The final dashboard reports optimistic and pessimistic CRITIC intensities, crisp intensity, normalized weights, and the ranking of criteria.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def intro_card():
    st.markdown(
        """
        <div id="input-guide"></div>
        <div class="glass-panel">
            <span class="section-label">Input Guide</span>
            <div class="caption-note">
                Create one sheet per expert. Each expert sheet must be a decision matrix:
                first column = alternative / challenge / option, first row = criteria. Valid CIF-CRITIC terms:
                <b>CHV, VHV, HV, AAV, AV, UAV, LV, VLV, CLV</b>. Numeric ratings <b>9..1</b> are also accepted.
                Optional sheet <b>Expert_Info</b> can contain columns <b>Expert</b> and either <b>Weight</b> or <b>WeightTerm</b>.
                Optional sheet <b>Criteria_Types</b> can contain <b>Criterion</b> and <b>Type</b> where Type is Benefit or Cost.
            </div>
            <br>
            <table style="width:100%; border-collapse: collapse; font-size:14px;">
                <tr>
                    <th style="text-align:left; padding:10px; background:rgba(47,166,106,0.20);">Alternative</th>
                    <th style="text-align:left; padding:10px; background:rgba(47,166,106,0.20);">C1</th>
                    <th style="text-align:left; padding:10px; background:rgba(47,166,106,0.20);">C2</th>
                    <th style="text-align:left; padding:10px; background:rgba(47,166,106,0.20);">C3</th>
                </tr>
                <tr><td style="padding:10px; background:rgba(255,255,255,0.72);">A1</td><td style="padding:10px;">HV</td><td style="padding:10px;">AAV</td><td style="padding:10px;">VHV</td></tr>
                <tr><td style="padding:10px; background:rgba(255,255,255,0.72);">A2</td><td style="padding:10px;">AV</td><td style="padding:10px;">UAV</td><td style="padding:10px;">HV</td></tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sheet_list(items, skipped: bool = False):
    """Backward-compatible renderer. Kept for older calls, but now uses bright cards."""
    status = "SKIPPED" if skipped else "USED"
    item_class = "sheet-clean-item skipped" if skipped else "sheet-clean-item"
    if not items:
        st.markdown(
            '<div class="sheet-clean-grid"><div class="sheet-clean-item skipped"><div class="sheet-name-wrap"><span class="sheet-dot"></span><span class="sheet-name">No sheets found</span></div><span class="sheet-status">EMPTY</span></div></div>',
            unsafe_allow_html=True,
        )
        return

    cards = []
    for item in items:
        safe_item = html.escape(str(item))
        cards.append(
            f'''
            <div class="{item_class}">
                <div class="sheet-name-wrap">
                    <span class="sheet-dot"></span>
                    <span class="sheet-name" title="{safe_item}">{safe_item}</span>
                </div>
                <span class="sheet-status">{status}</span>
            </div>
            '''
        )
    st.markdown(f'<div class="sheet-clean-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_sheet_summary(expert_items, skipped_items):
    """Render the Excel sheet detection result as one complete, high-contrast HTML block."""
    expert_items = list(expert_items or [])
    skipped_items = list(skipped_items or [])

    def make_cards(items, skipped=False):
        status = "SKIPPED" if skipped else "USED"
        item_class = "sheet-clean-item skipped" if skipped else "sheet-clean-item"
        if not items:
            return '<div class="sheet-clean-item skipped"><div class="sheet-name-wrap"><span class="sheet-dot"></span><span class="sheet-name">No sheets found</span></div><span class="sheet-status">EMPTY</span></div>'
        cards = []
        for item in items:
            safe_item = html.escape(str(item))
            cards.append(
                f'''
                <div class="{item_class}">
                    <div class="sheet-name-wrap">
                        <span class="sheet-dot"></span>
                        <span class="sheet-name" title="{safe_item}">{safe_item}</span>
                    </div>
                    <span class="sheet-status">{status}</span>
                </div>
                '''
            )
        return "".join(cards)

    skipped_html = ""
    if skipped_items:
        skipped_html = f'''
            <div class="sheet-clean-section-label">Skipped non-expert sheets</div>
            <div class="sheet-clean-grid">{make_cards(skipped_items, skipped=True)}</div>
        '''

    html_block = f'''
    <div class="sheet-clean-panel">
        <div class="sheet-clean-header">
            <div>
                <h3 class="sheet-clean-title">Detected Expert Sheets</h3>
                <p class="sheet-clean-subtitle">The workbook was read successfully. Green cards are expert sheets used in the CIF-DEMATEL calculation; gold cards are auxiliary sheets that were skipped.</p>
            </div>
            <div class="sheet-clean-counts">
                <div class="sheet-count-badge"><span class="num">{len(expert_items)}</span><span class="lbl">Used Sheets</span></div>
                <div class="sheet-count-badge skipped"><span class="num">{len(skipped_items)}</span><span class="lbl">Skipped</span></div>
            </div>
        </div>
        <div class="sheet-clean-section-label">Valid expert sheets</div>
        <div class="sheet-clean-grid">{make_cards(expert_items, skipped=False)}</div>
        {skipped_html}
    </div>
    '''
    st.markdown(html_block, unsafe_allow_html=True)



# -----------------------------------------------------------------------------
# CIF-CRITIC scales and linguistic conversion
# -----------------------------------------------------------------------------

CIF_CRITIC_VALUE_SCALE = {
    "CHV": {"rating": 9, "description": "Certainly High Value", "mu": 0.90, "nu": 0.10},
    "VHV": {"rating": 8, "description": "Very High Value", "mu": 0.80, "nu": 0.15},
    "HV":  {"rating": 7, "description": "High Value", "mu": 0.70, "nu": 0.25},
    "AAV": {"rating": 6, "description": "Above Average Value", "mu": 0.60, "nu": 0.35},
    "AV":  {"rating": 5, "description": "Average Value", "mu": 0.50, "nu": 0.45},
    "UAV": {"rating": 4, "description": "Under Average Value", "mu": 0.40, "nu": 0.55},
    "LV":  {"rating": 3, "description": "Low Value", "mu": 0.30, "nu": 0.65},
    "VLV": {"rating": 2, "description": "Very Low Value", "mu": 0.20, "nu": 0.75},
    "CLV": {"rating": 1, "description": "Certainly Low Value", "mu": 0.10, "nu": 0.90},
}

# Expert-weight terms follow the same importance orientation used in the CIF-DEMATEL software.
CIF_EXPERT_WEIGHT_SCALE = {
    "AL": (0.05, 0.85),
    "VL": (0.15, 0.75),
    "L": (0.25, 0.65),
    "ML": (0.35, 0.55),
    "AE": (0.45, 0.45),
    "MH": (0.55, 0.35),
    "H": (0.65, 0.25),
    "VH": (0.75, 0.15),
    "AH": (0.85, 0.05),
}

TERM_DESCRIPTIONS = {
    "AL": "Absolutely Low",
    "VL": "Very Low",
    "L": "Low",
    "ML": "Medium Low",
    "AE": "Average",
    "MH": "Medium High",
    "H": "High",
    "VH": "Very High",
    "AH": "Absolutely High",
}

EXPERT_INFO_SHEET_NAMES = {
    "expert_info", "experts", "expert_weights", "decision_makers", "decision maker weights", "dm_weights",
}

CRITERIA_TYPE_SHEET_NAMES = {
    "criteria_types", "criterion_types", "criteria type", "criterion type", "types", "benefit_cost", "criteria_info",
}

ALTERNATIVE_ALIASES = {"alternative", "alternatives", "option", "options", "challenge", "challenges", "row", "item", "case", "a"}
CRITERION_ALIASES = {"criterion", "criteria", "column", "factor", "attribute", "c"}
VALUE_ALIASES = {"value", "term", "evaluation", "assessment", "score", "rating"}

PERSIAN_DIGIT_MAP = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩٫٬", "01234567890123456789..")


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def is_auxiliary_sheet(sheet_name: str) -> bool:
    lower_name = sheet_name.lower().strip()
    if lower_name in EXPERT_INFO_SHEET_NAMES or lower_name in CRITERIA_TYPE_SHEET_NAMES:
        return False
    keywords = ["scale", "readme", "instruction", "guide", "result", "output", "weights", "parameter"]
    return any(keyword in lower_name for keyword in keywords)


def get_column_by_alias(df: pd.DataFrame, aliases: set) -> Optional[str]:
    for col in df.columns:
        if str(col).strip().lower() in aliases:
            return col
    return None


def hesitation_degree(mu: float, nu: float) -> float:
    return max(0.0, 1.0 - float(mu) - float(nu))


def validate_cif_pair(mu: float, nu: float, label: str = "") -> None:
    eps = 1e-12
    if not (0.0 - eps <= mu <= 1.0 + eps and 0.0 - eps <= nu <= 1.0 + eps):
        raise ValueError(f"Invalid CIF pair {label}: membership and non-membership must be in [0, 1].")
    if mu + nu > 1.0 + eps:
        raise ValueError(f"Invalid CIF pair {label}: mu + nu must be <= 1. Current value: {mu + nu:.6f}")


def standardize_value_term(value) -> str:
    if pd.isna(value):
        raise ValueError("Empty CIF-CRITIC value term found.")
    raw = str(value).strip()
    text = raw.translate(PERSIAN_DIGIT_MAP)
    compact = re.sub(r"\s+", "", text.upper()).replace("-", "").replace("_", "")

    # Numeric ratings 9..1 are accepted: 9=CHV, ..., 1=CLV.
    try:
        numeric_value = float(compact)
        rounded = int(round(numeric_value))
        numeric_map = {9: "CHV", 8: "VHV", 7: "HV", 6: "AAV", 5: "AV", 4: "UAV", 3: "LV", 2: "VLV", 1: "CLV"}
        if rounded in numeric_map:
            return numeric_map[rounded]
    except Exception:
        pass

    aliases = {
        "CHV": "CHV", "CERTAINLYHIGHVALUE": "CHV", "CERTAINLYHIGH": "CHV", "ABSOLUTELYHIGH": "CHV", "AHIGH": "CHV",
        "VHV": "VHV", "VERYHIGHVALUE": "VHV", "VERYHIGH": "VHV",
        "HV": "HV", "HIGHVALUE": "HV", "HIGH": "HV", "H": "HV",
        "AAV": "AAV", "ABOVEAVERAGEVALUE": "AAV", "ABOVEAVERAGE": "AAV",
        "AV": "AV", "AVERAGEVALUE": "AV", "AVERAGE": "AV", "MEDIUM": "AV", "M": "AV",
        "UAV": "UAV", "UNDERAVERAGEVALUE": "UAV", "UNDERAVERAGE": "UAV", "BELOWAVERAGE": "UAV",
        "LV": "LV", "LOWVALUE": "LV", "LOW": "LV", "L": "LV",
        "VLV": "VLV", "VERYLOWVALUE": "VLV", "VERYLOW": "VLV",
        "CLV": "CLV", "CERTAINLYLOWVALUE": "CLV", "CERTAINLYLOW": "CLV", "ABSOLUTELYLOW": "CLV",
    }
    if compact in aliases:
        return aliases[compact]

    persian = raw.replace(" ", "")
    if "کاملازیاد" in persian or "قطعازیاد" in persian or "بسیارزیاد" in persian:
        return "CHV"
    if "خیلیزیاد" in persian:
        return "VHV"
    if "زیاد" in persian or "بالا" in persian:
        return "HV"
    if "بالاترازمتوسط" in persian:
        return "AAV"
    if "متوسط" in persian and "زیر" not in persian and "پایین" not in persian:
        return "AV"
    if "زیرمتوسط" in persian or "پایینترازمتوسط" in persian:
        return "UAV"
    if "خیلیکم" in persian:
        return "VLV"
    if "کاملاکم" in persian or "قطعاکم" in persian:
        return "CLV"
    if "کم" in persian or "پایین" in persian:
        return "LV"

    raise ValueError(
        f"Invalid CIF-CRITIC value term '{value}'. Allowed terms: CHV, VHV, HV, AAV, AV, UAV, LV, VLV, CLV or numeric ratings 9..1."
    )


def value_to_cif_pair(value) -> np.ndarray:
    key = standardize_value_term(value)
    row = CIF_CRITIC_VALUE_SCALE[key]
    mu, nu = float(row["mu"]), float(row["nu"])
    validate_cif_pair(mu, nu, label=key)
    return np.array([mu, nu], dtype=float)


def standardize_weight_term(value) -> str:
    if pd.isna(value):
        raise ValueError("Empty expert weight term found.")
    key = str(value).strip().upper().replace(" ", "")
    if key not in CIF_EXPERT_WEIGHT_SCALE:
        raise ValueError("Invalid expert WeightTerm. Allowed terms: AL, VL, L, ML, AE, MH, H, VH, AH.")
    return key


def standardize_criterion_type(value, default_type: str = "Benefit") -> str:
    if pd.isna(value) or str(value).strip() == "":
        return default_type
    text = str(value).strip().lower().replace(" ", "").replace("-", "_")
    benefit_aliases = {"benefit", "beneficial", "positive", "max", "maximize", "gain", "سود", "مثبت", "بیشینه"}
    cost_aliases = {"cost", "nonbenefit", "negative", "min", "minimize", "expense", "هزینه", "منفی", "کمینه"}
    if text in benefit_aliases or "benefit" in text or "max" in text:
        return "Benefit"
    if text in cost_aliases or "cost" in text or "min" in text:
        return "Cost"
    if "سود" in str(value) or "مثبت" in str(value):
        return "Benefit"
    if "هزینه" in str(value) or "منفی" in str(value):
        return "Cost"
    return default_type


def create_value_scale_dataframe() -> pd.DataFrame:
    rows = []
    for term, row in CIF_CRITIC_VALUE_SCALE.items():
        rows.append({"Term": term, "Rating": row["rating"], "Description": row["description"], "mu": row["mu"], "nu": row["nu"], "pi": hesitation_degree(row["mu"], row["nu"])})
    return pd.DataFrame(rows)


def create_expert_weight_scale_dataframe() -> pd.DataFrame:
    rows = []
    for term, (mu, nu) in CIF_EXPERT_WEIGHT_SCALE.items():
        rows.append({"Term": term, "Description": TERM_DESCRIPTIONS[term], "mu": mu, "nu": nu, "pi": hesitation_degree(mu, nu)})
    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# Excel input parsing
# -----------------------------------------------------------------------------

def extract_wide_decision_matrix(df: pd.DataFrame) -> Tuple[List[str], List[str], np.ndarray]:
    """Extract CIF-CRITIC decision matrix from wide format: Alternative | C1 | C2 | ..."""
    df = clean_dataframe(df)
    if df.shape[1] < 2 or df.shape[0] < 2:
        raise ValueError("Decision matrix sheet must have at least two alternatives and one criterion.")

    alt_col = df.columns[0]
    alternatives = df[alt_col].astype(str).str.strip().tolist()
    criteria = [str(c).strip() for c in df.columns[1:]]
    matrix_df = df.iloc[:, 1:].copy()

    keep_cols = [idx for idx, c in enumerate(criteria) if c and c.lower() != "nan" and not c.lower().startswith("unnamed")]
    if len(keep_cols) != len(criteria):
        matrix_df = matrix_df.iloc[:, keep_cols]
        criteria = [criteria[i] for i in keep_cols]

    if len(criteria) == 0:
        raise ValueError("No criterion columns were found in the expert sheet.")

    term_matrix = np.empty((len(alternatives), len(criteria)), dtype=object)
    for i in range(len(alternatives)):
        for j in range(len(criteria)):
            term_matrix[i, j] = standardize_value_term(matrix_df.iloc[i, j])
    return alternatives, criteria, term_matrix


def extract_long_decision_matrix(df: pd.DataFrame) -> Tuple[List[str], List[str], np.ndarray]:
    """Extract CIF-CRITIC decision matrix from long format: Alternative | Criterion | Value."""
    df = clean_dataframe(df)
    alternative_col = get_column_by_alias(df, ALTERNATIVE_ALIASES)
    criterion_col = get_column_by_alias(df, CRITERION_ALIASES)
    value_col = get_column_by_alias(df, VALUE_ALIASES)
    if alternative_col is None or criterion_col is None or value_col is None:
        raise ValueError("Long format requires Alternative, Criterion and Value columns.")

    alternatives = list(dict.fromkeys(df[alternative_col].astype(str).str.strip().tolist()))
    criteria = list(dict.fromkeys(df[criterion_col].astype(str).str.strip().tolist()))
    ai = {a: i for i, a in enumerate(alternatives)}
    cj = {c: j for j, c in enumerate(criteria)}
    term_matrix = np.empty((len(alternatives), len(criteria)), dtype=object)
    term_matrix[:, :] = "AV"

    for _, row in df.iterrows():
        a = str(row[alternative_col]).strip()
        c = str(row[criterion_col]).strip()
        term_matrix[ai[a], cj[c]] = standardize_value_term(row[value_col])
    return alternatives, criteria, term_matrix


def extract_expert_matrix(df: pd.DataFrame) -> Tuple[List[str], List[str], np.ndarray, np.ndarray]:
    df = clean_dataframe(df)
    if df.empty:
        raise ValueError("Empty expert sheet.")

    try:
        alternatives, criteria, term_matrix = extract_long_decision_matrix(df)
    except Exception:
        alternatives, criteria, term_matrix = extract_wide_decision_matrix(df)

    pair_matrix = np.zeros((len(alternatives), len(criteria), 2), dtype=float)
    for i in range(len(alternatives)):
        for j in range(len(criteria)):
            pair_matrix[i, j, :] = value_to_cif_pair(term_matrix[i, j])
    return alternatives, criteria, term_matrix, pair_matrix


def read_excel_file(uploaded_file) -> Tuple[Dict[str, pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame], List[str]]:
    sheets = pd.read_excel(uploaded_file, sheet_name=None, dtype=object)
    expert_sheets: Dict[str, pd.DataFrame] = {}
    expert_info = None
    criteria_type_info = None
    skipped_sheets: List[str] = []

    for sheet_name, df in sheets.items():
        df = clean_dataframe(df)
        lower_name = sheet_name.lower().strip()
        if lower_name in EXPERT_INFO_SHEET_NAMES:
            expert_info = df
            skipped_sheets.append(sheet_name)
            continue
        if lower_name in CRITERIA_TYPE_SHEET_NAMES:
            criteria_type_info = df
            skipped_sheets.append(sheet_name)
            continue
        if is_auxiliary_sheet(sheet_name):
            skipped_sheets.append(sheet_name)
            continue
        try:
            extract_expert_matrix(df)
            expert_sheets[sheet_name] = df
        except Exception:
            skipped_sheets.append(sheet_name)

    if len(expert_sheets) == 0:
        raise ValueError("No valid CIF-CRITIC expert decision matrix was found. Use one decision matrix per expert sheet.")
    return expert_sheets, expert_info, criteria_type_info, skipped_sheets


def criteria_types_from_info(criteria: List[str], criteria_type_info: Optional[pd.DataFrame], default_type: str) -> pd.DataFrame:
    rows = []
    type_lookup = {}
    if criteria_type_info is not None and not criteria_type_info.empty:
        df = clean_dataframe(criteria_type_info)
        criterion_col = get_column_by_alias(df, {"criterion", "criteria", "factor", "attribute", "name"})
        type_col = get_column_by_alias(df, {"type", "criterion_type", "criteria_type", "benefit_cost", "direction"})
        if criterion_col is not None and type_col is not None:
            for _, row in df.iterrows():
                c = str(row[criterion_col]).strip()
                type_lookup[c] = standardize_criterion_type(row[type_col], default_type=default_type)
    for criterion in criteria:
        rows.append({"Criterion": criterion, "Type": type_lookup.get(criterion, default_type)})
    return pd.DataFrame(rows)


def calculate_expert_weights(expert_names: List[str], expert_info: Optional[pd.DataFrame]) -> pd.DataFrame:
    if expert_info is None or expert_info.empty:
        weights = np.ones(len(expert_names), dtype=float) / len(expert_names)
        return pd.DataFrame(
            {
                "Expert": expert_names,
                "Weight_Source": "Equal",
                "Term_or_Value": "Equal",
                "mu": np.nan,
                "nu": np.nan,
                "pi": np.nan,
                "Raw_Expert_Value": np.nan,
                "Expert_Weight": weights,
            }
        )

    df = clean_dataframe(expert_info)
    expert_col = get_column_by_alias(df, {"expert", "decision_maker", "dm", "name"})
    weight_col = get_column_by_alias(df, {"weight"})
    term_col = get_column_by_alias(df, {"weightterm", "term", "linguistic", "expertise", "level"})

    rows = []
    if expert_col is not None:
        df[expert_col] = df[expert_col].astype(str).str.strip()

    for position, expert in enumerate(expert_names):
        row = None
        if expert_col is not None:
            matches = df[df[expert_col] == expert]
            if not matches.empty:
                row = matches.iloc[0]
        elif position < len(df):
            row = df.iloc[position]

        if row is None:
            rows.append({"Expert": expert, "Weight_Source": "Equal fallback", "Term_or_Value": "Missing", "mu": np.nan, "nu": np.nan, "pi": np.nan, "Raw_Expert_Value": 1.0})
            continue

        if weight_col is not None and not pd.isna(row[weight_col]):
            raw_value = float(str(row[weight_col]).translate(PERSIAN_DIGIT_MAP))
            rows.append({"Expert": expert, "Weight_Source": "Numeric weight", "Term_or_Value": raw_value, "mu": np.nan, "nu": np.nan, "pi": np.nan, "Raw_Expert_Value": raw_value})
        elif term_col is not None and not pd.isna(row[term_col]):
            term = standardize_weight_term(row[term_col])
            mu, nu = CIF_EXPERT_WEIGHT_SCALE[term]
            pi = hesitation_degree(mu, nu)
            denominator = max(1e-12, 1.0 - pi)
            raw_value = mu + pi * (mu / denominator)
            rows.append({"Expert": expert, "Weight_Source": "CIF expertise term", "Term_or_Value": term, "mu": mu, "nu": nu, "pi": pi, "Raw_Expert_Value": raw_value})
        else:
            rows.append({"Expert": expert, "Weight_Source": "Equal fallback", "Term_or_Value": "Missing", "mu": np.nan, "nu": np.nan, "pi": np.nan, "Raw_Expert_Value": 1.0})

    weights_df = pd.DataFrame(rows)
    raw = weights_df["Raw_Expert_Value"].astype(float).clip(lower=0).to_numpy(dtype=float)
    weights = np.ones(len(expert_names), dtype=float) / len(expert_names) if raw.sum() <= 0 else raw / raw.sum()
    weights_df["Expert_Weight"] = weights
    return weights_df


def aggregate_experts(
    expert_sheets: Dict[str, pd.DataFrame], expert_weights: np.ndarray
) -> Tuple[List[str], List[str], Dict[str, pd.DataFrame], np.ndarray, np.ndarray, np.ndarray]:
    term_matrices: Dict[str, pd.DataFrame] = {}
    pair_matrices = []
    reference_alternatives = None
    reference_criteria = None

    for sheet_name, df in expert_sheets.items():
        alternatives, criteria, term_matrix, pair_matrix = extract_expert_matrix(df)
        if reference_alternatives is None:
            reference_alternatives = alternatives
            reference_criteria = criteria
        elif alternatives != reference_alternatives or criteria != reference_criteria:
            raise ValueError(f"Alternatives/criteria in sheet '{sheet_name}' are not consistent with the first expert sheet.")
        pair_matrices.append(pair_matrix)
        term_matrices[sheet_name] = pd.DataFrame(term_matrix, index=alternatives, columns=criteria)

    arrays = np.stack(pair_matrices, axis=0)  # experts x alternatives x criteria x 2
    weights = np.asarray(expert_weights, dtype=float)
    weights = weights / weights.sum()

    mus = arrays[:, :, :, 0]
    nus = arrays[:, :, :, 1]
    # CIF aggregation operator consistent with the existing CIF-DEMATEL file.
    mu_agg = 1.0 - np.prod(np.power(1.0 - mus, weights[:, None, None]), axis=0)
    nu_agg = np.prod(np.power(nus, weights[:, None, None]), axis=0)

    m, n = len(reference_alternatives), len(reference_criteria)
    radius = np.zeros((m, n), dtype=float)
    for i in range(m):
        for j in range(n):
            distances = np.sqrt((mu_agg[i, j] - mus[:, i, j]) ** 2 + (nu_agg[i, j] - nus[:, i, j]) ** 2)
            radius[i, j] = float(np.max(distances))

    aggregated = np.stack([mu_agg, nu_agg, radius], axis=2)  # alternatives x criteria x 3
    return reference_alternatives, reference_criteria, term_matrices, arrays, aggregated, weights


# -----------------------------------------------------------------------------
# CIF-CRITIC calculation
# -----------------------------------------------------------------------------

def calculate_optimistic_pessimistic_matrices(aggregated: np.ndarray) -> Dict[str, np.ndarray]:
    mu = aggregated[:, :, 0]
    nu = aggregated[:, :, 1]
    r = aggregated[:, :, 2]
    matrices = {
        "optimistic_mu": np.clip(mu + r, 0.0, 1.0),
        "optimistic_nu": np.clip(nu - r, 0.0, 1.0),
        "pessimistic_mu": np.clip(mu - r, 0.0, 1.0),
        "pessimistic_nu": np.clip(nu + r, 0.0, 1.0),
    }
    return matrices


def normalize_matrix_by_criteria_type(matrix: np.ndarray, criteria_types: List[str], component_kind: str = "mu") -> np.ndarray:
    X = np.asarray(matrix, dtype=float)
    normalized = np.zeros_like(X, dtype=float)
    for j, ctype in enumerate(criteria_types):
        col = X[:, j]
        min_v = float(np.min(col))
        max_v = float(np.max(col))
        denom = max_v - min_v
        if denom <= 1e-12:
            normalized[:, j] = 0.0
            continue

        # Membership is preference-positive for benefit criteria.
        # Non-membership is preference-negative; therefore its direction is reversed.
        effective_type = ctype
        if component_kind == "nu":
            effective_type = "Cost" if ctype == "Benefit" else "Benefit"

        if effective_type == "Benefit":
            normalized[:, j] = (col - min_v) / denom
        else:
            normalized[:, j] = (max_v - col) / denom
    return np.clip(normalized, 0.0, 1.0)


def correlation_matrix(normalized: np.ndarray) -> np.ndarray:
    X = np.asarray(normalized, dtype=float)
    n = X.shape[1]
    if X.shape[0] <= 1:
        return np.eye(n)
    corr = np.corrcoef(X, rowvar=False)
    if np.isscalar(corr):
        corr = np.array([[1.0]], dtype=float)
    corr = np.nan_to_num(corr, nan=0.0, posinf=0.0, neginf=0.0)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)
    return corr


def calculate_critic_for_normalized(normalized: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    X = np.asarray(normalized, dtype=float)
    corr = correlation_matrix(X)
    sigma = np.std(X, axis=0, ddof=0)
    conflict = np.sum(1.0 - corr, axis=1)
    intensity = sigma * conflict
    return corr, sigma, conflict, intensity


def calculate_cif_critic(
    criteria: List[str],
    aggregated: np.ndarray,
    criteria_types_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, np.ndarray], Dict[str, pd.DataFrame]]:
    criteria_types = criteria_types_df["Type"].tolist()
    op = calculate_optimistic_pessimistic_matrices(aggregated)

    normalized = {
        "norm_optimistic_mu": normalize_matrix_by_criteria_type(op["optimistic_mu"], criteria_types, component_kind="mu"),
        "norm_optimistic_nu": normalize_matrix_by_criteria_type(op["optimistic_nu"], criteria_types, component_kind="nu"),
        "norm_pessimistic_mu": normalize_matrix_by_criteria_type(op["pessimistic_mu"], criteria_types, component_kind="mu"),
        "norm_pessimistic_nu": normalize_matrix_by_criteria_type(op["pessimistic_nu"], criteria_types, component_kind="nu"),
    }

    component_results = {}
    for key, matrix in normalized.items():
        corr, sigma, conflict, intensity = calculate_critic_for_normalized(matrix)
        component_results[key] = {"corr": corr, "sigma": sigma, "conflict": conflict, "intensity": intensity}

    optimistic_intensity = 0.5 * (component_results["norm_optimistic_mu"]["intensity"] + component_results["norm_optimistic_nu"]["intensity"])
    pessimistic_intensity = 0.5 * (component_results["norm_pessimistic_mu"]["intensity"] + component_results["norm_pessimistic_nu"]["intensity"])
    crisp_intensity = 0.5 * (optimistic_intensity + pessimistic_intensity)

    if crisp_intensity.sum() <= 1e-12:
        final_weights = np.ones(len(criteria), dtype=float) / len(criteria)
    else:
        final_weights = crisp_intensity / crisp_intensity.sum()

    result_df = pd.DataFrame(
        {
            "Criterion": criteria,
            "Type": criteria_types,
            "Optimistic_CRITIC_Intensity": optimistic_intensity,
            "Pessimistic_CRITIC_Intensity": pessimistic_intensity,
            "Crisp_CRITIC_Intensity": crisp_intensity,
            "Final_Normalized_Weight": final_weights,
        }
    )
    result_df["Rank"] = result_df["Final_Normalized_Weight"].rank(ascending=False, method="dense").astype(int)
    result_df = result_df.sort_values(["Rank", "Criterion"]).reset_index(drop=True)

    matrices = {**op, **normalized}
    diagnostics = {}
    for key, res in component_results.items():
        diagnostics[f"{key}_correlation"] = pd.DataFrame(res["corr"], index=criteria, columns=criteria)
        diagnostics[f"{key}_sigma_conflict_intensity"] = pd.DataFrame(
            {"Criterion": criteria, "Sigma": res["sigma"], "Conflict": res["conflict"], "Intensity": res["intensity"]}
        )
    return result_df, matrices, diagnostics


def matrix_to_dataframe(matrix: np.ndarray, rows: List[str], cols: List[str]) -> pd.DataFrame:
    return pd.DataFrame(matrix, index=rows, columns=cols)


def aggregated_component_to_dataframe(aggregated: np.ndarray, alternatives: List[str], criteria: List[str], component_index: int) -> pd.DataFrame:
    return pd.DataFrame(aggregated[:, :, component_index], index=alternatives, columns=criteria)


# -----------------------------------------------------------------------------
# Template and output workbooks generated inside Streamlit
# -----------------------------------------------------------------------------

def sample_workbook_data():
    alternatives = [
        "A1 - Challenge 1",
        "A2 - Challenge 2",
        "A3 - Challenge 3",
        "A4 - Challenge 4",
        "A5 - Challenge 5",
    ]
    criteria = [
        "C1 - Economic Impact",
        "C2 - Environmental Impact",
        "C3 - Implementation Cost",
        "C4 - Technological Readiness",
        "C5 - Stakeholder Acceptance",
    ]
    expert_1 = [
        ["HV", "VHV", "UAV", "AAV", "HV"],
        ["AAV", "HV", "LV", "AV", "AAV"],
        ["VHV", "CHV", "AV", "HV", "VHV"],
        ["AV", "AAV", "VLV", "UAV", "AV"],
        ["HV", "AAV", "LV", "VHV", "HV"],
    ]
    expert_2 = [
        ["AAV", "VHV", "LV", "HV", "AAV"],
        ["HV", "HV", "UAV", "AV", "HV"],
        ["VHV", "CHV", "AV", "AAV", "VHV"],
        ["AV", "HV", "VLV", "UAV", "AV"],
        ["AAV", "AAV", "LV", "VHV", "HV"],
    ]
    expert_3 = [
        ["HV", "HV", "UAV", "AAV", "HV"],
        ["AAV", "AAV", "LV", "AV", "AAV"],
        ["CHV", "VHV", "AV", "HV", "VHV"],
        ["AV", "HV", "VLV", "UAV", "AV"],
        ["HV", "AAV", "LV", "HV", "HV"],
    ]
    return alternatives, criteria, expert_1, expert_2, expert_3


def matrix_df_from_terms(alternatives: List[str], criteria: List[str], terms: List[List[str]]) -> pd.DataFrame:
    df = pd.DataFrame(terms, columns=criteria)
    df.insert(0, "Alternative", alternatives)
    return df


def create_template_excel() -> bytes:
    output = BytesIO()
    alternatives, criteria, expert_1, expert_2, expert_3 = sample_workbook_data()
    expert_info = pd.DataFrame({"Expert": ["Expert_1", "Expert_2", "Expert_3"], "WeightTerm": ["AH", "VH", "H"]})
    criteria_types = pd.DataFrame({"Criterion": criteria, "Type": ["Benefit", "Benefit", "Cost", "Benefit", "Benefit"]})
    readme = pd.DataFrame(
        {
            "Guide": [
                "Create one sheet per expert.",
                "Use a decision matrix: first column Alternative, first row criteria.",
                "Allowed value terms: CHV, VHV, HV, AAV, AV, UAV, LV, VLV, CLV. Numeric ratings 9..1 are also accepted.",
                "Optional Expert_Info sheet can use WeightTerm or numeric Weight.",
                "Optional Criteria_Types sheet can define Benefit/Cost criteria.",
            ]
        }
    )
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        matrix_df_from_terms(alternatives, criteria, expert_1).to_excel(writer, sheet_name="Expert_1", index=False)
        matrix_df_from_terms(alternatives, criteria, expert_2).to_excel(writer, sheet_name="Expert_2", index=False)
        matrix_df_from_terms(alternatives, criteria, expert_3).to_excel(writer, sheet_name="Expert_3", index=False)
        expert_info.to_excel(writer, sheet_name="Expert_Info", index=False)
        criteria_types.to_excel(writer, sheet_name="Criteria_Types", index=False)
        create_value_scale_dataframe().to_excel(writer, sheet_name="CIF_CRITIC_Scale", index=False)
        create_expert_weight_scale_dataframe().to_excel(writer, sheet_name="ExpertWeight_Scale", index=False)
        readme.to_excel(writer, sheet_name="README", index=False)
    return output.getvalue()


def create_excel_output(
    expert_sheets: Dict[str, pd.DataFrame],
    skipped_sheets: List[str],
    value_scale_df: pd.DataFrame,
    expert_weight_scale_df: pd.DataFrame,
    expert_weights_df: pd.DataFrame,
    criteria_types_df: pd.DataFrame,
    term_matrices: Dict[str, pd.DataFrame],
    aggregated: np.ndarray,
    matrices: Dict[str, np.ndarray],
    diagnostics: Dict[str, pd.DataFrame],
    result_df: pd.DataFrame,
    alternatives: List[str],
    criteria: List[str],
) -> bytes:
    output = BytesIO()
    params = pd.DataFrame(
        {
            "Parameter": ["Method", "Aggregation", "Optimistic", "Pessimistic", "Normalization", "Correlation", "Final_Weight", "Number_of_Experts", "Number_of_Alternatives", "Number_of_Criteria"],
            "Value": [
                "CIF-CRITIC",
                "CIF weighted aggregation with expert weights; radius=max Euclidean distance",
                "mu+r and nu-r",
                "mu-r and nu+r",
                "Benefit/Cost min-max normalization; non-membership direction is reversed",
                "Pearson correlation across normalized criterion columns",
                "Crisp intensity normalized to sum 1",
                len(expert_sheets),
                len(alternatives),
                len(criteria),
            ],
        }
    )
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        params.to_excel(writer, sheet_name="Parameters", index=False)
        value_scale_df.to_excel(writer, sheet_name="CIF_CRITIC_Scale", index=False)
        expert_weight_scale_df.to_excel(writer, sheet_name="ExpertWeight_Scale", index=False)
        expert_weights_df.to_excel(writer, sheet_name="Expert_Weights", index=False)
        criteria_types_df.to_excel(writer, sheet_name="Criteria_Types", index=False)
        for sheet_name, df in expert_sheets.items():
            df.to_excel(writer, sheet_name=f"Input_{sheet_name[:22]}", index=False)
        for sheet_name, terms_df in term_matrices.items():
            terms_df.to_excel(writer, sheet_name=f"Terms_{sheet_name[:22]}")
        aggregated_component_to_dataframe(aggregated, alternatives, criteria, 0).to_excel(writer, sheet_name="Aggregated_mu")
        aggregated_component_to_dataframe(aggregated, alternatives, criteria, 1).to_excel(writer, sheet_name="Aggregated_nu")
        aggregated_component_to_dataframe(aggregated, alternatives, criteria, 2).to_excel(writer, sheet_name="Radius_r")
        for key, matrix in matrices.items():
            matrix_to_dataframe(matrix, alternatives, criteria).to_excel(writer, sheet_name=key[:31])
        for key, df in diagnostics.items():
            df.to_excel(writer, sheet_name=key[:31], index=not "correlation" in key)
        result_df.to_excel(writer, sheet_name="CIF_CRITIC_Results", index=False)
        pd.DataFrame({"Skipped_sheets": skipped_sheets}).to_excel(writer, sheet_name="Skipped_Sheets", index=False)
    return output.getvalue()


# -----------------------------------------------------------------------------
# Visualizations
# -----------------------------------------------------------------------------

def show_heatmap(df: pd.DataFrame, title: str):
    if PLOTLY_AVAILABLE:
        fig = px.imshow(
            df,
            text_auto=".3f",
            aspect="auto",
            color_continuous_scale=["#FFFDF8", "#F4D58D", "#7BAE7F", "#1E4C78", "#102A43"],
            title=title,
        )
        fig.update_layout(height=520, margin=dict(l=30, r=30, t=60, b=30))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(df.round(6), use_container_width=True)


def show_weights_bar(result_df: pd.DataFrame):
    plot_df = result_df.copy().sort_values("Final_Normalized_Weight", ascending=True)
    plot_df["Label"] = plot_df["Criterion"].map(display_criterion_label)
    if PLOTLY_AVAILABLE:
        fig = px.bar(
            plot_df,
            x="Final_Normalized_Weight",
            y="Label",
            orientation="h",
            text="Final_Normalized_Weight",
            hover_data=["Optimistic_CRITIC_Intensity", "Pessimistic_CRITIC_Intensity", "Crisp_CRITIC_Intensity", "Rank"],
            title="Final CIF-CRITIC Criterion Weights",
            color="Final_Normalized_Weight",
            color_continuous_scale=["#F4D58D", "#7BAE7F", "#1E4C78", "#102A43"],
        )
        fig.update_traces(texttemplate="%{text:.4f}", textposition="outside")
        fig.update_layout(height=max(450, 70 * len(plot_df)), margin=dict(l=30, r=30, t=60, b=30), yaxis_title="", xaxis_title="Weight")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(plot_df.round(6), use_container_width=True)


# -----------------------------------------------------------------------------
# Streamlit app
# -----------------------------------------------------------------------------

def run_app():
    st.set_page_config(
        page_title="CIF-CRITIC | Executive Edition",
        page_icon="C",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_custom_style()
    hamburger_menu()
    hero_section()
    st.markdown('<div class="three-d-divider"></div>', unsafe_allow_html=True)
    header_panels()
    intro_card()

    value_scale_df = create_value_scale_dataframe()
    expert_weight_scale_df = create_expert_weight_scale_dataframe()

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-block">
                <h4>Developer</h4>
                <p><strong>Dr. Saeed Alinejad - Shiraz University, Iran</strong></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        default_type = st.selectbox("Default Criterion Type", ["Benefit", "Cost"], index=0)
        st.markdown(
            """
            <div class="sidebar-block">
                <h4>Allowed CIF-CRITIC Terms</h4>
                <ul>
                    <li>CHV = Certainly High Value = 9</li>
                    <li>VHV = Very High Value = 8</li>
                    <li>HV = High Value = 7</li>
                    <li>AAV = Above Average Value = 6</li>
                    <li>AV = Average Value = 5</li>
                    <li>UAV = Under Average Value = 4</li>
                    <li>LV = Low Value = 3</li>
                    <li>VLV = Very Low Value = 2</li>
                    <li>CLV = Certainly Low Value = 1</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="sidebar-block">
                <h4>Server</h4>
                <p><code>{DISPLAY_URL}</code></p>
                <p>Change DISPLAY_URL at the top of the file if your PC IP is different.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.download_button(
            label="Download Input Template",
            data=create_template_excel(),
            file_name="cif_critic_input_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.markdown('<div id="active-scale"></div>', unsafe_allow_html=True)
    scale_tab, expert_scale_tab = st.tabs(["CIF-CRITIC Value Scale", "Expert Weight Scale"])
    with scale_tab:
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.dataframe(value_scale_df.round(6), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with expert_scale_tab:
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.dataframe(expert_weight_scale_df.round(6), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div id="upload-workbook"></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="upload-zone-card upload-zone-gold-final" style="background:radial-gradient(circle at 9% 12%, rgba(255,255,255,0.45), transparent 28%), radial-gradient(circle at 88% 16%, rgba(255,244,210,0.38), transparent 32%), linear-gradient(135deg,#6F4E00 0%,#9B7208 23%,#D4AF37 52%,#FFD166 74%,#8A6508 100%) !important; border:2px solid rgba(255,244,210,0.98) !important; box-shadow:0 30px 68px rgba(111,78,0,0.38), 0 0 0 5px rgba(255,209,102,0.22), 0 6px 0 rgba(255,255,255,0.28) inset !important;">
            <div class="upload-zone-badge" style="display:inline-block; color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; background:rgba(16,42,67,0.36) !important; border:1px solid rgba(255,255,255,0.58) !important; padding:8px 16px !important; border-radius:999px !important; font-weight:950 !important; letter-spacing:0.9px !important; text-transform:uppercase !important; text-shadow:0 2px 10px rgba(0,0,0,0.35) !important;">Upload Zone</div>
            <div class="upload-zone-title" style="color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; opacity:1 !important; font-size:28px !important; font-weight:950 !important; line-height:1.25 !important; margin:30px 0 26px 0 !important; text-shadow:0 4px 16px rgba(0,0,0,0.68) !important;">Upload Your CIF-CRITIC Excel Workbook</div>
            <div id="force-upload-desc-white" class="upload-zone-description" style="margin-top:18px !important; color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; opacity:1 !important; font-size:16px !important; font-weight:900 !important; line-height:1.9 !important; text-shadow:0 4px 18px rgba(0,0,0,0.78) !important; background:rgba(16,42,67,0.22) !important; border:1px solid rgba(255,255,255,0.24) !important; border-radius:14px !important; padding:12px 14px !important;"><span style="color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; opacity:1 !important; font-weight:900 !important; text-shadow:0 4px 18px rgba(0,0,0,0.78) !important;">Load expert decision matrices. The app will calculate aggregated CIF matrices, optimistic/pessimistic matrices, normalized matrices, correlation matrices, CRITIC intensities, and final criterion weights.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Upload CIF-CRITIC Excel workbook", type=["xlsx"])

    if uploaded_file is None:
        st.info("Download the template from the sidebar, fill your expert decision matrices, then upload the workbook here.")
        return

    try:
        expert_sheets, expert_info, criteria_type_info, skipped_sheets = read_excel_file(uploaded_file)
        expert_names = list(expert_sheets.keys())
        expert_weights_df = calculate_expert_weights(expert_names, expert_info)
        alternatives, criteria, term_matrices, arrays, aggregated, normalized_weights = aggregate_experts(
            expert_sheets,
            expert_weights_df["Expert_Weight"].to_numpy(dtype=float),
        )
        criteria_types_df = criteria_types_from_info(criteria, criteria_type_info, default_type=default_type)
        result_df, matrices, diagnostics = calculate_cif_critic(criteria, aggregated, criteria_types_df)

        display_alternatives = display_criterion_labels(alternatives)
        display_criteria = display_criterion_labels(criteria)
        top_row = result_df.sort_values("Rank").iloc[0]

        st.markdown('<div id="results-dashboard"></div>', unsafe_allow_html=True)
        st.success("CIF-CRITIC calculations completed successfully.")
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Valid Expert Sheets", len(expert_sheets))
        with c2:
            st.metric("Alternatives", len(alternatives))
        with c3:
            st.metric("Criteria", len(criteria))
        with c4:
            st.metric("Top Criterion", display_criterion_label(top_row["Criterion"]))
        with c5:
            st.metric("Top Weight", f"{top_row['Final_Normalized_Weight']:.4f}")

        overview_tab, matrix_tab, visual_tab, export_tab = st.tabs(["Overview", "Matrices", "Visual Maps", "Export"])

        with overview_tab:
            render_sheet_summary(expert_names, skipped_sheets)

            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader("Expert Weights")
            st.dataframe(expert_weights_df.round(6), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader("Criteria Types")
            st.dataframe(criteria_types_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader("Final CIF-CRITIC Results")
            display_result = result_df.copy()
            display_result["Criterion"] = display_result["Criterion"].map(display_criterion_label)
            st.dataframe(display_result.round(6), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with matrix_tab:
            matrix_options = {
                "Aggregated Membership Matrix (mu)": aggregated[:, :, 0],
                "Aggregated Non-membership Matrix (nu)": aggregated[:, :, 1],
                "Circular Radius Matrix (r)": aggregated[:, :, 2],
                "Optimistic Membership Matrix (mu+r)": matrices["optimistic_mu"],
                "Optimistic Non-membership Matrix (nu-r)": matrices["optimistic_nu"],
                "Pessimistic Membership Matrix (mu-r)": matrices["pessimistic_mu"],
                "Pessimistic Non-membership Matrix (nu+r)": matrices["pessimistic_nu"],
                "Normalized Optimistic Membership": matrices["norm_optimistic_mu"],
                "Normalized Optimistic Non-membership": matrices["norm_optimistic_nu"],
                "Normalized Pessimistic Membership": matrices["norm_pessimistic_mu"],
                "Normalized Pessimistic Non-membership": matrices["norm_pessimistic_nu"],
            }
            for title, matrix in matrix_options.items():
                st.markdown('<div class="table-card">', unsafe_allow_html=True)
                st.subheader(title)
                st.dataframe(matrix_to_dataframe(matrix, display_alternatives, display_criteria).round(6), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with visual_tab:
            show_weights_bar(result_df)
            show_heatmap(matrix_to_dataframe(matrices["norm_optimistic_mu"], display_alternatives, display_criteria), "Normalized Optimistic Membership Heatmap")
            show_heatmap(diagnostics["norm_optimistic_mu_correlation"].rename(index=dict(zip(criteria, display_criteria)), columns=dict(zip(criteria, display_criteria))), "Correlation Matrix - Normalized Optimistic Membership")

        with export_tab:
            excel_output = create_excel_output(
                expert_sheets=expert_sheets,
                skipped_sheets=skipped_sheets,
                value_scale_df=value_scale_df,
                expert_weight_scale_df=expert_weight_scale_df,
                expert_weights_df=expert_weights_df,
                criteria_types_df=criteria_types_df,
                term_matrices=term_matrices,
                aggregated=aggregated,
                matrices=matrices,
                diagnostics=diagnostics,
                result_df=result_df,
                alternatives=alternatives,
                criteria=criteria,
            )
            st.markdown('<div id="download-results"></div>', unsafe_allow_html=True)
            st.download_button(
                label="Download Excel Results",
                data=excel_output,
                file_name="cif_critic_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            st.caption(f"Final weights sum = {result_df['Final_Normalized_Weight'].sum():.6f}")

    except Exception as error:
        st.error(f"Error: {error}")

    st.markdown(
        """
        <div class="footer-note">
            Executive CIF-CRITIC Interface - Designed for professional circular intuitionistic fuzzy objective weighting analytics.
        </div>
        """,
        unsafe_allow_html=True,
    )


def is_running_inside_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


if __name__ == "__main__" and not is_running_inside_streamlit() and os.environ.get("RUNNING_CIF_CRITIC_STREAMLIT") != "1":
    import streamlit.web.cli as stcli
    os.environ["RUNNING_CIF_CRITIC_STREAMLIT"] = "1"
    sys.argv = [
        "streamlit",
        "run",
        sys.argv[0],
        "--server.port",
        str(PORT),
        "--server.address",
        SERVER_ADDRESS,
    ]
    sys.exit(stcli.main())

if is_running_inside_streamlit():
    run_app()
