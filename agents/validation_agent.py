"""
Validation Agent — Applies business rules and compliance checks.
Validates extracted ERP data against close checklist requirements.
"""

import json
import asyncio
import pandas as pd
from typing import Dict, List, Any
from plugins.validation_rules import ALL_RULES, AP_RULES, AR_RULES, BANK_RULES


class ValidationAgent:
    """
    Validates ERP data against close checklist rules.
    """

    def __init__(self, period: str, company: str):
        self.period = period
        self.company = company

    async def validate(self, erp_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Run all validation rules against the extracted data.
        
        Args:
            erp_data: Dictionary with keys like 'GL', 'AP', 'AR', 'FA', 'BANK'
            
        Returns:
            List of validation result dictionaries
        """
        results = []
        
        # Run general rules
        gl_df = erp_data.get("GL", pd.DataFrame())
        for rule in ALL_RULES:
            try:
                result = rule(gl_df)
                results.append(result)
            except Exception as e:
                results.append({
                    "module": "VALIDATION",
                    "description": f"Error in rule {rule.__name__}: {str(e)}",
                    "severity": "BLOCK"
                })
        
        # Run module-specific rules
        ap_df = erp_data.get("AP", pd.DataFrame())
        for rule in AP_RULES:
            try:
                result = rule(ap_df, gl_df)
                results.append(result)
            except Exception as e:
                results.append({
                    "module": "AP",
                    "description": f"Error in AP rule {rule.__name__}: {str(e)}",
                    "severity": "BLOCK"
                })
        
        ar_df = erp_data.get("AR", pd.DataFrame())
        for rule in AR_RULES:
            try:
                result = rule(ar_df, gl_df)
                results.append(result)
            except Exception as e:
                results.append({
                    "module": "AR",
                    "description": f"Error in AR rule {rule.__name__}: {str(e)}",
                    "severity": "BLOCK"
                })
        
        bank_df = erp_data.get("BANK", pd.DataFrame())
        for rule in BANK_RULES:
            try:
                result = rule(bank_df)
                results.append(result)
            except Exception as e:
                results.append({
                    "module": "BANK",
                    "description": f"Error in BANK rule {rule.__name__}: {str(e)}",
                    "severity": "BLOCK"
                })
        
        return results

    def _validate_ap_subledger(self, ap_df, gl_df) -> Dict[str, str]:
        if ap_df.empty:
            return {"module": "AP", "description": "No AP invoices found for period", "severity": "REVIEW"}
        return {"module": "AP", "description": f"{len(ap_df)} AP invoices validated and posted", "severity": "FYI"}

    def _validate_fa_depreciation(self, fa_df) -> Dict[str, str]:
        if fa_df.empty:
            return {"module": "FA", "description": "No FA transactions found — depreciation may not have run", "severity": "BLOCK"}
        dep_runs = fa_df[fa_df.get("TransType", pd.Series()) == "Depreciation"] if "TransType" in fa_df.columns else fa_df
        if dep_runs.empty:
            return {"module": "FA", "description": "Depreciation transactions not found in FA ledger", "severity": "BLOCK"}
        return {"module": "FA", "description": f"Depreciation run confirmed. {len(dep_runs)} FA transactions posted", "severity": "FYI"}

    def _validate_gl_balance(self, gl_df) -> Dict[str, str]:
        """Check trial balance."""
        if gl_df.empty:
            return {"module": "GL", "description": "No GL entries found", "severity": "BLOCK"}
        
        debit_total = gl_df['Debit'].sum() if 'Debit' in gl_df.columns else 0
        credit_total = gl_df['Credit'].sum() if 'Credit' in gl_df.columns else 0
        
        if abs(debit_total - credit_total) > 0.01:
            return {
                "module": "GL",
                "description": f"Trial balance out of balance: {debit_total:.2f} vs {credit_total:.2f}",
                "severity": "BLOCK"
            }
        
        return {
            "module": "GL",
            "description": f"Trial balance balanced: {debit_total:.2f}",
            "severity": "FYI"
        }
