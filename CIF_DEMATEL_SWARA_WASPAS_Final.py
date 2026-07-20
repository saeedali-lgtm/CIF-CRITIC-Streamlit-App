# -*- coding: utf-8 -*-
"""
CIF Decision Analytics Suite
============================
A single three-tab Streamlit application for:
1. Circular Intuitionistic Fuzzy DEMATEL
2. Circular Intuitionistic Fuzzy SWARA
3. Circular Intuitionistic Fuzzy WASPAS

Each module accepts its own Excel workbook and performs calculations independently.
The visual shell follows the emerald, forest-green, and warm-gold CIF-WASPAS design.
"""
from __future__ import annotations


# ============================== DEMATEL MODULE ==============================
import os
os.environ.setdefault('STREAMLIT_THEME_BASE', 'light')
os.environ.setdefault('STREAMLIT_BROWSER_GATHER_USAGE_STATS', 'false')
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
    dematel_PLOTLY_AVAILABLE = True
except Exception:
    dematel_PLOTLY_AVAILABLE = False
dematel_PORT = 8802
dematel_SERVER_ADDRESS = '0.0.0.0'
dematel_DISPLAY_URL = 'http://192.168.0.100:8802/'
dematel_PERSIAN_ARABIC_TEXT_PATTERN = re.compile('[\\u0600-\\u06FF]')

def dematel_display_criterion_label(value) -> str:
    """Return a clean English-safe label for charts/cards while preserving raw labels in calculations."""
    text = str(value).strip()
    if not dematel_PERSIAN_ARABIC_TEXT_PATTERN.search(text):
        return text
    parts = re.split('\\s*[-–—|:]\\s*', text, maxsplit=1)
    if parts and parts[0].strip() and (not dematel_PERSIAN_ARABIC_TEXT_PATTERN.search(parts[0])):
        return parts[0].strip()
    latin_only = re.sub('[\\u0600-\\u06FF\\u200c\\u200f\\u202a-\\u202e]+', '', text)
    latin_only = re.sub('\\s+', ' ', latin_only).strip(' -–—|:')
    return latin_only if latin_only else 'Criterion'

def dematel_display_criterion_labels(values) -> List[str]:
    return [dematel_display_criterion_label(v) for v in values]

def dematel_apply_custom_style():
    st.markdown('\n        <style>\n        @import url(\'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap\');\n\n        :root {\n            /* User-selected palette: true soft emerald green + deep royal blue. */\n            --cif-emerald: #2FA66A;\n            --cif-emerald-dark: #247A50;\n            --cif-forest: #164A34;\n            --cif-lapis: #123B2A;\n            --cif-ink: #102B20;\n            --cif-text: #102018;\n            --cif-muted: #496356;\n            --cif-cream: #FBFFFC;\n            --cif-card: rgba(255, 255, 255, 0.94);\n            --cif-border: rgba(39, 138, 89, 0.20);\n            --cif-gold: #C5962D;\n        }\n\n        html, body, [class*="css"] {\n            font-family: \'Inter\', \'Segoe UI\', sans-serif;\n        }\n\n        .stApp {\n            background:\n                radial-gradient(circle at 8% 7%, rgba(47, 166, 106, 0.22), transparent 26%),\n                radial-gradient(circle at 92% 10%, rgba(47, 166, 106, 0.20), transparent 28%),\n                radial-gradient(circle at 76% 92%, rgba(197, 150, 45, 0.11), transparent 28%),\n                linear-gradient(145deg, #FBFFFC 0%, #F6FFF9 32%, #F1FFF6 68%, #ffffff 100%);\n            color: var(--cif-text);\n        }\n\n        .block-container {\n            padding-top: 1.45rem;\n            padding-bottom: 2rem;\n            max-width: 1480px;\n        }\n\n        /* General readable text: fixes white/low-contrast native Streamlit headings and labels. */\n        h1, h2, h3, h4, h5, h6,\n        .stMarkdown, .stMarkdown p, .stMarkdown li,\n        .stCaptionContainer, .stText, label,\n        div[data-testid="stWidgetLabel"], div[data-testid="stWidgetLabel"] p,\n        div[data-testid="stMarkdownContainer"] p,\n        div[data-testid="stMarkdownContainer"] li,\n        div[data-testid="stMetricLabel"], div[data-testid="stMetricDelta"],\n        .caption-note, .muted {\n            color: var(--cif-text) !important;\n        }\n\n        h1, h2, h3, h4 {\n            color: var(--cif-ink) !important;\n            letter-spacing: 0.15px;\n        }\n\n        p, li, td, th, span {\n            text-rendering: optimizeLegibility;\n        }\n\n        /* Streamlit\'s native sidebar toggle is turned into a cleaner hamburger-style control. */\n        [data-testid="collapsedControl"],\n        [data-testid="stSidebarCollapsedControl"],\n        [data-testid="stSidebarCollapseButton"] {\n            border-radius: 18px !important;\n            background: linear-gradient(135deg, var(--cif-emerald-dark), var(--cif-emerald) 42%, var(--cif-forest)) !important;\n            box-shadow: 0 18px 38px rgba(39, 138, 89, 0.24), 0 2px 0 rgba(255,255,255,0.34) inset !important;\n            border: 1px solid rgba(255, 255, 255, 0.72) !important;\n        }\n\n        [data-testid="collapsedControl"] button,\n        [data-testid="stSidebarCollapsedControl"] button,\n        [data-testid="stSidebarCollapseButton"] button,\n        [data-testid="collapsedControl"] svg,\n        [data-testid="stSidebarCollapsedControl"] svg,\n        [data-testid="stSidebarCollapseButton"] svg {\n            color: #ffffff !important;\n            stroke-width: 2.8px !important;\n        }\n\n        .hamburger-shell {\n            position: sticky;\n            top: 0.75rem;\n            z-index: 999;\n            max-width: 430px;\n            margin: 0 0 16px auto;\n            border-radius: 22px;\n            background:\n                radial-gradient(circle at 10% 10%, rgba(255,255,255,0.45), transparent 28%),\n                linear-gradient(135deg, var(--cif-emerald-dark) 0%, var(--cif-emerald) 42%, var(--cif-forest) 100%);\n            border: 1px solid rgba(255, 255, 255, 0.62);\n            box-shadow: 0 22px 46px rgba(39, 138, 89, 0.22), 0 4px 0 rgba(255,255,255,0.25) inset;\n            backdrop-filter: blur(16px);\n            overflow: hidden;\n        }\n\n        .hamburger-shell summary {\n            list-style: none;\n            cursor: pointer;\n            user-select: none;\n            padding: 13px 16px;\n            display: flex;\n            align-items: center;\n            gap: 12px;\n        }\n\n        .hamburger-shell summary::-webkit-details-marker { display: none; }\n\n        .hamburger-icon {\n            width: 42px;\n            height: 42px;\n            display: inline-flex;\n            flex-direction: column;\n            justify-content: center;\n            align-items: center;\n            gap: 5px;\n            border-radius: 15px;\n            background: rgba(255, 255, 255, 0.20);\n            box-shadow: 0 9px 20px rgba(7, 22, 63, 0.16), 0 2px 0 rgba(255,255,255,0.28) inset;\n            transition: all 0.25s ease;\n        }\n\n        .hamburger-icon span {\n            width: 20px;\n            height: 2.5px;\n            border-radius: 999px;\n            background: #ffffff;\n            box-shadow: 0 1px 4px rgba(7,22,63,0.18);\n            transition: all 0.25s ease;\n        }\n\n        .hamburger-shell[open] .hamburger-icon span:nth-child(1) { transform: translateY(7.5px) rotate(45deg); }\n        .hamburger-shell[open] .hamburger-icon span:nth-child(2) { opacity: 0; transform: scaleX(0.2); }\n        .hamburger-shell[open] .hamburger-icon span:nth-child(3) { transform: translateY(-7.5px) rotate(-45deg); }\n\n        .hamburger-title {\n            color: #ffffff !important;\n            font-size: 15px;\n            font-weight: 950;\n            letter-spacing: 0.4px;\n            text-shadow: 0 2px 8px rgba(7, 22, 63, 0.28);\n        }\n\n        .hamburger-pill {\n            margin-left: auto;\n            padding: 7px 10px;\n            border-radius: 999px;\n            color: #ffffff !important;\n            background: rgba(255,255,255,0.17);\n            border: 1px solid rgba(255,255,255,0.30);\n            font-size: 11px;\n            font-weight: 900;\n            text-transform: uppercase;\n            letter-spacing: 0.9px;\n        }\n\n        .hamburger-links {\n            display: grid;\n            grid-template-columns: repeat(2, minmax(0, 1fr));\n            gap: 9px;\n            padding: 0 14px 14px 14px;\n        }\n\n        .hamburger-links a {\n            text-decoration: none !important;\n            color: var(--cif-ink) !important;\n            font-size: 13px;\n            font-weight: 900;\n            padding: 10px 12px;\n            border-radius: 14px;\n            background: rgba(255, 255, 255, 0.92);\n            border: 1px solid rgba(255,255,255,0.70);\n            box-shadow: 0 8px 18px rgba(7,22,63,0.11);\n            transition: all 0.22s ease;\n        }\n\n        .hamburger-links a:hover {\n            transform: translateY(-2px);\n            color: var(--cif-emerald-dark) !important;\n            background: #ffffff;\n            box-shadow: 0 12px 24px rgba(7,22,63,0.15);\n        }\n\n        @media (max-width: 760px) {\n            .hamburger-shell {\n                margin-left: 0;\n                max-width: 100%;\n            }\n            .hamburger-links { grid-template-columns: 1fr; }\n            .hero-title { font-size: 34px !important; }\n        }\n\n        .hero-card {\n            position: relative;\n            overflow: hidden;\n            border-radius: 30px;\n            padding: 34px 34px 28px 34px;\n            margin-bottom: 20px;\n            background:\n                radial-gradient(circle at 8% 10%, rgba(255,255,255,0.78), transparent 25%),\n                radial-gradient(circle at 92% 16%, rgba(47,166,106,0.22), transparent 30%),\n                linear-gradient(135deg, #ffffff 0%, #F4FFF8 34%, #D6F5E2 72%, #FFF9EF 100%);\n            border: 1px solid rgba(39, 138, 89, 0.22);\n            box-shadow:\n                0 30px 72px rgba(39, 138, 89, 0.16),\n                0 10px 24px rgba(255, 255, 255, 0.94) inset,\n                0 -14px 28px rgba(18, 74, 52, 0.07) inset;\n        }\n\n        .hero-card::before {\n            content: "";\n            position: absolute;\n            inset: 0;\n            background: linear-gradient(120deg, transparent 0%, rgba(255,255,255,0.72) 38%, transparent 74%);\n            transform: translateX(-100%);\n            animation: shine 7s linear infinite;\n            pointer-events: none;\n        }\n\n        @keyframes shine { 100% { transform: translateX(160%); } }\n\n        .hero-topline {\n            display: inline-block;\n            padding: 8px 14px;\n            border-radius: 999px;\n            background: rgba(47, 166, 106, 0.13);\n            border: 1px solid rgba(39, 138, 89, 0.25);\n            color: var(--cif-emerald-dark) !important;\n            font-size: 12px;\n            font-weight: 900;\n            letter-spacing: 1.35px;\n            text-transform: uppercase;\n            margin-bottom: 16px;\n            box-shadow: 0 8px 20px rgba(39, 138, 89, 0.10), 0 2px 0 rgba(255,255,255,0.90) inset;\n        }\n\n        .hero-title {\n            font-size: 46px;\n            font-weight: 900;\n            line-height: 1.05;\n            margin: 0 0 10px 0;\n            color: var(--cif-ink) !important;\n            text-shadow: 0 2px 0 rgba(255,255,255,0.84);\n        }\n\n        .hero-subtitle {\n            font-size: 16px;\n            line-height: 1.72;\n            color: var(--cif-lapis) !important;\n            max-width: 1040px;\n            margin-bottom: 0;\n            font-weight: 550;\n        }\n\n        .three-d-divider {\n            height: 10px;\n            margin: 4px 0 18px 0;\n            border-radius: 999px;\n            background: linear-gradient(90deg, rgba(47,166,106,0.05), rgba(47,166,106,0.54), rgba(18,74,52,0.36), rgba(197,150,45,0.22), rgba(47,166,106,0.05));\n            box-shadow: 0 10px 20px rgba(39,138,89,0.11), 0 2px 0 rgba(255,255,255,0.86) inset;\n        }\n\n        .info-grid {\n            display: grid;\n            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));\n            gap: 16px;\n            margin-bottom: 18px;\n        }\n\n        .mini-card, .glass-panel, .table-card, .brand-card, .sidebar-block {\n            position: relative;\n            overflow: hidden;\n            border-radius: 22px;\n            background:\n                linear-gradient(145deg, rgba(255,255,255,0.97), rgba(246,255,249,0.88));\n            border: 1px solid var(--cif-border);\n            box-shadow: 0 18px 44px rgba(39, 138, 89, 0.11), 0 3px 0 rgba(255,255,255,0.95) inset;\n            backdrop-filter: blur(12px);\n        }\n\n        .mini-card { padding: 18px 18px 16px 18px; }\n        .glass-panel { padding: 20px 22px; margin-bottom: 18px; }\n        .table-card { padding: 13px 15px 17px 15px; margin-bottom: 18px; }\n        .brand-card { padding: 16px 18px; margin-bottom: 18px; }\n        .sidebar-block { padding: 14px 16px; margin-bottom: 15px; }\n\n        .mini-card:hover, .glass-panel:hover, .table-card:hover, .brand-card:hover, .sidebar-block:hover {\n            transform: translateY(-3px) rotateX(0.8deg);\n            box-shadow: 0 26px 58px rgba(39, 138, 89, 0.17), 0 3px 0 rgba(255,255,255,0.95) inset;\n        }\n\n        .mini-card h4, .sidebar-block h4 {\n            font-size: 14px;\n            color: var(--cif-emerald-dark) !important;\n            margin-bottom: 8px;\n            text-transform: uppercase;\n            letter-spacing: 0.8px;\n        }\n\n        .mini-card p, .mini-card li, .sidebar-block p, .sidebar-block li, .caption-note, .muted {\n            color: var(--cif-muted) !important;\n            font-size: 14px;\n            line-height: 1.74;\n            margin-bottom: 0;\n        }\n\n        .mini-card strong, .brand-card strong, .sidebar-block strong {\n            color: var(--cif-lapis) !important;\n        }\n\n        .developer-card {\n            background:\n                radial-gradient(circle at 9% 12%, rgba(255,255,255,0.72), transparent 30%),\n                linear-gradient(135deg, #FFF7DD 0%, #EEF9E7 42%, #DDF4E5 100%) !important;\n            border: 1px solid rgba(197, 150, 45, 0.34) !important;\n            box-shadow:\n                0 22px 52px rgba(128, 95, 24, 0.13),\n                0 8px 24px rgba(47, 166, 106, 0.11),\n                0 3px 0 rgba(255,255,255,0.96) inset !important;\n        }\n\n        .developer-card::before {\n            content: "";\n            position: absolute;\n            inset: 0 auto 0 0;\n            width: 7px;\n            background: linear-gradient(180deg, #C5962D 0%, #2FA66A 54%, #1F6F49 100%);\n            box-shadow: 6px 0 18px rgba(197, 150, 45, 0.18);\n        }\n\n        .developer-card h4 {\n            color: #7A5814 !important;\n        }\n\n        .developer-card strong {\n            color: #1F6F49 !important;\n            font-weight: 950 !important;\n        }\n\n        .developer-card p,\n        .developer-card li {\n            color: #3F513B !important;\n        }\n\n        .section-label {\n            display: inline-block;\n            margin-bottom: 12px;\n            padding: 6px 12px;\n            border-radius: 999px;\n            background: rgba(47, 166, 106, 0.13);\n            color: var(--cif-emerald-dark) !important;\n            border: 1px solid rgba(39, 138, 89, 0.22);\n            font-size: 12px;\n            font-weight: 900;\n            letter-spacing: 1px;\n            text-transform: uppercase;\n        }\n\n        section[data-testid="stSidebar"] {\n            background:\n                radial-gradient(circle at 12% 5%, rgba(47,166,106,0.12), transparent 28%),\n                linear-gradient(180deg, #ffffff 0%, #F6FFF9 48%, #F1FFF6 100%);\n            border-right: 1px solid rgba(39, 138, 89, 0.16);\n            box-shadow: 14px 0 36px rgba(39, 138, 89, 0.08);\n        }\n\n        section[data-testid="stSidebar"] * {\n            color: var(--cif-text) !important;\n        }\n\n        .brand-card .name {\n            color: var(--cif-lapis) !important;\n            font-size: 20px;\n            font-weight: 900;\n            margin-top: 6px;\n            margin-bottom: 8px;\n        }\n\n        div[data-testid="metric-container"] {\n            background: linear-gradient(145deg, rgba(255,255,255,0.97), rgba(234,251,241,0.92));\n            border: 1px solid rgba(39, 138, 89, 0.20);\n            border-radius: 18px;\n            padding: 15px;\n            box-shadow: 0 14px 32px rgba(39, 138, 89, 0.12), 0 2px 0 rgba(255,255,255,0.95) inset;\n        }\n\n        div[data-testid="stMetricValue"] { color: var(--cif-emerald-dark) !important; font-weight: 900; }\n        div[data-testid="stMetricLabel"] { color: var(--cif-lapis) !important; font-weight: 800; }\n\n        div[data-testid="stDataFrame"] {\n            background: rgba(255,255,255,0.92);\n            border: 1px solid rgba(39, 138, 89, 0.16);\n            border-radius: 18px;\n            box-shadow: 0 16px 38px rgba(39, 138, 89, 0.10);\n        }\n\n        .stTabs [data-baseweb="tab-list"] {\n            gap: 8px;\n            background: rgba(47, 166, 106, 0.08);\n            padding: 8px;\n            border-radius: 18px;\n            border: 1px solid rgba(39, 138, 89, 0.12);\n            box-shadow: 0 8px 18px rgba(39, 138, 89, 0.07) inset;\n        }\n\n        .stTabs [data-baseweb="tab"] {\n            height: 42px;\n            border-radius: 12px;\n            background: rgba(255,255,255,0.92);\n            color: var(--cif-lapis) !important;\n            font-weight: 900;\n            padding: 0 18px;\n            box-shadow: 0 6px 16px rgba(39, 138, 89, 0.08);\n        }\n\n        .stTabs [aria-selected="true"] {\n            background: linear-gradient(135deg, var(--cif-emerald-dark) 0%, var(--cif-emerald) 42%, var(--cif-forest) 100%) !important;\n            color: #ffffff !important;\n            box-shadow: 0 10px 28px rgba(39, 138, 89, 0.24), 0 2px 0 rgba(255,255,255,0.30) inset;\n        }\n\n        .stTabs [aria-selected="true"] p,\n        .stTabs [aria-selected="true"] span,\n        .stButton > button *, .stDownloadButton > button * {\n            color: #ffffff !important;\n        }\n\n        .stButton > button, .stDownloadButton > button {\n            background: linear-gradient(135deg, var(--cif-emerald-dark) 0%, var(--cif-emerald) 42%, var(--cif-forest) 100%);\n            color: #ffffff !important;\n            border: 1px solid rgba(255,255,255,0.62);\n            border-radius: 16px;\n            font-weight: 900;\n            padding: 0.78rem 1.15rem;\n            box-shadow: 0 16px 30px rgba(39, 138, 89, 0.22), 0 3px 0 rgba(255,255,255,0.34) inset;\n            transition: all 0.25s ease;\n        }\n\n        .stButton > button:hover, .stDownloadButton > button:hover {\n            transform: translateY(-2px);\n            box-shadow: 0 20px 40px rgba(39, 138, 89, 0.30), 0 3px 0 rgba(255,255,255,0.34) inset;\n        }\n\n        .upload-zone-card {\n            position: relative;\n            overflow: hidden;\n            margin: 8px 0 14px 0;\n            padding: 22px 24px;\n            border-radius: 26px;\n            background:\n                radial-gradient(circle at 8% 16%, rgba(255,255,255,0.78), transparent 26%),\n                linear-gradient(135deg, #ffffff 0%, #E5F8EE 42%, #D6F5E2 100%);\n            border: 1px solid rgba(39,138,89,0.28);\n            box-shadow: 0 24px 46px rgba(39, 138, 89, 0.16), 0 5px 0 rgba(255,255,255,0.88) inset;\n        }\n\n        .upload-zone-card h3 {\n            color: var(--cif-ink) !important;\n            font-size: 23px;\n            font-weight: 900;\n            margin: 0 0 7px 0;\n            text-shadow: 0 2px 0 rgba(255,255,255,0.75);\n        }\n\n        .upload-zone-card p {\n            color: var(--cif-lapis) !important;\n            font-size: 14px;\n            line-height: 1.65;\n            margin: 0;\n            font-weight: 650;\n        }\n\n        .upload-zone-badge {\n            display: inline-block;\n            margin-bottom: 10px;\n            padding: 6px 12px;\n            border-radius: 999px;\n            background: rgba(255,255,255,0.72);\n            color: var(--cif-emerald-dark) !important;\n            border: 1px solid rgba(255,255,255,0.82);\n            font-size: 12px;\n            font-weight: 900;\n            letter-spacing: 1px;\n            text-transform: uppercase;\n        }\n\n        .stFileUploader, div[data-testid="stFileUploader"] {\n            background: linear-gradient(145deg, rgba(255,255,255,0.97), rgba(214,245,226,0.82));\n            border: 2px dashed rgba(39, 138, 89, 0.58);\n            padding: 14px;\n            border-radius: 22px;\n            box-shadow: 0 18px 36px rgba(39, 138, 89, 0.14), 0 10px 26px rgba(18, 74, 52, 0.07) inset;\n        }\n\n        .footer-note {\n            margin-top: 28px;\n            color: var(--cif-muted) !important;\n            font-size: 13px;\n            text-align: center;\n            opacity: 0.95;\n        }\n\n        code {\n            color: var(--cif-lapis) !important;\n            background: rgba(47, 166, 106, 0.10) !important;\n            border-radius: 8px;\n            padding: 2px 5px;\n        }\n\n\n        /* ------------------------------------------------------------------\n           Strong green soft emerald green override requested by user.\n           Main visible color = #2FA66A; soft emerald, not neon and not blue/violet.\n        ------------------------------------------------------------------ */\n        :root {\n            --cif-emerald: #2FA66A;\n            --cif-emerald-dark: #1F6F49;\n            --cif-emerald-deep: #164A34;\n            --cif-emerald-soft: #EAFBF1;\n            --cif-emerald-card: #F6FFF9;\n            --cif-ink: #123B2A;\n            --cif-text: #11251B;\n            --cif-muted: #496356;\n            --cif-border: rgba(47, 166, 106, 0.34);\n            --cif-gold: #C5962D;\n        }\n\n        .stApp {\n            background:\n                radial-gradient(circle at 8% 8%, rgba(47,166,106,0.34), transparent 27%),\n                radial-gradient(circle at 92% 8%, rgba(31,111,73,0.22), transparent 30%),\n                radial-gradient(circle at 78% 92%, rgba(47,166,106,0.20), transparent 32%),\n                linear-gradient(145deg, #FAFFFC 0%, #EAFBF1 38%, #F6FFF9 70%, #FFFFFF 100%) !important;\n            color: var(--cif-text) !important;\n        }\n\n        .hero-card {\n            background:\n                radial-gradient(circle at 10% 8%, rgba(255,255,255,0.40), transparent 28%),\n                linear-gradient(135deg, #2FA66A 0%, #278A59 48%, #1F6F49 100%) !important;\n            border: 1px solid rgba(255,255,255,0.58) !important;\n            box-shadow: 0 32px 76px rgba(31, 111, 73, 0.28), 0 8px 0 rgba(255,255,255,0.18) inset !important;\n        }\n\n        .hero-title,\n        .hero-subtitle,\n        .hero-topline {\n            color: #ffffff !important;\n            text-shadow: 0 2px 12px rgba(18, 59, 42, 0.32) !important;\n        }\n\n        .hero-topline {\n            background: rgba(255,255,255,0.18) !important;\n            border: 1px solid rgba(255,255,255,0.38) !important;\n            box-shadow: 0 8px 22px rgba(18,74,52,0.18), 0 2px 0 rgba(255,255,255,0.18) inset !important;\n        }\n\n        .mini-card, .glass-panel, .table-card, .brand-card, .sidebar-block,\n        div[data-testid="metric-container"] {\n            background: linear-gradient(145deg, #ffffff 0%, #F6FFF9 58%, #EAFBF1 100%) !important;\n            border: 1px solid rgba(47, 166, 106, 0.34) !important;\n            box-shadow: 0 18px 44px rgba(31, 111, 73, 0.13), 0 3px 0 rgba(255,255,255,0.96) inset !important;\n        }\n\n        .developer-card {\n            background:\n                radial-gradient(circle at 9% 12%, rgba(255,255,255,0.72), transparent 30%),\n                linear-gradient(135deg, #FFF7DD 0%, #EEF9E7 42%, #DDF4E5 100%) !important;\n            border: 1px solid rgba(197, 150, 45, 0.36) !important;\n            box-shadow:\n                0 22px 52px rgba(128, 95, 24, 0.13),\n                0 8px 24px rgba(47, 166, 106, 0.11),\n                0 3px 0 rgba(255,255,255,0.96) inset !important;\n        }\n\n        .developer-card::before {\n            content: "";\n            position: absolute;\n            inset: 0 auto 0 0;\n            width: 7px;\n            background: linear-gradient(180deg, #C5962D 0%, #2FA66A 54%, #1F6F49 100%);\n            box-shadow: 6px 0 18px rgba(197, 150, 45, 0.18);\n        }\n\n        .developer-card h4 {\n            color: #7A5814 !important;\n        }\n\n        .developer-card strong {\n            color: #1F6F49 !important;\n            font-weight: 950 !important;\n        }\n\n        .developer-card p,\n        .developer-card li {\n            color: #3F513B !important;\n        }\n\n        h1, h2, h3, h4, h5, h6,\n        .mini-card h4, .sidebar-block h4,\n        .brand-card .name,\n        div[data-testid="stMetricValue"],\n        div[data-testid="stMetricLabel"] {\n            color: #123B2A !important;\n        }\n\n        .section-label,\n        .upload-zone-badge {\n            color: #123B2A !important;\n            background: rgba(47, 166, 106, 0.18) !important;\n            border-color: rgba(47, 166, 106, 0.40) !important;\n        }\n\n        .hamburger-shell,\n        [data-testid="collapsedControl"],\n        [data-testid="stSidebarCollapsedControl"],\n        [data-testid="stSidebarCollapseButton"],\n        .stTabs [aria-selected="true"],\n        .stButton > button,\n        .stDownloadButton > button {\n            background: linear-gradient(135deg, #2FA66A 0%, #278A59 52%, #1F6F49 100%) !important;\n            color: #ffffff !important;\n            border-color: rgba(255,255,255,0.62) !important;\n            box-shadow: 0 16px 34px rgba(31, 111, 73, 0.27), 0 3px 0 rgba(255,255,255,0.25) inset !important;\n        }\n\n        .stTabs [data-baseweb="tab-list"] {\n            background: rgba(47,166,106,0.13) !important;\n            border-color: rgba(47,166,106,0.24) !important;\n        }\n\n        .stTabs [data-baseweb="tab"] {\n            background: rgba(255,255,255,0.96) !important;\n            color: #123B2A !important;\n            border: 1px solid rgba(47,166,106,0.18) !important;\n        }\n\n        .stTabs [aria-selected="true"] p,\n        .stTabs [aria-selected="true"] span,\n        .stButton > button *,\n        .stDownloadButton > button *,\n        .hamburger-title,\n        .hamburger-pill {\n            color: #ffffff !important;\n        }\n\n        section[data-testid="stSidebar"] {\n            background:\n                radial-gradient(circle at 16% 4%, rgba(47,166,106,0.23), transparent 30%),\n                linear-gradient(180deg, #ffffff 0%, #F6FFF9 44%, #EAFBF1 100%) !important;\n            border-right: 1px solid rgba(47,166,106,0.26) !important;\n            box-shadow: 14px 0 36px rgba(31, 111, 73, 0.10) !important;\n        }\n\n        .upload-zone-card {\n            background:\n                radial-gradient(circle at 8% 16%, rgba(255,255,255,0.44), transparent 26%),\n                linear-gradient(135deg, #2FA66A 0%, #3DBB78 50%, #1F6F49 100%) !important;\n            border: 1px solid rgba(255,255,255,0.62) !important;\n            box-shadow: 0 24px 48px rgba(31, 111, 73, 0.25), 0 5px 0 rgba(255,255,255,0.22) inset !important;\n        }\n\n        .upload-zone-card h3,\n        .upload-zone-card p {\n            color: #ffffff !important;\n            text-shadow: 0 2px 10px rgba(18, 59, 42, 0.24) !important;\n        }\n\n        .upload-zone-badge {\n            background: rgba(255,255,255,0.22) !important;\n            color: #ffffff !important;\n            border-color: rgba(255,255,255,0.42) !important;\n        }\n\n        .stFileUploader, div[data-testid="stFileUploader"] {\n            background: linear-gradient(145deg, #ffffff 0%, #EAFBF1 100%) !important;\n            border: 2px dashed #2FA66A !important;\n        }\n\n        .three-d-divider {\n            background: linear-gradient(90deg, rgba(47,166,106,0.08), #2FA66A, #1F6F49, #2FA66A, rgba(47,166,106,0.08)) !important;\n        }\n\n\n\n        /* ------------------------------------------------------------------\n           Final requested fix:\n           1) Upload Zone is emerald green.\n           2) Metric cards/headings after file upload are forced dark/readable.\n        ------------------------------------------------------------------ */\n        :root {\n            --cif-emerald: #2FA66A;\n            --cif-emerald-dark: #1F6F49;\n            --cif-emerald-deep: #123B2A;\n            --cif-emerald-soft: #EAFBF1;\n        }\n\n        .upload-zone-card {\n            background:\n                radial-gradient(circle at 9% 14%, rgba(255,255,255,0.52), transparent 28%),\n                linear-gradient(135deg, #2FA66A 0%, #278A59 46%, #1F6F49 100%) !important;\n            border: 1px solid rgba(255,255,255,0.66) !important;\n            box-shadow:\n                0 26px 54px rgba(31, 111, 73, 0.32),\n                0 5px 0 rgba(255,255,255,0.24) inset !important;\n        }\n\n        .upload-zone-card .upload-zone-badge {\n            background: rgba(255,255,255,0.24) !important;\n            color: #ffffff !important;\n            border-color: rgba(255,255,255,0.48) !important;\n            box-shadow: 0 8px 20px rgba(0, 77, 50, 0.18) !important;\n        }\n\n        .upload-zone-card h3,\n        .upload-zone-card p,\n        .upload-zone-card span,\n        .upload-zone-card b,\n        .upload-zone-card strong {\n            color: #ffffff !important;\n            text-shadow: 0 2px 12px rgba(18, 59, 42, 0.34) !important;\n        }\n\n        /* Metric cards shown after upload: labels and values must never inherit white text. */\n        div[data-testid="metric-container"] {\n            background:\n                linear-gradient(145deg, #ffffff 0%, #F4FFFA 54%, #EAFBF1 100%) !important;\n            border: 1px solid rgba(31, 111, 73, 0.28) !important;\n            box-shadow:\n                0 16px 38px rgba(31, 111, 73, 0.14),\n                0 3px 0 rgba(255,255,255,0.96) inset !important;\n        }\n\n        div[data-testid="metric-container"] *,\n        div[data-testid="metric-container"] p,\n        div[data-testid="metric-container"] span,\n        div[data-testid="metric-container"] label,\n        div[data-testid="metric-container"] div {\n            color: #123B2A !important;\n            text-shadow: none !important;\n        }\n\n        div[data-testid="stMetricLabel"],\n        div[data-testid="stMetricLabel"] *,\n        div[data-testid="stMetricLabel"] p,\n        div[data-testid="stMetricLabel"] span {\n            color: #123B2A !important;\n            font-weight: 850 !important;\n            opacity: 1 !important;\n        }\n\n        div[data-testid="stMetricValue"],\n        div[data-testid="stMetricValue"] *,\n        div[data-testid="stMetricValue"] p,\n        div[data-testid="stMetricValue"] span {\n            color: #247A50 !important;\n            font-weight: 950 !important;\n            opacity: 1 !important;\n        }\n\n        /* Native Streamlit success/info/subheader text after upload can also inherit light colors in some themes. */\n        div[data-testid="stAlert"] *,\n        div[data-testid="stMarkdownContainer"] h1,\n        div[data-testid="stMarkdownContainer"] h2,\n        div[data-testid="stMarkdownContainer"] h3,\n        div[data-testid="stMarkdownContainer"] h4,\n        div[data-testid="stMarkdownContainer"] h5,\n        div[data-testid="stMarkdownContainer"] h6,\n        .table-card h1,\n        .table-card h2,\n        .table-card h3,\n        .table-card h4,\n        .glass-panel h1,\n        .glass-panel h2,\n        .glass-panel h3,\n        .glass-panel h4 {\n            color: #123B2A !important;\n            text-shadow: none !important;\n            opacity: 1 !important;\n        }\n\n        /* Keep active tabs/buttons readable on dark green backgrounds. */\n        .stTabs [aria-selected="true"],\n        .stTabs [aria-selected="true"] *,\n        .stButton > button,\n        .stButton > button *,\n        .stDownloadButton > button,\n        .stDownloadButton > button * {\n            color: #ffffff !important;\n        }\n\n\n        /* ------------------------------------------------------------------\n           Vivid Developer card override: clearly different from emerald cards.\n           Uses deep navy/petrol + gold accents while staying compatible with emerald theme.\n        ------------------------------------------------------------------ */\n        .info-grid > .mini-card.developer-card {\n            isolation: isolate !important;\n            position: relative !important;\n            overflow: hidden !important;\n            padding: 22px 22px 20px 24px !important;\n            background:\n                radial-gradient(circle at 12% 10%, rgba(255,255,255,0.24), transparent 27%),\n                radial-gradient(circle at 92% 18%, rgba(255,215,122,0.24), transparent 28%),\n                linear-gradient(135deg, #102A43 0%, #0B5D5A 50%, #113B5B 100%) !important;\n            border: 2px solid rgba(255, 202, 88, 0.88) !important;\n            box-shadow:\n                0 26px 62px rgba(16, 42, 67, 0.30),\n                0 10px 28px rgba(47, 166, 106, 0.20),\n                0 0 0 4px rgba(255, 202, 88, 0.18),\n                0 4px 0 rgba(255,255,255,0.18) inset !important;\n            transform: translateY(-2px) !important;\n        }\n\n        .info-grid > .mini-card.developer-card::before {\n            content: "" !important;\n            position: absolute !important;\n            inset: 0 auto 0 0 !important;\n            width: 11px !important;\n            background: linear-gradient(180deg, #FFD166 0%, #F6B73C 45%, #2FA66A 100%) !important;\n            box-shadow: 8px 0 24px rgba(255, 209, 102, 0.38) !important;\n            z-index: 0 !important;\n        }\n\n        .info-grid > .mini-card.developer-card::after {\n            content: "Developer" !important;\n            position: absolute !important;\n            top: 14px !important;\n            right: 16px !important;\n            padding: 6px 11px !important;\n            border-radius: 999px !important;\n            background: rgba(255, 209, 102, 0.22) !important;\n            color: #FFF5D6 !important;\n            border: 1px solid rgba(255, 209, 102, 0.58) !important;\n            font-size: 11px !important;\n            font-weight: 950 !important;\n            letter-spacing: 0.75px !important;\n            text-transform: uppercase !important;\n            z-index: 1 !important;\n        }\n\n        .info-grid > .mini-card.developer-card h4,\n        .info-grid > .mini-card.developer-card h4 * {\n            color: #FFD166 !important;\n            text-shadow: 0 2px 12px rgba(0,0,0,0.36) !important;\n            font-size: 15px !important;\n            letter-spacing: 1.15px !important;\n            margin-right: 112px !important;\n            position: relative !important;\n            z-index: 2 !important;\n        }\n\n        .info-grid > .mini-card.developer-card p,\n        .info-grid > .mini-card.developer-card li,\n        .info-grid > .mini-card.developer-card span {\n            color: #E9FFF5 !important;\n            text-shadow: 0 2px 10px rgba(0,0,0,0.28) !important;\n            position: relative !important;\n            z-index: 2 !important;\n            opacity: 1 !important;\n        }\n\n        .info-grid > .mini-card.developer-card strong,\n        .info-grid > .mini-card.developer-card b {\n            display: inline-block !important;\n            margin: 2px 0 4px 0 !important;\n            padding: 7px 10px !important;\n            border-radius: 12px !important;\n            background: rgba(255, 255, 255, 0.14) !important;\n            color: #FFFFFF !important;\n            border: 1px solid rgba(255, 255, 255, 0.22) !important;\n            box-shadow: 0 8px 18px rgba(0,0,0,0.16) !important;\n            font-weight: 950 !important;\n            text-shadow: 0 2px 10px rgba(0,0,0,0.32) !important;\n        }\n\n        .info-grid > .mini-card.developer-card:hover {\n            transform: translateY(-6px) scale(1.01) !important;\n            box-shadow:\n                0 34px 76px rgba(16, 42, 67, 0.38),\n                0 12px 34px rgba(47, 166, 106, 0.24),\n                0 0 0 5px rgba(255, 202, 88, 0.24),\n                0 4px 0 rgba(255,255,255,0.20) inset !important;\n        }\n\n\n\n        /* ------------------------------------------------------------------\n           Global visible theme refresh requested by user:\n           Use the same vivid navy + gold combination across the whole UI,\n           while keeping a soft emerald accent for harmony.\n        ------------------------------------------------------------------ */\n        :root {\n            --cif-primary-navy: #102A43;\n            --cif-primary-navy-2: #163A5B;\n            --cif-primary-navy-3: #1E4C78;\n            --cif-gold-bright: #FFC857;\n            --cif-gold-soft: #F4D58D;\n            --cif-emerald-accent: #2FA66A;\n            --cif-emerald-accent-dark: #1F6F49;\n            --cif-cream-bg: #FFF8EA;\n            --cif-surface: #FFFDF8;\n            --cif-surface-2: #FDF6E8;\n            --cif-text-deep: #13273F;\n            --cif-text-soft: #4A5B70;\n        }\n\n        .stApp {\n            background:\n                radial-gradient(circle at 8% 7%, rgba(255, 200, 87, 0.16), transparent 24%),\n                radial-gradient(circle at 92% 10%, rgba(47, 166, 106, 0.10), transparent 26%),\n                radial-gradient(circle at 75% 88%, rgba(16, 42, 67, 0.08), transparent 28%),\n                linear-gradient(145deg, #FFFDF8 0%, #FFF8EA 40%, #F9FBFC 72%, #FFFFFF 100%) !important;\n            color: var(--cif-text-deep) !important;\n        }\n\n        h1, h2, h3, h4, h5, h6,\n        .stMarkdown, .stMarkdown p, .stMarkdown li,\n        .stCaptionContainer, .stText, label,\n        div[data-testid="stWidgetLabel"], div[data-testid="stWidgetLabel"] p,\n        div[data-testid="stMarkdownContainer"] p,\n        div[data-testid="stMarkdownContainer"] li,\n        .caption-note, .muted,\n        td, th, span {\n            color: var(--cif-text-deep) !important;\n        }\n\n        .hero-card,\n        .upload-zone-card,\n        .hamburger-shell,\n        [data-testid="collapsedControl"],\n        [data-testid="stSidebarCollapsedControl"],\n        [data-testid="stSidebarCollapseButton"] {\n            background:\n                radial-gradient(circle at 10% 12%, rgba(255,255,255,0.16), transparent 28%),\n                linear-gradient(135deg, var(--cif-primary-navy) 0%, var(--cif-primary-navy-2) 52%, var(--cif-primary-navy-3) 100%) !important;\n            border: 1px solid rgba(255, 200, 87, 0.68) !important;\n            box-shadow:\n                0 28px 60px rgba(16, 42, 67, 0.30),\n                0 10px 30px rgba(255, 200, 87, 0.14),\n                0 3px 0 rgba(255,255,255,0.10) inset !important;\n        }\n\n        .hero-card::after,\n        .upload-zone-card::after,\n        .hamburger-shell::after {\n            content: "";\n            position: absolute;\n            inset: 0;\n            pointer-events: none;\n            border-radius: inherit;\n            box-shadow: 0 0 0 1px rgba(255, 200, 87, 0.22) inset;\n        }\n\n        .hero-topline,\n        .upload-zone-badge,\n        .hamburger-pill {\n            background: rgba(255, 200, 87, 0.16) !important;\n            color: #FFF4D2 !important;\n            border: 1px solid rgba(255, 200, 87, 0.40) !important;\n            box-shadow: 0 10px 20px rgba(0,0,0,0.12) !important;\n        }\n\n        .hero-title,\n        .hero-subtitle,\n        .upload-zone-card h3,\n        .upload-zone-card p,\n        .upload-zone-card span,\n        .upload-zone-card b,\n        .upload-zone-card strong,\n        .hamburger-title,\n        .hamburger-shell summary,\n        .hamburger-shell summary *,\n        [data-testid="collapsedControl"] button,\n        [data-testid="stSidebarCollapsedControl"] button,\n        [data-testid="stSidebarCollapseButton"] button,\n        [data-testid="collapsedControl"] svg,\n        [data-testid="stSidebarCollapsedControl"] svg,\n        [data-testid="stSidebarCollapseButton"] svg {\n            color: #FFFFFF !important;\n        }\n\n        .mini-card,\n        .glass-panel,\n        .table-card,\n        .brand-card,\n        .sidebar-block,\n        div[data-testid="metric-container"],\n        div[data-testid="stDataFrame"] {\n            background:\n                linear-gradient(145deg, rgba(255,253,248,0.98) 0%, rgba(253,246,232,0.96) 100%) !important;\n            border: 1px solid rgba(255, 200, 87, 0.42) !important;\n            box-shadow:\n                0 18px 42px rgba(16, 42, 67, 0.08),\n                0 6px 18px rgba(255, 200, 87, 0.12),\n                0 3px 0 rgba(255,255,255,0.96) inset !important;\n        }\n\n        .mini-card:hover,\n        .glass-panel:hover,\n        .table-card:hover,\n        .brand-card:hover,\n        .sidebar-block:hover,\n        div[data-testid="metric-container"]:hover {\n            transform: translateY(-4px) !important;\n            box-shadow:\n                0 26px 58px rgba(16, 42, 67, 0.14),\n                0 10px 24px rgba(255, 200, 87, 0.18),\n                0 3px 0 rgba(255,255,255,0.96) inset !important;\n        }\n\n        .mini-card h4,\n        .sidebar-block h4,\n        .brand-card .name,\n        div[data-testid="stMetricLabel"],\n        div[data-testid="stMetricLabel"] *,\n        div[data-testid="stMetricValue"],\n        div[data-testid="stMetricValue"] *,\n        .table-card h1, .table-card h2, .table-card h3, .table-card h4,\n        .glass-panel h1, .glass-panel h2, .glass-panel h3, .glass-panel h4 {\n            color: var(--cif-primary-navy) !important;\n            text-shadow: none !important;\n        }\n\n        .mini-card p,\n        .mini-card li,\n        .sidebar-block p,\n        .sidebar-block li,\n        .caption-note,\n        .muted,\n        .brand-card p,\n        .glass-panel p,\n        .table-card p,\n        div[data-testid="metric-container"] p,\n        div[data-testid="metric-container"] span,\n        div[data-testid="metric-container"] div {\n            color: var(--cif-text-soft) !important;\n        }\n\n        .mini-card strong,\n        .brand-card strong,\n        .sidebar-block strong {\n            color: var(--cif-primary-navy-2) !important;\n        }\n\n        .section-label {\n            background: rgba(255, 200, 87, 0.18) !important;\n            color: var(--cif-primary-navy) !important;\n            border: 1px solid rgba(255, 200, 87, 0.48) !important;\n        }\n\n        section[data-testid="stSidebar"] {\n            background:\n                radial-gradient(circle at 12% 5%, rgba(255,200,87,0.16), transparent 28%),\n                linear-gradient(180deg, #FFFDF8 0%, #FFF8EA 45%, #FDF1D8 100%) !important;\n            border-right: 1px solid rgba(255, 200, 87, 0.34) !important;\n            box-shadow: 14px 0 36px rgba(16, 42, 67, 0.08) !important;\n        }\n        section[data-testid="stSidebar"] * { color: var(--cif-text-deep) !important; }\n\n        .stTabs [data-baseweb="tab-list"] {\n            background: rgba(16, 42, 67, 0.08) !important;\n            border: 1px solid rgba(255, 200, 87, 0.22) !important;\n        }\n\n        .stTabs [data-baseweb="tab"] {\n            background: rgba(255,255,255,0.96) !important;\n            color: var(--cif-primary-navy) !important;\n            border: 1px solid rgba(255, 200, 87, 0.18) !important;\n            box-shadow: 0 6px 16px rgba(16, 42, 67, 0.06) !important;\n        }\n\n        .stTabs [aria-selected="true"],\n        .stButton > button,\n        .stDownloadButton > button {\n            background: linear-gradient(135deg, var(--cif-primary-navy) 0%, var(--cif-primary-navy-2) 58%, var(--cif-primary-navy-3) 100%) !important;\n            color: #FFFFFF !important;\n            border: 1px solid rgba(255, 200, 87, 0.62) !important;\n            box-shadow: 0 18px 36px rgba(16, 42, 67, 0.22), 0 0 0 1px rgba(255, 200, 87, 0.18) inset !important;\n        }\n\n        .stTabs [aria-selected="true"] p,\n        .stTabs [aria-selected="true"] span,\n        .stButton > button *,\n        .stDownloadButton > button * {\n            color: #FFFFFF !important;\n        }\n\n        .hamburger-links a {\n            color: var(--cif-primary-navy) !important;\n            background: rgba(255, 250, 240, 0.98) !important;\n            border: 1px solid rgba(255, 200, 87, 0.30) !important;\n            box-shadow: 0 8px 18px rgba(16, 42, 67, 0.08) !important;\n        }\n\n        .hamburger-links a:hover {\n            color: var(--cif-primary-navy-2) !important;\n            border-color: rgba(47, 166, 106, 0.44) !important;\n            box-shadow: 0 12px 24px rgba(16, 42, 67, 0.12), 0 0 0 3px rgba(47, 166, 106, 0.10) !important;\n        }\n\n        .stFileUploader, div[data-testid="stFileUploader"] {\n            background: linear-gradient(145deg, #FFFEFB 0%, #FFF4DC 100%) !important;\n            border: 2px dashed #FFC857 !important;\n            box-shadow: 0 18px 36px rgba(16,42,67,0.08), 0 8px 18px rgba(255,200,87,0.10) inset !important;\n        }\n\n        code {\n            color: var(--cif-primary-navy) !important;\n            background: rgba(255, 200, 87, 0.12) !important;\n            border-radius: 8px;\n            padding: 2px 5px;\n        }\n\n        .three-d-divider {\n            background: linear-gradient(90deg, rgba(255,200,87,0.05), #FFC857, #2FA66A, #163A5B, rgba(255,200,87,0.05)) !important;\n        }\n\n        /* Make the developer card match the same global language even more strongly. */\n        .info-grid > .mini-card.developer-card {\n            background:\n                radial-gradient(circle at 10% 12%, rgba(255,255,255,0.14), transparent 30%),\n                linear-gradient(135deg, var(--cif-primary-navy) 0%, var(--cif-primary-navy-2) 55%, var(--cif-primary-navy-3) 100%) !important;\n            border: 1px solid rgba(255, 200, 87, 0.72) !important;\n            box-shadow:\n                0 34px 76px rgba(16, 42, 67, 0.34),\n                0 12px 32px rgba(255, 200, 87, 0.15),\n                0 0 0 4px rgba(255, 200, 87, 0.10),\n                0 3px 0 rgba(255,255,255,0.10) inset !important;\n        }\n\n        .info-grid > .mini-card.developer-card h4 {\n            color: #FFD778 !important;\n            letter-spacing: 1px !important;\n        }\n\n        .info-grid > .mini-card.developer-card p,\n        .info-grid > .mini-card.developer-card li,\n        .info-grid > .mini-card.developer-card span {\n            color: #EAF4FF !important;\n        }\n\n        .info-grid > .mini-card.developer-card strong,\n        .info-grid > .mini-card.developer-card b {\n            display: inline-block !important;\n            background: rgba(255, 200, 87, 0.16) !important;\n            color: #FFFFFF !important;\n            border: 1px solid rgba(255, 200, 87, 0.34) !important;\n        }\n\n        \n        /* ================================================================\n           CLEAN FINAL FIX\n           1) Hero subtitle readable\n           2) Upload component readable\n           3) Sidebar brand card no longer shows raw HTML/code\n        ================================================================ */\n\n        .hero-card .hero-subtitle,\n        .hero-card .hero-subtitle * {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            opacity: 1 !important;\n            font-weight: 800 !important;\n            line-height: 1.75 !important;\n            text-shadow: 0 2px 12px rgba(0,0,0,0.70) !important;\n        }\n\n        .sidebar-brand-card {\n            background: linear-gradient(135deg, #102A43 0%, #163A5B 55%, #1E4C78 100%) !important;\n            border: 1px solid rgba(255, 200, 87, 0.70) !important;\n            box-shadow: 0 18px 42px rgba(16, 42, 67, 0.26), 0 0 0 3px rgba(255, 200, 87, 0.12) !important;\n        }\n\n        .sidebar-brand-card .brand-kicker {\n            font-size: 12px !important;\n            color: #FFC857 !important;\n            -webkit-text-fill-color: #FFC857 !important;\n            letter-spacing: 1.4px !important;\n            text-transform: uppercase !important;\n            font-weight: 900 !important;\n            margin-bottom: 8px !important;\n        }\n\n        .sidebar-brand-card .name {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            font-weight: 950 !important;\n            font-size: 19px !important;\n            line-height: 1.35 !important;\n            margin-bottom: 8px !important;\n        }\n\n        .sidebar-brand-card .muted {\n            color: #EAF4FF !important;\n            -webkit-text-fill-color: #EAF4FF !important;\n            opacity: 1 !important;\n            text-shadow: 0 2px 10px rgba(0,0,0,0.35) !important;\n            line-height: 1.65 !important;\n            font-weight: 600 !important;\n        }\n\n        /* File uploader */\n        div[data-testid="stFileUploader"] {\n            background: #FFF8EA !important;\n            border: 2px dashed #FFC857 !important;\n            border-radius: 22px !important;\n            padding: 14px !important;\n            box-shadow: 0 16px 34px rgba(16, 42, 67, 0.10) !important;\n        }\n\n        div[data-testid="stFileUploader"] > label,\n        div[data-testid="stFileUploader"] > label *,\n        div[data-testid="stFileUploader"] label,\n        div[data-testid="stFileUploader"] label * {\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            opacity: 1 !important;\n            font-weight: 900 !important;\n            text-shadow: none !important;\n        }\n\n        div[data-testid="stFileUploader"] section,\n        section[data-testid="stFileUploaderDropzone"],\n        div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {\n            background: #102A43 !important;\n            border: 1px solid rgba(255,200,87,0.72) !important;\n            border-radius: 14px !important;\n        }\n\n        div[data-testid="stFileUploader"] section *,\n        section[data-testid="stFileUploaderDropzone"] *,\n        div[data-testid="stFileUploader"] small,\n        div[data-testid="stFileUploader"] span,\n        div[data-testid="stFileUploader"] p {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            opacity: 1 !important;\n            fill: #FFFFFF !important;\n            stroke: #FFFFFF !important;\n            font-weight: 700 !important;\n            text-shadow: none !important;\n        }\n\n        div[data-testid="stFileUploader"] button,\n        div[data-testid="stFileUploader"] button *,\n        section[data-testid="stFileUploaderDropzone"] button,\n        section[data-testid="stFileUploaderDropzone"] button * {\n            background: #FFC857 !important;\n            background-color: #FFC857 !important;\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            border: 1px solid rgba(255,255,255,0.85) !important;\n            opacity: 1 !important;\n            font-weight: 900 !important;\n            text-shadow: none !important;\n        }\n\n\n\n        /* ---------------------------------------------------------------\n           Readable sheet-list cards: replaces dark JSON/code output after upload.\n        --------------------------------------------------------------- */\n        .sheet-list-box {\n            display: flex !important;\n            flex-wrap: wrap !important;\n            gap: 10px !important;\n            align-items: center !important;\n            margin: 8px 0 14px 0 !important;\n            padding: 14px 14px !important;\n            border-radius: 18px !important;\n            background: linear-gradient(145deg, #FFFEFB 0%, #FFF8EA 100%) !important;\n            border: 1px solid rgba(255, 200, 87, 0.44) !important;\n            box-shadow: 0 12px 28px rgba(16, 42, 67, 0.08), 0 2px 0 rgba(255,255,255,0.92) inset !important;\n        }\n\n        .sheet-pill {\n            display: inline-flex !important;\n            align-items: center !important;\n            gap: 8px !important;\n            padding: 9px 13px !important;\n            border-radius: 999px !important;\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            background: #FFFFFF !important;\n            border: 1px solid rgba(16, 42, 67, 0.14) !important;\n            box-shadow: 0 8px 18px rgba(16, 42, 67, 0.07) !important;\n            font-weight: 900 !important;\n            font-size: 13px !important;\n            letter-spacing: 0.2px !important;\n            text-shadow: none !important;\n        }\n\n        .sheet-pill::before {\n            content: "" !important;\n            width: 8px !important;\n            height: 8px !important;\n            border-radius: 999px !important;\n            background: #2FA66A !important;\n            box-shadow: 0 0 0 4px rgba(47, 166, 106, 0.13) !important;\n        }\n\n        .sheet-pill.skipped::before {\n            background: #FFC857 !important;\n            box-shadow: 0 0 0 4px rgba(255, 200, 87, 0.18) !important;\n        }\n\n        .sheet-pill.skipped {\n            color: #4A5B70 !important;\n            -webkit-text-fill-color: #4A5B70 !important;\n            background: #FFFDF8 !important;\n            border-color: rgba(255, 200, 87, 0.52) !important;\n        }\n\n        .sheet-list-note {\n            margin: 8px 0 6px 0 !important;\n            color: #4A5B70 !important;\n            -webkit-text-fill-color: #4A5B70 !important;\n            font-size: 14px !important;\n            font-weight: 800 !important;\n            text-shadow: none !important;\n        }\n\n        /* In case Streamlit JSON/code blocks remain anywhere, make them readable too. */\n        div[data-testid="stJson"],\n        div[data-testid="stJson"] *,\n        pre, pre *, code, code * {\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            text-shadow: none !important;\n        }\n\n        div[data-testid="stJson"], pre {\n            background: #FFFDF8 !important;\n            border: 1px solid rgba(255, 200, 87, 0.44) !important;\n            border-radius: 16px !important;\n        }\n\n\n\n        /* ================================================================\n           CIF_DEMATEL_16 - High-contrast uploaded workbook sheet summary\n           Fixes unreadable dark JSON/code blocks after Excel upload.\n        ================================================================ */\n        .sheet-clean-panel,\n        .sheet-clean-panel * {\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            opacity: 1 !important;\n            text-shadow: none !important;\n            font-family: \'Inter\', \'Segoe UI\', sans-serif !important;\n            box-sizing: border-box !important;\n        }\n\n        .sheet-clean-panel {\n            width: 100% !important;\n            margin: 0 0 18px 0 !important;\n            padding: 22px 24px !important;\n            border-radius: 24px !important;\n            background: linear-gradient(145deg, #FFFFFF 0%, #FFF8EA 48%, #F4FFFA 100%) !important;\n            border: 2px solid rgba(255, 200, 87, 0.72) !important;\n            box-shadow:\n                0 22px 52px rgba(16, 42, 67, 0.12),\n                0 6px 16px rgba(255, 200, 87, 0.16),\n                0 3px 0 rgba(255,255,255,0.98) inset !important;\n            overflow: hidden !important;\n        }\n\n        .sheet-clean-header {\n            display: flex !important;\n            justify-content: space-between !important;\n            gap: 14px !important;\n            align-items: flex-start !important;\n            margin-bottom: 18px !important;\n            padding-bottom: 14px !important;\n            border-bottom: 1px solid rgba(16, 42, 67, 0.10) !important;\n        }\n\n        .sheet-clean-title {\n            margin: 0 !important;\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            font-size: 26px !important;\n            line-height: 1.25 !important;\n            font-weight: 950 !important;\n            letter-spacing: -0.3px !important;\n        }\n\n        .sheet-clean-subtitle {\n            margin: 6px 0 0 0 !important;\n            color: #4A5B70 !important;\n            -webkit-text-fill-color: #4A5B70 !important;\n            font-size: 14px !important;\n            line-height: 1.65 !important;\n            font-weight: 750 !important;\n        }\n\n        .sheet-clean-counts {\n            display: flex !important;\n            gap: 10px !important;\n            flex-wrap: wrap !important;\n            justify-content: flex-end !important;\n        }\n\n        .sheet-count-badge {\n            min-width: 112px !important;\n            padding: 10px 12px !important;\n            border-radius: 16px !important;\n            background: #FFFFFF !important;\n            border: 1px solid rgba(16, 42, 67, 0.12) !important;\n            box-shadow: 0 10px 22px rgba(16, 42, 67, 0.08) !important;\n            text-align: center !important;\n        }\n\n        .sheet-count-badge .num {\n            display: block !important;\n            font-size: 22px !important;\n            line-height: 1 !important;\n            font-weight: 950 !important;\n            color: #1F6F49 !important;\n            -webkit-text-fill-color: #1F6F49 !important;\n        }\n\n        .sheet-count-badge.skipped .num {\n            color: #9B6500 !important;\n            -webkit-text-fill-color: #9B6500 !important;\n        }\n\n        .sheet-count-badge .lbl {\n            display: block !important;\n            margin-top: 5px !important;\n            color: #4A5B70 !important;\n            -webkit-text-fill-color: #4A5B70 !important;\n            font-size: 11px !important;\n            font-weight: 900 !important;\n            letter-spacing: 0.75px !important;\n            text-transform: uppercase !important;\n        }\n\n        .sheet-clean-grid {\n            display: grid !important;\n            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)) !important;\n            gap: 12px !important;\n            margin-top: 12px !important;\n        }\n\n        .sheet-clean-item {\n            display: flex !important;\n            align-items: center !important;\n            justify-content: space-between !important;\n            gap: 12px !important;\n            min-height: 58px !important;\n            padding: 13px 14px !important;\n            border-radius: 18px !important;\n            background: #FFFFFF !important;\n            border: 1px solid rgba(31, 111, 73, 0.22) !important;\n            box-shadow: 0 10px 24px rgba(16, 42, 67, 0.07) !important;\n        }\n\n        .sheet-clean-item.skipped {\n            background: #FFFDF8 !important;\n            border-color: rgba(255, 200, 87, 0.60) !important;\n        }\n\n        .sheet-name-wrap {\n            display: flex !important;\n            align-items: center !important;\n            gap: 10px !important;\n            min-width: 0 !important;\n        }\n\n        .sheet-dot {\n            flex: 0 0 auto !important;\n            width: 11px !important;\n            height: 11px !important;\n            border-radius: 999px !important;\n            background: #2FA66A !important;\n            box-shadow: 0 0 0 5px rgba(47, 166, 106, 0.14) !important;\n        }\n\n        .sheet-clean-item.skipped .sheet-dot {\n            background: #FFC857 !important;\n            box-shadow: 0 0 0 5px rgba(255, 200, 87, 0.18) !important;\n        }\n\n        .sheet-name {\n            display: block !important;\n            min-width: 0 !important;\n            overflow: hidden !important;\n            text-overflow: ellipsis !important;\n            white-space: nowrap !important;\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            font-size: 16px !important;\n            line-height: 1.35 !important;\n            font-weight: 950 !important;\n        }\n\n        .sheet-status {\n            flex: 0 0 auto !important;\n            padding: 6px 9px !important;\n            border-radius: 999px !important;\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            background: #1F6F49 !important;\n            font-size: 10px !important;\n            line-height: 1 !important;\n            font-weight: 950 !important;\n            letter-spacing: 0.65px !important;\n            text-transform: uppercase !important;\n        }\n\n        .sheet-clean-item.skipped .sheet-status {\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            background: #FFC857 !important;\n        }\n\n        .sheet-clean-section-label {\n            display: inline-flex !important;\n            align-items: center !important;\n            margin: 18px 0 6px 0 !important;\n            padding: 7px 11px !important;\n            border-radius: 999px !important;\n            background: rgba(16, 42, 67, 0.08) !important;\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            font-size: 12px !important;\n            font-weight: 950 !important;\n            letter-spacing: 0.85px !important;\n            text-transform: uppercase !important;\n            border: 1px solid rgba(16, 42, 67, 0.10) !important;\n        }\n\n        @media (max-width: 760px) {\n            .sheet-clean-header { flex-direction: column !important; }\n            .sheet-clean-counts { justify-content: flex-start !important; }\n            .sheet-clean-title { font-size: 22px !important; }\n            .sheet-clean-grid { grid-template-columns: 1fr !important; }\n        }\n\n\n\n        /* ================================================================\n           FINAL TOP BAR FIX - Heavy Gold Streamlit header / toolbar\n           Makes the native Streamlit top bar readable instead of black.\n        ================================================================ */\n        header[data-testid="stHeader"],\n        .stAppHeader {\n            background:\n                radial-gradient(circle at 4% 50%, rgba(255,255,255,0.28), transparent 24%),\n                linear-gradient(135deg, #6F4E00 0%, #B8860B 28%, #D4AF37 54%, #8A6508 100%) !important;\n            border-bottom: 1px solid rgba(255, 238, 178, 0.70) !important;\n            box-shadow:\n                0 14px 34px rgba(111, 78, 0, 0.35),\n                0 2px 0 rgba(255,255,255,0.22) inset !important;\n            color: #102A43 !important;\n        }\n\n        header[data-testid="stHeader"]::before,\n        .stAppHeader::before {\n            content: "" !important;\n            position: absolute !important;\n            inset: 0 !important;\n            pointer-events: none !important;\n            background: linear-gradient(90deg, rgba(255,255,255,0.18), transparent 35%, rgba(255,255,255,0.12)) !important;\n        }\n\n        /* Streamlit toolbar / deploy / menu icons */\n        header[data-testid="stHeader"] *,\n        .stAppHeader *,\n        div[data-testid="stToolbar"],\n        div[data-testid="stToolbar"] *,\n        div[data-testid="stDeployButton"],\n        div[data-testid="stDeployButton"] *,\n        button[kind="header"],\n        button[kind="header"] *,\n        [data-testid="baseButton-header"],\n        [data-testid="baseButton-header"] * {\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            fill: #102A43 !important;\n            stroke: #102A43 !important;\n            opacity: 1 !important;\n            text-shadow: none !important;\n        }\n\n        header[data-testid="stHeader"] button,\n        .stAppHeader button,\n        div[data-testid="stToolbar"] button,\n        div[data-testid="stDeployButton"] button,\n        button[kind="header"],\n        [data-testid="baseButton-header"] {\n            background: rgba(255, 253, 248, 0.34) !important;\n            border: 1px solid rgba(16, 42, 67, 0.20) !important;\n            border-radius: 12px !important;\n            box-shadow: 0 8px 18px rgba(111, 78, 0, 0.18) !important;\n        }\n\n        header[data-testid="stHeader"] button:hover,\n        .stAppHeader button:hover,\n        div[data-testid="stToolbar"] button:hover,\n        div[data-testid="stDeployButton"] button:hover,\n        button[kind="header"]:hover,\n        [data-testid="baseButton-header"]:hover {\n            background: rgba(255, 255, 255, 0.58) !important;\n            border-color: rgba(16, 42, 67, 0.34) !important;\n            transform: translateY(-1px) !important;\n        }\n\n        /* The small top decoration line should match the gold header. */\n        [data-testid="stDecoration"] {\n            background: linear-gradient(90deg, #6F4E00 0%, #D4AF37 45%, #FFC857 65%, #8A6508 100%) !important;\n            height: 4px !important;\n        }\n\n        /* In some Streamlit builds the top bar is rendered as these classes. */\n        .st-emotion-cache-18ni7ap,\n        .st-emotion-cache-h4xjwg,\n        .st-emotion-cache-zq5wmm {\n            background:\n                radial-gradient(circle at 4% 50%, rgba(255,255,255,0.24), transparent 24%),\n                linear-gradient(135deg, #6F4E00 0%, #B8860B 30%, #D4AF37 58%, #8A6508 100%) !important;\n            color: #102A43 !important;\n            border-bottom: 1px solid rgba(255, 238, 178, 0.65) !important;\n        }\n\n\n        /* ================================================================\n           FINAL UPLOAD ZONE FIX - Heavy Gold box + white readable text\n           Requested: make Upload Zone text white / make upload box gold.\n        ================================================================ */\n        .upload-zone-card {\n            background:\n                radial-gradient(circle at 8% 12%, rgba(255,255,255,0.34), transparent 28%),\n                radial-gradient(circle at 92% 18%, rgba(255,255,255,0.18), transparent 30%),\n                linear-gradient(135deg, #6F4E00 0%, #A87400 28%, #D4AF37 58%, #8A6508 100%) !important;\n            border: 2px solid rgba(255, 238, 178, 0.92) !important;\n            box-shadow:\n                0 28px 64px rgba(111, 78, 0, 0.34),\n                0 0 0 4px rgba(255, 200, 87, 0.14),\n                0 5px 0 rgba(255,255,255,0.22) inset !important;\n        }\n\n        .upload-zone-card .upload-zone-badge {\n            background: rgba(16, 42, 67, 0.30) !important;\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            border: 1px solid rgba(255,255,255,0.42) !important;\n            box-shadow: 0 8px 20px rgba(0,0,0,0.18) !important;\n            opacity: 1 !important;\n        }\n\n        .upload-zone-card h1,\n        .upload-zone-card h2,\n        .upload-zone-card h3,\n        .upload-zone-card h4,\n        .upload-zone-card p,\n        .upload-zone-card span,\n        .upload-zone-card div,\n        .upload-zone-card b,\n        .upload-zone-card strong,\n        .upload-zone-card * {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            opacity: 1 !important;\n            text-shadow: 0 3px 14px rgba(0,0,0,0.58) !important;\n        }\n\n        .upload-zone-card h3 {\n            font-weight: 950 !important;\n            letter-spacing: 0.2px !important;\n        }\n\n        .upload-zone-card p {\n            font-weight: 750 !important;\n            line-height: 1.75 !important;\n        }\n\n\n\n\n        /* ================================================================\n           FINAL REQUEST 19 - keep everything else unchanged\n           1) Force a light-looking default interface.\n           2) Make the Upload Zone a clear premium gold box.\n        ================================================================ */\n        html,\n        body,\n        .stApp,\n        [data-testid="stAppViewContainer"],\n        [data-testid="stMain"],\n        [data-testid="stMainBlockContainer"],\n        .block-container {\n            color-scheme: light !important;\n        }\n\n        .stApp,\n        [data-testid="stAppViewContainer"],\n        [data-testid="stMain"] {\n            background:\n                radial-gradient(circle at 8% 7%, rgba(255, 209, 102, 0.14), transparent 25%),\n                radial-gradient(circle at 94% 8%, rgba(47, 166, 106, 0.08), transparent 27%),\n                linear-gradient(145deg, #FFFDF8 0%, #FFF8EA 42%, #FFFFFF 100%) !important;\n            color: #102A43 !important;\n        }\n\n        .upload-zone-card {\n            background:\n                radial-gradient(circle at 9% 12%, rgba(255,255,255,0.42), transparent 28%),\n                radial-gradient(circle at 88% 18%, rgba(255,244,210,0.30), transparent 32%),\n                linear-gradient(135deg, #8A6508 0%, #B8860B 24%, #D4AF37 50%, #FFD166 72%, #A87400 100%) !important;\n            border: 2px solid rgba(255, 244, 210, 0.96) !important;\n            box-shadow:\n                0 30px 68px rgba(111, 78, 0, 0.35),\n                0 0 0 5px rgba(255, 209, 102, 0.18),\n                0 6px 0 rgba(255,255,255,0.26) inset !important;\n        }\n\n        .upload-zone-card .upload-zone-badge {\n            background: rgba(16, 42, 67, 0.34) !important;\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            border: 1px solid rgba(255,255,255,0.52) !important;\n            box-shadow: 0 10px 24px rgba(0,0,0,0.20) !important;\n            opacity: 1 !important;\n        }\n\n        .upload-zone-card h1,\n        .upload-zone-card h2,\n        .upload-zone-card h3,\n        .upload-zone-card h4,\n        .upload-zone-card p,\n        .upload-zone-card span,\n        .upload-zone-card div,\n        .upload-zone-card b,\n        .upload-zone-card strong,\n        .upload-zone-card * {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            opacity: 1 !important;\n            text-shadow: 0 3px 15px rgba(0,0,0,0.62) !important;\n        }\n\n        .upload-zone-card h3 {\n            font-weight: 950 !important;\n        }\n\n        .upload-zone-card p {\n            font-weight: 800 !important;\n            line-height: 1.78 !important;\n        }\n\n        \n\n        /* ================================================================\n           FINAL REQUEST 20 - Upload Zone must be gold and all text white\n           This is intentionally placed at the very end of the CSS.\n        ================================================================ */\n        .upload-zone-card.upload-zone-gold-final,\n        div.upload-zone-card.upload-zone-gold-final {\n            background:\n                radial-gradient(circle at 9% 12%, rgba(255,255,255,0.45), transparent 28%),\n                radial-gradient(circle at 88% 16%, rgba(255,244,210,0.38), transparent 32%),\n                linear-gradient(135deg, #6F4E00 0%, #9B7208 23%, #D4AF37 52%, #FFD166 74%, #8A6508 100%) !important;\n            border: 2px solid rgba(255,244,210,0.98) !important;\n            box-shadow:\n                0 30px 68px rgba(111,78,0,0.38),\n                0 0 0 5px rgba(255,209,102,0.22),\n                0 6px 0 rgba(255,255,255,0.28) inset !important;\n        }\n\n        .upload-zone-card.upload-zone-gold-final,\n        .upload-zone-card.upload-zone-gold-final *,\n        .upload-zone-card.upload-zone-gold-final .upload-zone-title,\n        .upload-zone-card.upload-zone-gold-final .upload-zone-description,\n        .upload-zone-card.upload-zone-gold-final .upload-zone-badge {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            opacity: 1 !important;\n            text-shadow: 0 4px 16px rgba(0,0,0,0.72) !important;\n        }\n\n        .upload-zone-card.upload-zone-gold-final .upload-zone-description {\n            font-size: 16px !important;\n            font-weight: 850 !important;\n            line-height: 1.85 !important;\n        }\n\n\n        /* FINAL FORCE: Upload Zone description text must stay pure white. */\n        #force-upload-desc-white,\n        #force-upload-desc-white *,\n        div#force-upload-desc-white,\n        div#force-upload-desc-white span {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            opacity: 1 !important;\n            font-weight: 900 !important;\n            text-shadow: 0 4px 18px rgba(0,0,0,0.78) !important;\n        }\n\n\n\n        /* ================================================================\n           FINAL EXPORT DOWNLOAD BUTTON FIX\n           Make the "Download Excel Results" button highly visible.\n        ================================================================ */\n        div[data-testid="stDownloadButton"] button,\n        div[data-testid="stDownloadButton"] > button,\n        .stDownloadButton > button {\n            background: linear-gradient(135deg, #8A5A00 0%, #B8860B 28%, #D4AF37 58%, #F4D06F 100%) !important;\n            background-color: #D4AF37 !important;\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            border: 2px solid rgba(255, 244, 210, 0.95) !important;\n            border-radius: 18px !important;\n            font-weight: 950 !important;\n            letter-spacing: 0.2px !important;\n            text-shadow: 0 2px 10px rgba(0,0,0,0.55) !important;\n            box-shadow:\n                0 18px 38px rgba(138, 90, 0, 0.32),\n                0 0 0 3px rgba(212, 175, 55, 0.18),\n                0 3px 0 rgba(255,255,255,0.30) inset !important;\n            opacity: 1 !important;\n        }\n\n        div[data-testid="stDownloadButton"] button *,\n        div[data-testid="stDownloadButton"] button p,\n        div[data-testid="stDownloadButton"] button span,\n        div[data-testid="stDownloadButton"] button div,\n        .stDownloadButton > button *,\n        .stDownloadButton > button p,\n        .stDownloadButton > button span,\n        .stDownloadButton > button div {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            fill: #FFFFFF !important;\n            stroke: #FFFFFF !important;\n            opacity: 1 !important;\n            font-weight: 950 !important;\n            text-shadow: 0 2px 10px rgba(0,0,0,0.55) !important;\n        }\n\n        div[data-testid="stDownloadButton"] button:hover,\n        .stDownloadButton > button:hover {\n            background: linear-gradient(135deg, #9A6600 0%, #C99612 30%, #E2BD43 62%, #FFE08A 100%) !important;\n            transform: translateY(-2px) !important;\n            box-shadow:\n                0 24px 48px rgba(138, 90, 0, 0.42),\n                0 0 0 4px rgba(212, 175, 55, 0.24),\n                0 3px 0 rgba(255,255,255,0.36) inset !important;\n        }\n\n</style>\n        ', unsafe_allow_html=True)

