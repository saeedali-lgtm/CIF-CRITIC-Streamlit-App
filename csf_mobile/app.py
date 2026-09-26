"""Original author interface with validated workbook uploads and reproducible exports."""
from typing import Optional
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import core
import service
from core import create_swara_template, create_cocoso_template
PLOTLY_AVAILABLE = True
APP_TITLE = "CSF-SWARA / CSF-CoCoSo | Executive Edition"

def calculate_uploaded(uploaded,module,p,radius_policy,lam=.5):
    with st.spinner("Validating your workbook and calculating results..."):
        results,metadata=service.calculate(uploaded.getvalue(),module,p,radius_policy,lam)
    metadata['input_source']='uploaded_workbook'
    results['_run_metadata']=metadata
    bad=metadata.get('diagnostics',{}).get('scenario_triples_outside_unit_sphere',0)
    if bad:
        st.warning(f"{bad} scenario triples fall outside the unit sphere under the original equations. Review METHOD_NOTES.md before interpreting these rankings.")
    return results

def calculate_csf_swara(uploaded,p=.5,radius_policy='max'):
    return calculate_uploaded(uploaded,'swara',p,radius_policy)

def calculate_csf_cocoso(uploaded,p=.5,lambda_value=.5,radius_policy='max'):
    return calculate_uploaded(uploaded,'cocoso',p,radius_policy,lambda_value)

def export_swara_results(results):
    return service.export(results,results['_run_metadata'],'swara')

def export_cocoso_results(results):
    return service.export(results,results['_run_metadata'],'cocoso')

