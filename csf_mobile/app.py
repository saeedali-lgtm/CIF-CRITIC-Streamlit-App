"""Original author interface with validated workbook uploads and reproducible exports."""
from typing import Optional
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import core
import service
from ui_text import text, render_text, text_warning
from core import create_swara_template, create_cocoso_template
PLOTLY_AVAILABLE = True
APP_TITLE = text('page_title')

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
    st.download_button(text('download_record'),json.dumps(results['_run_metadata'],indent=2),file_name=module+'_run.json',mime='application/json',key=module+'_record')


def apply_custom_style():
    st.markdown("""<style>
    :root { --ink:#183F31; --muted:#53675F; --line:#DCE6E0; --green:#174F3C; --gold:#DDC389; }
    html { color-scheme:light; }
    .stApp { background:#F5F8F6; color:var(--ink); }
    .block-container { max-width:1080px; padding:4.5rem 2rem 3rem; }
    header[data-testid="stHeader"] { background:#F5F8F6; }
    .hero-card { margin:0 0 26px; border-radius:20px; overflow:hidden;
      border:1px solid #184739; box-shadow:0 8px 28px #173C3210; }
    .research-heading { padding:30px 34px 28px; background:linear-gradient(110deg,#102E2B,#1C5047); }
    .research-eyebrow { display:flex; align-items:center; gap:12px; color:var(--gold);
      font-size:12px; font-weight:650; letter-spacing:.16em; margin-bottom:19px; }
    .research-eyebrow svg { width:32px; height:32px; flex:none; }
    .hero-card h1 { color:#FFF !important; font-size:clamp(26px,4vw,40px); font-weight:600;
      letter-spacing:-.035em; line-height:1.15; margin:0 0 12px; padding:0; }
    .research-subtitle { color:#CEE1D7; font-size:15px; line-height:1.6; margin:0; }
    .research-methods { color:#F0E3C6; font-size:13px; font-weight:500; margin:17px 0 0; }
    .research-credit { display:flex; align-items:center; flex-wrap:wrap; gap:8px 28px;
      border-top:2px solid var(--gold); padding:17px 34px; background:#FCFCF8; }
    .research-credit-label { display:block; color:#627468; font-size:10px;
      letter-spacing:.12em; text-transform:uppercase; margin-bottom:3px; }
    .research-credit strong { color:var(--ink); font-size:15px; font-weight:650; }
    .research-affiliation { color:var(--muted); font-size:13px; margin-left:auto; }
    [role="tablist"] { display:flex; gap:5px; padding:5px; background:#E7EFE9;
      border-radius:13px; margin-bottom:20px; }
    [role="tab"] { display:flex; justify-content:center; flex:1; min-height:48px; padding:10px 16px;
      border-radius:9px; color:#385349 !important; font-weight:600; background:transparent; white-space:normal; }
    [role="tab"] p { font-size:15px; color:inherit !important; }
    [role="tab"][aria-selected="true"] { color:#FFF !important;
      background:var(--green) !important; box-shadow:0 2px 6px #143B3218; }
    .react-aria-SelectionIndicator, [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display:none !important; }
    .glass-panel { background:#FFF; border:1px solid var(--line); border-radius:14px;
      padding:20px 24px; margin-bottom:18px; }
    .section-label { display:block; color:var(--green); font-size:12px;
      font-weight:700; letter-spacing:.08em; text-transform:uppercase; margin-bottom:7px; }
    .caption-note { color:var(--muted); font-size:14px; line-height:1.65; margin:0; }
    [data-testid="stWidgetLabel"] p { color:var(--ink); font-weight:600; }
    [data-testid="stFileUploaderDropzone"] { background:#FFF; border:1px dashed #95B4A3;
      border-radius:14px; padding:22px; }
    [data-testid="stFileUploaderDropzone"] * { color:var(--ink); }
    [data-testid="stDownloadButton"] button, [data-testid="stButton"] button,
    [data-testid="stFileUploaderDropzone"] button { min-height:46px; border-radius:9px;
      border:1px solid #B9CDC0; background:#FFF; color:var(--green); font-weight:600; }
    [data-testid="stDownloadButton"] button:hover, [data-testid="stFileUploaderDropzone"] button:hover {
      border-color:var(--green); background:#EEF5F0; }
    [data-testid="stDownloadButton"] button[kind="primary"] { background:var(--green); color:#FFF; border-color:var(--green); }
    [data-testid="stExpander"] { border:1px solid var(--line); border-radius:12px; background:#FFF; }
    [data-testid="stExpander"] summary { min-height:48px; color:var(--ink) !important; }
    [data-testid="stExpander"] summary p { color:var(--ink) !important; }
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] { color:var(--ink); }
    [data-testid="stMetric"] { background:#FFF; border:1px solid var(--line); border-radius:12px; padding:18px; }
    [data-testid="stMetricValue"] { color:var(--green); font-weight:600; }
    [data-testid="stMetricLabel"] { color:var(--muted); }
    [data-testid="stDataFrame"], [data-testid="stPlotlyChart"] { border-radius:12px; overflow:hidden; }
    .stApp h2, .stApp h3 { color:var(--ink); letter-spacing:-.02em; }
    .stApp h3 { font-size:22px; }
    [data-testid="stAlert"] { border-radius:12px; }
    [data-baseweb="select"] > div, [data-baseweb="input"] { background:#FFF; color:var(--ink); }
    .info-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
    .mini-card { padding:18px; border:1px solid var(--line); border-radius:12px; background:#F8FAF8; }
    .mini-card h4 { color:var(--ink); margin:0 0 8px; font-size:16px; }
    .mini-card p { color:var(--muted); margin:0; font-size:14px; line-height:1.65; }
    button:focus-visible, a:focus-visible, [role="tab"]:focus-visible { outline:3px solid #A77C26 !important; outline-offset:3px; }
    @media(max-width:760px) {
      .block-container { padding:4.5rem 14px 2rem; }
      .hero-card { border-radius:16px; margin-bottom:20px; }
      .research-heading { padding:22px 21px; }
      .research-eyebrow { margin-bottom:15px; font-size:11px; }
      .research-subtitle { font-size:14px; }
      .research-credit { padding:14px 21px; gap:6px; }
      .research-affiliation { margin-left:0; width:100%; }
      .glass-panel { padding:18px; }
      [data-testid="stFileUploaderDropzone"] { padding:16px; }
      [data-testid="stDownloadButton"] button { width:100%; }
      .info-grid { grid-template-columns:1fr; }
      [data-testid="stMetric"] { padding:12px; }
    }
    @media(prefers-reduced-motion:reduce) { * { scroll-behavior:auto !important; transition:none !important; } }
    </style>""",unsafe_allow_html=True)



