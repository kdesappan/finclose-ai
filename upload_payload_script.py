import base64
import json
import os
from typing import Dict, List

# Script to generate upload payload for testing

def create_upload_payload():
    """Create a sample upload payload for testing the system."""
    
    # Sample data structure
    payload = {
        "metadata": {
            "company": "USMF",
            "period": "2026-04",
            "upload_type": "close_data",
            "timestamp": "2026-05-12T10:00:00Z"
        },
        "data": {
            "gl_entries": [
                {
                    "date": "2026-04-15",
                    "account": "6200",
                    "debit": 1000.0,
                    "credit": 0.0,
                    "description": "Sample GL entry"
                },
                {
                    "date": "2026-04-15",
                    "account": "2300",
                    "debit": 0.0,
                    "credit": 1000.0,
                    "description": "Sample GL entry"
                }
            ],
            "ap_invoices": [
                {
                    "date": "2026-04-10",
                    "vendor": "VEND-001",
                    "amount": 500.0,
                    "status": "Posted"
                }
            ],
            "ar_invoices": [
                {
                    "date": "2026-04-12",
                    "customer": "CUST-001",
                    "amount": 800.0,
                    "status": "Posted"
                }
            ],
            "fa_transactions": [
                {
                    "date": "2026-04-30",
                    "asset_id": "FA-001",
                    "type": "Depreciation",
                    "amount": -250.0
                }
            ],
            "bank_transactions": [
                {
                    "date": "2026-04-15",
                    "account": "BANK-001",
                    "amount": 1000.0,
                    "type": "Deposit"
                }
            ]
        }
    }
    
    return payload

if __name__ == "__main__":
    payload = create_upload_payload()
    
    # Save as JSON
    with open('upload_payload.json', 'w') as f:
        json.dump(payload, f, indent=2)
    
    print("Upload payload created: upload_payload.json")
    
    # Also create base64 encoded version for API testing
    payload_str = json.dumps(payload)
    encoded = base64.b64encode(payload_str.encode()).decode()
    
    with open('upload_payload.b64', 'w') as f:
        f.write(encoded)
    
    print("Base64 encoded payload created: upload_payload.b64")