def download_record(results,module):
    st.download_button("Download reproducibility record",json.dumps(results['_run_metadata'],indent=2),file_name=module+'_run.json',mime='application/json',key=module+'_record')


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
           VISUAL POLISH 2026-06-19
           A calmer executive palette with better contrast and less glare.
        ================================================================ */
        :root {
            --cif-ink-final: #0F2437;
            --cif-navy-final: #16324A;
            --cif-teal-final: #1F7A7A;
            --cif-teal-dark-final: #155E63;
            --cif-mint-final: #DFF5EC;
            --cif-gold-final: #D8A23A;
            --cif-gold-soft-final: #F5DFAC;
            --cif-page-final: #F6F8F5;
            --cif-card-final: #FFFFFF;
            --cif-muted-final: #536579;
        }

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background:
                radial-gradient(circle at 12% 8%, rgba(31, 122, 122, 0.13), transparent 24%),
                radial-gradient(circle at 88% 12%, rgba(216, 162, 58, 0.13), transparent 24%),
                linear-gradient(145deg, #F7FAF8 0%, #F4F7F1 44%, #FFFFFF 100%) !important;
            color: var(--cif-ink-final) !important;
        }

        .hero-card {
            border-radius: 24px !important;
            background:
                radial-gradient(circle at 10% 14%, rgba(255,255,255,0.20), transparent 30%),
                radial-gradient(circle at 90% 18%, rgba(245,223,172,0.20), transparent 32%),
                linear-gradient(135deg, #0F2437 0%, #16324A 52%, #155E63 100%) !important;
            border: 1px solid rgba(245, 223, 172, 0.62) !important;
            box-shadow:
                0 24px 54px rgba(15, 36, 55, 0.24),
                0 4px 0 rgba(255,255,255,0.10) inset !important;
        }

        .hero-topline,
        .upload-zone-badge,
        .hamburger-pill {
            background: rgba(245, 223, 172, 0.18) !important;
            color: #FFF7DF !important;
            border-color: rgba(245, 223, 172, 0.42) !important;
        }

        .mini-card,
        .glass-panel,
        .table-card,
        .brand-card,
        .sidebar-block,
        div[data-testid="metric-container"],
        div[data-testid="stDataFrame"],
        .sheet-clean-panel {
            background: linear-gradient(145deg, rgba(255,255,255,0.98) 0%, rgba(247,250,248,0.96) 100%) !important;
            border: 1px solid rgba(31, 122, 122, 0.16) !important;
            border-radius: 18px !important;
            box-shadow:
                0 14px 34px rgba(15, 36, 55, 0.08),
                0 2px 0 rgba(255,255,255,0.95) inset !important;
        }

        .mini-card:hover,
        .glass-panel:hover,
        .table-card:hover,
        .brand-card:hover,
        .sidebar-block:hover,
        div[data-testid="metric-container"]:hover {
            transform: translateY(-2px) !important;
            box-shadow:
                0 20px 44px rgba(15, 36, 55, 0.12),
                0 2px 0 rgba(255,255,255,0.95) inset !important;
        }

        .mini-card h4,
        .sidebar-block h4,
        .brand-card .name,
        .section-label,
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricValue"] {
            color: var(--cif-navy-final) !important;
        }

        .caption-note,
        .muted,
        .mini-card p,
        .mini-card li,
        .sidebar-block p,
        .sidebar-block li,
        .glass-panel p,
        .table-card p {
            color: var(--cif-muted-final) !important;
        }

        .section-label {
            background: rgba(31, 122, 122, 0.10) !important;
            border-color: rgba(31, 122, 122, 0.20) !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            background: rgba(31, 122, 122, 0.08) !important;
            border-color: rgba(31, 122, 122, 0.14) !important;
            border-radius: 14px !important;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 10px !important;
            color: var(--cif-navy-final) !important;
            border-color: rgba(31, 122, 122, 0.12) !important;
        }

        .stTabs [aria-selected="true"],
        .stButton > button,
        .stDownloadButton > button,
        div[data-testid="stDownloadButton"] button {
            background: linear-gradient(135deg, var(--cif-teal-dark-final) 0%, var(--cif-teal-final) 58%, #2C8B72 100%) !important;
            border: 1px solid rgba(255,255,255,0.76) !important;
            color: #FFFFFF !important;
            border-radius: 14px !important;
            box-shadow:
                0 14px 28px rgba(31, 122, 122, 0.24),
                0 2px 0 rgba(255,255,255,0.22) inset !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        div[data-testid="stDownloadButton"] button:hover {
            background: linear-gradient(135deg, #174C55 0%, #1F7A7A 54%, #D8A23A 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 18px 36px rgba(31, 122, 122, 0.30) !important;
        }

        div[data-testid="stFileUploader"],
        .stFileUploader {
            background: #FFFFFF !important;
            border: 2px dashed rgba(31, 122, 122, 0.42) !important;
            border-radius: 18px !important;
            box-shadow: 0 12px 30px rgba(15, 36, 55, 0.08) !important;
        }

        div[data-testid="stFileUploader"] section,
        section[data-testid="stFileUploaderDropzone"],
        div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
            background: linear-gradient(145deg, #F7FAF8 0%, #EEF7F3 100%) !important;
            border: 1px solid rgba(31, 122, 122, 0.18) !important;
        }

        div[data-testid="stFileUploader"] section *,
        section[data-testid="stFileUploaderDropzone"] *,
        div[data-testid="stFileUploader"] small,
        div[data-testid="stFileUploader"] span,
        div[data-testid="stFileUploader"] p {
            color: var(--cif-ink-final) !important;
            -webkit-text-fill-color: var(--cif-ink-final) !important;
            text-shadow: none !important;
        }

        .upload-zone-card,
        .upload-zone-card.upload-zone-gold-final,
        div.upload-zone-card.upload-zone-gold-final {
            background:
                radial-gradient(circle at 12% 12%, rgba(255,255,255,0.24), transparent 30%),
                linear-gradient(135deg, #16324A 0%, #155E63 55%, #1F7A7A 100%) !important;
            border: 1px solid rgba(245, 223, 172, 0.58) !important;
            box-shadow: 0 22px 48px rgba(15, 36, 55, 0.20) !important;
        }

        header[data-testid="stHeader"],
        .stAppHeader,
        .st-emotion-cache-18ni7ap,
        .st-emotion-cache-h4xjwg,
        .st-emotion-cache-zq5wmm {
            background: rgba(247, 250, 248, 0.92) !important;
            border-bottom: 1px solid rgba(31, 122, 122, 0.12) !important;
            box-shadow: 0 8px 26px rgba(15, 36, 55, 0.06) !important;
        }

        [data-testid="stDecoration"] {
            background: linear-gradient(90deg, #16324A 0%, #1F7A7A 48%, #D8A23A 100%) !important;
            height: 3px !important;
        }

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, #FFFFFF 0%, #F7FAF8 54%, #F1F6F3 100%) !important;
            border-right: 1px solid rgba(31, 122, 122, 0.14) !important;
        }

        .three-d-divider {
            height: 6px !important;
            background: linear-gradient(90deg, rgba(31,122,122,0.06), #1F7A7A, #D8A23A, rgba(31,122,122,0.06)) !important;
            box-shadow: none !important;
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

        /* Final palette lock: keeps the polished teal/navy look after older overrides. */
        .stButton > button,
        .stDownloadButton > button,
        div[data-testid="stDownloadButton"] button {
            background: linear-gradient(135deg, #155E63 0%, #1F7A7A 58%, #2C8B72 100%) !important;
            background-color: #1F7A7A !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            border: 1px solid rgba(255,255,255,0.78) !important;
            border-radius: 14px !important;
            box-shadow:
                0 14px 28px rgba(31, 122, 122, 0.24),
                0 2px 0 rgba(255,255,255,0.24) inset !important;
            text-shadow: none !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        div[data-testid="stDownloadButton"] button:hover {
            background: linear-gradient(135deg, #16324A 0%, #1F7A7A 58%, #D8A23A 100%) !important;
            box-shadow: 0 18px 36px rgba(31, 122, 122, 0.30) !important;
        }

</style>
        """,
        unsafe_allow_html=True,
    )

def st_df(df: pd.DataFrame, height: Optional[int] = None) -> None:
    """Render dataframes safely across Streamlit versions.

    New Streamlit versions reject height=None. This helper only passes a
    height argument when it is a valid positive integer or an accepted layout
    keyword such as "stretch" or "content".
    """
    kwargs = {"width": "stretch"}
    if isinstance(height, int) and height > 0:
        kwargs["height"] = height
    elif isinstance(height, str) and height in {"stretch", "content"}:
        kwargs["height"] = height
    try:
        st.dataframe(df, **kwargs)
    except TypeError:
        fallback = {"use_container_width": True}
        if isinstance(height, int) and height > 0:
            fallback["height"] = height
        st.dataframe(df, **fallback)

def st_plot(fig) -> None:
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)

def hero_section() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-topline">Executive Decision Analytics</div>
            <div class="hero-title">CSF-SWARA / CSF-CoCoSo Calculator</div>
            <p class="hero-subtitle" style="color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; opacity:1 !important; font-weight:800 !important; line-height:1.75 !important; text-shadow:0 2px 12px rgba(0,0,0,0.70) !important;">
                A polished teal, navy, and warm-gold Streamlit interface for Circular Spherical Fuzzy SWARA criterion weighting
                and Circular Spherical Fuzzy CoCoSo alternative ranking. Upload independent Excel workbooks in each tab,
                calculate results, visualize outputs, and download complete Excel reports.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def header_panels() -> None:
    st.markdown(
        """
        <div class="info-grid">
            <div class="mini-card developer-card">
                <h4>Developer & Concept Designer</h4>
                <p><strong>Dr. Saeed Alinejad - Shiraz University, Iran</strong></p>
                <p>Advanced decision-making tool developer.</p>
            </div>
            <div class="mini-card">
                <h4>CSF-SWARA Logic</h4>
                <p>Expert judgments are modeled with circular spherical fuzzy numbers to calculate normalized criterion weights under uncertainty.</p>
            </div>
            <div class="mini-card">
                <h4>CSF-CoCoSo Logic</h4>
                <p>Decision matrices and user-provided criterion weights are processed independently to rank alternatives using CoCoSo-based compromise scores.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def show_bar(df: pd.DataFrame, x: str, y: str, title: str, text_col: Optional[str] = None) -> None:
    if PLOTLY_AVAILABLE:
        plot_df = df.copy().sort_values(x, ascending=True)
        fig = px.bar(plot_df, x=x, y=y, orientation="h", text=text_col or x, title=title, color=x, color_continuous_scale=["#F5DFAC", "#8FCDBD", "#1F7A7A", "#16324A"])
        fig.update_traces(texttemplate="%{text:.4f}", textposition="outside")
        fig.update_layout(
            height=max(420, 65 * len(plot_df)),
            margin=dict(l=30, r=30, t=60, b=30),
            yaxis_title="",
            xaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.88)",
            font=dict(color="#0F2437"),
            title_font=dict(color="#16324A", size=20),
        )
        st_plot(fig)
    else:
        st_df(df)

def show_heatmap(df: pd.DataFrame, title: str) -> None:
    if PLOTLY_AVAILABLE:
        fig = px.imshow(df, text_auto=".3f", aspect="auto", title=title, color_continuous_scale=["#FFFFFF", "#F5DFAC", "#8FCDBD", "#1F7A7A", "#16324A"])
        fig.update_layout(
            height=500,
            margin=dict(l=30, r=30, t=60, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.88)",
            font=dict(color="#0F2437"),
            title_font=dict(color="#16324A", size=20),
        )
        st_plot(fig)
    else:
        st_df(df.round(6))

def swara_tab() -> None:
    st.markdown('<div class="glass-panel"><span class="section-label">CSF-SWARA Weighting</span><p class="caption-note">Upload a SWARA workbook to calculate criterion weights from expert linguistic judgments. This tab is independent from CoCoSo.</p></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("1. Upload SWARA Excel workbook", type=["xlsx"], key="swara_upload")
    st.download_button("Download SWARA input template",data=create_swara_template(),file_name="csf_swara_input_template.xlsx",key="swara_template")
    with st.expander("Calculation settings", expanded=False):
        p=st.slider("Decision-maker attitude p",0.0,1.0,0.5,0.05,key="swara_p")
        radius_policy=st.selectbox("Radius policy",["max","min"],key="swara_radius")

    if not uploaded:
        st.info("Upload your SWARA workbook above to calculate results automatically. The downloadable template contains synthetic examples; replace them with your data.")
        return
    try:
        results = calculate_csf_swara(uploaded, p=p, radius_policy=radius_policy)
    except Exception as exc:
        st.error(f"SWARA calculation failed: {exc}")
        return

    weights = results["weights"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Criteria", len(weights))
    c2.metric("Top criterion", str(weights.sort_values("Rank").iloc[0]["Criterion"]))
    c3.metric("Top weight", f"{weights['Final_SWARA_Weight'].max():.4f}")

    st.subheader("2. Final CSF-SWARA weights")
    st_df(weights.round(6))
    show_bar(weights, x="Final_SWARA_Weight", y="Criterion", title="Final CSF-SWARA Criterion Weights", text_col="Final_SWARA_Weight")

    with st.expander("Aggregated CSF values and expert weights"):
        st.markdown("**Aggregated criterion evaluations**")
        st_df(results["aggregated"].round(6))
        st.markdown("**Expert weights**")
        st_df(results["expert_weights"].round(6))
        st.markdown("**Parsed input terms**")
        st_df(results["terms"].round(6), height=360)

    st.subheader("3. Download results")
    download_record(results,"swara")
    st.download_button("Download SWARA results Excel", data=export_swara_results(results), file_name="csf_swara_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def cocoso_tab() -> None:
    st.markdown('<div class="glass-panel"><span class="section-label">CSF-CoCoSo Ranking</span><p class="caption-note">Upload a CoCoSo workbook containing decision matrix sheets and a Criteria_Weights sheet. The weights may come from SWARA, CRITIC, AHP, or any other method.</p></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("1. Upload CoCoSo Excel workbook", type=["xlsx"], key="cocoso_upload")
    st.download_button("Download CoCoSo input template",data=create_cocoso_template(),file_name="csf_cocoso_input_template.xlsx",key="cocoso_template")
    with st.expander("Calculation settings", expanded=False):
        p=st.slider("Decision-maker attitude p",0.0,1.0,0.5,0.05,key="cocoso_p")
        radius_policy=st.selectbox("Radius policy",["max","min"],key="cocoso_radius")
        lam=st.slider("CoCoSo lambda",0.0,1.0,0.5,0.05,key="cocoso_lambda")

    if not uploaded:
        st.info("Upload your CoCoSo workbook above to calculate results automatically. The downloadable template contains synthetic examples; replace them with your data.")
        return
    try:
        results = calculate_csf_cocoso(uploaded, p=p, lambda_value=lam, radius_policy=radius_policy)
    except Exception as exc:
        st.error(f"CoCoSo calculation failed: {exc}")
        return

    ranking = results["results"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Alternatives", len(ranking))
    c2.metric("Best alternative", str(ranking.sort_values("Rank").iloc[0]["Alternative"]))
    c3.metric("Best score", f"{ranking['Final_Crisp_Score'].max():.4f}")

    st.subheader("2. Final CSF-CoCoSo ranking")
    st_df(ranking.round(6))
    show_bar(ranking, x="Final_Crisp_Score", y="Alternative", title="Final CSF-CoCoSo Alternative Ranking", text_col="Final_Crisp_Score")

    with st.expander("Criterion weights, types, and matrices"):
        st.markdown("**Criterion weights used in CoCoSo**")
        st_df(results["criteria_weights"].round(6))
        st.markdown("**Criterion types**")
        st_df(results["criteria_types"])
        st.markdown("**Expert weights**")
        st_df(results["expert_weights"].round(6))
        st.markdown("**Aggregated score matrix**")
        show_heatmap(results["matrices"]["optimistic_score_matrix"].round(6), "Optimistic score matrix")
        show_heatmap(results["matrices"]["pessimistic_score_matrix"].round(6), "Pessimistic score matrix")

    st.subheader("3. Download results")
    download_record(results,"cocoso")
    st.download_button("Download CoCoSo results Excel", data=export_cocoso_results(results), file_name="csf_cocoso_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def mobile_style():
    st.markdown("""<style>
    .block-container {max-width:1080px !important;padding-top:1.5rem !important;}
    .hero-card {padding:24px !important;margin-bottom:18px !important;}
    .hero-title {font-size:36px !important;line-height:1.15 !important;}
    .hero-subtitle {margin-bottom:0 !important;}
    button {min-height:44px !important;}
    div[data-testid="stFileUploader"] {border:2px solid #2FA66A !important;border-radius:16px !important;padding:12px !important;background:#f0faf5 !important;}
    @media(max-width:760px){
      .block-container{padding:1rem .8rem 2rem !important;}
      .hero-card{padding:20px 18px !important;border-radius:18px !important;}
      .hero-title{font-size:28px !important;}
      .hero-topline{font-size:10px !important;letter-spacing:1px !important;}
      .hero-subtitle{font-size:13px !important;line-height:1.6 !important;}
      .glass-panel{padding:12px !important;margin-bottom:12px !important;}
      .caption-note{font-size:13px !important;line-height:1.5 !important;}
      .info-grid{display:block !important;}
      .mini-card{margin-bottom:12px !important;min-height:0 !important;padding:16px !important;}
      h3{font-size:21px !important;}
      div[data-testid="stHorizontalBlock"]{flex-wrap:wrap !important;}
      div[data-testid="stColumn"]{min-width:100% !important;width:100% !important;flex:1 1 100% !important;}
      div[data-testid="stDownloadButton"] button{width:100% !important;}
      [data-baseweb="tab"]{min-height:46px !important;flex:1 !important;font-size:15px !important;}
    }
    </style>""",unsafe_allow_html=True)

def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="C", layout="wide")
    apply_custom_style()
    mobile_style()
    st.markdown('<div class="hero-card"><div class="hero-topline">CSF RESEARCH · MOBILE WEB</div><div class="hero-title">SWARA &amp; CoCoSo</div><p class="hero-subtitle">Upload Excel · Calculate · Download results</p></div>',unsafe_allow_html=True)
    tab_swara, tab_cocoso = st.tabs(["CSF-SWARA", "CSF-CoCoSo"])
    with tab_swara:
        swara_tab()
    with tab_cocoso:
        cocoso_tab()
    with st.expander("About this research tool"):
        header_panels()
    with st.expander("Method version and data processing"):
        st.write("This release preserves the equations of the supplied Python implementation. It differs from the previously revised maturity workbook; see METHOD_NOTES.md for the documented choices and limitations.")
        st.write("Local execution processes uploaded workbooks on this computer. A hosted deployment processes them on its server. The app does not deliberately save uploaded workbooks.")

if __name__ == "__main__":
    main()
