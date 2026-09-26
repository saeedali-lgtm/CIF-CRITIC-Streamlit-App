"""Strict input checks and reproducibility records around the unchanged author engine."""
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime, timezone
from importlib.metadata import version
import hashlib
import json
import math
import numpy as np
import pandas as pd
import core

VERSION = '1.0.0'

def number(value, label, low=0, high=None):
    try:
        out = float(str(value).translate(core.PERSIAN_DIGIT_MAP))
    except (TypeError, ValueError):
        raise ValueError(f'{label} must be numeric.') from None
    if not math.isfinite(out) or out < low or (high is not None and out > high):
        raise ValueError(f'{label} is outside the permitted range.')
    return out

def labels(series, label):
    if series.isna().any() or series.astype(str).str.strip().eq('').any():
        raise ValueError(f'{label} contains a blank identifier.')
    return series.astype(str).str.strip()

def term(value):
    raw = core.normalize_text(value)
    try:
        n = float(raw)
    except ValueError:
        return core.standardize_term(value)
    if not math.isfinite(n) or n != int(n) or not 1 <= n <= 9:
        raise ValueError('Numeric linguistic ratings must be integers from 1 to 9.')
    return core.standardize_term(value)

def read_upload(data):
    if not data or len(data) > 10 * 1024 * 1024:
        raise ValueError('Upload a non-empty .xlsx file smaller than 10 MB.')
    try:
        with ZipFile(BytesIO(data)) as z:
            if len(z.infolist()) > 2000 or sum(i.file_size for i in z.infolist()) > 60 * 1024 * 1024:
                raise ValueError('This workbook is too large after decompression.')
        sheets = pd.read_excel(BytesIO(data), sheet_name=None, dtype=object)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError('The file could not be read as an .xlsx workbook.') from exc
    if len(sheets) > 50 or sum(df.size for df in sheets.values()) > 100000:
        raise ValueError('Use at most 50 sheets and 100,000 input cells per workbook.')
    return {n: core.clean_dataframe(df) for n, df in sheets.items()}

def auxiliary(sheets, names):
    found = [df for n, df in sheets.items() if n.strip().lower() in names]
    if len(found) > 1:
        raise ValueError('More than one sheet was supplied for the same auxiliary input.')
    return found[0] if found else None

def check_experts(names, df):
    if df is None:
        return
    col = core.get_column_by_alias(df, core.EXPERT_ALIASES)
    if col is None:
        raise ValueError('Expert_Info must include an Expert column.')
    ids = labels(df[col], 'Expert_Info')
    if ids.duplicated().any() or set(ids) != set(names):
        raise ValueError('Expert_Info must contain exactly one row for every expert.')
    wc = core.get_column_by_alias(df, core.WEIGHT_ALIASES)
    tc = core.get_column_by_alias(df, {'weightterm','term','linguistic','expertise','level'})
    for _, row in df.iterrows():
        if wc and not pd.isna(row[wc]):
            if number(row[wc], 'Expert weight') <= 0:
                raise ValueError('Expert weights must be positive.')
        elif tc and not pd.isna(row[tc]):
            term(row[tc])
        else:
            raise ValueError('Each expert requires a weight or an expertise term.')

