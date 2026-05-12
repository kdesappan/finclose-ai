"""
FinClose AI — Autonomous Finance Close Orchestrator

This project implements an AI-powered autonomous finance close system using Microsoft Agent Framework.
The system orchestrates data extraction, validation, and reporting for comprehensive financial close processes.

Features:
- Multi-agent architecture for specialized financial operations
- D365 ERP integration for data extraction
- Excel-based reporting with automated formatting
- Comprehensive validation rules engine
- IFRS compliance mapping
- Real-time close checklist management

Architecture:
- Orchestrator Agent: Coordinates the entire close process
- Data Agent: Extracts and processes financial data from D365
- Validation Agent: Applies business rules and compliance checks
- Reporting Agent: Generates formatted Excel reports

Prerequisites:
- Python 3.8+
- D365 environment access
- Azure AD authentication setup

Installation:
1. Clone the repository
2. Install dependencies: pip install -r requirements.txt
3. Configure environment variables in .env
4. Run the orchestrator: python main.py

For detailed documentation, see the README files in each module.
"""

import asyncio
import os
import json
import base64
from typing import Dict, List, Any
from agents.orchestrator_agent import OrchestratorAgent
from agents.data_agent import DataAgent
from agents.validation_agent import ValidationAgent
from agents.reporting_agent import ReportingAgent


class FinCloseAI:
    """
    Main orchestrator for the FinClose AI system.
    Coordinates data extraction, validation, and reporting agents.
    """
    
    def __init__(self, period: str, company: str):
        self.period = period
        self.company = company
        self.orchestrator = OrchestratorAgent(period, company)
        self.data_agent = DataAgent(period, company)
        self.validation_agent = ValidationAgent(period, company)
        self.reporting_agent = ReportingAgent(period, company)
        
    async def run_close_process(self) -> Dict[str, Any]:
        """
        Execute the complete financial close process.
        
        Returns:
            Dict containing validation results and report paths
        """
        try:
            # Step 1: Extract data from D365
            print(f"Starting data extraction for {self.company} - {self.period}")
            erp_data = await self.data_agent.extract_data()
            
            # Step 2: Run validation checks
            print("Running validation checks...")
            validation_results = await self.validation_agent.validate(erp_data)
            
            # Step 3: Generate reports
            print("Generating close reports...")
            report_path = await self.reporting_agent.generate_report(erp_data, validation_results)
            
            return {
                "status": "success",
                "validation_results": validation_results,
                "report_path": report_path,
                "period": self.period,
                "company": self.company
            }
            
        except Exception as e:
            print(f"Error in close process: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "period": self.period,
                "company": self.company
            }


async def main():
    """
    Main entry point for the FinClose AI system.
    """
    # Configuration
    PERIOD = os.getenv("CLOSE_PERIOD", "2026-04")
    COMPANY = os.getenv("COMPANY_ID", "USMF")
    
    print(f"FinClose AI - Starting autonomous close for {COMPANY} - {PERIOD}")
    
    # Initialize and run the system
    finclose = FinCloseAI(PERIOD, COMPANY)
    result = await finclose.run_close_process()
    
    # Output results
    print("\n=== Close Process Results ===")
    print(json.dumps(result, indent=2))
    
    if result["status"] == "success":
        print(f"\nReport generated: {result['report_path']}")
    

if __name__ == "__main__":
    asyncio.run(main())