def dematel_hamburger_menu():
    st.markdown('\n        <details class="hamburger-shell">\n            <summary>\n                <span class="hamburger-icon"><span></span><span></span><span></span></span>\n                <span class="hamburger-title">CIF-DEMATEL Menu</span>\n                <span class="hamburger-pill">Quick access</span>\n            </summary>\n            <div class="hamburger-links">\n                <a href="#input-guide">Input Guide</a>\n                <a href="#active-scale">Scales</a>\n                <a href="#upload-workbook">Upload Workbook</a>\n                <a href="#results-dashboard">Results</a>\n                <a href="#download-results">Export</a>\n                <a href="#">Back to Top</a>\n            </div>\n        </details>\n        ', unsafe_allow_html=True)

def dematel_hero_section():
    st.markdown('\n        <div class="hero-card">\n            <div class="hero-topline">Navy & Gold Decision Analytics</div>\n            <div class="hero-title">CIF-DEMATEL Calculator</div>\n            <p class="hero-subtitle" style="color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; opacity:1 !important; font-weight:800 !important; line-height:1.75 !important; text-shadow:0 2px 12px rgba(0,0,0,0.70) !important;">\n                A navy, gold, and soft emerald executive Streamlit interface for Circular Intuitionistic Fuzzy DEMATEL.\n                Upload direct-influence matrices from experts, aggregate circular intuitionistic fuzzy evaluations,\n                defuzzify by lambda attitude, build total relation matrix, and classify criteria into cause/effect groups.\n            </p>\n        </div>\n        ', unsafe_allow_html=True)

def dematel_header_panels():
    st.markdown('\n        <div class="info-grid">\n            <div class="mini-card developer-card">\n                <h4>Developer & Concept Designer</h4>\n                <p><strong>Dr. Saeed Alinejad - Shiraz University, Iran</strong></p>\n                <p>Advanced decision-making tool developer.</p>\n            </div>\n            <div class="mini-card">\n                <h4>CIF-DEMATEL Logic</h4>\n                <p>Each pairwise influence is modeled by membership, non-membership, hesitation, and a circular radius. This gives a richer representation of ambiguity than crisp DEMATEL matrices.</p>\n            </div>\n            <div class="mini-card">\n                <h4>Cause / Effect Analysis</h4>\n                <p>The final dashboard reports D, R, D+R prominence, and D-R relation values, with causal and affected criteria separated automatically.</p>\n            </div>\n        </div>\n        ', unsafe_allow_html=True)

def dematel_intro_card():
    st.markdown('\n        <div id="input-guide"></div>\n        <div class="glass-panel">\n            <span class="section-label">Input Guide</span>\n            <div class="caption-note">\n                Create one sheet per expert. Each sheet must be a square direct-influence matrix:\n                first column = source criterion, first row = target criteria. The diagonal is automatically forced to <b>NI</b>.\n                Valid influence terms: <b>NI, LI, MI, HI, VHI</b>. Numeric values <b>0, 1, 2, 3, 4</b> are also accepted.\n                Optional sheet <b>Expert_Info</b> can contain columns <b>Expert</b> and either <b>Weight</b> or <b>WeightTerm</b>.\n            </div>\n            <br>\n            <table style="width:100%; border-collapse: collapse; font-size:14px;">\n                <tr>\n                    <th style="text-align:left; padding:10px; background:rgba(47,166,106,0.20);">Criterion</th>\n                    <th style="text-align:left; padding:10px; background:rgba(47,166,106,0.20);">C1</th>\n                    <th style="text-align:left; padding:10px; background:rgba(47,166,106,0.20);">C2</th>\n                    <th style="text-align:left; padding:10px; background:rgba(47,166,106,0.20);">C3</th>\n                </tr>\n                <tr><td style="padding:10px; background:rgba(255,255,255,0.72);">C1</td><td style="padding:10px;">NI</td><td style="padding:10px;">HI</td><td style="padding:10px;">MI</td></tr>\n                <tr><td style="padding:10px; background:rgba(255,255,255,0.72);">C2</td><td style="padding:10px;">LI</td><td style="padding:10px;">NI</td><td style="padding:10px;">VHI</td></tr>\n            </table>\n        </div>\n        ', unsafe_allow_html=True)

def dematel_render_sheet_list(items, skipped: bool=False):
    """Backward-compatible renderer. Kept for older calls, but now uses bright cards."""
    status = 'SKIPPED' if skipped else 'USED'
    item_class = 'sheet-clean-item skipped' if skipped else 'sheet-clean-item'
    if not items:
        st.markdown('<div class="sheet-clean-grid"><div class="sheet-clean-item skipped"><div class="sheet-name-wrap"><span class="sheet-dot"></span><span class="sheet-name">No sheets found</span></div><span class="sheet-status">EMPTY</span></div></div>', unsafe_allow_html=True)
        return
    cards = []
    for item in items:
        safe_item = html.escape(str(item))
        cards.append(f'\n            <div class="{item_class}">\n                <div class="sheet-name-wrap">\n                    <span class="sheet-dot"></span>\n                    <span class="sheet-name" title="{safe_item}">{safe_item}</span>\n                </div>\n                <span class="sheet-status">{status}</span>\n            </div>\n            ')
    st.markdown(f"""<div class="sheet-clean-grid">{''.join(cards)}</div>""", unsafe_allow_html=True)

