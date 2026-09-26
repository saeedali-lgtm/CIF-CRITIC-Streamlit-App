"""Load editable display copy; preserve defaults when an edit is invalid."""
from pathlib import Path
from html import escape
import json
import re

DEFAULT_TEXTS = {'page_title': 'CSF Research | Circular Spherical Fuzzy Sets', 'download_record': 'Download reproducibility record', 'swara_upload': '1. Upload SWARA Excel workbook', 'swara_template': 'Download SWARA input template', 'calculation_settings': 'Calculation settings', 'attitude_label': 'Decision-maker attitude p', 'radius_label': 'Radius policy', 'swara_empty': 'Upload your SWARA workbook above to calculate results automatically. The downloadable template contains synthetic examples; replace them with your data.', 'criteria_metric': 'Criteria', 'top_criterion': 'Top criterion', 'top_weight': 'Top weight', 'swara_results': '2. Final CSF-SWARA weights', 'swara_chart': 'Final CSF-SWARA Criterion Weights', 'swara_details': 'Aggregated CSF values and expert weights', 'aggregated_evaluations': '**Aggregated criterion evaluations**', 'expert_weights': '**Expert weights**', 'parsed_terms': '**Parsed input terms**', 'download_section': '3. Download results', 'swara_download': 'Download SWARA results Excel', 'cocoso_upload': '1. Upload CoCoSo Excel workbook', 'cocoso_template': 'Download CoCoSo input template', 'lambda_label': 'CoCoSo lambda', 'cocoso_empty': 'Upload your CoCoSo workbook above to calculate results automatically. The downloadable template contains synthetic examples; replace them with your data.', 'alternatives_metric': 'Alternatives', 'best_alternative': 'Best alternative', 'best_score': 'Best score', 'cocoso_results': '2. Final CSF-CoCoSo ranking', 'cocoso_chart': 'Final CSF-CoCoSo Alternative Ranking', 'cocoso_details': 'Criterion weights, types, and matrices', 'criterion_weights': '**Criterion weights used in CoCoSo**', 'criterion_types': '**Criterion types**', 'score_matrix': '**Aggregated score matrix**', 'optimistic_chart': 'Optimistic score matrix', 'pessimistic_chart': 'Pessimistic score matrix', 'cocoso_download': 'Download CoCoSo results Excel', 'swara_tab': 'CSF-SWARA', 'cocoso_tab': 'CSF-CoCoSo', 'about_section': 'About this research tool', 'method_section': 'Method version and data processing', 'method_note': 'This release preserves the equations of the supplied Python implementation. It differs from the previously revised maturity workbook; see METHOD_NOTES.md for the documented choices and limitations.', 'privacy_note': 'Local execution processes uploaded workbooks on this computer. A hosted deployment processes them on its server. The app does not deliberately save uploaded workbooks.', 'brand': 'CSF / RESEARCH', 'title': 'Circular Spherical Fuzzy Sets', 'subtitle': 'Criterion weighting and alternative ranking under uncertainty.', 'methods': 'SWARA weighting · CoCoSo ranking', 'developer_label': 'Developer & Concept Designer', 'developer_name': 'Dr. Saeed Alinejad', 'affiliation': 'Shiraz University, Iran', 'swara_about': 'Expert judgments are represented with circular spherical fuzzy numbers to calculate normalized criterion weights under uncertainty.', 'cocoso_about': 'Decision matrices and user-provided criterion weights are processed independently to rank alternatives using CoCoSo-based compromise scores.', 'swara_intro_title': 'CSF-SWARA Weighting', 'swara_intro': 'Upload a SWARA workbook to calculate criterion weights from expert linguistic judgments. This tab is independent from CoCoSo.', 'cocoso_intro_title': 'CSF-CoCoSo Ranking', 'cocoso_intro': 'Upload a CoCoSo workbook containing decision matrix sheets and a Criteria_Weights sheet. The weights may come from SWARA, CRITIC, AHP, or any other method.'}

def load_texts(path):
    values = DEFAULT_TEXTS.copy()
    try:
        supplied = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        if not isinstance(supplied, dict):
            raise ValueError("The file must contain a JSON object")
        invalid = []
        for key, value in supplied.items():
            if key not in values:
                invalid.append(key)
            elif not isinstance(value, str) or (not value.strip() and key not in {"subtitle", "methods", "affiliation", "extra_note"}):
                invalid.append(key)
            else:
                values[key] = value
        warning = ("Some entries in ui_texts.json were ignored. Use the original keys and non-empty text values: " + ", ".join(invalid)) if invalid else ""
        return values, warning
    except (OSError, ValueError) as exc:
        return values, "The text settings could not be loaded; the default interface is being shown. Check ui_texts.json: " + str(exc)

# Load on each Streamlit rerun, including after a text-only edit.
def text(key):
    return load_texts(Path(__file__).with_name("ui_texts.json"))[0][key]

def render_text(template):
    values, _ = load_texts(Path(__file__).with_name("ui_texts.json"))
    return re.sub(r"\{\{([a-z_]+)\}\}", lambda match: escape(values[match.group(1)]), template)

DEFAULT_TEXTS["extra_note"] = ""

def text_warning():
    return load_texts(Path(__file__).with_name("ui_texts.json"))[1]
