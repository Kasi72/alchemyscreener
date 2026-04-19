# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║            ALCHEMY SCREENER v4.0 ULTRA — WORLD'S BEST MULTIBAGGER ENGINE        ║
║                                                                                  ║
║  COMPLETE REIMAGINATION — Built on ALL peer-reviewed research:                  ║
║                                                                                  ║
║  ACADEMIC FOUNDATIONS:                                                           ║
║  [Y] Yartseva 2025 (BCU CAFÉ #33) — 464 US multibaggers 2009-2024              ║
║      ★ FCF/P β=46–82 = #1 predictor  ★ B/M β=7–42                             ║
║      ★ Investment Dummy (AssetGrowth>EBITDAgrowth) β=−5 to −23                 ║
║      ★ ROA (not EBITDA margin) in dynamic specs  ★ Price-near-52WLow signal    ║
║      ★ Rising Fed rate → −10pp on multibagger returns                           ║
║  [G] Gunasekaran/IJCRT 2024 — 503 NSE+BSE multibaggers                        ║
║      ★ D/E β=0.4586, p=5.28e-19 (STRONGEST India predictor)                   ║
║      ★ P/FCF p=1.53e-12  ★ ROCE p=7.13e-5  ★ PAT CAGR p=1.57e-4             ║
║      ★ Historical PE p=3.40e-22 (HIGHEST in India)                             ║
║  [A] AQR Quality-Minus-Junk — Asness, Frazzini, Pedersen 2019                 ║
║      ★ Profitability(25%) Growth(25%) Safety(25%) Payout(25%)                  ║
║  [F] Fama-French 5-Factor (2015): SMB, HML, RMW, CMA                          ║
║  [M] Mayer "100 Baggers" (2018): ROIC × Reinvestment Rate; Coffee-can          ║
║  [L] Lynch GARP: PEG < 1.0; "simple boring business"                           ║
║  [P] Piotroski F-Score (2000): Alta Fox — 88% multibaggers had F≥7             ║
║  [O] O'Neil CANSLIM: EPS acceleration + institutional buying                   ║
║  [JT] Jegadeesh-Titman (1993): 6-month momentum reversal for multibaggers      ║
║  [B] Buffett: Moat (ROIC consistency), Owner-operator, Asset-light             ║
║                                                                                  ║
║  NEW IN v4.0:                                                                    ║
║  ✦ P4 Capital Discipline: Yartseva Investment Pattern Guard (key finding)       ║
║  ✦ Altman Z-Score analogue for financial distress detection                     ║
║  ✦ Contrarian Entry Score — stocks near 52-wk low score HIGHER [Y]             ║
║  ✦ Smart Moat Detection — ROIC consistency, gross margin stability              ║
║  ✦ DuPont Analysis — decomposes ROIC into margin × asset turnover              ║
║  ✦ EV/Sales as secondary value signal [Y]                                       ║
║  ✦ Shareholder Yield (FCF Yield + Div Yield)                                   ║
║  ✦ Cash ROIC (FCF/Capital) — AQR quality metric                                ║
║  ✦ 9 disqualifier tripwires vs 5 in v3.1                                       ║
║  ✦ Dual bonus system: Yartseva Compounder + Twin Engine                        ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
import io, math, warnings, json, logging
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st
try:
    import yfinance as yf
    _YF_OK = True
except ImportError:
    _YF_OK = False

try:
    _JGD_IMPORT_ERR = None
    try:
        from jugaad_data.nse import stock_df as _jgd_stock_df
    except Exception:
        from jugaad_data.stock import stock_df as _jgd_stock_df  # older package layouts
    try:
        from jugaad_data.nse import NSELive as _JGD_NSELive
    except Exception:
        _JGD_NSELive = None
    _JGD_OK = True
except Exception as _jgd_e:
    _JGD_OK = False
    _JGD_IMPORT_ERR = str(_jgd_e)
    _jgd_stock_df = None
    _JGD_NSELive = None

import time, re as _re, threading
from datetime import date as _date, timedelta as _timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    import requests
    from bs4 import BeautifulSoup as _BS
    _SCR_OK = True
except ImportError:
    _SCR_OK = False
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")
pd.options.display.float_format = "{:.2f}".format
np.seterr(all="ignore")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
LOGGER = logging.getLogger("alchemy_screener")


# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚗️ Alchemy v4.0 Ultra",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# CSS — DARK GOLD THEME
# ──────────────────────────────────────────────────────────────────────────────
APP_CSS = r"""
<style>
:root {
    --gold: #ffd700; --silver: #c0c0c0; --bronze: #cd7f32;
    --blue: #4a9eff; --green: #00e676; --orange: #ff9800;
    --red: #ff4757; --bg: #0d1117; --card: #161b22; --border: #21262d;
}
.block-container{max-width:100%!important;padding:1.2rem 1.4rem 2.25rem!important}
section[data-testid="stSidebar"]{min-width:360px;max-width:500px;background:#0a0e14;border-right:1px solid var(--border)}
section[data-testid="stSidebar"] .block-container{padding-top:1rem!important;padding-left:1rem!important;padding-right:1rem!important}
.main-header-wrap{background:linear-gradient(180deg,rgba(22,27,34,.95),rgba(13,17,23,.92));border:1px solid var(--border);border-radius:18px;padding:16px 18px 14px;margin:0 0 12px 0;box-shadow:0 6px 18px rgba(0,0,0,.28)}
.main-header{font-size:clamp(1.9rem,2.35vw,2.55rem);font-weight:900;line-height:1.18;margin:0 0 6px 0;padding-top:2px;background:linear-gradient(135deg,#ffd700 0%,#ff8c00 40%,#4a9eff 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-0.4px;overflow:visible}
.sub-header{color:#97a8c0;font-size:.9rem;line-height:1.55;margin:0;max-width:1180px}
.hero-card{background:linear-gradient(180deg,rgba(22,27,34,.96),rgba(15,23,34,.96));border-radius:16px;padding:18px 22px;border:1px solid var(--border);
    margin-bottom:10px;box-shadow:0 4px 12px rgba(0,0,0,.28)}
.metric-card{background:var(--card);border-radius:14px;padding:16px 18px;border:1px solid var(--border);
    margin-bottom:10px;box-shadow:0 4px 12px rgba(0,0,0,.32)}
.tier1{border-left:4px solid var(--gold)!important;background:linear-gradient(135deg,#1f1800 0%,var(--card) 100%)}
.tier2{border-left:4px solid var(--silver)!important}
.tier3{border-left:4px solid var(--bronze)!important}
.tier4{border-left:4px solid var(--orange)!important}
.tier5{border-left:4px solid var(--red)!important}
.score-mega{font-size:3.5rem;font-weight:900;letter-spacing:-2px}
.t1-score{color:var(--gold)} .t2-score{color:var(--silver)} .t3-score{color:var(--bronze)}
.t4-score{color:var(--orange)} .t5-score{color:var(--red)}
.pillar-lbl{font-size:.75rem;font-weight:700;color:#8b9ab0;text-transform:uppercase;letter-spacing:.5px}
.pillar-val{font-size:1.5rem;font-weight:800}
.sig-good{color:var(--green);font-size:.78rem;font-weight:600}
.sig-warn{color:var(--orange);font-size:.78rem;font-weight:600}
.sig-bad{color:var(--red);font-size:.78rem;font-weight:600}
.disq-pill{background:#2a0808;color:#ff6b6b;border-radius:6px;padding:2px 9px;
    font-size:.75rem;font-weight:700;border:1px solid #ff3333;margin-right:4px}
.entry-badge{background:#0a2a0a;color:var(--green);border-radius:8px;padding:4px 10px;
    font-size:.8rem;font-weight:700;border:1px solid #00c853}
.warn-badge{background:#2a1a00;color:var(--orange);border-radius:8px;padding:4px 10px;
    font-size:.8rem;font-weight:700;border:1px solid #ff8c00}
.stTabs [data-baseweb="tab"]{font-weight:700;font-size:.88rem;padding:8px 20px}
div.stButton>button{border-radius:10px;font-weight:800;
    background:linear-gradient(135deg,#1a3a5a,#0d2040);color:var(--blue);
    border:1px solid var(--blue);font-size:.9rem;letter-spacing:.3px}
div.stButton>button:hover{background:linear-gradient(135deg,#4a9eff,#1a3a5a);color:white}
.research-pill{background:#0a1a2a;color:var(--blue);border-radius:4px;padding:1px 6px;
    font-size:.7rem;font-weight:600;border:1px solid #1a3a5a;margin-left:3px}
.yartseva-pill{background:#1a1a00;color:#ffd700;border-radius:4px;padding:1px 6px;
    font-size:.7rem;font-weight:600;border:1px solid #666600;margin-left:3px}
.section-title{font-size:1rem;font-weight:800;color:#ccc;margin:12px 0 6px;padding-left:3px;
    border-left:3px solid var(--blue)}
.score-bar-bg{background:#21262d;border-radius:6px;height:8px;overflow:hidden}
.score-bar-fill{height:8px;border-radius:6px;background:linear-gradient(90deg,#4a9eff,#00e676)}
.insight-box{background:#0d1f2d;border-radius:10px;padding:12px 16px;border:1px solid #1a3a5a;
    font-size:.82rem;color:#aac4d8;margin:6px 0}
.finding-box{background:#1a1a00;border-radius:10px;padding:12px 16px;border:1px solid #666600;
    font-size:.82rem;color:#d4c87a;margin:6px 0}
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

_YF_ISSUES: List[str] = []
_YF_ISSUE_LOCK = threading.Lock()

def clear_yf_issues() -> None:
    with _YF_ISSUE_LOCK:
        _YF_ISSUES.clear()

def _add_yf_issue(message: str) -> None:
    if not message:
        return
    with _YF_ISSUE_LOCK:
        if message not in _YF_ISSUES and len(_YF_ISSUES) < 12:
            _YF_ISSUES.append(message)

def log_yf_issue(context: str, sym: Optional[str] = None, exc: Optional[Exception] = None,
                 user_message: Optional[str] = None) -> None:
    prefix = f"[{sym}] " if sym else ""
    if exc is not None:
        LOGGER.warning("%s%s: %s", prefix, context, exc)
    else:
        LOGGER.warning("%s%s", prefix, context)
    if user_message:
        _add_yf_issue(f"{prefix}{user_message}")

def render_yf_issues() -> None:
    if not _YF_ISSUES:
        return
    lines = "\n".join(f"• {msg}" for msg in _YF_ISSUES[:8])
    st.warning(
        "⚠️ Yahoo Finance had partial fetch issues. Fallback sources were used where possible.\n"
        + lines
    )

def _safe_yf_ticker(sym: str, context: str):
    if not _YF_OK:
        log_yf_issue(context, sym=sym, user_message="yfinance is not installed on this environment.")
        return None
    try:
        query = _clean_identifier(sym)
        if not query:
            return None
        uq = query.upper()
        if uq.endswith((".NS", ".BO")) or _is_isin_like(uq):
            yf_query = query
        else:
            base = _normalise_symbol_base(query)
            yf_query = base + ".NS"
        return yf.Ticker(yf_query)
    except Exception as exc:
        log_yf_issue(context, sym=sym, exc=exc,
                     user_message="Could not initialize Yahoo Finance ticker; using fallback sources.")
        return None

def _safe_yf_info(ticker, sym: str, context: str) -> dict:
    if ticker is None:
        return {}
    try:
        return ticker.info or {}
    except Exception as exc:
        log_yf_issue(context, sym=sym, exc=exc,
                     user_message="Yahoo Finance fundamentals were unavailable; using fallback sources.")
        return {}

def _safe_yf_fast_info(ticker, sym: str, context: str):
    if ticker is None:
        return None
    try:
        return ticker.fast_info
    except Exception as exc:
        log_yf_issue(context, sym=sym, exc=exc,
                     user_message="Yahoo Finance fast price info was unavailable; 52-week fields may be partial.")
        return None

def _safe_yf_history(ticker, sym: str, context: str, **kwargs) -> pd.DataFrame:
    if ticker is None:
        return pd.DataFrame()
    try:
        hist = ticker.history(**kwargs)
        return hist if isinstance(hist, pd.DataFrame) else pd.DataFrame()
    except Exception as exc:
        log_yf_issue(context, sym=sym, exc=exc,
                     user_message="Yahoo Finance price history was unavailable; entry signals may be partial.")
        return pd.DataFrame()

def _safe_yf_frame(ticker, attr_name: str, sym: str, context: str) -> pd.DataFrame:
    if ticker is None:
        return pd.DataFrame()
    try:
        frame = getattr(ticker, attr_name)
        return frame if isinstance(frame, pd.DataFrame) else pd.DataFrame(frame)
    except Exception as exc:
        log_yf_issue(context, sym=sym, exc=exc,
                     user_message=f"Yahoo Finance {attr_name} data was unavailable; some fundamentals may be partial.")
        return pd.DataFrame()


_STATE_HEAVY_COLS = [
    "P1_Detail", "P2_Detail", "P3_Detail", "P4_Detail", "P5_Detail", "P6_Detail",
    "ALL_SIGNALS",
]

_STATE_PREVIEW_COLS = [
    "Rank", "Name", "NSE Code", "Industry", "SCORE_V40", "TIER_V40",
    "Entry_Signal", "DISQ", "Fundamental_Score", "Entry_Bonus",
]

def _read_uploaded_csv(uploaded_file, *, thousands=",") -> pd.DataFrame:
    """Safely read a Streamlit UploadedFile across reruns without pointer-exhaustion."""
    if uploaded_file is None:
        return pd.DataFrame()
    raw = None
    try:
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
    except Exception:
        pass
    try:
        raw = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    except Exception:
        raw = None
    if raw is None:
        raise ValueError("Could not read uploaded file bytes")
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if len(raw) == 0:
        raise ValueError("Uploaded file is empty")
    df = pd.read_csv(io.BytesIO(raw), thousands=thousands)
    df.columns = df.columns.str.strip()
    return df


def _compact_results_for_state(df: pd.DataFrame, *, preview_only: bool = False, top_n: Optional[int] = None) -> pd.DataFrame:
    """Trim bulky per-row diagnostics before persisting to session_state."""
    if df is None:
        return None
    slim = df.drop(columns=[c for c in _STATE_HEAVY_COLS if c in df.columns], errors="ignore").copy()
    if preview_only:
        keep = [c for c in _STATE_PREVIEW_COLS if c in slim.columns]
        if keep:
            slim = slim[keep].copy()
    if top_n is not None and len(slim) > top_n:
        slim = slim.head(top_n).copy()
    try:
        slim.attrs = {
            k: v for k, v in getattr(df, "attrs", {}).items()
            if isinstance(v, (str, int, float, bool, type(None)))
        }
    except Exception:
        pass
    return slim


_SIDEBAR_STATUS_PLACEHOLDER = None


def _status_box_html(msg: str) -> str:
    safe = str(msg or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        "<div style='border:1px solid #2a3442;border-radius:10px;padding:10px 12px;"
        "background:#0d1117;color:#cbd5e1;font-size:.84rem;line-height:1.45;"
        "white-space:pre-wrap;min-height:128px'>"
        + safe +
        "</div>"
    )


def _set_run_status(message: str) -> None:
    global _SIDEBAR_STATUS_PLACEHOLDER
    try:
        msg = str(message or "")
        st.session_state["alchemy_sidebar_status"] = msg
        if _SIDEBAR_STATUS_PLACEHOLDER is not None:
            _SIDEBAR_STATUS_PLACEHOLDER.markdown(_status_box_html(msg), unsafe_allow_html=True)
    except Exception:
        pass


def _render_run_status_box() -> None:
    global _SIDEBAR_STATUS_PLACEHOLDER
    msg = str(st.session_state.get("alchemy_sidebar_status", "Ready — upload files and run the engine."))
    st.markdown("#### 📝 Run Status")
    _SIDEBAR_STATUS_PLACEHOLDER = st.empty()
    _SIDEBAR_STATUS_PLACEHOLDER.markdown(_status_box_html(msg), unsafe_allow_html=True)


_IDENTIFIER_COLS = [
    "NSE Code", "NSE Symbol", "Symbol", "Ticker", "Security Id", "Security ID",
    "BSE Code", "BSE Symbol", "Scrip Code", "Security Code", "Code",
    "ISIN Code", "ISIN", "ISIN No", "ISIN Number", "Name",
]


def _clean_identifier(value) -> str:
    if value is None:
        return ""
    s = str(value).strip()
    if not s or s.lower() in {"nan", "none", "null", "n/a", "na", "-", "--"}:
        return ""
    return s


def _is_isin_like(value: str) -> bool:
    s = _clean_identifier(value).upper()
    return bool(_re.fullmatch(r"[A-Z]{2}[A-Z0-9]{9}\d", s))


def _is_probable_bse_code(value: str) -> bool:
    s = _clean_identifier(value)
    return bool(_re.fullmatch(r"\d{4,6}", s))


def _normalise_symbol_base(value: str) -> str:
    s = _clean_identifier(value).upper().replace(" ", "")
    s = s.replace("-EQ", "")
    if s.endswith(".NS") or s.endswith(".BO"):
        s = s[:-3]
    return s.strip(".")


def _row_identifiers(row_d: dict) -> dict:
    bundle = {}
    if not isinstance(row_d, dict):
        return bundle
    for col in _IDENTIFIER_COLS:
        if col in row_d:
            val = _clean_identifier(row_d.get(col))
            if val:
                bundle[col] = val
    return bundle


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        key = _clean_identifier(item)
        if not key:
            continue
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


@st.cache_data(show_spinner=False, ttl=86400)
def _search_yf_symbol_candidates(query: str) -> List[str]:
    query = _clean_identifier(query)
    if not query or not _YF_OK:
        return []
    try:
        search_obj = getattr(yf, "Search", None)
        if search_obj is None:
            return []
        search = search_obj(query, max_results=8)
        quotes = getattr(search, "quotes", None) or []
        candidates = []
        for q in quotes:
            try:
                raw_sym = _clean_identifier(q.get("symbol"))
                if not raw_sym:
                    continue
                exch = " ".join([
                    _clean_identifier(q.get("exchange")),
                    _clean_identifier(q.get("exchangeDisp")),
                    _clean_identifier(q.get("fullExchangeName")),
                ]).lower()
                qtype = _clean_identifier(q.get("quoteType") or q.get("type")).lower()
                if qtype and qtype not in {"equity", "etf", "mutualfund", "fund"}:
                    continue
                upper_sym = raw_sym.upper()
                if upper_sym.endswith((".NS", ".BO")):
                    candidates.append(upper_sym)
                    continue
                base = _normalise_symbol_base(upper_sym)
                if "bombay" in exch or "bse" in exch:
                    if _is_probable_bse_code(base):
                        candidates.append(base.zfill(6) + ".BO")
                    else:
                        candidates.append(base + ".BO")
                if "national" in exch or "nse" in exch or "india" in exch:
                    candidates.append(base + ".NS")
                candidates.append(base)
            except Exception:
                continue
        return _dedupe_keep_order(candidates)
    except Exception:
        return []


def _ticker_candidates_from_identifiers(bundle: dict) -> List[str]:
    bundle = bundle or {}
    cands: List[str] = []

    def _add_nse(value: str):
        base = _normalise_symbol_base(value)
        if base and not _is_isin_like(base):
            cands.append(base + ".NS")
            cands.append(base)

    def _add_bse(value: str):
        base = _normalise_symbol_base(value)
        if not base or _is_isin_like(base):
            return
        if _is_probable_bse_code(base):
            base = base.zfill(6)
        cands.append(base + ".BO")
        cands.append(base)

    for key in ("NSE Code", "NSE Symbol", "Symbol", "Ticker", "Security Id", "Security ID"):
        val = bundle.get(key)
        if val:
            _add_nse(val)
    for key in ("BSE Code", "BSE Symbol", "Scrip Code", "Security Code"):
        val = bundle.get(key)
        if val:
            _add_bse(val)

    generic_code = bundle.get("Code")
    if generic_code:
        if _is_probable_bse_code(generic_code):
            _add_bse(generic_code)
        else:
            _add_nse(generic_code)

    for key in ("ISIN Code", "ISIN", "ISIN No", "ISIN Number"):
        val = bundle.get(key)
        if val and _is_isin_like(val):
            cands.extend(_search_yf_symbol_candidates(val))

    if not cands:
        name_q = bundle.get("Name")
        if name_q:
            cands.extend(_search_yf_symbol_candidates(name_q))

    return _dedupe_keep_order(cands)


def _resolve_lookup_targets(bundle: dict) -> dict:
    bundle = bundle or {}
    cands = _ticker_candidates_from_identifiers(bundle)
    out = {"yf_candidates": cands, "nse_symbol": "", "bse_code": ""}
    for cand in cands:
        uc = _clean_identifier(cand).upper()
        base = _normalise_symbol_base(uc)
        if uc.endswith(".NS") and not out["nse_symbol"] and base and not _is_probable_bse_code(base):
            out["nse_symbol"] = base
        if uc.endswith(".BO") and not out["bse_code"] and _is_probable_bse_code(base):
            out["bse_code"] = base.zfill(6)
    if not out["nse_symbol"]:
        for key in ("NSE Code", "NSE Symbol", "Symbol", "Ticker", "Security Id", "Security ID"):
            val = bundle.get(key)
            if val and not _is_probable_bse_code(val) and not _is_isin_like(val):
                out["nse_symbol"] = _normalise_symbol_base(val)
                break
    if not out["bse_code"]:
        for key in ("BSE Code", "Scrip Code", "Security Code", "Code"):
            val = bundle.get(key)
            if val and _is_probable_bse_code(val):
                out["bse_code"] = _normalise_symbol_base(val).zfill(6)
                break
    if not out["nse_symbol"] and bundle.get("Name"):
        searched = _search_yf_symbol_candidates(bundle.get("Name"))
        for cand in searched:
            uc = cand.upper()
            base = _normalise_symbol_base(uc)
            if uc.endswith(".NS"):
                out["nse_symbol"] = base
                break
    if not out["bse_code"] and bundle.get("Name"):
        searched = _search_yf_symbol_candidates(bundle.get("Name"))
        for cand in searched:
            uc = cand.upper()
            base = _normalise_symbol_base(uc)
            if uc.endswith(".BO") and _is_probable_bse_code(base):
                out["bse_code"] = base.zfill(6)
                break
    return out

# ──────────────────────────────────────────────────────────────────────────────
# SCIENTIFIC WEIGHT MATRIX  — v4.0 Ultra
# ──────────────────────────────────────────────────────────────────────────────
# Pillar architecture: 6 pillars (added P4 Capital Discipline)
# P3 Value elevated: FCF/P β=46-82 [Y] is the WORLD'S #1 predictor found empirically

DEFAULT_PILLAR_W: Dict[str, float] = {
    "P1_Quality":      20,   # ROIC+ROCE+ROA+FCFq+Moat; [G] ROCE p=7.13e-5; [A] AQR
    "P2_Growth":       15,   # PAT CAGR 5Y; Accel; RevCAGR demoted [G] p=0.164 NOT sig
    "P3_Value":        28,   # FCF/P #1 [Y][G]; B/M [Y]; PE_Hist p=3.40e-22 [G]
    "P4_Discipline":   13,   # NEW: Yartseva Investment Pattern Guard (central finding)
    "P5_Size":          7,   # SMB [F]; India small-cap discovery alpha
    "P6_Safety":       17,   # D/E β=0.4586 p=5.28e-19 [G]; Piotroski [P]; Pledge India
}

CONFIG_FILE_CANDIDATES = [
    Path(__file__).with_name("config.yaml") if "__file__" in globals() else Path("config.yaml"),
    Path.cwd() / "config.yaml",
]

def _resolve_config_path() -> Path:
    for candidate in CONFIG_FILE_CANDIDATES:
        if candidate.exists():
            return candidate
    return CONFIG_FILE_CANDIDATES[0]

def _load_weight_config(default_weights: Dict[str, float]) -> Dict[str, float]:
    cfg_path = _resolve_config_path()
    if yaml is None or not cfg_path.exists():
        LOGGER.info("Weight config not loaded; using in-code defaults from %s", cfg_path)
        return dict(default_weights)
    try:
        raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        weights = raw.get("weights", {}) if isinstance(raw, dict) else {}
        cleaned = {}
        for key, default_val in default_weights.items():
            val = weights.get(key, default_val)
            try:
                cleaned[key] = float(val)
            except Exception:
                cleaned[key] = float(default_val)
        if sum(cleaned.values()) <= 0:
            raise ValueError("Weight sum must be positive")
        LOGGER.info("Loaded pillar weights from %s", cfg_path)
        return cleaned
    except Exception as exc:
        LOGGER.warning("Failed to load %s; using defaults. Error: %s", cfg_path, exc)
        return dict(default_weights)

DEFAULT_PILLAR_W = _load_weight_config(DEFAULT_PILLAR_W)


# ── P1 QUALITY SUB-WEIGHTS ────────────────────────────────────────────────────
# [Y] ROA significant in ALL dynamic specs; EBITDA margin drops out dynamically
P1_SUB: Dict[str, float] = {
    "roic":     0.28,  # [M] McKinsey: ROIC>WACC compounds; [Y] quality proxy
    "roce":     0.25,  # [G] p=7.13e-5 — most significant India quality signal
    "roa":      0.18,  # [Y] Yartseva: ROA in ALL dynamic models β=0.4-1.9
    "fcf_pat":  0.17,  # [A] AQR CFOA; earnings quality; asset-light proxy
    "moat":     0.12,  # [B] ROIC consistency + gross margin = economic moat
}

# ── P2 GROWTH SUB-WEIGHTS ─────────────────────────────────────────────────────
# [Y] WARNING: Earnings growth NOT significant in Yartseva dynamic specs!
# [G] India study: PAT CAGR p=1.57e-4 significant; Rev CAGR p=0.164 NOT sig
P2_SUB: Dict[str, float] = {
    "pat5":     0.38,  # [G] p=1.57e-4; best predictive India growth metric
    "opm_exp":  0.28,  # Margin EXPANSION trend (not level); [G] OPM p=0.008
    "accel":    0.20,  # [O] CANSLIM C+A: TTM acceleration vs 5Y baseline
    "rev5":     0.08,  # [G] NOT sig p=0.164 → demoted; India revenue growth noisy
    "reinv":    0.06,  # [M] Mayer: ROIC × Reinv Rate = intrinsic growth floor
}

# ── P3 VALUE SUB-WEIGHTS ──────────────────────────────────────────────────────
# [Y] FCF/P THE single dominant predictor (β=46-82); B/M β=7-42 significant
P3_SUB: Dict[str, float] = {
    "fcfy":     0.40,  # [Y][G] #1 predictor globally; FCF Yield = FCF/MarketCap
    "bm":       0.18,  # [Y] B/M β=7-42; undervaluation proxy; Fama-French HML
    "pe_hist":  0.20,  # [G] Hist PE p=3.40e-22 HIGHEST significance India study
    "ev_eb":    0.12,  # [Y] EV/EBITDA significant in within-FE models
    "ev_sales": 0.06,  # [Y] EV/Sales sig in Model 3; secondary valuation check
    "peg":      0.04,  # [L] Lynch GARP; demoted since [Y] shows PE not best proxy
}

# ── P4 CAPITAL DISCIPLINE SUB-WEIGHTS ─────────────────────────────────────────
# NEW PILLAR — The Yartseva "Investment Pattern" — single most unique finding
# β of investment dummy = −5 to −23 across ALL model specs [Y]
P4_SUB: Dict[str, float] = {
    "inv_guard":    0.50,  # [Y] CORE: asset_growth ≤ EBITDA_growth → sustainable invest
    "capex_eff":    0.22,  # Capex intensity vs revenue; asset-light moat
    "cash_conv":    0.16,  # CFO/EBITDA — cash conversion quality
    "shreholder":   0.12,  # Shareholder yield: FCF yield + dividend yield together
}

# ── P5 SIZE SUB-WEIGHTS ───────────────────────────────────────────────────────
P5_SUB: Dict[str, float] = {
    "mcap":     0.50,  # [F] SMB factor; India: <2000Cr optimal discovery window
    "inst_gap": 0.30,  # Under-coverage → mispricing → alpha; [O] CANSLIM I
    "float":    0.20,  # Tight float with high promoter conviction
}

# ── P6 SAFETY SUB-WEIGHTS ─────────────────────────────────────────────────────
# D/E single strongest predictor in India study [G]; Piotroski validated [P]
P6_SUB: Dict[str, float] = {
    "de":       0.35,  # [G] D/E β=0.4586, p=5.28e-19 — DOMINANT India predictor
    "pio":      0.24,  # [P] Alta Fox: 88% multibaggers had Piotroski ≥7 at entry
    "intcov":   0.14,  # Interest coverage ≥3; [A] AQR safety sub-score
    "pledge":   0.16,  # India-specific catastrophe signal — governance red flag
    "prom_fii": 0.11,  # Insider conviction: promoter + institutional trend
}

# ── SECTOR ROCE BENCHMARKS (India) ───────────────────────────────────────────
SECT_ROCE: Dict[str, float] = {
    "software": 25, "it services": 25, "technology": 22,
    "pharmaceuticals": 21, "healthcare": 20, "hospital": 18,
    "chemicals": 19, "specialty chemicals": 21, "agrochemicals": 18,
    "fmcg": 32, "consumer": 22, "retail": 16, "food": 17,
    "bank": 9, "nbfc": 10, "insurance": 13, "financial": 12,
    "auto ancillary": 17, "auto": 18, "tyres": 16, "ev": 14,
    "steel": 14, "metals": 13, "mining": 15, "cement": 18,
    "power": 13, "energy": 14, "renewables": 12, "solar": 13,
    "telecom": 10, "media": 14, "infra": 12, "construction": 14,
    "hospitality": 13, "aviation": 10, "logistics": 15,
    "paper": 14, "textile": 13, "packaging": 15, "agri": 15,
    "defence": 18, "electronics": 16, "capital goods": 16,
    "real estate": 12, "default": 15,
}

SECT_GROSS_MARGIN: Dict[str, float] = {
    "software": 70, "it services": 65, "pharmaceuticals": 55, "chemicals": 40,
    "fmcg": 45, "consumer": 38, "bank": 40, "nbfc": 50,
    "auto": 25, "auto ancillary": 30, "steel": 20, "cement": 35,
    "power": 35, "healthcare": 50, "default": 35,
}


# ──────────────────────────────────────────────────────────────────────────────
# MATH HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def fv(x) -> float:
    try:
        v = float(x)
        return v if np.isfinite(v) else np.nan
    except:
        return np.nan

# ok() removed (Bug 19 audit fix — was never called; ok2() handles all checks)

def ok2(x) -> bool:
    v = fv(x)
    return not np.isnan(v)

def first_num(d: dict, keys) -> float:
    """Return first finite numeric value from a dict across alias keys."""
    for k in keys:
        try:
            v = fv(d.get(k))
            if np.isfinite(v):
                return v
        except Exception:
            pass
    return np.nan

def df_first_numeric(df: pd.DataFrame, cols) -> pd.Series:
    """Return first available numeric series across alias columns, aligned to df.index."""
    out = pd.Series(np.nan, index=df.index, dtype=float)
    for c in cols:
        if c in df.columns:
            s = pd.to_numeric(df[c], errors="coerce")
            out = out.where(out.notna(), s)
    return out

def pct(x) -> float:
    """Convert decimal to % if abs < 2, else pass-through."""
    if not ok2(x): return np.nan
    v = fv(x)
    return v * 100 if abs(v) < 2 else v

def log_s(val: float, z: float, o: float, cap: float = 10.0) -> float:
    """Logarithmic score [0,cap] with diminishing returns. z=zero, o=optimal."""
    if not ok2(val): return cap / 2
    v = fv(val)
    if v <= z: return 0.0
    if v >= o: return cap
    try:
        return float(np.clip(
            math.log(max(v - z + 1e-9, 1e-9)) / math.log(max(o - z + 1e-9, 1e-9)) * cap,
            0, cap))
    except:
        return 0.0

def lin_s(val: float, z: float, o: float, cap: float = 10.0) -> float:
    """Linear score [0,cap]."""
    if not ok2(val): return cap / 2
    v = fv(val)
    if z == o: return 0.0
    return float(np.clip((v - z) / (o - z) * cap, 0, cap))

def inv_s(val: float, best: float, worst: float, cap: float = 10.0) -> float:
    """Lower is better scoring — maps [best,worst] → [cap,0]."""
    if not ok2(val): return cap / 2
    v = fv(val)
    if v <= best: return cap
    if v >= worst: return 0.0
    return float(np.clip((worst - v) / (worst - best) * cap, 0, cap))

def sect_roce(industry: str) -> float:
    if not industry or str(industry) == "nan": return 15
    il = str(industry).lower()
    for k, v in SECT_ROCE.items():
        if k in il: return v
    return 15

def sect_gm(industry: str) -> float:
    if not industry or str(industry) == "nan": return 35
    il = str(industry).lower()
    for k, v in SECT_GROSS_MARGIN.items():
        if k in il: return v
    return 35

_FINANCIAL_SECTOR_KEYS = (
    "bank", "nbfc", "insurance", "financial", "finance", "lender",
    "housing finance", "microfinance", "asset management", "broker",
    "broking", "capital market", "wealth", "amc"
)

def is_financial_sector(industry: str) -> bool:
    il = str(industry or "").strip().lower()
    return any(k in il for k in _FINANCIAL_SECTOR_KEYS)


def sanitize_fcf_yield_pct(fcfy: float) -> float:
    """Sanity-clean equity FCF yield while preserving meaningful negative values."""
    if not ok2(fcfy):
        return np.nan
    v = fv(fcfy)
    # Extremely large positive or negative values are almost always bad source data.
    if v > 50 or v < -100:
        return np.nan
    return v


def compute_fcf_yield_pct(r: dict, return_basis: bool = False):
    """
    Canonical equity FCF yield.
    Preference order:
      1) TTM FCF / Market Cap
      2) Latest annual FCF / Market Cap
      3) Direct precomputed yield
      4) Vendor P/FCF inverse

    For financials (banks/NBFCs/insurers/etc.), return NaN because FCF yield is
    not an apples-to-apples primary valuation metric under international norms.
    """
    industry = str(r.get("Industry", "") or "")
    if is_financial_sector(industry):
        return (np.nan, "N/A_FINANCIAL") if return_basis else np.nan

    mcap = fv(r.get("Market Capitalization"))
    fcf_ttm = fv(r.get("Free cash flow TTM"))
    fcf_last = fv(r.get("Free cash flow last year"))
    fcfy_direct = fv(r.get("_FCFYield_Direct"))
    pfcf = fv(r.get("Price to Free Cash Flow"))

    fcfy = np.nan
    basis = "NA"
    if ok2(fcf_ttm) and ok2(mcap) and mcap > 0:
        fcfy = fcf_ttm / mcap * 100
        basis = "TTM_FCF/MarketCap"
    elif ok2(fcf_last) and ok2(mcap) and mcap > 0:
        fcfy = fcf_last / mcap * 100
        basis = "Annual_FCF/MarketCap"
    elif ok2(fcfy_direct):
        fcfy = fcfy_direct
        basis = "DirectYield"
    elif ok2(pfcf) and pfcf != 0:
        fcfy = 100.0 / pfcf
        basis = "Vendor_P/FCF"

    fcfy = sanitize_fcf_yield_pct(fcfy)
    return (fcfy, basis) if return_basis else fcfy


# ──────────────────────────────────────────────────────────────────────────────
# P1: QUALITY SCORING  (20%)
# ROIC(28%) ROCE(25%) ROA(18%) FCF/PAT(17%) Moat(12%)
# Key research: [Y] ROA in all dynamic models; [G] ROCE p=7.13e-5; [A] AQR
# ──────────────────────────────────────────────────────────────────────────────

def p1_quality(r: dict) -> Tuple[float, List[str], dict]:
    sigs, detail = [], {}
    ind = str(r.get("Industry", "default"))

    # ── ROIC ── [M] McKinsey gold standard; ROIC-WACC spread = moat proxy
    roic = pct(r.get("Return on invested capital"))
    if ok2(roic):
        rs = log_s(roic, 8, 30)  # V5-3: o=30; ROIC=20%→5.0, 30%→6.9, 40%→8.5, 60%→9.5 [Indian multibaggers]
        tag = ("★★★★" if roic >= 35 else "★★★" if roic >= 25 else "★★" if roic >= 15 else "★" if roic >= 10 else "⚠")
        sigs.append(f"ROIC {roic:.1f}%{tag}")
        detail["ROIC"] = {"raw": round(roic, 1), "score": round(rs, 2), "w": P1_SUB["roic"]}
    else:
        rs = 4.5; detail["ROIC"] = {"raw": None, "score": rs, "w": P1_SUB["roic"]}

    # ── ROCE ── [G] p=7.13e-5 sector-adjusted
    roce = pct(r.get("Return on capital employed"))
    sr = sect_roce(ind)
    if ok2(roce):
        xs = roce - sr  # excess over sector median
        rcs = log_s(xs + 8, 0, 18)  # Calibrated: +10pp→6.3, +15pp→7.2 [Indian market]
        tag = ("★★★★" if roce >= 35 else "★★★" if roce >= 25 else "★★" if roce >= 15 else "★" if roce >= 10 else "⚠")
        sigs.append(f"ROCE {roce:.1f}%({xs:+.0f}pp sect){tag}")  # Bug C fix: :+ handles sign
        detail["ROCE"] = {"raw": round(roce, 1), "score": round(rcs, 2), "w": P1_SUB["roce"]}
    else:
        rcs = 4.5; detail["ROCE"] = {"raw": None, "score": rcs, "w": P1_SUB["roce"]}

    # ── ROA ── [Y] Yartseva: ROA in ALL dynamic models β≈0.4-1.9; key quality signal
    pat = fv(r.get("Profit after tax"))
    mcap = fv(r.get("Market Capitalization"))
    # Try to get total assets proxy: equity + debt
    bv = fv(r.get("Book value")); price = fv(r.get("Current Price"))
    de = fv(r.get("Debt to equity"))
    shares = mcap / price if (ok2(mcap) and ok2(price) and price > 0) else None
    equity = bv * shares if (ok2(bv) and shares) else None
    total_debt = equity * de if (ok2(equity) and ok2(de)) else None
    total_assets = (equity + total_debt) if (ok2(equity) and ok2(total_debt)) else None

    if ok2(pat) and ok2(total_assets) and total_assets > 0:
        roa = pat / total_assets * 100
        roa_s = log_s(roa, 2, 12)  # Calibrated: ROA=12%→6.3, 15%→7.3
        tag = "★★★" if roa >= 12 else "★★" if roa >= 7 else "★" if roa >= 3 else "⚠"
        sigs.append(f"ROA {roa:.1f}%{tag}[Yartseva]")
        detail["ROA"] = {"raw": round(roa, 1), "score": round(roa_s, 2), "w": P1_SUB["roa"]}
    else:
        # Fallback: use ROE as proxy for ROA if assets unavailable
        roe = pct(r.get("Return on equity"))
        if ok2(roe):
            # DuPont: ROA = ROE / (1 + D/E); use actual leverage if available
            _de_roa = fv(r.get("Debt to equity"))
            _roa_mult = 1.0 / (1.0 + _de_roa) if ok2(_de_roa) and _de_roa >= 0 else 0.55
            roa_est = roe * _roa_mult
            roa_s = log_s(roa_est, 2, 12)  # Calibrated: same as direct
            detail["ROA"] = {"raw": round(roa_est, 1), "score": round(roa_s, 2), "w": P1_SUB["roa"]}
        else:
            roa_s = 5.0; detail["ROA"] = {"raw": None, "score": roa_s, "w": P1_SUB["roa"]}  # neutral: unknown ROA ≠ bad

    # ── FCF/PAT ── [A] AQR CFOA; asset-light earnings quality
    fcf = fv(r.get("Free cash flow last year"))
    if ok2(fcf) and ok2(pat) and pat != 0:
        ratio = fcf / pat
        if ratio < 0:
            fps = 0.0; sigs.append(f"⚠NegFCF/PAT {ratio:.2f}x(cash burn)")
        elif ratio >= 1.2:
            fps = 10.0; sigs.append(f"FCF/PAT {ratio:.2f}x★★★★ asset-light")
        elif ratio >= 0.85:
            fps = 8.5; sigs.append(f"FCF/PAT {ratio:.2f}x★★★")
        elif ratio >= 0.65:
            fps = 6.5; sigs.append(f"FCF/PAT {ratio:.2f}x★★")
        elif ratio >= 0.4:
            fps = 4.0
        else:
            fps = 1.5; sigs.append(f"⚠FCF/PAT {ratio:.2f}x low")
        detail["FCF/PAT"] = {"raw": round(ratio, 3), "score": round(fps, 2), "w": P1_SUB["fcf_pat"]}
    else:
        fps = 4.5; detail["FCF/PAT"] = {"raw": None, "score": fps, "w": P1_SUB["fcf_pat"]}

    # ── MOAT SCORE ── [B] Buffett: ROIC consistency + gross margin above sector
    # Proxy: Gross Profit Margin vs sector + ROIC premium
    # Bug J fix: removed `npm` and `sg` — shadowed by _npm_moat/_sg_moat below; dead code
    moat_signals = []
    moat_s_base = 4.0   # Bug A fix: always initialised BEFORE the conditional block
    if ok2(roic) and ok2(roce):
        dual_high = (roic >= 20) and (roce >= sect_roce(ind) + 5)
        if dual_high:
            moat_signals.append("DualROIC★★★")
        moat_s_base = log_s((roic + roce) / 2, 10, 30)
    # else: moat_s_base stays 4.0 (neutral) — already initialised above
    # Bug fix: use gross margin vs sector instead of FCF/PAT (avoids double-count with fcf_pat sub-score)
    _npm_moat = pct(r.get("Net profit margin") or r.get("OPM"))
    _sg_moat  = sect_gm(ind)
    if ok2(_npm_moat) and _npm_moat > _sg_moat + 8:
        moat_s_base = min(10, moat_s_base + 1.5)  # margin premium = pricing power moat
    moat_s = float(np.clip(moat_s_base, 0, 10))
    if moat_signals: sigs.append(" ".join(moat_signals))
    detail["Moat"] = {"raw": round(moat_s, 2), "score": round(moat_s, 2), "w": P1_SUB["moat"]}

    raw = (rs * P1_SUB["roic"] + rcs * P1_SUB["roce"] + roa_s * P1_SUB["roa"] +
           fps * P1_SUB["fcf_pat"] + moat_s * P1_SUB["moat"])
    return float(np.clip(raw, 0, 10)), sigs, detail


# ──────────────────────────────────────────────────────────────────────────────
# P2: GROWTH SCORING  (15%)
# PAT5(38%) OPM_Expansion(28%) EPS_Accel(20%) Rev5(8%) Reinv(6%)
# Key: [Y] EPS growth NOT sig in dynamic models! PAT CAGR still works India [G]
# ──────────────────────────────────────────────────────────────────────────────

def p2_growth(r: dict) -> Tuple[float, List[str], dict]:
    sigs, detail = [], {}

    # ── PAT CAGR 5Y ── [G] β=0.4137, p=1.57e-4; best India growth predictor
    pat5 = fv(r.get("Profit growth 5Years"))
    cyc_pen = 1.0
    # Cyclical base detection: if TTM FCF >> 3Y avg FCF, may be peak cycle
    fcf3 = fv(r.get("Free cash flow 3years"))
    fcfl = fv(r.get("Free cash flow last year"))
    if ok2(pat5) and pat5 > 80 and ok2(fcf3) and ok2(fcfl) and fcf3 > 0 and fcfl > fcf3 * 2.5:
        cyc_pen = 0.65
        sigs.append(f"⚠CyclicalPeak(PAT5={pat5:.0f}%→penalised)")
    if ok2(pat5):
        es = log_s(pat5, 5, 35) * cyc_pen  # V5-5: o=35; PAT5=20%→5.5, 25%→6.5, 35%→7.9, 50%→9.2 [Gunasekaran p=1.57e-4 continuous]
        tag = "★★★★" if pat5 >= 35 else "★★★" if pat5 >= 25 else "★★" if pat5 >= 15 else "★" if pat5 >= 8 else "⚠"
        if pat5 >= 8: sigs.append(f"5Y_PAT_CAGR {pat5:.1f}%{tag}")
        elif pat5 < 0: sigs.append(f"⚠PAT Decline {pat5:.1f}%")  # Bug L fix: es=0.0 was unreachable; log_s already returns 0 for negatives
        detail["PAT_CAGR_5Y"] = {"raw": round(pat5, 1), "score": round(es, 2), "w": P2_SUB["pat5"]}
    else:
        es = 4.0; detail["PAT_CAGR_5Y"] = {"raw": None, "score": es, "w": P2_SUB["pat5"]}  # slightly below neutral: missing 5Y growth warrants caution

    # ── OPM EXPANSION ── [G] OPM p=0.008; TREND not level matters
    pg = fv(r.get("Profit growth")); sg = fv(r.get("Sales growth"))
    if ok2(pg) and ok2(sg):  # Bug D fix: sg==0 is valid (flat-revenue margin expansion)
        # Bug fix: both contracting = no expansion signal (pg=-5%, sg=-20% is NOT +15pp expansion)
        if pg < 0 and sg < 0:
            delta = 0  # dual contraction → treat as neutral
        else:
            delta = pg - sg  # profit growing faster than revenue = margin expansion
        ops = lin_s(delta, -25, 35)
        if delta >= 20: sigs.append(f"MarginExpand +{delta:.0f}pp ★★★★")
        elif delta >= 10: sigs.append(f"MarginExpand +{delta:.0f}pp ★★★")
        elif delta >= 3: sigs.append(f"Margin +{delta:.0f}pp ★★")
        elif delta < -20: sigs.append(f"⚠MarginCompress {delta:.0f}pp")
        detail["OPM_Expansion"] = {"raw": round(delta, 1), "score": round(ops, 2), "w": P2_SUB["opm_exp"]}
    else:
        ops = 5.0; detail["OPM_Expansion"] = {"raw": None, "score": ops, "w": P2_SUB["opm_exp"]}

    # ── EPS ACCELERATION ── [O] CANSLIM C+A: current vs multi-year baseline
    if ok2(pg) and ok2(pat5) and pat5 > 0:
        acc = pg - pat5  # positive = accelerating above trend
        acs = lin_s(acc, -30, 45)
        if acc > 25 and pg > 20: sigs.append(f"EPS Accel ★★★★ ({pg:.0f}%TTM vs {pat5:.0f}%5Y)")
        elif acc > 10 and pg > 15: sigs.append(f"EPS Accel ★★★ ({pg:.0f}%TTM)")
        elif pg < -25: sigs.append(f"⚠EPS Collapse {pg:.0f}%")
        detail["EPS_Accel"] = {"raw": round(acc, 1), "score": round(acs, 2), "w": P2_SUB["accel"]}
    else:
        acs = 4.0; detail["EPS_Accel"] = {"raw": None, "score": acs, "w": P2_SUB["accel"]}

    # ── REV CAGR 5Y ── [G] p=0.164 NOT significant → demoted but retained
    rev5 = fv(r.get("Sales growth 5Years"))
    if ok2(rev5):
        rvs = log_s(rev5, 3, 20)  # Calibrated: Rev5=15%→5.1, 20%→6.3
        if rev5 >= 20: sigs.append(f"RevCAGR5Y {rev5:.1f}%★★")
        elif rev5 < 0: rvs = 1.0; sigs.append(f"⚠RevDecline {rev5:.1f}%")
        detail["Rev_CAGR_5Y"] = {"raw": round(rev5, 1), "score": round(rvs, 2), "w": P2_SUB["rev5"]}
    else:
        rvs = 3.0; detail["Rev_CAGR_5Y"] = {"raw": None, "score": rvs, "w": P2_SUB["rev5"]}

    # ── REINVESTMENT RATE ── [M] Mayer: ROIC × Reinv = intrinsic growth
    roce = pct(r.get("Return on capital employed"))
    pat = fv(r.get("Profit after tax")); fcf = fv(r.get("Free cash flow last year"))
    if ok2(roce) and ok2(fcf) and ok2(pat) and pat > 0:
        fcf_ratio = fcf / pat
        if fcf_ratio >= 1: reinv_rate = roce * 0.25   # high cash = low reinvest
        elif fcf_ratio < 0: reinv_rate = 0.0
        else: reinv_rate = max(0, (1 - fcf_ratio)) * roce
        rrs = log_s(reinv_rate, 0, 22)
        detail["Reinv_Rate"] = {"raw": round(reinv_rate, 1), "score": round(rrs, 2), "w": P2_SUB["reinv"]}
    else:
        rrs = 4.0; detail["Reinv_Rate"] = {"raw": None, "score": rrs, "w": P2_SUB["reinv"]}

    raw = (es * P2_SUB["pat5"] + ops * P2_SUB["opm_exp"] + acs * P2_SUB["accel"] +
           rvs * P2_SUB["rev5"] + rrs * P2_SUB["reinv"])
    return float(np.clip(raw, 0, 10)), sigs, detail


# ──────────────────────────────────────────────────────────────────────────────
# P3: VALUE SCORING  (28%) — Elevated because FCF/P is #1 predictor [Y]
# FCF_Yield(40%) B/M(18%) PE_vs_Hist(20%) EV/EBITDA(12%) EV/Sales(6%) PEG(4%)
# ──────────────────────────────────────────────────────────────────────────────

def p3_value(r: dict) -> Tuple[float, List[str], dict, float]:
    sigs, detail = [], {}
    fcfy_out = np.nan

    # ── EQUITY FCF YIELD ── [Y] #1 global predictor β=46-82; [G] p=1.53e-12
    # International norm for equity screens: FCF / Market Cap (or inverse of P/FCF).
    # Use one canonical helper everywhere to avoid inconsistent recomputation.
    fcfy, fcfy_basis = compute_fcf_yield_pct(r, return_basis=True)
    fcfy_out = fcfy

    if ok2(fcfy):
        if fcfy < 0:
            fys = 0.0; sigs.append(f"⚠EqFCFYield {fcfy:.1f}% (cash burn)")
        else:
            fys = log_s(fcfy, 0, 22)  # V5-4: o=22; Yartseva β=46-82 is continuous.
                                       # EqFCFYield=4%→4.8, 8%→6.3, 15%→8.0, 22%→9.1 [Indian mkt]
            tier = "★★★★[Y]#1" if fcfy >= 15 else "★★★[Y]#1" if fcfy >= 8 else "★★★" if fcfy >= 4 else "★★" if fcfy >= 1.5 else "★"
            sigs.append(f"EqFCFYield {fcfy:.1f}%{tier}")
        detail["FCF_Yield"] = {"raw": round(fcfy, 2), "score": round(fys, 2), "w": P3_SUB["fcfy"], "basis": fcfy_basis}
    else:
        # Neutral for missing/non-applicable (especially financials where FCF yield is not primary).
        fys = 5.0; detail["FCF_Yield"] = {"raw": None, "score": fys, "w": P3_SUB["fcfy"], "basis": fcfy_basis}

    # ── BOOK-TO-MARKET (B/M) ── [Y] β=7-42; Fama-French HML factor
    bv = fv(r.get("Book value")); price = fv(r.get("Current Price"))
    if ok2(bv) and ok2(price) and price > 0:
        bm = bv / price
        bms = log_s(bm, 0.03, 0.85)
        tag = "★★★[Y]HML" if bm >= 0.65 else "★★" if bm >= 0.3 else "★" if bm >= 0.1 else "⚠overval"
        sigs.append(f"B/M {bm:.3f}{tag}")
        detail["B/M"] = {"raw": round(bm, 3), "score": round(bms, 2), "w": P3_SUB["bm"]}
    else:
        bms = 5.0; detail["B/M"] = {"raw": None, "score": bms, "w": P3_SUB["bm"]}  # neutral: unknown B/M ≠ overvalued

    # ── PE vs HISTORICAL ── [G] p=3.40e-22 HIGHEST significance India
    pe = fv(r.get("Price to Earning"))
    h5pe = fv(r.get("Historical PE 5Years"))
    ipe = fv(r.get("Industry PE"))
    pes = 5.0  # neutral default: unknown PE context ≠ expensive
    if ok2(pe) and pe > 0:
        if ok2(h5pe) and h5pe > 0 and ok2(ipe) and ipe > 0:
            dh = (1 - pe / h5pe) * 100
            ds = (1 - pe / ipe) * 100
            combined = dh * 0.65 + ds * 0.35
            pes = lin_s(combined, -20, 55)
            if combined >= 30: sigs.append(f"PE {combined:.0f}%belowHist+Sect ★★★[G]")
        elif ok2(h5pe) and h5pe > 0:
            dh = (1 - pe / h5pe) * 100
            pes = lin_s(dh, -20, 55)
            if dh >= 25: sigs.append(f"PE {dh:.0f}%belowHist ★★★")
            elif dh >= 12: sigs.append(f"PE {dh:.0f}%belowHist ★★")
            elif dh < -25: sigs.append(f"⚠PE {-dh:.0f}%aboveHist")
        elif ok2(ipe) and ipe > 0:
            ds = (1 - pe / ipe) * 100
            pes = lin_s(ds, -20, 60)
            if ds >= 40: sigs.append(f"PE {ds:.0f}%belowSect ★★★")
        else:
            pes = log_s(35 - pe, 0, 30) if pe > 0 else 3.0
        detail["PE_vs_Hist"] = {"raw": round(pe, 1), "score": round(pes, 2), "w": P3_SUB["pe_hist"]}
    else:
        detail["PE_vs_Hist"] = {"raw": None, "score": pes, "w": P3_SUB["pe_hist"]}

    # ── EV/EBITDA ── [Y] significant in within-FE specs
    eveb = fv(r.get("EVEBITDA"))
    if ok2(eveb) and eveb > 0:
        evs = inv_s(eveb, 4, 35)
        tag = "★★★" if eveb < 7 else "★★" if eveb < 15 else "★" if eveb < 22 else "⚠"
        sigs.append(f"EV/EBITDA {eveb:.1f}x{tag}")
        detail["EV/EBITDA"] = {"raw": round(eveb, 2), "score": round(evs, 2), "w": P3_SUB["ev_eb"]}
    else:
        evs = 5.0; detail["EV/EBITDA"] = {"raw": None, "score": evs, "w": P3_SUB["ev_eb"]}  # neutral: unknown EV/EBITDA ≠ overpriced

    # ── EV/SALES ── [Y] significant in Model 3; low = overlooked company
    evss = 5.0   # V5-2: safe default — UnboundLocalError if ev_s directly available & ≤0
    ev_s = fv(r.get("EV to Sales") or r.get("EV/Sales"))
    if not ok2(ev_s):
        # Approximate EV/Sales from available data
        _npm = pct(r.get("Net profit margin") or r.get("OPM"))
        _pat = fv(r.get("Profit after tax"))
        _mcap_ev = fv(r.get("Market Capitalization"))
        _de_ev = fv(r.get("Debt to equity"))
        if ok2(_npm) and _npm > 0 and ok2(_pat) and ok2(_mcap_ev) and ok2(_de_ev):
            _rev_est = _pat / (_npm / 100)
            _ev_est  = _mcap_ev * (1 + max(_de_ev, 0))
            if _rev_est > 0:
                ev_s = _ev_est / _rev_est
    if ok2(ev_s) and ev_s > 0:
        evss = inv_s(ev_s, 0.3, 5)
        tag = "★★★" if ev_s < 0.8 else "★★" if ev_s < 2 else "★" if ev_s < 4 else "⚠"
        sigs.append(f"EV/Sales {ev_s:.2f}x{tag}[Y]")
        detail["EV/Sales"] = {"raw": round(ev_s, 2), "score": round(evss, 2), "w": P3_SUB["ev_sales"]}
    else:
        evss = 5.0; detail["EV/Sales"] = {"raw": None, "score": evss, "w": P3_SUB["ev_sales"]}  # neutral: unknown EV/Sales ≠ overpriced

    # ── PEG ── [L] Lynch; demoted but still useful cross-check
    peg = fv(r.get("PEG Ratio"))
    eg5 = fv(r.get("Profit growth 5Years"))
    if not ok2(peg) and ok2(pe) and ok2(eg5) and eg5 > 0:
        peg = pe / eg5
    if ok2(peg):
        if peg <= 0:
            pgs = 0.0; sigs.append(f"⚠NegPEG (earnings declining)")
        elif peg < 0.3: pgs = 10.0; sigs.append(f"PEG {peg:.2f} ★★★★Lynch!")
        elif peg < 0.7: pgs = 8.5; sigs.append(f"PEG {peg:.2f} ★★★")
        elif peg < 1.0: pgs = 7.0; sigs.append(f"PEG {peg:.2f} ★★")
        elif peg < 1.5: pgs = 4.5
        elif peg < 2.5: pgs = 2.0
        else:           pgs = 0.0; sigs.append(f"⚠PEG {peg:.2f} overval")
        detail["PEG"] = {"raw": round(peg, 3), "score": round(pgs, 2), "w": P3_SUB["peg"]}
    else:
        pgs = 5.0; detail["PEG"] = {"raw": None, "score": pgs, "w": P3_SUB["peg"]}  # neutral: unknown PEG ≠ expensive

    raw = (fys * P3_SUB["fcfy"] + bms * P3_SUB["bm"] + pes * P3_SUB["pe_hist"] +
           evs * P3_SUB["ev_eb"] + evss * P3_SUB["ev_sales"] + pgs * P3_SUB["peg"])
    return float(np.clip(raw, 0, 10)), sigs, detail, fcfy_out


# ──────────────────────────────────────────────────────────────────────────────
# P4: CAPITAL DISCIPLINE  (13%) — THE YARTSEVA FINDING
# Investment Guard(50%) CapexEff(22%) CashConv(16%) ShldrYield(12%)
# Key: [Y] Asset growth > EBITDA growth → next year returns −5 to −23pp
# ──────────────────────────────────────────────────────────────────────────────

def p4_discipline(r: dict) -> Tuple[float, List[str], dict]:
    sigs, detail = [], {}

    # ── YARTSEVA INVESTMENT GUARD ── [Y] β=−5 to −23; most unique finding
    # "Firms must invest aggressively but EBITDA growth must keep pace"
    asset_growth = fv(r.get("Asset growth") or r.get("Total assets growth"))
    ebitda_growth = fv(r.get("EBITDA growth") or r.get("Profit growth"))
    cfo = fv(r.get("Cash from operations last year") or r.get("CFO"))
    pat = fv(r.get("Profit after tax"))
    fcf = fv(r.get("Free cash flow last year"))

    # Fallback: use profit growth as EBITDA growth proxy
    if not ok2(ebitda_growth):
        ebitda_growth = fv(r.get("Profit growth"))

    inv_guard_score = 5.0  # default neutral (was 6.0 — biased upward for data-sparse stocks)
    if ok2(asset_growth) and ok2(ebitda_growth):
        # Yartseva Inv Dummy = 1 if asset_growth > EBITDA_growth
        if asset_growth > 0 and ebitda_growth > 0:
            # Bug I fix: ratio = asset_growth/ebitda_growth was computed but never used
            if asset_growth > ebitda_growth and asset_growth > 15:
                # WARNING: assets growing faster than earnings (Yartseva negative signal)
                penalty = min(1.0, (asset_growth - ebitda_growth) / 50)
                inv_guard_score = max(0.0, 6.0 - penalty * 8)
                sigs.append(f"⚠InvDummy=1 (Asset{asset_growth:.0f}%>EBITDA{ebitda_growth:.0f}%)[Y−signal]")
            elif ebitda_growth >= asset_growth and asset_growth > 5:
                # IDEAL: growing assets AND earnings keeping pace or exceeding
                inv_guard_score = min(10.0, 7.0 + (ebitda_growth - asset_growth) / 20)
                sigs.append(f"InvGuard ★★★ (EBITDA{ebitda_growth:.0f}%≥Asset{asset_growth:.0f}%)[Y+]")
            elif asset_growth <= 0:
                # Shrinking assets with low EBITDA growth = distress
                if ebitda_growth <= 0:
                    inv_guard_score = 1.0; sigs.append("⚠ShrinkingAssets+FlatEBITDA")
                else:
                    inv_guard_score = 4.0  # at least profitable
            else:
                inv_guard_score = 5.0
        elif asset_growth <= 0 and ebitda_growth > 10:
            # Asset-light: not growing assets but highly profitable — IDEAL for quality
            inv_guard_score = 9.0; sigs.append("AssetLight+ProfitGrow ★★★★[B]")
        elif asset_growth > 30 and ebitda_growth <= 0:
            inv_guard_score = 0.0; sigs.append("⚠⚠OverInvest+NegEBITDA [Y-worst]")
        else:
            inv_guard_score = 5.0
    else:
        # Fallback: use FCF/PAT ratio as discipline signal
        if ok2(fcf) and ok2(pat) and pat > 0:
            ratio = fcf / pat
            inv_guard_score = lin_s(ratio, 0, 1.2)
    detail["Inv_Guard"] = {"raw": round(inv_guard_score, 2), "score": round(inv_guard_score, 2), "w": P4_SUB["inv_guard"]}

    # ── CAPEX EFFICIENCY ── CFO/Revenue: operational cash generation efficiency [AQR]
    # Bug E fix: was FCF/PAT — identical to P1 fcf_pat (double-count worth ~6.3% score)
    # Replaced with CFO/Revenue: distinct metric, measures operational cash per ₹ of sales
    rev = fv(r.get("Total revenue") or r.get("Sales") or r.get("Net Sales"))
    if ok2(cfo) and ok2(rev) and rev > 0:
        cfo_rev_pct = cfo / rev * 100   # CFO as % of revenue
        cxs = log_s(cfo_rev_pct, 2, 15)  # Calibrated: CFO/Rev=12%→5.4, 15%→6.3
        if cfo_rev_pct >= 15: sigs.append(f"CFO/Rev {cfo_rev_pct:.1f}% ★★★[AQR]")
        elif cfo_rev_pct >= 8: sigs.append(f"CFO/Rev {cfo_rev_pct:.1f}% ★★")
        elif cfo_rev_pct < 0: cxs = 0.0; sigs.append("⚠NegCFO/Rev")
        detail["CapexEff"] = {"raw": round(cfo_rev_pct, 1), "score": round(cxs, 2), "w": P4_SUB["capex_eff"]}
    elif ok2(fcf) and ok2(pat) and pat > 0:
        # Fallback when revenue unavailable: use Capex/CFO ratio if possible, else neutral
        cxs = 5.0; detail["CapexEff"] = {"raw": None, "score": cxs, "w": P4_SUB["capex_eff"]}  # neutral: unknown CFO/Rev ≠ poor discipline
    else:
        cxs = 5.0; detail["CapexEff"] = {"raw": None, "score": cxs, "w": P4_SUB["capex_eff"]}  # neutral: unknown CFO/Rev ≠ poor discipline

    # ── CASH CONVERSION ── [A] AQR: CFO/EBITDA or CFO/PAT
    if ok2(cfo) and ok2(pat) and pat > 0:
        cc = cfo / pat
        ccs = log_s(cc, 0, 1.0)  # Calibrated: CFO/PAT=1.0x→6.3, 1.5x→7.8
        if cc >= 1.0: sigs.append(f"CashConv {cc:.2f}x ★★★[AQR]")
        elif cc < 0: ccs = 0.0; sigs.append("⚠NegCFO")
        detail["CashConv"] = {"raw": round(cc, 2), "score": round(ccs, 2), "w": P4_SUB["cash_conv"]}
    else:
        ccs = 4.0; detail["CashConv"] = {"raw": None, "score": ccs, "w": P4_SUB["cash_conv"]}

    # ── SHAREHOLDER YIELD ── Equity FCF yield + Dividend yield
    dy = fv(r.get("Dividend yield"))
    fcfy_val, fcfy_basis = compute_fcf_yield_pct(r, return_basis=True)
    if ok2(fcfy_val):
        shr_yield = fcfy_val + (dy if ok2(dy) else 0)
        shs = log_s(shr_yield, 0, 18)
        if shr_yield >= 10: sigs.append(f"ShhldrYield {shr_yield:.1f}%★★★")
        detail["Shhldr_Yield"] = {"raw": round(shr_yield, 2), "score": round(shs, 2), "w": P4_SUB["shreholder"], "basis": fcfy_basis}
    elif ok2(dy):
        # For financials/non-FCF cases, keep partial dividend-only signal rather than forcing NaN.
        shr_yield = dy
        shs = log_s(shr_yield, 0, 8)
        detail["Shhldr_Yield"] = {"raw": round(shr_yield, 2), "score": round(shs, 2), "w": P4_SUB["shreholder"], "basis": "DividendOnly"}
    else:
        shs = 3.0; detail["Shhldr_Yield"] = {"raw": None, "score": shs, "w": P4_SUB["shreholder"], "basis": fcfy_basis}

    raw = (inv_guard_score * P4_SUB["inv_guard"] + cxs * P4_SUB["capex_eff"] +
           ccs * P4_SUB["cash_conv"] + shs * P4_SUB["shreholder"])
    return float(np.clip(raw, 0, 10)), sigs, detail


# ──────────────────────────────────────────────────────────────────────────────
# P5: SIZE & DISCOVERY  (7%)
# MCap(50%) InstGap(30%) Float(20%)
# ──────────────────────────────────────────────────────────────────────────────

def p5_size(r: dict) -> Tuple[float, List[str], dict]:
    sigs, detail = [], {}

    # ── MCAP BAND ── [F] SMB; India: 300-3000Cr optimal window
    mcap = fv(r.get("Market Capitalization"))
    if ok2(mcap):
        if mcap < 150:      mcs = 6.5;  sigs.append(f"Micro ₹{mcap:.0f}Cr⚠LiqRisk")
        elif mcap < 500:    mcs = 9.0;  sigs.append(f"Micro-Small ₹{mcap:.0f}Cr ★★★")
        elif mcap < 2000:   mcs = 10.0; sigs.append(f"Small ₹{mcap:.0f}Cr ★★★★ sweetspot")
        elif mcap < 5000:   mcs = 8.5;  sigs.append(f"Small-Mid ₹{mcap:.0f}Cr ★★★")
        elif mcap < 12000:  mcs = 6.5;  sigs.append(f"Mid ₹{mcap:.0f}Cr ★★")
        elif mcap < 35000:  mcs = 4.0;  sigs.append(f"Large-Mid ₹{mcap:.0f}Cr ★")
        elif mcap < 100000: mcs = 2.0;  sigs.append(f"Large ₹{mcap:.0f}Cr")
        else:               mcs = 0.5;  sigs.append(f"Mega ₹{mcap:.0f}Cr (SMB≈0)")
        detail["MCap_Band"] = {"raw": round(mcap, 0), "score": mcs, "w": P5_SUB["mcap"]}
    else:
        mcs = 5.0; detail["MCap_Band"] = {"raw": None, "score": mcs, "w": P5_SUB["mcap"]}

    # ── INST COVERAGE GAP ── Undiscovery = future re-rating potential [O]
    dii = fv(r.get("DII holding")); fii = fv(r.get("FII holding"))
    if ok2(dii) and ok2(fii): inst = dii + fii
    elif ok2(dii): inst = dii
    elif ok2(fii): inst = fii
    else: inst = np.nan
    if ok2(inst):
        if inst < 3:    igs = 8.0;  sigs.append(f"Inst {inst:.1f}% ★★★ undiscovered")
        elif inst < 15: igs = 10.0; sigs.append(f"Inst {inst:.1f}% ★★★★ sweet spot")
        elif inst < 30: igs = 7.5
        elif inst < 50: igs = 4.5
        else:           igs = 1.5;  sigs.append(f"Inst {inst:.1f}% crowded")
        detail["Inst_Gap"] = {"raw": round(inst, 1), "score": igs, "w": P5_SUB["inst_gap"]}
    else:
        igs = 5.0; detail["Inst_Gap"] = {"raw": None, "score": igs, "w": P5_SUB["inst_gap"]}

    # ── FREE FLOAT ── Tight float = faster re-rating upon discovery
    promo = fv(r.get("Promoter holding"))
    if ok2(promo):
        fl = 100 - promo
        if fl < 15:    fls = 6.5;  sigs.append(f"TightFloat {fl:.0f}%")
        elif fl < 35:  fls = 9.5;  sigs.append(f"OptFloat {fl:.0f}% ★★★")
        elif fl < 55:  fls = 8.0
        elif fl < 75:  fls = 5.5
        else:          fls = 2.5;  sigs.append(f"WideFloat {fl:.0f}% (less conviction)")
        detail["Float"] = {"raw": round(fl, 1), "score": fls, "w": P5_SUB["float"]}
    else:
        fls = 5.0; detail["Float"] = {"raw": None, "score": fls, "w": P5_SUB["float"]}

    raw = mcs * P5_SUB["mcap"] + igs * P5_SUB["inst_gap"] + fls * P5_SUB["float"]
    return float(np.clip(raw, 0, 10)), sigs, detail


# ──────────────────────────────────────────────────────────────────────────────
# P6: SAFETY & GOVERNANCE  (17%)
# D/E(35%) Piotroski(24%) IntCov(14%) Pledge(16%) Prom+FII(11%)
# Key: D/E β=0.4586 p=5.28e-19 [G] DOMINANT India predictor
# ──────────────────────────────────────────────────────────────────────────────

def p6_safety(r: dict) -> Tuple[float, List[str], dict]:
    sigs, detail = [], {}

    # ── D/E RATIO ── [G] β=0.4586, p=5.28e-19 — SINGLE STRONGEST India predictor
    de = fv(r.get("Debt to equity"))
    if ok2(de):
        if de == 0:      des = 10.0; sigs.append("ZERO DEBT ★★★★[G]#1")
        elif de < 0.1:   des = 9.5;  sigs.append(f"D/E {de:.2f} ★★★★")
        elif de < 0.3:   des = 8.5;  sigs.append(f"D/E {de:.2f} ★★★")
        elif de < 0.6:   des = 7.0;  sigs.append(f"D/E {de:.2f} ★★")
        elif de < 1.0:   des = 5.0;  sigs.append(f"D/E {de:.2f} ★")
        elif de < 1.5:   des = 3.0;  sigs.append(f"⚠D/E {de:.2f}")
        elif de < 2.5:   des = 1.0;  sigs.append(f"⚠⚠D/E {de:.2f} HIGH")
        else:            des = 0.0;  sigs.append(f"⚠⚠⚠D/E {de:.2f} DANGER")
        detail["D/E"] = {"raw": round(de, 3), "score": des, "w": P6_SUB["de"]}
    else:
        des = 5.0; detail["D/E"] = {"raw": None, "score": des, "w": P6_SUB["de"]}

    # ── PIOTROSKI F-SCORE ── [P] Alta Fox: 88% multibaggers had F≥7
    pio = fv(r.get("Piotroski score"))
    if ok2(pio):
        if pio >= 8:   pios = 10.0; sigs.append(f"Piotroski {int(pio)}/9 ★★★★[88%MB]")
        elif pio >= 7: pios = 8.5;  sigs.append(f"Piotroski {int(pio)}/9 ★★★")
        elif pio >= 6: pios = 6.0;  sigs.append(f"Piotroski {int(pio)}/9 ★★")
        elif pio >= 4: pios = 3.0
        elif pio >= 2: pios = 1.0;  sigs.append(f"⚠Piotroski {int(pio)}/9")
        else:          pios = 0.0;  sigs.append(f"⚠⚠Piotroski {int(pio)}/9 DISTRESS")
        detail["Piotroski"] = {"raw": int(pio), "score": pios, "w": P6_SUB["pio"]}
    else:
        pios = 5.0; detail["Piotroski"] = {"raw": None, "score": pios, "w": P6_SUB["pio"]}

    # ── INTEREST COVERAGE ── [A] AQR safety; EBITDA/InterestExp ≥ 3x
    icr = fv(r.get("Interest coverage ratio"))
    if ok2(icr):
        if icr >= 20:   ics = 10.0; sigs.append(f"IntCov {icr:.1f}x ★★★★")
        elif icr >= 8:  ics = 8.5;  sigs.append(f"IntCov {icr:.1f}x ★★★")
        elif icr >= 4:  ics = 6.5;  sigs.append(f"IntCov {icr:.1f}x ★★")
        elif icr >= 2:  ics = 3.5
        elif icr >= 1:  ics = 1.0;  sigs.append(f"⚠IntCov {icr:.1f}x low")
        else:           ics = 0.0;  sigs.append(f"⚠⚠IntCov {icr:.1f}x DANGER")
        detail["IntCov"] = {"raw": round(icr, 1), "score": ics, "w": P6_SUB["intcov"]}
    else:
        # Fallback: use D/E as proxy (zero debt = high interest coverage)
        if ok2(de) and de == 0: ics = 10.0
        elif ok2(de) and de < 0.3: ics = 7.5
        else: ics = 4.5
        detail["IntCov"] = {"raw": None, "score": ics, "w": P6_SUB["intcov"]}

    # ── PLEDGE ── India governance catastrophe signal
    # FIX-4: screener.in exports "Pledging %" — try all known variants
    pledge = fv(r.get("Pledged percentage") or r.get("Pledging %") or
                r.get("Pledge %") or r.get("Pledged shares %") or r.get("% Pledged"))
    if ok2(pledge):
        if pledge == 0:    pls = 10.0; sigs.append("ZeroPledge ★★★★")
        elif pledge < 5:   pls = 8.5;  sigs.append(f"Pledge {pledge:.0f}% ★★★")
        elif pledge < 15:  pls = 5.5
        elif pledge < 30:  pls = 2.0;  sigs.append(f"⚠Pledge {pledge:.0f}%")
        elif pledge < 50:  pls = 0.5;  sigs.append(f"⚠⚠Pledge {pledge:.0f}% HIGH")
        else:              pls = 0.0;  sigs.append(f"⚠⚠⚠Pledge {pledge:.0f}% EXTREME")
        detail["Pledge"] = {"raw": round(pledge, 1), "score": pls, "w": P6_SUB["pledge"]}
    else:
        pls = 5.0; detail["Pledge"] = {"raw": None, "score": pls, "w": P6_SUB["pledge"]}  # neutral; unknown governance ≠ good governance

    # ── PROMOTER + FII TREND ── [O] CANSLIM I; insider conviction signal
    cp = fv(r.get("Change in promoter holding"))
    cf = fv(r.get("Change in FII holding"))
    trend_s = 5.0
    if ok2(cp):
        if cp >= 1.5:     pts = 10.0; sigs.append(f"PromoterBuying +{cp:.1f}% ★★★★")
        elif cp >= 0.5:   pts = 7.5;  sigs.append(f"Prom +{cp:.1f}% ★★")
        elif cp > -0.5:   pts = 5.5
        elif cp > -2.0:   pts = 2.5;  sigs.append(f"⚠PromoterSelling {cp:.1f}%")
        else:             pts = 0.0;  sigs.append(f"⚠⚠PromoterSelling {cp:.1f}%")
    else:
        pts = 5.0
    if ok2(cf):
        fts = 8.0 if cf > 1.0 else 6.5 if cf > 0 else 4.5 if cf > -1 else 2.0
    else:
        fts = 5.0
    trend_s = pts * 0.65 + fts * 0.35
    detail["Prom_FII_Trend"] = {"raw": round(cp if ok2(cp) else 0, 2),
                                "score": round(trend_s, 2), "w": P6_SUB["prom_fii"]}

    raw = (des * P6_SUB["de"] + pios * P6_SUB["pio"] + ics * P6_SUB["intcov"] +
           pls * P6_SUB["pledge"] + trend_s * P6_SUB["prom_fii"])
    return float(np.clip(raw, 0, 10)), sigs, detail


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY TIMING SCORE (not a pillar — bonus/penalty signal)
# [Y] Yartseva: "entry point critical; near 52-week LOW = higher next-year return"
# [JT] Jegadeesh-Titman: multibagger momentum reversal pattern
# ──────────────────────────────────────────────────────────────────────────────

def entry_signal(r: dict) -> Tuple[float, str, str]:
    """Returns (score -5 to +5, label, color)"""
    ph52 = fv(r.get("52 Week High")); pl52 = fv(r.get("52 Week Low"))
    price = fv(r.get("Current Price"))
    rsi = fv(r.get("RSI 14") or r.get("RSI"))
    mom6 = fv(r.get("6 Month Return") or r.get("6M Return") or r.get("Return over 6months"))

    # If 52W data missing but price available, try to derive from Current Price ±
    # (This handles rate-limited minimal-row stocks that have price but no history)
    if ok2(price) and (not ok2(ph52) or not ok2(pl52)):
        # Can't compute range without history — but RSI fallback may still work
        pass  # fall through to RSI-only path below

    if ok2(price) and ok2(ph52) and ok2(pl52) and ph52 > pl52:
        # Price range 0=at52WLow, 100=at52WHigh
        range_pct = (price - pl52) / (ph52 - pl52) * 100
        # [Y] "closer to 52-week low = better next-year return"
        entry = lin_s(100 - range_pct, 0, 100, 5)  # inverted!
        label = ("★★★PRIME ENTRY" if range_pct < 25 else
                 "★★GOOD ENTRY" if range_pct < 45 else
                 "★FAIR ENTRY" if range_pct < 65 else
                 "⚠ELEVATED" if range_pct < 85 else
                 "⚠⚠NEAR 52WHIGH — WAIT")
        color = "#00e676" if range_pct < 45 else "#ff9800" if range_pct < 65 else "#ff4757"
        # [JT] Jegadeesh-Titman: RSI oversold + 6M price drop = reversal setup
        if ok2(rsi) and rsi < 35:
            entry = min(5.0, entry + 1.0)
            label += " | RSI Oversold[JT]"
        elif ok2(rsi) and rsi < 45:
            entry = min(5.0, entry + 0.5)
        if ok2(mom6) and mom6 < -15:
            entry = min(5.0, entry + 0.5)  # 6M decline → mean-reversion signal
            label += " | 6M-Reversal[JT]"
        return float(entry), f"{label} ({range_pct:.0f}% of 52W range)", color

    # Bug G fix: RSI-only fallback when 52W range data unavailable
    # Catches fresh listings, yfinance gaps, and CSV-only mode
    rsi_bonus = 0.0; rsi_lbl = ""
    if ok2(rsi):
        if rsi < 30:
            rsi_bonus = 2.0; rsi_lbl = " | RSI Extreme Oversold[JT]"
        elif rsi < 40:
            rsi_bonus = 1.0; rsi_lbl = " | RSI Oversold[JT]"
    if ok2(mom6) and mom6 < -15:
        rsi_bonus = min(3.0, rsi_bonus + 0.5)
        rsi_lbl += " | 6M-Reversal[JT]"
    if rsi_bonus > 0:
        return float(rsi_bonus), f"RSI-Only Entry{rsi_lbl}", "#00e676"
    # Distinguish: price exists but no 52W history (rate-limited) vs truly no data
    if ok2(price):
        return 0.0, "52W data unavailable — rerun enrichment", "#666666"
    return 0.0, "Entry timing N/A — no price data", "#888888"


# ──────────────────────────────────────────────────────────────────────────────
# COMPOSITE SCORE ENGINE  — v4.0 Ultra
# ──────────────────────────────────────────────────────────────────────────────

def tier_label(score: float) -> str:
    if score >= 80:   return "🥇 TIER 1"
    elif score >= 65: return "🥈 TIER 2"
    elif score >= 50: return "🥉 TIER 3"
    elif score >= 35: return "⚠️ TIER 4"
    else:             return "❌ TIER 5"

def tier_css(tier: str) -> str:
    return {"🥇 TIER 1":"tier1","🥈 TIER 2":"tier2","🥉 TIER 3":"tier3",
            "⚠️ TIER 4":"tier4","❌ TIER 5":"tier5"}.get(tier,"")

def tier_score_css(tier: str) -> str:
    return {"🥇 TIER 1":"t1-score","🥈 TIER 2":"t2-score","🥉 TIER 3":"t3-score",
            "⚠️ TIER 4":"t4-score","❌ TIER 5":"t5-score"}.get(tier,"")

def compute_score(row, pw: dict) -> dict:
    r = row.to_dict() if hasattr(row, "to_dict") else dict(row)

    p1s, p1sig, p1d = p1_quality(r)
    p2s, p2sig, p2d = p2_growth(r)
    p3s, p3sig, p3d, fcfy = p3_value(r)
    p4s, p4sig, p4d = p4_discipline(r)
    p5s, p5sig, p5d = p5_size(r)
    p6s, p6sig, p6d = p6_safety(r)
    entry_s, entry_lbl, entry_col = entry_signal(r)

    pillar_scores = {"P1": p1s, "P2": p2s, "P3": p3s, "P4": p4s, "P5": p5s, "P6": p6s}

    # Normalise pillar weights
    total_pw = sum(pw.values())
    w = {k: v / total_pw for k, v in pw.items()}

    # ── STEP 1: BASE SCORE ────────────────────────────────────────────────────
    base = (p1s * w["P1_Quality"] + p2s * w["P2_Growth"] + p3s * w["P3_Value"] +
            p4s * w["P4_Discipline"] + p5s * w["P5_Size"] + p6s * w["P6_Safety"]) * 10

    # ── STEP 2: WEAKEST LINK PENALTY (AQR QMJ principle) ─────────────────────
    worst = min(pillar_scores.values())
    # v4.0: softer penalty — weakest pillar < 2.5 drags overall score
    wl_pen = max(0.0, (2.5 - worst) * 1.8) if worst < 2.5 else 0.0

    # ── STEP 3: HARD DISQUALIFIERS ────────────────────────────────────────────
    disq = []
    de = fv(r.get("Debt to equity")); pledge = first_num(r, ["Pledged percentage", "Pledging %", "Pledge %", "Pledged shares %", "% Pledged"])
    pio = fv(r.get("Piotroski score")); eg5 = fv(r.get("Profit growth 5Years"))
    cp = fv(r.get("Change in promoter holding")); pat = fv(r.get("Profit after tax"))
    fcf = fv(r.get("Free cash flow last year")); mcap = fv(r.get("Market Capitalization"))
    fcfy_canon, fcfy_basis = compute_fcf_yield_pct(r, return_basis=True)
    asset_g = fv(r.get("Asset growth") or r.get("Total assets growth"))
    ebitda_g = fv(r.get("EBITDA growth"))  # Bug NEW-6 fix: use asset_g in a disqualifier

    # FIX-5: Recalibrated DISQ thresholds for Indian multibagger screening
    if ok2(de) and de > 2.0:          disq.append(f"D/E={de:.1f}>2.0")
    if ok2(pledge) and pledge > 25:    disq.append(f"Pledge={pledge:.0f}%>25%")
    if ok2(pio) and pio <= 3:          disq.append(f"Piotroski≤3 (weakness)")
    if ok2(eg5) and eg5 < -10:         disq.append(f"5Y_PAT_Decline={eg5:.0f}%")
    if ok2(cp) and cp < -3.0:          disq.append(f"PromoterSelling={cp:.1f}%")
    if ok2(fcfy_canon) and fcfy_canon < -15:
        disq.append("FCFYield<-15% (cash destruction)")
    if ok2(pat) and pat < 0 and ok2(p3s) and p3s < 4.5:
        disq.append("LossMaking+LowValue")   # V5-8: was p3s<3 (never triggered when P3 defaults=5.0)
    elif not ok2(pat):
        # Try raw net income from compute context (p1 already computed pat_cr proxy)
        _npm = fv(r.get("Net profit margin"))
        if ok2(_npm) and _npm < -10 and ok2(p3s) and p3s < 3:
            disq.append("LossMaking+LowValue(estd)")
    # Bug NEW-6 fix: Asset Bloat — aggressive asset expansion without earnings support [Y]
    if ok2(asset_g) and ok2(ebitda_g) and ebitda_g > 0 and asset_g > ebitda_g * 2.5 and asset_g > 40:
        disq.append(f"AssetBloat={asset_g:.0f}%>2.5×EBITDA_g")

    # ── STEP 4: BONUS MULTIPLIERS (hard cap 8.0) ──────────────────────────────
    bonus = 0.0
    roic = pct(r.get("Return on invested capital"))
    roce = pct(r.get("Return on capital employed"))
    peg = fv(r.get("PEG Ratio")); pe = fv(r.get("Price to Earning"))
    pat5 = fv(r.get("Profit growth 5Years")); pg = fv(r.get("Profit growth"))
    npq = fv(r.get("Net Profit latest quarter")); gf = fv(r.get("G Factor"))
    if not ok2(peg) and ok2(pe) and ok2(pat5) and pat5 > 0:
        peg = pe / pat5

    # ⬛ YARTSEVA COMPOUNDER BONUS [Y]: FCF Yield + B/M alignment + low PE
    bv = fv(r.get("Book value")); price = fv(r.get("Current Price"))
    bm = (bv / price) if (ok2(bv) and ok2(price) and price > 0) else None
    fcfy_val = fcfy_canon
    yartseva_triggered = (ok2(fcfy_val) and fcfy_val >= 6 and
                          ok2(bm) and bm >= 0.25 and
                          ok2(pe) and pe > 0 and pe < 20)
    if yartseva_triggered:
        bonus += 3.5

    # ⬛ TWIN ENGINE BONUS [M][L]: Quality + Growth + Value aligned perfectly
    q_ok = (ok2(roic) and roic >= 20) or (ok2(roce) and roce >= sect_roce(str(r.get("Industry","default"))) + 8)
    g_ok = ok2(pat5) and pat5 >= 20
    v_ok = ok2(peg) and 0 < peg < 1.0
    if q_ok and g_ok and v_ok:
        # Bug fix: if Yartseva already triggered, the overlap is not independent — cap the Twin bonus
        twin_bonus = 3.0
        if yartseva_triggered:
            twin_bonus = min(1.5, twin_bonus)  # signals overlap; avoid double-rewarding same stock traits
        bonus += twin_bonus

    # ⬛ QMJ COMPOUNDER [A]: High quality pillar + high safety pillar
    if p1s >= 7.5 and p6s >= 7.5:
        bonus += 2.0

    # ⬛ CANSLIM CATALYST [O]: Recent acceleration + positive FCF + Q profit
    if (ok2(npq) and npq > 0 and ok2(fcf) and fcf > 0 and
        ok2(pg) and pg > 25 and ok2(pat5) and pg > pat5 * 1.5):
        bonus += 1.8

    # ⬛ PRIME ENTRY BONUS [Y]: Near 52-week low = higher expected return [Yartseva]
    # V5-7: entry_bonus tracked separately → added to final but shown in own column
    #        Cap at 1.5 pts (was 2.0) so timing alone can't lift weak stock to Tier 3
    _entry_bonus = 0.0
    if entry_s >= 3.5:   _entry_bonus = 1.5  # near 52-wk low — strong reversal setup
    elif entry_s >= 2.5: _entry_bonus = 0.75  # moderate discount
    bonus += _entry_bonus

    # ⬛ G-FACTOR [screener.in]: minor confirmation
    if ok2(gf) and gf >= 9 and p1s >= 7.0 and p6s >= 6.5: bonus += 0.5
    elif ok2(gf) and gf >= 8: bonus += 0.2

    bonus = min(bonus, 8.0)  # HARD CAP

    # ── STEP 5: FINAL SCORE ───────────────────────────────────────────────────
    pre_final = float(np.clip(base - wl_pen + bonus, 0, 100))
    _fundamental_pre = float(np.clip(base - wl_pen + (bonus - _entry_bonus), 0, 100))
    if disq:
        # Graduated caps: severity matches the disqualification reason
        # FIX-5b: Graduated caps — calibrated for Indian multibagger context (audit)
        _DISQ_CAPS = {
            "D/E":           55,   # D/E>2 = moderate concern; still investable in capital-intensive sectors
            "Pledge":        42,   # >25% pledge = governance warning, not catastrophe
            "Piotroski":     28,   # ≤3 = weakness; ≤2 is true distress — moderate cap
            "5Y_PAT":        38,   # sustained ≥10% decline warrants monitoring
            "PromoterSell":  45,   # consistent selling = soft flag, not disqualification
            "FCFYield<":     25,   # cash destruction — hard cap (unchanged)
            "LossMaking":    30,   # loss + low value (unchanged)
            "AssetBloat":    40,   # unearned asset expansion (unchanged)
        }
        cap = 100.0  # Bug B fix: start permissive, tighten per disqualifier
        for d in disq:
            matched = False
            for key, val in _DISQ_CAPS.items():
                if key.lower() in d.lower():
                    cap = min(cap, val)  # now 45/40/38/35 actually fire
                    matched = True
                    break
            if not matched:
                cap = min(cap, 28.0)  # unknown disqualifier → conservative floor
        final = min(pre_final, float(cap))
    else:
        final = pre_final
        _fundamental_pre = _fundamental_pre  # no disq cap change

    if disq:
        _fundamental_final = min(_fundamental_pre, float(cap))
    else:
        _fundamental_final = _fundamental_pre
    tier = tier_label(final)

    return {
        "P1_Quality":    round(p1s, 2),
        "P2_Growth":     round(p2s, 2),
        "P3_Value":      round(p3s, 2),
        "P4_Discipline": round(p4s, 2),
        "P5_Size":       round(p5s, 2),
        "P6_Safety":     round(p6s, 2),
        "Base_Score":    round(base, 2),
        "WL_Penalty":    round(wl_pen, 2),
        "Bonus":         round(bonus, 2),
        "SCORE_V40":     round(final, 1),
        "Fundamental_Score": round(_fundamental_final, 1),   # V5-7: score excl. entry timing bonus
        "Entry_Bonus":   round(_entry_bonus, 2),
        "TIER_V40":      tier,
        "DISQ":          "; ".join(disq) if disq else "",
        "Entry_Signal":  entry_lbl,
        "Entry_Score":   round(entry_s, 2),
        "P1_Signals":    " | ".join(p1sig[:4]),
        "P2_Signals":    " | ".join(p2sig[:4]),
        "P3_Signals":    " | ".join(p3sig[:4]),
        "P4_Signals":    " | ".join(p4sig[:4]),
        "P5_Signals":    " | ".join(p5sig[:3]),
        "P6_Signals":    " | ".join(p6sig[:4]),
        "ALL_SIGNALS":   " | ".join((p1sig + p2sig + p3sig + p4sig + p5sig + p6sig)[:10]),
        "FCFYield_Pct":  round(fcfy, 2) if ok2(fv(fcfy)) else np.nan,
        "FCFYield_Basis": fcfy_basis,
        "P1_Detail":     p1d, "P2_Detail": p2d, "P3_Detail": p3d,
        "P4_Detail":     p4d, "P5_Detail": p5d, "P6_Detail": p6d,
    }


# ──────────────────────────────────────────────────────────────────────────────
# SCREENER PIPELINE
# ──────────────────────────────────────────────────────────────────────────────


# ──────────────────────────────────────────────────────────────────────────────
# LIVE FETCH ENGINE  (yfinance → Screener.in column schema)
# ──────────────────────────────────────────────────────────────────────────────

def _yf_row(idx, candidates) -> list:
    """Return column-ordered values for first matching row in a DataFrame."""
    for name in candidates:
        for i in idx:
            if name.lower() in str(i).lower():
                return idx[i] if hasattr(idx, '__getitem__') else []
    return []

def _fin_val(df, candidates, col=0):
    """Get a single float from financials/balance_sheet/cashflow df."""
    if df is None or df.empty:
        return np.nan
    for name in candidates:
        for idx in df.index:
            if name.lower() in str(idx).lower():
                try:
                    vals = df.loc[idx].values
                    v = float(vals[col]) if col < len(vals) else np.nan
                    return v if np.isfinite(v) else np.nan
                except:
                    pass
    return np.nan

def _calc_pio(info: dict, fin, bs, cf) -> float:
    """Compute Piotroski F-Score (0-9) from yfinance statements."""
    score = 0
    try:
        roa = info.get("returnOnAssets") or np.nan
        if not np.isnan(roa) and roa > 0: score += 1          # F1 ROA>0

        cfo = _fin_val(cf, ["Operating Cash Flow","Total Cash From Operating Activities","Cash From Operations"])
        if not np.isnan(cfo) and cfo > 0: score += 1           # F2 CFO>0

        # F3 delta ROA
        ni0 = _fin_val(fin, ["Net Income","Net Income Common Stockholders"])
        ni1 = _fin_val(fin, ["Net Income","Net Income Common Stockholders"], col=1)
        ta0 = _fin_val(bs,  ["Total Assets"], col=0)
        ta1 = _fin_val(bs,  ["Total Assets"], col=1)
        if all(not np.isnan(x) for x in [ni0,ni1,ta0,ta1]) and ta0>0 and ta1>0:
            if (ni0/ta0) > (ni1/ta1): score += 1

        # F4 accruals
        if not np.isnan(cfo) and not np.isnan(ta0) and ta0>0 and not np.isnan(roa):
            if cfo/ta0 > roa: score += 1

        # F5 leverage
        ltd0 = _fin_val(bs, ["Long Term Debt","Long Term Debt And Capital Lease Obligation"])
        ltd1 = _fin_val(bs, ["Long Term Debt","Long Term Debt And Capital Lease Obligation"], col=1)
        if all(not np.isnan(x) for x in [ltd0,ltd1,ta0,ta1]) and ta0>0 and ta1>0:
            if ltd0/ta0 < ltd1/ta1: score += 1

        # F6 current ratio
        ca0 = _fin_val(bs, ["Current Assets","Total Current Assets"])
        ca1 = _fin_val(bs, ["Current Assets","Total Current Assets"], col=1)
        cl0 = _fin_val(bs, ["Current Liabilities","Total Current Liabilities"])
        cl1 = _fin_val(bs, ["Current Liabilities","Total Current Liabilities"], col=1)
        if all(not np.isnan(x) for x in [ca0,ca1,cl0,cl1]) and cl0>0 and cl1>0:
            if ca0/cl0 > ca1/cl1: score += 1

        # F7 no dilution (use diluted shares from income stmt)
        d0 = _fin_val(fin, ["Diluted Average Shares","Diluted Shares Outstanding"])
        d1 = _fin_val(fin, ["Diluted Average Shares","Diluted Shares Outstanding"], col=1)
        if not any(np.isnan(x) for x in [d0,d1]):
            if d0 <= d1 * 1.02: score += 1   # no dilution → award point
            # else: dilution detected — no point (Bug 2 fix: was incorrectly always +1)
        else:
            score += 1  # data unavailable → benefit of the doubt

        # F8 gross margin
        gp0 = _fin_val(fin, ["Gross Profit"])
        gp1 = _fin_val(fin, ["Gross Profit"], col=1)
        rv0 = _fin_val(fin, ["Total Revenue","Revenue"])
        rv1 = _fin_val(fin, ["Total Revenue","Revenue"], col=1)
        if all(not np.isnan(x) for x in [gp0,gp1,rv0,rv1]) and rv0>0 and rv1>0:
            if gp0/rv0 > gp1/rv1: score += 1

        # F9 asset turnover
        if all(not np.isnan(x) for x in [rv0,rv1,ta0,ta1]) and ta0>0 and ta1>0:
            if rv0/ta0 > rv1/ta1: score += 1

    except Exception:
        pass
    return float(score)



# ──────────────────────────────────────────────────────────────────────────────
# SCREENER.IN SCRAPER  — fills fields missing from yfinance
# ──────────────────────────────────────────────────────────────────────────────

_SCR_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.screener.in/",
}


def _num(txt: str) -> float:
    """Parse a messy Screener.in number string → float.
    Bug NEW-3 fix: handle Indian accounting negative notation (123.4) → -123.4
    """
    if not txt:
        return np.nan
    s = str(txt).replace(",", "").replace("₹", "").replace("%", "").strip()
    # Indian financial statements use parentheses for negatives: (45.67) means -45.67
    is_negative = s.startswith("(") and ")" in s
    if is_negative:
        s = "-" + s.replace("(", "").replace(")", "").strip()
    m = _re.search(r"[-+]?\d+\.?\d*", s)
    return float(m.group()) if m else np.nan


def _scrape_screener(sym: str, session: "requests.Session") -> dict:
    """
    Fetch https://www.screener.in/company/{SYM}/consolidated/ (fallback: standalone)
    and return a dict of missing fields mapped to Screener.in column names.
    Returns {} on failure.
    """
    if not _SCR_OK: return {}  # Bug 16 fix: guard before _BS reference
    result: dict = {}
    for suffix in ("consolidated/", ""):
        url = f"https://www.screener.in/company/{sym}/{suffix}"
        try:
            resp = session.get(url, timeout=12, headers=_SCR_HEADERS)
            if resp.status_code == 404:
                continue
            if resp.status_code != 200:
                break
            soup = _BS(resp.text, "html.parser")

            # ── Top Ratios bar ─────────────────────────────────────────────
            top = soup.select_one("#top-ratios")
            if top:
                for li in top.select("li"):
                    name_el = li.select_one(".name")
                    val_el  = li.select_one(".value, .number")
                    if not name_el or not val_el:
                        continue
                    key = name_el.get_text(strip=True).lower()
                    val = _num(val_el.get_text(strip=True))
                    if "industry pe" in key or "ind. pe" in key:
                        result["Industry PE"] = val
                    elif "stock p/e" in key or "stock pe" in key or key == "p/e":
                        if "Price to Earning" not in result:
                            result["Price to Earning"] = val
                    elif "book value" in key:
                        result["_BV_per_share"] = val   # store; Book value total needs shares
                    elif "dividend yield" in key or "div yield" in key:
                        result["Dividend yield"] = val
                    elif "roce" in key:
                        result["Return on capital employed"] = val
                    elif "roe" in key:
                        result["Return on equity"] = val
                    elif "roic" in key or "return on invested" in key or "return on capital" == key.strip():
                        result["Return on invested capital"] = val  # Bug 22b: scrape ROIC directly

            # ── Company Ratios section ─────────────────────────────────────
            # Screener shows a two-column ratio table under #company-ratios
            cr = soup.select_one("#company-ratios, .company-ratios")
            if cr:
                for li in cr.select("li"):
                    name_el = li.select_one(".name")
                    val_el  = li.select_one(".value, .number")
                    if not name_el or not val_el:
                        continue
                    key = name_el.get_text(strip=True).lower()
                    val = _num(val_el.get_text(strip=True))
                    if "piotroski" in key:
                        result["Piotroski score"] = val
                    elif "pledg" in key:
                        result["Pledged percentage"] = val
                    elif "interest coverage" in key or "int. coverage" in key:
                        result["Interest coverage ratio"] = val
                    elif "debt to equity" in key or "d/e" in key:
                        if "Debt to equity" not in result:
                            result["Debt to equity"] = val
                    elif "g factor" in key or "g-factor" in key:
                        result["G Factor"] = val
                    elif "rsi" in key:
                        result["RSI 14"] = val
                    elif "p/fcf" in key or "price to free" in key:
                        result["Price to Free Cash Flow"] = val
                    elif "evebitda" in key or "ev/ebitda" in key:
                        result["EVEBITDA"] = val
                    elif "ev/sales" in key or "ev to sales" in key:
                        result["EV to Sales"] = val
                    elif "peg" in key:
                        result["PEG Ratio"] = val
                    elif "roic" in key or "return on invested capital" in key:
                        result["Return on invested capital"] = val  # Bug 22b: direct ROIC
                    elif "return on net worth" in key or "ronw" in key:
                        result.setdefault("Return on equity", val)  # India term for ROE
                    elif "net profit margin" in key or "npm" in key:
                        result.setdefault("Net profit margin", val)
                    elif "opm" in key or "operating margin" in key:
                        result.setdefault("OPM", val)

            # ── Historical PE: robust multi-strategy extraction ───────────
            # Strategy 1: Screener.in shows median PE in the ratios list
            for el in soup.select("#company-ratios li, #top-ratios li"):
                name_el = el.select_one(".name")
                val_el  = el.select_one(".value, .number")
                if name_el and val_el:
                    label_txt = name_el.get_text(strip=True).lower()
                    if any(x in label_txt for x in ["median pe","hist pe","5yr pe","historical pe","med pe"]):
                        result.setdefault("Historical PE 5Years", _num(val_el.get_text(strip=True)))
            # Strategy 2: PE chart data-src JSON sometimes embeds median PE
            for tag in soup.select("[data-src]"):
                ds = tag.get("data-src","")
                if "pe" in ds.lower():
                    m_pe = _re.search(r'median["\s:]+([\d.]+)', ds, _re.I)
                    if m_pe:
                        result.setdefault("Historical PE 5Years", float(m_pe.group(1)))
            # Strategy 3: If current PE known + Industry PE known → use industry PE as proxy
            if "Historical PE 5Years" not in result and "Industry PE" in result:
                result.setdefault("Historical PE 5Years", result["Industry PE"])
            # Strategy 4: peers table — look for a row labeled 'median' (column, not header)
            peers = soup.select_one("#peers, .peers")
            if peers:
                for tr_p in peers.select("tr"):
                    first = tr_p.select_one("td, th")
                    if first and "median" in first.get_text(strip=True).lower():
                        cells_p = tr_p.select("td")
                        for c in cells_p:
                            val = _num(c.get_text(strip=True))
                            if not np.isnan(val) and 2 < val < 300:
                                result.setdefault("Historical PE 5Years", val)
                                break

            # ── Profit & Loss table  (growth CAGRs + OPM + Net Profit) ────
            pl = soup.select_one("#profit-loss")
            if pl:
                rows_pl = pl.select("tr")
                years_row = rows_pl[0] if rows_pl else None
                year_headers = []
                if years_row:
                    year_headers = [th.get_text(strip=True)
                                    for th in years_row.select("th")]

                for tr in rows_pl[1:]:
                    cells  = tr.select("td, th")
                    if not cells: continue
                    row_label = cells[0].get_text(strip=True).lower()
                    vals      = [_num(c.get_text(strip=True)) for c in cells[1:]]
                    non_nan   = [v for v in vals if not np.isnan(v)]

                    if "sales" in row_label or "revenue" in row_label:
                        # 5Y CAGR: compare oldest & newest non-nan
                        if len(non_nan) >= 6:
                            v_new, v_old = non_nan[-1], non_nan[-6]
                            if v_old > 0:
                                result.setdefault("Sales growth 5Years",
                                    ((v_new/v_old)**0.2 - 1)*100)
                        if non_nan:
                            result.setdefault("Sales growth", (
                                (non_nan[-1]-non_nan[-2])/abs(non_nan[-2])*100
                                if len(non_nan) >= 2 and non_nan[-2] != 0 else np.nan))

                    elif (("net profit" in row_label or "pat" in row_label)
                          and "growth" not in row_label):  # Bug NEW-2 fix: explicit parentheses
                        if len(non_nan) >= 6:
                            v_new, v_old = non_nan[-1], non_nan[-6]
                            if v_old != 0:
                                # Bug NEW-5 fix: abs(v_new) was masking loss-making companies
                                # CAGR only valid when both old and new are positive
                                if v_old > 0 and v_new > 0:
                                    _cagr5 = ((v_new / v_old) ** 0.2 - 1) * 100
                                elif v_old < 0 and v_new > 0:
                                    _cagr5 = 50.0   # recovery turnaround — positive signal, capped conservatively
                                else:
                                    _cagr5 = np.nan  # loss-making or profit→loss: undefined CAGR
                                result.setdefault("Profit growth 5Years", _cagr5)
                        if non_nan:
                            result.setdefault("Profit after tax", non_nan[-1])
                        if len(non_nan) >= 2 and non_nan[-2] != 0:
                            result.setdefault("Profit growth",
                                (non_nan[-1]-non_nan[-2])/abs(non_nan[-2])*100)

                    elif "opm" in row_label or "operating profit margin" in row_label:
                        if non_nan:
                            result.setdefault("OPM", non_nan[-1])

                    elif "net profit margin" in row_label or "npm" in row_label:
                        if non_nan:
                            result.setdefault("Net profit margin", non_nan[-1])

                    elif "eps" in row_label:
                        if non_nan:
                            result.setdefault("_EPS_latest", non_nan[-1])

                    elif "interest" in row_label and "coverage" not in row_label:
                        # Store raw interest values; ICR computed after EBIT row found
                        if non_nan:
                            result["_interest_latest"] = non_nan[-1]  # latest year
                    elif "ebit" in row_label or ("operating profit" in row_label and "margin" not in row_label):
                        if non_nan:
                            result["_ebit_latest"] = non_nan[-1]

            # ── ICR: compute from same-period EBIT and Interest ────────────
            _ebit_l = result.pop("_ebit_latest", None)
            _int_l  = result.pop("_interest_latest", None)
            if _ebit_l and _int_l and _int_l != 0 and _ebit_l > 0:
                result.setdefault("Interest coverage ratio", _ebit_l / _int_l)

            # ── Cash Flow table ────────────────────────────────────────────
            cf_table = soup.select_one("#cash-flow")
            if cf_table:
                rows_cf = cf_table.select("tr")
                for tr in rows_cf[1:]:
                    cells = tr.select("td, th")
                    if not cells: continue
                    label = cells[0].get_text(strip=True).lower()
                    vals  = [_num(c.get_text(strip=True)) for c in cells[1:]]
                    non_nan = [v for v in vals if not np.isnan(v)]
                    if "operating" in label or "cfo" in label:
                        if non_nan:
                            result.setdefault("Cash from operations last year", non_nan[-1])
                    elif "free cash" in label or "fcf" in label:
                        if non_nan:
                            result.setdefault("Free cash flow last year", non_nan[-1])
                        if len(non_nan) >= 3:
                            result.setdefault("Free cash flow 3years",
                                              sum(non_nan[-3:]) / 3)

            # ── Balance Sheet ──────────────────────────────────────────────
            bs_table = soup.select_one("#balance-sheet")
            if bs_table:
                rows_bs = bs_table.select("tr")
                for tr in rows_bs[1:]:
                    cells = tr.select("td, th")
                    if not cells: continue
                    label = cells[0].get_text(strip=True).lower()
                    vals  = [_num(c.get_text(strip=True)) for c in cells[1:]]
                    non_nan = [v for v in vals if not np.isnan(v)]
                    if "total assets" in label or "balance sheet size" in label:
                        if len(non_nan) >= 2 and non_nan[-2] != 0:
                            result.setdefault("Asset growth",
                                (non_nan[-1]-non_nan[-2])/abs(non_nan[-2])*100)
                            result.setdefault("Total assets growth",
                                result["Asset growth"])
                    elif "borrowings" in label or "total debt" in label:
                        if len(non_nan) >= 2 and non_nan[-2] != 0:
                            result.setdefault("_debt_growth",
                                (non_nan[-1]-non_nan[-2])/abs(non_nan[-2])*100)
                    elif "book value" in label:
                        if non_nan:
                            result.setdefault("Book value", non_nan[-1])

            # ── Shareholding pattern ───────────────────────────────────────
            # Multiple tables under #shareholding (one per quarter)
            sh_section = soup.select_one("#shareholding")
            if sh_section:
                sh_tables = sh_section.select("table")
                if sh_tables:
                    # Use first table (most recent quarters, columns = dates)
                    t0 = sh_tables[0]
                    headers = [th.get_text(strip=True)
                               for th in t0.select("thead th")]
                    n_cols = len(headers)
                    prom_vals = fii_vals = dii_vals = []
                    for tr in t0.select("tbody tr"):
                        cells = tr.select("td")
                        if not cells: continue
                        label = cells[0].get_text(strip=True).lower()
                        vals  = [_num(c.get_text(strip=True)) for c in cells[1:]]
                        if "promoter" in label:
                            prom_vals = [v for v in vals if not np.isnan(v)]
                        elif "fii" in label or "foreign" in label:
                            fii_vals  = [v for v in vals if not np.isnan(v)]
                        elif "dii" in label or "domestic" in label:
                            dii_vals  = [v for v in vals if not np.isnan(v)]

                    if prom_vals:
                        result["Promoter holding"] = prom_vals[0]
                        if len(prom_vals) >= 2:
                            result["Change in promoter holding"] = (
                                prom_vals[0] - prom_vals[1])
                    if fii_vals:
                        result["FII holding"] = fii_vals[0]
                        if len(fii_vals) >= 2:
                            result["Change in FII holding"] = (
                                fii_vals[0] - fii_vals[1])
                    if dii_vals:
                        result["DII holding"] = dii_vals[0]

            # ── Quarterly results (latest quarter PAT, RSI-like momentum) ─
            qt = soup.select_one("#quarters")
            if qt:
                rows_qt = qt.select("tr")
                for tr in rows_qt:
                    cells = tr.select("td, th")
                    if not cells: continue
                    label = cells[0].get_text(strip=True).lower()
                    vals  = [_num(c.get_text(strip=True)) for c in cells[1:]]
                    non_nan = [v for v in vals if not np.isnan(v)]
                    if "net profit" in label or "pat" in label:
                        if non_nan:
                            result.setdefault("Net Profit latest quarter", non_nan[-1])

            # ── Historical PE from dedicated ratios row ────────────────────
            # Screener shows median PE over 5Y in the PE chart section
            # Sometimes accessible via a data-src JSON or table row
            for tag in soup.select("[data-field]"):
                field = tag.get("data-field", "").lower()
                val   = _num(tag.get_text(strip=True))
                if "median pe" in field or "hist pe" in field:
                    result.setdefault("Historical PE 5Years", val)

            # If we got any meaningful data, stop trying consolidated/standalone
            if result:
                break

        except Exception:
            break

    return result

# ── Optional jugaad-data fallback — market-history backup for NSE symbols ──
def _jgd_standardize_hist(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame()
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    cols_up = {str(c).strip().upper(): c for c in out.columns}

    def _pick(*names):
        canon = lambda s: str(s).upper().replace(" ", "").replace("_", "")
        wanted = {canon(n) for n in names}
        for raw in out.columns:
            if canon(raw) in wanted:
                return raw
        for raw in out.columns:
            c = canon(raw)
            for n in names:
                cn = canon(n)
                if cn in c or c in cn:
                    return raw
        return None

    mapping = {}
    for std, names in {
        "Date": ["DATE", "TIMESTAMP", "DATE1", "TRADEDATE"],
        "Open": ["OPEN"],
        "High": ["HIGH"],
        "Low": ["LOW"],
        "Close": ["CLOSE", "LAST", "LTP"],
        "PrevClose": ["PREVCLOSE", "PREV CLOSE"],
        "Volume": ["TOTTRDQTY", "VOLUME", "TTL_TRD_QNTY"],
    }.items():
        p = _pick(*names)
        if p:
            mapping[p] = std
    out = out.rename(columns=mapping)
    if "Date" in out.columns:
        out["Date"] = pd.to_datetime(out["Date"], errors="coerce")
        out = out.sort_values("Date")
    for c in ["Open", "High", "Low", "Close", "PrevClose", "Volume"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    return out.reset_index(drop=True)


def _fetch_jugaad_snapshot(sym: str, lookback_days: int = 370) -> dict:
    """Best-effort market-data fallback using jugaad-data.
    Does NOT replace fundamentals; only fills price/history-derived fields.
    """
    if not _JGD_OK or _jgd_stock_df is None:
        return {}
    fd = _date.today() - _timedelta(days=max(int(lookback_days), 200))
    td = _date.today()
    raw = None
    calls = [
        lambda: _jgd_stock_df(symbol=sym, from_date=fd, to_date=td, series="EQ"),
        lambda: _jgd_stock_df(sym, fd, td, series="EQ"),
        lambda: _jgd_stock_df(sym, fd, td),
    ]
    for fn in calls:
        try:
            raw = fn()
            if raw is not None:
                break
        except Exception:
            continue
    hist = _jgd_standardize_hist(raw)
    if hist.empty or "Close" not in hist.columns:
        return {}
    close = hist["Close"].dropna()
    if close.empty:
        return {}
    out = {
        "price": float(close.iloc[-1]),
        "wk52h": float(hist["High"].max()) if "High" in hist.columns and hist["High"].notna().any() else np.nan,
        "wk52l": float(hist["Low"].min()) if "Low" in hist.columns and hist["Low"].notna().any() else np.nan,
        "rsi_14": np.nan,
        "six_mo": np.nan,
        "source": "jugaad-data",
    }
    if len(close) >= 15:
        d = close.diff()
        g = d.clip(lower=0).ewm(span=14, adjust=False).mean()
        lo = (-d.clip(upper=0)).ewm(span=14, adjust=False).mean()
        rs = g / lo
        rsi_s = 100 - (100 / (1 + rs))
        try:
            rsi_v = float(rsi_s.iloc[-1])
            out["rsi_14"] = rsi_v if np.isfinite(rsi_v) else np.nan
        except Exception:
            pass
    if len(close) >= 60:
        idx6 = max(0, len(close) - 126)
        try:
            out["six_mo"] = (float(close.iloc[-1]) / float(close.iloc[idx6]) - 1.0) * 100.0
        except Exception:
            pass
    return out


# ── NSE direct quote API — used as price/MCap fallback when yfinance is rate-limited ──
_NSE_QUOTE_FAST = "https://www.nseindia.com/api/quote-equity?symbol={sym}"
_NSE_PRICE_CACHE: dict = {}
# sym → {"price": float, "mcap_cr": float, "wk52h": float, "wk52l": float}
# Populated by _nse_price_prefetch Phase 0; used as guaranteed fallback in _fetch_one_yf


def _nse_price_prefetch(syms: list) -> None:
    """
    Pre-populate _NSE_PRICE_CACHE with price+MCap from NSE quote-equity API.
    Called once before Phase 1 to give yfinance a fallback for rate-limited stocks.
    Uses a single session with NSE cookies.
    """
    if not _SCR_OK:
        return
    try:
        s = requests.Session()
        s.headers.update(_NSE_HEADERS)
        s.get("https://www.nseindia.com/", timeout=8)
        for sym in syms:
            try:
                r = s.get(_NSE_QUOTE_FAST.format(sym=sym), timeout=5)
                if r.status_code == 200:
                    d = r.json()
                    pi = d.get("priceInfo", {})
                    price = (pi.get("lastPrice") or pi.get("close") or
                             d.get("underlyingValue") or
                             d.get("lastPrice"))
                    mcap_raw = (d.get("industryInfo", {}).get("marketCap") or
                                d.get("securityInfo", {}).get("issuedCap") or
                                d.get("marketCapFull") or 0)
                    if price and float(price) > 0:
                        # Also extract 52W High/Low from priceInfo.weekHighLow
                        _whl = pi.get("weekHighLow") or pi.get("weekhighLow") or {}
                        _wh = _whl.get("max") or _whl.get("maxValue") or pi.get("weekHigh52") or 0
                        _wl = _whl.get("min") or _whl.get("minValue") or pi.get("weekLow52") or 0
                        _NSE_PRICE_CACHE[sym] = {
                            "price":   float(price),
                            "mcap_cr": float(mcap_raw) / 1e7 if mcap_raw else np.nan,
                            "wk52h":   float(_wh) if _wh and float(_wh) > 0 else np.nan,
                            "wk52l":   float(_wl) if _wl and float(_wl) > 0 else np.nan,
                        }
                time.sleep(0.05)
            except Exception:
                continue
    except Exception:
        pass


def _fetch_one_yf(sym: str) -> dict:
    """
    Fetch yfinance data for a single NSE symbol.
    Retries up to 3× with exponential backoff to handle Yahoo rate-limiting.
    Falls back to NSE price cache and optional jugaad-data market history.
    Returns row dict or {} on complete failure.
    """
    info = {}
    t = None
    jgd_snapshot = {}
    if _YF_OK:
        for attempt in range(3):
            try:
                t = _safe_yf_ticker(sym, f"phase_1_ticker_attempt_{attempt + 1}")
                info = _safe_yf_info(t, sym, f"phase_1_info_attempt_{attempt + 1}")
                price_raw = info.get("currentPrice") or info.get("regularMarketPrice")
                if price_raw and float(price_raw) > 0:
                    break   # good response
                # Empty info → likely rate-limited; back off and retry
                time.sleep(0.4 * (2 ** attempt))   # 0.4s, 0.8s, 1.6s
            except Exception:
                time.sleep(0.4 * (2 ** attempt))

    try:
        price_raw = info.get("currentPrice") or info.get("regularMarketPrice")
        if (price_raw is None or (isinstance(price_raw, (int, float)) and float(price_raw) == 0)) and _JGD_OK:
            jgd_snapshot = _fetch_jugaad_snapshot(sym)
            if jgd_snapshot:
                price_raw = jgd_snapshot.get("price")
        # Fallback: NSE price cache (populated by _nse_price_prefetch)
        _nse_cached = _NSE_PRICE_CACHE.get(sym)
        # Normalise: cache is now a dict (was tuple in older code)
        if isinstance(_nse_cached, (tuple, list)):
            _nse_cached = {"price": _nse_cached[0], "mcap_cr": _nse_cached[1],
                           "wk52h": np.nan, "wk52l": np.nan}
        if (price_raw is None or float(price_raw) == 0) and _nse_cached:
            price_raw = _nse_cached.get("price") if isinstance(_nse_cached, dict) else _nse_cached[0]

        # Bug 17 fix: robust None/non-numeric guard before float()
        if price_raw is None:
            return {}
        try:
            price_f = float(price_raw)
        except (TypeError, ValueError):
            return {}
        if np.isnan(price_f) or price_f == 0:
            return {}

        mcap_inr = float(info.get("marketCap") or 0)
        if mcap_inr:
            mcap_cr = mcap_inr / 1e7
        elif _nse_cached and isinstance(_nse_cached, dict) and not np.isnan(_nse_cached.get("mcap_cr", np.nan)):
            mcap_cr = _nse_cached["mcap_cr"]  # NSE fallback MCap
        elif _nse_cached and isinstance(_nse_cached, (tuple,list)) and _nse_cached[1] and not np.isnan(_nse_cached[1]):
            mcap_cr = _nse_cached[1]  # legacy tuple fallback
        else:
            mcap_cr = np.nan

        def _f(k): return float(info.get(k) or np.nan)
        pe     = _f("trailingPE"); peg  = _f("pegRatio")
        ev_eb  = _f("enterpriseToEbitda"); ev_sal = _f("enterpriseToRevenue")
        div_y  = float(info.get("dividendYield") or 0) * 100
        roe    = _f("returnOnEquity")
        roe    = roe * 100 if not np.isnan(roe) else np.nan
        de_raw = float(info.get("debtToEquity") or 0)
        # yfinance 0.2+ returns as ratio (e.g. 0.75); older returns 75.0
        de     = de_raw / 100 if de_raw > 20 else de_raw  # auto-detect format
        opm    = _f("operatingMargins")
        opm    = opm * 100 if not np.isnan(opm) else np.nan
        npm    = _f("profitMargins")
        npm    = npm * 100 if not np.isnan(npm) else np.nan
        rev_g  = _f("revenueGrowth")
        rev_g  = rev_g * 100 if not np.isnan(rev_g) else np.nan
        # Bug H fix: earningsGrowth = quarterly YoY, mismatched with Screener.in TTM annual
        # Compute TTM PAT growth from annual financials (fin columns = annual periods)
        try:
            ni0 = _fin_val(fin if 'fin' in dir() else None,
                           ["Net Income","Net Income Common Stockholders","Net Income From Continuing Operations"])
            ni1 = _fin_val(fin if 'fin' in dir() else None,
                           ["Net Income","Net Income Common Stockholders","Net Income From Continuing Operations"], col=1)
            if not np.isnan(ni0) and not np.isnan(ni1) and ni1 != 0:
                earn_g = (ni0 - ni1) / abs(ni1) * 100   # annual YoY PAT growth
            else:
                earn_g = _f("earningsGrowth")
                earn_g = earn_g * 100 if not np.isnan(earn_g) else np.nan
        except Exception:
            earn_g = _f("earningsGrowth")
            earn_g = earn_g * 100 if not np.isnan(earn_g) else np.nan
        bv_ps  = _f("bookValue"); shares = _f("sharesOutstanding")
        # FIX-1: t.fast_info.year_high/year_low is lightweight + reliable for .NS tickers.
        # yfinance info["fiftyTwoWeekHigh"] returns 0/NaN for NSE — long-standing bug.
        wk52h = np.nan; wk52l = np.nan
        try:
            if t is not None:
                fi = _safe_yf_fast_info(t, sym, "phase_1_fast_info")
                if hasattr(fi, "year_high") and fi.year_high and float(fi.year_high) > 0:
                    wk52h = float(fi.year_high)
                if hasattr(fi, "year_low") and fi.year_low and float(fi.year_low) > 0:
                    wk52l = float(fi.year_low)
        except Exception:
            pass
        # Fallback: info dict (keep for non-NSE tickers that work fine)
        if np.isnan(wk52h):
            try:
                _rh = float(info.get("fiftyTwoWeekHigh") or 0)
                if _rh > 0: wk52h = _rh
            except Exception: pass
        if np.isnan(wk52l):
            try:
                _rl = float(info.get("fiftyTwoWeekLow") or 0)
                if _rl > 0: wk52l = _rl
            except Exception: pass
        # Compute D/E from balance sheet if info D/E is missing
        _de_bs = np.nan
        try:
            _td = _fin_val(bs, ["Total Debt", "Long Term Debt", "Total Long Term Debt"])
            _eq = _fin_val(bs, ["Stockholders Equity", "Total Stockholder Equity",
                                 "Common Stock Equity", "Total Equity Gross Minority Interest"])
            if not np.isnan(_td) and not np.isnan(_eq) and _eq > 0:
                _de_bs = _td / _eq
        except Exception:
            pass
        # Canonical FCF fields:
        # - info[freeCashflow] is usually trailing/TTM when available
        # - statement-derived cashflow is latest reported annual FCF
        fcf_i  = _f("freeCashflow"); cfo_i = _f("operatingCashflow")
        fcf_ttm_cr = fcf_i / 1e7 if not np.isnan(fcf_i) else np.nan
        cfo_cr = cfo_i / 1e7 if not np.isnan(cfo_i) else np.nan
        fcf_cr = np.nan  # latest annual FCF

        # Annual FCF from annual cashflow statement
        _fcf_from_stmt = np.nan
        try:
            _cf_tmp = _safe_yf_frame(t, "cashflow", sym, "phase_1_cashflow")   # reuse already-fetched ticker object
            _cfo_row = None; _capex_row = None; _fcf_row = None
            for idx in _cf_tmp.index:
                si = str(idx).lower()
                if "free cash flow" in si and _fcf_row is None:
                    _fcf_row = _cf_tmp.loc[idx]
                if any(x in si for x in ["operating cash", "cash from operations", "operating activities"]):
                    if _cfo_row is None: _cfo_row = _cf_tmp.loc[idx]
                elif any(x in si for x in ["capital expenditure", "capex", "purchase of property",
                                             "purchase of ppe", "acquisition of property"]):
                    if _capex_row is None: _capex_row = _cf_tmp.loc[idx]
            if _fcf_row is not None:
                _fcf_v = float(_fcf_row.iloc[0]) if np.isfinite(float(_fcf_row.iloc[0])) else np.nan
                if not np.isnan(_fcf_v):
                    _fcf_from_stmt = _fcf_v / 1e7
            elif _cfo_row is not None:
                _cfo_v = float(_cfo_row.iloc[0]) if np.isfinite(float(_cfo_row.iloc[0])) else np.nan
                _capex_v = float(_capex_row.iloc[0]) if (_capex_row is not None and
                           np.isfinite(float(_capex_row.iloc[0]))) else 0.0
                if not np.isnan(_cfo_v):
                    _fcf_from_stmt = (_cfo_v - abs(_capex_v)) / 1e7   # Cr
        except Exception:
            pass
        if not np.isnan(_fcf_from_stmt):
            fcf_cr = _fcf_from_stmt

        # TTM override from quarterly cashflow if vendor field is missing
        if np.isnan(fcf_ttm_cr):
            try:
                _qcf = _safe_yf_frame(t, "quarterly_cashflow", sym, "phase_1_quarterly_cashflow")
                _q_cfo_row = None; _q_capex_row = None; _q_fcf_row = None
                for idx in _qcf.index:
                    si = str(idx).lower()
                    if "free cash flow" in si and _q_fcf_row is None:
                        _q_fcf_row = _qcf.loc[idx]
                    if any(x in si for x in ["operating cash", "cash from operations", "operating activities"]):
                        if _q_cfo_row is None: _q_cfo_row = _qcf.loc[idx]
                    elif any(x in si for x in ["capital expenditure", "capex", "purchase of property",
                                                 "purchase of ppe", "acquisition of property"]):
                        if _q_capex_row is None: _q_capex_row = _qcf.loc[idx]
                if _q_fcf_row is not None:
                    _vals = [float(v) for v in _q_fcf_row.iloc[:4] if np.isfinite(float(v))]
                    if _vals:
                        fcf_ttm_cr = sum(_vals) / 1e7
                elif _q_cfo_row is not None:
                    _cfo_vals = [float(v) for v in _q_cfo_row.iloc[:4] if np.isfinite(float(v))]
                    _capex_vals = [float(v) for v in _q_capex_row.iloc[:4] if (_q_capex_row is not None and np.isfinite(float(v)))]
                    if _cfo_vals:
                        fcf_ttm_cr = (sum(_cfo_vals) - sum(abs(v) for v in _capex_vals)) / 1e7
            except Exception:
                pass

        # If only one flavour exists, reuse it as the fallback for legacy consumers.
        if np.isnan(fcf_cr) and not np.isnan(fcf_ttm_cr):
            fcf_cr = fcf_ttm_cr
        industry = info.get("industry") or info.get("sector") or "Unknown"
        name     = info.get("longName") or info.get("shortName") or sym
        eps      = _f("trailingEps")

        _fcf_pref = fcf_ttm_cr if not np.isnan(fcf_ttm_cr) else fcf_cr
        p_fcf  = (mcap_cr / _fcf_pref if not any(np.isnan(x) for x in [_fcf_pref, mcap_cr])
                  and _fcf_pref > 0 else np.nan)
        _fcfy_direct = (_fcf_pref / mcap_cr * 100
                        if not any(np.isnan(x) for x in [_fcf_pref, mcap_cr])
                        and mcap_cr > 0 else np.nan)
        graham = (math.sqrt(22.5 * eps * bv_ps)
                  if all(not np.isnan(x) for x in [eps, bv_ps]) and eps > 0 and bv_ps > 0
                  else np.nan)
        bv_cr  = (bv_ps * shares / 1e7
                  if all(not np.isnan(x) for x in [bv_ps, shares]) else np.nan)

        roce = roic = intcov = pat_cr = ebitda_g = asset_g = pio = np.nan
        pat5_yf = sal5_yf = np.nan  # Bug 18: 5Y CAGR from yfinance annuals

        fin = bs = cf = pd.DataFrame()
        try:
            if t is not None:
                fin = _safe_yf_frame(t, "financials", sym, "phase_1_financials")
                bs = _safe_yf_frame(t, "balance_sheet", sym, "phase_1_balance_sheet")
                cf = _safe_yf_frame(t, "cashflow", sym, "phase_1_cashflow_fundamentals")
            ebit   = _fin_val(fin, ["Operating Income","EBIT","Ebit"])
            dep    = _fin_val(fin, ["Reconciled Depreciation","Depreciation",
                                    "D&A","Depreciation And Amortization"])
            int_ex = _fin_val(fin, ["Interest Expense","Net Interest Income"])
            net_i  = _fin_val(fin, ["Net Income","Net Income Common Stockholders"])
            ta0    = _fin_val(bs,  ["Total Assets"])
            ta1    = _fin_val(bs,  ["Total Assets"], col=1)
            cl0    = _fin_val(bs,  ["Current Liabilities","Total Current Liabilities"])
            cash0  = _fin_val(bs,  ["Cash And Cash Equivalents",
                                    "Cash Cash Equivalents And Short Term Investments"])
            if not np.isnan(net_i):   pat_cr = net_i / 1e7
            if not np.isnan(ebit) and not np.isnan(int_ex) and int_ex != 0:
                intcov = abs(ebit / int_ex)
            if all(not np.isnan(x) for x in [ebit, ta0, cl0]) and (ta0 - cl0) > 0:
                roce = ebit / (ta0 - cl0) * 100
            if all(not np.isnan(x) for x in [ebit, ta0, cash0, cl0]):
                inv_cap = ta0 - cash0 - cl0
                if inv_cap > 0:
                    roic = ebit * 0.75 / inv_cap * 100  # Bug 22: approx (assumes 25% tax); screener.in direct ROIC preferred via _PREFER_SCR
            ebit1 = _fin_val(fin, ["Operating Income","EBIT","Ebit"], col=1)
            dep1  = _fin_val(fin, ["Reconciled Depreciation","Depreciation"], col=1)
            if all(not np.isnan(x) for x in [ebit, dep, ebit1, dep1]):
                eb0 = ebit + dep; eb1 = ebit1 + dep1
                if eb1 != 0: ebitda_g = (eb0 - eb1) / abs(eb1) * 100
            if not np.isnan(ta0) and not np.isnan(ta1) and ta1 != 0:
                asset_g = (ta0 - ta1) / abs(ta1) * 100
            pio = _calc_pio(info, fin, bs, cf)

            # ── Bug 18 fix: 5Y PAT CAGR + 5Y Sales CAGR from yfinance annuals ──
            # yfinance gives up to 4 annual columns (newest → oldest in fin.columns)
            # Use oldest available as base; compute annualised CAGR
            try:
                ni_row = None
                for cand in ["Net Income","Net Income Common Stockholders","Net Income From Continuing Operations"]:
                    for idx in fin.index:
                        if cand.lower() in str(idx).lower():
                            ni_row = fin.loc[idx]; break
                    if ni_row is not None: break
                if ni_row is not None:
                    ni_vals = [float(v) for v in ni_row.values if np.isfinite(float(v))]
                    if len(ni_vals) >= 3:
                        # newest is index 0, oldest is last
                        ni_new, ni_old = ni_vals[0], ni_vals[-1]
                        n_yrs = len(ni_vals) - 1  # 1, 2, or 3 years
                        if ni_old > 0 and ni_new > 0:
                            pat5_yf = ((ni_new / ni_old) ** (1.0 / n_yrs) - 1) * 100
                        elif ni_old < 0 and ni_new > 0:
                            pat5_yf = 50.0   # recovery — positive signal, conservative cap
                        else:
                            pat5_yf = ((abs(ni_new) / max(abs(ni_old), 1)) ** (1.0 / n_yrs) - 1) * 100 * (-1 if ni_new < 0 else 1)
                        pat5_yf = float(np.clip(pat5_yf, -100, 200))
                    else:
                        pat5_yf = np.nan
                else:
                    pat5_yf = np.nan
            except Exception:
                pat5_yf = np.nan

            try:
                rev_row = None
                for cand in ["Total Revenue","Revenue","Net Revenue"]:
                    for idx in fin.index:
                        if cand.lower() in str(idx).lower():
                            rev_row = fin.loc[idx]; break
                    if rev_row is not None: break
                if rev_row is not None:
                    rev_vals = [float(v) for v in rev_row.values if np.isfinite(float(v))]
                    if len(rev_vals) >= 3:
                        rev_new, rev_old = rev_vals[0], rev_vals[-1]
                        n_yrs_r = len(rev_vals) - 1
                        if rev_old > 0 and rev_new > 0:
                            sal5_yf = ((rev_new / rev_old) ** (1.0 / n_yrs_r) - 1) * 100
                        else:
                            sal5_yf = np.nan
                        sal5_yf = float(np.clip(sal5_yf, -100, 200))
                    else:
                        sal5_yf = np.nan
                else:
                    sal5_yf = np.nan
            except Exception:
                sal5_yf = np.nan

        except Exception:
            pat5_yf = sal5_yf = np.nan

        # ── Compute RSI-14, 6M return, 52W High/Low from a single 1Y price fetch ──
        six_mo = rsi_14 = hist_pe_5y = np.nan
        wk52h_hist = wk52l_hist = np.nan   # computed from history (more reliable for NSE)
        try:
            # FIX-2: explicit None/empty check — rate-limited calls return empty DF, not exception
            hist1y = _safe_yf_history(t, sym, "phase_1_history_1y", period="1y", auto_adjust=True, timeout=15)
            if hist1y is None: hist1y = pd.DataFrame()
            # V5-9: guard lowered to >=2 (was >5) — new listings have few rows;
            #       each sub-computation guarded by its own minimum row count
            if not hist1y.empty and len(hist1y) >= 2:
                # 52W High/Low — only need 1+ row; max/min of any history is valid
                wk52h_hist = float(hist1y["High"].max())
                wk52l_hist = float(hist1y["Low"].min())
                # 6-month return — needs 60+ trading days (≈3 months min for stability)
                if len(hist1y) >= 60:
                    six_mo_idx = max(0, len(hist1y) - 126)
                    six_mo = (hist1y["Close"].iloc[-1] / hist1y["Close"].iloc[six_mo_idx] - 1) * 100
                # RSI 14 — minimum 15 rows for Wilder EMA to be meaningful
                if len(hist1y) >= 15:
                    delta = hist1y["Close"].diff()
                    gain  = delta.clip(lower=0).ewm(span=14, adjust=False).mean()
                    loss  = (-delta.clip(upper=0)).ewm(span=14, adjust=False).mean()
                    rs    = gain / loss
                    rsi_s = 100 - (100 / (1 + rs))
                    rsi_14 = float(rsi_s.iloc[-1])
                    if not np.isfinite(rsi_14): rsi_14 = np.nan
        except Exception:
            pass
        # Priority: hist1y (most accurate) → yfinance info → NSE pre-fetch cache
        if np.isfinite(wk52h_hist): wk52h = wk52h_hist
        if np.isfinite(wk52l_hist): wk52l = wk52l_hist
        # FIX-B: NSE cache guaranteed fallback for rate-limited stocks
        _nc = _NSE_PRICE_CACHE.get(sym)
        if isinstance(_nc, (tuple, list)):
            _nc = {"wk52h": np.nan, "wk52l": np.nan}
        if _nc:
            if (np.isnan(wk52h) or wk52h <= 0) and not np.isnan(_nc.get("wk52h", np.nan)):
                wk52h = _nc["wk52h"]
            if (np.isnan(wk52l) or wk52l <= 0) and not np.isnan(_nc.get("wk52l", np.nan)):
                wk52l = _nc["wk52l"]
        if ((np.isnan(wk52h) or wk52h <= 0 or np.isnan(wk52l) or wk52l <= 0 or np.isnan(rsi_14) or np.isnan(six_mo))
                and _JGD_OK and not jgd_snapshot):
            jgd_snapshot = _fetch_jugaad_snapshot(sym)
        if jgd_snapshot:
            if (np.isnan(wk52h) or wk52h <= 0) and np.isfinite(jgd_snapshot.get("wk52h", np.nan)):
                wk52h = float(jgd_snapshot["wk52h"])
            if (np.isnan(wk52l) or wk52l <= 0) and np.isfinite(jgd_snapshot.get("wk52l", np.nan)):
                wk52l = float(jgd_snapshot["wk52l"])
            if np.isnan(rsi_14) and np.isfinite(jgd_snapshot.get("rsi_14", np.nan)):
                rsi_14 = float(jgd_snapshot["rsi_14"])
            if np.isnan(six_mo) and np.isfinite(jgd_snapshot.get("six_mo", np.nan)):
                six_mo = float(jgd_snapshot["six_mo"])

        # Historical PE 5Y — median trailing PE over 5Y price history (constant-EPS approx)
        try:
            hist5y = _safe_yf_history(t, sym, "phase_1_history_5y", period="5y")
            if not hist5y.empty and not np.isnan(eps) and eps > 0 and len(hist5y) > 250:
                pe_ts = hist5y["Close"] / eps
                pe_valid = pe_ts[(pe_ts > 1) & (pe_ts < 500)]
                if len(pe_valid) > 50:
                    hist_pe_5y = float(pe_valid.median())
        except Exception:
            pass

        # FCF 3Y — sum 3 years of free cash flow from cashflow statement
        fcf_3y_cr = np.nan
        try:
            cf_row = None
            for cand in ["Free Cash Flow", "Capital Expenditure"]:
                for idx in cf.index:
                    if cand.lower() in str(idx).lower():
                        cf_row = cf.loc[idx]; break
                if cf_row is not None: break
            # Prefer direct FCF row; else compute CFO - CapEx
            fcf_direct = None
            for idx in cf.index:
                if "free cash flow" in str(idx).lower():
                    fcf_direct = cf.loc[idx]; break
            if fcf_direct is not None:
                fcf3_vals = [float(v) for v in fcf_direct.values[:3] if np.isfinite(float(v))]
                if fcf3_vals:
                    fcf_3y_cr = sum(fcf3_vals) / 1e7  # Cr
            elif not np.isnan(fcf_cr):
                # fallback: 1Y FCF × 3 as rough proxy
                fcf_3y_cr = fcf_cr * 3
        except Exception:
            pass

        return {
            "Name": name, "NSE Code": sym, "Industry": industry,
            "Market Capitalization": mcap_cr, "Current Price": price_f,
            "Price to Earning": pe, "Industry PE": np.nan, "PEG Ratio": peg,
            "Historical PE 5Years": hist_pe_5y,
            "Return on capital employed": roce, "Return on equity": roe,
            "Return on invested capital": roic,
            "Profit growth 5Years": pat5_yf, "Sales growth 5Years": sal5_yf,  # Bug 18: computed from yfinance annual statements; screener.in overrides if available
            "Profit growth": earn_g, "Sales growth": rev_g,
            "Debt to equity": de if not np.isnan(de) else _de_bs, "Pledged percentage": np.nan,
            "Piotroski score": pio, "G Factor": np.nan,
            "Free cash flow TTM": fcf_ttm_cr,
            "Free cash flow last year": fcf_cr, "Free cash flow 3years": fcf_3y_cr, "_FCFYield_Direct": _fcfy_direct,
            "Price to Free Cash Flow": p_fcf, "Graham Number": graham,
            "Book value": bv_cr,
            "Promoter holding": np.nan, "DII holding": np.nan, "FII holding": np.nan,
            "Change in promoter holding": np.nan, "Change in FII holding": np.nan,
            "EVEBITDA": ev_eb, "EV to Sales": ev_sal,
            "Net Profit latest quarter": np.nan,
            "Profit after tax": pat_cr, "Dividend yield": div_y,
            "Interest coverage ratio": intcov,
            "Cash from operations last year": cfo_cr,
            "52 Week High": wk52h, "52 Week Low": wk52l,
            "Asset growth": asset_g, "Total assets growth": asset_g,
            "EBITDA growth": ebitda_g, "Net profit margin": npm, "OPM": opm,
            "RSI 14": rsi_14, "6 Month Return": six_mo,
        }
    except Exception:
        return {}



# ──────────────────────────────────────────────────────────────────────────────
# MULTI-SOURCE ENRICHMENT — NSE API • BSE API • Trendlyne • Screener.in fallback
# Priority: yfinance (P1) → NSE API (P2a) → Trendlyne (P2b) → Screener.in (P2c)
# ──────────────────────────────────────────────────────────────────────────────

_NSE_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.nseindia.com/",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
}

_BSE_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.bseindia.com/",
}

_NSE_SHP_URL   = "https://www.nseindia.com/api/corporates-shp?symbol={sym}&issueType=EQ"
_NSE_QUOTE_URL = "https://www.nseindia.com/api/quote-equity?symbol={sym}"
_BSE_SHP_URL   = "https://api.bseindia.com/BseIndiaAPI/api/SHPMain/w?scripcode={bsecode}&type=C"
_TREND_URL     = "https://trendlyne.com/fundamentals/stock/{sym}/"


def _make_nse_session() -> "requests.Session":
    """Bootstrap a requests.Session with NSE cookies (required for API calls)."""
    if not _SCR_OK:
        return None
    try:
        s = requests.Session()
        s.headers.update(_NSE_HEADERS)
        s.get("https://www.nseindia.com/", timeout=8)
        return s
    except Exception:
        return None


def _fetch_nse_data(sym: str, session=None) -> dict:
    """
    Fetch shareholding (Promoter/FII/DII/Pledged) + Industry PE from NSE APIs.
    Uses two endpoints: corporates-shp and quote-equity.
    Returns {} on any failure.
    """
    if not _SCR_OK:
        return {}
    result: dict = {}
    try:
        s = session or _make_nse_session()
        if s is None:
            return {}

        # ── SHP endpoint: Promoter + Pledge ───────────────────────────────
        try:
            r = s.get(_NSE_SHP_URL.format(sym=sym), timeout=8)
            if r.status_code == 200:
                data = r.json()
                # NSE returns list or {"data": [...]}
                records = (data if isinstance(data, list)
                           else data.get("data", []) if isinstance(data, dict)
                           else [])
                if records:
                    latest = records[0]  # most recent quarter first
                    # Promoter holding — try multiple field name variants
                    for key in ("promoterAndPromoterGroupShareholding",
                                "promoter_and_promoter_group",
                                "promoterHolding", "promoter"):
                        val = latest.get(key)
                        if val is not None:
                            result["Promoter holding"] = float(val)
                            break
                    # Pledged %
                    for key in ("pledgeSharePercentage", "pledgedPercentage",
                                "pledge", "totalPledgedShares"):
                        val = latest.get(key)
                        if val is not None:
                            result["Pledged percentage"] = float(val)
                            break
                    # Public = FII + DII + Retail; NSE sometimes gives breakdown
                    pub = latest.get("publicShareholding") or latest.get("public")
                    if pub:
                        result["_nse_public"] = float(pub)
        except Exception:
            pass

        # ── Quote-equity endpoint: Industry PE + FII/DII breakdown ────────
        try:
            r2 = s.get(_NSE_QUOTE_URL.format(sym=sym), timeout=8)
            if r2.status_code == 200:
                qd = r2.json()
                # Industry PE — nested in several possible paths
                for path in (
                    ["industryInfo", "peRatio"],
                    ["industryInfo", "pe"],
                    ["priceInfo", "industryPE"],
                    ["securityInfo", "industryPE"],
                    ["metadata", "pdSectPe"],
                ):
                    val = qd
                    try:
                        for k in path:
                            val = val[k]
                        if val and float(val) > 0:
                            result.setdefault("Industry PE", float(val))
                            break
                    except Exception:
                        continue

                # Shareholding from quote (backup to SHP endpoint)
                shp = (qd.get("shareholdingPattern") or
                       qd.get("shp") or {})
                for key in ("promoterAndPromoterGroupShareholding", "promoterHolding"):
                    if key in shp:
                        result.setdefault("Promoter holding", float(shp[key]))
                for key in ("fii", "fpiHolding", "foreignInstitutionalInvestors"):
                    if key in shp:
                        result.setdefault("FII holding", float(shp[key]))
                for key in ("dii", "diiHolding", "domesticInstitutionalInvestors"):
                    if key in shp:
                        result.setdefault("DII holding", float(shp[key]))
                for key in ("pledgeSharePercentage", "pledgedPercentage"):
                    if key in shp:
                        result.setdefault("Pledged percentage", float(shp[key]))

                # Promoter change QoQ — NSE sometimes gives prev quarter too
                if "promoterHoldingChange" in qd:
                    result["Change in promoter holding"] = float(qd["promoterHoldingChange"])

                # ── 52-Week High / Low ── (authoritative for NSE; yfinance often NaN)
                # NSE priceInfo.weekHighLow.max / .min  OR  .maxValue / .minValue
                try:
                    pi  = qd.get("priceInfo", {})
                    whl = pi.get("weekHighLow") or pi.get("weekhighLow") or {}
                    _wh = (whl.get("max") or whl.get("maxValue") or
                           pi.get("weekHigh52") or pi.get("52weekHigh"))
                    _wl = (whl.get("min") or whl.get("minValue") or
                           pi.get("weekLow52") or pi.get("52weekLow"))
                    if _wh and float(_wh) > 0:
                        result["52 Week High"] = float(_wh)
                    if _wl and float(_wl) > 0:
                        result["52 Week Low"] = float(_wl)
                except Exception:
                    pass

        except Exception:
            pass

    except Exception:
        pass

    return result


def _fetch_bse_shp(sym: str, bse_code: str = None) -> dict:
    """
    Fallback: fetch shareholding from BSE API.
    BSE requires a 6-digit script code; we try to guess from NSE symbol if not given.
    Returns {} on failure.
    """
    if not _SCR_OK or not bse_code:
        return {}
    result: dict = {}
    try:
        s = requests.Session()
        s.headers.update(_BSE_HEADERS)
        r = s.get(_BSE_SHP_URL.format(bsecode=bse_code), timeout=8)
        if r.status_code == 200:
            data = r.json()
            rows = data.get("Table", data.get("data", []))
            for row in rows:
                cat = str(row.get("category_of_shareholders", "")).lower()
                pct = row.get("percentage_of_total_shares") or row.get("pct", 0)
                if pct:
                    pct = float(pct)
                    if "promoter" in cat:
                        result.setdefault("Promoter holding", pct)
                    elif "foreign" in cat or "fii" in cat or "fpi" in cat:
                        result.setdefault("FII holding", pct)
                    elif "mutual fund" in cat or "insurance" in cat or "dii" in cat:
                        result.setdefault("DII holding", pct)
    except Exception:
        pass
    return result


def _fetch_trendlyne_gf(sym: str) -> float:
    """
    Scrape G-Factor (Greenblatt Magic Formula rank) from Trendlyne.
    Returns NaN on failure. Makes one GET request.
    """
    if not _SCR_OK:
        return np.nan
    try:
        s = requests.Session()
        s.headers.update(_SCR_HEADERS)
        r = s.get(_TREND_URL.format(sym=sym), timeout=8)
        if r.status_code != 200:
            return np.nan
        soup = _BS(r.text, "html.parser")
        # Trendlyne shows "G Factor" in a scorecard table or info panel
        for el in soup.find_all(string=_re.compile(r"g.?factor|magic.?formula|greenblatt",
                                                    _re.I)):
            parent = el.parent
            # Look for a sibling/nearby element with a number
            for sib in (parent.find_next_siblings() +
                        parent.parent.find_all(class_=_re.compile(r"value|score|num"))):
                txt = sib.get_text(strip=True)
                val = _num(txt)
                if not np.isnan(val) and 1 <= val <= 100:
                    return val
    except Exception:
        pass
    return np.nan


def _compute_gfactor_approx(roic: float, ev_ebitda: float) -> float:
    """
    Approximate G-Factor (Greenblatt) from ROIC rank + EV/EBITDA rank.
    Returns a 0–10 score (higher = better magic formula rank).
    Uses threshold-based scoring as a proxy for cross-sectional ranking.
    """
    if np.isnan(roic) and np.isnan(ev_ebitda):
        return np.nan
    score = 0.0
    if not np.isnan(roic):
        # ROIC component (earnings quality): higher ROIC = better
        score += min(5.0, max(0.0, (roic - 5) / 6))   # 0 at 5%, 5 at 35%+
    if not np.isnan(ev_ebitda):
        # EV/EBITDA component: lower = cheaper = better
        score += min(5.0, max(0.0, (30 - ev_ebitda) / 5))  # 5 at ≤5x, 0 at 30x+
    return round(float(np.clip(score, 0, 10)), 1)

def _enrich_screener_row(row_d: dict, sym: str) -> dict:
    """Legacy alias — calls _enrich_all_sources for backward compatibility."""
    return _enrich_all_sources(row_d, sym)


def _enrich_all_sources(row_d: dict, sym: str, nse_sess=None) -> dict:
    """
    Multi-source enrichment pipeline (per stock, thread-safe — each call owns its sessions).

    Priority waterfall:
      P2a — NSE API (json)  : Promoter/FII/DII holding, Pledged %, Industry PE
      P2b — Computed        : G-Factor approx from ROIC + EV/EBITDA (no HTTP call)
      P2c — Trendlyne (html): G-Factor actual, Historical PE fallback
      P2d — Screener.in     : Final fallback for any field still NaN
    """

    def _is_nan(v):
        return v is None or (isinstance(v, float) and np.isnan(v))
    def import_math_isnan(v):
        try: return not (v == v)  # NaN check without import
        except Exception: return True

    def _set_if_missing(col, val, prefer=False):
        """Write val to row_d[col] only if missing (or prefer=True to override)."""
        try:
            fv = float(val)
            if np.isnan(fv):
                return
            if _is_nan(row_d.get(col)) or prefer:
                row_d[col] = fv
        except Exception:
            pass

    # ── P2a: NSE API ─────────────────────────────────────────────────────────
    nse_data: dict = {}
    try:
        nse_data = _fetch_nse_data(sym, session=nse_sess)
    except Exception:
        pass

    _PREFER_NSE = {"Promoter holding", "FII holding", "DII holding",
                   "Pledged percentage", "Industry PE",
                   "Change in promoter holding", "Change in FII holding",
                   "52 Week High", "52 Week Low"}  # V5-1: NSE data authoritative for 52W
    for col, val in nse_data.items():
        if col.startswith("_"):
            continue   # internal scratch fields
        _set_if_missing(col, val, prefer=(col in _PREFER_NSE))

    # Derive DII from public − FII if DII still missing
    if _is_nan(row_d.get("DII holding")) and not _is_nan(row_d.get("FII holding")):
        pub = nse_data.get("_nse_public")
        if pub is not None:
            dii_est = float(pub) - float(row_d["FII holding"])
            if dii_est >= 0:
                row_d["DII holding"] = dii_est

    # ── P2a.5: 52W High/Low last-resort — targeted history() if still NaN ──
    # yfinance .info fiftyTwoWeekHigh is unreliable for NSE; NSE API above is primary.
    # If BOTH failed (rate-limit + NSE API down), attempt one targeted history call.
    if _is_nan(row_d.get("52 Week High")) or _is_nan(row_d.get("52 Week Low")):
        try:
            _t_52w = _safe_yf_ticker(sym, "enrichment_52w_ticker")
            _h52 = _safe_yf_history(_t_52w, sym, "enrichment_52w_history", period="1y", auto_adjust=True)
            if _h52 is not None and not _h52.empty and len(_h52) >= 2:
                _wh52 = float(_h52["High"].max())
                _wl52 = float(_h52["Low"].min())
                if _wh52 > 0:
                    _set_if_missing("52 Week High", _wh52, prefer=True)
                if _wl52 > 0:
                    _set_if_missing("52 Week Low",  _wl52, prefer=True)
                # Also fill RSI-14 and 6M return if missing (common for NSE stubs)
                if _is_nan(row_d.get("RSI 14")) and len(_h52) >= 15:
                    _d = _h52["Close"].diff()
                    _g = _d.clip(lower=0).ewm(span=14, adjust=False).mean()
                    _lo = (-_d.clip(upper=0)).ewm(span=14, adjust=False).mean()
                    _rs = _g / _lo
                    _rsi_v = float((100 - 100 / (1 + _rs)).iloc[-1])
                    if not import_math_isnan(_rsi_v):
                        _set_if_missing("RSI 14", _rsi_v)
                if _is_nan(row_d.get("6 Month Return")) and len(_h52) >= 60:
                    _6m_idx = max(0, len(_h52) - 126)
                    _6m_ret = (float(_h52["Close"].iloc[-1]) /
                               float(_h52["Close"].iloc[_6m_idx]) - 1) * 100
                    _set_if_missing("6 Month Return", _6m_ret)
        except Exception:
            pass
        if (_is_nan(row_d.get("52 Week High")) or _is_nan(row_d.get("52 Week Low")) or
                _is_nan(row_d.get("RSI 14")) or _is_nan(row_d.get("6 Month Return"))):
            try:
                _jgd = _fetch_jugaad_snapshot(sym)
                if _jgd:
                    if np.isfinite(_jgd.get("wk52h", np.nan)):
                        _set_if_missing("52 Week High", float(_jgd["wk52h"]), prefer=True)
                    if np.isfinite(_jgd.get("wk52l", np.nan)):
                        _set_if_missing("52 Week Low", float(_jgd["wk52l"]), prefer=True)
                    if np.isfinite(_jgd.get("rsi_14", np.nan)):
                        _set_if_missing("RSI 14", float(_jgd["rsi_14"]))
                    if np.isfinite(_jgd.get("six_mo", np.nan)):
                        _set_if_missing("6 Month Return", float(_jgd["six_mo"]))
            except Exception:
                pass

    # ── P2b: Computed G-Factor (zero HTTP calls) ─────────────────────────────
    if _is_nan(row_d.get("G Factor")):
        roic_v = row_d.get("Return on invested capital", np.nan)
        eveb_v = row_d.get("EVEBITDA", np.nan)
        gf = _compute_gfactor_approx(
            float(roic_v) if not _is_nan(roic_v) else np.nan,
            float(eveb_v) if not _is_nan(eveb_v) else np.nan,
        )
        if not np.isnan(gf):
            row_d["G Factor"] = gf

    # ── P2c: Trendlyne (only if G-Factor still missing) ──────────────────────
    if _is_nan(row_d.get("G Factor")):
        try:
            gf_tl = _fetch_trendlyne_gf(sym)
            if not np.isnan(gf_tl):
                row_d["G Factor"] = gf_tl
        except Exception:
            pass

    # ── P2d: Screener.in — final fallback for remaining NaN fields ────────────
    # Only scrape if there are still important fields missing
    _SCREENER_NEEDED_FIELDS = {
        "Historical PE 5Years", "Piotroski score",
        "Profit growth 5Years", "Sales growth 5Years",
        "Return on capital employed", "Return on invested capital",
        "Net Profit latest quarter", "Change in promoter holding",
        "Change in FII holding", "Free cash flow 3years",
    }
    needs_screener = any(_is_nan(row_d.get(f)) for f in _SCREENER_NEEDED_FIELDS)

    if needs_screener and _SCR_OK:
        try:
            s = requests.Session()
            s.headers.update(_SCR_HEADERS)
            s.get("https://www.screener.in/", timeout=6)
            scr = _scrape_screener(sym, s)

            _PREFER_SCR = {
                "Return on capital employed", "Return on equity",
                "Return on invested capital",
                "Profit growth 5Years", "Sales growth 5Years",
            }
            _FILL_COLS = [
                "Industry PE", "Historical PE 5Years", "Profit growth 5Years",
                "Sales growth 5Years", "Pledged percentage", "Piotroski score",
                "G Factor", "RSI 14", "Promoter holding", "Change in promoter holding",
                "FII holding", "DII holding", "Change in FII holding",
                "Free cash flow 3years", "Net Profit latest quarter", "OPM",
                "Net profit margin", "EV to Sales", "EVEBITDA", "PEG Ratio",
                "Price to Free Cash Flow", "Book value", "Interest coverage ratio",
                "Debt to equity",
                "Profit after tax", "Profit growth", "Sales growth",
                "Cash from operations last year", "Free cash flow TTM", "Free cash flow last year",
                "Asset growth", "Total assets growth",
                "Return on capital employed", "Return on equity", "Dividend yield",
                "Return on invested capital",
            ]
            for col in _FILL_COLS:
                val = scr.get(col)
                if val is None:
                    continue
                try:
                    fval = float(val)
                except Exception:
                    continue
                if np.isnan(fval):
                    continue
                existing = row_d.get(col)
                is_nan = _is_nan(existing)
                # Screener.in overrides yfinance for preferred fields, but NOT NSE fields
                prefer_scr = (col in _PREFER_SCR) and (col not in _PREFER_NSE)
                if is_nan or prefer_scr:
                    row_d[col] = fval

            # Bug 15 fix: convert _BV_per_share → total Book value
            bvps = scr.get("_BV_per_share")
            if bvps and _is_nan(row_d.get("Book value")):
                _price_bv = row_d.get("Current Price")
                _mcap_bv  = row_d.get("Market Capitalization")
                if _price_bv and _mcap_bv and _price_bv > 0:
                    _shares_bv = (_mcap_bv * 1e7) / _price_bv
                    row_d["Book value"] = float(bvps) * _shares_bv / 1e7

            time.sleep(0.25)   # reduced delay — NSE already got most fields
        except Exception:
            pass

    return row_d


def fetch_nse_live_data(symbols: list, max_n: int,
                         prog_bar=None, status_txt=None,
                         use_screener: bool = True) -> pd.DataFrame:
    """
    Phase 1 — Parallel yfinance fetch  (20 workers, ~2-3 min for 1783 stocks)
    Phase 2 — Parallel Screener.in enrichment (8 workers, ~3-4 min for 1783)
    Returns DataFrame matching Screener.in column schema for Alchemy scoring.
    """
    LOGGER.info("Starting live fetch for %s symbols (max_n=%s, use_screener=%s)", len(symbols), max_n, use_screener)
    clear_yf_issues()
    _set_run_status(f"Live fetch started — {min(len(symbols), max_n)} symbols queued.")

    if not _YF_OK and not _JGD_OK:
        st.error("Neither yfinance nor jugaad-data is installed. Run: pip install yfinance jugaad-data")
        return pd.DataFrame()

    syms  = [s.strip() for s in symbols if s.strip()][:max_n]
    n     = len(syms)
    rows  = {}          # sym → row dict (thread-safe by key)
    lock  = threading.Lock()
    done  = [0]
    failed = []

    # ── Phase 0: NSE price pre-fetch (gives yfinance a fallback for rate-limited stocks) ──
    if status_txt:
        status_txt.markdown(
            f"<span style='color:#888'>⚡ Phase 0/2 — Pre-fetching {n} prices "
            f"from NSE API (fallback cache)…</span>",
            unsafe_allow_html=True)
    try:
        LOGGER.info("Phase 0: NSE prefetch for %s symbols", len(syms))
        _nse_price_prefetch(syms)
    except Exception as exc:
        LOGGER.warning("Phase 0 prefetch failed: %s", exc)

    # ── Phase 1: Parallel yfinance fetch — batched to avoid Yahoo rate-limiting ──
    # Root cause of 410/1783: 20 concurrent workers trigger Yahoo's rate limiter
    # which returns empty info{} → price=None → stock silently dropped.
    # Fix: 5 workers (safe threshold) + batch pause every 200 stocks + retry in _fetch_one_yf
    if status_txt:
        status_txt.markdown(
            f"<span style='color:#ffd700'>⚡ Phase 1/2 — Fetching **{n}** stocks "
            f"from yfinance (5 workers, batched to avoid rate-limiting)…</span>",
            unsafe_allow_html=True)

    YF_WORKERS = min(5, n)   # 5 = safe Yahoo concurrency limit
    BATCH_SIZE  = 200         # pause every 200 stocks to let Yahoo rate-limit window reset
    # V5-10: adaptive pause — Yahoo's rate-limit window is ~60s; 3s was far too short
    # Formula: 10s minimum (warm), scales to 60s max for large universes
    BATCH_PAUSE = float(max(10.0, min(60.0, n // 10)))  # e.g. n=200→20s, n=1783→60s

    sym_batches = [syms[i:i+BATCH_SIZE] for i in range(0, n, BATCH_SIZE)]

    LOGGER.info("Phase 1: yfinance fetch in %s batches with %s workers", len(sym_batches), YF_WORKERS)
    for batch_idx, batch in enumerate(sym_batches):
        if batch_idx > 0:
            if prog_bar:
                prog_bar.progress(
                    min(done[0] / n * 0.55, 0.54),
                    text=f"Phase 1/2 — batch pause {batch_idx}/{len(sym_batches)}… ({done[0]}/{n} fetched)")
            time.sleep(BATCH_PAUSE)

        with ThreadPoolExecutor(max_workers=YF_WORKERS) as ex:
            future_map = {ex.submit(_fetch_one_yf, sym): sym for sym in batch}
            for fut in as_completed(future_map):
                sym = future_map[fut]
                try:
                    row = fut.result()
                    if row:
                        with lock:
                            rows[sym] = row
                            done[0]  += 1
                    else:
                        failed.append(sym)
                except Exception:
                    failed.append(sym)
                if prog_bar:
                    prog_bar.progress(
                        min(done[0] / n * 0.55, 0.54),
                        text=(f"Phase 1/2 — yfinance: {done[0]}/{n} fetched "
                              f"({len(failed)} skipped) [batch {batch_idx+1}/{len(sym_batches)}]"))

    # ── Phase 1b: Retry failed symbols once with longer backoff ──────────────
    LOGGER.info("Phase 1 complete: fetched=%s, initial_failed=%s", len(rows), len(failed))
    if failed:
        retry_syms = failed.copy()
        failed.clear()
        if status_txt:
            status_txt.markdown(
                f"<span style='color:#ff9800'>⚡ Phase 1b/2 — Retrying {len(retry_syms)} "
                f"rate-limited stocks…</span>",
                unsafe_allow_html=True)
        time.sleep(5.0)   # let Yahoo rate-limit window reset
        with ThreadPoolExecutor(max_workers=3) as ex:
            retry_map = {ex.submit(_fetch_one_yf, sym): sym for sym in retry_syms}
            for fut in as_completed(retry_map):
                sym = retry_map[fut]
                try:
                    row = fut.result()
                    if row:
                        with lock:
                            rows[sym] = row
                            done[0]  += 1
                    else:
                        # Last resort: build minimal row from NSE price cache
                        cached = _NSE_PRICE_CACHE.get(sym)
                        if isinstance(cached, (tuple, list)):
                            cached = {"price": cached[0], "mcap_cr": cached[1],
                                      "wk52h": np.nan, "wk52l": np.nan}
                        if cached and cached.get("price", 0) > 0:
                            with lock:
                                rows[sym] = {
                                    "Name": sym, "NSE Code": sym, "Industry": "Unknown",
                                    "Market Capitalization": cached.get("mcap_cr", np.nan),
                                    "Current Price": cached["price"],
                                    "52 Week High": cached.get("wk52h", np.nan),
                                    "52 Week Low":  cached.get("wk52l", np.nan),
                                    **{k: np.nan for k in [
                                        "Price to Earning","Industry PE","PEG Ratio",
                                        "Historical PE 5Years","Return on capital employed",
                                        "Return on equity","Return on invested capital",
                                        "Profit growth 5Years","Sales growth 5Years",
                                        "Profit growth","Sales growth","Debt to equity",
                                        "Pledged percentage","Piotroski score","G Factor",
                                        "Free cash flow TTM","Free cash flow last year","Free cash flow 3years",
                                        "Price to Free Cash Flow","Graham Number","Book value",
                                        "Promoter holding","DII holding","FII holding",
                                        "Change in promoter holding","Change in FII holding",
                                        "EVEBITDA","EV to Sales","Net Profit latest quarter",
                                        "Profit after tax","Dividend yield",
                                        "Interest coverage ratio","Cash from operations last year",
                                        "52 Week High","52 Week Low","Asset growth",
                                        "Total assets growth","EBITDA growth",
                                        "Net profit margin","OPM","RSI 14","6 Month Return",
                                    ]}
                                }
                                done[0] += 1
                        else:
                            failed.append(sym)
                except Exception:
                    failed.append(sym)

    yf_count = len(rows)
    if status_txt:
        status_txt.markdown(
            f"<span style='color:#00e676'>✅ Phase 1 done — **{yf_count}** stocks fetched "
            f"({len(failed)} permanently failed after retry)</span>",
            unsafe_allow_html=True)

    # ── Phase 2: Multi-source enrichment ─────────────────────────────────────
    # Sources: NSE API (shareholding/Industry PE) → computed G-Factor
    #          → Trendlyne (G-Factor actual) → Screener.in fallback
    if use_screener and rows:
        enrich_syms = list(rows.keys())
        enr_done = [0]
        src_label = "NSE API + computed fields"
        if _SCR_OK:
            src_label += " → Screener.in fallback"
        if status_txt:
            status_txt.markdown(
                f"<span style='color:#ffd700'>⚡ Phase 2/2 — Enriching **{len(enrich_syms)}** "
                f"stocks ({src_label})…</span>",
                unsafe_allow_html=True)

        ENR_WORKERS = 12   # NSE API is faster than Screener.in, can use more workers
        with ThreadPoolExecutor(max_workers=ENR_WORKERS) as ex:
            future_map2 = {
                ex.submit(_enrich_all_sources, rows[sym], sym): sym
                for sym in enrich_syms
            }
            for fut in as_completed(future_map2):
                sym = future_map2[fut]
                try:
                    enriched = fut.result()
                    with lock:
                        rows[sym] = enriched
                except Exception:
                    pass
                enr_done[0] += 1
                if prog_bar:
                    prog_bar.progress(
                        min(0.55 + enr_done[0] / len(enrich_syms) * 0.44, 0.99),
                        text=(f"Phase 2/2 — Multi-source enrichment: "
                              f"{enr_done[0]}/{len(enrich_syms)}"))

        if status_txt:
            status_txt.markdown(
                f"<span style='color:#00e676'>✅ Phase 2 done — enrichment complete "
                f"for {enr_done[0]} stocks (NSE API + computed + Screener.in fallback)</span>",
                unsafe_allow_html=True)
    elif not use_screener:
        if status_txt:
            status_txt.markdown(
                "<span style='color:#888'>ℹ️ Deep enrichment skipped (fast mode)</span>",
                unsafe_allow_html=True)

    if prog_bar:
        prog_bar.progress(
            1.0,
            text=f"✅ Complete — {len(rows)} stocks ready for Alchemy scoring")

    LOGGER.info("Live fetch complete: returning %s rows", len(rows))
    _set_run_status(
        f"Live fetch complete — {len(rows)}/{n} rows fetched. "
        f"Deep enrichment={'on' if use_screener else 'off'}."
    )
    render_yf_issues()
    return pd.DataFrame(list(rows.values()))

KEEP_COLS = [
    "Name", "NSE Code", "Industry", "Market Capitalization", "Current Price",
    "Price to Earning", "Industry PE", "PEG Ratio", "Historical PE 5Years",
    "Return on capital employed", "Return on equity", "Return on invested capital",
    "Profit growth 5Years", "Sales growth 5Years", "Profit growth", "Sales growth",
    "Debt to equity", "Pledged percentage", "Pledging %", "Pledge %", "Pledged shares %",
    "Piotroski score", "G Factor",
    "Free cash flow TTM", "Free cash flow last year", "Free cash flow 3years",
    "Price to Free Cash Flow", "Graham Number", "Book value",
    "Promoter holding", "DII holding", "FII holding",
    "Change in promoter holding", "Change in FII holding",
    "EVEBITDA", "EV to Sales", "Net Profit latest quarter",
    "Profit after tax", "Dividend yield", "Interest coverage ratio",
    "Cash from operations last year", "52 Week High", "52 Week Low",
    "Asset growth", "Total assets growth", "EBITDA growth",
    "Net profit margin", "OPM", "RSI 14", "6 Month Return",
]


def run_screen(df: pd.DataFrame, nse_df: Optional[pd.DataFrame],
               pw: dict, filters: dict) -> pd.DataFrame:

    LOGGER.info("Starting run_screen on %s rows", len(df))

    # ── B3A: Warn if DISQ-critical columns are absent from input CSV ─────────────
    _DISQ_NEEDED = ["Change in promoter holding","Change in FII holding",
                    "Pledged percentage","Pledging %","Piotroski score","Debt to equity"]
    _missing_disq = [c for c in _DISQ_NEEDED
                     if c not in df.columns and
                     not any(alt in df.columns for alt in ["Pledging %","Pledge %","Pledged shares %","% Pledged"]
                             if c == "Pledged percentage")]
    # Do NOT warn yet. CSV-mode enrichment below can backfill these fields from NSE/Screener.

    # ── FIX-C: Entry Signal Prefetch ──────────────────────────────────────────
    # Resolve per-row identifiers intelligently: NSE symbol → BSE code/symbol → ISIN/name search.
    _TPE = ThreadPoolExecutor
    _asc = as_completed
    _row_meta = []
    for _idx, _row in enumerate(df.to_dict("records")):
        _bundle = _row_identifiers(_row)
        _targets = _resolve_lookup_targets(_bundle)
        _row_meta.append({
            "row_idx": _idx,
            "bundle": _bundle,
            "targets": _targets,
        })

    _ENTRY_COLS = {"52 Week High", "52 Week Low", "RSI 14", "6 Month Return"}
    _entry_existing_hi = pd.to_numeric(df.get("52 Week High", pd.Series(dtype=float)), errors="coerce")
    _needs_entry_fetch = (not _ENTRY_COLS.issubset(set(df.columns))) or (_entry_existing_hi.isna().mean() > 0.35)
    _entry_rows = [m for m in _row_meta if m["targets"].get("yf_candidates") or m["targets"].get("nse_symbol") or m["targets"].get("bse_code")]
    if _needs_entry_fetch and _entry_rows and (_YF_OK or _JGD_OK):
        _entry_prog = st.progress(0, text="⚡ Fetching entry data (NSE/BSE/ISIN-aware)…")

        def _fetch_entry_only(meta: dict) -> tuple:
            bundle = meta.get("bundle", {}) or {}
            targets = meta.get("targets", {}) or {}
            label = next(iter(bundle.values()), f"row_{meta.get('row_idx', -1)}")
            out = {"52 Week High": np.nan, "52 Week Low": np.nan, "RSI 14": np.nan, "6 Month Return": np.nan}

            for cand in targets.get("yf_candidates", [])[:8]:
                try:
                    _t = _safe_yf_ticker(cand, "entry_prefetch_ticker")
                    if _t is None:
                        continue
                    try:
                        _fi = _safe_yf_fast_info(_t, cand, "entry_prefetch_fast_info")
                        if hasattr(_fi, "year_high") and _fi.year_high and float(_fi.year_high) > 0:
                            out["52 Week High"] = float(_fi.year_high)
                        if hasattr(_fi, "year_low") and _fi.year_low and float(_fi.year_low) > 0:
                            out["52 Week Low"] = float(_fi.year_low)
                    except Exception:
                        pass
                    _h = _safe_yf_history(_t, cand, "entry_prefetch_history", period="1y", auto_adjust=True, timeout=15)
                    if _h is None or _h.empty:
                        _h = pd.DataFrame()
                    if not _h.empty and len(_h) >= 2:
                        out["52 Week High"] = float(_h["High"].max())
                        out["52 Week Low"] = float(_h["Low"].min())
                    if len(_h) >= 15:
                        _d = _h["Close"].diff()
                        _g = _d.clip(lower=0).ewm(span=14, adjust=False).mean()
                        _lo = (-_d.clip(upper=0)).ewm(span=14, adjust=False).mean()
                        _rs = _g / _lo
                        _rsi = float((100 - (100 / (1 + _rs))).iloc[-1])
                        if np.isfinite(_rsi):
                            out["RSI 14"] = _rsi
                    if len(_h) >= 60:
                        _idx6 = max(0, len(_h) - 126)
                        out["6 Month Return"] = (float(_h["Close"].iloc[-1]) / float(_h["Close"].iloc[_idx6]) - 1) * 100
                    if sum(np.isfinite(v) for v in out.values()) >= 3:
                        break
                except Exception:
                    continue

            _nse_symbol = targets.get("nse_symbol")
            if (_nse_symbol and (np.isnan(out["52 Week High"]) or np.isnan(out["52 Week Low"]))):
                try:
                    _nse_data = _fetch_nse_data(_nse_symbol) or {}
                    for _col in ("52 Week High", "52 Week Low"):
                        _val = _nse_data.get(_col)
                        if _val is not None and np.isfinite(float(_val)):
                            out[_col] = float(_val)
                except Exception:
                    pass

            if _nse_symbol and (np.isnan(out["52 Week High"]) or np.isnan(out["52 Week Low"]) or np.isnan(out["RSI 14"]) or np.isnan(out["6 Month Return"])) and _JGD_OK:
                try:
                    _jgd = _fetch_jugaad_snapshot(_nse_symbol)
                    if _jgd:
                        if np.isnan(out["52 Week High"]) and np.isfinite(_jgd.get("wk52h", np.nan)):
                            out["52 Week High"] = float(_jgd["wk52h"])
                        if np.isnan(out["52 Week Low"]) and np.isfinite(_jgd.get("wk52l", np.nan)):
                            out["52 Week Low"] = float(_jgd["wk52l"])
                        if np.isnan(out["RSI 14"]) and np.isfinite(_jgd.get("rsi_14", np.nan)):
                            out["RSI 14"] = float(_jgd["rsi_14"])
                        if np.isnan(out["6 Month Return"]) and np.isfinite(_jgd.get("six_mo", np.nan)):
                            out["6 Month Return"] = float(_jgd["six_mo"])
                except Exception:
                    pass

            if not any(np.isfinite(v) for v in out.values()):
                return meta.get("row_idx"), {}, label
            return meta.get("row_idx"), out, label

        import threading as _thr
        _elock = _thr.Lock()
        _entry_cache = {}
        _entry_resolved = 0
        _entry_attempted = len(_entry_rows)
        with _TPE(max_workers=min(6, max(1, _entry_attempted))) as _ex:
            _futs = {_ex.submit(_fetch_entry_only, meta): meta for meta in _entry_rows}
            for _done_n, _fut in enumerate(_asc(_futs), start=1):
                _row_idx_r, _data_r, _label_r = _fut.result()
                if _data_r:
                    with _elock:
                        _entry_cache[_row_idx_r] = _data_r
                        _entry_resolved += 1
                _entry_prog.progress(
                    min(_done_n / _entry_attempted, 1.0),
                    text=f"⚡ Entry data: {_entry_resolved}/{_entry_attempted} resolved…"
                )
        if _entry_cache:
            for _col in ["52 Week High", "52 Week Low", "RSI 14", "6 Month Return"]:
                if _col not in df.columns:
                    df[_col] = np.nan
            for _row_idx_r, _data_r in _entry_cache.items():
                for _col, _val in _data_r.items():
                    if np.isfinite(_val):
                        df.at[_row_idx_r, _col] = _val if pd.isna(df.at[_row_idx_r, _col]) else df.at[_row_idx_r, _col]
        _entry_prog.progress(1.0, text=f"✅ Entry data ready for {_entry_resolved}/{_entry_attempted} identifier-bearing rows")
        _entry_prog.empty()
    else:
        _entry_attempted = len(_entry_rows)
        _entry_resolved = 0

    # ── FIX-C2: Parallel DISQ enrichment for CSV mode ─────────────────────
    # Populate DISQ-critical fields using the same per-row resolver used for entry data.
    _DISQ_COLS = {"Pledged percentage", "Change in promoter holding", "Debt to equity", "Piotroski score"}
    _pledge_existing = df_first_numeric(df, ["Pledged percentage", "Pledging %", "Pledge %", "Pledged shares %", "% Pledged"])
    _needs_disq_fetch = (
        not _DISQ_COLS.issubset(set(df.columns)) or
        _pledge_existing.isna().mean() > 0.65 or
        df_first_numeric(df, ["Debt to equity"]).isna().mean() > 0.65 or
        df_first_numeric(df, ["Piotroski score"]).isna().mean() > 0.65 or
        df_first_numeric(df, ["Change in promoter holding"]).isna().mean() > 0.65
    )
    if _needs_disq_fetch and _row_meta:
        _disq_prog = st.progress(0, text="⚡ Fetching DISQ coverage (NSE/BSE/ISIN-aware)…")
        _disq_done = 0
        _disq_records = {}

        def _fetch_disq_only(meta: dict) -> tuple:
            bundle = meta.get("bundle", {}) or {}
            targets = meta.get("targets", {}) or {}
            merged = {}
            nse_symbol = targets.get("nse_symbol")
            bse_code = targets.get("bse_code")
            if nse_symbol:
                try:
                    merged.update(_fetch_nse_data(nse_symbol) or {})
                except Exception:
                    pass
            if bse_code:
                try:
                    merged.update(_fetch_bse_shp(nse_symbol or bse_code, bse_code=bse_code) or {})
                except Exception:
                    pass
            needs_scr = (
                not ok2(first_num(merged, ["Piotroski score"])) or
                not ok2(first_num(merged, ["Debt to equity"])) or
                not ok2(first_num(merged, ["Change in promoter holding"]))
            )
            if needs_scr and _SCR_OK:
                scr_sym = nse_symbol or _normalise_symbol_base(bundle.get("Symbol") or bundle.get("Ticker") or bundle.get("NSE Code") or bundle.get("Code") or "")
                if scr_sym:
                    try:
                        _s = requests.Session()
                        _s.headers.update(_SCR_HEADERS)
                        _s.get("https://www.screener.in/", timeout=6)
                        merged.update(_scrape_screener(scr_sym, _s) or {})
                    except Exception:
                        pass
            return meta.get("row_idx"), {k: v for k, v in merged.items() if not str(k).startswith("_")}

        _eligible_disq_rows = [m for m in _row_meta if m.get("targets", {}).get("nse_symbol") or m.get("targets", {}).get("bse_code")]
        if _eligible_disq_rows:
            with _TPE(max_workers=min(6, max(1, len(_eligible_disq_rows)))) as _ex2:
                _futs2 = {_ex2.submit(_fetch_disq_only, meta): meta for meta in _eligible_disq_rows}
                for _fut2 in _asc(_futs2):
                    _row_idx_r2, _data_r2 = _fut2.result()
                    if _data_r2:
                        _disq_records[_row_idx_r2] = _data_r2
                    _disq_done += 1
                    _disq_prog.progress(
                        min(_disq_done / len(_eligible_disq_rows), 1.0),
                        text=f"⚡ DISQ coverage: {_disq_done}/{len(_eligible_disq_rows)}…"
                    )
            if _disq_records:
                for _row_idx_r2, _payload in _disq_records.items():
                    for _col2, _val2 in _payload.items():
                        if _col2 not in df.columns:
                            df[_col2] = np.nan
                        try:
                            _fv = float(_val2)
                        except Exception:
                            continue
                        if np.isnan(_fv):
                            continue
                        if pd.isna(df.at[_row_idx_r2, _col2]):
                            df.at[_row_idx_r2, _col2] = _fv
        _disq_prog.empty()

    # Effective post-enrichment DISQ coverage warning
    _disq_cov = {
        "Change in promoter holding": df_first_numeric(df, ["Change in promoter holding"]),
        "Piotroski score": df_first_numeric(df, ["Piotroski score"]),
        "Debt to equity": df_first_numeric(df, ["Debt to equity"]),
    }
    _still_sparse = []
    for _colname, _series in _disq_cov.items():
        _miss = float(_series.isna().mean()) if len(_series) else 1.0
        if _miss > 0.35:
            _still_sparse.append(f"{_colname} ({(1-_miss)*100:.0f}% covered)")
    if _still_sparse:
        _strict_disq_active = bool((filters.get("min_pio", 0) > 0) or (filters.get("max_de", 2.0) < 2.0))
        _msg = (
            "DISQ coverage is still partial after enrichment: "
            + ", ".join(_still_sparse)
            + ". Ranking still works because the relevant filters are NaN-tolerant, but DISQ capping is not fully deterministic for those rows."
        )
        if _strict_disq_active:
            st.warning("⚠️ " + _msg)
        else:
            st.info("ℹ️ " + _msg)

    with st.spinner("⚗️ Alchemy v4.0 Ultra — Calculating 35 parameters × 6 pillars + Entry Signal..."):
        prog = st.progress(0, text="Scoring stocks...")
        n = len(df)
        records = df.to_dict("records")
        results = []
        for i, record in enumerate(records):
            results.append(compute_score(record, pw))
            if i % max(1, n // 25) == 0:
                prog.progress(min(i / n, 0.99), text=f"Alchemy Processing {i + 1}/{n}...")
        prog.progress(1.0, text="Complete!")

    LOGGER.info("Scoring complete for %s rows", len(results))
    render_yf_issues()
    res_df = pd.DataFrame(results)
    existing = [c for c in KEEP_COLS if c in df.columns]
    scored = pd.concat([df[existing].reset_index(drop=True), res_df], axis=1)

    # ── Detect the ticker/symbol column robustly ──────────────────────────────
    # Screener.in exports vary: "NSE Code", "NSE Symbol", "Symbol", "Ticker" etc.
    NSE_COL_CANDIDATES = ["NSE Code", "NSE Symbol", "Symbol", "Ticker",
                          "ISIN Code", "NSE", "Code"]
    _nse_col = next((c for c in NSE_COL_CANDIDATES if c in scored.columns), None)
    # Also try case-insensitive match as last resort
    if _nse_col is None:
        _lower_map = {c.lower(): c for c in scored.columns}
        for cand in NSE_COL_CANDIDATES:
            if cand.lower() in _lower_map:
                _nse_col = _lower_map[cand.lower()]
                break
    # Ensure "NSE Code" column always exists (use found col or blank)
    if _nse_col and _nse_col != "NSE Code":
        scored["NSE Code"] = scored[_nse_col]
    elif _nse_col is None:
        scored["NSE Code"] = ""          # no ticker column found — graceful degradation

    # ── Market Cap column ─────────────────────────────────────────────────────
    MCAP_CANDIDATES = ["Market Capitalization", "Market Cap", "Mkt Cap", "MarketCap"]
    _mcap_col = next((c for c in MCAP_CANDIDATES if c in scored.columns), None)
    if _mcap_col and _mcap_col != "Market Capitalization":
        scored["Market Capitalization"] = scored[_mcap_col]
    scored["MCap_Cr"] = pd.to_numeric(
        scored.get("Market Capitalization", pd.Series(dtype=float)), errors="coerce")

    # ── NSE filter ────────────────────────────────────────────────────────────
    if nse_df is not None:
        def _norm_sym(x):
            s = str(x).strip().upper()
            for suf in ('.NS', '-EQ'):
                if s.endswith(suf):
                    s = s[:-len(suf)]
            return s
        nse_syms = set(nse_df.iloc[:, 0].astype(str).map(_norm_sym).tolist())
        scored["is_NSE"] = scored["NSE Code"].apply(
            lambda x: _norm_sym(x) in nse_syms if pd.notna(x) and str(x).strip() != "" else False)
    else:
        scored["is_NSE"] = True

    # ── Apply filters ─────────────────────────────────────────────────────────
    _filter_diag = {"total": int(len(scored)), "pass": {}}
    mask = pd.Series(True, index=scored.index)
    if filters.get("nse_only") and nse_df is not None:
        cond = scored["is_NSE"].reindex(scored.index, fill_value=False)
        _filter_diag["pass"]["NSE Listed Only"] = int(cond.sum())
        mask &= cond
    cond = scored["MCap_Cr"].fillna(0).reindex(scored.index, fill_value=0) >= filters.get("min_mcap", 0)
    _filter_diag["pass"][f"Min MCap ≥ {filters.get('min_mcap', 0)}"] = int(cond.sum())
    mask &= cond
    cond = scored["MCap_Cr"].fillna(9e9).reindex(scored.index, fill_value=9e9) <= filters.get("max_mcap", 9e9)
    _filter_diag["pass"][f"Max MCap ≤ {filters.get('max_mcap', 9e9)}"] = int(cond.sum())
    mask &= cond
    if filters.get("min_score", 0) > 0:
        cond = scored["SCORE_V40"].reindex(scored.index, fill_value=-np.inf) >= filters["min_score"]
        _filter_diag["pass"][f"Min Score ≥ {filters['min_score']}"] = int(cond.sum())
        mask &= cond
    # NaN-tolerant aligned filters — NaN data skips the filter instead of silently failing
    if filters.get("max_de") is not None:
        de_col = df_first_numeric(scored, ["Debt to equity"])
        cond = de_col.isna() | (de_col <= filters["max_de"])
        _filter_diag["pass"][f"Max D/E ≤ {filters['max_de']}"] = int(cond.sum())
        mask &= cond
    if filters.get("max_pledge") is not None:
        pl_col = df_first_numeric(scored, ["Pledged percentage", "Pledging %", "Pledge %", "Pledged shares %", "% Pledged"])
        cond = pl_col.isna() | (pl_col <= filters["max_pledge"])
        _filter_diag["pass"][f"Max Pledge ≤ {filters['max_pledge']}%"] = int(cond.sum())
        mask &= cond
    if filters.get("min_pio") is not None and filters["min_pio"] > 0:
        pio_col = df_first_numeric(scored, ["Piotroski score"])
        cond = pio_col.isna() | (pio_col >= filters["min_pio"])
        _filter_diag["pass"][f"Min Piotroski ≥ {filters['min_pio']}"] = int(cond.sum())
        mask &= cond
    if filters.get("min_roce") is not None and filters["min_roce"] > 0:
        rc_raw = df_first_numeric(scored, ["Return on capital employed"])
        rc = rc_raw.apply(lambda x: pct(x) if ok2(fv(x)) else np.nan)
        cond = rc.isna() | (rc >= filters["min_roce"])
        _filter_diag["pass"][f"Min ROCE ≥ {filters['min_roce']}%"] = int(cond.sum())
        mask &= cond
    if filters.get("entry_only"):
        cond = scored["Entry_Score"].reindex(scored.index, fill_value=np.nan) >= 3.5
        _filter_diag["pass"]["Prime Entry Only"] = int(cond.sum())
        mask &= cond
    if filters.get("tiers"):
        cond = scored["TIER_V40"].isin(filters["tiers"])
        _filter_diag["pass"]["Tier selection"] = int(cond.sum())
        mask &= cond
    if filters.get("industries") and "Industry" in scored.columns:
        cond = scored["Industry"].isin(filters["industries"])
        _filter_diag["pass"]["Industry selection"] = int(cond.sum())
        mask &= cond

    st.session_state.scored_unfiltered_v40 = _compact_results_for_state(
        scored.sort_values("SCORE_V40", ascending=False).reset_index(drop=True),
        preview_only=True,
        top_n=200,
    )
    st.session_state.filter_diag_v40 = _filter_diag
    out = scored[mask].copy()
    _hidden = len(scored) - len(out)
    if _hidden > 0:
        out.attrs["hidden_by_filters"] = _hidden
        out.attrs["total_scored"] = len(scored)
    out = out.sort_values("SCORE_V40", ascending=False).reset_index(drop=True)
    out.insert(0, "Rank", range(1, len(out) + 1))
    _final_entry_resolved = int(df_first_numeric(df, ["52 Week High"]).notna().sum()) if "52 Week High" in df.columns else 0
    _bse_hint = sum(1 for m in _row_meta if m.get("targets", {}).get("bse_code"))
    _isin_hint = sum(1 for m in _row_meta if any(_is_isin_like(v) for v in m.get("bundle", {}).values()))
    _set_run_status(
        f"Merged {len(df)} rows. Entry coverage: {_final_entry_resolved}/{len(df)} rows now have 52W data. "
        f"BSE-aware retries on {_bse_hint} row(s); ISIN-aware resolution on {_isin_hint} row(s). "
        f"Final output: {len(out)} stock(s) after filters."
    )
    return _compact_results_for_state(out)


# ──────────────────────────────────────────────────────────────────────────────
# CHART HELPERS
# ──────────────────────────────────────────────────────────────────────────────

PILLAR_COLORS = {
    "P1_Quality": "#4a9eff",  "P2_Growth": "#00e676",
    "P3_Value":   "#ffd700",  "P4_Discipline": "#ff6bc6",
    "P5_Size":    "#ff9800",  "P6_Safety": "#ff4757",
}

def dark_layout(fig, title="", height=None):
    kw = dict(paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
              font=dict(color="#cdd9e5", size=12), title_x=0.5,
              title=dict(text=title, font=dict(size=14, color="#ffd700")))
    if height: kw["height"] = height
    fig.update_layout(**kw)
    return fig

def radar_chart(row: pd.Series, name: str) -> go.Figure:
    cats = ["P1 Quality","P2 Growth","P3 Value","P4 Discipline","P5 Size","P6 Safety"]
    vals = [row.get("P1_Quality",5), row.get("P2_Growth",5), row.get("P3_Value",5),
            row.get("P4_Discipline",5), row.get("P5_Size",5), row.get("P6_Safety",5)]
    vals += [vals[0]]; cats += [cats[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals, theta=cats, fill="toself",
        fillcolor="rgba(74,158,255,0.12)", line=dict(color="#4a9eff", width=2.5),
        name=name[:22]))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,10],
                                   tickfont=dict(color="#666",size=8),
                                   gridcolor="#21262d"),
                   angularaxis=dict(tickfont=dict(color="#cdd9e5",size=11),
                                    gridcolor="#21262d"),
                   bgcolor="#0d1117"),
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
        font=dict(color="#cdd9e5"), margin=dict(l=55,r=55,t=65,b=55),
        title=dict(text=f"⚗️ {name[:26]} — Pillar Radar",
                   font=dict(size=13,color="#ffd700"), x=0.5))
    return fig

def multi_radar(df: pd.DataFrame, names: List[str]) -> go.Figure:
    cats = ["P1 Quality","P2 Growth","P3 Value","P4 Discipline","P5 Size","P6 Safety","P1 Quality"]
    colors = ["#ffd700","#4a9eff","#00e676","#ff9800","#ff4757","#c0c0c0"]
    fig = go.Figure()
    for i, nm in enumerate(names[:6]):
        sub = df[df["Name"].str[:18] == nm[:18]]
        if sub.empty: continue
        row = sub.iloc[0]
        vals = [row.get("P1_Quality",5), row.get("P2_Growth",5), row.get("P3_Value",5),
                row.get("P4_Discipline",5), row.get("P5_Size",5), row.get("P6_Safety",5), row.get("P1_Quality",5)]
        fig.add_trace(go.Scatterpolar(r=vals, theta=cats, fill="toself",
            fillcolor=f"rgba{(*tuple(int(colors[i][j:j+2],16) for j in (1,3,5)),0.10)}",
            line=dict(color=colors[i], width=2), name=nm[:18]))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,10], tickfont=dict(color="#555",size=8),
                                   gridcolor="#21262d"),
                   angularaxis=dict(tickfont=dict(color="#cdd9e5",size=10), gridcolor="#21262d"),
                   bgcolor="#0d1117"),
        paper_bgcolor="#0d1117", font=dict(color="#cdd9e5"), height=430,
        title=dict(text="Multi-Stock Pillar Comparison", font=dict(size=13,color="#ffd700"), x=0.5),
        legend=dict(bgcolor="#161b22", bordercolor="#21262d", borderwidth=1))
    return fig

def score_histogram(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(df, x="SCORE_V40", nbins=25, color="TIER_V40",
        color_discrete_map={"🥇 TIER 1":"#ffd700","🥈 TIER 2":"#c0c0c0",
                            "🥉 TIER 3":"#cd7f32","⚠️ TIER 4":"#ff9800","❌ TIER 5":"#ff4757"},
        labels={"SCORE_V40":"Composite Score","count":"# Stocks"})
    return dark_layout(fig, "Score Distribution — Alchemy v4.0 Ultra")

def top_bar(df: pd.DataFrame) -> go.Figure:
    top = df.head(25).copy()
    _ticker = top["NSE Code"] if "NSE Code" in top.columns else pd.Series([""] * len(top), index=top.index)
    top["Label"] = top["Name"].fillna("").astype(str).str[:16] + " (" + _ticker.fillna("").astype(str).str[:6] + ")"
    fig = go.Figure(go.Bar(
        y=top["Label"][::-1], x=top["SCORE_V40"][::-1], orientation="h",
        marker=dict(color=top["SCORE_V40"][::-1],
                    colorscale=[[0,"#ff4757"],[0.35,"#ff9800"],[0.65,"#cd7f32"],
                                [0.8,"#c0c0c0"],[1.0,"#ffd700"]],
                    showscale=True, colorbar=dict(title="Score")),
        text=top["SCORE_V40"][::-1], textposition="outside",
        textfont=dict(color="#cdd9e5", size=10)))
    return dark_layout(fig, "Top 25 — Alchemy v4.0 Score", 580)

def pillar_heatmap(df: pd.DataFrame) -> go.Figure:
    top = df.head(40).copy()
    _name_col = top["Name"] if "Name" in top.columns else pd.Series([f"Stock {i}" for i in range(len(top))], index=top.index)
    top["Label"] = _name_col.str[:14] + " (" + top["SCORE_V40"].astype(str) + ")"
    pillars = ["P1_Quality","P2_Growth","P3_Value","P4_Discipline","P5_Size","P6_Safety"]
    z = top[pillars].values
    fig = go.Figure(data=go.Heatmap(
        z=z.T, x=top["Label"].tolist(),
        y=["P1 Quality","P2 Growth","P3 Value","P4 Discipline","P5 Size","P6 Safety"],
        colorscale=[[0,"#1a0000"],[0.3,"#ff4757"],[0.5,"#ff9800"],
                    [0.7,"#ffd700"],[1.0,"#00e676"]],
        zmin=0, zmax=10, showscale=True,
        colorbar=dict(title="Score<br>(0-10)",tickfont=dict(color="#cdd9e5"))))
    return dark_layout(fig, "Pillar Heatmap — Top 40", 350)

def scatter_fcf_roic(df: pd.DataFrame) -> go.Figure:
    plot_df = df.copy()
    _roic_col = next((c for c in plot_df.columns if "invested capital" in c.lower() or c == "ROIC"), None)
    if _roic_col:
        plot_df["ROIC_pct"] = plot_df[_roic_col].apply(lambda x: pct(x) if ok2(fv(x)) else np.nan)
    else:
        plot_df["ROIC_pct"] = np.nan
    plot_df["MCap_sz"] = pd.to_numeric(plot_df.get("Market Capitalization", pd.Series()), errors="coerce")
    plot_df["FCFYpct"] = pd.to_numeric(plot_df.get("FCFYield_Pct", pd.Series()), errors="coerce")
    _tkr = plot_df["NSE Code"] if "NSE Code" in plot_df.columns else pd.Series([""] * len(plot_df), index=plot_df.index)
    plot_df["Lbl"] = plot_df["Name"].str[:14] + " (" + _tkr.astype(str).str[:5] + ")"
    plot_df = plot_df.dropna(subset=["ROIC_pct", "FCFYpct"])
    plot_df = plot_df[plot_df["ROIC_pct"].between(-5, 120) & plot_df["FCFYpct"].between(-5, 40)]
    fig = px.scatter(plot_df, x="ROIC_pct", y="FCFYpct",
                     size="MCap_sz", color="TIER_V40",
                     hover_name="Lbl",
                     hover_data={"SCORE_V40":True,"P4_Discipline":True,"P6_Safety":True},
                     size_max=38, opacity=0.85,
                     color_discrete_map={"🥇 TIER 1":"#ffd700","🥈 TIER 2":"#c0c0c0",
                                         "🥉 TIER 3":"#cd7f32","⚠️ TIER 4":"#ff9800","❌ TIER 5":"#ff4757"},
                     labels={"ROIC_pct":"ROIC %","FCFYpct":"FCF Yield %"})
    fig.add_hline(y=6, line_dash="dot", line_color="#ffd700", opacity=0.5,
                  annotation_text="FCF Yield ≥ 6% [Yartseva Zone]", annotation_position="right")
    fig.add_vline(x=20, line_dash="dot", line_color="#4a9eff", opacity=0.5,
                  annotation_text="ROIC ≥ 20%", annotation_position="top")
    return dark_layout(fig, "FCF Yield vs ROIC — The Yartseva Quality Map (bubble=MCap)")

def sector_chart(df: pd.DataFrame) -> go.Figure:
    # Bug NEW-4 fix: guard against missing/all-NaN Industry column
    if "Industry" not in df.columns or df["Industry"].isna().all():
        fig = go.Figure()
        fig.update_layout(title_text="Industry data not available",
                          paper_bgcolor="#1a1a2e", font_color="#e0e0e0")
        return fig
    inds = df["Industry"].value_counts().head(12).index.tolist()
    plot_df = df[df["Industry"].isin(inds)]
    fig = px.box(plot_df, x="Industry", y="SCORE_V40", color="Industry",
                 labels={"SCORE_V40":"Score"}, points="all")
    fig.update_layout(showlegend=False, xaxis_tickangle=-40)
    return dark_layout(fig, "Score Distribution by Sector", 430)

def entry_chart(df: pd.DataFrame) -> go.Figure:
    plot_df = df.copy()
    plot_df = plot_df[plot_df["Entry_Score"].notna() & (plot_df["Entry_Score"] != 0)]
    fig = px.scatter(plot_df, x="Entry_Score", y="SCORE_V40",
                     color="TIER_V40", hover_name="Name",
                     hover_data={"Entry_Signal": True, "FCFYield_Pct": True},
                     color_discrete_map={"🥇 TIER 1":"#ffd700","🥈 TIER 2":"#c0c0c0",
                                         "🥉 TIER 3":"#cd7f32","⚠️ TIER 4":"#ff9800","❌ TIER 5":"#ff4757"},
                     labels={"Entry_Score": "Entry Timing Score (higher=near 52WL=better)",
                             "SCORE_V40": "Fundamental Score"})
    fig.add_vline(x=3.5, line_dash="dot", line_color="#00e676", opacity=0.7,
                  annotation_text="Prime Entry Zone [Yartseva]")
    return dark_layout(fig, "Entry Timing vs Fundamental Score — Best candidates: top-right")

def pillar_contribution_bar(row: pd.Series, pw: dict) -> go.Figure:
    total_pw = sum(pw.values())
    w = {k: v / total_pw for k, v in pw.items()}
    labels = ["P1 Quality","P2 Growth","P3 Value","P4 Discipline","P5 Size","P6 Safety"]
    scores = [row.get("P1_Quality",0), row.get("P2_Growth",0), row.get("P3_Value",0),
              row.get("P4_Discipline",0), row.get("P5_Size",0), row.get("P6_Safety",0)]
    wts = [w["P1_Quality"], w["P2_Growth"], w["P3_Value"], w["P4_Discipline"], w["P5_Size"], w["P6_Safety"]]
    contribs = [s * wt * 10 for s, wt in zip(scores, wts)]
    colors = ["#4a9eff","#00e676","#ffd700","#ff6bc6","#ff9800","#ff4757"]
    fig = go.Figure(go.Bar(x=labels, y=contribs, marker_color=colors,
                           text=[f"{c:.1f}" for c in contribs], textposition="outside",
                           textfont=dict(color="#cdd9e5")))
    return dark_layout(fig, "Pillar Contribution to Score", 280)


# ──────────────────────────────────────────────────────────────────────────────
# ARROW / STREAMLIT SERIALISATION SAFETY
# ──────────────────────────────────────────────────────────────────────────────
def _arrow_safe_scalar(x):
    """Convert problematic Python/pandas objects into Arrow-safe scalars."""
    try:
        if x is None:
            return None
        if isinstance(x, (bytes, bytearray, memoryview)):
            try:
                return bytes(x).decode("utf-8", errors="ignore")
            except Exception:
                return repr(x)
        if isinstance(x, (pd.DataFrame, pd.Series)):
            try:
                return x.to_json(orient="split", date_format="iso")
            except Exception:
                return str(x)
        if isinstance(x, (dict, list, tuple, set, np.ndarray)):
            try:
                return json.dumps(x, default=str, ensure_ascii=False)
            except Exception:
                return str(x)
        return x
    except Exception:
        return str(x)


def _arrow_safe_df(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy safe for st.dataframe / pyarrow serialisation."""
    if df is None:
        return df
    safe = df.copy(deep=True)

    # DataFrame.attrs can also break pyarrow metadata serialisation.
    try:
        safe.attrs = {k: v for k, v in getattr(safe, "attrs", {}).items()
                      if isinstance(v, (str, int, float, bool, type(None)))}
    except Exception:
        try:
            safe.attrs = {}
        except Exception:
            pass

    # Make labels safe / JSON-serialisable.
    try:
        safe.columns = [str(c) for c in safe.columns]
    except Exception:
        pass
    try:
        if isinstance(safe.index, pd.MultiIndex):
            safe.index = safe.index.map(lambda x: " | ".join(map(str, x)))
    except Exception:
        pass

    for col in safe.columns:
        if pd.api.types.is_object_dtype(safe[col]) or pd.api.types.is_string_dtype(safe[col]):
            safe[col] = safe[col].map(_arrow_safe_scalar)
            # Final hardening: object/string cols become plain strings (preserve NaN/None).
            safe[col] = safe[col].map(lambda v: (np.nan if v is None else v))
    return safe