def dematel_render_sheet_summary(expert_items, skipped_items):
    """Render the Excel sheet detection result as one complete, high-contrast HTML block."""
    expert_items = list(expert_items or [])
    skipped_items = list(skipped_items or [])

    def make_cards(items, skipped=False):
        status = 'SKIPPED' if skipped else 'USED'
        item_class = 'sheet-clean-item skipped' if skipped else 'sheet-clean-item'
        if not items:
            return '<div class="sheet-clean-item skipped"><div class="sheet-name-wrap"><span class="sheet-dot"></span><span class="sheet-name">No sheets found</span></div><span class="sheet-status">EMPTY</span></div>'
        cards = []
        for item in items:
            safe_item = html.escape(str(item))
            cards.append(f'\n                <div class="{item_class}">\n                    <div class="sheet-name-wrap">\n                        <span class="sheet-dot"></span>\n                        <span class="sheet-name" title="{safe_item}">{safe_item}</span>\n                    </div>\n                    <span class="sheet-status">{status}</span>\n                </div>\n                ')
        return ''.join(cards)
    skipped_html = ''
    if skipped_items:
        skipped_html = f'\n            <div class="sheet-clean-section-label">Skipped non-expert sheets</div>\n            <div class="sheet-clean-grid">{make_cards(skipped_items, skipped=True)}</div>\n        '
    html_block = f'\n    <div class="sheet-clean-panel">\n        <div class="sheet-clean-header">\n            <div>\n                <h3 class="sheet-clean-title">Detected Expert Sheets</h3>\n                <p class="sheet-clean-subtitle">The workbook was read successfully. Green cards are expert sheets used in the CIF-DEMATEL calculation; gold cards are auxiliary sheets that were skipped.</p>\n            </div>\n            <div class="sheet-clean-counts">\n                <div class="sheet-count-badge"><span class="num">{len(expert_items)}</span><span class="lbl">Used Sheets</span></div>\n                <div class="sheet-count-badge skipped"><span class="num">{len(skipped_items)}</span><span class="lbl">Skipped</span></div>\n            </div>\n        </div>\n        <div class="sheet-clean-section-label">Valid expert sheets</div>\n        <div class="sheet-clean-grid">{make_cards(expert_items, skipped=False)}</div>\n        {skipped_html}\n    </div>\n    '
    st.markdown(html_block, unsafe_allow_html=True)
dematel_CIF_DEMATEL_INFLUENCE_SCALE = {'NI': {'rating': 0, 'description': 'No Influence', 'mu': 0.0, 'nu': 1.0}, 'LI': {'rating': 1, 'description': 'Low Influence', 'mu': 0.35, 'nu': 0.6}, 'MI': {'rating': 2, 'description': 'Medium Influence', 'mu': 0.5, 'nu': 0.45}, 'HI': {'rating': 3, 'description': 'High Influence', 'mu': 0.75, 'nu': 0.2}, 'VHI': {'rating': 4, 'description': 'Very High Influence', 'mu': 0.9, 'nu': 0.1}}
dematel_CIF_EXPERT_WEIGHT_SCALE = {'AL': (0.05, 0.85), 'VL': (0.15, 0.75), 'L': (0.25, 0.65), 'ML': (0.35, 0.55), 'AE': (0.45, 0.45), 'MH': (0.55, 0.35), 'H': (0.65, 0.25), 'VH': (0.75, 0.15), 'AH': (0.85, 0.05)}
dematel_TERM_DESCRIPTIONS = {'AL': 'Absolutely Low', 'VL': 'Very Low', 'L': 'Low', 'ML': 'Medium Low', 'AE': 'Average', 'MH': 'Medium High', 'H': 'High', 'VH': 'Very High', 'AH': 'Absolutely High'}
dematel_EXPERT_INFO_SHEET_NAMES = {'expert_info', 'experts', 'expert_weights', 'decision_makers', 'decision maker weights', 'dm_weights'}
dematel_SOURCE_ALIASES = {'source', 'from', 'criterion', 'criteria', 'factor', 'row', 'cause'}
dematel_TARGET_ALIASES = {'target', 'to', 'affected', 'column', 'effect'}
dematel_INFLUENCE_ALIASES = {'influence', 'evaluation', 'assessment', 'term', 'value', 'score'}
dematel_PERSIAN_DIGIT_MAP = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩٫٬', '01234567890123456789..')

def dematel_clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how='all')
    df = df.dropna(axis=1, how='all')
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

def dematel_is_auxiliary_sheet(sheet_name: str) -> bool:
    lower_name = sheet_name.lower().strip()
    if lower_name in dematel_EXPERT_INFO_SHEET_NAMES:
        return False
    keywords = ['scale', 'readme', 'instruction', 'guide', 'result', 'output', 'weights', 'parameter']
    return any((keyword in lower_name for keyword in keywords))

def dematel_get_column_by_alias(df: pd.DataFrame, aliases: set) -> Optional[str]:
    for col in df.columns:
        if str(col).strip().lower() in aliases:
            return col
    return None

def dematel_hesitation_degree(mu: float, nu: float) -> float:
    return max(0.0, 1.0 - float(mu) - float(nu))

def dematel_validate_cif_pair(mu: float, nu: float, label: str='') -> None:
    eps = 1e-12
    if not (0.0 - eps <= mu <= 1.0 + eps and 0.0 - eps <= nu <= 1.0 + eps):
        raise ValueError(f'Invalid CIF pair {label}: membership and non-membership must be in [0, 1].')
    if mu + nu > 1.0 + eps:
        raise ValueError(f'Invalid CIF pair {label}: mu + nu must be <= 1. Current value: {mu + nu:.6f}')

def dematel_standardize_influence_term(value) -> str:
    if pd.isna(value):
        return 'NI'
    text = str(value).strip().translate(dematel_PERSIAN_DIGIT_MAP)
    text = re.sub('\\s+', '', text.upper())
    text = text.replace('-', '').replace('_', '')
    try:
        numeric_value = float(text)
        rounded = int(round(numeric_value))
        if rounded == 0:
            return 'NI'
        if rounded == 1:
            return 'LI'
        if rounded == 2:
            return 'MI'
        if rounded == 3:
            return 'HI'
        if rounded == 4:
            return 'VHI'
    except Exception:
        pass
    aliases = {'NI': 'NI', 'NO': 'NI', 'NONE': 'NI', 'NOINFLUENCE': 'NI', 'WITHOUTINFLUENCE': 'NI', 'N': 'NI', 'LI': 'LI', 'LOW': 'LI', 'LOWINFLUENCE': 'LI', 'L': 'LI', 'MI': 'MI', 'MEDIUM': 'MI', 'MEDIUMINFLUENCE': 'MI', 'M': 'MI', 'MODERATE': 'MI', 'HI': 'HI', 'HIGH': 'HI', 'HIGHINFLUENCE': 'HI', 'H': 'HI', 'VHI': 'VHI', 'VERYHIGH': 'VHI', 'VERYHIGHINFLUENCE': 'VHI', 'VH': 'VHI', 'V': 'VHI'}
    if text in aliases:
        return aliases[text]
    compact_persian = str(value).strip().replace(' ', '')
    if 'بدون' in compact_persian or compact_persian in {'هیچ', 'بیاثر', 'بدونتاثیر', 'بدونتأثیر'}:
        return 'NI'
    if 'کم' in compact_persian and 'خیلی' not in compact_persian and ('بسیار' not in compact_persian):
        return 'LI'
    if 'متوسط' in compact_persian:
        return 'MI'
    if ('زیاد' in compact_persian or 'بالا' in compact_persian) and 'خیلی' not in compact_persian and ('بسیار' not in compact_persian):
        return 'HI'
    if 'خیلیزیاد' in compact_persian or 'بسیارزیاد' in compact_persian or 'بسیار' in compact_persian:
        return 'VHI'
    raise ValueError(f"Invalid DEMATEL influence term '{value}'. Allowed terms: NI, LI, MI, HI, VHI or numeric ratings 0..4.")

def dematel_influence_to_cif_pair(value) -> np.ndarray:
    key = dematel_standardize_influence_term(value)
    row = dematel_CIF_DEMATEL_INFLUENCE_SCALE[key]
    mu, nu = (float(row['mu']), float(row['nu']))
    dematel_validate_cif_pair(mu, nu, label=key)
    return np.array([mu, nu], dtype=float)

def dematel_standardize_weight_term(value) -> str:
    if pd.isna(value):
        raise ValueError('Empty expert weight term found.')
    key = str(value).strip().upper().replace(' ', '')
    if key not in dematel_CIF_EXPERT_WEIGHT_SCALE:
        raise ValueError('Invalid expert WeightTerm. Allowed terms: AL, VL, L, ML, AE, MH, H, VH, AH.')
    return key

def dematel_create_influence_scale_dataframe() -> pd.DataFrame:
    rows = []
    for term, row in dematel_CIF_DEMATEL_INFLUENCE_SCALE.items():
        rows.append({'Term': term, 'Rating': row['rating'], 'Description': row['description'], 'mu': row['mu'], 'nu': row['nu'], 'pi': dematel_hesitation_degree(row['mu'], row['nu'])})
    return pd.DataFrame(rows)

def dematel_create_expert_weight_scale_dataframe() -> pd.DataFrame:
    rows = []
    for term, (mu, nu) in dematel_CIF_EXPERT_WEIGHT_SCALE.items():
        rows.append({'Term': term, 'Description': dematel_TERM_DESCRIPTIONS[term], 'mu': mu, 'nu': nu, 'pi': dematel_hesitation_degree(mu, nu)})
    return pd.DataFrame(rows)

def dematel_extract_matrix_format(df: pd.DataFrame) -> Tuple[List[str], np.ndarray]:
    """Extract square DEMATEL matrix from the usual wide matrix format."""
    df = dematel_clean_dataframe(df)
    if df.shape[1] < 3 or df.shape[0] < 2:
        raise ValueError('Matrix sheet must have at least two criteria.')
    row_criteria = df.iloc[:, 0].astype(str).str.strip().tolist()
    col_criteria = [str(c).strip() for c in df.columns[1:]]
    matrix_df = df.iloc[:, 1:].copy()
    keep_cols = [idx for idx, c in enumerate(col_criteria) if c and c.lower() != 'nan' and (not c.lower().startswith('unnamed'))]
    if len(keep_cols) != len(col_criteria):
        matrix_df = matrix_df.iloc[:, keep_cols]
        col_criteria = [col_criteria[i] for i in keep_cols]
    if matrix_df.shape[0] != matrix_df.shape[1]:
        raise ValueError('DEMATEL direct-influence sheet must be square: n source rows and n target columns.')
    if len(row_criteria) != len(col_criteria):
        raise ValueError('Number of source criteria and target criteria must be equal.')
    criteria = row_criteria
    term_matrix = np.empty((len(criteria), len(criteria)), dtype=object)
    for i in range(len(criteria)):
        for j in range(len(criteria)):
            term_matrix[i, j] = 'NI' if i == j else dematel_standardize_influence_term(matrix_df.iloc[i, j])
    return (criteria, term_matrix)

def dematel_extract_long_format(df: pd.DataFrame) -> Tuple[List[str], np.ndarray]:
    """Extract DEMATEL matrix from long format: Source | Target | Influence."""
    df = dematel_clean_dataframe(df)
    source_col = dematel_get_column_by_alias(df, dematel_SOURCE_ALIASES)
    target_col = dematel_get_column_by_alias(df, dematel_TARGET_ALIASES)
    influence_col = dematel_get_column_by_alias(df, dematel_INFLUENCE_ALIASES)
    if source_col is None or target_col is None or influence_col is None:
        raise ValueError('Long format requires Source, Target and Influence columns.')
    sources = df[source_col].astype(str).str.strip().tolist()
    targets = df[target_col].astype(str).str.strip().tolist()
    criteria = list(dict.fromkeys(sources + targets))
    n = len(criteria)
    index = {c: i for i, c in enumerate(criteria)}
    term_matrix = np.full((n, n), 'NI', dtype=object)
    for _, row in df.iterrows():
        src = str(row[source_col]).strip()
        trg = str(row[target_col]).strip()
        if src not in index or trg not in index:
            continue
        i, j = (index[src], index[trg])
        term_matrix[i, j] = 'NI' if i == j else dematel_standardize_influence_term(row[influence_col])
    return (criteria, term_matrix)

def dematel_extract_expert_matrix(df: pd.DataFrame) -> Tuple[List[str], np.ndarray, np.ndarray]:
    df = dematel_clean_dataframe(df)
    if df.empty:
        raise ValueError('Empty expert sheet.')
    try:
        criteria, term_matrix = dematel_extract_long_format(df)
    except Exception:
        criteria, term_matrix = dematel_extract_matrix_format(df)
    n = len(criteria)
    pair_matrix = np.zeros((n, n, 2), dtype=float)
    for i in range(n):
        for j in range(n):
            pair_matrix[i, j, :] = dematel_influence_to_cif_pair(term_matrix[i, j])
    return (criteria, term_matrix, pair_matrix)

def dematel_read_excel_file(uploaded_file) -> Tuple[Dict[str, pd.DataFrame], Optional[pd.DataFrame], List[str]]:
    sheets = pd.read_excel(uploaded_file, sheet_name=None, dtype=object)
    expert_sheets: Dict[str, pd.DataFrame] = {}
    expert_info = None
    skipped_sheets: List[str] = []
    for sheet_name, df in sheets.items():
        df = dematel_clean_dataframe(df)
        lower_name = sheet_name.lower().strip()
        if lower_name in dematel_EXPERT_INFO_SHEET_NAMES:
            expert_info = df
            skipped_sheets.append(sheet_name)
            continue
        if dematel_is_auxiliary_sheet(sheet_name):
            skipped_sheets.append(sheet_name)
            continue
        try:
            dematel_extract_expert_matrix(df)
            expert_sheets[sheet_name] = df
        except Exception:
            skipped_sheets.append(sheet_name)
    if len(expert_sheets) == 0:
        raise ValueError('No valid CIF-DEMATEL expert matrix was found. Use one square direct-influence matrix per expert.')
    return (expert_sheets, expert_info, skipped_sheets)

def dematel_calculate_expert_weights(expert_names: List[str], expert_info: Optional[pd.DataFrame]) -> pd.DataFrame:
    if expert_info is None or expert_info.empty:
        weights = np.ones(len(expert_names), dtype=float) / len(expert_names)
        return pd.DataFrame({'Expert': expert_names, 'Weight_Source': 'Equal', 'Term_or_Value': 'Equal', 'mu': np.nan, 'nu': np.nan, 'pi': np.nan, 'Raw_Expert_Value': np.nan, 'Expert_Weight': weights})
    df = dematel_clean_dataframe(expert_info)
    expert_col = dematel_get_column_by_alias(df, {'expert', 'decision_maker', 'dm', 'name'})
    weight_col = dematel_get_column_by_alias(df, {'weight'})
    term_col = dematel_get_column_by_alias(df, {'weightterm', 'term', 'linguistic', 'expertise', 'level'})
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
            rows.append({'Expert': expert, 'Weight_Source': 'Equal fallback', 'Term_or_Value': 'Missing', 'mu': np.nan, 'nu': np.nan, 'pi': np.nan, 'Raw_Expert_Value': 1.0})
            continue
        if weight_col is not None and (not pd.isna(row[weight_col])):
            raw_value = float(str(row[weight_col]).translate(dematel_PERSIAN_DIGIT_MAP))
            rows.append({'Expert': expert, 'Weight_Source': 'Numeric weight', 'Term_or_Value': raw_value, 'mu': np.nan, 'nu': np.nan, 'pi': np.nan, 'Raw_Expert_Value': raw_value})
        elif term_col is not None and (not pd.isna(row[term_col])):
            term = dematel_standardize_weight_term(row[term_col])
            mu, nu = dematel_CIF_EXPERT_WEIGHT_SCALE[term]
            pi = dematel_hesitation_degree(mu, nu)
            denominator = max(1e-12, 1.0 - pi)
            raw_value = mu + pi * (mu / denominator)
            rows.append({'Expert': expert, 'Weight_Source': 'CIF expertise term', 'Term_or_Value': term, 'mu': mu, 'nu': nu, 'pi': pi, 'Raw_Expert_Value': raw_value})
        else:
            rows.append({'Expert': expert, 'Weight_Source': 'Equal fallback', 'Term_or_Value': 'Missing', 'mu': np.nan, 'nu': np.nan, 'pi': np.nan, 'Raw_Expert_Value': 1.0})
    weights_df = pd.DataFrame(rows)
    raw = weights_df['Raw_Expert_Value'].astype(float).clip(lower=0).to_numpy(dtype=float)
    weights = np.ones(len(expert_names), dtype=float) / len(expert_names) if raw.sum() <= 0 else raw / raw.sum()
    weights_df['Expert_Weight'] = weights
    return weights_df

def dematel_aggregate_experts(expert_sheets: Dict[str, pd.DataFrame], expert_weights: np.ndarray) -> Tuple[List[str], Dict[str, pd.DataFrame], np.ndarray, np.ndarray, np.ndarray]:
    term_matrices: Dict[str, pd.DataFrame] = {}
    pair_matrices = []
    reference_criteria = None
    for sheet_name, df in expert_sheets.items():
        criteria, term_matrix, pair_matrix = dematel_extract_expert_matrix(df)
        if reference_criteria is None:
            reference_criteria = criteria
        elif criteria != reference_criteria:
            raise ValueError(f"Criteria in sheet '{sheet_name}' are not consistent with the first expert sheet.")
        pair_matrices.append(pair_matrix)
        term_matrices[sheet_name] = pd.DataFrame(term_matrix, index=criteria, columns=criteria)
    arrays = np.stack(pair_matrices, axis=0)
    weights = np.asarray(expert_weights, dtype=float)
    weights = weights / weights.sum()
    mus = arrays[:, :, :, 0]
    nus = arrays[:, :, :, 1]
    mu_agg = 1.0 - np.prod(np.power(1.0 - mus, weights[:, None, None]), axis=0)
    nu_agg = np.prod(np.power(nus, weights[:, None, None]), axis=0)
    n = len(reference_criteria)
    radius = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            distances = np.sqrt((mu_agg[i, j] - mus[:, i, j]) ** 2 + (nu_agg[i, j] - nus[:, i, j]) ** 2)
            radius[i, j] = float(np.max(distances))
    for i in range(n):
        mu_agg[i, i] = 0.0
        nu_agg[i, i] = 1.0
        radius[i, i] = 0.0
    aggregated = np.stack([mu_agg, nu_agg, radius], axis=2)
    return (reference_criteria, term_matrices, arrays, aggregated, weights)

def dematel_calculate_score_matrix(aggregated: np.ndarray, lambda_value: float) -> np.ndarray:
    mu = aggregated[:, :, 0]
    nu = aggregated[:, :, 1]
    r = aggregated[:, :, 2]
    return mu - nu + (2.0 * lambda_value - 1.0) * r

def dematel_calculate_crisp_matrix(score_matrix: np.ndarray) -> np.ndarray:
    crisp = (score_matrix + 1.0) / 2.0
    crisp = np.clip(crisp, 0.0, 1.0)
    np.fill_diagonal(crisp, 0.0)
    return crisp

def dematel_calculate_dematel(criteria: List[str], crisp_matrix: np.ndarray, normalization_mode: str, threshold_factor: float=1.0) -> Tuple[pd.DataFrame, Dict[str, np.ndarray], pd.DataFrame, float, float]:
    Z = np.asarray(crisp_matrix, dtype=float).copy()
    np.fill_diagonal(Z, 0.0)
    n = Z.shape[0]
    row_max = float(np.max(np.sum(Z, axis=1))) if n else 0.0
    col_max = float(np.max(np.sum(Z, axis=0))) if n else 0.0
    if normalization_mode.startswith('Max row and column'):
        denominator = max(row_max, col_max)
    else:
        denominator = row_max
    alpha = 0.0 if denominator <= 0 else 1.0 / denominator
    X = alpha * Z
    if n > 0:
        try:
            rho = float(max(abs(np.linalg.eigvals(X))))
        except Exception:
            rho = 0.0
        if rho >= 0.999:
            X = X * (0.999 / (rho + 1e-12))
    I = np.eye(n)
    try:
        T = np.linalg.solve((I - X).T, X.T).T
    except np.linalg.LinAlgError:
        T = X @ np.linalg.pinv(I - X)
    D = T.sum(axis=1)
    R = T.sum(axis=0)
    prominence = D + R
    relation = D - R
    group = np.where(relation >= 0, 'Cause', 'Effect')
    result_df = pd.DataFrame({'Criterion': criteria, 'D_Dispatching': D, 'R_Receiving': R, 'Prominence_D_plus_R': prominence, 'Relation_D_minus_R': relation, 'Group': group})
    result_df['Rank_by_Prominence'] = result_df['Prominence_D_plus_R'].rank(ascending=False, method='dense').astype(int)
    result_df = result_df.sort_values(['Rank_by_Prominence', 'Criterion']).reset_index(drop=True)
    off_diag = T[~np.eye(n, dtype=bool)] if n > 1 else np.array([])
    base_threshold = float(off_diag.mean()) if off_diag.size else 0.0
    threshold = base_threshold * threshold_factor
    edge_rows = []
    for i, source in enumerate(criteria):
        for j, target in enumerate(criteria):
            if i != j and T[i, j] > threshold:
                edge_rows.append({'Source': source, 'Target': target, 'Total_Relation': T[i, j]})
    edges_df = pd.DataFrame(edge_rows).sort_values('Total_Relation', ascending=False).reset_index(drop=True) if edge_rows else pd.DataFrame(columns=['Source', 'Target', 'Total_Relation'])
    matrices = {'crisp': Z, 'normalized': X, 'total_relation': T}
    return (result_df, matrices, edges_df, threshold, alpha)

def dematel_matrix_to_dataframe(matrix: np.ndarray, criteria: List[str]) -> pd.DataFrame:
    return pd.DataFrame(matrix, index=criteria, columns=criteria)

def dematel_aggregated_component_to_dataframe(aggregated: np.ndarray, criteria: List[str], component_index: int) -> pd.DataFrame:
    return pd.DataFrame(aggregated[:, :, component_index], index=criteria, columns=criteria)

def dematel_sample_workbook_data():
    criteria = ['C1 - Data Availability', 'C2 - Top Management Support', 'C3 - Technological Capability', 'C4 - Stakeholder Collaboration', 'C5 - Financial Resources']
    expert_1 = [['NI', 'HI', 'MI', 'LI', 'MI'], ['LI', 'NI', 'HI', 'MI', 'LI'], ['MI', 'HI', 'NI', 'HI', 'MI'], ['LI', 'MI', 'HI', 'NI', 'HI'], ['MI', 'LI', 'MI', 'HI', 'NI']]
    expert_2 = [['NI', 'MI', 'HI', 'LI', 'LI'], ['MI', 'NI', 'HI', 'MI', 'MI'], ['LI', 'HI', 'NI', 'VHI', 'MI'], ['MI', 'LI', 'HI', 'NI', 'HI'], ['LI', 'MI', 'LI', 'HI', 'NI']]
    expert_3 = [['NI', 'HI', 'MI', 'MI', 'LI'], ['LI', 'NI', 'VHI', 'HI', 'MI'], ['MI', 'HI', 'NI', 'HI', 'HI'], ['LI', 'MI', 'MI', 'NI', 'VHI'], ['MI', 'LI', 'MI', 'HI', 'NI']]
    return (criteria, expert_1, expert_2, expert_3)

def dematel_matrix_df_from_terms(criteria: List[str], terms: List[List[str]]) -> pd.DataFrame:
    df = pd.DataFrame(terms, columns=criteria)
    df.insert(0, 'Criterion', criteria)
    return df

def dematel_create_template_excel() -> bytes:
    output = BytesIO()
    criteria, expert_1, expert_2, expert_3 = dematel_sample_workbook_data()
    expert_info = pd.DataFrame({'Expert': ['Expert_1', 'Expert_2', 'Expert_3'], 'WeightTerm': ['AH', 'VH', 'H']})
    readme = pd.DataFrame({'Guide': ['Create one sheet per expert.', 'Use a square direct-influence matrix: first column Criterion, first row target criteria.', 'Allowed influence terms: NI, LI, MI, HI, VHI. Numeric ratings 0, 1, 2, 3, 4 are also accepted.', 'Optional Expert_Info sheet can use WeightTerm or numeric Weight.', 'The diagonal is automatically interpreted as NI.']})
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dematel_matrix_df_from_terms(criteria, expert_1).to_excel(writer, sheet_name='Expert_1', index=False)
        dematel_matrix_df_from_terms(criteria, expert_2).to_excel(writer, sheet_name='Expert_2', index=False)
        dematel_matrix_df_from_terms(criteria, expert_3).to_excel(writer, sheet_name='Expert_3', index=False)
        expert_info.to_excel(writer, sheet_name='Expert_Info', index=False)
        dematel_create_influence_scale_dataframe().to_excel(writer, sheet_name='CIF_DEMATEL_Scale', index=False)
        dematel_create_expert_weight_scale_dataframe().to_excel(writer, sheet_name='ExpertWeight_Scale', index=False)
        readme.to_excel(writer, sheet_name='README', index=False)
    return output.getvalue()

def dematel_create_excel_output(expert_sheets: Dict[str, pd.DataFrame], skipped_sheets: List[str], influence_scale_df: pd.DataFrame, expert_weight_scale_df: pd.DataFrame, expert_weights_df: pd.DataFrame, term_matrices: Dict[str, pd.DataFrame], aggregated: np.ndarray, score_matrix: np.ndarray, crisp_matrix: np.ndarray, matrices: Dict[str, np.ndarray], result_df: pd.DataFrame, edges_df: pd.DataFrame, criteria: List[str], lambda_value: float, normalization_mode: str, threshold: float, alpha: float) -> bytes:
    output = BytesIO()
    params = pd.DataFrame({'Parameter': ['Method', 'Lambda_Attitude', 'Defuzzification', 'Crisp_Transform', 'Normalization_Mode', 'Normalization_Alpha', 'Network_Threshold', 'Number_of_Experts', 'Number_of_Criteria'], 'Value': ['CIF-DEMATEL', lambda_value, 'Score = mu - nu + (2lambda - 1)r', 'Crisp = clipped((Score + 1) / 2)', normalization_mode, alpha, threshold, len(expert_sheets), len(criteria)]})
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        params.to_excel(writer, sheet_name='Parameters', index=False)
        influence_scale_df.to_excel(writer, sheet_name='CIF_DEMATEL_Scale', index=False)
        expert_weight_scale_df.to_excel(writer, sheet_name='ExpertWeight_Scale', index=False)
        expert_weights_df.to_excel(writer, sheet_name='Expert_Weights', index=False)
        for sheet_name, df in expert_sheets.items():
            df.to_excel(writer, sheet_name=f'Input_{sheet_name[:22]}', index=False)
        for sheet_name, terms_df in term_matrices.items():
            terms_df.to_excel(writer, sheet_name=f'Terms_{sheet_name[:22]}')
        dematel_aggregated_component_to_dataframe(aggregated, criteria, 0).to_excel(writer, sheet_name='Aggregated_mu')
        dematel_aggregated_component_to_dataframe(aggregated, criteria, 1).to_excel(writer, sheet_name='Aggregated_nu')
        dematel_aggregated_component_to_dataframe(aggregated, criteria, 2).to_excel(writer, sheet_name='Radius_r')
        dematel_matrix_to_dataframe(score_matrix, criteria).to_excel(writer, sheet_name='Score_Matrix')
        dematel_matrix_to_dataframe(crisp_matrix, criteria).to_excel(writer, sheet_name='Crisp_Direct_Matrix')
        dematel_matrix_to_dataframe(matrices['normalized'], criteria).to_excel(writer, sheet_name='Normalized_Matrix')
        dematel_matrix_to_dataframe(matrices['total_relation'], criteria).to_excel(writer, sheet_name='Total_Relation_T')
        result_df.to_excel(writer, sheet_name='DEMATEL_Results', index=False)
        edges_df.to_excel(writer, sheet_name='Network_Edges', index=False)
        pd.DataFrame({'Skipped_sheets': skipped_sheets}).to_excel(writer, sheet_name='Skipped_Sheets', index=False)
    return output.getvalue()

def dematel_show_heatmap(df: pd.DataFrame, title: str):
    if dematel_PLOTLY_AVAILABLE:
        fig = px.imshow(df, text_auto='.3f', aspect='auto', color_continuous_scale=['#FFFDF8', '#F4D58D', '#7BAE7F', '#1E4C78', '#102A43'], title=title)
        fig.update_layout(height=520, margin=dict(l=30, r=30, t=60, b=30))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(df.round(6), use_container_width=True)

def dematel_show_cause_effect_map(result_df: pd.DataFrame):
    plot_df = result_df.copy()
    plot_df['Label'] = plot_df['Criterion'].map(dematel_display_criterion_label)
    x_mean = float(plot_df['Prominence_D_plus_R'].mean())
    if dematel_PLOTLY_AVAILABLE:
        fig = px.scatter(plot_df, x='Prominence_D_plus_R', y='Relation_D_minus_R', color='Group', text='Label', size='Prominence_D_plus_R', hover_data=['D_Dispatching', 'R_Receiving', 'Rank_by_Prominence'], color_discrete_map={'Cause': '#1E4C78', 'Effect': '#FFC857'}, title='Causal Relation Map: Prominence vs Relation')
        fig.add_hline(y=0, line_dash='dash', line_color='#64748b')
        fig.add_vline(x=x_mean, line_dash='dot', line_color='#1E4C78')
        fig.update_traces(textposition='top center')
        fig.update_layout(height=520, margin=dict(l=30, r=30, t=60, b=30))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(plot_df.round(6), use_container_width=True)

def dematel_show_network(criteria: List[str], total_relation: np.ndarray, threshold: float):
    if not dematel_PLOTLY_AVAILABLE:
        return
    n = len(criteria)
    labels = dematel_display_criterion_labels(criteria)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x = np.cos(angles)
    y = np.sin(angles)
    edge_x = []
    edge_y = []
    annotations = []
    for i in range(n):
        for j in range(n):
            if i != j and total_relation[i, j] > threshold:
                edge_x += [x[i], x[j], None]
                edge_y += [y[i], y[j], None]
                mid_x, mid_y = ((x[i] + x[j]) / 2.0, (y[i] + y[j]) / 2.0)
                annotations.append(dict(x=mid_x, y=mid_y, text=f'{total_relation[i, j]:.2f}', showarrow=False, font=dict(size=10, color='#496356')))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=1.7, color='rgba(39,138,89,0.35)'), hoverinfo='none', name='Influential relations'))
    fig.add_trace(go.Scatter(x=x, y=y, mode='markers+text', text=labels, textposition='top center', marker=dict(size=26, color='#2FA66A', line=dict(width=2, color='#ffffff')), name='Criteria'))
    fig.update_layout(title=f'Network Map - Edges above threshold {threshold:.4f}', showlegend=False, height=560, annotations=annotations, xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor='x', scaleratio=1), margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)

