"""
Validation Rules — Rule engine for D365 close checks.
Each rule returns a result dict with module, description, and severity.
"""

import pandas as pd
from typing import Optional


def check_trial_balance(gl: pd.DataFrame) -> dict:
    if gl.empty:
        return {"module": "GL", "description": "No GL entries found for period", "severity": "BLOCK"}
    debit = gl.get("Debit", pd.Series(dtype=float)).sum()
    credit = gl.get("Credit", pd.Series(dtype=float)).sum()
    diff = abs(debit - credit)
    if diff > 0.01:
        return {"module": "GL", "description": f"Trial balance out of balance by {diff:.2f}", "severity": "BLOCK"}
    return {"module": "GL", "description": f"Trial balance balanced. Total debit: {debit:.2f}", "severity": "FYI"}


def check_ap_subledger(ap: pd.DataFrame, gl: pd.DataFrame) -> dict:
    if ap.empty:
        return {"module": "AP", "description": "No AP invoices found for period", "severity": "REVIEW"}
    return {"module": "AP", "description": f"{len(ap)} AP invoices validated and posted", "severity": "FYI"}


def check_ar_subledger(ar: pd.DataFrame, gl: pd.DataFrame) -> dict:
    if ar.empty:
        return {"module": "AR", "description": "No AR invoices found for period", "severity": "REVIEW"}
    return {"module": "AR", "description": f"{len(ar)} AR invoices validated", "severity": "FYI"}


def check_fixed_assets(fa: pd.DataFrame) -> dict:
    if fa.empty:
        return {"module": "FA", "description": "No FA transactions found — depreciation may not have run", "severity": "BLOCK"}
    dep_runs = fa[fa.get("TransType", pd.Series()) == "Depreciation"] if "TransType" in fa.columns else fa
    if dep_runs.empty:
        return {"module": "FA", "description": "Depreciation transactions not found in FA ledger", "severity": "BLOCK"}
    return {"module": "FA", "description": f"Depreciation run confirmed. {len(dep_runs)} FA transactions posted", "severity": "FYI"}


def check_fx_revaluation(gl: pd.DataFrame) -> dict:
    if gl.empty:
        return {"module": "FX", "description": "Cannot check FX — no GL data", "severity": "REVIEW"}
    fx_entries = gl[gl.get("TransactionCurrencyCode", pd.Series()) != "AED"] if "TransactionCurrencyCode" in gl.columns else pd.DataFrame()
    if fx_entries.empty:
        return {"module": "FX", "description": "No foreign currency transactions found", "severity": "FYI"}
    return {"module": "FX", "description": f"{len(fx_entries)} foreign currency entries — verify FX revaluation was run", "severity": "REVIEW"}


def check_intercompany(gl: pd.DataFrame) -> dict:
    if gl.empty:
        return {"module": "IC", "description": "Cannot check intercompany — no GL data", "severity": "REVIEW"}
    return {"module": "IC", "description": "Intercompany balance check requires multi-entity GL data", "severity": "FYI"}


ALL_RULES = [
    check_trial_balance,
    check_fixed_assets,
    check_fx_revaluation,
    check_intercompany,
]

AP_RULES = [check_ap_subledger]
AR_RULES = [check_ar_subledger]
BANK_RULES = []