# ──────────────────────────────────────────────────────────────────────────────
# DISPLAY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def display_leaderboard(df: pd.DataFrame):
    # Summary stats bar
    _hidden = getattr(df, "attrs", {}).get("hidden_by_filters", 0)
    _total_scored = getattr(df, "attrs", {}).get("total_scored", len(df))
    if _hidden > 0:
        st.warning(
            f"⚠️ **{_hidden} of {_total_scored} scored stocks are hidden by active filters** "
            f"({len(df)} shown). Filters treating NaN as failing: try lowering "
            f"Min Piotroski → 0, Min ROCE → 0, or Min Score → 35.",
            icon="🔽")
    tier_counts = df["TIER_V40"].value_counts()
    c0, c1, c2, c3, c4, c5 = st.columns(6)
    c0.metric("Total", f"{len(df)} / {_total_scored}" if _hidden else len(df))
    c1.metric("🥇 Tier 1", tier_counts.get("🥇 TIER 1", 0))
    c2.metric("🥈 Tier 2", tier_counts.get("🥈 TIER 2", 0))
    c3.metric("🥉 Tier 3", tier_counts.get("🥉 TIER 3", 0))
    c4.metric("Prime Entry 🎯", int((df["Entry_Score"] >= 3.5).sum()))
    avg = df["SCORE_V40"].mean()
    c5.metric("Avg Score", f"{avg:.1f}")
    st.divider()

    # Compact table
    show_cols = ["Rank","Name","NSE Code","SCORE_V40","TIER_V40",
                 "P1_Quality","P2_Growth","P3_Value","P4_Discipline","P5_Size","P6_Safety",
                 "Fundamental_Score","Entry_Bonus","FCFYield_Pct","FCFYield_Basis","Entry_Signal",
                 "Promoter holding","Change in promoter holding",
                 "Change in FII holding","Pledged percentage",
                 "DISQ"]
    avail = [c for c in show_cols if c in df.columns]
    display = df[avail].copy()

    # Format numbers
    for col in ["P1_Quality","P2_Growth","P3_Value","P4_Discipline","P5_Size","P6_Safety"]:
        if col in display.columns:
            display[col] = display[col].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "-")
    if "Entry_Bonus" in display.columns:
        display["Entry_Bonus"] = display["Entry_Bonus"].apply(
            lambda x: f"+{x:.2f}" if pd.notna(x) and float(x) > 0.0 else "—")
    if "FCFYield_Pct" in display.columns:
        display["FCFYield_Pct"] = display["FCFYield_Pct"].apply(
            lambda x: f"{x:.1f}%" if pd.notna(x) else "-")

    # B1 FIX: Drop nested-detail columns not meant for compact table view
    _DICT_COLS = ["P1_Detail","P2_Detail","P3_Detail","P4_Detail","P5_Detail","P6_Detail",
                  "ALL_SIGNALS","Bonus","Entry_Score",
                  "P1_Signals","P2_Signals","P3_Signals","P4_Signals","P5_Signals","P6_Signals"]
    display = display.drop(columns=[c for c in _DICT_COLS if c in display.columns])
    display = _arrow_safe_df(display)
    st.dataframe(display, width="stretch", hide_index=True,
                 height=min(700, 40 + len(display) * 37))

    # Charts
    st.divider()
    col1, col2 = st.columns(2)
    with col1: st.plotly_chart(top_bar(df), width="stretch", key=f"leaderboard_top_bar_{len(df)}")
    with col2: st.plotly_chart(score_histogram(df), width="stretch", key=f"leaderboard_score_hist_{len(df)}")