def dematel_run_app():
    st.set_page_config(page_title='CIF-DEMATEL | Executive Edition', page_icon='D', layout='wide', initial_sidebar_state='expanded')
    dematel_apply_custom_style()
    dematel_hamburger_menu()
    dematel_hero_section()
    st.markdown('<div class="three-d-divider"></div>', unsafe_allow_html=True)
    dematel_header_panels()
    dematel_intro_card()
    with st.sidebar:
        st.markdown('\n            <div class="sidebar-block">\n                <h4>Developer</h4>\n                <p><strong>Dr. Saeed Alinejad - Shiraz University, Iran</strong></p>\n            </div>\n            ', unsafe_allow_html=True)
        lambda_value = st.slider('Lambda attitude parameter', 0.0, 1.0, 0.5, 0.05)
        normalization_mode = st.selectbox('Normalization Mode', ['Max row and column sum', 'Max row sum only'], index=0, help='The first option is conservative and stable; the second reproduces the common row-sum DEMATEL normalization.')
        threshold_factor = st.slider('Network threshold multiplier', 0.5, 2.0, 1.0, 0.05)
        st.markdown('\n            <div class="sidebar-block">\n                <h4>Allowed Influence Terms</h4>\n                <ul>\n                    <li>NI = No Influence = 0</li>\n                    <li>LI = Low Influence = 1</li>\n                    <li>MI = Medium Influence = 2</li>\n                    <li>HI = High Influence = 3</li>\n                    <li>VHI = Very High Influence = 4</li>\n                </ul>\n            </div>\n            ', unsafe_allow_html=True)
        st.markdown(f'\n            <div class="sidebar-block">\n                <h4>Server</h4>\n                <p><code>{dematel_DISPLAY_URL}</code></p>\n                <p>Change DISPLAY_URL at the top of the file if your PC IP is different.</p>\n            </div>\n            ', unsafe_allow_html=True)
        st.download_button(label='Download Input Template', data=dematel_create_template_excel(), file_name='cif_dematel_input_template.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    influence_scale_df = dematel_create_influence_scale_dataframe()
    expert_weight_scale_df = dematel_create_expert_weight_scale_dataframe()
    st.markdown('<div id="active-scale"></div>', unsafe_allow_html=True)
    scale_tab, expert_scale_tab = st.tabs(['DEMATEL Influence Scale', 'Expert Weight Scale'])
    with scale_tab:
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.subheader('Active CIF-DEMATEL Influence Scale')
        st.dataframe(influence_scale_df.round(6), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with expert_scale_tab:
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.subheader('Expert Weight Linguistic Scale')
        st.dataframe(expert_weight_scale_df.round(6), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div id="upload-workbook"></div>', unsafe_allow_html=True)
    st.markdown('\n        <div class="upload-zone-card upload-zone-gold-final" style="background:radial-gradient(circle at 9% 12%, rgba(255,255,255,0.45), transparent 28%), radial-gradient(circle at 88% 16%, rgba(255,244,210,0.38), transparent 32%), linear-gradient(135deg,#6F4E00 0%,#9B7208 23%,#D4AF37 52%,#FFD166 74%,#8A6508 100%) !important; border:2px solid rgba(255,244,210,0.98) !important; box-shadow:0 30px 68px rgba(111,78,0,0.38), 0 0 0 5px rgba(255,209,102,0.22), 0 6px 0 rgba(255,255,255,0.28) inset !important;">\n            <div class="upload-zone-badge" style="display:inline-block; color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; background:rgba(16,42,67,0.36) !important; border:1px solid rgba(255,255,255,0.58) !important; padding:8px 16px !important; border-radius:999px !important; font-weight:950 !important; letter-spacing:0.9px !important; text-transform:uppercase !important; text-shadow:0 2px 10px rgba(0,0,0,0.35) !important;">Upload Zone</div>\n            <div class="upload-zone-title" style="color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; opacity:1 !important; font-size:28px !important; font-weight:950 !important; line-height:1.25 !important; margin:30px 0 26px 0 !important; text-shadow:0 4px 16px rgba(0,0,0,0.68) !important;">Upload Your CIF-DEMATEL Excel Workbook</div>\n            <div id="force-upload-desc-white" class="upload-zone-description" style="margin-top:18px !important; color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; opacity:1 !important; font-size:16px !important; font-weight:900 !important; line-height:1.9 !important; text-shadow:0 4px 18px rgba(0,0,0,0.78) !important; background:rgba(16,42,67,0.22) !important; border:1px solid rgba(255,255,255,0.24) !important; border-radius:14px !important; padding:12px 14px !important;"><span style="color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; opacity:1 !important; font-weight:900 !important; text-shadow:0 4px 18px rgba(0,0,0,0.78) !important;">Load expert direct-influence matrices. The app will calculate aggregated CIF matrices, crisp direct-relation matrix, normalized relation matrix, total relation matrix, and cause/effect classification.</span></div>\n        </div>\n        ', unsafe_allow_html=True)
    uploaded_file = st.file_uploader('Upload CIF-DEMATEL Excel workbook', type=['xlsx'])
    if uploaded_file is None:
        st.info('Download the template from the sidebar, fill your expert matrices, then upload the workbook here.')
        return
    try:
        expert_sheets, expert_info, skipped_sheets = dematel_read_excel_file(uploaded_file)
        expert_names = list(expert_sheets.keys())
        expert_weights_df = dematel_calculate_expert_weights(expert_names, expert_info)
        criteria, term_matrices, arrays, aggregated, normalized_weights = dematel_aggregate_experts(expert_sheets, expert_weights_df['Expert_Weight'].to_numpy(dtype=float))
        score_matrix = dematel_calculate_score_matrix(aggregated, lambda_value=lambda_value)
        crisp_matrix = dematel_calculate_crisp_matrix(score_matrix)
        result_df, matrices, edges_df, threshold, alpha = dematel_calculate_dematel(criteria, crisp_matrix, normalization_mode=normalization_mode, threshold_factor=threshold_factor)
        display_criteria = dematel_display_criterion_labels(criteria)
        top_row = result_df.sort_values('Rank_by_Prominence').iloc[0]
        cause_count = int((result_df['Group'] == 'Cause').sum())
        effect_count = int((result_df['Group'] == 'Effect').sum())
        st.markdown('<div id="results-dashboard"></div>', unsafe_allow_html=True)
        st.success('CIF-DEMATEL calculations completed successfully.')
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric('Valid Expert Sheets', len(expert_sheets))
        with c2:
            st.metric('Criteria', len(criteria))
        with c3:
            st.metric('Top Prominence', dematel_display_criterion_label(top_row['Criterion']))
        with c4:
            st.metric('Cause Group', cause_count)
        with c5:
            st.metric('Effect Group', effect_count)
        overview_tab, matrix_tab, visual_tab, export_tab = st.tabs(['Overview', 'Matrices', 'Visual Maps', 'Export'])
        with overview_tab:
            dematel_render_sheet_summary(expert_names, skipped_sheets)
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Expert Weights')
            st.dataframe(expert_weights_df.round(6), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Final CIF-DEMATEL Results')
            display_result = result_df.copy()
            display_result['Criterion'] = display_result['Criterion'].map(dematel_display_criterion_label)
            st.dataframe(display_result.round(6), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Network Edges above Threshold')
            display_edges = edges_df.copy()
            if not display_edges.empty:
                display_edges['Source'] = display_edges['Source'].map(dematel_display_criterion_label)
                display_edges['Target'] = display_edges['Target'].map(dematel_display_criterion_label)
            st.dataframe(display_edges.round(6), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with matrix_tab:
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Aggregated Membership Matrix (mu)')
            st.dataframe(dematel_matrix_to_dataframe(aggregated[:, :, 0], display_criteria).round(6), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Aggregated Non-membership Matrix (nu)')
            st.dataframe(dematel_matrix_to_dataframe(aggregated[:, :, 1], display_criteria).round(6), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Circular Radius Matrix (r)')
            st.dataframe(dematel_matrix_to_dataframe(aggregated[:, :, 2], display_criteria).round(6), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Crisp Direct-Relation Matrix')
            st.dataframe(dematel_matrix_to_dataframe(crisp_matrix, display_criteria).round(6), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Total Relation Matrix T')
            st.dataframe(dematel_matrix_to_dataframe(matrices['total_relation'], display_criteria).round(6), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with visual_tab:
            dematel_show_cause_effect_map(result_df)
            dematel_show_heatmap(dematel_matrix_to_dataframe(matrices['total_relation'], display_criteria), 'Total Relation Matrix Heatmap')
            dematel_show_network(criteria, matrices['total_relation'], threshold)
        with export_tab:
            excel_output = dematel_create_excel_output(expert_sheets=expert_sheets, skipped_sheets=skipped_sheets, influence_scale_df=influence_scale_df, expert_weight_scale_df=expert_weight_scale_df, expert_weights_df=expert_weights_df, term_matrices=term_matrices, aggregated=aggregated, score_matrix=score_matrix, crisp_matrix=crisp_matrix, matrices=matrices, result_df=result_df, edges_df=edges_df, criteria=criteria, lambda_value=lambda_value, normalization_mode=normalization_mode, threshold=threshold, alpha=alpha)
            st.markdown('<div id="download-results"></div>', unsafe_allow_html=True)
            st.download_button(label='Download Excel Results', data=excel_output, file_name='cif_dematel_results.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            st.caption(f'Normalization alpha = {alpha:.6f} | Network threshold = {threshold:.6f}')
    except Exception as error:
        st.error(f'Error: {error}')
    st.markdown('\n        <div class="footer-note">\n            Executive CIF-DEMATEL Interface - Designed for professional circular intuitionistic fuzzy causal analytics.\n        </div>\n        ', unsafe_allow_html=True)

def dematel_is_running_inside_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


# ============================== SWARA MODULE ==============================
import os
os.environ.setdefault('STREAMLIT_THEME_BASE', 'light')
os.environ.setdefault('STREAMLIT_BROWSER_GATHER_USAGE_STATS', 'false')
import html
import re
import sys
from io import BytesIO
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import streamlit as st
swara_PORT = 8801
swara_SERVER_ADDRESS = '0.0.0.0'
swara_DISPLAY_URL = 'http://192.168.0.100:8801/'
swara_PERSIAN_ARABIC_TEXT_PATTERN = re.compile('[\\u0600-\\u06FF]')

def swara_display_criterion_label(value) -> str:
    """Return an English-safe criterion label for dashboard display.

    The calculation keeps the original uploaded criterion names unchanged.
    For dashboard cards and tables, if a user uploads a Persian descriptor such as
    "C1 - Persian text", the app displays only the Latin code "C1" to keep the
    interface fully English.
    """
    text = str(value).strip()
    if not swara_PERSIAN_ARABIC_TEXT_PATTERN.search(text):
        return text
    parts = re.split('\\s*[-–—|:]\\s*', text, maxsplit=1)
    if parts and parts[0].strip() and (not swara_PERSIAN_ARABIC_TEXT_PATTERN.search(parts[0])):
        return parts[0].strip()
    latin_only = re.sub('[\\u0600-\\u06FF\\u200c\\u200f\\u202a-\\u202e]+', '', text)
    latin_only = re.sub('\\s+', ' ', latin_only).strip(' -–—|:')
    return latin_only if latin_only else 'Criterion'

def swara_display_criterion_labels(values) -> List[str]:
    return [swara_display_criterion_label(value) for value in values]

def swara_apply_custom_style():
    st.markdown('\n        <style>\n        @import url(\'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap\');\n\n        :root {\n            /* User-selected palette: true soft emerald green + deep royal blue. */\n            --cif-emerald: #2FA66A;\n            --cif-emerald-dark: #247A50;\n            --cif-forest: #164A34;\n            --cif-lapis: #123B2A;\n            --cif-ink: #102B20;\n            --cif-text: #102018;\n            --cif-muted: #496356;\n            --cif-cream: #FBFFFC;\n            --cif-card: rgba(255, 255, 255, 0.94);\n            --cif-border: rgba(39, 138, 89, 0.20);\n            --cif-gold: #C5962D;\n        }\n\n        html, body, [class*="css"] {\n            font-family: \'Inter\', \'Segoe UI\', sans-serif;\n        }\n\n        .stApp {\n            background:\n                radial-gradient(circle at 8% 7%, rgba(47, 166, 106, 0.22), transparent 26%),\n                radial-gradient(circle at 92% 10%, rgba(47, 166, 106, 0.20), transparent 28%),\n                radial-gradient(circle at 76% 92%, rgba(197, 150, 45, 0.11), transparent 28%),\n                linear-gradient(145deg, #FBFFFC 0%, #F6FFF9 32%, #F1FFF6 68%, #ffffff 100%);\n            color: var(--cif-text);\n        }\n\n        .block-container {\n            padding-top: 1.45rem;\n            padding-bottom: 2rem;\n            max-width: 1480px;\n        }\n\n        /* General readable text: fixes white/low-contrast native Streamlit headings and labels. */\n        h1, h2, h3, h4, h5, h6,\n        .stMarkdown, .stMarkdown p, .stMarkdown li,\n        .stCaptionContainer, .stText, label,\n        div[data-testid="stWidgetLabel"], div[data-testid="stWidgetLabel"] p,\n        div[data-testid="stMarkdownContainer"] p,\n        div[data-testid="stMarkdownContainer"] li,\n        div[data-testid="stMetricLabel"], div[data-testid="stMetricDelta"],\n        .caption-note, .muted {\n            color: var(--cif-text) !important;\n        }\n\n        h1, h2, h3, h4 {\n            color: var(--cif-ink) !important;\n            letter-spacing: 0.15px;\n        }\n\n        p, li, td, th, span {\n            text-rendering: optimizeLegibility;\n        }\n\n        /* Streamlit\'s native sidebar toggle is turned into a cleaner hamburger-style control. */\n        [data-testid="collapsedControl"],\n        [data-testid="stSidebarCollapsedControl"],\n        [data-testid="stSidebarCollapseButton"] {\n            border-radius: 18px !important;\n            background: linear-gradient(135deg, var(--cif-emerald-dark), var(--cif-emerald) 42%, var(--cif-forest)) !important;\n            box-shadow: 0 18px 38px rgba(39, 138, 89, 0.24), 0 2px 0 rgba(255,255,255,0.34) inset !important;\n            border: 1px solid rgba(255, 255, 255, 0.72) !important;\n        }\n\n        [data-testid="collapsedControl"] button,\n        [data-testid="stSidebarCollapsedControl"] button,\n        [data-testid="stSidebarCollapseButton"] button,\n        [data-testid="collapsedControl"] svg,\n        [data-testid="stSidebarCollapsedControl"] svg,\n        [data-testid="stSidebarCollapseButton"] svg {\n            color: #ffffff !important;\n            stroke-width: 2.8px !important;\n        }\n\n        .hamburger-shell {\n            position: sticky;\n            top: 0.75rem;\n            z-index: 999;\n            max-width: 430px;\n            margin: 0 0 16px auto;\n            border-radius: 22px;\n            background:\n                radial-gradient(circle at 10% 10%, rgba(255,255,255,0.45), transparent 28%),\n                linear-gradient(135deg, var(--cif-emerald-dark) 0%, var(--cif-emerald) 42%, var(--cif-forest) 100%);\n            border: 1px solid rgba(255, 255, 255, 0.62);\n            box-shadow: 0 22px 46px rgba(39, 138, 89, 0.22), 0 4px 0 rgba(255,255,255,0.25) inset;\n            backdrop-filter: blur(16px);\n            overflow: hidden;\n        }\n\n        .hamburger-shell summary {\n            list-style: none;\n            cursor: pointer;\n            user-select: none;\n            padding: 13px 16px;\n            display: flex;\n            align-items: center;\n            gap: 12px;\n        }\n\n        .hamburger-shell summary::-webkit-details-marker { display: none; }\n\n        .hamburger-icon {\n            width: 42px;\n            height: 42px;\n            display: inline-flex;\n            flex-direction: column;\n            justify-content: center;\n            align-items: center;\n            gap: 5px;\n            border-radius: 15px;\n            background: rgba(255, 255, 255, 0.20);\n            box-shadow: 0 9px 20px rgba(7, 22, 63, 0.16), 0 2px 0 rgba(255,255,255,0.28) inset;\n            transition: all 0.25s ease;\n        }\n\n        .hamburger-icon span {\n            width: 20px;\n            height: 2.5px;\n            border-radius: 999px;\n            background: #ffffff;\n            box-shadow: 0 1px 4px rgba(7,22,63,0.18);\n            transition: all 0.25s ease;\n        }\n\n        .hamburger-shell[open] .hamburger-icon span:nth-child(1) { transform: translateY(7.5px) rotate(45deg); }\n        .hamburger-shell[open] .hamburger-icon span:nth-child(2) { opacity: 0; transform: scaleX(0.2); }\n        .hamburger-shell[open] .hamburger-icon span:nth-child(3) { transform: translateY(-7.5px) rotate(-45deg); }\n\n        .hamburger-title {\n            color: #ffffff !important;\n            font-size: 15px;\n            font-weight: 950;\n            letter-spacing: 0.4px;\n            text-shadow: 0 2px 8px rgba(7, 22, 63, 0.28);\n        }\n\n        .hamburger-pill {\n            margin-left: auto;\n            padding: 7px 10px;\n            border-radius: 999px;\n            color: #ffffff !important;\n            background: rgba(255,255,255,0.17);\n            border: 1px solid rgba(255,255,255,0.30);\n            font-size: 11px;\n            font-weight: 900;\n            text-transform: uppercase;\n            letter-spacing: 0.9px;\n        }\n\n        .hamburger-links {\n            display: grid;\n            grid-template-columns: repeat(2, minmax(0, 1fr));\n            gap: 9px;\n            padding: 0 14px 14px 14px;\n        }\n\n        .hamburger-links a {\n            text-decoration: none !important;\n            color: var(--cif-ink) !important;\n            font-size: 13px;\n            font-weight: 900;\n            padding: 10px 12px;\n            border-radius: 14px;\n            background: rgba(255, 255, 255, 0.92);\n            border: 1px solid rgba(255,255,255,0.70);\n            box-shadow: 0 8px 18px rgba(7,22,63,0.11);\n            transition: all 0.22s ease;\n        }\n\n        .hamburger-links a:hover {\n            transform: translateY(-2px);\n            color: var(--cif-emerald-dark) !important;\n            background: #ffffff;\n            box-shadow: 0 12px 24px rgba(7,22,63,0.15);\n        }\n\n        @media (max-width: 760px) {\n            .hamburger-shell {\n                margin-left: 0;\n                max-width: 100%;\n            }\n            .hamburger-links { grid-template-columns: 1fr; }\n            .hero-title { font-size: 34px !important; }\n        }\n\n        .hero-card {\n            position: relative;\n            overflow: hidden;\n            border-radius: 30px;\n            padding: 34px 34px 28px 34px;\n            margin-bottom: 20px;\n            background:\n                radial-gradient(circle at 8% 10%, rgba(255,255,255,0.78), transparent 25%),\n                radial-gradient(circle at 92% 16%, rgba(47,166,106,0.22), transparent 30%),\n                linear-gradient(135deg, #ffffff 0%, #F4FFF8 34%, #D6F5E2 72%, #FFF9EF 100%);\n            border: 1px solid rgba(39, 138, 89, 0.22);\n            box-shadow:\n                0 30px 72px rgba(39, 138, 89, 0.16),\n                0 10px 24px rgba(255, 255, 255, 0.94) inset,\n                0 -14px 28px rgba(18, 74, 52, 0.07) inset;\n        }\n\n        .hero-card::before {\n            content: "";\n            position: absolute;\n            inset: 0;\n            background: linear-gradient(120deg, transparent 0%, rgba(255,255,255,0.72) 38%, transparent 74%);\n            transform: translateX(-100%);\n            animation: shine 7s linear infinite;\n            pointer-events: none;\n        }\n\n        @keyframes shine { 100% { transform: translateX(160%); } }\n\n        .hero-topline {\n            display: inline-block;\n            padding: 8px 14px;\n            border-radius: 999px;\n            background: rgba(47, 166, 106, 0.13);\n            border: 1px solid rgba(39, 138, 89, 0.25);\n            color: var(--cif-emerald-dark) !important;\n            font-size: 12px;\n            font-weight: 900;\n            letter-spacing: 1.35px;\n            text-transform: uppercase;\n            margin-bottom: 16px;\n            box-shadow: 0 8px 20px rgba(39, 138, 89, 0.10), 0 2px 0 rgba(255,255,255,0.90) inset;\n        }\n\n        .hero-title {\n            font-size: 46px;\n            font-weight: 900;\n            line-height: 1.05;\n            margin: 0 0 10px 0;\n            color: var(--cif-ink) !important;\n            text-shadow: 0 2px 0 rgba(255,255,255,0.84);\n        }\n\n        .hero-subtitle {\n            font-size: 16px;\n            line-height: 1.72;\n            color: var(--cif-lapis) !important;\n            max-width: 1040px;\n            margin-bottom: 0;\n            font-weight: 550;\n        }\n\n        .three-d-divider {\n            height: 10px;\n            margin: 4px 0 18px 0;\n            border-radius: 999px;\n            background: linear-gradient(90deg, rgba(47,166,106,0.05), rgba(47,166,106,0.54), rgba(18,74,52,0.36), rgba(197,150,45,0.22), rgba(47,166,106,0.05));\n            box-shadow: 0 10px 20px rgba(39,138,89,0.11), 0 2px 0 rgba(255,255,255,0.86) inset;\n        }\n\n        .info-grid {\n            display: grid;\n            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));\n            gap: 16px;\n            margin-bottom: 18px;\n        }\n\n        .mini-card, .glass-panel, .table-card, .brand-card, .sidebar-block {\n            position: relative;\n            overflow: hidden;\n            border-radius: 22px;\n            background:\n                linear-gradient(145deg, rgba(255,255,255,0.97), rgba(246,255,249,0.88));\n            border: 1px solid var(--cif-border);\n            box-shadow: 0 18px 44px rgba(39, 138, 89, 0.11), 0 3px 0 rgba(255,255,255,0.95) inset;\n            backdrop-filter: blur(12px);\n        }\n\n        .mini-card { padding: 18px 18px 16px 18px; }\n        .glass-panel { padding: 20px 22px; margin-bottom: 18px; }\n        .table-card { padding: 13px 15px 17px 15px; margin-bottom: 18px; }\n        .brand-card { padding: 16px 18px; margin-bottom: 18px; }\n        .sidebar-block { padding: 14px 16px; margin-bottom: 15px; }\n\n        .mini-card:hover, .glass-panel:hover, .table-card:hover, .brand-card:hover, .sidebar-block:hover {\n            transform: translateY(-3px) rotateX(0.8deg);\n            box-shadow: 0 26px 58px rgba(39, 138, 89, 0.17), 0 3px 0 rgba(255,255,255,0.95) inset;\n        }\n\n        .mini-card h4, .sidebar-block h4 {\n            font-size: 14px;\n            color: var(--cif-emerald-dark) !important;\n            margin-bottom: 8px;\n            text-transform: uppercase;\n            letter-spacing: 0.8px;\n        }\n\n        .mini-card p, .mini-card li, .sidebar-block p, .sidebar-block li, .caption-note, .muted {\n            color: var(--cif-muted) !important;\n            font-size: 14px;\n            line-height: 1.74;\n            margin-bottom: 0;\n        }\n\n        .mini-card strong, .brand-card strong, .sidebar-block strong {\n            color: var(--cif-lapis) !important;\n        }\n\n        .developer-card {\n            background:\n                radial-gradient(circle at 9% 12%, rgba(255,255,255,0.72), transparent 30%),\n                linear-gradient(135deg, #FFF7DD 0%, #EEF9E7 42%, #DDF4E5 100%) !important;\n            border: 1px solid rgba(197, 150, 45, 0.34) !important;\n            box-shadow:\n                0 22px 52px rgba(128, 95, 24, 0.13),\n                0 8px 24px rgba(47, 166, 106, 0.11),\n                0 3px 0 rgba(255,255,255,0.96) inset !important;\n        }\n\n        .developer-card::before {\n            content: "";\n            position: absolute;\n            inset: 0 auto 0 0;\n            width: 7px;\n            background: linear-gradient(180deg, #C5962D 0%, #2FA66A 54%, #1F6F49 100%);\n            box-shadow: 6px 0 18px rgba(197, 150, 45, 0.18);\n        }\n\n        .developer-card h4 {\n            color: #7A5814 !important;\n        }\n\n        .developer-card strong {\n            color: #1F6F49 !important;\n            font-weight: 950 !important;\n        }\n\n        .developer-card p,\n        .developer-card li {\n            color: #3F513B !important;\n        }\n\n        .section-label {\n            display: inline-block;\n            margin-bottom: 12px;\n            padding: 6px 12px;\n            border-radius: 999px;\n            background: rgba(47, 166, 106, 0.13);\n            color: var(--cif-emerald-dark) !important;\n            border: 1px solid rgba(39, 138, 89, 0.22);\n            font-size: 12px;\n            font-weight: 900;\n            letter-spacing: 1px;\n            text-transform: uppercase;\n        }\n\n        section[data-testid="stSidebar"] {\n            background:\n                radial-gradient(circle at 12% 5%, rgba(47,166,106,0.12), transparent 28%),\n                linear-gradient(180deg, #ffffff 0%, #F6FFF9 48%, #F1FFF6 100%);\n            border-right: 1px solid rgba(39, 138, 89, 0.16);\n            box-shadow: 14px 0 36px rgba(39, 138, 89, 0.08);\n        }\n\n        section[data-testid="stSidebar"] * {\n            color: var(--cif-text) !important;\n        }\n\n        .brand-card .name {\n            color: var(--cif-lapis) !important;\n            font-size: 20px;\n            font-weight: 900;\n            margin-top: 6px;\n            margin-bottom: 8px;\n        }\n\n        div[data-testid="metric-container"] {\n            background: linear-gradient(145deg, rgba(255,255,255,0.97), rgba(234,251,241,0.92));\n            border: 1px solid rgba(39, 138, 89, 0.20);\n            border-radius: 18px;\n            padding: 15px;\n            box-shadow: 0 14px 32px rgba(39, 138, 89, 0.12), 0 2px 0 rgba(255,255,255,0.95) inset;\n        }\n\n        div[data-testid="stMetricValue"] { color: var(--cif-emerald-dark) !important; font-weight: 900; }\n        div[data-testid="stMetricLabel"] { color: var(--cif-lapis) !important; font-weight: 800; }\n\n        div[data-testid="stDataFrame"] {\n            background: rgba(255,255,255,0.92);\n            border: 1px solid rgba(39, 138, 89, 0.16);\n            border-radius: 18px;\n            box-shadow: 0 16px 38px rgba(39, 138, 89, 0.10);\n        }\n\n        .stTabs [data-baseweb="tab-list"] {\n            gap: 8px;\n            background: rgba(47, 166, 106, 0.08);\n            padding: 8px;\n            border-radius: 18px;\n            border: 1px solid rgba(39, 138, 89, 0.12);\n            box-shadow: 0 8px 18px rgba(39, 138, 89, 0.07) inset;\n        }\n\n        .stTabs [data-baseweb="tab"] {\n            height: 42px;\n            border-radius: 12px;\n            background: rgba(255,255,255,0.92);\n            color: var(--cif-lapis) !important;\n            font-weight: 900;\n            padding: 0 18px;\n            box-shadow: 0 6px 16px rgba(39, 138, 89, 0.08);\n        }\n\n        .stTabs [aria-selected="true"] {\n            background: linear-gradient(135deg, var(--cif-emerald-dark) 0%, var(--cif-emerald) 42%, var(--cif-forest) 100%) !important;\n            color: #ffffff !important;\n            box-shadow: 0 10px 28px rgba(39, 138, 89, 0.24), 0 2px 0 rgba(255,255,255,0.30) inset;\n        }\n\n        .stTabs [aria-selected="true"] p,\n        .stTabs [aria-selected="true"] span,\n        .stButton > button *, .stDownloadButton > button * {\n            color: #ffffff !important;\n        }\n\n        .stButton > button, .stDownloadButton > button {\n            background: linear-gradient(135deg, var(--cif-emerald-dark) 0%, var(--cif-emerald) 42%, var(--cif-forest) 100%);\n            color: #ffffff !important;\n            border: 1px solid rgba(255,255,255,0.62);\n            border-radius: 16px;\n            font-weight: 900;\n            padding: 0.78rem 1.15rem;\n            box-shadow: 0 16px 30px rgba(39, 138, 89, 0.22), 0 3px 0 rgba(255,255,255,0.34) inset;\n            transition: all 0.25s ease;\n        }\n\n        .stButton > button:hover, .stDownloadButton > button:hover {\n            transform: translateY(-2px);\n            box-shadow: 0 20px 40px rgba(39, 138, 89, 0.30), 0 3px 0 rgba(255,255,255,0.34) inset;\n        }\n\n        .upload-zone-card {\n            position: relative;\n            overflow: hidden;\n            margin: 8px 0 14px 0;\n            padding: 22px 24px;\n            border-radius: 26px;\n            background:\n                radial-gradient(circle at 8% 16%, rgba(255,255,255,0.78), transparent 26%),\n                linear-gradient(135deg, #ffffff 0%, #E5F8EE 42%, #D6F5E2 100%);\n            border: 1px solid rgba(39,138,89,0.28);\n            box-shadow: 0 24px 46px rgba(39, 138, 89, 0.16), 0 5px 0 rgba(255,255,255,0.88) inset;\n        }\n\n        .upload-zone-card h3 {\n            color: var(--cif-ink) !important;\n            font-size: 23px;\n            font-weight: 900;\n            margin: 0 0 7px 0;\n            text-shadow: 0 2px 0 rgba(255,255,255,0.75);\n        }\n\n        .upload-zone-card p {\n            color: var(--cif-lapis) !important;\n            font-size: 14px;\n            line-height: 1.65;\n            margin: 0;\n            font-weight: 650;\n        }\n\n        .upload-zone-badge {\n            display: inline-block;\n            margin-bottom: 10px;\n            padding: 6px 12px;\n            border-radius: 999px;\n            background: rgba(255,255,255,0.72);\n            color: var(--cif-emerald-dark) !important;\n            border: 1px solid rgba(255,255,255,0.82);\n            font-size: 12px;\n            font-weight: 900;\n            letter-spacing: 1px;\n            text-transform: uppercase;\n        }\n\n        .stFileUploader, div[data-testid="stFileUploader"] {\n            background: linear-gradient(145deg, rgba(255,255,255,0.97), rgba(214,245,226,0.82));\n            border: 2px dashed rgba(39, 138, 89, 0.58);\n            padding: 14px;\n            border-radius: 22px;\n            box-shadow: 0 18px 36px rgba(39, 138, 89, 0.14), 0 10px 26px rgba(18, 74, 52, 0.07) inset;\n        }\n\n        .footer-note {\n            margin-top: 28px;\n            color: var(--cif-muted) !important;\n            font-size: 13px;\n            text-align: center;\n            opacity: 0.95;\n        }\n\n        code {\n            color: var(--cif-lapis) !important;\n            background: rgba(47, 166, 106, 0.10) !important;\n            border-radius: 8px;\n            padding: 2px 5px;\n        }\n\n\n        /* ------------------------------------------------------------------\n           Strong green soft emerald green override requested by user.\n           Main visible color = #2FA66A; soft emerald, not neon and not blue/violet.\n        ------------------------------------------------------------------ */\n        :root {\n            --cif-emerald: #2FA66A;\n            --cif-emerald-dark: #1F6F49;\n            --cif-emerald-deep: #164A34;\n            --cif-emerald-soft: #EAFBF1;\n            --cif-emerald-card: #F6FFF9;\n            --cif-ink: #123B2A;\n            --cif-text: #11251B;\n            --cif-muted: #496356;\n            --cif-border: rgba(47, 166, 106, 0.34);\n            --cif-gold: #C5962D;\n        }\n\n        .stApp {\n            background:\n                radial-gradient(circle at 8% 8%, rgba(47,166,106,0.34), transparent 27%),\n                radial-gradient(circle at 92% 8%, rgba(31,111,73,0.22), transparent 30%),\n                radial-gradient(circle at 78% 92%, rgba(47,166,106,0.20), transparent 32%),\n                linear-gradient(145deg, #FAFFFC 0%, #EAFBF1 38%, #F6FFF9 70%, #FFFFFF 100%) !important;\n            color: var(--cif-text) !important;\n        }\n\n        .hero-card {\n            background:\n                radial-gradient(circle at 10% 8%, rgba(255,255,255,0.40), transparent 28%),\n                linear-gradient(135deg, #2FA66A 0%, #278A59 48%, #1F6F49 100%) !important;\n            border: 1px solid rgba(255,255,255,0.58) !important;\n            box-shadow: 0 32px 76px rgba(31, 111, 73, 0.28), 0 8px 0 rgba(255,255,255,0.18) inset !important;\n        }\n\n        .hero-title,\n        .hero-subtitle,\n        .hero-topline {\n            color: #ffffff !important;\n            text-shadow: 0 2px 12px rgba(18, 59, 42, 0.32) !important;\n        }\n\n        .hero-topline {\n            background: rgba(255,255,255,0.18) !important;\n            border: 1px solid rgba(255,255,255,0.38) !important;\n            box-shadow: 0 8px 22px rgba(18,74,52,0.18), 0 2px 0 rgba(255,255,255,0.18) inset !important;\n        }\n\n        .mini-card, .glass-panel, .table-card, .brand-card, .sidebar-block,\n        div[data-testid="metric-container"] {\n            background: linear-gradient(145deg, #ffffff 0%, #F6FFF9 58%, #EAFBF1 100%) !important;\n            border: 1px solid rgba(47, 166, 106, 0.34) !important;\n            box-shadow: 0 18px 44px rgba(31, 111, 73, 0.13), 0 3px 0 rgba(255,255,255,0.96) inset !important;\n        }\n\n        .developer-card {\n            background:\n                radial-gradient(circle at 9% 12%, rgba(255,255,255,0.72), transparent 30%),\n                linear-gradient(135deg, #FFF7DD 0%, #EEF9E7 42%, #DDF4E5 100%) !important;\n            border: 1px solid rgba(197, 150, 45, 0.36) !important;\n            box-shadow:\n                0 22px 52px rgba(128, 95, 24, 0.13),\n                0 8px 24px rgba(47, 166, 106, 0.11),\n                0 3px 0 rgba(255,255,255,0.96) inset !important;\n        }\n\n        .developer-card::before {\n            content: "";\n            position: absolute;\n            inset: 0 auto 0 0;\n            width: 7px;\n            background: linear-gradient(180deg, #C5962D 0%, #2FA66A 54%, #1F6F49 100%);\n            box-shadow: 6px 0 18px rgba(197, 150, 45, 0.18);\n        }\n\n        .developer-card h4 {\n            color: #7A5814 !important;\n        }\n\n        .developer-card strong {\n            color: #1F6F49 !important;\n            font-weight: 950 !important;\n        }\n\n        .developer-card p,\n        .developer-card li {\n            color: #3F513B !important;\n        }\n\n        h1, h2, h3, h4, h5, h6,\n        .mini-card h4, .sidebar-block h4,\n        .brand-card .name,\n        div[data-testid="stMetricValue"],\n        div[data-testid="stMetricLabel"] {\n            color: #123B2A !important;\n        }\n\n        .section-label,\n        .upload-zone-badge {\n            color: #123B2A !important;\n            background: rgba(47, 166, 106, 0.18) !important;\n            border-color: rgba(47, 166, 106, 0.40) !important;\n        }\n\n        .hamburger-shell,\n        [data-testid="collapsedControl"],\n        [data-testid="stSidebarCollapsedControl"],\n        [data-testid="stSidebarCollapseButton"],\n        .stTabs [aria-selected="true"],\n        .stButton > button,\n        .stDownloadButton > button {\n            background: linear-gradient(135deg, #2FA66A 0%, #278A59 52%, #1F6F49 100%) !important;\n            color: #ffffff !important;\n            border-color: rgba(255,255,255,0.62) !important;\n            box-shadow: 0 16px 34px rgba(31, 111, 73, 0.27), 0 3px 0 rgba(255,255,255,0.25) inset !important;\n        }\n\n        .stTabs [data-baseweb="tab-list"] {\n            background: rgba(47,166,106,0.13) !important;\n            border-color: rgba(47,166,106,0.24) !important;\n        }\n\n        .stTabs [data-baseweb="tab"] {\n            background: rgba(255,255,255,0.96) !important;\n            color: #123B2A !important;\n            border: 1px solid rgba(47,166,106,0.18) !important;\n        }\n\n        .stTabs [aria-selected="true"] p,\n        .stTabs [aria-selected="true"] span,\n        .stButton > button *,\n        .stDownloadButton > button *,\n        .hamburger-title,\n        .hamburger-pill {\n            color: #ffffff !important;\n        }\n\n        section[data-testid="stSidebar"] {\n            background:\n                radial-gradient(circle at 16% 4%, rgba(47,166,106,0.23), transparent 30%),\n                linear-gradient(180deg, #ffffff 0%, #F6FFF9 44%, #EAFBF1 100%) !important;\n            border-right: 1px solid rgba(47,166,106,0.26) !important;\n            box-shadow: 14px 0 36px rgba(31, 111, 73, 0.10) !important;\n        }\n\n        .upload-zone-card {\n            background:\n                radial-gradient(circle at 8% 16%, rgba(255,255,255,0.44), transparent 26%),\n                linear-gradient(135deg, #2FA66A 0%, #3DBB78 50%, #1F6F49 100%) !important;\n            border: 1px solid rgba(255,255,255,0.62) !important;\n            box-shadow: 0 24px 48px rgba(31, 111, 73, 0.25), 0 5px 0 rgba(255,255,255,0.22) inset !important;\n        }\n\n        .upload-zone-card h3,\n        .upload-zone-card p {\n            color: #ffffff !important;\n            text-shadow: 0 2px 10px rgba(18, 59, 42, 0.24) !important;\n        }\n\n        .upload-zone-badge {\n            background: rgba(255,255,255,0.22) !important;\n            color: #ffffff !important;\n            border-color: rgba(255,255,255,0.42) !important;\n        }\n\n        .stFileUploader, div[data-testid="stFileUploader"] {\n            background: linear-gradient(145deg, #ffffff 0%, #EAFBF1 100%) !important;\n            border: 2px dashed #2FA66A !important;\n        }\n\n        .three-d-divider {\n            background: linear-gradient(90deg, rgba(47,166,106,0.08), #2FA66A, #1F6F49, #2FA66A, rgba(47,166,106,0.08)) !important;\n        }\n\n\n\n        /* ------------------------------------------------------------------\n           Final requested fix:\n           1) Upload Zone is emerald green.\n           2) Metric cards/headings after file upload are forced dark/readable.\n        ------------------------------------------------------------------ */\n        :root {\n            --cif-emerald: #2FA66A;\n            --cif-emerald-dark: #1F6F49;\n            --cif-emerald-deep: #123B2A;\n            --cif-emerald-soft: #EAFBF1;\n        }\n\n        .upload-zone-card {\n            background:\n                radial-gradient(circle at 9% 14%, rgba(255,255,255,0.52), transparent 28%),\n                linear-gradient(135deg, #2FA66A 0%, #278A59 46%, #1F6F49 100%) !important;\n            border: 1px solid rgba(255,255,255,0.66) !important;\n            box-shadow:\n                0 26px 54px rgba(31, 111, 73, 0.32),\n                0 5px 0 rgba(255,255,255,0.24) inset !important;\n        }\n\n        .upload-zone-card .upload-zone-badge {\n            background: rgba(255,255,255,0.24) !important;\n            color: #ffffff !important;\n            border-color: rgba(255,255,255,0.48) !important;\n            box-shadow: 0 8px 20px rgba(0, 77, 50, 0.18) !important;\n        }\n\n        .upload-zone-card h3,\n        .upload-zone-card p,\n        .upload-zone-card span,\n        .upload-zone-card b,\n        .upload-zone-card strong {\n            color: #ffffff !important;\n            text-shadow: 0 2px 12px rgba(18, 59, 42, 0.34) !important;\n        }\n\n        /* Metric cards shown after upload: labels and values must never inherit white text. */\n        div[data-testid="metric-container"] {\n            background:\n                linear-gradient(145deg, #ffffff 0%, #F4FFFA 54%, #EAFBF1 100%) !important;\n            border: 1px solid rgba(31, 111, 73, 0.28) !important;\n            box-shadow:\n                0 16px 38px rgba(31, 111, 73, 0.14),\n                0 3px 0 rgba(255,255,255,0.96) inset !important;\n        }\n\n        div[data-testid="metric-container"] *,\n        div[data-testid="metric-container"] p,\n        div[data-testid="metric-container"] span,\n        div[data-testid="metric-container"] label,\n        div[data-testid="metric-container"] div {\n            color: #123B2A !important;\n            text-shadow: none !important;\n        }\n\n        div[data-testid="stMetricLabel"],\n        div[data-testid="stMetricLabel"] *,\n        div[data-testid="stMetricLabel"] p,\n        div[data-testid="stMetricLabel"] span {\n            color: #123B2A !important;\n            font-weight: 850 !important;\n            opacity: 1 !important;\n        }\n\n        div[data-testid="stMetricValue"],\n        div[data-testid="stMetricValue"] *,\n        div[data-testid="stMetricValue"] p,\n        div[data-testid="stMetricValue"] span {\n            color: #247A50 !important;\n            font-weight: 950 !important;\n            opacity: 1 !important;\n        }\n\n        /* Native Streamlit success/info/subheader text after upload can also inherit light colors in some themes. */\n        div[data-testid="stAlert"] *,\n        div[data-testid="stMarkdownContainer"] h1,\n        div[data-testid="stMarkdownContainer"] h2,\n        div[data-testid="stMarkdownContainer"] h3,\n        div[data-testid="stMarkdownContainer"] h4,\n        div[data-testid="stMarkdownContainer"] h5,\n        div[data-testid="stMarkdownContainer"] h6,\n        .table-card h1,\n        .table-card h2,\n        .table-card h3,\n        .table-card h4,\n        .glass-panel h1,\n        .glass-panel h2,\n        .glass-panel h3,\n        .glass-panel h4 {\n            color: #123B2A !important;\n            text-shadow: none !important;\n            opacity: 1 !important;\n        }\n\n        /* Keep active tabs/buttons readable on dark green backgrounds. */\n        .stTabs [aria-selected="true"],\n        .stTabs [aria-selected="true"] *,\n        .stButton > button,\n        .stButton > button *,\n        .stDownloadButton > button,\n        .stDownloadButton > button * {\n            color: #ffffff !important;\n        }\n\n\n        /* ------------------------------------------------------------------\n           Vivid Developer card override: clearly different from emerald cards.\n           Uses deep navy/petrol + gold accents while staying compatible with emerald theme.\n        ------------------------------------------------------------------ */\n        .info-grid > .mini-card.developer-card {\n            isolation: isolate !important;\n            position: relative !important;\n            overflow: hidden !important;\n            padding: 22px 22px 20px 24px !important;\n            background:\n                radial-gradient(circle at 12% 10%, rgba(255,255,255,0.24), transparent 27%),\n                radial-gradient(circle at 92% 18%, rgba(255,215,122,0.24), transparent 28%),\n                linear-gradient(135deg, #102A43 0%, #0B5D5A 50%, #113B5B 100%) !important;\n            border: 2px solid rgba(255, 202, 88, 0.88) !important;\n            box-shadow:\n                0 26px 62px rgba(16, 42, 67, 0.30),\n                0 10px 28px rgba(47, 166, 106, 0.20),\n                0 0 0 4px rgba(255, 202, 88, 0.18),\n                0 4px 0 rgba(255,255,255,0.18) inset !important;\n            transform: translateY(-2px) !important;\n        }\n\n        .info-grid > .mini-card.developer-card::before {\n            content: "" !important;\n            position: absolute !important;\n            inset: 0 auto 0 0 !important;\n            width: 11px !important;\n            background: linear-gradient(180deg, #FFD166 0%, #F6B73C 45%, #2FA66A 100%) !important;\n            box-shadow: 8px 0 24px rgba(255, 209, 102, 0.38) !important;\n            z-index: 0 !important;\n        }\n\n        .info-grid > .mini-card.developer-card::after {\n            content: "Developer" !important;\n            position: absolute !important;\n            top: 14px !important;\n            right: 16px !important;\n            padding: 6px 11px !important;\n            border-radius: 999px !important;\n            background: rgba(255, 209, 102, 0.22) !important;\n            color: #FFF5D6 !important;\n            border: 1px solid rgba(255, 209, 102, 0.58) !important;\n            font-size: 11px !important;\n            font-weight: 950 !important;\n            letter-spacing: 0.75px !important;\n            text-transform: uppercase !important;\n            z-index: 1 !important;\n        }\n\n        .info-grid > .mini-card.developer-card h4,\n        .info-grid > .mini-card.developer-card h4 * {\n            color: #FFD166 !important;\n            text-shadow: 0 2px 12px rgba(0,0,0,0.36) !important;\n            font-size: 15px !important;\n            letter-spacing: 1.15px !important;\n            margin-right: 112px !important;\n            position: relative !important;\n            z-index: 2 !important;\n        }\n\n        .info-grid > .mini-card.developer-card p,\n        .info-grid > .mini-card.developer-card li,\n        .info-grid > .mini-card.developer-card span {\n            color: #E9FFF5 !important;\n            text-shadow: 0 2px 10px rgba(0,0,0,0.28) !important;\n            position: relative !important;\n            z-index: 2 !important;\n            opacity: 1 !important;\n        }\n\n        .info-grid > .mini-card.developer-card strong,\n        .info-grid > .mini-card.developer-card b {\n            display: inline-block !important;\n            margin: 2px 0 4px 0 !important;\n            padding: 7px 10px !important;\n            border-radius: 12px !important;\n            background: rgba(255, 255, 255, 0.14) !important;\n            color: #FFFFFF !important;\n            border: 1px solid rgba(255, 255, 255, 0.22) !important;\n            box-shadow: 0 8px 18px rgba(0,0,0,0.16) !important;\n            font-weight: 950 !important;\n            text-shadow: 0 2px 10px rgba(0,0,0,0.32) !important;\n        }\n\n        .info-grid > .mini-card.developer-card:hover {\n            transform: translateY(-6px) scale(1.01) !important;\n            box-shadow:\n                0 34px 76px rgba(16, 42, 67, 0.38),\n                0 12px 34px rgba(47, 166, 106, 0.24),\n                0 0 0 5px rgba(255, 202, 88, 0.24),\n                0 4px 0 rgba(255,255,255,0.20) inset !important;\n        }\n\n\n\n        /* ------------------------------------------------------------------\n           Global visible theme refresh requested by user:\n           Use the same vivid navy + gold combination across the whole UI,\n           while keeping a soft emerald accent for harmony.\n        ------------------------------------------------------------------ */\n        :root {\n            --cif-primary-navy: #102A43;\n            --cif-primary-navy-2: #163A5B;\n            --cif-primary-navy-3: #1E4C78;\n            --cif-gold-bright: #FFC857;\n            --cif-gold-soft: #F4D58D;\n            --cif-emerald-accent: #2FA66A;\n            --cif-emerald-accent-dark: #1F6F49;\n            --cif-cream-bg: #FFF8EA;\n            --cif-surface: #FFFDF8;\n            --cif-surface-2: #FDF6E8;\n            --cif-text-deep: #13273F;\n            --cif-text-soft: #4A5B70;\n        }\n\n        .stApp {\n            background:\n                radial-gradient(circle at 8% 7%, rgba(255, 200, 87, 0.16), transparent 24%),\n                radial-gradient(circle at 92% 10%, rgba(47, 166, 106, 0.10), transparent 26%),\n                radial-gradient(circle at 75% 88%, rgba(16, 42, 67, 0.08), transparent 28%),\n                linear-gradient(145deg, #FFFDF8 0%, #FFF8EA 40%, #F9FBFC 72%, #FFFFFF 100%) !important;\n            color: var(--cif-text-deep) !important;\n        }\n\n        h1, h2, h3, h4, h5, h6,\n        .stMarkdown, .stMarkdown p, .stMarkdown li,\n        .stCaptionContainer, .stText, label,\n        div[data-testid="stWidgetLabel"], div[data-testid="stWidgetLabel"] p,\n        div[data-testid="stMarkdownContainer"] p,\n        div[data-testid="stMarkdownContainer"] li,\n        .caption-note, .muted,\n        td, th, span {\n            color: var(--cif-text-deep) !important;\n        }\n\n        .hero-card,\n        .upload-zone-card,\n        .hamburger-shell,\n        [data-testid="collapsedControl"],\n        [data-testid="stSidebarCollapsedControl"],\n        [data-testid="stSidebarCollapseButton"] {\n            background:\n                radial-gradient(circle at 10% 12%, rgba(255,255,255,0.16), transparent 28%),\n                linear-gradient(135deg, var(--cif-primary-navy) 0%, var(--cif-primary-navy-2) 52%, var(--cif-primary-navy-3) 100%) !important;\n            border: 1px solid rgba(255, 200, 87, 0.68) !important;\n            box-shadow:\n                0 28px 60px rgba(16, 42, 67, 0.30),\n                0 10px 30px rgba(255, 200, 87, 0.14),\n                0 3px 0 rgba(255,255,255,0.10) inset !important;\n        }\n\n        .hero-card::after,\n        .upload-zone-card::after,\n        .hamburger-shell::after {\n            content: "";\n            position: absolute;\n            inset: 0;\n            pointer-events: none;\n            border-radius: inherit;\n            box-shadow: 0 0 0 1px rgba(255, 200, 87, 0.22) inset;\n        }\n\n        .hero-topline,\n        .upload-zone-badge,\n        .hamburger-pill {\n            background: rgba(255, 200, 87, 0.16) !important;\n            color: #FFF4D2 !important;\n            border: 1px solid rgba(255, 200, 87, 0.40) !important;\n            box-shadow: 0 10px 20px rgba(0,0,0,0.12) !important;\n        }\n\n        .hero-title,\n        .hero-subtitle,\n        .upload-zone-card h3,\n        .upload-zone-card p,\n        .upload-zone-card span,\n        .upload-zone-card b,\n        .upload-zone-card strong,\n        .hamburger-title,\n        .hamburger-shell summary,\n        .hamburger-shell summary *,\n        [data-testid="collapsedControl"] button,\n        [data-testid="stSidebarCollapsedControl"] button,\n        [data-testid="stSidebarCollapseButton"] button,\n        [data-testid="collapsedControl"] svg,\n        [data-testid="stSidebarCollapsedControl"] svg,\n        [data-testid="stSidebarCollapseButton"] svg {\n            color: #FFFFFF !important;\n        }\n\n        .mini-card,\n        .glass-panel,\n        .table-card,\n        .brand-card,\n        .sidebar-block,\n        div[data-testid="metric-container"],\n        div[data-testid="stDataFrame"] {\n            background:\n                linear-gradient(145deg, rgba(255,253,248,0.98) 0%, rgba(253,246,232,0.96) 100%) !important;\n            border: 1px solid rgba(255, 200, 87, 0.42) !important;\n            box-shadow:\n                0 18px 42px rgba(16, 42, 67, 0.08),\n                0 6px 18px rgba(255, 200, 87, 0.12),\n                0 3px 0 rgba(255,255,255,0.96) inset !important;\n        }\n\n        .mini-card:hover,\n        .glass-panel:hover,\n        .table-card:hover,\n        .brand-card:hover,\n        .sidebar-block:hover,\n        div[data-testid="metric-container"]:hover {\n            transform: translateY(-4px) !important;\n            box-shadow:\n                0 26px 58px rgba(16, 42, 67, 0.14),\n                0 10px 24px rgba(255, 200, 87, 0.18),\n                0 3px 0 rgba(255,255,255,0.96) inset !important;\n        }\n\n        .mini-card h4,\n        .sidebar-block h4,\n        .brand-card .name,\n        div[data-testid="stMetricLabel"],\n        div[data-testid="stMetricLabel"] *,\n        div[data-testid="stMetricValue"],\n        div[data-testid="stMetricValue"] *,\n        .table-card h1, .table-card h2, .table-card h3, .table-card h4,\n        .glass-panel h1, .glass-panel h2, .glass-panel h3, .glass-panel h4 {\n            color: var(--cif-primary-navy) !important;\n            text-shadow: none !important;\n        }\n\n        .mini-card p,\n        .mini-card li,\n        .sidebar-block p,\n        .sidebar-block li,\n        .caption-note,\n        .muted,\n        .brand-card p,\n        .glass-panel p,\n        .table-card p,\n        div[data-testid="metric-container"] p,\n        div[data-testid="metric-container"] span,\n        div[data-testid="metric-container"] div {\n            color: var(--cif-text-soft) !important;\n        }\n\n        .mini-card strong,\n        .brand-card strong,\n        .sidebar-block strong {\n            color: var(--cif-primary-navy-2) !important;\n        }\n\n        .section-label {\n            background: rgba(255, 200, 87, 0.18) !important;\n            color: var(--cif-primary-navy) !important;\n            border: 1px solid rgba(255, 200, 87, 0.48) !important;\n        }\n\n        section[data-testid="stSidebar"] {\n            background:\n                radial-gradient(circle at 12% 5%, rgba(255,200,87,0.16), transparent 28%),\n                linear-gradient(180deg, #FFFDF8 0%, #FFF8EA 45%, #FDF1D8 100%) !important;\n            border-right: 1px solid rgba(255, 200, 87, 0.34) !important;\n            box-shadow: 14px 0 36px rgba(16, 42, 67, 0.08) !important;\n        }\n        section[data-testid="stSidebar"] * { color: var(--cif-text-deep) !important; }\n\n        .stTabs [data-baseweb="tab-list"] {\n            background: rgba(16, 42, 67, 0.08) !important;\n            border: 1px solid rgba(255, 200, 87, 0.22) !important;\n        }\n\n        .stTabs [data-baseweb="tab"] {\n            background: rgba(255,255,255,0.96) !important;\n            color: var(--cif-primary-navy) !important;\n            border: 1px solid rgba(255, 200, 87, 0.18) !important;\n            box-shadow: 0 6px 16px rgba(16, 42, 67, 0.06) !important;\n        }\n\n        .stTabs [aria-selected="true"],\n        .stButton > button,\n        .stDownloadButton > button {\n            background: linear-gradient(135deg, var(--cif-primary-navy) 0%, var(--cif-primary-navy-2) 58%, var(--cif-primary-navy-3) 100%) !important;\n            color: #FFFFFF !important;\n            border: 1px solid rgba(255, 200, 87, 0.62) !important;\n            box-shadow: 0 18px 36px rgba(16, 42, 67, 0.22), 0 0 0 1px rgba(255, 200, 87, 0.18) inset !important;\n        }\n\n        .stTabs [aria-selected="true"] p,\n        .stTabs [aria-selected="true"] span,\n        .stButton > button *,\n        .stDownloadButton > button * {\n            color: #FFFFFF !important;\n        }\n\n        .hamburger-links a {\n            color: var(--cif-primary-navy) !important;\n            background: rgba(255, 250, 240, 0.98) !important;\n            border: 1px solid rgba(255, 200, 87, 0.30) !important;\n            box-shadow: 0 8px 18px rgba(16, 42, 67, 0.08) !important;\n        }\n\n        .hamburger-links a:hover {\n            color: var(--cif-primary-navy-2) !important;\n            border-color: rgba(47, 166, 106, 0.44) !important;\n            box-shadow: 0 12px 24px rgba(16, 42, 67, 0.12), 0 0 0 3px rgba(47, 166, 106, 0.10) !important;\n        }\n\n        .stFileUploader, div[data-testid="stFileUploader"] {\n            background: linear-gradient(145deg, #FFFEFB 0%, #FFF4DC 100%) !important;\n            border: 2px dashed #FFC857 !important;\n            box-shadow: 0 18px 36px rgba(16,42,67,0.08), 0 8px 18px rgba(255,200,87,0.10) inset !important;\n        }\n\n        code {\n            color: var(--cif-primary-navy) !important;\n            background: rgba(255, 200, 87, 0.12) !important;\n            border-radius: 8px;\n            padding: 2px 5px;\n        }\n\n        .three-d-divider {\n            background: linear-gradient(90deg, rgba(255,200,87,0.05), #FFC857, #2FA66A, #163A5B, rgba(255,200,87,0.05)) !important;\n        }\n\n        /* Make the developer card match the same global language even more strongly. */\n        .info-grid > .mini-card.developer-card {\n            background:\n                radial-gradient(circle at 10% 12%, rgba(255,255,255,0.14), transparent 30%),\n                linear-gradient(135deg, var(--cif-primary-navy) 0%, var(--cif-primary-navy-2) 55%, var(--cif-primary-navy-3) 100%) !important;\n            border: 1px solid rgba(255, 200, 87, 0.72) !important;\n            box-shadow:\n                0 34px 76px rgba(16, 42, 67, 0.34),\n                0 12px 32px rgba(255, 200, 87, 0.15),\n                0 0 0 4px rgba(255, 200, 87, 0.10),\n                0 3px 0 rgba(255,255,255,0.10) inset !important;\n        }\n\n        .info-grid > .mini-card.developer-card h4 {\n            color: #FFD778 !important;\n            letter-spacing: 1px !important;\n        }\n\n        .info-grid > .mini-card.developer-card p,\n        .info-grid > .mini-card.developer-card li,\n        .info-grid > .mini-card.developer-card span {\n            color: #EAF4FF !important;\n        }\n\n        .info-grid > .mini-card.developer-card strong,\n        .info-grid > .mini-card.developer-card b {\n            display: inline-block !important;\n            background: rgba(255, 200, 87, 0.16) !important;\n            color: #FFFFFF !important;\n            border: 1px solid rgba(255, 200, 87, 0.34) !important;\n        }\n\n        \n        /* ================================================================\n           CLEAN FINAL FIX\n           1) Hero subtitle readable\n           2) Upload component readable\n           3) Sidebar brand card no longer shows raw HTML/code\n        ================================================================ */\n\n        .hero-card .hero-subtitle,\n        .hero-card .hero-subtitle * {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            opacity: 1 !important;\n            font-weight: 800 !important;\n            line-height: 1.75 !important;\n            text-shadow: 0 2px 12px rgba(0,0,0,0.70) !important;\n        }\n\n        .sidebar-brand-card {\n            background: linear-gradient(135deg, #102A43 0%, #163A5B 55%, #1E4C78 100%) !important;\n            border: 1px solid rgba(255, 200, 87, 0.70) !important;\n            box-shadow: 0 18px 42px rgba(16, 42, 67, 0.26), 0 0 0 3px rgba(255, 200, 87, 0.12) !important;\n        }\n\n        .sidebar-brand-card .brand-kicker {\n            font-size: 12px !important;\n            color: #FFC857 !important;\n            -webkit-text-fill-color: #FFC857 !important;\n            letter-spacing: 1.4px !important;\n            text-transform: uppercase !important;\n            font-weight: 900 !important;\n            margin-bottom: 8px !important;\n        }\n\n        .sidebar-brand-card .name {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            font-weight: 950 !important;\n            font-size: 19px !important;\n            line-height: 1.35 !important;\n            margin-bottom: 8px !important;\n        }\n\n        .sidebar-brand-card .muted {\n            color: #EAF4FF !important;\n            -webkit-text-fill-color: #EAF4FF !important;\n            opacity: 1 !important;\n            text-shadow: 0 2px 10px rgba(0,0,0,0.35) !important;\n            line-height: 1.65 !important;\n            font-weight: 600 !important;\n        }\n\n        /* File uploader */\n        div[data-testid="stFileUploader"] {\n            background: #FFF8EA !important;\n            border: 2px dashed #FFC857 !important;\n            border-radius: 22px !important;\n            padding: 14px !important;\n            box-shadow: 0 16px 34px rgba(16, 42, 67, 0.10) !important;\n        }\n\n        div[data-testid="stFileUploader"] > label,\n        div[data-testid="stFileUploader"] > label *,\n        div[data-testid="stFileUploader"] label,\n        div[data-testid="stFileUploader"] label * {\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            opacity: 1 !important;\n            font-weight: 900 !important;\n            text-shadow: none !important;\n        }\n\n        div[data-testid="stFileUploader"] section,\n        section[data-testid="stFileUploaderDropzone"],\n        div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {\n            background: #102A43 !important;\n            border: 1px solid rgba(255,200,87,0.72) !important;\n            border-radius: 14px !important;\n        }\n\n        div[data-testid="stFileUploader"] section *,\n        section[data-testid="stFileUploaderDropzone"] *,\n        div[data-testid="stFileUploader"] small,\n        div[data-testid="stFileUploader"] span,\n        div[data-testid="stFileUploader"] p {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            opacity: 1 !important;\n            fill: #FFFFFF !important;\n            stroke: #FFFFFF !important;\n            font-weight: 700 !important;\n            text-shadow: none !important;\n        }\n\n        div[data-testid="stFileUploader"] button,\n        div[data-testid="stFileUploader"] button *,\n        section[data-testid="stFileUploaderDropzone"] button,\n        section[data-testid="stFileUploaderDropzone"] button * {\n            background: #FFC857 !important;\n            background-color: #FFC857 !important;\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            border: 1px solid rgba(255,255,255,0.85) !important;\n            opacity: 1 !important;\n            font-weight: 900 !important;\n            text-shadow: none !important;\n        }\n\n\n\n        /* ---------------------------------------------------------------\n           Readable sheet-list cards: replaces dark JSON/code output after upload.\n        --------------------------------------------------------------- */\n        .sheet-list-box {\n            display: flex !important;\n            flex-wrap: wrap !important;\n            gap: 10px !important;\n            align-items: center !important;\n            margin: 8px 0 14px 0 !important;\n            padding: 14px 14px !important;\n            border-radius: 18px !important;\n            background: linear-gradient(145deg, #FFFEFB 0%, #FFF8EA 100%) !important;\n            border: 1px solid rgba(255, 200, 87, 0.44) !important;\n            box-shadow: 0 12px 28px rgba(16, 42, 67, 0.08), 0 2px 0 rgba(255,255,255,0.92) inset !important;\n        }\n\n        .sheet-pill {\n            display: inline-flex !important;\n            align-items: center !important;\n            gap: 8px !important;\n            padding: 9px 13px !important;\n            border-radius: 999px !important;\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            background: #FFFFFF !important;\n            border: 1px solid rgba(16, 42, 67, 0.14) !important;\n            box-shadow: 0 8px 18px rgba(16, 42, 67, 0.07) !important;\n            font-weight: 900 !important;\n            font-size: 13px !important;\n            letter-spacing: 0.2px !important;\n            text-shadow: none !important;\n        }\n\n        .sheet-pill::before {\n            content: "" !important;\n            width: 8px !important;\n            height: 8px !important;\n            border-radius: 999px !important;\n            background: #2FA66A !important;\n            box-shadow: 0 0 0 4px rgba(47, 166, 106, 0.13) !important;\n        }\n\n        .sheet-pill.skipped::before {\n            background: #FFC857 !important;\n            box-shadow: 0 0 0 4px rgba(255, 200, 87, 0.18) !important;\n        }\n\n        .sheet-pill.skipped {\n            color: #4A5B70 !important;\n            -webkit-text-fill-color: #4A5B70 !important;\n            background: #FFFDF8 !important;\n            border-color: rgba(255, 200, 87, 0.52) !important;\n        }\n\n        .sheet-list-note {\n            margin: 8px 0 6px 0 !important;\n            color: #4A5B70 !important;\n            -webkit-text-fill-color: #4A5B70 !important;\n            font-size: 14px !important;\n            font-weight: 800 !important;\n            text-shadow: none !important;\n        }\n\n        /* In case Streamlit JSON/code blocks remain anywhere, make them readable too. */\n        div[data-testid="stJson"],\n        div[data-testid="stJson"] *,\n        pre, pre *, code, code * {\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            text-shadow: none !important;\n        }\n\n        div[data-testid="stJson"], pre {\n            background: #FFFDF8 !important;\n            border: 1px solid rgba(255, 200, 87, 0.44) !important;\n            border-radius: 16px !important;\n        }\n\n\n\n        /* ================================================================\n           CIF_DEMATEL_16 - High-contrast uploaded workbook sheet summary\n           Fixes unreadable dark JSON/code blocks after Excel upload.\n        ================================================================ */\n        .sheet-clean-panel,\n        .sheet-clean-panel * {\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            opacity: 1 !important;\n            text-shadow: none !important;\n            font-family: \'Inter\', \'Segoe UI\', sans-serif !important;\n            box-sizing: border-box !important;\n        }\n\n        .sheet-clean-panel {\n            width: 100% !important;\n            margin: 0 0 18px 0 !important;\n            padding: 22px 24px !important;\n            border-radius: 24px !important;\n            background: linear-gradient(145deg, #FFFFFF 0%, #FFF8EA 48%, #F4FFFA 100%) !important;\n            border: 2px solid rgba(255, 200, 87, 0.72) !important;\n            box-shadow:\n                0 22px 52px rgba(16, 42, 67, 0.12),\n                0 6px 16px rgba(255, 200, 87, 0.16),\n                0 3px 0 rgba(255,255,255,0.98) inset !important;\n            overflow: hidden !important;\n        }\n\n        .sheet-clean-header {\n            display: flex !important;\n            justify-content: space-between !important;\n            gap: 14px !important;\n            align-items: flex-start !important;\n            margin-bottom: 18px !important;\n            padding-bottom: 14px !important;\n            border-bottom: 1px solid rgba(16, 42, 67, 0.10) !important;\n        }\n\n        .sheet-clean-title {\n            margin: 0 !important;\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            font-size: 26px !important;\n            line-height: 1.25 !important;\n            font-weight: 950 !important;\n            letter-spacing: -0.3px !important;\n        }\n\n        .sheet-clean-subtitle {\n            margin: 6px 0 0 0 !important;\n            color: #4A5B70 !important;\n            -webkit-text-fill-color: #4A5B70 !important;\n            font-size: 14px !important;\n            line-height: 1.65 !important;\n            font-weight: 750 !important;\n        }\n\n        .sheet-clean-counts {\n            display: flex !important;\n            gap: 10px !important;\n            flex-wrap: wrap !important;\n            justify-content: flex-end !important;\n        }\n\n        .sheet-count-badge {\n            min-width: 112px !important;\n            padding: 10px 12px !important;\n            border-radius: 16px !important;\n            background: #FFFFFF !important;\n            border: 1px solid rgba(16, 42, 67, 0.12) !important;\n            box-shadow: 0 10px 22px rgba(16, 42, 67, 0.08) !important;\n            text-align: center !important;\n        }\n\n        .sheet-count-badge .num {\n            display: block !important;\n            font-size: 22px !important;\n            line-height: 1 !important;\n            font-weight: 950 !important;\n            color: #1F6F49 !important;\n            -webkit-text-fill-color: #1F6F49 !important;\n        }\n\n        .sheet-count-badge.skipped .num {\n            color: #9B6500 !important;\n            -webkit-text-fill-color: #9B6500 !important;\n        }\n\n        .sheet-count-badge .lbl {\n            display: block !important;\n            margin-top: 5px !important;\n            color: #4A5B70 !important;\n            -webkit-text-fill-color: #4A5B70 !important;\n            font-size: 11px !important;\n            font-weight: 900 !important;\n            letter-spacing: 0.75px !important;\n            text-transform: uppercase !important;\n        }\n\n        .sheet-clean-grid {\n            display: grid !important;\n            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)) !important;\n            gap: 12px !important;\n            margin-top: 12px !important;\n        }\n\n        .sheet-clean-item {\n            display: flex !important;\n            align-items: center !important;\n            justify-content: space-between !important;\n            gap: 12px !important;\n            min-height: 58px !important;\n            padding: 13px 14px !important;\n            border-radius: 18px !important;\n            background: #FFFFFF !important;\n            border: 1px solid rgba(31, 111, 73, 0.22) !important;\n            box-shadow: 0 10px 24px rgba(16, 42, 67, 0.07) !important;\n        }\n\n        .sheet-clean-item.skipped {\n            background: #FFFDF8 !important;\n            border-color: rgba(255, 200, 87, 0.60) !important;\n        }\n\n        .sheet-name-wrap {\n            display: flex !important;\n            align-items: center !important;\n            gap: 10px !important;\n            min-width: 0 !important;\n        }\n\n        .sheet-dot {\n            flex: 0 0 auto !important;\n            width: 11px !important;\n            height: 11px !important;\n            border-radius: 999px !important;\n            background: #2FA66A !important;\n            box-shadow: 0 0 0 5px rgba(47, 166, 106, 0.14) !important;\n        }\n\n        .sheet-clean-item.skipped .sheet-dot {\n            background: #FFC857 !important;\n            box-shadow: 0 0 0 5px rgba(255, 200, 87, 0.18) !important;\n        }\n\n        .sheet-name {\n            display: block !important;\n            min-width: 0 !important;\n            overflow: hidden !important;\n            text-overflow: ellipsis !important;\n            white-space: nowrap !important;\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            font-size: 16px !important;\n            line-height: 1.35 !important;\n            font-weight: 950 !important;\n        }\n\n        .sheet-status {\n            flex: 0 0 auto !important;\n            padding: 6px 9px !important;\n            border-radius: 999px !important;\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            background: #1F6F49 !important;\n            font-size: 10px !important;\n            line-height: 1 !important;\n            font-weight: 950 !important;\n            letter-spacing: 0.65px !important;\n            text-transform: uppercase !important;\n        }\n\n        .sheet-clean-item.skipped .sheet-status {\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            background: #FFC857 !important;\n        }\n\n        .sheet-clean-section-label {\n            display: inline-flex !important;\n            align-items: center !important;\n            margin: 18px 0 6px 0 !important;\n            padding: 7px 11px !important;\n            border-radius: 999px !important;\n            background: rgba(16, 42, 67, 0.08) !important;\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            font-size: 12px !important;\n            font-weight: 950 !important;\n            letter-spacing: 0.85px !important;\n            text-transform: uppercase !important;\n            border: 1px solid rgba(16, 42, 67, 0.10) !important;\n        }\n\n        @media (max-width: 760px) {\n            .sheet-clean-header { flex-direction: column !important; }\n            .sheet-clean-counts { justify-content: flex-start !important; }\n            .sheet-clean-title { font-size: 22px !important; }\n            .sheet-clean-grid { grid-template-columns: 1fr !important; }\n        }\n\n\n\n        /* ================================================================\n           FINAL TOP BAR FIX - Heavy Gold Streamlit header / toolbar\n           Makes the native Streamlit top bar readable instead of black.\n        ================================================================ */\n        header[data-testid="stHeader"],\n        .stAppHeader {\n            background:\n                radial-gradient(circle at 4% 50%, rgba(255,255,255,0.28), transparent 24%),\n                linear-gradient(135deg, #6F4E00 0%, #B8860B 28%, #D4AF37 54%, #8A6508 100%) !important;\n            border-bottom: 1px solid rgba(255, 238, 178, 0.70) !important;\n            box-shadow:\n                0 14px 34px rgba(111, 78, 0, 0.35),\n                0 2px 0 rgba(255,255,255,0.22) inset !important;\n            color: #102A43 !important;\n        }\n\n        header[data-testid="stHeader"]::before,\n        .stAppHeader::before {\n            content: "" !important;\n            position: absolute !important;\n            inset: 0 !important;\n            pointer-events: none !important;\n            background: linear-gradient(90deg, rgba(255,255,255,0.18), transparent 35%, rgba(255,255,255,0.12)) !important;\n        }\n\n        /* Streamlit toolbar / deploy / menu icons */\n        header[data-testid="stHeader"] *,\n        .stAppHeader *,\n        div[data-testid="stToolbar"],\n        div[data-testid="stToolbar"] *,\n        div[data-testid="stDeployButton"],\n        div[data-testid="stDeployButton"] *,\n        button[kind="header"],\n        button[kind="header"] *,\n        [data-testid="baseButton-header"],\n        [data-testid="baseButton-header"] * {\n            color: #102A43 !important;\n            -webkit-text-fill-color: #102A43 !important;\n            fill: #102A43 !important;\n            stroke: #102A43 !important;\n            opacity: 1 !important;\n            text-shadow: none !important;\n        }\n\n        header[data-testid="stHeader"] button,\n        .stAppHeader button,\n        div[data-testid="stToolbar"] button,\n        div[data-testid="stDeployButton"] button,\n        button[kind="header"],\n        [data-testid="baseButton-header"] {\n            background: rgba(255, 253, 248, 0.34) !important;\n            border: 1px solid rgba(16, 42, 67, 0.20) !important;\n            border-radius: 12px !important;\n            box-shadow: 0 8px 18px rgba(111, 78, 0, 0.18) !important;\n        }\n\n        header[data-testid="stHeader"] button:hover,\n        .stAppHeader button:hover,\n        div[data-testid="stToolbar"] button:hover,\n        div[data-testid="stDeployButton"] button:hover,\n        button[kind="header"]:hover,\n        [data-testid="baseButton-header"]:hover {\n            background: rgba(255, 255, 255, 0.58) !important;\n            border-color: rgba(16, 42, 67, 0.34) !important;\n            transform: translateY(-1px) !important;\n        }\n\n        /* The small top decoration line should match the gold header. */\n        [data-testid="stDecoration"] {\n            background: linear-gradient(90deg, #6F4E00 0%, #D4AF37 45%, #FFC857 65%, #8A6508 100%) !important;\n            height: 4px !important;\n        }\n\n        /* In some Streamlit builds the top bar is rendered as these classes. */\n        .st-emotion-cache-18ni7ap,\n        .st-emotion-cache-h4xjwg,\n        .st-emotion-cache-zq5wmm {\n            background:\n                radial-gradient(circle at 4% 50%, rgba(255,255,255,0.24), transparent 24%),\n                linear-gradient(135deg, #6F4E00 0%, #B8860B 30%, #D4AF37 58%, #8A6508 100%) !important;\n            color: #102A43 !important;\n            border-bottom: 1px solid rgba(255, 238, 178, 0.65) !important;\n        }\n\n\n        /* ================================================================\n           FINAL UPLOAD ZONE FIX - Heavy Gold box + white readable text\n           Requested: make Upload Zone text white / make upload box gold.\n        ================================================================ */\n        .upload-zone-card {\n            background:\n                radial-gradient(circle at 8% 12%, rgba(255,255,255,0.34), transparent 28%),\n                radial-gradient(circle at 92% 18%, rgba(255,255,255,0.18), transparent 30%),\n                linear-gradient(135deg, #6F4E00 0%, #A87400 28%, #D4AF37 58%, #8A6508 100%) !important;\n            border: 2px solid rgba(255, 238, 178, 0.92) !important;\n            box-shadow:\n                0 28px 64px rgba(111, 78, 0, 0.34),\n                0 0 0 4px rgba(255, 200, 87, 0.14),\n                0 5px 0 rgba(255,255,255,0.22) inset !important;\n        }\n\n        .upload-zone-card .upload-zone-badge {\n            background: rgba(16, 42, 67, 0.30) !important;\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            border: 1px solid rgba(255,255,255,0.42) !important;\n            box-shadow: 0 8px 20px rgba(0,0,0,0.18) !important;\n            opacity: 1 !important;\n        }\n\n        .upload-zone-card h1,\n        .upload-zone-card h2,\n        .upload-zone-card h3,\n        .upload-zone-card h4,\n        .upload-zone-card p,\n        .upload-zone-card span,\n        .upload-zone-card div,\n        .upload-zone-card b,\n        .upload-zone-card strong,\n        .upload-zone-card * {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            opacity: 1 !important;\n            text-shadow: 0 3px 14px rgba(0,0,0,0.58) !important;\n        }\n\n        .upload-zone-card h3 {\n            font-weight: 950 !important;\n            letter-spacing: 0.2px !important;\n        }\n\n        .upload-zone-card p {\n            font-weight: 750 !important;\n            line-height: 1.75 !important;\n        }\n\n\n\n\n        /* ================================================================\n           FINAL REQUEST 19 - keep everything else unchanged\n           1) Force a light-looking default interface.\n           2) Make the Upload Zone a clear premium gold box.\n        ================================================================ */\n        html,\n        body,\n        .stApp,\n        [data-testid="stAppViewContainer"],\n        [data-testid="stMain"],\n        [data-testid="stMainBlockContainer"],\n        .block-container {\n            color-scheme: light !important;\n        }\n\n        .stApp,\n        [data-testid="stAppViewContainer"],\n        [data-testid="stMain"] {\n            background:\n                radial-gradient(circle at 8% 7%, rgba(255, 209, 102, 0.14), transparent 25%),\n                radial-gradient(circle at 94% 8%, rgba(47, 166, 106, 0.08), transparent 27%),\n                linear-gradient(145deg, #FFFDF8 0%, #FFF8EA 42%, #FFFFFF 100%) !important;\n            color: #102A43 !important;\n        }\n\n        .upload-zone-card {\n            background:\n                radial-gradient(circle at 9% 12%, rgba(255,255,255,0.42), transparent 28%),\n                radial-gradient(circle at 88% 18%, rgba(255,244,210,0.30), transparent 32%),\n                linear-gradient(135deg, #8A6508 0%, #B8860B 24%, #D4AF37 50%, #FFD166 72%, #A87400 100%) !important;\n            border: 2px solid rgba(255, 244, 210, 0.96) !important;\n            box-shadow:\n                0 30px 68px rgba(111, 78, 0, 0.35),\n                0 0 0 5px rgba(255, 209, 102, 0.18),\n                0 6px 0 rgba(255,255,255,0.26) inset !important;\n        }\n\n        .upload-zone-card .upload-zone-badge {\n            background: rgba(16, 42, 67, 0.34) !important;\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            border: 1px solid rgba(255,255,255,0.52) !important;\n            box-shadow: 0 10px 24px rgba(0,0,0,0.20) !important;\n            opacity: 1 !important;\n        }\n\n        .upload-zone-card h1,\n        .upload-zone-card h2,\n        .upload-zone-card h3,\n        .upload-zone-card h4,\n        .upload-zone-card p,\n        .upload-zone-card span,\n        .upload-zone-card div,\n        .upload-zone-card b,\n        .upload-zone-card strong,\n        .upload-zone-card * {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            opacity: 1 !important;\n            text-shadow: 0 3px 15px rgba(0,0,0,0.62) !important;\n        }\n\n        .upload-zone-card h3 {\n            font-weight: 950 !important;\n        }\n\n        .upload-zone-card p {\n            font-weight: 800 !important;\n            line-height: 1.78 !important;\n        }\n\n        \n\n        /* ================================================================\n           FINAL REQUEST 20 - Upload Zone must be gold and all text white\n           This is intentionally placed at the very end of the CSS.\n        ================================================================ */\n        .upload-zone-card.upload-zone-gold-final,\n        div.upload-zone-card.upload-zone-gold-final {\n            background:\n                radial-gradient(circle at 9% 12%, rgba(255,255,255,0.45), transparent 28%),\n                radial-gradient(circle at 88% 16%, rgba(255,244,210,0.38), transparent 32%),\n                linear-gradient(135deg, #6F4E00 0%, #9B7208 23%, #D4AF37 52%, #FFD166 74%, #8A6508 100%) !important;\n            border: 2px solid rgba(255,244,210,0.98) !important;\n            box-shadow:\n                0 30px 68px rgba(111,78,0,0.38),\n                0 0 0 5px rgba(255,209,102,0.22),\n                0 6px 0 rgba(255,255,255,0.28) inset !important;\n        }\n\n        .upload-zone-card.upload-zone-gold-final,\n        .upload-zone-card.upload-zone-gold-final *,\n        .upload-zone-card.upload-zone-gold-final .upload-zone-title,\n        .upload-zone-card.upload-zone-gold-final .upload-zone-description,\n        .upload-zone-card.upload-zone-gold-final .upload-zone-badge {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            opacity: 1 !important;\n            text-shadow: 0 4px 16px rgba(0,0,0,0.72) !important;\n        }\n\n        .upload-zone-card.upload-zone-gold-final .upload-zone-description {\n            font-size: 16px !important;\n            font-weight: 850 !important;\n            line-height: 1.85 !important;\n        }\n\n\n        /* FINAL FORCE: Upload Zone description text must stay pure white. */\n        #force-upload-desc-white,\n        #force-upload-desc-white *,\n        div#force-upload-desc-white,\n        div#force-upload-desc-white span {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            opacity: 1 !important;\n            font-weight: 900 !important;\n            text-shadow: 0 4px 18px rgba(0,0,0,0.78) !important;\n        }\n\n\n\n        /* ================================================================\n           FINAL EXPORT DOWNLOAD BUTTON FIX\n           Make the "Download Excel Results" button highly visible.\n        ================================================================ */\n        div[data-testid="stDownloadButton"] button,\n        div[data-testid="stDownloadButton"] > button,\n        .stDownloadButton > button {\n            background: linear-gradient(135deg, #8A5A00 0%, #B8860B 28%, #D4AF37 58%, #F4D06F 100%) !important;\n            background-color: #D4AF37 !important;\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            border: 2px solid rgba(255, 244, 210, 0.95) !important;\n            border-radius: 18px !important;\n            font-weight: 950 !important;\n            letter-spacing: 0.2px !important;\n            text-shadow: 0 2px 10px rgba(0,0,0,0.55) !important;\n            box-shadow:\n                0 18px 38px rgba(138, 90, 0, 0.32),\n                0 0 0 3px rgba(212, 175, 55, 0.18),\n                0 3px 0 rgba(255,255,255,0.30) inset !important;\n            opacity: 1 !important;\n        }\n\n        div[data-testid="stDownloadButton"] button *,\n        div[data-testid="stDownloadButton"] button p,\n        div[data-testid="stDownloadButton"] button span,\n        div[data-testid="stDownloadButton"] button div,\n        .stDownloadButton > button *,\n        .stDownloadButton > button p,\n        .stDownloadButton > button span,\n        .stDownloadButton > button div {\n            color: #FFFFFF !important;\n            -webkit-text-fill-color: #FFFFFF !important;\n            fill: #FFFFFF !important;\n            stroke: #FFFFFF !important;\n            opacity: 1 !important;\n            font-weight: 950 !important;\n            text-shadow: 0 2px 10px rgba(0,0,0,0.55) !important;\n        }\n\n        div[data-testid="stDownloadButton"] button:hover,\n        .stDownloadButton > button:hover {\n            background: linear-gradient(135deg, #9A6600 0%, #C99612 30%, #E2BD43 62%, #FFE08A 100%) !important;\n            transform: translateY(-2px) !important;\n            box-shadow:\n                0 24px 48px rgba(138, 90, 0, 0.42),\n                0 0 0 4px rgba(212, 175, 55, 0.24),\n                0 3px 0 rgba(255,255,255,0.36) inset !important;\n        }\n\n</style>\n        ', unsafe_allow_html=True)

def swara_hamburger_menu():
    st.markdown('\n        <details class="hamburger-shell">\n            <summary>\n                <span class="hamburger-icon"><span></span><span></span><span></span></span>\n                <span class="hamburger-title">CIF-SWARA Menu</span>\n                <span class="hamburger-pill">Quick access</span>\n            </summary>\n            <div class="hamburger-links">\n                <a href="#input-guide">Input Guide</a>\n                <a href="#active-scale">Scales</a>\n                <a href="#upload-workbook">Upload Workbook</a>\n                <a href="#results-dashboard">Results</a>\n                <a href="#download-results">Export</a>\n                <a href="#">Back to Top</a>\n            </div>\n        </details>\n        ', unsafe_allow_html=True)

def swara_hero_section():
    st.markdown('\n        <div class="hero-card">\n            <div class="hero-topline">Navy & Gold Decision Analytics</div>\n            <div class="hero-title">CIF-SWARA Calculator</div>\n            <p class="hero-subtitle" style="color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; opacity:1 !important; font-weight:800 !important; line-height:1.75 !important; text-shadow:0 2px 12px rgba(0,0,0,0.70) !important;">\n                A navy, gold, and soft emerald executive Streamlit interface for Circular Intuitionistic Fuzzy SWARA.\n                Upload expert criterion evaluations, aggregate circular intuitionistic fuzzy judgments,\n                calculate score values, comparative coefficients, relative weights, and final normalized SWARA weights.\n            </p>\n        </div>\n        ', unsafe_allow_html=True)

def swara_header_panels():
    st.markdown('\n        <div class="info-grid">\n            <div class="mini-card developer-card">\n                <h4>Developer & Concept Designer</h4>\n                <p><strong>Dr. Saeed Alinejad - Shiraz University, Iran</strong></p>\n                <p>Advanced decision-making tool developer.</p>\n            </div>\n            <div class="mini-card">\n                <h4>CIF-SWARA Logic</h4>\n                <p>Each criterion is modeled through membership, non-membership, hesitation, and circular radius. This supports richer uncertainty representation than crisp SWARA weighting.</p>\n            </div>\n            <div class="mini-card">\n                <h4>Weighting Dashboard</h4>\n                <p>The final dashboard reports CIF aggregation, score values, s<sub>j</sub>, k<sub>j</sub>, q<sub>j</sub>, final normalized weights, and criterion ranks.</p>\n            </div>\n        </div>\n        ', unsafe_allow_html=True)

def swara_intro_card():
    st.markdown('\n        <div id="input-guide"></div>\n        <div class="glass-panel">\n            <span class="section-label">Input Guide</span>\n            <div class="caption-note">\n                Create one sheet per expert. Recommended format is a two-column vector:\n                <b>Criterion</b> and <b>Evaluation</b>. Valid terms are\n                <b>AL, VL, L, ML, AE, MH, H, VH, AH</b>. Optional sheet <b>Expert_Info</b>\n                can contain columns <b>Expert</b> and either <b>Weight</b> or <b>WeightTerm</b>.\n                Auxiliary sheets containing words like <b>scale</b>, <b>readme</b>, <b>instruction</b>, or <b>result</b> are skipped automatically.\n            </div>\n            <br>\n            <table style="width:100%; border-collapse: collapse; font-size:14px;">\n                <tr>\n                    <th style="text-align:left; padding:10px; background:rgba(47,166,106,0.20);">Criterion</th>\n                    <th style="text-align:left; padding:10px; background:rgba(47,166,106,0.20);">Evaluation</th>\n                </tr>\n                <tr><td style="padding:10px; background:rgba(255,255,255,0.72);">C1 - Implementation Cost</td><td style="padding:10px;">AH</td></tr>\n                <tr><td style="padding:10px; background:rgba(255,255,255,0.72);">C2 - Technical Feasibility</td><td style="padding:10px;">VH</td></tr>\n            </table>\n        </div>\n        ', unsafe_allow_html=True)

def swara_render_sheet_summary(expert_items, skipped_items):

    def make_cards(items, skipped=False):
        status = 'SKIPPED' if skipped else 'USED'
        item_class = 'sheet-clean-item skipped' if skipped else 'sheet-clean-item'
        if not items:
            return '<div class="sheet-clean-item skipped"><div class="sheet-name-wrap"><span class="sheet-dot"></span><span class="sheet-name">No sheets found</span></div><span class="sheet-status">EMPTY</span></div>'
        cards = []
        for item in items:
            safe_item = html.escape(str(item))
            cards.append(f'\n                <div class="{item_class}">\n                    <div class="sheet-name-wrap">\n                        <span class="sheet-dot"></span>\n                        <span class="sheet-name" title="{safe_item}">{safe_item}</span>\n                    </div>\n                    <span class="sheet-status">{status}</span>\n                </div>\n                ')
        return ''.join(cards)
    skipped_html = ''
    if skipped_items:
        skipped_html = f'\n            <div class="sheet-clean-section-label">Skipped non-expert sheets</div>\n            <div class="sheet-clean-grid">{make_cards(skipped_items, skipped=True)}</div>\n        '
    html_block = f'\n    <div class="sheet-clean-panel">\n        <div class="sheet-clean-header">\n            <div>\n                <h3 class="sheet-clean-title">Detected Expert Sheets</h3>\n                <p class="sheet-clean-subtitle">The workbook was read successfully. Green cards are expert sheets used in the CIF-SWARA weighting calculation; gold cards are auxiliary sheets that were skipped.</p>\n            </div>\n            <div class="sheet-clean-counts">\n                <div class="sheet-count-badge"><span class="num">{len(expert_items)}</span><span class="lbl">Used Sheets</span></div>\n                <div class="sheet-count-badge skipped"><span class="num">{len(skipped_items)}</span><span class="lbl">Skipped</span></div>\n            </div>\n        </div>\n        <div class="sheet-clean-section-label">Valid expert sheets</div>\n        <div class="sheet-clean-grid">{make_cards(expert_items, skipped=False)}</div>\n        {skipped_html}\n    </div>\n    '
    st.markdown(html_block, unsafe_allow_html=True)
swara_CIF_SWARA_SCALE_IMPORTANCE = {'AL': (0.05, 0.85), 'VL': (0.15, 0.75), 'L': (0.25, 0.65), 'ML': (0.35, 0.55), 'AE': (0.45, 0.45), 'MH': (0.55, 0.35), 'H': (0.65, 0.25), 'VH': (0.75, 0.15), 'AH': (0.85, 0.05)}
swara_CIF_SWARA_SCALE_LITERAL_DOC = {'AL': (0.85, 0.05), 'VL': (0.75, 0.15), 'L': (0.65, 0.25), 'ML': (0.55, 0.35), 'AE': (0.45, 0.45), 'MH': (0.35, 0.55), 'H': (0.25, 0.65), 'VH': (0.15, 0.75), 'AH': (0.05, 0.85)}
swara_TERM_DESCRIPTIONS = {'AL': 'Absolutely Low', 'VL': 'Very Low', 'L': 'Low', 'ML': 'Medium Low', 'AE': 'Average', 'MH': 'Medium High', 'H': 'High', 'VH': 'Very High', 'AH': 'Absolutely High'}
swara_EXPERT_INFO_SHEET_NAMES = {'expert_info', 'experts', 'expert_weights', 'decision_makers', 'decision maker weights', 'dm_weights'}
swara_CRITERION_COLUMN_ALIASES = {'criterion', 'criteria', 'factor', 'index'}
swara_EVALUATION_COLUMN_ALIASES = {'evaluation', 'assessment', 'term', 'linguistic', 'value'}

def swara_standardize_term(value) -> str:
    if pd.isna(value):
        raise ValueError('Empty value found in the input file.')
    return str(value).strip().upper().replace(' ', '')

def swara_linguistic_to_cif_pair(value, scale: Dict[str, Tuple[float, float]]) -> np.ndarray:
    key = swara_standardize_term(value)
    if key not in scale:
        raise ValueError(f"Invalid linguistic term '{value}'. Allowed terms are: AL, VL, L, ML, AE, MH, H, VH, AH.")
    mu, nu = scale[key]
    swara_validate_cif_pair(mu, nu, label=key)
    return np.array([mu, nu], dtype=float)

def swara_validate_cif_pair(mu: float, nu: float, label: str='') -> None:
    eps = 1e-12
    if not (0 - eps <= mu <= 1 + eps and 0 - eps <= nu <= 1 + eps):
        raise ValueError(f'Invalid CIF pair {label}: membership and non-membership must be in [0, 1].')
    if mu + nu > 1 + eps:
        raise ValueError(f'Invalid CIF pair {label}: mu + nu must be <= 1. Current value: {mu + nu:.6f}')

def swara_hesitation_degree(mu: float, nu: float) -> float:
    return max(0.0, 1.0 - float(mu) - float(nu))

def swara_clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how='all')
    df = df.dropna(axis=1, how='all')
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

def swara_is_auxiliary_sheet(sheet_name: str) -> bool:
    lower_name = sheet_name.lower().strip()
    if lower_name in swara_EXPERT_INFO_SHEET_NAMES:
        return False
    keywords = ['scale', 'readme', 'instruction', 'guide', 'result', 'output', 'weights']
    return any((keyword in lower_name for keyword in keywords))

def swara_detect_columns(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    criterion_col = None
    eval_col = None
    lower_map = {str(c).strip().lower(): c for c in df.columns}
    for lower, original in lower_map.items():
        if lower in swara_CRITERION_COLUMN_ALIASES:
            criterion_col = original
        if lower in swara_EVALUATION_COLUMN_ALIASES:
            eval_col = original
    if criterion_col is None and df.shape[1] >= 2:
        criterion_col = df.columns[0]
    if eval_col is None and df.shape[1] >= 2:
        eval_col = df.columns[1]
    return (criterion_col, eval_col)

def swara_extract_expert_vector(df: pd.DataFrame, scale: Dict[str, Tuple[float, float]]) -> Tuple[List[str], List[str], np.ndarray]:
    df = swara_clean_dataframe(df)
    allowed_terms = set(scale.keys())
    if df.empty:
        raise ValueError('Empty expert sheet.')
    if df.shape[1] >= 2:
        criterion_col, eval_col = swara_detect_columns(df)
        candidate_values = [swara_standardize_term(v) for v in df[eval_col].tolist() if not pd.isna(v)]
        if len(candidate_values) == df.shape[0] and all((v in allowed_terms for v in candidate_values)):
            criteria = df[criterion_col].astype(str).str.strip().tolist()
            terms = df[eval_col].astype(str).str.strip().tolist()
            vector = np.vstack([swara_linguistic_to_cif_pair(v, scale) for v in terms])
            return (criteria, terms, vector)
    if df.shape[0] >= 1:
        first_row = df.iloc[0, :]
        row_terms = []
        valid_cols = []
        for col, val in first_row.items():
            if pd.isna(val):
                continue
            key = swara_standardize_term(val)
            if key in allowed_terms:
                valid_cols.append(str(col).strip())
                row_terms.append(str(val).strip())
        if len(valid_cols) >= 2 and len(valid_cols) == len(row_terms):
            vector = np.vstack([swara_linguistic_to_cif_pair(v, scale) for v in row_terms])
            return (valid_cols, row_terms, vector)
    raise ValueError('Invalid SWARA expert sheet. Use two columns Criterion/Evaluation or one row with linguistic terms under criteria columns.')

def swara_read_excel_file(uploaded_file, scale: Dict[str, Tuple[float, float]]) -> Tuple[Dict[str, pd.DataFrame], Optional[pd.DataFrame], List[str]]:
    sheets = pd.read_excel(uploaded_file, sheet_name=None, dtype=object)
    expert_sheets: Dict[str, pd.DataFrame] = {}
    expert_info = None
    skipped_sheets: List[str] = []
    for sheet_name, df in sheets.items():
        df = swara_clean_dataframe(df)
        lower_name = sheet_name.lower().strip()
        if lower_name in swara_EXPERT_INFO_SHEET_NAMES:
            expert_info = df
            skipped_sheets.append(sheet_name)
            continue
        if swara_is_auxiliary_sheet(sheet_name):
            skipped_sheets.append(sheet_name)
            continue
        try:
            swara_extract_expert_vector(df, scale)
            expert_sheets[sheet_name] = df
        except Exception:
            skipped_sheets.append(sheet_name)
    if len(expert_sheets) == 0:
        raise ValueError('No valid CIF-SWARA expert vector was found. Each expert sheet must include Criterion/Evaluation columns or a one-row vector of allowed terms.')
    return (expert_sheets, expert_info, skipped_sheets)

def swara_get_column_by_alias(df: pd.DataFrame, aliases: set) -> Optional[str]:
    for col in df.columns:
        lower = str(col).strip().lower()
        if lower in aliases:
            return col
    return None

def swara_calculate_expert_weights(expert_names: List[str], expert_info: Optional[pd.DataFrame], scale: Dict[str, Tuple[float, float]]) -> pd.DataFrame:
    if expert_info is None or expert_info.empty:
        weights = np.ones(len(expert_names), dtype=float) / len(expert_names)
        return pd.DataFrame({'Expert': expert_names, 'Weight_Source': 'Equal', 'Term_or_Value': 'Equal', 'mu': np.nan, 'nu': np.nan, 'pi': np.nan, 'Raw_Expert_Value': np.nan, 'Expert_Weight': weights})
    df = swara_clean_dataframe(expert_info)
    expert_col = swara_get_column_by_alias(df, {'expert', 'decision_maker', 'dm', 'name'})
    weight_col = swara_get_column_by_alias(df, {'weight'})
    term_col = swara_get_column_by_alias(df, {'weightterm', 'term', 'linguistic', 'expertise', 'level'})
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
            rows.append({'Expert': expert, 'Weight_Source': 'Equal fallback', 'Term_or_Value': 'Missing', 'mu': np.nan, 'nu': np.nan, 'pi': np.nan, 'Raw_Expert_Value': 1.0})
            continue
        if weight_col is not None and (not pd.isna(row[weight_col])):
            raw_value = float(row[weight_col])
            rows.append({'Expert': expert, 'Weight_Source': 'Numeric weight', 'Term_or_Value': raw_value, 'mu': np.nan, 'nu': np.nan, 'pi': np.nan, 'Raw_Expert_Value': raw_value})
        elif term_col is not None and (not pd.isna(row[term_col])):
            term = swara_standardize_term(row[term_col])
            mu, nu = swara_linguistic_to_cif_pair(term, scale)
            pi = swara_hesitation_degree(mu, nu)
            denominator = max(1e-12, 1.0 - pi)
            raw_value = mu + pi * (mu / denominator)
            rows.append({'Expert': expert, 'Weight_Source': 'CIF expertise term', 'Term_or_Value': term, 'mu': mu, 'nu': nu, 'pi': pi, 'Raw_Expert_Value': raw_value})
        else:
            rows.append({'Expert': expert, 'Weight_Source': 'Equal fallback', 'Term_or_Value': 'Missing', 'mu': np.nan, 'nu': np.nan, 'pi': np.nan, 'Raw_Expert_Value': 1.0})
    weights_df = pd.DataFrame(rows)
    raw = weights_df['Raw_Expert_Value'].astype(float).clip(lower=0).to_numpy(dtype=float)
    if raw.sum() <= 0:
        weights = np.ones(len(expert_names), dtype=float) / len(expert_names)
    else:
        weights = raw / raw.sum()
    weights_df['Expert_Weight'] = weights
    return weights_df

def swara_aggregate_experts(expert_sheets: Dict[str, pd.DataFrame], expert_weights: np.ndarray, scale: Dict[str, Tuple[float, float]]) -> Tuple[List[str], pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    vectors = []
    terms_by_expert = []
    reference_criteria = None
    for sheet_name, df in expert_sheets.items():
        criteria, terms, vector = swara_extract_expert_vector(df, scale)
        if reference_criteria is None:
            reference_criteria = criteria
        elif criteria != reference_criteria:
            raise ValueError(f"Criteria in sheet '{sheet_name}' are not consistent with the first expert sheet.")
        vectors.append(vector)
        terms_by_expert.append(terms)
    vectors_array = np.stack(vectors, axis=0)
    weights = np.asarray(expert_weights, dtype=float)
    weights = weights / weights.sum()
    mus = vectors_array[:, :, 0]
    nus = vectors_array[:, :, 1]
    mu_agg = 1.0 - np.prod(np.power(1.0 - mus, weights[:, None]), axis=0)
    nu_agg = np.prod(np.power(nus, weights[:, None]), axis=0)
    radius = np.zeros(len(reference_criteria), dtype=float)
    for j in range(len(reference_criteria)):
        distances = np.sqrt((mu_agg[j] - mus[:, j]) ** 2 + (nu_agg[j] - nus[:, j]) ** 2)
        radius[j] = float(np.max(distances))
    aggregated = np.column_stack([mu_agg, nu_agg, radius])
    terms_df = pd.DataFrame(np.array(terms_by_expert).T, columns=list(expert_sheets.keys()))
    terms_df.insert(0, 'Criterion', reference_criteria)
    return (reference_criteria, terms_df, vectors_array, aggregated, weights)

def swara_calculate_scores(aggregated: np.ndarray, score_mode: str, lambda_value: float) -> np.ndarray:
    mu = aggregated[:, 0]
    nu = aggregated[:, 1]
    r = aggregated[:, 2]
    if score_mode.startswith('Lambda'):
        return mu - nu + (2.0 * lambda_value - 1.0) * r
    return mu - nu + 2.0 * r / 3.0

def swara_calculate_cif_swara(criteria: List[str], aggregated: np.ndarray, score_mode: str, lambda_value: float) -> pd.DataFrame:
    scores = swara_calculate_scores(aggregated, score_mode, lambda_value)
    result_df = pd.DataFrame({'Criterion': criteria, 'mu': aggregated[:, 0], 'nu': aggregated[:, 1], 'pi': [swara_hesitation_degree(mu, nu) for mu, nu in aggregated[:, :2]], 'r': aggregated[:, 2], 'Score_SV': scores})
    result_df = result_df.sort_values('Score_SV', ascending=False).reset_index(drop=True)
    s_values = []
    k_values = []
    q_values = []
    for idx, row in result_df.iterrows():
        if idx == 0:
            s_values.append(0.0)
            k_values.append(1.0)
            q_values.append(1.0)
        else:
            previous_score = float(result_df.loc[idx - 1, 'Score_SV'])
            current_score = float(row['Score_SV'])
            s_j = max(0.0, previous_score - current_score)
            k_j = 1.0 + s_j
            q_j = q_values[idx - 1] / k_j
            s_values.append(s_j)
            k_values.append(k_j)
            q_values.append(q_j)
    result_df['s_j'] = s_values
    result_df['k_j'] = k_values
    result_df['q_j'] = q_values
    q_sum = float(np.sum(q_values))
    result_df['Weight'] = result_df['q_j'] / q_sum if q_sum > 0 else 1.0 / len(result_df)
    result_df['Rank'] = np.arange(1, len(result_df) + 1)
    return result_df

def swara_create_scale_dataframe(scale: Dict[str, Tuple[float, float]]) -> pd.DataFrame:
    rows = []
    for term, (mu, nu) in scale.items():
        rows.append({'Term': term, 'Description': swara_TERM_DESCRIPTIONS[term], 'mu': mu, 'nu': nu, 'pi': swara_hesitation_degree(mu, nu)})
    return pd.DataFrame(rows)

def swara_create_template_excel() -> bytes:
    output = BytesIO()
    criteria = ['C1 - Implementation Cost', 'C2 - Implementation Feasibility', 'C3 - Performance Impact', 'C4 - Stakeholder Acceptance', 'C5 - Technical Complexity', 'C6 - Sustainability Contribution', 'C7 - Data Availability', 'C8 - Risk Reduction']
    expert_1 = pd.DataFrame({'Criterion': criteria, 'Evaluation': ['AH', 'VH', 'H', 'MH', 'AE', 'H', 'MH', 'VH']})
    expert_2 = pd.DataFrame({'Criterion': criteria, 'Evaluation': ['VH', 'H', 'H', 'AE', 'MH', 'VH', 'H', 'MH']})
    expert_3 = pd.DataFrame({'Criterion': criteria, 'Evaluation': ['AH', 'VH', 'MH', 'H', 'AE', 'H', 'VH', 'H']})
    expert_info = pd.DataFrame({'Expert': ['Expert_1', 'Expert_2', 'Expert_3'], 'WeightTerm': ['AH', 'VH', 'H']})
    readme = pd.DataFrame({'Guide': ['Create one sheet per expert.', 'Use columns Criterion and Evaluation.', 'Allowed terms: AL, VL, L, ML, AE, MH, H, VH, AH.', 'Optional Expert_Info sheet can use WeightTerm or numeric Weight.']})
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        expert_1.to_excel(writer, sheet_name='Expert_1', index=False)
        expert_2.to_excel(writer, sheet_name='Expert_2', index=False)
        expert_3.to_excel(writer, sheet_name='Expert_3', index=False)
        expert_info.to_excel(writer, sheet_name='Expert_Info', index=False)
        readme.to_excel(writer, sheet_name='README', index=False)
        swara_create_scale_dataframe(swara_CIF_SWARA_SCALE_IMPORTANCE).to_excel(writer, sheet_name='CIF_SWARA_Scale', index=False)
    return output.getvalue()

def swara_create_excel_output(expert_sheets: Dict[str, pd.DataFrame], skipped_sheets: List[str], scale_df: pd.DataFrame, expert_weights_df: pd.DataFrame, terms_df: pd.DataFrame, aggregated: np.ndarray, result_df: pd.DataFrame, criteria: List[str], score_mode: str, lambda_value: float, scale_mode: str) -> bytes:
    output = BytesIO()
    aggregated_df = pd.DataFrame({'Criterion': criteria, 'mu': aggregated[:, 0], 'nu': aggregated[:, 1], 'pi': [swara_hesitation_degree(mu, nu) for mu, nu in aggregated[:, :2]], 'r': aggregated[:, 2]})
    parameter_df = pd.DataFrame({'Parameter': ['Scale_Mode', 'Score_Mode', 'Lambda', 'Number_of_Experts', 'Number_of_Criteria'], 'Value': [scale_mode, score_mode, lambda_value, len(expert_sheets), len(criteria)]})
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in expert_sheets.items():
            safe_name = sheet_name[:20]
            df.to_excel(writer, sheet_name=f'Input_{safe_name}', index=False)
        scale_df.to_excel(writer, sheet_name='CIF_SWARA_Scale', index=False)
        parameter_df.to_excel(writer, sheet_name='Parameters', index=False)
        expert_weights_df.to_excel(writer, sheet_name='Expert_Weights', index=False)
        terms_df.to_excel(writer, sheet_name='Expert_Terms', index=False)
        aggregated_df.to_excel(writer, sheet_name='Aggregated_CIF', index=False)
        result_df.to_excel(writer, sheet_name='CIF_SWARA_Weights', index=False)
        pd.DataFrame({'Skipped_sheets': skipped_sheets}).to_excel(writer, sheet_name='Skipped_Sheets', index=False)
    return output.getvalue()

def swara_run_app():
    st.set_page_config(page_title='CIF-SWARA | Executive Edition', page_icon='S', layout='wide', initial_sidebar_state='expanded')
    swara_apply_custom_style()
    swara_hamburger_menu()
    swara_hero_section()
    st.markdown('<div class="three-d-divider"></div>', unsafe_allow_html=True)
    swara_header_panels()
    swara_intro_card()
    with st.sidebar:
        st.markdown('\n            <div class="sidebar-block">\n                <h4>Developer</h4>\n                <p><strong>Dr. Saeed Alinejad - Shiraz University, Iran</strong></p>\n            </div>\n            ', unsafe_allow_html=True)
        scale_mode = st.radio('SWARA Scale Orientation', ['Importance-oriented scale: AH highest membership', 'Literal Word-table order: AL highest membership'], index=0, help='Use the first option for normal SWARA importance weighting. Use the second only if you want the literal extracted table orientation.')
        scale = swara_CIF_SWARA_SCALE_IMPORTANCE if scale_mode.startswith('Importance') else swara_CIF_SWARA_SCALE_LITERAL_DOC
        score_mode = st.selectbox('Score Function', ['Document Eq. 22: mu - nu + 2r/3', 'Lambda-adjusted sensitivity: mu - nu + (2lambda - 1)r'], index=0)
        lambda_value = st.slider('Lambda attitude parameter', 0.0, 1.0, 0.5, 0.05)
        st.markdown('\n            <div class="sidebar-block">\n                <h4>Allowed Linguistic Terms</h4>\n                <ul>\n                    <li>AL = Absolutely Low</li>\n                    <li>VL = Very Low</li>\n                    <li>L = Low</li>\n                    <li>ML = Medium Low</li>\n                    <li>AE = Average</li>\n                    <li>MH = Medium High</li>\n                    <li>H = High</li>\n                    <li>VH = Very High</li>\n                    <li>AH = Absolutely High</li>\n                </ul>\n            </div>\n            ', unsafe_allow_html=True)
        st.markdown(f'\n            <div class="sidebar-block">\n                <h4>Server</h4>\n                <p><code>{swara_DISPLAY_URL}</code></p>\n                <p>Change DISPLAY_URL at the top of the file if your PC IP is different.</p>\n            </div>\n            ', unsafe_allow_html=True)
        st.download_button(label='Download Input Template', data=swara_create_template_excel(), file_name='cif_swara_input_template.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    scale_df = swara_create_scale_dataframe(scale)
    st.markdown('<div id="active-scale"></div>', unsafe_allow_html=True)
    scale_tab, expert_scale_tab = st.tabs(['SWARA Linguistic Scale', 'Expert Weight Scale'])
    with scale_tab:
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.subheader('Active CIF-SWARA Linguistic Scale')
        st.dataframe(scale_df.round(6), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with expert_scale_tab:
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.subheader('Expert Weight Linguistic Scale')
        st.dataframe(scale_df.round(6), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div id="upload-workbook"></div>', unsafe_allow_html=True)
    st.markdown('\n        <div class="upload-zone-card upload-zone-gold-final" style="background:radial-gradient(circle at 9% 12%, rgba(255,255,255,0.45), transparent 28%), radial-gradient(circle at 88% 16%, rgba(255,244,210,0.38), transparent 32%), linear-gradient(135deg,#6F4E00 0%,#9B7208 23%,#D4AF37 52%,#FFD166 74%,#8A6508 100%) !important; border:2px solid rgba(255,244,210,0.98) !important; box-shadow:0 30px 68px rgba(111,78,0,0.38), 0 0 0 5px rgba(255,209,102,0.22), 0 6px 0 rgba(255,255,255,0.28) inset !important;">\n            <div class="upload-zone-badge" style="display:inline-block; color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; background:rgba(16,42,67,0.36) !important; border:1px solid rgba(255,255,255,0.58) !important; padding:8px 16px !important; border-radius:999px !important; font-weight:950 !important; letter-spacing:0.9px !important; text-transform:uppercase !important; text-shadow:0 2px 10px rgba(0,0,0,0.35) !important;">Upload Zone</div>\n            <div class="upload-zone-title" style="color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; opacity:1 !important; font-size:28px !important; font-weight:950 !important; line-height:1.25 !important; margin:30px 0 26px 0 !important; text-shadow:0 4px 16px rgba(0,0,0,0.68) !important;">Upload Your CIF-SWARA Excel Workbook</div>\n            <div id="force-upload-desc-white" class="upload-zone-description" style="margin-top:18px !important; color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; opacity:1 !important; font-size:16px !important; font-weight:900 !important; line-height:1.9 !important; text-shadow:0 4px 18px rgba(0,0,0,0.78) !important; background:rgba(16,42,67,0.22) !important; border:1px solid rgba(255,255,255,0.24) !important; border-radius:14px !important; padding:12px 14px !important;"><span style="color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; opacity:1 !important; font-weight:900 !important; text-shadow:0 4px 18px rgba(0,0,0,0.78) !important;">Load expert criterion-evaluation vectors. The app will calculate aggregated CIF vectors, circular radii, score values, comparative coefficients, relative weights, final normalized weights, and criterion ranking.</span></div>\n        </div>\n        ', unsafe_allow_html=True)
    uploaded_file = st.file_uploader('Upload CIF-SWARA Excel workbook', type=['xlsx'])
    if uploaded_file is None:
        st.info('Download the template from the sidebar, fill your expert evaluation sheets, then upload the workbook here.')
        return
    try:
        expert_sheets, expert_info, skipped_sheets = swara_read_excel_file(uploaded_file, scale)
        expert_names = list(expert_sheets.keys())
        expert_weights_df = swara_calculate_expert_weights(expert_names, expert_info, scale)
        criteria, terms_df, vectors_array, aggregated, normalized_weights = swara_aggregate_experts(expert_sheets, expert_weights_df['Expert_Weight'].to_numpy(dtype=float), scale)
        result_df = swara_calculate_cif_swara(criteria, aggregated, score_mode, lambda_value)
        display_criteria = swara_display_criterion_labels(criteria)
        st.markdown('<div id="results-dashboard"></div>', unsafe_allow_html=True)
        st.success('CIF-SWARA calculations completed successfully.')
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric('Valid Expert Sheets', len(expert_sheets))
        with c2:
            st.metric('Criteria', len(criteria))
        with c3:
            st.metric('Top Criterion', swara_display_criterion_label(result_df.iloc[0]['Criterion']))
        with c4:
            st.metric('Top Weight', f"{result_df.iloc[0]['Weight']:.6f}")
        overview_tab, vector_tab, ranking_tab, export_tab = st.tabs(['Overview', 'CIF Vectors', 'Weights', 'Export'])
        with overview_tab:
            swara_render_sheet_summary(expert_names, skipped_sheets)
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Expert Weights')
            st.dataframe(expert_weights_df.round(6), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Expert Linguistic Evaluations')
            terms_display_df = terms_df.copy()
            if 'Criterion' in terms_display_df.columns:
                terms_display_df['Criterion'] = terms_display_df['Criterion'].map(swara_display_criterion_label)
            st.dataframe(terms_display_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with vector_tab:
            aggregated_df = pd.DataFrame({'Criterion': display_criteria, 'mu': aggregated[:, 0], 'nu': aggregated[:, 1], 'pi': [swara_hesitation_degree(mu, nu) for mu, nu in aggregated[:, :2]], 'r': aggregated[:, 2]})
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Aggregated Circular Intuitionistic Fuzzy Vector')
            st.dataframe(aggregated_df.round(6), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            raw_vectors = []
            for expert_index, expert_name in enumerate(expert_names):
                for criterion_index, criterion in enumerate(criteria):
                    mu = vectors_array[expert_index, criterion_index, 0]
                    nu = vectors_array[expert_index, criterion_index, 1]
                    raw_vectors.append({'Expert': expert_name, 'Criterion': swara_display_criterion_label(criterion), 'mu': mu, 'nu': nu, 'pi': swara_hesitation_degree(mu, nu)})
            raw_vectors_df = pd.DataFrame(raw_vectors)
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Expert CIF Pairs')
            st.dataframe(raw_vectors_df.round(6), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with ranking_tab:
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Final CIF-SWARA Weights')
            result_display_df = result_df.copy()
            result_display_df['Criterion'] = result_display_df['Criterion'].map(swara_display_criterion_label)
            st.dataframe(result_display_df.round(6), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            chart_df = result_display_df[['Criterion', 'Weight']].copy()
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Weight Profile')
            st.bar_chart(chart_df.set_index('Criterion'))
            st.markdown('</div>', unsafe_allow_html=True)
        with export_tab:
            excel_output = swara_create_excel_output(expert_sheets=expert_sheets, skipped_sheets=skipped_sheets, scale_df=scale_df, expert_weights_df=expert_weights_df, terms_df=terms_df, aggregated=aggregated, result_df=result_df, criteria=criteria, score_mode=score_mode, lambda_value=lambda_value, scale_mode=scale_mode)
            st.markdown('<div id="download-results"></div>', unsafe_allow_html=True)
            st.download_button(label='Download Excel Results', data=excel_output, file_name='cif_swara_results.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            st.caption(f'Score mode = {score_mode} | Lambda = {lambda_value:.2f}')
    except Exception as error:
        st.error(f'Error: {error}')
    st.markdown('\n        <div class="footer-note">\n            Executive CIF-SWARA Interface - Designed for professional circular intuitionistic fuzzy weighting analytics.\n        </div>\n        ', unsafe_allow_html=True)

def swara_is_running_inside_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


# ============================== WASPAS MODULE ==============================
# The WASPAS calculation engine is integrated as the third independent tab.
# Its original standalone application description was removed to prevent
# Streamlit from rendering a WASPAS-only text block above the unified suite.
import os
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
    waspas_PLOTLY_AVAILABLE = True
except Exception:
    waspas_PLOTLY_AVAILABLE = False
os.environ.setdefault('STREAMLIT_THEME_BASE', 'light')
os.environ.setdefault('STREAMLIT_BROWSER_GATHER_USAGE_STATS', 'false')
waspas_APP_TITLE = 'CIF-WASPAS | Executive Edition'
waspas_PORT = 8802
waspas_SERVER_ADDRESS = '0.0.0.0'
waspas_PERSIAN_DIGIT_MAP = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩٫٬', '01234567890123456789..')
waspas_CIF_VALUE_SCALE = {'CHV': {'description': 'Certainly High Value', 'mu': 0.9, 'nu': 0.1}, 'VHV': {'description': 'Very High Value', 'mu': 0.8, 'nu': 0.15}, 'HV': {'description': 'High Value', 'mu': 0.7, 'nu': 0.25}, 'AAV': {'description': 'Above Average Value', 'mu': 0.6, 'nu': 0.35}, 'AV': {'description': 'Average Value', 'mu': 0.5, 'nu': 0.45}, 'UAV': {'description': 'Under Average Value', 'mu': 0.4, 'nu': 0.55}, 'LV': {'description': 'Low Value', 'mu': 0.3, 'nu': 0.65}, 'VLV': {'description': 'Very Low Value', 'mu': 0.2, 'nu': 0.75}, 'CLV': {'description': 'Certainly Low Value', 'mu': 0.1, 'nu': 0.9}}
waspas_NUMERIC_TERM_MAP = {9: 'CHV', 8: 'VHV', 7: 'HV', 6: 'AAV', 5: 'AV', 4: 'UAV', 3: 'LV', 2: 'VLV', 1: 'CLV'}
waspas_EXPERT_INFO_SHEET_NAMES = {'expert_info', 'experts', 'expert_weights', 'decision_makers', 'dm_weights'}
waspas_CRITERIA_WEIGHT_SHEET_NAMES = {'criteria_weights', 'criterion_weights', 'weights', 'swara_weights', 'cif_swara_weights'}
waspas_CRITERIA_TYPE_SHEET_NAMES = {'criteria_types', 'criterion_types', 'types', 'benefit_cost', 'criteria_info'}
waspas_AUX_SHEET_KEYWORDS = {'scale', 'readme', 'instruction', 'guide', 'result', 'output', 'parameter', 'template', 'note'}
waspas_ALTERNATIVE_ALIASES = {'alternative', 'alternatives', 'option', 'options', 'solution', 'solutions', 'item', 'case', 'a'}
waspas_CRITERION_ALIASES = {'criterion', 'criteria', 'factor', 'attribute', 'indicator', 'column', 'c'}
waspas_VALUE_ALIASES = {'value', 'term', 'evaluation', 'assessment', 'score', 'rating', 'cif'}
waspas_EXPERT_ALIASES = {'expert', 'decision_maker', 'dm', 'name'}
waspas_WEIGHT_ALIASES = {'weight', 'w', 'criterion_weight', 'criteria_weight', 'final_swara_weight', 'final_weight'}
waspas_TYPE_ALIASES = {'type', 'criterion_type', 'criteria_type', 'benefit_cost', 'direction'}
waspas_PAIR_PATTERN = re.compile('^[\\s\\(\\[\\{<]*([+-]?(?:\\d+(?:\\.\\d*)?|\\.\\d+))\\s*[,;/|]\\s*([+-]?(?:\\d+(?:\\.\\d*)?|\\.\\d+))[\\s\\)\\]\\}>]*$')

def waspas_apply_custom_style():
    st.markdown('\n        <style>\n        @import url(\'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap\');\n\n        :root {\n            --cif-emerald: #2FA66A;\n            --cif-emerald-dark: #1F6F49;\n            --cif-forest: #123B2A;\n            --cif-deep: #0C2D20;\n            --cif-gold: #D4AF37;\n            --cif-gold-soft: #FFF3C4;\n            --cif-gold-dark: #8A6508;\n            --cif-text: #102018;\n            --cif-muted: #52685B;\n            --cif-card: rgba(255, 255, 255, 0.95);\n            --cif-border: rgba(47, 166, 106, 0.28);\n            --cif-shadow: rgba(31, 111, 73, 0.14);\n        }\n\n        html, body, [class*="css"] {\n            font-family: \'Inter\', \'Segoe UI\', sans-serif;\n        }\n\n        .stApp {\n            background:\n                radial-gradient(circle at 7% 7%, rgba(47,166,106,0.30), transparent 27%),\n                radial-gradient(circle at 92% 12%, rgba(212,175,55,0.26), transparent 30%),\n                radial-gradient(circle at 78% 92%, rgba(31,111,73,0.16), transparent 32%),\n                linear-gradient(145deg, #FBFFFC 0%, #F4FFF8 36%, #FFF9E9 72%, #FFFFFF 100%) !important;\n            color: var(--cif-text) !important;\n        }\n\n        .block-container {\n            padding-top: 1.45rem;\n            padding-bottom: 2rem;\n            max-width: 1480px;\n        }\n\n        h1, h2, h3, h4, h5, h6,\n        .stMarkdown, .stMarkdown p, .stMarkdown li,\n        .stCaptionContainer, .stText, label,\n        div[data-testid="stWidgetLabel"], div[data-testid="stWidgetLabel"] p,\n        div[data-testid="stMarkdownContainer"] p,\n        div[data-testid="stMarkdownContainer"] li,\n        div[data-testid="stMetricLabel"], div[data-testid="stMetricDelta"],\n        .caption-note, .muted {\n            color: var(--cif-text) !important;\n        }\n\n        h1, h2, h3, h4 {\n            color: var(--cif-forest) !important;\n            letter-spacing: 0.15px;\n        }\n\n        p, li, td, th, span { text-rendering: optimizeLegibility; }\n\n        [data-testid="collapsedControl"],\n        [data-testid="stSidebarCollapsedControl"],\n        [data-testid="stSidebarCollapseButton"] {\n            border-radius: 18px !important;\n            background: linear-gradient(135deg, var(--cif-emerald-dark), var(--cif-emerald) 46%, var(--cif-gold)) !important;\n            box-shadow: 0 18px 38px rgba(31,111,73,0.25), 0 2px 0 rgba(255,255,255,0.34) inset !important;\n            border: 1px solid rgba(255,255,255,0.72) !important;\n        }\n\n        [data-testid="collapsedControl"] button,\n        [data-testid="stSidebarCollapsedControl"] button,\n        [data-testid="stSidebarCollapseButton"] button,\n        [data-testid="collapsedControl"] svg,\n        [data-testid="stSidebarCollapsedControl"] svg,\n        [data-testid="stSidebarCollapseButton"] svg {\n            color: #ffffff !important;\n            stroke-width: 2.8px !important;\n        }\n\n        .hamburger-shell {\n            position: sticky;\n            top: 0.75rem;\n            z-index: 999;\n            max-width: 460px;\n            margin: 0 0 16px auto;\n            border-radius: 22px;\n            background:\n                radial-gradient(circle at 10% 10%, rgba(255,255,255,0.45), transparent 28%),\n                linear-gradient(135deg, var(--cif-emerald-dark) 0%, var(--cif-emerald) 48%, var(--cif-gold) 100%);\n            border: 1px solid rgba(255,255,255,0.62);\n            box-shadow: 0 22px 46px rgba(31,111,73,0.22), 0 4px 0 rgba(255,255,255,0.25) inset;\n            backdrop-filter: blur(16px);\n            overflow: hidden;\n        }\n\n        .hamburger-shell summary {\n            list-style: none;\n            cursor: pointer;\n            user-select: none;\n            padding: 13px 16px;\n            display: flex;\n            align-items: center;\n            gap: 12px;\n        }\n\n        .hamburger-shell summary::-webkit-details-marker { display: none; }\n\n        .hamburger-icon {\n            width: 42px;\n            height: 42px;\n            display: inline-flex;\n            flex-direction: column;\n            justify-content: center;\n            align-items: center;\n            gap: 5px;\n            border-radius: 15px;\n            background: rgba(255,255,255,0.20);\n            box-shadow: 0 9px 20px rgba(7,22,63,0.16), 0 2px 0 rgba(255,255,255,0.28) inset;\n            transition: all 0.25s ease;\n        }\n\n        .hamburger-icon span {\n            width: 20px;\n            height: 2.5px;\n            border-radius: 999px;\n            background: #ffffff !important;\n            box-shadow: 0 1px 4px rgba(7,22,63,0.18);\n            transition: all 0.25s ease;\n        }\n\n        .hamburger-shell[open] .hamburger-icon span:nth-child(1) { transform: translateY(7.5px) rotate(45deg); }\n        .hamburger-shell[open] .hamburger-icon span:nth-child(2) { opacity: 0; transform: scaleX(0.2); }\n        .hamburger-shell[open] .hamburger-icon span:nth-child(3) { transform: translateY(-7.5px) rotate(-45deg); }\n\n        .hamburger-title {\n            color: #ffffff !important;\n            font-size: 15px;\n            font-weight: 950;\n            letter-spacing: 0.4px;\n            text-shadow: 0 2px 8px rgba(7,22,63,0.28);\n        }\n\n        .hamburger-pill {\n            margin-left: auto;\n            padding: 7px 10px;\n            border-radius: 999px;\n            color: #ffffff !important;\n            background: rgba(12,45,32,0.28);\n            border: 1px solid rgba(255,255,255,0.32);\n            font-size: 11px;\n            font-weight: 900;\n            text-transform: uppercase;\n            letter-spacing: 0.9px;\n        }\n\n        .hamburger-links {\n            display: grid;\n            grid-template-columns: repeat(2, minmax(0, 1fr));\n            gap: 9px;\n            padding: 0 14px 14px 14px;\n        }\n\n        .hamburger-links a {\n            text-decoration: none !important;\n            color: var(--cif-forest) !important;\n            font-size: 13px;\n            font-weight: 900;\n            padding: 10px 12px;\n            border-radius: 14px;\n            background: rgba(255,255,255,0.92);\n            border: 1px solid rgba(255,255,255,0.70);\n            box-shadow: 0 8px 18px rgba(7,22,63,0.11);\n            transition: all 0.22s ease;\n        }\n\n        .hamburger-links a:hover {\n            transform: translateY(-2px);\n            color: var(--cif-emerald-dark) !important;\n            background: #ffffff;\n            box-shadow: 0 12px 24px rgba(7,22,63,0.15);\n        }\n\n        @media (max-width: 760px) {\n            .hamburger-shell { margin-left: 0; max-width: 100%; }\n            .hamburger-links { grid-template-columns: 1fr; }\n            .hero-title { font-size: 34px !important; }\n        }\n\n        .hero-card {\n            position: relative;\n            overflow: hidden;\n            border-radius: 30px;\n            padding: 34px 34px 28px 34px;\n            margin-bottom: 20px;\n            background:\n                radial-gradient(circle at 10% 8%, rgba(255,255,255,0.42), transparent 28%),\n                radial-gradient(circle at 88% 18%, rgba(255,243,196,0.32), transparent 30%),\n                linear-gradient(135deg, #123B2A 0%, #1F6F49 44%, #2FA66A 70%, #D4AF37 100%) !important;\n            border: 1px solid rgba(255,255,255,0.58) !important;\n            box-shadow: 0 32px 76px rgba(31,111,73,0.28), 0 8px 0 rgba(255,255,255,0.18) inset !important;\n        }\n\n        .hero-card::before {\n            content: "";\n            position: absolute;\n            inset: 0;\n            background: linear-gradient(120deg, transparent 0%, rgba(255,255,255,0.56) 38%, transparent 74%);\n            transform: translateX(-100%);\n            animation: shine 7s linear infinite;\n            pointer-events: none;\n        }\n\n        @keyframes shine { 100% { transform: translateX(160%); } }\n\n        .hero-topline {\n            display: inline-block;\n            padding: 8px 14px;\n            border-radius: 999px;\n            background: rgba(255,255,255,0.18) !important;\n            border: 1px solid rgba(255,255,255,0.38) !important;\n            color: #ffffff !important;\n            font-size: 12px;\n            font-weight: 900;\n            letter-spacing: 1.35px;\n            text-transform: uppercase;\n            margin-bottom: 16px;\n            box-shadow: 0 8px 22px rgba(18,74,52,0.18), 0 2px 0 rgba(255,255,255,0.18) inset !important;\n            text-shadow: 0 2px 12px rgba(18,59,42,0.32) !important;\n        }\n\n        .hero-title {\n            font-size: 46px;\n            font-weight: 900;\n            line-height: 1.05;\n            margin: 0 0 10px 0;\n            color: #ffffff !important;\n            text-shadow: 0 3px 16px rgba(12,45,32,0.44) !important;\n        }\n\n        .hero-subtitle {\n            font-size: 16px;\n            line-height: 1.72;\n            color: #ffffff !important;\n            max-width: 1040px;\n            margin-bottom: 0;\n            font-weight: 650;\n            text-shadow: 0 2px 12px rgba(12,45,32,0.36) !important;\n        }\n\n        .three-d-divider {\n            height: 10px;\n            margin: 4px 0 18px 0;\n            border-radius: 999px;\n            background: linear-gradient(90deg, rgba(47,166,106,0.08), #2FA66A, #D4AF37, #1F6F49, rgba(212,175,55,0.08)) !important;\n            box-shadow: 0 10px 20px rgba(31,111,73,0.11), 0 2px 0 rgba(255,255,255,0.86) inset;\n        }\n\n        .info-grid {\n            display: grid;\n            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));\n            gap: 16px;\n            margin-bottom: 18px;\n        }\n\n        .mini-card, .glass-panel, .table-card, .brand-card, .sidebar-block, div[data-testid="metric-container"] {\n            position: relative;\n            overflow: hidden;\n            border-radius: 22px;\n            background: linear-gradient(145deg, #ffffff 0%, #F6FFF9 58%, #FFF9E9 100%) !important;\n            border: 1px solid var(--cif-border) !important;\n            box-shadow: 0 18px 44px var(--cif-shadow), 0 3px 0 rgba(255,255,255,0.96) inset !important;\n            backdrop-filter: blur(12px);\n        }\n\n        .mini-card { padding: 18px 18px 16px 18px; }\n        .glass-panel { padding: 20px 22px; margin-bottom: 18px; }\n        .table-card { padding: 16px 18px 18px 18px; margin-bottom: 18px; }\n        .brand-card { padding: 16px 18px; margin-bottom: 18px; }\n        .sidebar-block { padding: 14px 16px; margin-bottom: 15px; }\n\n        .mini-card:hover, .glass-panel:hover, .table-card:hover, .brand-card:hover, .sidebar-block:hover {\n            transform: translateY(-3px) rotateX(0.8deg);\n            box-shadow: 0 26px 58px rgba(31,111,73,0.17), 0 3px 0 rgba(255,255,255,0.95) inset !important;\n        }\n\n        .mini-card h4, .sidebar-block h4 {\n            font-size: 14px;\n            color: var(--cif-emerald-dark) !important;\n            margin-bottom: 8px;\n            text-transform: uppercase;\n            letter-spacing: 0.8px;\n        }\n\n        .mini-card p, .mini-card li, .sidebar-block p, .sidebar-block li, .caption-note, .muted {\n            color: var(--cif-muted) !important;\n            font-size: 14px;\n            line-height: 1.74;\n            margin-bottom: 0;\n        }\n\n        .mini-card strong, .brand-card strong, .sidebar-block strong { color: var(--cif-forest) !important; }\n\n        .developer-card {\n            background: radial-gradient(circle at 9% 12%, rgba(255,255,255,0.72), transparent 30%), linear-gradient(135deg, #FFF7DD 0%, #EEF9E7 42%, #DDF4E5 100%) !important;\n            border: 1px solid rgba(212,175,55,0.38) !important;\n            box-shadow: 0 22px 52px rgba(128,95,24,0.13), 0 8px 24px rgba(47,166,106,0.11), 0 3px 0 rgba(255,255,255,0.96) inset !important;\n        }\n\n        .developer-card::before {\n            content: "";\n            position: absolute;\n            inset: 0 auto 0 0;\n            width: 7px;\n            background: linear-gradient(180deg, var(--cif-gold) 0%, var(--cif-emerald) 54%, var(--cif-emerald-dark) 100%);\n            box-shadow: 6px 0 18px rgba(212,175,55,0.18);\n        }\n\n        .developer-card h4 { color: #7A5814 !important; }\n        .developer-card strong { color: #1F6F49 !important; font-weight: 950 !important; }\n        .developer-card p, .developer-card li { color: #3F513B !important; }\n\n        .section-label {\n            display: inline-block;\n            margin-bottom: 12px;\n            padding: 6px 12px;\n            border-radius: 999px;\n            background: rgba(47,166,106,0.13);\n            color: var(--cif-emerald-dark) !important;\n            border: 1px solid rgba(47,166,106,0.28);\n            font-size: 12px;\n            font-weight: 900;\n            letter-spacing: 1px;\n            text-transform: uppercase;\n        }\n\n        section[data-testid="stSidebar"] {\n            background: radial-gradient(circle at 16% 4%, rgba(47,166,106,0.20), transparent 30%), linear-gradient(180deg, #ffffff 0%, #F6FFF9 44%, #FFF9E9 100%) !important;\n            border-right: 1px solid rgba(47,166,106,0.26) !important;\n            box-shadow: 14px 0 36px rgba(31,111,73,0.10) !important;\n        }\n\n        section[data-testid="stSidebar"] * { color: var(--cif-text) !important; }\n\n        .brand-card .name {\n            color: var(--cif-forest) !important;\n            font-size: 20px;\n            font-weight: 900;\n            margin-top: 6px;\n            margin-bottom: 8px;\n        }\n\n        div[data-testid="metric-container"] {\n            border-radius: 18px !important;\n            padding: 15px !important;\n        }\n        div[data-testid="stMetricValue"] { color: var(--cif-emerald-dark) !important; font-weight: 900 !important; }\n        div[data-testid="stMetricLabel"] { color: var(--cif-forest) !important; font-weight: 800 !important; }\n\n        div[data-testid="stDataFrame"] {\n            background: rgba(255,255,255,0.92);\n            border: 1px solid rgba(47,166,106,0.16);\n            border-radius: 18px;\n            box-shadow: 0 16px 38px rgba(31,111,73,0.10);\n        }\n\n        .stTabs [data-baseweb="tab-list"] {\n            gap: 8px;\n            background: rgba(47,166,106,0.10) !important;\n            padding: 8px;\n            border-radius: 18px;\n            border: 1px solid rgba(47,166,106,0.18) !important;\n            box-shadow: 0 8px 18px rgba(31,111,73,0.07) inset;\n        }\n\n        .stTabs [data-baseweb="tab"] {\n            height: 42px;\n            border-radius: 12px;\n            background: rgba(255,255,255,0.96) !important;\n            color: var(--cif-forest) !important;\n            font-weight: 900;\n            padding: 0 18px;\n            border: 1px solid rgba(47,166,106,0.16) !important;\n            box-shadow: 0 6px 16px rgba(31,111,73,0.08);\n        }\n\n        .stTabs [aria-selected="true"] {\n            background: linear-gradient(135deg, var(--cif-emerald-dark) 0%, var(--cif-emerald) 50%, var(--cif-gold) 100%) !important;\n            color: #ffffff !important;\n            box-shadow: 0 10px 28px rgba(31,111,73,0.24), 0 2px 0 rgba(255,255,255,0.30) inset !important;\n        }\n\n        .stTabs [aria-selected="true"] p,\n        .stTabs [aria-selected="true"] span,\n        .stButton > button *, .stDownloadButton > button * { color: #ffffff !important; }\n\n        .stButton > button, .stDownloadButton > button {\n            background: linear-gradient(135deg, var(--cif-emerald-dark) 0%, var(--cif-emerald) 52%, var(--cif-gold) 100%) !important;\n            color: #ffffff !important;\n            border: 1px solid rgba(255,255,255,0.62) !important;\n            border-radius: 16px !important;\n            font-weight: 900 !important;\n            padding: 0.78rem 1.15rem !important;\n            box-shadow: 0 16px 30px rgba(31,111,73,0.22), 0 3px 0 rgba(255,255,255,0.34) inset !important;\n            transition: all 0.25s ease !important;\n        }\n\n        .stButton > button:hover, .stDownloadButton > button:hover {\n            transform: translateY(-2px) !important;\n            box-shadow: 0 20px 40px rgba(31,111,73,0.30), 0 3px 0 rgba(255,255,255,0.34) inset !important;\n        }\n\n        .upload-zone-card {\n            position: relative;\n            overflow: hidden;\n            margin: 8px 0 14px 0;\n            padding: 24px 26px;\n            border-radius: 26px;\n            background:\n                radial-gradient(circle at 9% 14%, rgba(255,255,255,0.52), transparent 28%),\n                radial-gradient(circle at 88% 16%, rgba(255,243,196,0.40), transparent 32%),\n                linear-gradient(135deg, #123B2A 0%, #1F6F49 38%, #2FA66A 68%, #D4AF37 100%) !important;\n            border: 1px solid rgba(255,255,255,0.62) !important;\n            box-shadow: 0 24px 48px rgba(31,111,73,0.25), 0 5px 0 rgba(255,255,255,0.22) inset !important;\n        }\n\n        .upload-zone-badge {\n            display: inline-block;\n            margin-bottom: 10px;\n            padding: 7px 13px;\n            border-radius: 999px;\n            background: rgba(255,255,255,0.20) !important;\n            color: #ffffff !important;\n            border: 1px solid rgba(255,255,255,0.42) !important;\n            font-size: 12px;\n            font-weight: 900;\n            letter-spacing: 1px;\n            text-transform: uppercase;\n            text-shadow: 0 2px 10px rgba(12,45,32,0.32);\n        }\n\n        .upload-zone-title {\n            color: #ffffff !important;\n            font-size: 25px !important;\n            font-weight: 950 !important;\n            line-height: 1.28 !important;\n            margin: 8px 0 8px 0 !important;\n            text-shadow: 0 4px 16px rgba(12,45,32,0.48) !important;\n        }\n\n        .upload-zone-description {\n            color: #ffffff !important;\n            opacity: 1 !important;\n            font-size: 15px !important;\n            font-weight: 750 !important;\n            line-height: 1.8 !important;\n            text-shadow: 0 3px 14px rgba(12,45,32,0.50) !important;\n            background: rgba(12,45,32,0.18) !important;\n            border: 1px solid rgba(255,255,255,0.20) !important;\n            border-radius: 14px !important;\n            padding: 10px 12px !important;\n        }\n\n        .stFileUploader, div[data-testid="stFileUploader"] {\n            background: linear-gradient(145deg, #ffffff 0%, #F6FFF9 58%, #FFF9E9 100%) !important;\n            border: 2px dashed rgba(47,166,106,0.72) !important;\n            padding: 14px !important;\n            border-radius: 22px !important;\n            box-shadow: 0 18px 36px rgba(31,111,73,0.14), 0 10px 26px rgba(18,74,52,0.07) inset !important;\n        }\n\n        div[data-testid="stAlert"] {\n            border-radius: 18px !important;\n            border: 1px solid rgba(47,166,106,0.20) !important;\n            box-shadow: 0 12px 26px rgba(31,111,73,0.08) !important;\n        }\n\n        .footer-note {\n            margin-top: 28px;\n            color: var(--cif-muted) !important;\n            font-size: 13px;\n            text-align: center;\n            opacity: 0.95;\n        }\n\n        code {\n            color: var(--cif-forest) !important;\n            background: rgba(47,166,106,0.10) !important;\n            border-radius: 8px;\n            padding: 2px 5px;\n        }\n        </style>\n        ', unsafe_allow_html=True)

def waspas_st_df(df: pd.DataFrame, height: Optional[int]=None) -> None:
    """Render dataframes safely across Streamlit versions.

    New Streamlit versions reject height=None. This helper only passes a
    height argument when it is a valid positive integer or an accepted layout
    keyword such as "stretch" or "content".
    """
    kwargs = {'width': 'stretch'}
    if isinstance(height, int) and height > 0:
        kwargs['height'] = height
    elif isinstance(height, str) and height in {'stretch', 'content'}:
        kwargs['height'] = height
    try:
        st.dataframe(df, **kwargs)
    except TypeError:
        fallback = {'use_container_width': True}
        if isinstance(height, int) and height > 0:
            fallback['height'] = height
        st.dataframe(df, **fallback)

def waspas_st_plot(fig) -> None:
    try:
        st.plotly_chart(fig, width='stretch')
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)

def waspas_clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how='all').dropna(axis=1, how='all').copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

def waspas_normalize_text(value) -> str:
    if pd.isna(value):
        return ''
    return str(value).strip().translate(waspas_PERSIAN_DIGIT_MAP)

def waspas_normalize_key(value) -> str:
    return re.sub('[^a-z0-9]+', '_', waspas_normalize_text(value).lower()).strip('_')

def waspas_get_column_by_alias(df: pd.DataFrame, aliases: set) -> Optional[str]:
    aliases_norm = {waspas_normalize_key(a) for a in aliases}
    for col in df.columns:
        if waspas_normalize_key(col) in aliases_norm:
            return col
    return None

def waspas_standardize_term(value) -> str:
    raw = waspas_normalize_text(value)
    if not raw:
        raise ValueError('Empty CIF linguistic term found.')
    compact = re.sub('\\s+', '', raw.upper()).replace('-', '').replace('_', '')
    try:
        number = int(round(float(compact)))
        if number in waspas_NUMERIC_TERM_MAP:
            return waspas_NUMERIC_TERM_MAP[number]
    except Exception:
        pass
    aliases = {'CHV': 'CHV', 'CERTAINLYHIGHVALUE': 'CHV', 'CERTAINLYHIGH': 'CHV', 'ABSOLUTELYHIGH': 'CHV', 'AH': 'CHV', 'VHV': 'VHV', 'VERYHIGHVALUE': 'VHV', 'VERYHIGH': 'VHV', 'VH': 'VHV', 'HV': 'HV', 'HIGHVALUE': 'HV', 'HIGH': 'HV', 'H': 'HV', 'AAV': 'AAV', 'ABOVEAVERAGEVALUE': 'AAV', 'ABOVEAVERAGE': 'AAV', 'MEDIUMHIGH': 'AAV', 'MH': 'AAV', 'AV': 'AV', 'AVERAGEVALUE': 'AV', 'AVERAGE': 'AV', 'EQUAL': 'AV', 'AE': 'AV', 'UAV': 'UAV', 'UNDERAVERAGEVALUE': 'UAV', 'UNDERAVERAGE': 'UAV', 'MEDIUMLOW': 'UAV', 'ML': 'UAV', 'LV': 'LV', 'LOWVALUE': 'LV', 'LOW': 'LV', 'L': 'LV', 'VLV': 'VLV', 'VERYLOWVALUE': 'VLV', 'VERYLOW': 'VLV', 'VL': 'VLV', 'CLV': 'CLV', 'CERTAINLYLOWVALUE': 'CLV', 'CERTAINLYLOW': 'CLV', 'ABSOLUTELYLOW': 'CLV', 'AL': 'CLV'}
    if compact in aliases:
        return aliases[compact]
    p = raw.replace(' ', '')
    if any((x in p for x in ['قطعاًزیاد', 'قطعازیاد', 'کاملاًزیاد', 'کاملازیاد', 'بسیارزیاد'])):
        return 'CHV'
    if 'خیلیزیاد' in p:
        return 'VHV'
    if 'بالاترازمتوسط' in p or 'بالاترازمتوسط' in p:
        return 'AAV'
    if 'زیاد' in p or 'بالا' in p:
        return 'HV'
    if 'متوسط' in p and 'کم' not in p and ('پایین' not in p):
        return 'AV'
    if 'پایینترازمتوسط' in p or 'کمترازمتوسط' in p:
        return 'UAV'
    if 'خیلیکم' in p or 'خیلیپایین' in p:
        return 'VLV'
    if any((x in p for x in ['قطعاًکم', 'قطعاکم', 'کاملاًکم', 'کاملاکم'])):
        return 'CLV'
    if 'کم' in p or 'پایین' in p:
        return 'LV'
    raise ValueError(f'Invalid CIF linguistic term: {value}')

def waspas_validate_cif_pair(pair: np.ndarray, label: str='') -> None:
    mu, nu = [float(v) for v in pair]
    eps = 1e-10
    if not (-eps <= mu <= 1.0 + eps and -eps <= nu <= 1.0 + eps):
        raise ValueError(f'Invalid CIF pair {label}: membership and non-membership must be in [0, 1].')
    if mu + nu > 1.0 + eps:
        raise ValueError(f'Invalid CIF pair {label}: mu + nu must be <= 1; current sum is {mu + nu:.6f}.')

def waspas_term_to_cif(value) -> np.ndarray:
    term = waspas_standardize_term(value)
    row = waspas_CIF_VALUE_SCALE[term]
    pair = np.array([row['mu'], row['nu']], dtype=float)
    waspas_validate_cif_pair(pair, label=term)
    return pair

def waspas_parse_cif_value(value) -> np.ndarray:
    """Accept a linguistic term, a 1-9 numeric alias, or a direct '(mu, nu)' pair."""
    if isinstance(value, np.ndarray):
        arr = np.asarray(value, dtype=float).reshape(-1)
        if len(arr) >= 2:
            pair = arr[:2]
            waspas_validate_cif_pair(pair, label=str(value))
            return pair
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        pair = np.array([float(value[0]), float(value[1])], dtype=float)
        waspas_validate_cif_pair(pair, label=str(value))
        return pair
    raw = waspas_normalize_text(value)
    match = waspas_PAIR_PATTERN.match(raw)
    if match:
        pair = np.array([float(match.group(1)), float(match.group(2))], dtype=float)
        waspas_validate_cif_pair(pair, label=raw)
        return pair
    return waspas_term_to_cif(value)

def waspas_hesitation_degree(mu: float, nu: float) -> float:
    return max(0.0, 1.0 - float(mu) - float(nu))

def waspas_cif_score(pair: np.ndarray) -> float:
    """Document Eq. (11): ((1-nu)(1-mu)+mu)/3."""
    mu, nu = [float(v) for v in pair]
    return ((1.0 - nu) * (1.0 - mu) + mu) / 3.0

def waspas_cif_accuracy(pair: np.ndarray) -> float:
    mu, nu = [float(v) for v in pair]
    return mu + nu

def waspas_cif_complement(pair: np.ndarray) -> np.ndarray:
    mu, nu = [float(v) for v in pair]
    return np.array([nu, mu], dtype=float)

def waspas__weighted_power_product(values: np.ndarray, weights: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    out = 1.0
    for value, weight in zip(values, weights):
        if weight <= 0:
            continue
        out *= float(value) ** float(weight)
    return float(out)

def waspas_cif_add(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    mu1, nu1 = [float(v) for v in a]
    mu2, nu2 = [float(v) for v in b]
    out = np.array([mu1 + mu2 - mu1 * mu2, nu1 * nu2], dtype=float)
    out = np.clip(out, 0.0, 1.0)
    waspas_validate_cif_pair(out, label='addition')
    return out

def waspas_cif_product(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    mu1, nu1 = [float(v) for v in a]
    mu2, nu2 = [float(v) for v in b]
    out = np.array([mu1 * mu2, nu1 + nu2 - nu1 * nu2], dtype=float)
    out = np.clip(out, 0.0, 1.0)
    waspas_validate_cif_pair(out, label='product')
    return out

def waspas_cif_scalar_multiply(weight: float, pair: np.ndarray) -> np.ndarray:
    weight = max(0.0, float(weight))
    mu, nu = [float(v) for v in pair]
    out = np.array([1.0 - (1.0 - mu) ** weight, nu ** weight], dtype=float)
    out = np.clip(out, 0.0, 1.0)
    waspas_validate_cif_pair(out, label='scalar multiplication')
    return out

def waspas_cif_power(pair: np.ndarray, weight: float) -> np.ndarray:
    weight = max(0.0, float(weight))
    mu, nu = [float(v) for v in pair]
    out = np.array([mu ** weight, 1.0 - (1.0 - nu) ** weight], dtype=float)
    out = np.clip(out, 0.0, 1.0)
    waspas_validate_cif_pair(out, label='power')
    return out

def waspas_cif_add_many(values: List[np.ndarray]) -> np.ndarray:
    total = np.array([0.0, 1.0], dtype=float)
    for value in values:
        total = waspas_cif_add(total, value)
    return total

def waspas_cif_product_many(values: List[np.ndarray]) -> np.ndarray:
    total = np.array([1.0, 0.0], dtype=float)
    for value in values:
        total = waspas_cif_product(total, value)
    return total

def waspas_cif_weighted_average(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    weights = weights / weights.sum() if weights.sum() > 0 else np.ones(len(values), dtype=float) / len(values)
    mu = 1.0 - waspas__weighted_power_product(1.0 - values[:, 0], weights)
    nu = waspas__weighted_power_product(values[:, 1], weights)
    out = np.clip(np.array([mu, nu], dtype=float), 0.0, 1.0)
    waspas_validate_cif_pair(out, label='IFWA aggregation')
    return out

def waspas_circular_radius(center: np.ndarray, values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    distances = np.sqrt(np.sum((values - center[None, :]) ** 2, axis=1))
    return float(np.max(distances)) if len(distances) else 0.0

def waspas_optimistic_pessimistic(center: np.ndarray, radius: float) -> Tuple[np.ndarray, np.ndarray, bool]:
    mu, nu = [float(v) for v in center]
    raw_o = np.array([mu + radius, nu - radius], dtype=float)
    raw_p = np.array([mu - radius, nu + radius], dtype=float)
    optimistic = np.clip(raw_o, 0.0, 1.0)
    pessimistic = np.clip(raw_p, 0.0, 1.0)
    adjusted = bool(np.any(np.abs(raw_o - optimistic) > 1e-12) or np.any(np.abs(raw_p - pessimistic) > 1e-12))
    waspas_validate_cif_pair(optimistic, label='optimistic point')
    waspas_validate_cif_pair(pessimistic, label='pessimistic point')
    return (optimistic, pessimistic, adjusted)

def waspas_weighted_sum_cif(row: np.ndarray, weights: np.ndarray) -> np.ndarray:
    return waspas_cif_add_many([waspas_cif_scalar_multiply(w, row[j, :]) for j, w in enumerate(weights)])

def waspas_weighted_product_cif(row: np.ndarray, weights: np.ndarray) -> np.ndarray:
    return waspas_cif_product_many([waspas_cif_power(row[j, :], w) for j, w in enumerate(weights)])

def waspas_combine_waspas(q1: np.ndarray, q2: np.ndarray, lambda_value: float) -> np.ndarray:
    lambda_value = float(np.clip(lambda_value, 0.0, 1.0))
    return waspas_cif_add(waspas_cif_scalar_multiply(lambda_value, q1), waspas_cif_scalar_multiply(1.0 - lambda_value, q2))

def waspas_standardize_criterion_type(value, default_type: str='Benefit') -> str:
    if pd.isna(value) or waspas_normalize_text(value) == '':
        return default_type
    text = waspas_normalize_text(value).lower().replace(' ', '_').replace('-', '_')
    if any((k in text for k in ['benefit', 'positive', 'max', 'maximize', 'gain', 'سود', 'مثبت', 'بیشینه'])):
        return 'Benefit'
    if any((k in text for k in ['cost', 'negative', 'min', 'minimize', 'expense', 'هزینه', 'منفی', 'کمینه'])):
        return 'Cost'
    raise ValueError(f"Unknown criterion type '{value}'. Use Benefit or Cost.")

def waspas_extract_wide_matrix(df: pd.DataFrame) -> Tuple[List[str], List[str], np.ndarray, np.ndarray]:
    df = waspas_clean_dataframe(df)
    if df.shape[1] < 2:
        raise ValueError('Decision matrix must have an Alternative column and at least one criterion.')
    alternatives = df.iloc[:, 0].astype(str).str.strip().tolist()
    criteria = [str(c).strip() for c in df.columns[1:]]
    raw = df.iloc[:, 1:].to_numpy(dtype=object)
    pairs = np.zeros((len(alternatives), len(criteria), 2), dtype=float)
    for i in range(len(alternatives)):
        for j in range(len(criteria)):
            pairs[i, j, :] = waspas_parse_cif_value(raw[i, j])
    return (alternatives, criteria, raw, pairs)

def waspas_extract_long_matrix(df: pd.DataFrame) -> Tuple[List[str], List[str], np.ndarray, np.ndarray]:
    df = waspas_clean_dataframe(df)
    alt_col = waspas_get_column_by_alias(df, waspas_ALTERNATIVE_ALIASES)
    crit_col = waspas_get_column_by_alias(df, waspas_CRITERION_ALIASES)
    value_col = waspas_get_column_by_alias(df, waspas_VALUE_ALIASES)
    if not alt_col or not crit_col or (not value_col):
        raise ValueError('Long decision matrix requires Alternative, Criterion, and Value columns.')
    alternatives = list(dict.fromkeys(df[alt_col].astype(str).str.strip().tolist()))
    criteria = list(dict.fromkeys(df[crit_col].astype(str).str.strip().tolist()))
    raw = np.empty((len(alternatives), len(criteria)), dtype=object)
    raw[:] = None
    pairs = np.zeros((len(alternatives), len(criteria), 2), dtype=float)
    a_idx = {a: i for i, a in enumerate(alternatives)}
    c_idx = {c: j for j, c in enumerate(criteria)}
    seen = set()
    for _, row in df.iterrows():
        a = str(row[alt_col]).strip()
        c = str(row[crit_col]).strip()
        key = (a, c)
        if key in seen:
            raise ValueError(f"Duplicate decision value for alternative '{a}' and criterion '{c}'.")
        seen.add(key)
        raw[a_idx[a], c_idx[c]] = row[value_col]
        pairs[a_idx[a], c_idx[c], :] = waspas_parse_cif_value(row[value_col])
    if len(seen) != len(alternatives) * len(criteria):
        raise ValueError('Long decision matrix is incomplete; every alternative-criterion combination is required.')
    return (alternatives, criteria, raw, pairs)

def waspas_extract_decision_matrix(df: pd.DataFrame) -> Tuple[List[str], List[str], np.ndarray, np.ndarray]:
    df = waspas_clean_dataframe(df)
    if df.empty:
        raise ValueError('Empty expert decision matrix.')
    if waspas_get_column_by_alias(df, waspas_ALTERNATIVE_ALIASES) and waspas_get_column_by_alias(df, waspas_CRITERION_ALIASES) and waspas_get_column_by_alias(df, waspas_VALUE_ALIASES):
        return waspas_extract_long_matrix(df)
    return waspas_extract_wide_matrix(df)

def waspas_is_aux_sheet(name: str) -> bool:
    key = waspas_normalize_key(name)
    if key in waspas_EXPERT_INFO_SHEET_NAMES or key in waspas_CRITERIA_WEIGHT_SHEET_NAMES or key in waspas_CRITERIA_TYPE_SHEET_NAMES:
        return True
    return any((word in key for word in waspas_AUX_SHEET_KEYWORDS))

def waspas_read_waspas_workbook(uploaded_file):
    sheets = pd.read_excel(uploaded_file, sheet_name=None, dtype=object)
    expert_sheets: Dict[str, pd.DataFrame] = {}
    expert_info = None
    criteria_weights = None
    criteria_types = None
    skipped: List[str] = []
    for name, df in sheets.items():
        df = waspas_clean_dataframe(df)
        key = waspas_normalize_key(name)
        if key in waspas_EXPERT_INFO_SHEET_NAMES:
            expert_info = df
            skipped.append(name)
        elif key in waspas_CRITERIA_WEIGHT_SHEET_NAMES:
            criteria_weights = df
            skipped.append(name)
        elif key in waspas_CRITERIA_TYPE_SHEET_NAMES:
            criteria_types = df
            skipped.append(name)
        elif waspas_is_aux_sheet(name):
            skipped.append(name)
        else:
            try:
                waspas_extract_decision_matrix(df)
                expert_sheets[name] = df
            except Exception:
                skipped.append(name)
    if not expert_sheets:
        raise ValueError('No valid expert decision matrix was found. Add at least one expert sheet.')
    if criteria_weights is None or criteria_weights.empty:
        raise ValueError('A Criteria_Weights sheet is required. It must contain Criterion and Weight columns.')
    return (expert_sheets, expert_info, criteria_weights, criteria_types, skipped)

def waspas_calculate_expert_weights(expert_names: List[str], expert_info: Optional[pd.DataFrame]) -> pd.DataFrame:
    if expert_info is None or expert_info.empty:
        weights = np.ones(len(expert_names), dtype=float) / len(expert_names)
        return pd.DataFrame({'Expert': expert_names, 'Weight_Source': 'Equal', 'Term_or_Value': 'Equal', 'mu': np.nan, 'nu': np.nan, 'pi': np.nan, 'Raw_Expert_Value': 1.0, 'Expert_Weight': weights})
    df = waspas_clean_dataframe(expert_info)
    expert_col = waspas_get_column_by_alias(df, waspas_EXPERT_ALIASES)
    weight_col = waspas_get_column_by_alias(df, {'weight', 'expert_weight', 'dm_weight'})
    term_col = waspas_get_column_by_alias(df, {'weightterm', 'weight_term', 'term', 'linguistic', 'expertise', 'level'})
    if expert_col:
        df[expert_col] = df[expert_col].astype(str).str.strip()
    rows = []
    for position, expert in enumerate(expert_names):
        row = None
        if expert_col:
            matches = df[df[expert_col] == expert]
            if not matches.empty:
                row = matches.iloc[0]
        elif position < len(df):
            row = df.iloc[position]
        if row is None:
            rows.append({'Expert': expert, 'Weight_Source': 'Equal fallback', 'Term_or_Value': 'Missing', 'mu': np.nan, 'nu': np.nan, 'pi': np.nan, 'Raw_Expert_Value': 1.0})
            continue
        if weight_col and (not pd.isna(row[weight_col])):
            raw_value = float(waspas_normalize_text(row[weight_col]))
            rows.append({'Expert': expert, 'Weight_Source': 'Numeric weight', 'Term_or_Value': raw_value, 'mu': np.nan, 'nu': np.nan, 'pi': np.nan, 'Raw_Expert_Value': raw_value})
        elif term_col and (not pd.isna(row[term_col])):
            pair = waspas_parse_cif_value(row[term_col])
            mu, nu = pair
            pi = waspas_hesitation_degree(mu, nu)
            raw_value = mu + pi * (mu / max(1e-12, 1.0 - pi))
            rows.append({'Expert': expert, 'Weight_Source': 'CIF expertise term', 'Term_or_Value': waspas_normalize_text(row[term_col]), 'mu': mu, 'nu': nu, 'pi': pi, 'Raw_Expert_Value': raw_value})
        else:
            rows.append({'Expert': expert, 'Weight_Source': 'Equal fallback', 'Term_or_Value': 'Missing', 'mu': np.nan, 'nu': np.nan, 'pi': np.nan, 'Raw_Expert_Value': 1.0})
    out = pd.DataFrame(rows)
    raw = out['Raw_Expert_Value'].astype(float).clip(lower=0).to_numpy(dtype=float)
    out['Expert_Weight'] = raw / raw.sum() if raw.sum() > 0 else np.ones(len(expert_names), dtype=float) / len(expert_names)
    return out

def waspas_read_criterion_weights(criteria: List[str], weights_df: pd.DataFrame) -> pd.DataFrame:
    df = waspas_clean_dataframe(weights_df)
    c_col = waspas_get_column_by_alias(df, waspas_CRITERION_ALIASES | {'name'})
    w_col = waspas_get_column_by_alias(df, waspas_WEIGHT_ALIASES)
    if not c_col or not w_col:
        raise ValueError('Criteria_Weights sheet must contain Criterion and Weight columns.')
    lookup = {}
    for _, row in df.iterrows():
        if pd.isna(row[c_col]) or pd.isna(row[w_col]):
            continue
        lookup[str(row[c_col]).strip()] = float(waspas_normalize_text(row[w_col]))
    weights = np.array([lookup.get(c, np.nan) for c in criteria], dtype=float)
    if np.isnan(weights).any():
        missing = [c for c, w in zip(criteria, weights) if np.isnan(w)]
        raise ValueError(f'Missing criterion weights for: {missing}')
    if np.any(weights < 0):
        raise ValueError('Criterion weights must be non-negative.')
    if weights.sum() <= 0:
        raise ValueError('The sum of criterion weights must be greater than zero.')
    normalized = weights / weights.sum()
    return pd.DataFrame({'Criterion': criteria, 'Original_Weight': weights, 'Weight': normalized, 'Weight_Source': 'Criteria_Weights'})

def waspas_criteria_types_from_sheet(criteria: List[str], type_df: Optional[pd.DataFrame]) -> pd.DataFrame:
    lookup = {}
    if type_df is not None and (not type_df.empty):
        df = waspas_clean_dataframe(type_df)
        c_col = waspas_get_column_by_alias(df, waspas_CRITERION_ALIASES | {'name'})
        t_col = waspas_get_column_by_alias(df, waspas_TYPE_ALIASES)
        if not c_col or not t_col:
            raise ValueError('Criteria_Types sheet must contain Criterion and Type columns.')
        for _, row in df.iterrows():
            if not pd.isna(row[c_col]):
                lookup[str(row[c_col]).strip()] = waspas_standardize_criterion_type(row[t_col])
    return pd.DataFrame({'Criterion': criteria, 'Type': [lookup.get(c, 'Benefit') for c in criteria]})

def waspas__align_expert_matrix(alts, criteria, raw, pairs, ref_alts, ref_criteria):
    if set(alts) != set(ref_alts):
        raise ValueError('Alternatives are inconsistent across expert sheets.')
    if set(criteria) != set(ref_criteria):
        raise ValueError('Criteria are inconsistent across expert sheets.')
    a_order = [alts.index(a) for a in ref_alts]
    c_order = [criteria.index(c) for c in ref_criteria]
    raw_aligned = raw[np.ix_(a_order, c_order)]
    pair_aligned = pairs[np.ix_(a_order, c_order, [0, 1])]
    return (raw_aligned, pair_aligned)

def waspas_aggregate_experts(expert_sheets: Dict[str, pd.DataFrame], expert_weights: np.ndarray, types_df: pd.DataFrame):
    expert_arrays = []
    term_matrices: Dict[str, pd.DataFrame] = {}
    ref_alts = ref_criteria = None
    for name, df in expert_sheets.items():
        alts, criteria, raw, pairs = waspas_extract_decision_matrix(df)
        if ref_alts is None:
            ref_alts, ref_criteria = (alts, criteria)
            raw_aligned, pairs_aligned = (raw, pairs)
        else:
            raw_aligned, pairs_aligned = waspas__align_expert_matrix(alts, criteria, raw, pairs, ref_alts, ref_criteria)
        expert_arrays.append(pairs_aligned)
        term_matrices[name] = pd.DataFrame(raw_aligned, index=ref_alts, columns=ref_criteria)
    stacked = np.stack(expert_arrays, axis=0)
    weights = np.asarray(expert_weights, dtype=float)
    weights = weights / weights.sum() if weights.sum() > 0 else np.ones(len(expert_arrays), dtype=float) / len(expert_arrays)
    m, n = (len(ref_alts), len(ref_criteria))
    aggregated = np.zeros((m, n, 2), dtype=float)
    radius = np.zeros((m, n), dtype=float)
    type_lookup = dict(zip(types_df['Criterion'], types_df['Type']))
    for i in range(m):
        for j, criterion in enumerate(ref_criteria):
            center = waspas_cif_weighted_average(stacked[:, i, j, :], weights)
            r = waspas_circular_radius(center, stacked[:, i, j, :])
            if type_lookup.get(criterion, 'Benefit') == 'Cost':
                center = waspas_cif_complement(center)
            aggregated[i, j, :] = center
            radius[i, j] = r
    return (ref_alts, ref_criteria, term_matrices, stacked, aggregated, radius, weights)

def waspas_score_matrix(matrix: np.ndarray) -> np.ndarray:
    m, n, _ = matrix.shape
    result = np.zeros((m, n), dtype=float)
    for i in range(m):
        for j in range(n):
            result[i, j] = waspas_cif_score(matrix[i, j, :])
    return result

def waspas_calculate_cif_waspas(uploaded_file, lambda_value: float=0.5, optimism_weight: float=0.5) -> Dict[str, object]:
    expert_sheets, expert_info, weights_raw, types_raw, skipped = waspas_read_waspas_workbook(uploaded_file)
    expert_names = list(expert_sheets.keys())
    first_alts, first_criteria, _, _ = waspas_extract_decision_matrix(next(iter(expert_sheets.values())))
    expert_weights_df = waspas_calculate_expert_weights(expert_names, expert_info)
    criteria_weights_df = waspas_read_criterion_weights(first_criteria, weights_raw)
    criteria_types_df = waspas_criteria_types_from_sheet(first_criteria, types_raw)
    alternatives, criteria, term_matrices, stacked, aggregated, radius, expert_weights = waspas_aggregate_experts(expert_sheets, expert_weights_df['Expert_Weight'].to_numpy(dtype=float), criteria_types_df)
    criterion_weights = criteria_weights_df['Weight'].to_numpy(dtype=float)
    optimistic = np.zeros_like(aggregated)
    pessimistic = np.zeros_like(aggregated)
    boundary_adjusted = np.zeros(radius.shape, dtype=bool)
    for i in range(len(alternatives)):
        for j in range(len(criteria)):
            optimistic[i, j, :], pessimistic[i, j, :], boundary_adjusted[i, j] = waspas_optimistic_pessimistic(aggregated[i, j, :], radius[i, j])
    q_rows = []
    for i, alternative in enumerate(alternatives):
        q1_o = waspas_weighted_sum_cif(optimistic[i, :, :], criterion_weights)
        q2_o = waspas_weighted_product_cif(optimistic[i, :, :], criterion_weights)
        q1_p = waspas_weighted_sum_cif(pessimistic[i, :, :], criterion_weights)
        q2_p = waspas_weighted_product_cif(pessimistic[i, :, :], criterion_weights)
        q_o = waspas_combine_waspas(q1_o, q2_o, lambda_value)
        q_p = waspas_combine_waspas(q1_p, q2_p, lambda_value)
        score_o = waspas_cif_score(q_o)
        score_p = waspas_cif_score(q_p)
        final_score = float(optimism_weight) * score_o + (1.0 - float(optimism_weight)) * score_p
        final_accuracy = float(optimism_weight) * waspas_cif_accuracy(q_o) + (1.0 - float(optimism_weight)) * waspas_cif_accuracy(q_p)
        q_rows.append({'Alternative': alternative, 'Q1_Optimistic_mu': q1_o[0], 'Q1_Optimistic_nu': q1_o[1], 'Q2_Optimistic_mu': q2_o[0], 'Q2_Optimistic_nu': q2_o[1], 'Q_Optimistic_mu': q_o[0], 'Q_Optimistic_nu': q_o[1], 'Score_Optimistic': score_o, 'Q1_Pessimistic_mu': q1_p[0], 'Q1_Pessimistic_nu': q1_p[1], 'Q2_Pessimistic_mu': q2_p[0], 'Q2_Pessimistic_nu': q2_p[1], 'Q_Pessimistic_mu': q_p[0], 'Q_Pessimistic_nu': q_p[1], 'Score_Pessimistic': score_p, 'Final_Accuracy': final_accuracy, 'Final_CIF_WASPAS_Score': final_score})
    result_df = pd.DataFrame(q_rows)
    result_df['Rank'] = result_df['Final_CIF_WASPAS_Score'].rank(ascending=False, method='dense').astype(int)
    result_df = result_df.sort_values(['Rank', 'Final_CIF_WASPAS_Score', 'Final_Accuracy', 'Alternative'], ascending=[True, False, False, True]).reset_index(drop=True)
    matrices = {'aggregated_mu': pd.DataFrame(aggregated[:, :, 0], index=alternatives, columns=criteria), 'aggregated_nu': pd.DataFrame(aggregated[:, :, 1], index=alternatives, columns=criteria), 'aggregated_pi': pd.DataFrame(1.0 - aggregated[:, :, 0] - aggregated[:, :, 1], index=alternatives, columns=criteria), 'radius_r': pd.DataFrame(radius, index=alternatives, columns=criteria), 'optimistic_mu': pd.DataFrame(optimistic[:, :, 0], index=alternatives, columns=criteria), 'optimistic_nu': pd.DataFrame(optimistic[:, :, 1], index=alternatives, columns=criteria), 'pessimistic_mu': pd.DataFrame(pessimistic[:, :, 0], index=alternatives, columns=criteria), 'pessimistic_nu': pd.DataFrame(pessimistic[:, :, 1], index=alternatives, columns=criteria), 'optimistic_score_matrix': pd.DataFrame(waspas_score_matrix(optimistic), index=alternatives, columns=criteria), 'pessimistic_score_matrix': pd.DataFrame(waspas_score_matrix(pessimistic), index=alternatives, columns=criteria), 'boundary_adjusted': pd.DataFrame(boundary_adjusted, index=alternatives, columns=criteria)}
    return {'results': result_df, 'criteria_weights': criteria_weights_df, 'criteria_types': criteria_types_df, 'expert_weights': expert_weights_df, 'matrices': matrices, 'term_matrices': term_matrices, 'skipped_sheets': skipped, 'params': {'lambda': float(lambda_value), 'optimism_weight': float(optimism_weight)}}

def waspas_scale_dataframe() -> pd.DataFrame:
    return pd.DataFrame([{'Term': term, 'Description': item['description'], 'mu': item['mu'], 'nu': item['nu'], 'pi': waspas_hesitation_degree(item['mu'], item['nu'])} for term, item in waspas_CIF_VALUE_SCALE.items()])

def waspas__style_openpyxl_workbook(workbook, dropdown_sheets: Optional[List[str]]=None) -> None:
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.worksheet.datavalidation import DataValidation
    emerald = '2FA66A'
    forest = '123B2A'
    gold = 'D4AF37'
    pale = 'F6FFF9'
    soft_gold = 'FFF3C4'
    white = 'FFFFFF'
    thin = Side(style='thin', color='C9DED1')
    for ws in workbook.worksheets:
        ws.freeze_panes = 'A2'
        ws.sheet_view.showGridLines = False
        for cell in ws[1]:
            cell.fill = PatternFill('solid', fgColor=forest)
            cell.font = Font(color=white, bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = Border(bottom=Side(style='medium', color=gold))
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(vertical='center', wrap_text=True)
                cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
                if cell.row % 2 == 0:
                    cell.fill = PatternFill('solid', fgColor=pale)
        for col_cells in ws.columns:
            values = [str(c.value) if c.value is not None else '' for c in col_cells]
            width = min(max(max((len(v) for v in values), default=8) + 2, 11), 34)
            ws.column_dimensions[col_cells[0].column_letter].width = width
        ws.row_dimensions[1].height = 28
    if dropdown_sheets:
        formula = '"' + ','.join(waspas_CIF_VALUE_SCALE.keys()) + '"'
        for sheet_name in dropdown_sheets:
            ws = workbook[sheet_name]
            if ws.max_column >= 2 and ws.max_row >= 2:
                dv = DataValidation(type='list', formula1=formula, allow_blank=False)
                dv.error = 'Select a valid CIF linguistic term.'
                dv.errorTitle = 'Invalid CIF term'
                dv.prompt = 'Choose CHV, VHV, HV, AAV, AV, UAV, LV, VLV, or CLV.'
                dv.promptTitle = 'CIF-WASPAS linguistic scale'
                ws.add_data_validation(dv)
                dv.add(f'B2:{ws.cell(1, ws.max_column).column_letter}{max(ws.max_row, 200)}')

def waspas_create_waspas_template() -> bytes:
    output = BytesIO()
    alternatives = ['A1 - Smart Analytics', 'A2 - Supplier Collaboration', 'A3 - Closed-Loop Platform', 'A4 - Predictive Maintenance', 'A5 - Digital Traceability']
    criteria = ['C1 - Strategic Value', 'C2 - Implementation Cost', 'C3 - Technical Feasibility', 'C4 - Sustainability Impact', 'C5 - Risk Reduction', 'C6 - Time to Deploy']
    expert_values = {'Expert_1': [['VHV', 'UAV', 'HV', 'CHV', 'VHV', 'AAV'], ['HV', 'AAV', 'VHV', 'HV', 'HV', 'HV'], ['CHV', 'LV', 'AAV', 'CHV', 'VHV', 'UAV'], ['VHV', 'AAV', 'HV', 'VHV', 'CHV', 'AAV'], ['HV', 'HV', 'VHV', 'VHV', 'HV', 'HV']], 'Expert_2': [['CHV', 'UAV', 'VHV', 'VHV', 'HV', 'AAV'], ['HV', 'HV', 'HV', 'VHV', 'VHV', 'HV'], ['VHV', 'LV', 'AAV', 'CHV', 'CHV', 'UAV'], ['VHV', 'AAV', 'VHV', 'HV', 'VHV', 'HV'], ['HV', 'VHV', 'HV', 'VHV', 'HV', 'VHV']], 'Expert_3': [['VHV', 'AAV', 'HV', 'CHV', 'VHV', 'HV'], ['AAV', 'HV', 'VHV', 'HV', 'HV', 'VHV'], ['CHV', 'UAV', 'HV', 'CHV', 'VHV', 'AAV'], ['HV', 'AAV', 'VHV', 'VHV', 'CHV', 'HV'], ['VHV', 'HV', 'VHV', 'VHV', 'HV', 'VHV']]}
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for expert, values in expert_values.items():
            df = pd.DataFrame(values, columns=criteria)
            df.insert(0, 'Alternative', alternatives)
            df.to_excel(writer, sheet_name=expert, index=False)
        pd.DataFrame({'Expert': list(expert_values.keys()), 'WeightTerm': ['VHV', 'HV', 'AAV']}).to_excel(writer, sheet_name='Expert_Info', index=False)
        pd.DataFrame({'Criterion': criteria, 'Weight': [0.2, 0.15, 0.17, 0.18, 0.17, 0.13]}).to_excel(writer, sheet_name='Criteria_Weights', index=False)
        pd.DataFrame({'Criterion': criteria, 'Type': ['Benefit', 'Cost', 'Benefit', 'Benefit', 'Benefit', 'Cost']}).to_excel(writer, sheet_name='Criteria_Types', index=False)
        waspas_scale_dataframe().to_excel(writer, sheet_name='CIF_Value_Scale', index=False)
        pd.DataFrame({'Guide': ['Create one decision-matrix sheet per expert.', 'Wide format: first column Alternative; remaining columns are criteria.', 'Cells may contain linguistic terms CHV...CLV or direct pairs such as (0.8, 0.15).', 'Criteria_Weights is required and is normalized automatically.', 'Criteria_Types is optional; omitted criteria default to Benefit.', 'Expert_Info is optional; without it, experts receive equal weights.', 'Cost criteria are converted by the intuitionistic complement before WASPAS operations.']}).to_excel(writer, sheet_name='README', index=False)
        workbook = writer.book
        waspas__style_openpyxl_workbook(workbook, dropdown_sheets=list(expert_values.keys()))
    return output.getvalue()

def waspas_export_waspas_results(results: Dict[str, object]) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        results['results'].to_excel(writer, sheet_name='Final_Ranking', index=False)
        pd.DataFrame({'Parameter': list(results['params'].keys()), 'Value': list(results['params'].values())}).to_excel(writer, sheet_name='Parameters', index=False)
        results['expert_weights'].to_excel(writer, sheet_name='Expert_Weights', index=False)
        results['criteria_weights'].to_excel(writer, sheet_name='Criteria_Weights', index=False)
        results['criteria_types'].to_excel(writer, sheet_name='Criteria_Types', index=False)
        for name, matrix in results['matrices'].items():
            matrix.to_excel(writer, sheet_name=name[:31], index=True)
        for expert, matrix in results['term_matrices'].items():
            safe_name = re.sub('[^A-Za-z0-9_]', '_', expert)[:20]
            matrix.to_excel(writer, sheet_name=f'Input_{safe_name}'[:31], index=True)
        waspas_scale_dataframe().to_excel(writer, sheet_name='CIF_Value_Scale', index=False)
        pd.DataFrame({'Skipped_Sheet': results['skipped_sheets']}).to_excel(writer, sheet_name='Skipped_Sheets', index=False)
        waspas__style_openpyxl_workbook(writer.book)
    return output.getvalue()

def waspas_show_bar(df: pd.DataFrame, x: str, y: str, title: str, text_col: Optional[str]=None) -> None:
    if waspas_PLOTLY_AVAILABLE:
        plot_df = df.copy().sort_values(x, ascending=True)
        fig = px.bar(plot_df, x=x, y=y, orientation='h', text=text_col or x, title=title, color=x, color_continuous_scale=['#FFF3C4', '#D4AF37', '#2FA66A', '#1F6F49', '#123B2A'])
        fig.update_traces(texttemplate='%{text:.4f}', textposition='outside')
        fig.update_layout(height=max(430, 68 * len(plot_df)), margin=dict(l=30, r=30, t=60, b=30), yaxis_title='', xaxis_title='', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.72)', font=dict(color='#102018'))
        waspas_st_plot(fig)
    else:
        waspas_st_df(df)

def waspas_show_heatmap(df: pd.DataFrame, title: str) -> None:
    if waspas_PLOTLY_AVAILABLE:
        fig = px.imshow(df, text_auto='.3f', aspect='auto', title=title, color_continuous_scale=['#FFFDF8', '#FFF3C4', '#D4AF37', '#2FA66A', '#123B2A'])
        fig.update_layout(height=520, margin=dict(l=30, r=30, t=60, b=30), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.72)', font=dict(color='#102018'))
        waspas_st_plot(fig)
    else:
        waspas_st_df(df.round(6))

def waspas_hamburger_menu() -> None:
    st.markdown('\n        <details class="hamburger-shell">\n            <summary>\n                <span class="hamburger-icon"><span></span><span></span><span></span></span>\n                <span class="hamburger-title">CIF Decision Suite</span>\n                <span class="hamburger-pill">WASPAS</span>\n            </summary>\n            <div class="hamburger-links">\n                <a href="#cif-waspas-workflow">CIF-WASPAS Workflow</a>\n                <a href="#input-guide">Input Guide</a>\n                <a href="#results-dashboard">Results</a>\n                <a href="#download-results">Export</a>\n            </div>\n        </details>\n        ', unsafe_allow_html=True)

def waspas_hero_section() -> None:
    st.markdown('\n        <div class="hero-card">\n            <div class="hero-topline">Green & Gold Circular Fuzzy Analytics</div>\n            <div class="hero-title">CIF-WASPAS Calculator</div>\n            <p class="hero-subtitle">\n                A professional Streamlit application for Circular Intuitionistic Fuzzy WASPAS.\n                Aggregate expert judgments, construct optimistic and pessimistic circular matrices,\n                calculate CIF weighted-sum and weighted-product utilities, and rank alternatives in a transparent workflow.\n            </p>\n        </div>\n        ', unsafe_allow_html=True)

def waspas_header_panels() -> None:
    st.markdown('\n        <div class="info-grid">\n            <div class="mini-card developer-card">\n                <h4>Developer & Concept Designer</h4>\n                <p><strong>Dr. Saeed Alinejad - Shiraz University, Iran</strong></p>\n                <p>Advanced circular fuzzy decision-support application.</p>\n            </div>\n            <div class="mini-card">\n                <h4>CIF Representation</h4>\n                <p>Every evaluation is modeled by membership μ, non-membership ν, hesitation π, and a circular radius r derived from expert dispersion.</p>\n            </div>\n            <div class="mini-card">\n                <h4>WASPAS Integration</h4>\n                <p>The application combines the weighted-sum and weighted-product CIF utilities through λ, reports optimistic and pessimistic scores, and produces a final rank.</p>\n            </div>\n        </div>\n        ', unsafe_allow_html=True)

def waspas_intro_card() -> None:
    st.markdown('\n        <div id="input-guide" class="glass-panel">\n            <span class="section-label">Input Workbook Guide</span>\n            <p class="caption-note">\n                Add one decision-matrix sheet per expert. Use a wide matrix with <b>Alternative</b> in the first column and criteria in the remaining columns,\n                or a long table with <b>Alternative</b>, <b>Criterion</b>, and <b>Value</b>. Values may be linguistic terms\n                <b>CHV, VHV, HV, AAV, AV, UAV, LV, VLV, CLV</b> or direct pairs such as <b>(0.80, 0.15)</b>.\n                A <b>Criteria_Weights</b> sheet is required. <b>Criteria_Types</b> and <b>Expert_Info</b> are optional.\n            </p>\n        </div>\n        ', unsafe_allow_html=True)

def waspas_upload_zone_card() -> None:
    st.markdown('\n        <div class="upload-zone-card">\n            <div class="upload-zone-badge">Upload Zone</div>\n            <div class="upload-zone-title">Upload Your CIF-WASPAS Excel Workbook</div>\n            <div class="upload-zone-description">\n                The engine validates expert matrices, aggregates CIF judgments, calculates circular radii,\n                evaluates optimistic and pessimistic utilities, and exports a complete audit-ready Excel report.\n            </div>\n        </div>\n        ', unsafe_allow_html=True)

def waspas_sidebar_content() -> None:
    with st.sidebar:
        st.markdown('\n            <div class="sidebar-block developer-card">\n                <h4>Developer</h4>\n                <p><strong>Dr. Saeed Alinejad - Shiraz University, Iran</strong></p>\n            </div>\n            <div class="sidebar-block">\n                <h4>Visual Theme</h4>\n                <p>Scientific emerald, forest green, and warm gold palette aligned with the executive CSF application.</p>\n            </div>\n            ', unsafe_allow_html=True)
        st.download_button('Download CIF-WASPAS Template', data=waspas_create_waspas_template(), file_name='cif_waspas_input_template.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        st.markdown('\n            <div class="sidebar-block">\n                <h4>Allowed Value Terms</h4>\n                <ul>\n                    <li>CHV, VHV, HV, AAV, AV</li>\n                    <li>UAV, LV, VLV, CLV</li>\n                    <li>Numeric aliases: 9 to 1</li>\n                    <li>Direct pair: (μ, ν)</li>\n                </ul>\n            </div>\n            <div class="sidebar-block">\n                <h4>Method Sequence</h4>\n                <p>Expert aggregation → radius → optimistic/pessimistic matrices → weighted sum/product → λ integration → crisp score → ranking.</p>\n            </div>\n            ', unsafe_allow_html=True)

def waspas_show_score_comparison(ranking: pd.DataFrame) -> None:
    plot_df = ranking[['Alternative', 'Score_Optimistic', 'Score_Pessimistic', 'Final_CIF_WASPAS_Score']].copy()
    if waspas_PLOTLY_AVAILABLE:
        melted = plot_df.melt(id_vars='Alternative', var_name='Score_Type', value_name='Score')
        fig = px.bar(melted, x='Alternative', y='Score', color='Score_Type', barmode='group', title='Optimistic, Pessimistic, and Final CIF-WASPAS Scores', color_discrete_sequence=['#2FA66A', '#D4AF37', '#123B2A'])
        fig.update_layout(height=520, margin=dict(l=30, r=30, t=65, b=40), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.72)', font=dict(color='#102018'), xaxis_title='')
        waspas_st_plot(fig)
    else:
        waspas_st_df(plot_df)

def waspas_waspas_app() -> None:
    st.markdown('<div id="cif-waspas-workflow" class="glass-panel"><span class="section-label">CIF-WASPAS Ranking</span><p class="caption-note">The implementation follows the supplied circular intuitionistic fuzzy operators and CIF-WASPAS sequence. Criterion weights can be imported from CIF-SWARA or any validated weighting method.</p></div>', unsafe_allow_html=True)
    left, right = st.columns([1, 2])
    with left:
        st.markdown('<div class="table-card"><span class="section-label">Parameters</span><p class="caption-note">λ balances the weighted-sum and weighted-product components. α balances optimistic and pessimistic crisp scores; the neutral document-style setting is 0.50.</p></div>', unsafe_allow_html=True)
        lambda_value = st.slider('WASPAS integration λ', 0.0, 1.0, 0.5, 0.05, help='λ=1 uses only the weighted-sum component; λ=0 uses only the weighted-product component.')
        optimism_weight = st.slider('Optimistic score weight α', 0.0, 1.0, 0.5, 0.05, help='Final score = α × optimistic score + (1−α) × pessimistic score.')
        st.download_button('Download input template', data=waspas_create_waspas_template(), file_name='cif_waspas_input_template.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', key='main_template')
    with right:
        waspas_upload_zone_card()
        uploaded = st.file_uploader('Upload CIF-WASPAS Excel workbook', type=['xlsx', 'xls'], key='waspas_upload')
    if not uploaded:
        st.info('Download the template, fill the expert decision matrices and criterion weights, then upload the workbook.')
        return
    try:
        results = waspas_calculate_cif_waspas(uploaded, lambda_value=lambda_value, optimism_weight=optimism_weight)
    except Exception as exc:
        st.error(f'CIF-WASPAS calculation failed: {exc}')
        return
    ranking = results['results']
    top_row = ranking.sort_values('Rank').iloc[0]
    adjusted_count = int(results['matrices']['boundary_adjusted'].to_numpy(dtype=bool).sum())
    st.markdown('<div id="results-dashboard"></div>', unsafe_allow_html=True)
    st.success('CIF-WASPAS calculations completed successfully.')
    if adjusted_count:
        st.warning(f'Boundary control clipped {adjusted_count} optimistic/pessimistic CIF point(s) to the valid [0,1] interval. The affected cells are listed in the Boundary_Adjusted matrix.')
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Alternatives', len(ranking))
    c2.metric('Criteria', len(results['criteria_weights']))
    c3.metric('Best alternative', str(top_row['Alternative']))
    c4.metric('Best score', f"{top_row['Final_CIF_WASPAS_Score']:.6f}")
    overview_tab, cif_tab, components_tab, visual_tab, export_tab = st.tabs(['Overview', 'CIF Matrices', 'WASPAS Components', 'Visual Maps', 'Export'])
    with overview_tab:
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.subheader('Final CIF-WASPAS ranking')
        display_cols = ['Rank', 'Alternative', 'Score_Optimistic', 'Score_Pessimistic', 'Final_CIF_WASPAS_Score', 'Final_Accuracy']
        waspas_st_df(ranking[display_cols].round(8))
        st.markdown('</div>', unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Criterion weights')
            waspas_st_df(results['criteria_weights'].round(8))
            st.caption(f"Normalized weights sum = {results['criteria_weights']['Weight'].sum():.8f}")
            st.markdown('</div>', unsafe_allow_html=True)
        with col_b:
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader('Criterion types')
            waspas_st_df(results['criteria_types'])
            st.markdown('</div>', unsafe_allow_html=True)
    with cif_tab:
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.subheader('Expert weights')
        waspas_st_df(results['expert_weights'].round(8))
        st.markdown('</div>', unsafe_allow_html=True)
        matrix_names = [('aggregated_mu', 'Aggregated membership μ'), ('aggregated_nu', 'Aggregated non-membership ν'), ('aggregated_pi', 'Aggregated hesitation π'), ('radius_r', 'Circular radius r'), ('optimistic_mu', 'Optimistic μ'), ('optimistic_nu', 'Optimistic ν'), ('pessimistic_mu', 'Pessimistic μ'), ('pessimistic_nu', 'Pessimistic ν')]
        for key, title in matrix_names:
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader(title)
            waspas_st_df(results['matrices'][key].round(8), height=330)
            st.markdown('</div>', unsafe_allow_html=True)
    with components_tab:
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.subheader('CIF weighted-sum, weighted-product, and integrated utilities')
        waspas_st_df(ranking.round(8), height=480)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.subheader('Optimistic score matrix')
        waspas_st_df(results['matrices']['optimistic_score_matrix'].round(8), height=350)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.subheader('Pessimistic score matrix')
        waspas_st_df(results['matrices']['pessimistic_score_matrix'].round(8), height=350)
        st.markdown('</div>', unsafe_allow_html=True)
    with visual_tab:
        waspas_show_bar(ranking, x='Final_CIF_WASPAS_Score', y='Alternative', title='Final CIF-WASPAS Alternative Ranking', text_col='Final_CIF_WASPAS_Score')
        waspas_show_score_comparison(ranking)
        waspas_show_heatmap(results['matrices']['optimistic_score_matrix'].round(6), 'Optimistic CIF Score Matrix')
        waspas_show_heatmap(results['matrices']['pessimistic_score_matrix'].round(6), 'Pessimistic CIF Score Matrix')
    with export_tab:
        st.markdown('<div id="download-results" class="table-card">', unsafe_allow_html=True)
        st.subheader('Export complete CIF-WASPAS report')
        st.download_button('Download CIF-WASPAS results Excel', data=waspas_export_waspas_results(results), file_name='cif_waspas_results.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        st.caption(f'λ = {lambda_value:.2f} | optimistic weight α = {optimism_weight:.2f} | score function = document Eq. (11)')
        st.markdown('</div>', unsafe_allow_html=True)

def waspas_main() -> None:
    st.set_page_config(page_title=waspas_APP_TITLE, page_icon='C', layout='wide', initial_sidebar_state='expanded')
    waspas_apply_custom_style()
    waspas_hamburger_menu()
    waspas_hero_section()
    st.markdown('<div class="three-d-divider"></div>', unsafe_allow_html=True)
    waspas_header_panels()
    waspas_intro_card()
    waspas_sidebar_content()
    waspas_waspas_app()
    st.markdown('\n        <div class="footer-note">\n            Executive CIF-WASPAS Interface - Circular intuitionistic fuzzy ranking with an emerald, forest, and gold scientific palette.\n        </div>\n        ', unsafe_allow_html=True)

def waspas_is_running_inside_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False



# ============================== COMBINED THREE-TAB SHELL ==============================

SUITE_APP_TITLE = "CIF-DEMATEL / CIF-SWARA / CIF-WASPAS | Executive Suite"
SUITE_PORT = 8803
SUITE_SERVER_ADDRESS = "0.0.0.0"


def suite_df(df, height=None):
    """Render dataframes across old and new Streamlit versions."""
    kwargs = {"width": "stretch"}
    if isinstance(height, int) and height > 0:
        kwargs["height"] = height
    try:
        st.dataframe(df, **kwargs)
    except TypeError:
        fallback = {"use_container_width": True}
        if isinstance(height, int) and height > 0:
            fallback["height"] = height
        st.dataframe(df, **fallback)


def suite_hamburger_menu():
    st.markdown(
        """
        <details class="hamburger-shell">
            <summary>
                <span class="hamburger-icon"><span></span><span></span><span></span></span>
                <span class="hamburger-title">CIF Decision Suite</span>
                <span class="hamburger-pill">DEMATEL · SWARA · WASPAS</span>
            </summary>
            <div class="hamburger-links">
                <a href="#suite-overview">Suite Overview</a>
                <a href="#dematel-workflow">CIF-DEMATEL</a>
                <a href="#swara-workflow">CIF-SWARA</a>
                <a href="#cif-waspas-workflow">CIF-WASPAS</a>
            </div>
        </details>
        """,
        unsafe_allow_html=True,
    )


def suite_hero():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-topline">Circular Intuitionistic Fuzzy Decision Analytics</div>
            <div class="hero-title">CIF Decision Analytics Suite</div>
            <p class="hero-subtitle">
                An integrated platform for three independent circular intuitionistic fuzzy techniques:
                CIF-DEMATEL maps causal relationships and cause/effect groups, CIF-SWARA derives criterion weights,
                and CIF-WASPAS ranks alternatives through weighted-sum and weighted-product analysis.
                Upload each method's workbook in its dedicated tab and run the calculations independently.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def suite_header_cards():
    st.markdown(
        """
        <div id="suite-overview" class="info-grid">
            <div class="mini-card developer-card">
                <h4>Developer & Concept Designer</h4>
                <p><strong>Dr. Saeed Alinejad - Shiraz University, Iran</strong></p>
                <p>Integrated circular intuitionistic fuzzy decision analytics.</p>
            </div>
            <div class="mini-card">
                <h4>CIF-DEMATEL</h4>
                <p>Models direct causal influences, total relations, prominence, relation, and cause/effect groups.</p>
            </div>
            <div class="mini-card">
                <h4>CIF-SWARA</h4>
                <p>Aggregates expert criterion judgments and calculates normalized criterion weights.</p>
            </div>
            <div class="mini-card">
                <h4>CIF-WASPAS</h4>
                <p>Ranks alternatives through optimistic and pessimistic circular decision matrices and integrated utilities.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def suite_upload_zone(title: str, description: str, badge: str):
    st.markdown(
        f"""
        <div class="upload-zone-card">
            <div class="upload-zone-badge">{badge}</div>
            <div class="upload-zone-title">{title}</div>
            <div class="upload-zone-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def suite_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-block developer-card">
                <h4>Integrated Application</h4>
                <p><strong>CIF-DEMATEL · CIF-SWARA · CIF-WASPAS</strong></p>
                <p>Each tab has a separate uploader, parameters, results dashboard, and Excel export.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sidebar-block"><h4>Input Templates</h4><p>Download the workbook that belongs to the method you want to calculate.</p></div>', unsafe_allow_html=True)
        st.download_button(
            "Download DEMATEL Template",
            data=dematel_create_template_excel(),
            file_name="cif_dematel_input_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="suite_dematel_template",
        )
        st.download_button(
            "Download SWARA Template",
            data=swara_create_template_excel(),
            file_name="cif_swara_input_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="suite_swara_template",
        )
        st.download_button(
            "Download WASPAS Template",
            data=waspas_create_waspas_template(),
            file_name="cif_waspas_input_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="suite_waspas_template",
        )
        st.markdown(
            """
            <div class="sidebar-block">
                <h4>Independent Workbooks</h4>
                <ul>
                    <li>DEMATEL: direct-influence matrices</li>
                    <li>SWARA: criterion-evaluation vectors</li>
                    <li>WASPAS: alternative matrices and criterion weights</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_dematel_tab():
    st.markdown(
        '<div id="dematel-workflow" class="glass-panel"><span class="section-label">CIF-DEMATEL Causal Analysis</span><p class="caption-note">Upload a DEMATEL workbook only in this tab. The module aggregates expert direct-influence matrices and calculates the total-relation system and cause/effect classification.</p></div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns([1, 2])
    with left:
        st.markdown('<div class="table-card"><span class="section-label">Parameters</span><p class="caption-note">Adjust the CIF score attitude, DEMATEL normalization, and network threshold.</p></div>', unsafe_allow_html=True)
        lambda_value = st.slider("DEMATEL lambda attitude", 0.0, 1.0, 0.5, 0.05, key="suite_dematel_lambda")
        normalization_mode = st.selectbox(
            "DEMATEL normalization mode",
            ["Max row and column sum", "Max row sum only"],
            index=0,
            key="suite_dematel_normalization",
            help="The first option is conservative and stable; the second reproduces common row-sum normalization.",
        )
        threshold_factor = st.slider("DEMATEL network threshold multiplier", 0.50, 2.00, 1.00, 0.05, key="suite_dematel_threshold")
        st.download_button(
            "Download DEMATEL input template",
            data=dematel_create_template_excel(),
            file_name="cif_dematel_input_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dematel_tab_template",
        )
    with right:
        suite_upload_zone(
            "Upload Your CIF-DEMATEL Excel Workbook",
            "Load expert direct-influence matrices. The module calculates aggregated CIF matrices, crisp and normalized direct relations, total relations, prominence, relation, cause/effect groups, and network edges.",
            "DEMATEL Upload Zone",
        )
        uploaded_file = st.file_uploader("Upload CIF-DEMATEL Excel workbook", type=["xlsx", "xls"], key="suite_dematel_upload")

    influence_scale_df = dematel_create_influence_scale_dataframe()
    expert_weight_scale_df = dematel_create_expert_weight_scale_dataframe()
    with st.expander("View active DEMATEL and expert-weight scales"):
        a, b = st.tabs(["Influence Scale", "Expert Weight Scale"])
        with a:
            suite_df(influence_scale_df.round(6))
        with b:
            suite_df(expert_weight_scale_df.round(6))

    if uploaded_file is None:
        st.info("Fill the DEMATEL template and upload it in this tab.")
        return

    try:
        expert_sheets, expert_info, skipped_sheets = dematel_read_excel_file(uploaded_file)
        expert_names = list(expert_sheets.keys())
        expert_weights_df = dematel_calculate_expert_weights(expert_names, expert_info)
        criteria, term_matrices, arrays, aggregated, normalized_weights = dematel_aggregate_experts(
            expert_sheets,
            expert_weights_df["Expert_Weight"].to_numpy(dtype=float),
        )
        cif_score_matrix = dematel_calculate_score_matrix(aggregated, lambda_value=lambda_value)
        crisp_matrix = dematel_calculate_crisp_matrix(cif_score_matrix)
        result_df, matrices, edges_df, threshold, alpha = dematel_calculate_dematel(
            criteria,
            crisp_matrix,
            normalization_mode=normalization_mode,
            threshold_factor=threshold_factor,
        )

        display_criteria = dematel_display_criterion_labels(criteria)
        top_row = result_df.sort_values("Rank_by_Prominence").iloc[0]
        cause_count = int((result_df["Group"] == "Cause").sum())
        effect_count = int((result_df["Group"] == "Effect").sum())

        st.success("CIF-DEMATEL calculations completed successfully.")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Expert sheets", len(expert_sheets))
        c2.metric("Criteria", len(criteria))
        c3.metric("Top prominence", dematel_display_criterion_label(top_row["Criterion"]))
        c4.metric("Cause group", cause_count)
        c5.metric("Effect group", effect_count)

        overview_tab, matrix_tab, visual_tab, export_tab = st.tabs(["Overview", "Matrices", "Visual Maps", "Export"])
        with overview_tab:
            dematel_render_sheet_summary(expert_names, skipped_sheets)
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader("Expert weights")
            suite_df(expert_weights_df.round(6))
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader("Final CIF-DEMATEL results")
            display_result = result_df.copy()
            display_result["Criterion"] = display_result["Criterion"].map(dematel_display_criterion_label)
            suite_df(display_result.round(6))
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader("Network edges above threshold")
            display_edges = edges_df.copy()
            if not display_edges.empty:
                display_edges["Source"] = display_edges["Source"].map(dematel_display_criterion_label)
                display_edges["Target"] = display_edges["Target"].map(dematel_display_criterion_label)
            suite_df(display_edges.round(6))
            st.markdown('</div>', unsafe_allow_html=True)

        with matrix_tab:
            matrix_items = [
                ("Aggregated membership matrix (μ)", aggregated[:, :, 0]),
                ("Aggregated non-membership matrix (ν)", aggregated[:, :, 1]),
                ("Circular radius matrix (r)", aggregated[:, :, 2]),
                ("CIF score matrix", cif_score_matrix),
                ("Crisp direct-relation matrix", crisp_matrix),
                ("Normalized direct-relation matrix", matrices["normalized"]),
                ("Total relation matrix T", matrices["total_relation"]),
            ]
            for title, matrix in matrix_items:
                st.markdown('<div class="table-card">', unsafe_allow_html=True)
                st.subheader(title)
                suite_df(dematel_matrix_to_dataframe(matrix, display_criteria).round(6), height=390)
                st.markdown('</div>', unsafe_allow_html=True)

        with visual_tab:
            dematel_show_cause_effect_map(result_df)
            dematel_show_heatmap(dematel_matrix_to_dataframe(matrices["total_relation"], display_criteria), "Total Relation Matrix Heatmap")
            dematel_show_network(criteria, matrices["total_relation"], threshold)

        with export_tab:
            excel_output = dematel_create_excel_output(
                expert_sheets=expert_sheets,
                skipped_sheets=skipped_sheets,
                influence_scale_df=influence_scale_df,
                expert_weight_scale_df=expert_weight_scale_df,
                expert_weights_df=expert_weights_df,
                term_matrices=term_matrices,
                aggregated=aggregated,
                score_matrix=cif_score_matrix,
                crisp_matrix=crisp_matrix,
                matrices=matrices,
                result_df=result_df,
                edges_df=edges_df,
                criteria=criteria,
                lambda_value=lambda_value,
                normalization_mode=normalization_mode,
                threshold=threshold,
                alpha=alpha,
            )
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader("Export complete CIF-DEMATEL report")
            st.download_button(
                "Download CIF-DEMATEL results Excel",
                data=excel_output,
                file_name="cif_dematel_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="suite_dematel_export",
            )
            st.caption(f"Normalization alpha = {alpha:.6f} | network threshold = {threshold:.6f}")
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception as error:
        st.error(f"CIF-DEMATEL calculation failed: {error}")


def render_swara_tab():
    st.markdown(
        '<div id="swara-workflow" class="glass-panel"><span class="section-label">CIF-SWARA Criterion Weighting</span><p class="caption-note">Upload a SWARA workbook only in this tab. The module aggregates circular intuitionistic fuzzy criterion vectors and calculates final normalized criterion weights.</p></div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns([1, 2])
    with left:
        st.markdown('<div class="table-card"><span class="section-label">Parameters</span><p class="caption-note">Select the scale orientation and score function before calculating the weights.</p></div>', unsafe_allow_html=True)
        scale_mode = st.radio(
            "SWARA scale orientation",
            [
                "Importance-oriented scale: AH highest membership",
                "Literal Word-table order: AL highest membership",
            ],
            index=0,
            key="suite_swara_scale_mode",
            help="Use the first option for normal SWARA importance weighting.",
        )
        scale = swara_CIF_SWARA_SCALE_IMPORTANCE if scale_mode.startswith("Importance") else swara_CIF_SWARA_SCALE_LITERAL_DOC
        score_mode = st.selectbox(
            "SWARA score function",
            [
                "Document Eq. 22: mu - nu + 2r/3",
                "Lambda-adjusted sensitivity: mu - nu + (2lambda - 1)r",
            ],
            index=0,
            key="suite_swara_score_mode",
        )
        lambda_value = st.slider("SWARA lambda attitude", 0.0, 1.0, 0.5, 0.05, key="suite_swara_lambda")
        st.download_button(
            "Download SWARA input template",
            data=swara_create_template_excel(),
            file_name="cif_swara_input_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="swara_tab_template",
        )
    with right:
        suite_upload_zone(
            "Upload Your CIF-SWARA Excel Workbook",
            "Load expert criterion-evaluation vectors. The module calculates aggregated CIF vectors, circular radii, score values, comparative coefficients, relative weights, final normalized weights, and criterion ranks.",
            "SWARA Upload Zone",
        )
        uploaded_file = st.file_uploader("Upload CIF-SWARA Excel workbook", type=["xlsx", "xls"], key="suite_swara_upload")

    scale_df = swara_create_scale_dataframe(scale)
    with st.expander("View the active CIF-SWARA linguistic scale"):
        suite_df(scale_df.round(6))

    if uploaded_file is None:
        st.info("Fill the SWARA template and upload it in this tab.")
        return

    try:
        expert_sheets, expert_info, skipped_sheets = swara_read_excel_file(uploaded_file, scale)
        expert_names = list(expert_sheets.keys())
        expert_weights_df = swara_calculate_expert_weights(expert_names, expert_info, scale)
        criteria, terms_df, vectors_array, aggregated, normalized_weights = swara_aggregate_experts(
            expert_sheets,
            expert_weights_df["Expert_Weight"].to_numpy(dtype=float),
            scale,
        )
        result_df = swara_calculate_cif_swara(criteria, aggregated, score_mode, lambda_value)
        display_criteria = swara_display_criterion_labels(criteria)

        st.success("CIF-SWARA calculations completed successfully.")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Expert sheets", len(expert_sheets))
        c2.metric("Criteria", len(criteria))
        c3.metric("Top criterion", swara_display_criterion_label(result_df.iloc[0]["Criterion"]))
        c4.metric("Top weight", f"{result_df.iloc[0]['Weight']:.6f}")

        overview_tab, vector_tab, ranking_tab, export_tab = st.tabs(["Overview", "CIF Vectors", "Weights", "Export"])
        with overview_tab:
            swara_render_sheet_summary(expert_names, skipped_sheets)
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader("Expert weights")
            suite_df(expert_weights_df.round(6))
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader("Expert linguistic evaluations")
            terms_display_df = terms_df.copy()
            if "Criterion" in terms_display_df.columns:
                terms_display_df["Criterion"] = terms_display_df["Criterion"].map(swara_display_criterion_label)
            suite_df(terms_display_df)
            st.markdown('</div>', unsafe_allow_html=True)

        with vector_tab:
            aggregated_df = pd.DataFrame(
                {
                    "Criterion": display_criteria,
                    "mu": aggregated[:, 0],
                    "nu": aggregated[:, 1],
                    "pi": [swara_hesitation_degree(mu, nu) for mu, nu in aggregated[:, :2]],
                    "r": aggregated[:, 2],
                }
            )
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader("Aggregated circular intuitionistic fuzzy vector")
            suite_df(aggregated_df.round(6))
            st.markdown('</div>', unsafe_allow_html=True)

            raw_vectors = []
            for expert_index, expert_name in enumerate(expert_names):
                for criterion_index, criterion in enumerate(criteria):
                    mu = vectors_array[expert_index, criterion_index, 0]
                    nu = vectors_array[expert_index, criterion_index, 1]
                    raw_vectors.append(
                        {
                            "Expert": expert_name,
                            "Criterion": swara_display_criterion_label(criterion),
                            "mu": mu,
                            "nu": nu,
                            "pi": swara_hesitation_degree(mu, nu),
                        }
                    )
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader("Expert CIF pairs")
            suite_df(pd.DataFrame(raw_vectors).round(6), height=420)
            st.markdown('</div>', unsafe_allow_html=True)

        with ranking_tab:
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader("Final CIF-SWARA weights")
            result_display_df = result_df.copy()
            result_display_df["Criterion"] = result_display_df["Criterion"].map(swara_display_criterion_label)
            suite_df(result_display_df.round(6))
            st.markdown('</div>', unsafe_allow_html=True)

            chart_df = result_display_df[["Criterion", "Weight"]].copy().set_index("Criterion")
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader("Weight profile")
            st.bar_chart(chart_df)
            st.markdown('</div>', unsafe_allow_html=True)

        with export_tab:
            excel_output = swara_create_excel_output(
                expert_sheets=expert_sheets,
                skipped_sheets=skipped_sheets,
                scale_df=scale_df,
                expert_weights_df=expert_weights_df,
                terms_df=terms_df,
                aggregated=aggregated,
                result_df=result_df,
                criteria=criteria,
                score_mode=score_mode,
                lambda_value=lambda_value,
                scale_mode=scale_mode,
            )
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.subheader("Export complete CIF-SWARA report")
            st.download_button(
                "Download CIF-SWARA results Excel",
                data=excel_output,
                file_name="cif_swara_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="suite_swara_export",
            )
            st.caption(f"Score mode = {score_mode} | lambda = {lambda_value:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception as error:
        st.error(f"CIF-SWARA calculation failed: {error}")


def render_waspas_tab():
    # The original WASPAS calculation and result dashboard are preserved.
    waspas_waspas_app()


def combined_main():
    st.set_page_config(
        page_title=SUITE_APP_TITLE,
        page_icon="C",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    waspas_apply_custom_style()
    suite_hamburger_menu()
    suite_hero()
    st.markdown('<div class="three-d-divider"></div>', unsafe_allow_html=True)
    suite_header_cards()
    suite_sidebar()

    dematel_tab, swara_tab, waspas_tab = st.tabs(["CIF-DEMATEL", "CIF-SWARA", "CIF-WASPAS"])
    with dematel_tab:
        render_dematel_tab()
    with swara_tab:
        render_swara_tab()
    with waspas_tab:
        render_waspas_tab()

    st.markdown(
        """
        <div class="footer-note">
            CIF Decision Analytics Suite — three independent circular intuitionistic fuzzy methods in one emerald, forest, and gold interface.
        </div>
        """,
        unsafe_allow_html=True,
    )


def suite_is_running_inside_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


if __name__ == "__main__" and not suite_is_running_inside_streamlit() and os.environ.get("RUNNING_CIF_SUITE_STREAMLIT") != "1":
    import streamlit.web.cli as stcli
    os.environ["RUNNING_CIF_SUITE_STREAMLIT"] = "1"
    sys.argv = [
        "streamlit", "run", sys.argv[0],
        "--server.port", str(SUITE_PORT),
        "--server.address", SUITE_SERVER_ADDRESS,
    ]
    sys.exit(stcli.main())

if suite_is_running_inside_streamlit():
    combined_main()