def apply_dream_style():
    st.markdown("""<style>
:root { --ink:#173e3b; --muted:#597565; --line:#dce3d8; --green:#075b57; --gold:#c7a34e; --cif-emerald:#0b625a; --cif-emerald-dark:#075b57; --cif-forest:#073d3b; --cif-lapis:#073d3b; --cif-ink:#173e3b; --cif-text:#173e3b; --cif-muted:#597565; --cif-gold:#c7a34e; }
.stApp {background:radial-gradient(ellipse at 90% 5%,#ede4cc80,transparent 45%),radial-gradient(ellipse at 15% 75%,#d7e9df70,transparent 50%),#f6f8f4 !important;}
.hero-card {border:1px solid #c7a34e70 !important;box-shadow:0 8px 30px #073d3b18 !important;border-radius:20px !important;background:linear-gradient(115deg,#083f3b,#0b625a) !important;}
.research-heading {background:radial-gradient(ellipse at 90% 20%,#287b6665,transparent 55%),linear-gradient(115deg,#083f3b,#0b625a) !important;}
.research-subtitle,.hero-subtitle {color:#cee1d7 !important;}
.hero-title,.hero-topline {color:#fff8e8 !important;}.research-eyebrow,.research-methods{color:#ead39b !important;}
.research-credit {border-top:2px solid #c7a34e;background:#fffdf6 !important;}
.glass-panel,.mini-card,[data-testid="stMetric"],[data-testid="stExpander"] {background:#fffefb !important;border:1px solid #dce3d8 !important;border-radius:16px !important;box-shadow:0 5px 20px #073d3b08 !important;}
[data-testid="stFileUploaderDropzone"] {background:linear-gradient(145deg,#fcfdf9,#f0f6ee) !important;border:1px dashed #aebfb3 !important;border-radius:12px !important;}
[data-testid="stButton"] button,[data-testid="stDownloadButton"] button {background:linear-gradient(110deg,#b9933e,#ead395 55%,#c6a04a) !important;border:1px solid #b28d39 !important;color:#173e32 !important;border-radius:9px !important;box-shadow:0 4px 12px #aa873920 !important;}
[data-testid="stButton"] button p,[data-testid="stDownloadButton"] button p {color:#173e32 !important;}
[role="tab"][aria-selected="true"] {background:#075b57 !important;color:#fff8e8 !important;border-bottom:2px solid #c7a34e !important;}
[role="tab"][aria-selected="true"] p {color:#fff8e8 !important;}
[data-testid="stSidebar"] {background:linear-gradient(155deg,#073d3b,#075b57) !important;}
button:focus-visible,a:focus-visible {outline:3px solid #a3802b !important;outline-offset:3px;}
@media(prefers-reduced-motion:reduce) {* {transition:none!important;animation:none!important;}}

.hero-card,.research-heading{position:relative;isolation:isolate;overflow:hidden;background:radial-gradient(ellipse at 22% 0%,#499a8755,transparent 58%),linear-gradient(170deg,#176c60,#0a514a 40%,#073c39) !important;box-shadow:inset 0 2px 0 #ffffff1f,inset 0 -7px 13px #001c2540,0 10px 22px #073d3b1c !important;border-color:#bb9847 !important;}
.hero-card:after,.research-heading:after{content:'';position:absolute;right:24px;top:24px;width:92px;height:92px;border:1px solid #d8bf7770;border-radius:50%;opacity:.22;pointer-events:none;z-index:-1;background:radial-gradient(ellipse at 30% 25%,#e9d39890,#0b5243a8 60%,#032d2bcc);box-shadow:inset -12px -8px 18px #001b2b90,inset 3px 4px 9px #fff4be50,0 9px 15px #00232365;}
.hero-title,.hero-card h1{text-shadow:0 2px 3px #001e20a0 !important;}
</style>""", unsafe_allow_html=True)


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
    # Keep the hero-card hook: Android supplies its own native identity and hides this block.
    st.markdown(render_text('<section class="hero-card" aria-label="CSF Research">\n<div class="research-heading">\n<div class="research-eyebrow"><svg viewBox="0 0 36 36" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><circle cx="18" cy="18" r="15"/><path d="M3 18h30M18 3C7 11 7 25 18 33C29 25 29 11 18 3M6 9Q18 17 30 9M6 27Q18 19 30 27"/><circle fill="white" stroke="none" cx="29" cy="9" r="2.7"/></svg><span>{{brand}}</span></div>\n<h1>{{title}}</h1>\n<p class="research-subtitle">{{subtitle}}</p>\n<p class="research-methods">{{methods}}</p>\n</div>\n<div class="research-credit"><div><span class="research-credit-label">{{developer_label}}</span><strong>{{developer_name}}</strong></div><span class="research-affiliation">{{affiliation}}</span></div>\n</section>'),unsafe_allow_html=True)