def display_radar_tab(df: pd.DataFrame):
    st.markdown("#### 🕸️ Multi-Stock Pillar Comparison")
    names = df["Name"].head(30).tolist()
    sel = st.multiselect("Select 2-6 stocks to compare", names, default=names[:min(4, len(names))])
    if sel:
        st.plotly_chart(multi_radar(df, sel), width="stretch", key="radar_compare_" + "_".join(sel))

    st.markdown("#### Single-Stock Radar")
    single = st.selectbox("Detailed view", df["Name"].head(50).tolist())
    if single:
        sub = df[df["Name"] == single]
        if not sub.empty:
            st.plotly_chart(radar_chart(sub.iloc[0], single), width="stretch", key=f"single_radar_{single}")


def display_analytics(df: pd.DataFrame):
    st.plotly_chart(pillar_heatmap(df), width="stretch", key=f"analytics_heatmap_{len(df)}")
    col1, col2 = st.columns(2)
    with col1: st.plotly_chart(scatter_fcf_roic(df), width="stretch", key=f"analytics_scatter_fcf_roic_{len(df)}")
    with col2: st.plotly_chart(sector_chart(df), width="stretch", key=f"analytics_sector_chart_{len(df)}")
    st.plotly_chart(entry_chart(df), width="stretch", key=f"analytics_entry_chart_{len(df)}")


