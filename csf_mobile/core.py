"""Numerical implementation extracted unchanged from the author-supplied script."""
from __future__ import annotations
import re
from io import BytesIO
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

PERSIAN_DIGIT_MAP = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩٫٬", "01234567890123456789..")

CSF_IMPORTANCE_SCALE = {
    "AI":  {"description": "Absolutely Important", "T": 0.90, "I": 0.10, "F": 0.10},
    "VHI": {"description": "Very High Important", "T": 0.80, "I": 0.20, "F": 0.20},
    "HI":  {"description": "High Important", "T": 0.70, "I": 0.30, "F": 0.30},
    "MI":  {"description": "Minimum Important", "T": 0.60, "I": 0.40, "F": 0.40},
    "EI":  {"description": "Equal Importance", "T": 0.50, "I": 0.50, "F": 0.50},
    "MLI": {"description": "Medium/Low Important", "T": 0.40, "I": 0.60, "F": 0.40},
    "LI":  {"description": "Low Important", "T": 0.30, "I": 0.70, "F": 0.30},
    "VLI": {"description": "Very Low Important", "T": 0.20, "I": 0.80, "F": 0.20},
    "AL":  {"description": "Absolutely Low", "T": 0.10, "I": 0.90, "F": 0.10},
}

NUMERIC_TERM_MAP = {9: "AI", 8: "VHI", 7: "HI", 6: "MI", 5: "EI", 4: "MLI", 3: "LI", 2: "VLI", 1: "AL"}

EXPERT_INFO_SHEET_NAMES = {"expert_info", "experts", "expert_weights", "decision_makers", "dm_weights"}

CRITERIA_WEIGHT_SHEET_NAMES = {"criteria_weights", "criterion_weights", "weights", "swara_weights"}

CRITERIA_TYPE_SHEET_NAMES = {"criteria_types", "criterion_types", "types", "benefit_cost", "criteria_info"}

SWARA_EVAL_SHEET_NAMES = {"swara_evaluations", "swara", "criteria_evaluations", "criterion_evaluations"}

AUX_SHEET_KEYWORDS = {"scale", "readme", "instruction", "guide", "result", "output", "parameter", "template"}

ALTERNATIVE_ALIASES = {"alternative", "alternatives", "option", "options", "challenge", "row", "item", "case", "a"}

CRITERION_ALIASES = {"criterion", "criteria", "factor", "attribute", "column", "c"}

VALUE_ALIASES = {"value", "term", "evaluation", "assessment", "score", "rating"}

EXPERT_ALIASES = {"expert", "decision_maker", "dm", "name"}

WEIGHT_ALIASES = {"weight", "w", "criterion_weight", "criteria_weight"}

TYPE_ALIASES = {"type", "criterion_type", "criteria_type", "benefit_cost", "direction"}

RELATIVE_IMPORTANCE_ALIASES = {"s", "sj", "relative_importance", "relativeimportance", "comparative_importance"}

RADIUS_ALIASES = {"r", "radius"}

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how="all").dropna(axis=1, how="all").copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

def get_column_by_alias(df: pd.DataFrame, aliases: set) -> Optional[str]:
    for col in df.columns:
        if str(col).strip().lower().replace(" ", "_") in aliases:
            return col
    return None

def normalize_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().translate(PERSIAN_DIGIT_MAP)

def standardize_term(value) -> str:
    raw = normalize_text(value)
    if not raw:
        raise ValueError("Empty CSF linguistic term found.")
    compact = re.sub(r"\s+", "", raw.upper()).replace("-", "").replace("_", "")
    try:
        rounded = int(round(float(compact)))
        if rounded in NUMERIC_TERM_MAP:
            return NUMERIC_TERM_MAP[rounded]
    except Exception:
        pass
    aliases = {
        "AI": "AI", "ABSOLUTELYIMPORTANT": "AI", "ABSOLUTELYHIGH": "AI", "AH": "AI", "9": "AI",
        "VHI": "VHI", "VERYHIGHIMPORTANT": "VHI", "VERYHIGH": "VHI", "VH": "VHI", "8": "VHI",
        "HI": "HI", "HIGHIMPORTANT": "HI", "HIGH": "HI", "H": "HI", "7": "HI",
        "MI": "MI", "MINIMUMIMPORTANT": "MI", "MODERATEIMPORTANT": "MI", "MEDIUMHIGH": "MI", "MH": "MI", "6": "MI",
        "EI": "EI", "EQUALIMPORTANCE": "EI", "EQUAL": "EI", "AVERAGE": "EI", "AE": "EI", "5": "EI",
        "MLI": "MLI", "LOWIMPORTANT": "MLI", "MEDIUMLOW": "MLI", "ML": "MLI", "4": "MLI",
        "LI": "LI", "LOW": "LI", "L": "LI", "3": "LI",
        "VLI": "VLI", "VERYLOWIMPORTANT": "VLI", "VERYLOW": "VLI", "VL": "VLI", "2": "VLI",
        "AL": "AL", "ABSOLUTELYLOW": "AL", "1": "AL",
    }
    if compact in aliases:
        return aliases[compact]
    # Persian-friendly matching
    p = raw.replace(" ", "")
    if "بسیارزیاد" in p or "کاملازیاد" in p or "کاملاًزیاد" in p or "قطعا" in p:
        return "AI"
    if "خیلیزیاد" in p:
        return "VHI"
    if "زیاد" in p or "بالا" in p:
        return "HI"
    if "متوسط" in p and "کم" not in p and "پایین" not in p:
        return "EI"
    if "خیلیکم" in p:
        return "VLI"
    if "کاملاکم" in p or "کاملاًکم" in p:
        return "AL"
    if "کم" in p or "پایین" in p:
        return "LI"
    raise ValueError(f"Invalid CSF linguistic term: {value}")