def header_panels() -> None:
    st.markdown(render_text('<div class="info-grid">\n<div class="mini-card"><h4>{{swara_tab}}</h4><p>{{swara_about}}</p></div>\n<div class="mini-card"><h4>{{cocoso_tab}}</h4><p>{{cocoso_about}}</p></div>\n</div>'),unsafe_allow_html=True)


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
    st.markdown(render_text('<div class="glass-panel"><span class="section-label">{{swara_intro_title}}</span><p class="caption-note">{{swara_intro}}</p></div>'), unsafe_allow_html=True)
    uploaded = st.file_uploader(text('swara_upload'), type=["xlsx"], key="swara_upload", max_upload_size=10)
    st.download_button(text('swara_template'),data=create_swara_template(),file_name="csf_swara_input_template.xlsx",key="swara_template")
    with st.expander(text('calculation_settings'), expanded=False):
        p=st.slider(text('attitude_label'),0.0,1.0,0.5,0.05,key="swara_p")
        radius_policy=st.selectbox(text('radius_label'),["max","min"],key="swara_radius")

    if not uploaded:
        st.info(text('swara_empty'))
        return
    try:
        results = calculate_csf_swara(uploaded, p=p, radius_policy=radius_policy)
    except Exception as exc:
        st.error(f"SWARA calculation failed: {exc}")
        return

    weights = results["weights"]
    c1, c2, c3 = st.columns(3)
    c1.metric(text('criteria_metric'), len(weights))
    c2.metric(text('top_criterion'), str(weights.sort_values("Rank").iloc[0]["Criterion"]))
    c3.metric(text('top_weight'), f"{weights['Final_SWARA_Weight'].max():.4f}")

    st.subheader(text('swara_results'))
    st_df(weights.round(6))
    show_bar(weights, x="Final_SWARA_Weight", y="Criterion", title=text('swara_chart'), text_col="Final_SWARA_Weight")

    with st.expander(text('swara_details')):
        st.markdown(text('aggregated_evaluations'))
        st_df(results["aggregated"].round(6))
        st.markdown(text('expert_weights'))
        st_df(results["expert_weights"].round(6))
        st.markdown(text('parsed_terms'))
        st_df(results["terms"].round(6), height=360)

    st.subheader(text('download_section'))
    download_record(results,"swara")
    st.download_button(text('swara_download'), data=export_swara_results(results), file_name="csf_swara_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", key="swara_results_download")