def display_stock_detail(df: pd.DataFrame, pw: dict):
    stock = st.selectbox("Select Stock for Deep Dive", df["Name"].head(100).tolist())
    if not stock: return
    sub = df[df["Name"] == stock]
    if sub.empty: return
    row = sub.iloc[0]
    tier = row.get("TIER_V40", "")
    score = row.get("SCORE_V40", 0)
    entry_sig = row.get("Entry_Signal", "")
    disq = row.get("DISQ", "")

    # Header
    tier_c = tier_css(tier); score_c = tier_score_css(tier)
    st.markdown(f"""
    <div class="metric-card {tier_c}">
    <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap">
        <div>
            <div style="font-size:.9rem;color:#8b9ab0;font-weight:600">ALCHEMY v4.0 ULTRA SCORE</div>
            <div class="score-mega {score_c}">{score}</div>
            <div style="font-size:1.1rem;font-weight:700;margin-top:2px">{tier}</div>
        </div>
        <div style="flex:1;min-width:200px">
            <div style="font-size:1.3rem;font-weight:800;color:#cdd9e5">{row.get('Name','')}</div>
            <div style="color:#8b9ab0;font-size:.85rem">{row.get('NSE Code', row.get('Symbol', row.get('Ticker', '')))} · {row.get('Industry','')}</div>
            <div style="margin-top:6px">
                <span style="color:{('#00e676' if 'PRIME' in str(entry_sig) else '#ff9800' if 'GOOD' in str(entry_sig) else '#ff4757')};font-size:.85rem;font-weight:700">
                    🎯 {entry_sig}
                </span>
            </div>
        </div>
    </div>
    {"".join(f'<span class="disq-pill">⛔ {d}</span>' for d in disq.split(";") if d.strip()) if disq else ""}
    </div>""", unsafe_allow_html=True)

    # Pillar Breakdown
    pillar_data = [
        ("P1 Quality",    row.get("P1_Quality",0),    row.get("P1_Signals",""), "#4a9eff", "20%", "[G] ROCE p=7.13e-5 | [Y] ROA | [A] FCF/PAT | [M] ROIC"),
        ("P2 Growth",     row.get("P2_Growth",0),     row.get("P2_Signals",""), "#00e676", "15%", "[G] PAT CAGR p=1.57e-4 | [O] EPS Accel | Rev CAGR demoted p=0.164"),
        ("P3 Value",      row.get("P3_Value",0),      row.get("P3_Signals",""), "#ffd700", "28%", "[Y] FCF Yield β=46-82 (#1) | [Y] B/M β=7-42 | [G] HistPE p=3.40e-22"),
        ("P4 Discipline", row.get("P4_Discipline",0), row.get("P4_Signals",""), "#ff6bc6", "13%", "[Y] Inv Dummy β=−5 to −23 | AssetGrowth ≤ EBITDAGrowth | AssetLight"),
        ("P5 Size",       row.get("P5_Size",0),       row.get("P5_Signals",""), "#ff9800", "7%",  "[F] SMB | India undiscovery alpha | Tight float"),
        ("P6 Safety",     row.get("P6_Safety",0),     row.get("P6_Signals",""), "#ff4757", "17%", "[G] D/E p=5.28e-19 (#1 India) | [P] Piotroski 88%MB | Pledge | IntCov"),
    ]

    st.markdown("<div class='section-title'>PILLAR BREAKDOWN</div>", unsafe_allow_html=True)
    for pl_name, pl_score, pl_sigs, color, weight, cite in pillar_data:
        bar_w = int(pl_score * 10)
        sig_class = "sig-good" if pl_score >= 7 else "sig-warn" if pl_score >= 4 else "sig-bad"
        st.markdown(f"""
        <div style="background:#161b22;border-radius:10px;padding:12px 16px;margin:6px 0;border-left:3px solid {color}">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
            <span style="font-weight:800;color:{color};font-size:.9rem">{pl_name}</span>
            <span style="font-size:.75rem;color:#8b9ab0">{weight} weight</span>
            <span style="font-weight:900;font-size:1.2rem;color:{color}">{pl_score:.1f}/10</span>
        </div>
        <div class="score-bar-bg"><div class="score-bar-fill" style="width:{bar_w}%;background:{color}40;border:1px solid {color}"></div></div>
        <div class="{sig_class}" style="margin-top:5px;font-size:.75rem">{pl_sigs}</div>
        <div style="color:#555;font-size:.68rem;margin-top:3px">{cite}</div>
        </div>""", unsafe_allow_html=True)

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(radar_chart(row, str(row.get("Name",""))), width="stretch", key=f"detail_radar_{stock}")
    with col2:
        st.plotly_chart(pillar_contribution_bar(row, pw), width="stretch", key=f"detail_pillar_bar_{stock}")

    # Score decomposition
    st.markdown("<div class='section-title'>SCORE DECOMPOSITION</div>", unsafe_allow_html=True)
    dc1, dc2, dc3, dc4 = st.columns(4)
    dc1.metric("Base Score", f"{row.get('Base_Score',0):.1f}")
    dc2.metric("Weakest-Link Pen.", f"−{row.get('WL_Penalty',0):.1f}")
    dc3.metric("Bonus (capped 8)", f"+{row.get('Bonus',0):.1f}")
    dc4.metric("Final Score", f"{row.get('SCORE_V40',0):.1f}")

    # Raw data
    with st.expander("📊 Raw Data"):
        raw_cols = [c for c in KEEP_COLS if c in df.columns and c in sub.columns]
        _raw_view = sub[raw_cols].T.reset_index().rename(columns={"index":"Field",0:"Value"})
        _raw_view = _arrow_safe_df(_raw_view)
        if "Value" in _raw_view.columns:
            _raw_view["Value"] = _raw_view["Value"].map(lambda v: np.nan if v is None else str(v))
        st.dataframe(_raw_view, width="stretch", hide_index=True)