def validate_input(data, module):
    sheets = read_upload(data)
    if module == 'swara':
        df, info = core.read_swara_workbook(BytesIO(data))
        ec = core.get_column_by_alias(df, core.EXPERT_ALIASES)
        cc = core.get_column_by_alias(df, core.CRITERION_ALIASES)
        vc = core.get_column_by_alias(df, core.VALUE_ALIASES)
        if not all([ec, cc, vc]):
            raise ValueError('SWARA requires Expert, Criterion and Term columns.')
        pairs = pd.DataFrame({'e': labels(df[ec], 'Expert'), 'c': labels(df[cc], 'Criterion')})
        if pairs.duplicated().any() or len(pairs) != pairs.e.nunique()*pairs.c.nunique():
            raise ValueError('Provide exactly one rating for every expert-criterion pair.')
        if pairs.c.nunique() > 250 or pairs.e.nunique() > 50:
            raise ValueError('Use at most 250 criteria and 50 experts.')
        for val in df[vc]:
            term(val)
        for aliases, label, high in [(core.RADIUS_ALIASES, 'Radius', 1), (core.RELATIVE_IMPORTANCE_ALIASES, 'S', None)]:
            col = core.get_column_by_alias(df, aliases)
            if col:
                for val in df[col].dropna():
                    number(val, label, high=high)
        check_experts(list(pairs.e.unique()), info)
    else:
        experts = {}
        reference = None
        for name, df in sheets.items():
            if core.is_aux_sheet(name):
                continue
            ac = core.get_column_by_alias(df, core.ALTERNATIVE_ALIASES)
            cc = core.get_column_by_alias(df, core.CRITERION_ALIASES)
            vc = core.get_column_by_alias(df, core.VALUE_ALIASES)
            if all([ac, cc, vc]):
                pairs = pd.DataFrame({'a': labels(df[ac], 'Alternative'), 'c': labels(df[cc], 'Criterion')})
                if pairs.duplicated().any() or len(pairs) != pairs.a.nunique()*pairs.c.nunique():
                    raise ValueError(f'{name}: provide every alternative-criterion pair exactly once.')
                for val in df[vc]:
                    term(val)
            else:
                if len(df.columns)<2 or df.empty:
                    raise ValueError(f'{name}: decision matrix is empty.')
                if labels(df.iloc[:,0], 'Alternative').duplicated().any():
                    raise ValueError(f'{name}: duplicate alternative identifiers.')
                for val in df.iloc[:,1:].to_numpy().ravel():
                    term(val)
            alts, crits, _, _ = core.extract_decision_matrix(df)
            if reference and reference != (alts, crits):
                raise ValueError('All expert sheets must use identical alternative and criterion order.')
            reference = (alts, crits)
            experts[name] = df
        if not experts:
            raise ValueError('No expert decision matrix found.')
        if len(alts)*len(crits)*len(experts)>20000:
            raise ValueError('Use at most 20,000 expert-alternative-criterion ratings.')
        check_experts(list(experts), auxiliary(sheets, core.EXPERT_INFO_SHEET_NAMES))
        weights = auxiliary(sheets, core.CRITERIA_WEIGHT_SHEET_NAMES)
        if weights is None:
            raise ValueError('Add Criteria_Weights with Criterion and Weight columns.')
        cc = core.get_column_by_alias(weights, core.CRITERION_ALIASES | {'name'})
        wc = core.get_column_by_alias(weights, core.WEIGHT_ALIASES)
        if cc is None or wc is None:
            raise ValueError('Criteria_Weights requires Criterion and Weight columns.')
        ids = labels(weights[cc], 'Criterion')
        if ids.duplicated().any() or set(ids)!=set(crits):
            raise ValueError('Supply exactly one weight for every criterion.')
        if any(number(v, 'Criterion weight') <= 0 for v in weights[wc]):
            raise ValueError('Criterion weights must be positive.')
        types = auxiliary(sheets, core.CRITERIA_TYPE_SHEET_NAMES)
        if types is not None:
            cc = core.get_column_by_alias(types, core.CRITERION_ALIASES | {'name'})
            tc = core.get_column_by_alias(types, core.TYPE_ALIASES)
            if cc is None or tc is None:
                raise ValueError('Criteria_Types requires Criterion and Type columns.')
            ids = labels(types[cc], 'Criterion')
            if ids.duplicated().any() or set(ids)!=set(crits):
                raise ValueError('Supply one type for every criterion, or omit Criteria_Types.')
            if not types[tc].astype(str).str.strip().str.lower().isin(['benefit','cost']).all():
                raise ValueError('Criterion types must be Benefit or Cost.')
    return sheets

def geometry_diagnostics(result):
    m = result['matrices']
    centers = np.stack([m[k].to_numpy() for k in ['aggregated_T','aggregated_I','aggregated_F','radius_r']],axis=-1)
    count = 0
    for x in centers.reshape(-1,4):
        for scenario in core.optimistic_pessimistic(x):
            count += int(np.sum(scenario[:3]**2)>1+1e-12)
    return {'scenario_triples_outside_unit_sphere':count,'scenario_triples_total':int(2*centers.shape[0]*centers.shape[1])}

def calculate(data, module, p=.5, radius_policy='max', lambda_value=.5):
    if module not in ['swara','cocoso'] or radius_policy not in ['max','min']:
        raise ValueError('Unknown calculation module or radius policy.')
    number(p,'p',high=1);number(lambda_value,'lambda',high=1)
    validate_input(data,module)
    result = core.calculate_csf_swara(BytesIO(data),p,radius_policy) if module=='swara' else core.calculate_csf_cocoso(BytesIO(data),p,lambda_value,radius_policy)
    metadata={'software':'CSF Research App','version':VERSION,'method':'Author implementation (unchanged equations)','module':module,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'input_sha256':hashlib.sha256(data).hexdigest(),'parameters':{'p':p,'radius_policy':radius_policy,**({'lambda':lambda_value} if module=='cocoso' else {})},'dependencies':{n:version(n) for n in ['numpy','pandas','openpyxl','streamlit']},'synthetic_demo':False}
    if module=='cocoso':metadata['diagnostics']=geometry_diagnostics(result)
    return result,metadata

def export(result,metadata,module):
    raw=core.export_swara_results(result) if module=='swara' else core.export_cocoso_results(result)
    stream=BytesIO(raw)
    with pd.ExcelWriter(stream,engine='openpyxl',mode='a') as writer:
        pd.DataFrame([{'Field':k,'Value':json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else str(v)} for k,v in metadata.items()]).to_excel(writer,sheet_name='Run_Metadata',index=False)
    return stream.getvalue()
