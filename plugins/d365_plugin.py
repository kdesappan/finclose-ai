"""
D365 Plugin — MAAF-compatible plugin for Dynamics 365 F&O OData API calls.
Wraps common D365 data fetch operations as callable agent tools.
"""

import os
import requests
import pandas as pd
from msal import ConfidentialClientApplication
from typing import Dict, List, Any
from semantic_kernel.functions import kernel_function
from typing import Annotated


class D365Plugin:
    """
    Exposes D365 OData queries as agent-callable tools.
    """

    def __init__(self):
        self.base_url = os.environ["D365_BASE_URL"]
        self.company = os.environ["D365_COMPANY_ID"]
        self._token = None

    def _get_token(self) -> str:
        if self._token:
            return self._token
        app = ConfidentialClientApplication(
            client_id=os.environ["D365_CLIENT_ID"],
            client_credential=os.environ["D365_CLIENT_SECRET"],
            authority=f"https://login.microsoftonline.com/{os.environ['D365_TENANT_ID']}",
        )
        result = app.acquire_token_for_client(scopes=[f"{self.base_url}/.default"])
        self._token = result["access_token"]
        return self._token

    def _fetch(self, entity: str, filters: str = "", select: str = "") -> pd.DataFrame:
        url = f"{self.base_url}/data/{entity}"
        params = {"cross-company": "true", "$filter": f"dataAreaId eq '{self.company}'"}
        if filters:
            params["$filter"] += f" and {filters}"
        if select:
            params["$select"] = select
        headers = {"Authorization": f"Bearer {self._get_token()}"}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return pd.DataFrame(response.json().get("value", []))

    @kernel_function(description="Fetch General Ledger journal lines for a given accounting period.")
    def get_gl_entries(
        self,
        period: Annotated[str, "Accounting period in YYYY-MM format, e.g. 2026-04"],
    ) -> str:
        df = self._fetch(
            "LedgerJournalLines",
            filters=f"AccountingDate ge {period}-01 and AccountingDate le {period}-31",
            select="AccountingDate,LedgerAccount,Debit,Credit,TransactionCurrencyCode,Voucher",
        )
        return df.to_json(orient="records")

    @kernel_function(description="Fetch Accounts Payable vendor invoice lines for a given period.")
    def get_ap_invoices(
        self,
        period: Annotated[str, "Accounting period in YYYY-MM format, e.g. 2026-04"],
    ) -> str:
        df = self._fetch(
            "VendorInvoiceJournalLines",
            filters=f"InvoiceDate ge {period}-01 and InvoiceDate le {period}-31",
            select="InvoiceDate,InvoiceAccount,AmountCurDebit,AmountCurCredit,CurrencyCode,InvoiceId",
        )
        return df.to_json(orient="records")

    @kernel_function(description="Fetch Accounts Receivable customer invoice lines for a given period.")
    def get_ar_invoices(
        self,
        period: Annotated[str, "Accounting period in YYYY-MM format, e.g. 2026-04"],
    ) -> str:
        df = self._fetch(
            "CustInvoiceJournalLines",
            filters=f"InvoiceDate ge {period}-01 and InvoiceDate le {period}-31",
            select="InvoiceDate,InvoiceAccount,AmountCurDebit,AmountCurCredit,CurrencyCode,InvoiceId",
        )
        return df.to_json(orient="records")

    @kernel_function(description="Fetch Fixed Asset transactions for a given period.")
    def get_fixed_assets(
        self,
        period: Annotated[str, "Accounting period in YYYY-MM format, e.g. 2026-04"],
    ) -> str:
        df = self._fetch(
            "FixedAssetTransactions",
            filters=f"TransDate ge {period}-01 and TransDate le {period}-31",
            select="TransDate,AssetId,TransType,Amount,BookId",
        )
        return df.to_json(orient="records")

    @kernel_function(description="Fetch bank account transactions for a given period.")
    def get_bank_transactions(
        self,
        period: Annotated[str, "Accounting period in YYYY-MM format, e.g. 2026-04"],
    ) -> str:
        df = self._fetch(
            "BankAccountTransactions",
            filters=f"TransactionDate ge {period}-01 and TransactionDate le {period}-31",
            select="TransactionDate,BankAccountId,Amount,CurrencyCode,TransType",
        )
        return df.to_json(orient="records")

    @kernel_function(description="Fetch the Chart of Accounts (main accounts) for the company.")
    def get_chart_of_accounts(self) -> str:
        df = self._fetch(
            "MainAccounts",
            select="MainAccountId,Name,Type,AccountCategoryRef",
        )
        return df.to_json(orient="records")