def display_methodology():
    st.markdown("""
    <div class="main-header">⚗️ Alchemy v4.0 Ultra — Scientific Methodology</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="finding-box">
    <b>🔬 WORLD'S FIRST: Direct implementation of Yartseva (2025) BCU CAFÉ Working Paper #33</b><br>
    Analysis of 464 US multibaggers (2009–2024) using dynamic panel GMM — 150+ variables tested, 
    only statistically significant ones retained. All factor weights derived from β-coefficients and p-values.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📐 6-Pillar Architecture")

    methodology_data = {
        "Pillar": ["P1 Quality (20%)", "P2 Growth (15%)", "P3 Value (28%) ★", "P4 Discipline (13%) ★★NEW",
                   "P5 Size (7%)", "P6 Safety (17%)"],
        "Top Parameters": [
            "ROIC(28%) ROCE(25%) ROA(18%) FCF/PAT(17%) Moat(12%)",
            "PAT_CAGR5Y(38%) OPM_Expansion(28%) EPS_Accel(20%) RevCAGR(8%) Reinv(6%)",
            "FCF_Yield(40%) PE_vs_Hist(20%) B/M(18%) EV/EBITDA(12%) EV/Sales(6%) PEG(4%)",
            "InvGuard(50%) CapexEff(22%) CashConv(16%) ShhldrYield(12%)",
            "MCap_Band(50%) Inst_Gap(30%) Float(20%)",
            "D/E(35%) Piotroski(24%) Pledge(16%) IntCov(14%) Prom+FII(11%)",
        ],
        "Key Research": [
            "[G] ROCE p=7.13e-5 | [Y] ROA in ALL dynamic specs | [A] AQR FCF/PAT | [M] ROIC",
            "[G] PAT CAGR p=1.57e-4 | WARNING: earnings growth NOT sig in [Y] dynamic specs",
            "[Y] FCF/P β=46-82 #1 PREDICTOR | [G] HistPE p=3.40e-22 | [Y] B/M β=7-42",
            "[Y] Inv Dummy β=−5 to −23 | CORE FINDING: AssetGrowth MUST ≤ EBITDA Growth",
            "[F] Fama-French SMB | India small-cap discovery premium | Under-institutional coverage",
            "[G] D/E β=0.4586 p=5.28e-19 STRONGEST India | [P] Piotroski 88% multibaggers had F≥7",
        ]
    }
    st.dataframe(_arrow_safe_df(pd.DataFrame(methodology_data)), width="stretch", hide_index=True)

    st.markdown("""
    <div class="insight-box">
    <b>⚡ KEY YARTSEVA FINDINGS DIRECTLY IMPLEMENTED IN v4.0:</b><br>
    1. <b>FCF Yield is the single strongest global predictor</b> (β=46-82) → P3 elevated to 28%, FCFYield subweight=40%<br>
    2. <b>Investment Pattern Guard (P4)</b>: when asset growth > EBITDA growth, next-year returns fall −5 to −23pp → dedicated pillar<br>
    3. <b>Entry Signal</b>: stocks near 52-week LOW deliver higher next-year returns → Contrarian Entry Bonus up to +2pts<br>
    4. <b>ROA > EBITDA Margin</b> in dynamic specs: ROA implemented in P1 as key quality metric<br>
    5. <b>Earnings growth NOT significant</b> in dynamic models → P2 Growth demoted; PAT CAGR retained for India [G]<br>
    6. <b>B/M β=7-42</b>: Book-to-Market significant → P3 subweight=18%<br>
    7. <b>Asset-light businesses with growing EBITDA</b> score highest in P4
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
    <b>🏆 BONUS SYSTEM (Hard Cap: 8.0 pts):</b><br>
    • <b>Yartseva Compounder</b> (+3.5): FCFYield≥6% + B/M≥0.25 + PE<20 — Yartseva value trifecta<br>
    • <b>Twin Engine</b> (+3.0): ROIC≥20% + PAT_CAGR≥20% + PEG<1 — Mayer × Lynch alignment<br>
    • <b>QMJ Compounder</b> (+2.0): P1≥7.5 + P6≥7.5 — AQR Quality-Minus-Junk double-high<br>
    • <b>CANSLIM Catalyst</b> (+1.8): Quarterly acceleration + positive FCF + TTM>5Y trend<br>
    • <b>Prime Entry</b> (+2.0): Entry Score≥3.5 (near 52-week low) — Yartseva contrarian signal<br>
    • <b>Good Entry</b> (+1.0): Entry Score≥2.5 (moderate discount)<br>
    • <b>G-Factor Confirm</b> (+0.5): G-Factor≥9 + Quality+Safety aligned
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="finding-box">
    <b>🚨 DISQUALIFIER TRIPWIRES (any → score capped at 28):</b><br>
    D/E>2 | Pledge>25% | Piotroski≤3 | 5Y_PAT_Decline<-10% | PromoterSelling<-3%<br>
    FCFYield<-15% (cash destruction) | LossMaking+LowValue combination
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📚 Full Research References"):
        st.markdown("""
        **[Y] Yartseva, A. (2025)** — *The Alchemy of Multibagger Stocks.* BCU CAFÉ Working Paper #33.
        464 US multibaggers, dynamic panel GMM (Arellano-Bond + Blundell-Bond), 150+ variables tested.
        FCF/P β=46-82 | B/M β=7-42 | Inv Dummy β=−5 to −23 | ROA sig in all dynamic specs.

        **[G] Gunasekaran et al. (2024/IJCRT)** — 503 NSE+BSE multibaggers (2013-2023) OLS.
        D/E β=0.4586 p=5.28e-19 | P/FCF p=1.53e-12 | ROCE p=7.13e-5 | HistPE p=3.40e-22

        **[A] Asness, Frazzini, Pedersen (2019)** — AQR Quality-Minus-Junk. 4 sub-factors (25% each):
        Profitability, Growth, Safety, Payout. CFO/Assets as earnings quality metric.

        **[F] Fama & French (2015)** — Five-factor model. SMB (size), HML (value), RMW (profitability),
        CMA (investment). Conservative-minus-aggressive investment factor (REVERSED for multibaggers [Y]).

        **[M] Mayer, C.W. (2018)** — 100 Baggers. ROIC × Reinvestment Rate = intrinsic growth engine.
        Coffee-can portfolio (10yr hold). Twin engines: EPS + P/E expansion.

        **[L] Lynch, P. (1988, 1993)** — GARP (Growth At Reasonable Price). PEG < 1.0 as primary signal.
        Simple businesses, low analyst coverage.

        **[P] Piotroski, J.D. (2000)** — F-Score. Alta Fox Capital: 88% of US multibaggers had F≥7 at entry.
        9-component financial health score.

        **[O] O'Neil, W.J.** — CANSLIM. C=Current earnings, A=Annual growth, I=Institutional buying.
        Quarterly acceleration: current quarter > prior year × 1.25.

        **[JT] Jegadeesh & Titman (1993)** — Momentum. 6-month holding period optimal.
        Yartseva extends: multibaggers show REVERSAL pattern → near 52wk low = better entry.

        **[B] Buffett/Munger** — Economic moat, ROIC consistency, owner-operators, asset-light models.
        """)


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────

def build_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:10px 0 5px">
        <span style="font-size:2.5rem">⚗️</span><br>
        <span style="font-size:1.2rem;font-weight:900;background:linear-gradient(135deg,#ffd700,#ff8c00);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent">Alchemy v4.0 Ultra</span><br>
        <span style="font-size:.7rem;color:#666">World's Best Multibagger Engine</span>
        </div>""", unsafe_allow_html=True)
        st.divider()

        # FILE UPLOADS
        st.markdown("#### 📂 Data Sources")
        screen_files = st.file_uploader(
            "📊 Screener.in Query CSV(s)",
            type=["csv"], key="screener_csv",
            accept_multiple_files=True,
            help="Upload one or more CSVs from Screener.in. Multiple files are merged automatically — duplicates removed by Name.")
        if screen_files:
            st.caption(f"✅ {len(screen_files)} file(s) loaded — will be merged before scoring")
        nse_file = st.file_uploader(
            "📋 NSE Equity List",
            type=["csv"], key="nse_csv",
            help="Upload NSE equity list CSV (Symbol,SERIES). "
                 "If no Screener.in CSV is uploaded, stocks are fetched live via yfinance.")
        live_opts = {}
        if nse_file is not None and not screen_files:
            st.markdown(
                "<div style='background:#0a1628;border:1px solid #ffd700;border-radius:8px;"
                "padding:10px;margin:4px 0'>"
                "<span style='color:#ffd700;font-weight:700'>⚡ Live Fetch Mode</span><br>"
                "<span style='color:#8b9ab0;font-size:.78rem'>No Screener CSV uploaded — "
                "financial data will be fetched from yfinance for each symbol.</span></div>",
                unsafe_allow_html=True)
            _total_syms = len(symbols) if 'symbols' in dir() else "all"
            live_opts["max_n"] = st.select_slider(
                "Stocks to fetch",
                options=[50, 100, 200, 300, 500, 750, 1000, 1500, 9999],
                value=9999,
                help=(
                    "9999 = fetch ALL symbols in list. "
                    "Parallel fetching: ~3 min for 1800 stocks (yfinance) "
                    "+ ~5 min Screener.in enrichment."))
            live_opts["eq_only"] = st.checkbox("EQ series only", value=True)
            live_opts["use_screener"] = st.checkbox(
                "Deep Enrichment 🌐 (NSE/BSE/Trendlyne/Screener.in)",
                value=True,
                help=(
                    "Multi-source enrichment pipeline — no single dependency:\n"
                    "• RSI 14, 6M return, 52W High/Low: yfinance primary; jugaad-data fallback if installed\n"
                    "• FCF 3Y, Historical PE 5Y: computed from yfinance\n"
                    "• Promoter/FII/DII holding, Pledged %, Industry PE: NSE open API (primary)\n"
                    "• G-Factor: auto-computed from ROIC+EV/EBITDA; Trendlyne if needed\n"
                    "• Piotroski, 5Y CAGRs, ROIC, ROCE: Screener.in fallback only\n"
                    "Adds ~0.3s per stock. Disable for yfinance-only (faster, fewer fields)."))
            if live_opts["use_screener"] and not _SCR_OK:
                st.info("ℹ️ Install requests + beautifulsoup4 to enable Screener.in fallback: "
                        "`pip install requests beautifulsoup4` — NSE/computed enrichment still works without it.")
            if not _YF_OK and not _JGD_OK:
                st.error("⚠️ Neither yfinance nor jugaad-data is installed. Run: `pip install yfinance jugaad-data`")
            elif not _JGD_OK:
                st.info("ℹ️ jugaad-data not detected — optional fallback is inactive. Install with `pip install jugaad-data` if you want a secondary NSE market-data source.")
        elif nse_file is not None and screen_files:
            st.caption("✅ NSE list loaded — used for NSE-only filter")
        st.divider()

        # FILTERS
        st.markdown("#### 🎯 Filters")
        nse_only = st.checkbox("NSE Listed Only", value=True)
        entry_only = st.checkbox("🎯 Prime Entry Only (Yartseva signal)", value=False,
                                  help="Show only stocks near 52-week low (highest next-year return signal)")
        min_score = st.slider("Min Score", 0, 100, 35, 5,
                               help="Tier 1≥80 | Tier 2≥65 | Tier 3≥50 | Tier 4≥35")
        c1, c2 = st.columns(2)
        min_mcap = c1.number_input("Min MCap (Cr)", 0, 500000, 100, 100)
        max_mcap = c2.number_input("Max MCap (Cr)", 1000, 5000000, 1000000, 10000)
        max_de = st.slider("Max D/E", 0.0, 5.0, 2.0, 0.1,
                           help="NaN D/E always shown. DISQ fires at D/E>2 (India β=0.46, Gunasekaran 2024).")
        max_pledge = st.slider("Max Pledge %", 0, 100, 25, 5,
                               help="NaN Pledge always shown. DISQ fires at >25% — any material pledge is India governance red flag.")
        min_pio = st.slider("Min Piotroski", 0, 9, 0, 1,
                            help="0 = show all. NaN Piotroski stocks always shown regardless.")
        min_roce = st.slider("Min ROCE %", 0, 60, 0, 2,
                             help="0 = show all. NaN ROCE stocks always shown regardless.")

        _tier_defaults = ["🥇 TIER 1","🥈 TIER 2","🥉 TIER 3","⚠️ TIER 4"] if min_score <= 35 else                          ["🥇 TIER 1","🥈 TIER 2","🥉 TIER 3"] if min_score <= 50 else                          ["🥇 TIER 1","🥈 TIER 2"] if min_score <= 65 else ["🥇 TIER 1"]
        tier_choices = st.multiselect("Tiers to Include",
            ["🥇 TIER 1","🥈 TIER 2","🥉 TIER 3","⚠️ TIER 4","❌ TIER 5"],
            default=_tier_defaults,
            help="Defaults now align with Min Score. For Min Score 35, Tier 4 is included by default.")

        industries = []
        if screen_files:
            try:
                _frames = []
                for _f in screen_files:
                    _frames.append(pd.read_csv(_f, thousands=","))
                    _f.seek(0)
                _tmp = pd.concat(_frames, ignore_index=True)
                if "Industry" in _tmp.columns:
                    all_inds = sorted(_tmp["Industry"].dropna().unique().tolist())
                    industries = st.multiselect("Industries (blank=all)", all_inds, default=[])
            except:
                pass
        st.divider()

        # WEIGHT EDITOR
        st.markdown("#### ⚖️ Pillar Weight Editor")
        st.caption("Scientific defaults from peer-reviewed research — adjust with caution")
        with st.expander("Customise Weights", expanded=False):
            pw_custom = {}
            labels_map = {
                "P1_Quality": "P1 Quality [ROCE/ROIC/ROA]",
                "P2_Growth": "P2 Growth [PAT CAGR/OPM Exp]",
                "P3_Value": "P3 Value [FCF Yield #1]",
                "P4_Discipline": "P4 Discipline [Yartseva★★NEW]",
                "P5_Size": "P5 Size [SMB/Discovery]",
                "P6_Safety": "P6 Safety [D/E #1-India]",
            }
            for k, dv in DEFAULT_PILLAR_W.items():
                pw_custom[k] = st.slider(labels_map.get(k, k), 0, 50, int(dv), 1, key=f"pw_{k}")
            total_cust = sum(pw_custom.values())
            if total_cust > 0:
                pw_use = {k: v * 100.0 / total_cust for k, v in pw_custom.items()}
                st.caption("Normalised: " + " | ".join(f"{k.split('_')[0]}:{v:.0f}%" for k, v in pw_use.items()))
            else:
                pw_use = dict(DEFAULT_PILLAR_W)
            if st.button("↺ Reset to Scientific Defaults"):
                pw_use = dict(DEFAULT_PILLAR_W)
        try:
            pw_final = pw_use
        except Exception:
            pw_final = dict(DEFAULT_PILLAR_W)
        LOGGER.info("Using pillar weights: %s", {k: round(v, 2) for k, v in pw_final.items()})
        st.divider()

        _has_data = bool(screen_files) or (nse_file is not None)
        run_btn = st.button("⚗️ Run Alchemy v4.0 Ultra", type="primary",
                            width="stretch", disabled=(not _has_data))
        if not _has_data:
            st.info("Upload Screener.in CSV(s) **or** NSE Equity List to begin")
        elif nse_file is not None and not screen_files and not (_YF_OK or _JGD_OK):
            st.error("Install at least one live market-data source: `pip install yfinance jugaad-data`")
        _render_run_status_box()

    # ── Load & merge multiple Screener.in CSVs ──────────────────────────────
    df_main = None; df_nse = None
    if screen_files:
        frames = []
        for _f in screen_files:
            try:
                _df = _read_uploaded_csv(_f, thousands=",")
                frames.append(_df)
            except Exception as e:
                st.warning(f"⚠️ Could not read '{_f.name}': {e}")
        if frames:
            df_main = pd.concat(frames, ignore_index=True)
            # De-duplicate: keep first occurrence by Name (case-insensitive)
            if "Name" in df_main.columns:
                df_main["_name_lower"] = df_main["Name"].astype(str).str.strip().str.lower()
                df_main = df_main.drop_duplicates(subset="_name_lower", keep="first")
                df_main = df_main.drop(columns=["_name_lower"])
            df_main = df_main.reset_index(drop=True)
            total_rows = len(df_main)
            st.sidebar.success(f"✅ Merged {len(frames)} file(s) → {total_rows} unique stocks")

    if nse_file is not None:
        try:
            df_nse = _read_uploaded_csv(nse_file)
        except Exception:
            pass

    filters = {
        "nse_only": nse_only, "min_score": min_score,
        "min_mcap": min_mcap, "max_mcap": max_mcap,
        "max_de": max_de, "max_pledge": max_pledge,
        "min_pio": min_pio, "min_roce": min_roce,
        "tiers": tier_choices or None,
        "industries": industries or None,
        "entry_only": entry_only,
    }
    return df_main, df_nse, pw_final, filters, run_btn, live_opts, nse_file


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    st.markdown("""
    <div class="main-header-wrap">
        <div class="main-header">⚗️ Alchemy Screener v4.0 Ultra</div>
        <div class="sub-header">
            World’s Best Multibagger Engine · 6 Pillars · 35+ Parameters · 9 Research Sources<br>
            <span style="color:#ffd700">★ Directly implements Yartseva 2025 (BCU CAFÉ #33) — 464 multibaggers empirically validated</span>
            <span style="color:#4a9eff">&nbsp;★ P4 Yartseva Investment Guard · Entry Timing Signal · Cash ROIC · ROA Dynamic Spec</span>
        </div>
    </div>""", unsafe_allow_html=True)

    df_main, df_nse, pw_final, filters, run_btn, live_opts, nse_file_obj = build_sidebar()

    if "results_v40" not in st.session_state:
        st.session_state.results_v40 = None
    if "alchemy_sidebar_status" not in st.session_state:
        _set_run_status("Ready — upload files and run the engine.")

    if run_btn:
        if df_main is not None and len(df_main) > 0:
            # ── CSV Mode ──────────────────────────────────────────────────────
            _set_run_status(f"Running CSV mode on {len(df_main)} merged rows…")
            st.session_state.results_v40 = run_screen(df_main, df_nse, pw_final, filters)

        elif live_opts and nse_file_obj is not None and (_YF_OK or _JGD_OK):
            # ── Live Fetch Mode ───────────────────────────────────────────────
            try:
                nse_raw = _read_uploaded_csv(nse_file_obj)
                # B2 FIX: NSE official EQUITY_L.csv = SYMBOL|NAME OF COMPANY|SERIES|...
                # columns[1] is "NAME OF COMPANY" not "SERIES" — must detect by name
                sym_col = next(
                    (c for c in nse_raw.columns
                     if c.strip().upper() in ("SYMBOL","NSE CODE","NSE SYMBOL","TICKER")),
                    nse_raw.columns[0])  # fallback: first col
                ser_col = next(
                    (c for c in nse_raw.columns
                     if c.strip().upper() in ("SERIES","SERIES NAME")),
                    None)  # no fallback by position — too risky
                # Last resort: col[1] if its values look like series codes
                if ser_col is None and len(nse_raw.columns) > 1:
                    _cand = nse_raw.columns[1]
                    _samp = set(nse_raw[_cand].astype(str).str.strip().str.upper().unique()[:20])
                    if _samp.issubset({"EQ","BE","BZ","IL","SM","ST","N",""}):
                        ser_col = _cand
                if live_opts.get("eq_only") and ser_col:
                    nse_raw = nse_raw[nse_raw[ser_col].astype(str).str.strip().str.upper() == "EQ"]
                symbols = nse_raw[sym_col].astype(str).str.strip().tolist()
                symbols = [s for s in symbols if s and s.lower() not in ("nan","","symbol")]
                if not symbols:
                    st.error(
                        f"⚠️ No symbols found after EQ filter. "
                        f"Columns found: {list(nse_raw.columns[:6])}. "
                        "NSE CSV should have SYMBOL | NAME OF COMPANY | SERIES | columns.")
                    st.stop()

                st.info(f"⚡ Live Fetch Mode — fetching up to {live_opts['max_n']} stocks "
                        f"from {len(symbols)} NSE EQ symbols via yfinance…")
                _set_run_status(f"Live fetch mode started — {len(symbols)} NSE symbols queued.")
                prog_bar  = st.progress(0, text="Starting fetch…")
                status_el = st.empty()

                fetched = fetch_nse_live_data(
                    symbols, live_opts["max_n"], prog_bar, status_el,
                    use_screener=live_opts.get("use_screener", True))

                status_el.empty()
                if fetched.empty:
                    _set_run_status("Live fetch failed — no rows returned.")
                    st.error("No data fetched. Check yfinance connectivity.")
                else:
                    st.success(f"✅ Fetched {len(fetched)} stocks — running Alchemy scoring…")
                    st.session_state.results_v40 = run_screen(
                        fetched, None, pw_final, filters)
            except Exception as e:
                _set_run_status(f"Live fetch error: {e}")
                st.error(f"Live fetch error: {e}")

    out = st.session_state.results_v40

    if out is None:
        # Landing page
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            <div class="hero-card">
                <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:18px;flex-wrap:wrap">
                    <div style="flex:1;min-width:320px">
                        <div style="font-size:1.65rem;font-weight:900;color:#ffd700;line-height:1.2;margin:0 0 8px 0">Welcome to Alchemy v4.0 Ultra</div>
                        <div style="color:#9fb1c7;font-size:.96rem;line-height:1.6;max-width:760px;margin-bottom:14px">
                            Upload one or more Screener.in CSVs from different queries, then run the engine to merge, enrich, score, and rank the universe.
                        </div>
                    </div>
                    <div style="min-width:220px;max-width:280px;background:rgba(255,215,0,.06);border:1px solid rgba(255,215,0,.16);border-radius:12px;padding:12px 14px">
                        <div style="color:#ffd700;font-size:.76rem;font-weight:800;letter-spacing:.04em;text-transform:uppercase;margin-bottom:6px">Quick Start</div>
                        <div style="color:#c8d3df;font-size:.84rem;line-height:1.55">
                            Upload CSVs in the sidebar and click <b>Run Alchemy v4.0 Ultra</b>.
                        </div>
                    </div>
                </div>
                <div style="margin-top:6px;color:#77879b;font-size:.83rem;line-height:1.65">
                    <b style="color:#4a9eff">How to export from Screener.in</b><br>
                    1. Go to screener.in → Screens → Create New Screen<br>
                    2. Add the required parameters from the recommended query below<br>
                    3. Run the query and choose <b>Export to Excel/CSV</b><br>
                    4. Upload one or more CSVs in the sidebar — duplicates will be merged automatically
                </div>
            </div>""", unsafe_allow_html=True)

            with st.expander("📝 Recommended Screener.in Query"):
                st.code("""
Market Capitalization > 100 AND
Return on capital employed > 5 AND
Piotroski score > 3 AND
Pledged percentage < 60 AND
Profit after tax > 0
                """, language="sql")
                st.caption("Run this on Screener.in to get a broad starting universe. The Alchemy engine then scores and ranks all stocks.")

        with col2:
            st.markdown("""
            <div class="metric-card" style="padding:20px">
            <div style="font-size:.85rem;font-weight:800;color:#ffd700;margin-bottom:10px">WEIGHT MATRIX</div>
            """, unsafe_allow_html=True)

            wm = pd.DataFrame({
                "Pillar": ["P1 Quality","P2 Growth","P3 Value ★","P4 Discipline ★","P5 Size","P6 Safety"],
                "Wt": ["20%","15%","28%","13%","7%","17%"],
                "Top Factor": ["ROIC 28%","PAT CAGR 38%","FCFYield 40%","InvGuard 50%","MCap 50%","D/E 35%"],
                "Key Paper": ["[G] p=7.13e-5","[G] p=1.57e-4","[Y] β=46-82","[Y] β=−5→−23","[F] SMB","[G] p=5.28e-19★"],
            })
            st.dataframe(_arrow_safe_df(wm), width="stretch", hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

        return

    if out.empty:
        st.warning("No stocks match current filters. The filter stack is currently stricter than the scored universe.")
        _diag = st.session_state.get("filter_diag_v40") or {}
        _total = int(_diag.get("total", 0) or 0)
        _pass = _diag.get("pass", {}) or {}
        if _pass:
            _worst = sorted(_pass.items(), key=lambda kv: kv[1])[:5]
            _lines = [f"• {k}: {v}/{_total} stocks pass" for k, v in _worst]
            st.info("Most restrictive filters right now:\n" + "\n".join(_lines))
            if filters.get("min_score", 0) <= 35 and filters.get("tiers") and "⚠️ TIER 4" not in filters.get("tiers"):
                st.caption("Your Min Score allows Tier 4, but Tier 4 is excluded in tier selection. That mismatch often causes empty results.")
        _preview = st.session_state.get("scored_unfiltered_v40")
        if isinstance(_preview, pd.DataFrame) and not _preview.empty:
            st.markdown("#### Top ranked stocks before filters")
            _cols = [c for c in ["Name","NSE Code","Industry","SCORE_V40","TIER_V40","Entry_Signal","DISQ"] if c in _preview.columns]
            st.dataframe(_arrow_safe_df(_preview[_cols].head(20)), width="stretch", hide_index=True)
        return

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 Leaderboard", "🕸️ Radar Compare",
        "📊 Analytics", "🔬 Stock Deep Dive", "📚 Methodology"
    ])
    with tab1: display_leaderboard(out)
    with tab2: display_radar_tab(out)
    with tab3: display_analytics(out)
    with tab4: display_stock_detail(out, pw_final)
    with tab5: display_methodology()


if __name__ == "__main__":
    main()
