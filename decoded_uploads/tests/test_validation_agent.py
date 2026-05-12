"""
Tests for ValidationAgent — Validates close check logic.
Run with: pytest tests/test_validation_agent.py -v
"""

import pytest
import pandas as pd
from agents.validation_agent import ValidationAgent


@pytest.fixture
def agent():
    return ValidationAgent(period="2026-04", company="USMF")


@pytest.fixture
def balanced_gl():
    return pd.DataFrame([
        {"Debit": 1000.0, "Credit": 0.0, "LedgerAccount": "6200"},
        {"Debit": 0.0, "Credit": 1000.0, "LedgerAccount": "2300"},
    ])


@pytest.fixture
def unbalanced_gl():
    return pd.DataFrame([
        {"Debit": 1500.0, "Credit": 0.0, "LedgerAccount": "6200"},
        {"Debit": 0.0, "Credit": 1000.0, "LedgerAccount": "2300"},
    ])


@pytest.fixture
def sample_ap():
    return pd.DataFrame([
        {"InvoiceDate": "2026-04-10", "InvoiceAccount": "VEND-001", "AmountCurDebit": 500.0},
    ])


@pytest.fixture
def sample_fa():
    return pd.DataFrame([
        {"TransDate": "2026-04-30", "AssetId": "FA-001", "TransType": "Depreciation", "Amount": -250.0},
    ])


def test_balanced_gl_passes(agent, balanced_gl):
    result = agent._validate_gl_balance(balanced_gl)
    assert result["severity"] == "FYI"
    assert "balanced" in result["description"]


def test_unbalanced_gl_blocks(agent, unbalanced_gl):
    result = agent._validate_gl_balance(unbalanced_gl)
    assert result["severity"] == "BLOCK"
    assert "out of balance" in result["description"]


def test_empty_gl_blocks(agent):
    result = agent._validate_gl_balance(pd.DataFrame())
    assert result["severity"] == "BLOCK"
    assert "No GL entries" in result["description"]


def test_ap_with_data_passes(agent, sample_ap, balanced_gl):
    result = agent._validate_ap_subledger(sample_ap, balanced_gl)
    assert result["severity"] == "FYI"


def test_empty_ap_review(agent, balanced_gl):
    result = agent._validate_ap_subledger(pd.DataFrame(), balanced_gl)
    assert result["severity"] == "REVIEW"


def test_fa_with_depreciation_passes(agent, sample_fa):
    result = agent._validate_fa_depreciation(sample_fa)
    assert result["severity"] == "FYI"


def test_empty_fa_blocks(agent):
    result = agent._validate_fa_depreciation(pd.DataFrame())
    assert result["severity"] == "BLOCK"
