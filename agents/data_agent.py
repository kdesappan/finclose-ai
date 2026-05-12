"""
Data Agent — Extracts financial data from D365 ERP system.
Coordinates data extraction from various modules for close validation.
"""

import asyncio
import pandas as pd
from typing import Dict, Any
from plugins.d365_plugin import D365Plugin


class DataAgent:
    """
    Extracts and processes financial data from D365.
    """

    def __init__(self, period: str, company: str):
        self.period = period
        self.company = company
        self.d365 = D365Plugin()

    async def extract_data(self) -> Dict[str, pd.DataFrame]:
        """
        Extract all required data for close validation.
        
        Returns:
            Dictionary with DataFrames for each module
        """
        try:
            # Extract data concurrently
            tasks = [
                self._extract_gl(),
                self._extract_ap(),
                self._extract_ar(),
                self._extract_fa(),
                self._extract_bank(),
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle results
            data = {}
            modules = ["GL", "AP", "AR", "FA", "BANK"]
            for module, result in zip(modules, results):
                if isinstance(result, Exception):
                    print(f"Error extracting {module}: {str(result)}")
                    data[module] = pd.DataFrame()
                else:
                    data[module] = result
            
            return data
            
        except Exception as e:
            print(f"Data extraction error: {str(e)}")
            return {
                "GL": pd.DataFrame(),
                "AP": pd.DataFrame(),
                "AR": pd.DataFrame(),
                "FA": pd.DataFrame(),
                "BANK": pd.DataFrame(),
            }

    async def _extract_gl(self) -> pd.DataFrame:
        """Extract General Ledger data."""
        json_str = await asyncio.get_event_loop().run_in_executor(
            None, self.d365.get_gl_entries, self.period
        )
        return pd.read_json(json_str, orient="records")

    async def _extract_ap(self) -> pd.DataFrame:
        """Extract Accounts Payable data."""
        json_str = await asyncio.get_event_loop().run_in_executor(
            None, self.d365.get_ap_invoices, self.period
        )
        return pd.read_json(json_str, orient="records")

    async def _extract_ar(self) -> pd.DataFrame:
        """Extract Accounts Receivable data."""
        json_str = await asyncio.get_event_loop().run_in_executor(
            None, self.d365.get_ar_invoices, self.period
        )
        return pd.read_json(json_str, orient="records")

    async def _extract_fa(self) -> pd.DataFrame:
        """Extract Fixed Assets data."""
        json_str = await asyncio.get_event_loop().run_in_executor(
            None, self.d365.get_fixed_assets, self.period
        )
        return pd.read_json(json_str, orient="records")

    async def _extract_bank(self) -> pd.DataFrame:
        """Extract Bank data."""
        json_str = await asyncio.get_event_loop().run_in_executor(
            None, self.d365.get_bank_transactions, self.period
        )
        return pd.read_json(json_str, orient="records")
