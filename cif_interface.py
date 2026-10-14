"""Presentation layer for CIF. No calculation code lives in this module."""
from pathlib import Path
import html
import json
import streamlit as st

ROOT = Path(__file__).resolve().parent

def content():
    return json.loads((ROOT / 'cif_content.json').read_text(encoding='utf-8'))

def apply_theme():
    st.markdown('<style>' + (ROOT / 'cif_theme.css').read_text(encoding='utf-8') + '</style>', unsafe_allow_html=True)

def hero():
    c = {k: html.escape(str(v)) for k, v in content().items() if isinstance(v, str)}
    st.markdown(f'''<section class="cif-masthead" id="suite-overview">
    <div class="cif-identity"><span class="cif-seal">CIF<span>RESEARCH</span></span>
    <div><div class="cif-eyebrow">CIRCULAR INTUITIONISTIC FUZZY SETS</div>
    <div class="cif-author">{c['developer']}</div><div class="cif-affiliation">{c['affiliation']}</div></div>
    <span class="cif-edition">DECISION ANALYTICS</span></div>
    <div class="cif-hero-layout"><div><div class="cif-kicker">EXPERT JUDGMENT · STRUCTURED DECISIONS</div>
    <h1>{c['title']}</h1><p class="cif-lead">{c['description']}</p>
    <div class="cif-chips"><span>CIF–DEMATEL</span><span>CIF–SWARA</span><span>CIF–WASPAS</span></div></div>
    <div class="cif-orbit" aria-hidden="true"><div class="cif-orbit-ring one"></div><div class="cif-orbit-ring two"></div>
    <div class="cif-orbit-core">CIF<small>μ · ν · r</small></div><span class="orbit-label causal">CAUSALITY</span>
    <span class="orbit-label weights">WEIGHTING</span><span class="orbit-label ranking">RANKING</span></div></div>
    <div class="cif-hero-bottom"><span>01 &nbsp; Choose a method</span><span>02 &nbsp; Upload your workbook</span><span>03 &nbsp; Review & export results</span></div>
    </section>''', unsafe_allow_html=True)

def cards():
    methods = content()['methods']
    chunks=[]
    for i, m in enumerate(methods, 1):
        e={k:html.escape(str(v)) for k,v in m.items()}
        chunks.append(f'<article class="cif-method"><div class="cif-method-top"><span class="cif-method-number">0{i}</span><span>{e["category"]}</span></div><h3>{e["name"]}</h3><p>{e["description"]}</p><div class="cif-method-output">{e["output"]}</div></article>')
    st.markdown('<div class="cif-method-grid">'+''.join(chunks)+'</div><div class="cif-workspace-heading"><div><span class="cif-eyebrow-dark">YOUR ANALYSIS WORKSPACE</span><h2>Select a method to begin</h2></div><span>Separate inputs · Independent calculations</span></div>', unsafe_allow_html=True)

def menu():
    # Navigation is provided by the native method tabs and sidebar.
    pass

def upload_zone(title, description, badge):
    st.markdown(f'<div class="cif-upload-heading"><span>{html.escape(badge)}</span><h3>{html.escape(title)}</h3><p>{html.escape(description)}</p></div>', unsafe_allow_html=True)
