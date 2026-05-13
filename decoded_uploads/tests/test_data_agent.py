"""
Tests for DataAgent — Validates D365 OData extraction logic.
Run with: pytest tests/test_data_agent.py -v
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from agents.data_agent import DataAgent


SAMPLE_GL = [
    {"AccountingDate": "2026-04-15", "LedgerAccount": "6200", "Debit": 1000.0, "Credit": 0.0, "Voucher": "JNL-001"},
    {"AccountingDate": "2026-04-15", "LedgerAccount": "2300", "Debit": 0.0, "Credit": 1000.0, "Voucher": "JNL-001"},
]
SAMPLE_AP = [
    {"InvoiceDate": "2026-04-10", "InvoiceAccount": "VEND-001", "AmountCurDebit": 500.0, "InvoiceId": "INV-001"},
]


@pytest.fixture
def agent():
    with patch.dict("os.environ", {
        "D365_BASE_URL": "https://test.dynamics.com",
        "D365_CLIENT_ID": "test-client",
        "D365_CLIENT_SECRET": "test-secret",
        "D365_TENANT_ID": "test-tenant",
        "D365_COMPANY_ID": "USMF",
    }):
        return DataAgent(period="2026-04", company="USMF")


def test_agent_initialization(agent):
    assert agent.period == "2026-04"
    assert agent.company == "USMF"


@patch("agents.data_agent.DataAgent._extract_gl")
@patch("agents.data_agent.DataAgent._extract_ap")
@patch("agents.data_agent.DataAgent._extract_ar")
@patch("agents.data_agent.DataAgent._extract_fa")
@patch("agents.data_agent.DataAgent._extract_bank")
@pytest.mark.asyncio
async def test_extract_data_success(mock_bank, mock_fa, mock_ar, mock_ap, mock_gl, agent):
    mock_gl.return_value = pd.DataFrame(SAMPLE_GL)
    mock_ap.return_value = pd.DataFrame(SAMPLE_AP)
    mock_ar.return_value = pd.DataFrame()
    mock_fa.return_value = pd.DataFrame()
    mock_bank.return_value = pd.DataFrame()

    result = await agent.extract_data()

    assert "GL" in result
    assert "AP" in result
    assert len(result["GL"]) == 2
    assert len(result["AP"]) == 1


@patch("agents.data_agent.DataAgent._extract_gl")
@pytest.mark.asyncio
async def test_extract_data_with_exception(mock_gl, agent):
    mock_gl.side_effect = Exception("API Error")

    result = await agent.extract_data()

    assert result["GL"].empty
    assert "AP" in result