def term_to_csf(value, radius: float = 0.0) -> np.ndarray:
    term = standardize_term(value)
    row = CSF_IMPORTANCE_SCALE[term]
    csf = np.array([row["T"], row["I"], row["F"], float(radius)], dtype=float)
    validate_csf(csf, label=term)
    return csf

def validate_csf(x: np.ndarray, label: str = "") -> None:
    T, I, F, r = [float(v) for v in x]
    eps = 1e-12
    if not all(-eps <= v <= 1 + eps for v in [T, I, F, r]):
        raise ValueError(f"Invalid CSF number {label}: T, I, F, and r must be in [0,1].")
    if T * T + I * I + F * F > 1 + eps:
        raise ValueError(f"Invalid CSF number {label}: T^2 + I^2 + F^2 must be <= 1.")

def hesitation_degree(T: float, I: float, F: float) -> float:
    return max(0.0, 1.0 - T * T - I * I - F * F)

def score_csf(x: np.ndarray, p: float = 0.5) -> float:
    T, I, F, r = [float(v) for v in x]
    return 0.25 * (T - I - F + np.sqrt(2.0) + r * (2.0 * p - 1.0))

def accuracy_csf(x: np.ndarray) -> float:
    T, I, F, _ = [float(v) for v in x]
    return T + I + F

def complement_csf(x: np.ndarray) -> np.ndarray:
    T, I, F, r = [float(v) for v in x]
    return np.array([F, I, T, r], dtype=float)

def rho_radius(a: float, b: float, policy: str = "max") -> float:
    return max(float(a), float(b)) if policy.lower() == "max" else min(float(a), float(b))

def csf_algebraic_add(a: np.ndarray, b: np.ndarray, radius_policy: str = "max") -> np.ndarray:
    Ta, Ia, Fa, ra = [float(v) for v in a]
    Tb, Ib, Fb, rb = [float(v) for v in b]
    T = np.sqrt(max(0.0, Ta * Ta + Tb * Tb - (Ta * Ta) * (Tb * Tb)))
    I = Ia * Ib
    F = Fa * Fb
    r = rho_radius(ra, rb, radius_policy)
    out = np.clip(np.array([T, I, F, r], dtype=float), 0.0, 1.0)
    return out

def csf_scalar_multiply(j: float, a: np.ndarray) -> np.ndarray:
    j = max(0.0, float(j))
    T, I, F, r = [float(v) for v in a]
    return np.clip(np.array([
        np.sqrt(max(0.0, 1.0 - (1.0 - T * T) ** j)),
        I ** j,
        F ** j,
        r ** j if r > 0 else 0.0,
    ], dtype=float), 0.0, 1.0)

def csf_power(a: np.ndarray, j: float) -> np.ndarray:
    j = max(0.0, float(j))
    T, I, F, r = [float(v) for v in a]
    return np.clip(np.array([
        T ** j,
        I ** j,
        np.sqrt(max(0.0, 1.0 - (1.0 - F * F) ** j)),
        r ** j if r > 0 else 0.0,
    ], dtype=float), 0.0, 1.0)

