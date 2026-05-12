"""
Reporting Agent — Generates Excel reports from validation results.
Creates formatted workbooks for close review and sign-off.
"""

import os
import json
import asyncio
from typing import Dict, List, Any
from plugins.excel_plugin import ExcelPlugin


class ReportingAgent:
    """
    Generates Excel close reports from validation data.
    """

    def __init__(self, period: str, company: str):
        self.period = period
        self.company = company
        self.excel_plugin = ExcelPlugin()
        self.output_dir = os.getenv("OUTPUT_DIR", "reports")

    async def generate_report(self, erp_data: Dict[str, Any], validation_results: List[Dict[str, str]]) -> str:
        """
        Generate Excel close report.
        
        Args:
            erp_data: Extracted ERP data
            validation_results: Validation check results
            
        Returns:
            Path to generated Excel file
        """
        try:
            # Convert validation results to JSON string for the plugin
            validation_json = json.dumps(validation_results)
            
            # Generate the workbook
            report_path = await asyncio.get_event_loop().run_in_executor(
                None,
                self.excel_plugin.generate_close_workbook,
                self.period,
                self.company,
                validation_json,
                self.output_dir
            )
            
            return report_path
            
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            return ""
