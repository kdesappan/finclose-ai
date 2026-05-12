"""
Orchestrator Agent — Coordinates the entire financial close process.
Manages the sequence of data extraction, validation, and reporting.
"""

import asyncio
from typing import Dict, Any
from agents.data_agent import DataAgent
from agents.validation_agent import ValidationAgent
from agents.reporting_agent import ReportingAgent


class OrchestratorAgent:
    """
    Orchestrates the financial close process.
    """

    def __init__(self, period: str, company: str):
        self.period = period
        self.company = company

    async def run_close(self) -> Dict[str, Any]:
        """
        Execute the complete close process.
        
        Returns:
            Close results dictionary
        """
        try:
            # Initialize agents
            data_agent = DataAgent(self.period, self.company)
            validation_agent = ValidationAgent(self.period, self.company)
            reporting_agent = ReportingAgent(self.period, self.company)
            
            # Step 1: Extract data
            print(f"Extracting data for {self.company} - {self.period}...")
            erp_data = await data_agent.extract_data()
            
            # Step 2: Validate
            print("Running validations...")
            validation_results = await validation_agent.validate(erp_data)
            
            # Step 3: Generate report
            print("Generating report...")
            report_path = await reporting_agent.generate_report(erp_data, validation_results)
            
            # Check for blockers
            blockers = [r for r in validation_results if r.get("severity") == "BLOCK"]
            
            return {
                "period": self.period,
                "company": self.company,
                "status": "READY" if not blockers else "BLOCKED",
                "blockers": len(blockers),
                "total_checks": len(validation_results),
                "report_path": report_path,
                "validation_results": validation_results
            }
            
        except Exception as e:
            return {
                "period": self.period,
                "company": self.company,
                "status": "ERROR",
                "error": str(e)
            }
