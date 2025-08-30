# Contributing to TerraFlow

Thank you for your interest in contributing to TerraFlow! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites
- Python 3.11 or higher
- Git
- Basic understanding of real estate development concepts (helpful but not required)

### Development Setup
1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/youssefawwad88/RealEstate.git
   cd RealEstate
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install development dependencies**
   ```bash
   pip install -r dev-requirements.txt
   pip install pre-commit
   ```

5. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pre-commit install
   ```

### Running the Application

#### Streamlit Dashboard
```bash
streamlit run dashboard/streamlit_app.py
```

#### Jupyter Notebooks
```bash
jupyter notebook notebooks/
```

#### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=modules --cov=utils

# Run specific test file
pytest tests/test_land_acquisition.py
```

#### Code Quality Checks
```bash
# Format code
black .

# Lint code
flake8 .

# Lint notebooks
nbqa black notebooks/
nbqa flake8 notebooks/
```

## Project Structure

```
TerraFlow/
├── modules/           # Core business logic
│   ├── land_acquisition.py
│   ├── deal_model.py
│   └── market_lookup.py
├── utils/            # Helper functions
│   ├── io.py
│   └── scoring.py
├── dashboard/        # Streamlit UI
│   └── streamlit_app.py
├── notebooks/        # Jupyter notebooks for data entry
│   └── 01_land_acquisition.ipynb
├── tests/           # Unit and integration tests
├── data/
│   ├── raw/         # Raw data (not tracked)
│   └── processed/   # Cleaned data (tracked)
├── docs/            # Documentation
└── .github/         # GitHub workflows and templates
```

## Development Workflow

### Branching Strategy
- `main` - Stable, production-ready code
- `develop` - Integration branch (if used)
- `feat/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/documentation-update` - Documentation changes

### Making Changes
1. **Create a feature branch**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards below
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   pytest
   black --check .
   flake8 .
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add residual value calculation"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feat/your-feature-name
   ```

## Coding Standards

### Python Code Style
- **PEP 8 compliance** - Use `black` formatter and `flake8` linter
- **Type hints required** - All function parameters and return types
- **Docstrings mandatory** - Google-style docstrings
- **Line length** - Maximum 127 characters (GitHub friendly)

### Example Function
```python
def calculate_residual_land_value(
    gdv: float,
    construction_cost: float,
    profit_margin: float
) -> float:
    """
    Calculate residual land value for development project.
    
    Args:
        gdv: Gross Development Value in dollars
        construction_cost: Total construction cost in dollars
        profit_margin: Developer profit margin as decimal (e.g., 0.20 for 20%)
        
    Returns:
        Residual land value in dollars
        
    Raises:
        ValueError: If any input is negative
    """
    if gdv <= 0 or construction_cost <= 0:
        raise ValueError("GDV and construction cost must be positive")
    
    profit = gdv * profit_margin
    return gdv - construction_cost - profit
```

### Module Organization
- **Core logic in `/modules`** - Business calculations and data models
- **Helpers in `/utils`** - Reusable utility functions
- **UI in `/dashboard`** - Streamlit interface components
- **Data processing in notebooks** - Data entry and orchestration only

### Testing Requirements
- **Unit tests** - Test individual functions in isolation
- **Integration tests** - Test module interactions
- **Test coverage** - Aim for >80% coverage on new code
- **Test data** - Use fixtures and mock data, never real customer data

## Types of Contributions

### Bug Fixes
- Check existing issues first
- Create a clear bug report if none exists
- Include steps to reproduce
- Add regression tests

### New Features
- Discuss major features in an issue first
- Follow the existing architecture patterns
- Add comprehensive tests
- Update documentation

### Documentation
- Fix typos and improve clarity
- Add examples and usage guides
- Update API documentation
- Improve README and setup instructions

### Data and Market Research
- Add new market data sources
- Improve calculation accuracy
- Add new geographic regions
- Validate existing formulas

## Pull Request Process

### Before Submitting
1. **Check CI passes locally**
   ```bash
   pytest
   black --check .
   flake8 .
   ```

2. **Update relevant documentation**
3. **Add or update tests**
4. **Test the dashboard manually**

### PR Description
- Use the provided PR template
- Describe the problem and solution
- List breaking changes clearly
- Include screenshots for UI changes

### Review Process
- All PRs require at least one review
- Address all reviewer feedback
- Ensure CI passes completely
- Squash commits if requested

## Issue Reporting

### Bug Reports
Include:
- Python version and OS
- Steps to reproduce
- Expected vs actual behavior
- Error messages and stack traces
- Sample data (anonymized)

### Feature Requests
Include:
- Use case description
- Proposed implementation approach
- Any related real estate industry standards
- Examples from other tools

### Questions
- Check existing documentation first
- Search existing issues
- Provide context about your use case

## Code of Conduct

### Our Standards
- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn
- Acknowledge contributions

### Unacceptable Behavior
- Harassment or discrimination
- Spam or off-topic discussions
- Sharing proprietary real estate data
- Personal attacks

## Real Estate Industry Context

### Key Concepts
- **GDV (Gross Development Value)** - Total revenue from sales
- **Residual Land Value** - Maximum affordable land cost
- **FAR (Floor Area Ratio)** - Building area vs land area
- **Soft Costs** - Professional fees, permits, financing

### Industry Standards
- Land typically 15-25% of GDV
- Construction costs vary by region and type
- Profit margins typically 15-25% for developers
- Market research critical for pricing assumptions

## Questions?

- Check the [documentation](docs/)
- Search [existing issues](https://github.com/youssefawwad88/RealEstate/issues)
- Create a new issue for questions
- Review the [Agent Instructions](docs/AGENT_INSTRUCTIONS.md) for development guidelines

Thank you for contributing to TerraFlow! 🏗️