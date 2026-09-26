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
APP_TITLE = "CSF Research | Circular Spherical Fuzzy Sets"

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
    st.markdown("""<section class="hero-card" aria-label="CSF Research">
<div class="research-heading">
<div class="research-eyebrow"><svg viewBox="0 0 36 36" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><circle cx="18" cy="18" r="15"/><path d="M3 18h30M18 3C7 11 7 25 18 33C29 25 29 11 18 3M6 9Q18 17 30 9M6 27Q18 19 30 27"/><circle fill="white" stroke="none" cx="29" cy="9" r="2.7"/></svg><span>CSF / RESEARCH</span></div>
<h1>Circular Spherical Fuzzy Sets</h1>
<p class="research-subtitle">Criterion weighting and alternative ranking under uncertainty.</p>
<p class="research-methods">SWARA weighting &nbsp; · &nbsp; CoCoSo ranking</p>
</div>
<div class="research-credit"><div><span class="research-credit-label">Developer &amp; Concept Designer</span><strong>Dr. Saeed Alinejad</strong></div><span class="research-affiliation">Shiraz University, Iran</span></div>
</section>""",unsafe_allow_html=True)


def header_panels() -> None:
    st.markdown("""<div class="info-grid">
<div class="mini-card"><h4>CSF-SWARA</h4><p>Expert judgments are represented with circular spherical fuzzy numbers to calculate normalized criterion weights under uncertainty.</p></div>
<div class="mini-card"><h4>CSF-CoCoSo</h4><p>Decision matrices and user-provided criterion weights are processed independently to rank alternatives using CoCoSo-based compromise scores.</p></div>
</div>""",unsafe_allow_html=True)


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
    uploaded = st.file_uploader("1. Upload SWARA Excel workbook", type=["xlsx"], key="swara_upload", max_upload_size=10)
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
    st.download_button("Download SWARA results Excel", data=export_swara_results(results), file_name="csf_swara_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")

def cocoso_tab() -> None:
    st.markdown('<div class="glass-panel"><span class="section-label">CSF-CoCoSo Ranking</span><p class="caption-note">Upload a CoCoSo workbook containing decision matrix sheets and a Criteria_Weights sheet. The weights may come from SWARA, CRITIC, AHP, or any other method.</p></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("1. Upload CoCoSo Excel workbook", type=["xlsx"], key="cocoso_upload", max_upload_size=10)
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
    st.download_button("Download CoCoSo results Excel", data=export_cocoso_results(results), file_name="csf_cocoso_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")



def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="C", layout="wide")
    apply_custom_style()
    hero_section()
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