def weighted_arithmetic_aggregation(values: np.ndarray, weights: np.ndarray, radius_policy: str = "max") -> np.ndarray:
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    weights = weights / weights.sum() if weights.sum() > 0 else np.ones(len(values)) / len(values)
    T = np.sqrt(max(0.0, 1.0 - np.prod((1.0 - values[:, 0] ** 2) ** weights)))
    I = np.prod(values[:, 1] ** weights)
    F = np.prod(values[:, 2] ** weights)
    # If explicit radii are present, aggregate them geometrically; otherwise calculate radius from expert dispersion.
    explicit_r = values[:, 3]
    r_geo = np.prod(np.where(explicit_r <= 0, 1e-12, explicit_r) ** weights) if np.any(explicit_r > 0) else 0.0
    center = np.array([T, I, F], dtype=float)
    distances = np.sqrt(np.sum((values[:, :3] - center[None, :]) ** 2, axis=1))
    r_dispersion = float(np.max(distances)) if len(values) > 1 else 0.0
    r = max(float(r_geo), r_dispersion) if radius_policy == "max" else min(float(r_geo), r_dispersion) if np.any(explicit_r > 0) else r_dispersion
    return np.clip(np.array([T, I, F, r], dtype=float), 0.0, 1.0)

def optimistic_pessimistic(x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    T, I, F, r = [float(v) for v in x]
    optimistic = np.clip(np.array([T + r, I - r, F - r, r], dtype=float), 0.0, 1.0)
    pessimistic = np.clip(np.array([T - r, I + r, F + r, r], dtype=float), 0.0, 1.0)
    return optimistic, pessimistic

def add_many(values: List[np.ndarray], radius_policy: str = "max") -> np.ndarray:
    identity_r = 0.0 if radius_policy == "max" else 1.0
    total = np.array([0.0, 1.0, 1.0, identity_r], dtype=float)
    for val in values:
        total = csf_algebraic_add(total, val, radius_policy=radius_policy)
    return np.clip(total, 0.0, 1.0)

def standardize_criterion_type(value, default_type: str = "Benefit") -> str:
    if pd.isna(value) or str(value).strip() == "":
        return default_type
    text = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    if any(k in text for k in ["benefit", "positive", "max", "maximize", "gain", "سود", "مثبت", "بیشینه"]):
        return "Benefit"
    if any(k in text for k in ["cost", "negative", "min", "minimize", "expense", "هزینه", "منفی", "کمینه"]):
        return "Cost"
    return default_type

def calculate_expert_weights(expert_names: List[str], expert_info: Optional[pd.DataFrame]) -> pd.DataFrame:
    if expert_info is None or expert_info.empty:
        w = np.ones(len(expert_names), dtype=float) / len(expert_names)
        return pd.DataFrame({"Expert": expert_names, "Weight_Source": "Equal", "Term_or_Value": "Equal", "Raw_Expert_Value": 1.0, "Expert_Weight": w})

    df = clean_dataframe(expert_info)
    expert_col = get_column_by_alias(df, EXPERT_ALIASES)
    weight_col = get_column_by_alias(df, WEIGHT_ALIASES)
    term_col = get_column_by_alias(df, {"weightterm", "term", "linguistic", "expertise", "level"})
    rows = []
    if expert_col:
        df[expert_col] = df[expert_col].astype(str).str.strip()

    for pos, expert in enumerate(expert_names):
        row = None
        if expert_col:
            match = df[df[expert_col] == expert]
            if not match.empty:
                row = match.iloc[0]
        elif pos < len(df):
            row = df.iloc[pos]

        if row is None:
            rows.append({"Expert": expert, "Weight_Source": "Equal fallback", "Term_or_Value": "Missing", "Raw_Expert_Value": 1.0})
            continue
        if weight_col and not pd.isna(row[weight_col]):
            raw = float(str(row[weight_col]).translate(PERSIAN_DIGIT_MAP))
            rows.append({"Expert": expert, "Weight_Source": "Numeric weight", "Term_or_Value": raw, "Raw_Expert_Value": raw})
        elif term_col and not pd.isna(row[term_col]):
            term = standardize_term(row[term_col])
            csf = term_to_csf(term)
            T, I, F, _ = csf
            h = hesitation_degree(T, I, F)
            # Adapted expert-weight expression from the CSF-SWARA/CoCoSo method.
            raw = T + h * (T / max(1e-12, 1.0 - h))
            rows.append({"Expert": expert, "Weight_Source": "CSF expertise term", "Term_or_Value": term, "Raw_Expert_Value": raw})
        else:
            rows.append({"Expert": expert, "Weight_Source": "Equal fallback", "Term_or_Value": "Missing", "Raw_Expert_Value": 1.0})

    out = pd.DataFrame(rows)
    raw_values = out["Raw_Expert_Value"].astype(float).clip(lower=0).to_numpy()
    out["Expert_Weight"] = raw_values / raw_values.sum() if raw_values.sum() > 0 else np.ones(len(expert_names)) / len(expert_names)
    return out

def criteria_types_from_sheet(criteria: List[str], type_df: Optional[pd.DataFrame], default_type: str = "Benefit") -> pd.DataFrame:
    lookup = {}
    if type_df is not None and not type_df.empty:
        df = clean_dataframe(type_df)
        c_col = get_column_by_alias(df, CRITERION_ALIASES | {"name"})
        t_col = get_column_by_alias(df, TYPE_ALIASES)
        if c_col and t_col:
            lookup = {str(row[c_col]).strip(): standardize_criterion_type(row[t_col], default_type) for _, row in df.iterrows()}
    return pd.DataFrame({"Criterion": criteria, "Type": [lookup.get(c, default_type) for c in criteria]})

def read_swara_workbook(uploaded_file) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    sheets = pd.read_excel(uploaded_file, sheet_name=None, dtype=object)
    eval_df = None
    expert_info = None
    for name, df in sheets.items():
        lower = name.lower().strip()
        df = clean_dataframe(df)
        if lower in SWARA_EVAL_SHEET_NAMES:
            eval_df = df
        elif lower in EXPERT_INFO_SHEET_NAMES:
            expert_info = df
    if eval_df is None:
        # fallback: first sheet that contains Expert, Criterion, Term/Value
        for name, df in sheets.items():
            df = clean_dataframe(df)
            if get_column_by_alias(df, EXPERT_ALIASES) and get_column_by_alias(df, CRITERION_ALIASES) and get_column_by_alias(df, VALUE_ALIASES):
                eval_df = df
                break
    if eval_df is None:
        raise ValueError("No SWARA evaluation sheet was found. Use a sheet named 'SWARA_Evaluations' with columns Expert, Criterion, and Term.")
    return eval_df, expert_info

def calculate_csf_swara(uploaded_file, p: float = 0.5, radius_policy: str = "max") -> Dict[str, object]:
    df, expert_info = read_swara_workbook(uploaded_file)
    expert_col = get_column_by_alias(df, EXPERT_ALIASES)
    criterion_col = get_column_by_alias(df, CRITERION_ALIASES)
    value_col = get_column_by_alias(df, VALUE_ALIASES)
    r_col = get_column_by_alias(df, RADIUS_ALIASES)
    s_col = get_column_by_alias(df, RELATIVE_IMPORTANCE_ALIASES)
    if not expert_col or not criterion_col or not value_col:
        raise ValueError("SWARA_Evaluations must contain Expert, Criterion, and Term/Value columns.")

    df = df.copy()
    df[expert_col] = df[expert_col].astype(str).str.strip()
    df[criterion_col] = df[criterion_col].astype(str).str.strip()
    expert_names = list(dict.fromkeys(df[expert_col].tolist()))
    criteria = list(dict.fromkeys(df[criterion_col].tolist()))
    expert_weights_df = calculate_expert_weights(expert_names, expert_info)
    expert_w = dict(zip(expert_weights_df["Expert"], expert_weights_df["Expert_Weight"]))

    agg_rows = []
    term_rows = []
    numeric_s_rows = []
    for criterion in criteria:
        sub = df[df[criterion_col] == criterion]
        values = []
        weights = []
        s_values = []
        s_weights = []
        for _, row in sub.iterrows():
            expert = str(row[expert_col]).strip()
            w = float(expert_w.get(expert, 1.0 / len(expert_names)))
            rad = float(str(row[r_col]).translate(PERSIAN_DIGIT_MAP)) if r_col and not pd.isna(row[r_col]) else 0.0
            csf = term_to_csf(row[value_col], radius=rad)
            values.append(csf)
            weights.append(w)
            term_rows.append({"Expert": expert, "Criterion": criterion, "Input_Term": standardize_term(row[value_col]), "Expert_Weight": w, "T": csf[0], "I": csf[1], "F": csf[2], "r": csf[3]})
            if s_col and not pd.isna(row[s_col]):
                s_values.append(float(str(row[s_col]).translate(PERSIAN_DIGIT_MAP)))
                s_weights.append(w)
        agg = weighted_arithmetic_aggregation(np.array(values), np.array(weights), radius_policy=radius_policy)
        score = score_csf(agg, p=p)
        accuracy = accuracy_csf(agg)
        rel_s = float(np.average(s_values, weights=s_weights)) if s_values else score
        numeric_s_rows.append({"Criterion": criterion, "Relative_Importance_Source": "Numeric S" if s_values else "Score function", "Relative_Importance_S": rel_s})
        agg_rows.append({"Criterion": criterion, "T": agg[0], "I": agg[1], "F": agg[2], "r": agg[3], "Score": score, "Accuracy": accuracy})

    aggregated_df = pd.DataFrame(agg_rows)
    s_df = pd.DataFrame(numeric_s_rows)
    swara_df = aggregated_df.merge(s_df, on="Criterion", how="left")
    swara_df = swara_df.sort_values(["Score", "Accuracy"], ascending=[False, False]).reset_index(drop=True)
    swara_df["Order"] = np.arange(1, len(swara_df) + 1)
    k_values = []
    q_values = []
    for idx, row in swara_df.iterrows():
        if idx == 0:
            k = 1.0
            q = 1.0
            s_used = 0.0
        else:
            s_used = max(0.0, float(row["Relative_Importance_S"]))
            k = 1.0 + s_used
            q = q_values[-1] / k if k > 0 else q_values[-1]
        k_values.append(k)
        q_values.append(q)
        swara_df.loc[idx, "S_used"] = s_used
    swara_df["K_j"] = k_values
    swara_df["q_j"] = q_values
    swara_df["Final_SWARA_Weight"] = swara_df["q_j"] / swara_df["q_j"].sum()
    swara_df["Rank"] = swara_df["Final_SWARA_Weight"].rank(ascending=False, method="dense").astype(int)
    return {"weights": swara_df, "aggregated": aggregated_df, "expert_weights": expert_weights_df, "terms": pd.DataFrame(term_rows)}

def extract_wide_matrix(df: pd.DataFrame) -> Tuple[List[str], List[str], np.ndarray]:
    df = clean_dataframe(df)
    if df.shape[1] < 2:
        raise ValueError("Decision matrix must have an Alternative column and at least one criterion.")
    alternatives = df.iloc[:, 0].astype(str).str.strip().tolist()
    criteria = [str(c).strip() for c in df.columns[1:]]
    terms = np.empty((len(alternatives), len(criteria)), dtype=object)
    for i in range(len(alternatives)):
        for j in range(len(criteria)):
            terms[i, j] = standardize_term(df.iloc[i, j + 1])
    return alternatives, criteria, terms

def extract_long_matrix(df: pd.DataFrame) -> Tuple[List[str], List[str], np.ndarray]:
    df = clean_dataframe(df)
    alt_col = get_column_by_alias(df, ALTERNATIVE_ALIASES)
    crit_col = get_column_by_alias(df, CRITERION_ALIASES)
    value_col = get_column_by_alias(df, VALUE_ALIASES)
    if not alt_col or not crit_col or not value_col:
        raise ValueError("Long decision matrix requires Alternative, Criterion, and Value columns.")
    alternatives = list(dict.fromkeys(df[alt_col].astype(str).str.strip().tolist()))
    criteria = list(dict.fromkeys(df[crit_col].astype(str).str.strip().tolist()))
    ai = {a: i for i, a in enumerate(alternatives)}
    cj = {c: j for j, c in enumerate(criteria)}
    terms = np.empty((len(alternatives), len(criteria)), dtype=object)
    terms[:, :] = "EI"
    for _, row in df.iterrows():
        terms[ai[str(row[alt_col]).strip()], cj[str(row[crit_col]).strip()]] = standardize_term(row[value_col])
    return alternatives, criteria, terms

def extract_decision_matrix(df: pd.DataFrame) -> Tuple[List[str], List[str], np.ndarray, np.ndarray]:
    try:
        alternatives, criteria, terms = extract_long_matrix(df)
    except Exception:
        alternatives, criteria, terms = extract_wide_matrix(df)
    arr = np.zeros((len(alternatives), len(criteria), 4), dtype=float)
    for i in range(len(alternatives)):
        for j in range(len(criteria)):
            arr[i, j, :] = term_to_csf(terms[i, j], radius=0.0)
    return alternatives, criteria, terms, arr

def is_aux_sheet(name: str) -> bool:
    lower = name.lower().strip()
    if lower in EXPERT_INFO_SHEET_NAMES or lower in CRITERIA_TYPE_SHEET_NAMES or lower in CRITERIA_WEIGHT_SHEET_NAMES:
        return True
    return any(k in lower for k in AUX_SHEET_KEYWORDS)

def read_cocoso_workbook(uploaded_file) -> Tuple[Dict[str, pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame], List[str]]:
    sheets = pd.read_excel(uploaded_file, sheet_name=None, dtype=object)
    expert_sheets: Dict[str, pd.DataFrame] = {}
    expert_info = None
    criteria_weights = None
    criteria_types = None
    skipped = []
    for name, df in sheets.items():
        df = clean_dataframe(df)
        lower = name.lower().strip()
        if lower in EXPERT_INFO_SHEET_NAMES:
            expert_info = df
            skipped.append(name)
        elif lower in CRITERIA_WEIGHT_SHEET_NAMES:
            criteria_weights = df
            skipped.append(name)
        elif lower in CRITERIA_TYPE_SHEET_NAMES:
            criteria_types = df
            skipped.append(name)
        elif is_aux_sheet(name):
            skipped.append(name)
        else:
            try:
                extract_decision_matrix(df)
                expert_sheets[name] = df
            except Exception:
                skipped.append(name)
    if not expert_sheets:
        raise ValueError("No valid CoCoSo decision matrix was found. Add at least one expert decision matrix sheet.")
    return expert_sheets, expert_info, criteria_weights, criteria_types, skipped

def read_criterion_weights(criteria: List[str], weights_df: Optional[pd.DataFrame]) -> pd.DataFrame:
    if weights_df is None or weights_df.empty:
        return pd.DataFrame({"Criterion": criteria, "Weight": np.ones(len(criteria)) / len(criteria), "Weight_Source": "Equal fallback"})
    df = clean_dataframe(weights_df)
    c_col = get_column_by_alias(df, CRITERION_ALIASES | {"name"})
    w_col = get_column_by_alias(df, WEIGHT_ALIASES)
    if not c_col or not w_col:
        raise ValueError("Criteria_Weights sheet must contain Criterion and Weight columns.")
    lookup = {str(row[c_col]).strip(): float(str(row[w_col]).translate(PERSIAN_DIGIT_MAP)) for _, row in df.iterrows() if not pd.isna(row[w_col])}
    weights = np.array([lookup.get(c, np.nan) for c in criteria], dtype=float)
    if np.isnan(weights).any():
        missing = [c for c, w in zip(criteria, weights) if np.isnan(w)]
        raise ValueError(f"Missing weights for criteria: {missing}")
    weights = np.clip(weights, 0, None)
    if weights.sum() <= 0:
        weights = np.ones(len(criteria)) / len(criteria)
    else:
        weights = weights / weights.sum()
    return pd.DataFrame({"Criterion": criteria, "Weight": weights, "Weight_Source": "Criteria_Weights"})

def aggregate_cocoso_experts(expert_sheets: Dict[str, pd.DataFrame], expert_weights: np.ndarray, criteria_types_df: pd.DataFrame, radius_policy: str = "max"):
    arrays = []
    term_matrices = {}
    ref_alts = ref_criteria = None
    for name, df in expert_sheets.items():
        alts, criteria, terms, arr = extract_decision_matrix(df)
        if ref_alts is None:
            ref_alts, ref_criteria = alts, criteria
        elif alts != ref_alts or criteria != ref_criteria:
            raise ValueError(f"Alternatives/criteria in sheet '{name}' are inconsistent with the first decision matrix sheet.")
        arrays.append(arr)
        term_matrices[name] = pd.DataFrame(terms, index=alts, columns=criteria)
    stacked = np.stack(arrays, axis=0)  # experts x alternatives x criteria x 4
    weights = np.asarray(expert_weights, dtype=float)
    weights = weights / weights.sum() if weights.sum() > 0 else np.ones(len(arrays)) / len(arrays)
    m, n = len(ref_alts), len(ref_criteria)
    aggregated = np.zeros((m, n, 4), dtype=float)
    type_lookup = dict(zip(criteria_types_df["Criterion"], criteria_types_df["Type"]))
    for i in range(m):
        for j, criterion in enumerate(ref_criteria):
            val = weighted_arithmetic_aggregation(stacked[:, i, j, :], weights, radius_policy=radius_policy)
            if type_lookup.get(criterion, "Benefit") == "Cost":
                val = complement_csf(val)
            aggregated[i, j, :] = val
    return ref_alts, ref_criteria, term_matrices, stacked, aggregated, weights

def score_matrix(matrix: np.ndarray, p: float) -> np.ndarray:
    m, n, _ = matrix.shape
    out = np.zeros((m, n), dtype=float)
    for i in range(m):
        for j in range(n):
            out[i, j] = score_csf(matrix[i, j, :], p=p)
    return out

def weighted_sum_csf(row: np.ndarray, weights: np.ndarray, radius_policy: str = "max") -> np.ndarray:
    vals = [csf_scalar_multiply(w, row[j, :]) for j, w in enumerate(weights)]
    return add_many(vals, radius_policy=radius_policy)

def weighted_product_csf(row: np.ndarray, weights: np.ndarray, radius_policy: str = "max") -> np.ndarray:
    vals = [csf_power(row[j, :], w) for j, w in enumerate(weights)]
    return add_many(vals, radius_policy=radius_policy)

def ensure_positive(arr: np.ndarray, eps: float = 1e-9) -> np.ndarray:
    arr = np.asarray(arr, dtype=float)
    min_v = float(np.min(arr)) if len(arr) else 0.0
    if min_v <= eps:
        return arr - min_v + eps
    return arr

def calculate_csf_cocoso(uploaded_file, p: float = 0.5, lambda_value: float = 0.5, radius_policy: str = "max") -> Dict[str, object]:
    expert_sheets, expert_info, criteria_weights_raw, criteria_types_raw, skipped = read_cocoso_workbook(uploaded_file)
    expert_names = list(expert_sheets.keys())
    first_alts, first_criteria, _, _ = extract_decision_matrix(next(iter(expert_sheets.values())))
    expert_weights_df = calculate_expert_weights(expert_names, expert_info)
    weights_df = read_criterion_weights(first_criteria, criteria_weights_raw)
    types_df = criteria_types_from_sheet(first_criteria, criteria_types_raw, default_type="Benefit")
    alternatives, criteria, term_matrices, stacked, aggregated, expert_weights = aggregate_cocoso_experts(
        expert_sheets, expert_weights_df["Expert_Weight"].to_numpy(dtype=float), types_df, radius_policy=radius_policy
    )
    crit_weights = weights_df["Weight"].to_numpy(dtype=float)

    optimistic = np.zeros_like(aggregated)
    pessimistic = np.zeros_like(aggregated)
    for i in range(len(alternatives)):
        for j in range(len(criteria)):
            optimistic[i, j, :], pessimistic[i, j, :] = optimistic_pessimistic(aggregated[i, j, :])

    S_o_csf, S_p_csf, P_o_csf, P_p_csf = [], [], [], []
    for i in range(len(alternatives)):
        S_o_csf.append(weighted_sum_csf(optimistic[i, :, :], crit_weights, radius_policy))
        S_p_csf.append(weighted_sum_csf(pessimistic[i, :, :], crit_weights, radius_policy))
        P_o_csf.append(weighted_product_csf(optimistic[i, :, :], crit_weights, radius_policy))
        P_p_csf.append(weighted_product_csf(pessimistic[i, :, :], crit_weights, radius_policy))
    S_o_csf, S_p_csf, P_o_csf, P_p_csf = map(np.array, [S_o_csf, S_p_csf, P_o_csf, P_p_csf])

    S_o = np.array([score_csf(x, p) for x in S_o_csf], dtype=float)
    S_p = np.array([score_csf(x, p) for x in S_p_csf], dtype=float)
    P_o = np.array([score_csf(x, p) for x in P_o_csf], dtype=float)
    P_p = np.array([score_csf(x, p) for x in P_p_csf], dtype=float)

    def cocoso_k(S: np.ndarray, P: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        S_pos = ensure_positive(S)
        P_pos = ensure_positive(P)
        Kia = (P_pos + S_pos) / np.sum(P_pos + S_pos)
        Kib = S_pos / np.min(S_pos) + P_pos / np.min(P_pos)
        Kic = (lambda_value * S_pos + (1.0 - lambda_value) * P_pos) / (lambda_value * np.max(S_pos) + (1.0 - lambda_value) * np.max(P_pos))
        K = np.cbrt(np.maximum(Kia * Kib * Kic, 0.0)) + (Kia + Kib + Kic) / 3.0
        return Kia, Kib, Kic, K

    Kia_o, Kib_o, Kic_o, K_o = cocoso_k(S_o, P_o)
    Kia_p, Kib_p, Kic_p, K_p = cocoso_k(S_p, P_p)
    final_score = 0.5 * (K_o + K_p)
    result_df = pd.DataFrame({
        "Alternative": alternatives,
        "S_Optimistic": S_o,
        "P_Optimistic": P_o,
        "Kia_Optimistic": Kia_o,
        "Kib_Optimistic": Kib_o,
        "Kic_Optimistic": Kic_o,
        "K_Optimistic": K_o,
        "S_Pessimistic": S_p,
        "P_Pessimistic": P_p,
        "Kia_Pessimistic": Kia_p,
        "Kib_Pessimistic": Kib_p,
        "Kic_Pessimistic": Kic_p,
        "K_Pessimistic": K_p,
        "Final_Crisp_Score": final_score,
    })
    result_df["Rank"] = result_df["Final_Crisp_Score"].rank(ascending=False, method="dense").astype(int)
    result_df = result_df.sort_values(["Rank", "Alternative"]).reset_index(drop=True)

    matrices = {
        "aggregated_T": pd.DataFrame(aggregated[:, :, 0], index=alternatives, columns=criteria),
        "aggregated_I": pd.DataFrame(aggregated[:, :, 1], index=alternatives, columns=criteria),
        "aggregated_F": pd.DataFrame(aggregated[:, :, 2], index=alternatives, columns=criteria),
        "radius_r": pd.DataFrame(aggregated[:, :, 3], index=alternatives, columns=criteria),
        "optimistic_score_matrix": pd.DataFrame(score_matrix(optimistic, p), index=alternatives, columns=criteria),
        "pessimistic_score_matrix": pd.DataFrame(score_matrix(pessimistic, p), index=alternatives, columns=criteria),
    }
    return {
        "results": result_df,
        "criteria_weights": weights_df,
        "criteria_types": types_df,
        "expert_weights": expert_weights_df,
        "matrices": matrices,
        "term_matrices": term_matrices,
        "skipped_sheets": skipped,
        "params": {"p": p, "lambda": lambda_value, "radius_policy": radius_policy},
    }

def scale_dataframe() -> pd.DataFrame:
    return pd.DataFrame([
        {"Symbol": k, "Description": v["description"], "T": v["T"], "I": v["I"], "F": v["F"]}
        for k, v in CSF_IMPORTANCE_SCALE.items()
    ])

def create_swara_template() -> bytes:
    output = BytesIO()
    swara_eval = pd.DataFrame({
        "Expert": ["Expert_1"] * 4 + ["Expert_2"] * 4,
        "Criterion": ["C1", "C2", "C3", "C4"] * 2,
        "Term": ["AI", "VHI", "HI", "MI", "VHI", "HI", "MI", "EI"],
        "R": [0.0] * 8,
        "S": [np.nan] * 8,
    })
    expert_info = pd.DataFrame({"Expert": ["Expert_1", "Expert_2"], "WeightTerm": ["AI", "VHI"]})
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        swara_eval.to_excel(writer, sheet_name="SWARA_Evaluations", index=False)
        expert_info.to_excel(writer, sheet_name="Expert_Info", index=False)
        scale_dataframe().to_excel(writer, sheet_name="CSF_Scale", index=False)
        pd.DataFrame({"Note": ["Columns required in SWARA_Evaluations: Expert, Criterion, Term. Optional: R and S.", "If S is blank, the score function is used as comparative importance."]}).to_excel(writer, sheet_name="ReadMe", index=False)
    return output.getvalue()

def create_cocoso_template() -> bytes:
    output = BytesIO()
    expert1 = pd.DataFrame({"Alternative": ["A1", "A2", "A3"], "C1": ["AI", "VHI", "HI"], "C2": ["HI", "MI", "EI"], "C3": ["VHI", "HI", "MI"]})
    expert2 = pd.DataFrame({"Alternative": ["A1", "A2", "A3"], "C1": ["VHI", "HI", "HI"], "C2": ["HI", "EI", "MI"], "C3": ["AI", "HI", "EI"]})
    weights = pd.DataFrame({"Criterion": ["C1", "C2", "C3"], "Weight": [0.40, 0.35, 0.25]})
    types = pd.DataFrame({"Criterion": ["C1", "C2", "C3"], "Type": ["Benefit", "Benefit", "Cost"]})
    expert_info = pd.DataFrame({"Expert": ["Expert_1", "Expert_2"], "WeightTerm": ["AI", "VHI"]})
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        expert1.to_excel(writer, sheet_name="Expert_1", index=False)
        expert2.to_excel(writer, sheet_name="Expert_2", index=False)
        weights.to_excel(writer, sheet_name="Criteria_Weights", index=False)
        types.to_excel(writer, sheet_name="Criteria_Types", index=False)
        expert_info.to_excel(writer, sheet_name="Expert_Info", index=False)
        scale_dataframe().to_excel(writer, sheet_name="CSF_Scale", index=False)
        pd.DataFrame({"Note": ["One decision matrix sheet per expert. First column = Alternative; remaining columns = criteria.", "Criteria_Weights is required for independent CoCoSo. Criteria_Types is optional."]}).to_excel(writer, sheet_name="ReadMe", index=False)
    return output.getvalue()

def export_swara_results(results: Dict[str, object]) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        results["weights"].to_excel(writer, sheet_name="Final_SWARA_Weights", index=False)
        results["aggregated"].to_excel(writer, sheet_name="Aggregated_CSF", index=False)
        results["expert_weights"].to_excel(writer, sheet_name="Expert_Weights", index=False)
        results["terms"].to_excel(writer, sheet_name="Input_Terms", index=False)
        scale_dataframe().to_excel(writer, sheet_name="CSF_Scale", index=False)
    return output.getvalue()

def export_cocoso_results(results: Dict[str, object]) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame([results["params"]]).to_excel(writer, sheet_name="Parameters", index=False)
        results["results"].to_excel(writer, sheet_name="Final_CoCoSo_Ranking", index=False)
        results["criteria_weights"].to_excel(writer, sheet_name="Criteria_Weights", index=False)
        results["criteria_types"].to_excel(writer, sheet_name="Criteria_Types", index=False)
        results["expert_weights"].to_excel(writer, sheet_name="Expert_Weights", index=False)
        for name, df in results["matrices"].items():
            df.to_excel(writer, sheet_name=name[:31])
        for name, df in results["term_matrices"].items():
            df.to_excel(writer, sheet_name=f"Terms_{name[:24]}")
        pd.DataFrame({"Skipped_sheets": results["skipped_sheets"]}).to_excel(writer, sheet_name="Skipped_Sheets", index=False)
        scale_dataframe().to_excel(writer, sheet_name="CSF_Scale", index=False)
    return output.getvalue()
