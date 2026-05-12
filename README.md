# FinClose AI — Autonomous Finance Close Orchestrator

This project implements an AI-powered autonomous finance close system using Microsoft Agent Framework.
The system orchestrates data extraction, validation, and reporting for comprehensive financial close processes.

## Features

- **Multi-agent architecture** for specialized financial operations
- **D365 ERP integration** for data extraction
- **Excel-based reporting** with automated formatting
- **Comprehensive validation rules engine**
- **IFRS compliance mapping**
- **Real-time close checklist management**

## Architecture

- **Orchestrator Agent**: Coordinates the entire close process
- **Data Agent**: Extracts and processes financial data from D365
- **Validation Agent**: Applies business rules and compliance checks
- **Reporting Agent**: Generates formatted Excel reports

## Prerequisites

- Python 3.8+
- D365 environment access
- Azure AD authentication setup

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables in `.env`
4. Run the orchestrator: `python main.py`

## Usage

### Environment Variables

Create a `.env` file with the following variables:

```env
# D365 Configuration
D365_BASE_URL=https://your-tenant.sandbox.operations.dynamics.com
D365_CLIENT_ID=your-client-id
D365_CLIENT_SECRET=your-client-secret
D365_TENANT_ID=your-tenant-id
D365_COMPANY_ID=USMF

# Close Configuration
CLOSE_PERIOD=2026-04
COMPANY_ID=USMF

# Output Configuration
OUTPUT_DIR=reports
```

### Running the System

```bash
python main.py
```

## Modules

### Agents

- `agents/orchestrator_agent.py`: Main coordination logic
- `agents/data_agent.py`: D365 data extraction
- `agents/validation_agent.py`: Business rule validation
- `agents/reporting_agent.py`: Excel report generation

### Plugins

- `plugins/d365_plugin.py`: D365 OData API wrapper
- `plugins/excel_plugin.py`: Excel formatting utilities
- `plugins/validation_rules.py`: Validation rule definitions

### Configuration

- `config/close_checklist.yaml`: Close checklist configuration
- `config/ifrs_mappings.yaml`: IFRS account mappings

### Tests

Run tests with:

```bash
pytest tests/
```

## API Reference

### Data Agent

```python
from agents.data_agent import DataAgent

agent = DataAgent("2026-04", "USMF")
erp_data = await agent.extract_data()
```

### Validation Agent

```python
from agents.validation_agent import ValidationAgent

agent = ValidationAgent("2026-04", "USMF")
results = await agent.validate(erp_data)
```

### Reporting Agent

```python
from agents.reporting_agent import ReportingAgent

agent = ReportingAgent("2026-04", "USMF")
path = await agent.generate_report(erp_data, validation_results)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