def cocoso_tab() -> None:
    st.markdown(render_text('<div class="glass-panel"><span class="section-label">{{cocoso_intro_title}}</span><p class="caption-note">{{cocoso_intro}}</p></div>'), unsafe_allow_html=True)
    uploaded = st.file_uploader(text('cocoso_upload'), type=["xlsx"], key="cocoso_upload", max_upload_size=10)
    st.download_button(text('cocoso_template'),data=create_cocoso_template(),file_name="csf_cocoso_input_template.xlsx",key="cocoso_template")
    with st.expander(text('calculation_settings'), expanded=False):
        p=st.slider(text('attitude_label'),0.0,1.0,0.5,0.05,key="cocoso_p")
        radius_policy=st.selectbox(text('radius_label'),["max","min"],key="cocoso_radius")
        lam=st.slider(text('lambda_label'),0.0,1.0,0.5,0.05,key="cocoso_lambda")

    if not uploaded:
        st.info(text('cocoso_empty'))
        return
    try:
        results = calculate_csf_cocoso(uploaded, p=p, lambda_value=lam, radius_policy=radius_policy)
    except Exception as exc:
        st.error(f"CoCoSo calculation failed: {exc}")
        return

    ranking = results["results"]
    c1, c2, c3 = st.columns(3)
    c1.metric(text('alternatives_metric'), len(ranking))
    c2.metric(text('best_alternative'), str(ranking.sort_values("Rank").iloc[0]["Alternative"]))
    c3.metric(text('best_score'), f"{ranking['Final_Crisp_Score'].max():.4f}")

    st.subheader(text('cocoso_results'))
    st_df(ranking.round(6))
    show_bar(ranking, x="Final_Crisp_Score", y="Alternative", title=text('cocoso_chart'), text_col="Final_Crisp_Score")

    with st.expander(text('cocoso_details')):
        st.markdown(text('criterion_weights'))
        st_df(results["criteria_weights"].round(6))
        st.markdown(text('criterion_types'))
        st_df(results["criteria_types"])
        st.markdown(text('expert_weights'))
        st_df(results["expert_weights"].round(6))
        st.markdown(text('score_matrix'))
        show_heatmap(results["matrices"]["optimistic_score_matrix"].round(6), text('optimistic_chart'))
        show_heatmap(results["matrices"]["pessimistic_score_matrix"].round(6), text('pessimistic_chart'))

    st.subheader(text('download_section'))
    download_record(results,"cocoso")
    st.download_button(text('cocoso_download'), data=export_cocoso_results(results), file_name="csf_cocoso_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", key="cocoso_results_download")



def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="C", layout="wide")
    apply_custom_style()
    apply_dream_style()
    warning = text_warning()
    if warning:
        st.warning(warning)
    hero_section()
    if text("extra_note").strip():
        st.write(text("extra_note"))
    tab_swara, tab_cocoso = st.tabs([text('swara_tab'), text('cocoso_tab')])
    with tab_swara:
        swara_tab()
    with tab_cocoso:
        cocoso_tab()
    with st.expander(text('about_section')):
        header_panels()
    with st.expander(text('method_section')):
        st.write(text('method_note'))
        st.write(text('privacy_note'))

if __name__ == "__main__":
    main()
