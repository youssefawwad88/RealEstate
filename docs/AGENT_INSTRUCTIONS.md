# Agent Instructions for TerraFlow Development

## Overview
This document provides guidelines for GitHub Copilot agents working on the TerraFlow real estate development system. Follow these rules to maintain code quality, consistency, and project architecture integrity.

## Core Principles

### 1. Architecture Adherence
- **Keep core business logic in `/modules`** - All calculation engines, data models, and domain logic
- **Utility functions in `/utils`** - Helper functions, I/O operations, formatting, scoring
- **Notebooks for orchestration only** - Thin interface layers, no complex business logic
- **Dashboard for presentation** - UI components, visualization, user interaction only

### 2. Code Standards
- **Python 3.11** - Target version for all code
- **Type hints required** - All functions must have proper type annotations
- **Docstrings mandatory** - Google-style docstrings for all public functions
- **PEP8 compliance** - Use black formatter and flake8 linter
- **Unit tests** - All new functionality requires corresponding tests

### 3. Data Handling Rules
- **Raw data in `/data/raw/`** - Never commit raw data files (gitignored)
- **Processed data in `/data/processed/`** - Track cleaned, validated data only
- **CSV format preferred** - Use pandas-compatible CSV for data persistence
- **Schema validation** - Use Pydantic models for data validation

## Development Workflow

### Branch Strategy
- `main` - Production-ready code only
- `develop` - Integration branch for features
- `feat/*` - Feature development branches
- `fix/*` - Bug fix branches
- `docs/*` - Documentation updates

### Commit Standards
- Use conventional commits format
- Keep commits atomic and focused
- Reference issues when applicable
- Include tests in the same commit as features

### Pull Request Requirements
- All CI checks must pass (pytest, flake8, black)
- Code coverage must be maintained
- Manual testing documented
- Breaking changes clearly identified

## Module-Specific Guidelines

### Land Acquisition Module (`modules/land_acquisition.py`)
- Focus on input collection and validation
- No financial calculations (those go in deal_model.py)
- Maintain backward compatibility for data formats
- Handle edge cases gracefully

### Deal Model Module (`modules/deal_model.py`)
- Use Pydantic for data models
- Implement all residual value calculations
- Include sensitivity analysis
- Comprehensive error handling

### Market Lookup Module (`modules/market_lookup.py`)
- Abstract data source implementations
- Cache market data appropriately
- Handle API failures gracefully
- Support multiple markets/cities

### Utils Modules
- **`utils/io.py`** - File operations, data loading/saving
- **`utils/scoring.py`** - Deal scoring, color coding, formatting
- Keep functions pure and testable
- No side effects in utility functions

### Dashboard (`dashboard/streamlit_app.py`)
- Mobile-responsive design
- Error handling for data issues
- Performance optimization for large datasets
- Clear user feedback for all actions

## Testing Requirements

### Unit Tests
- Test files in `/tests/` directory
- Mirror the module structure (`test_land_acquisition.py`, `test_deal_model.py`)
- Use pytest framework
- Mock external dependencies
- Test both happy path and edge cases

### Integration Tests
- Test end-to-end workflows
- Validate data flow between modules
- Test dashboard functionality
- Performance benchmarks for key operations

### Test Data
- Use fixtures for test data
- Create realistic but anonymized test cases
- Include edge cases and boundary conditions
- Test both typical and stress scenarios

## Performance Guidelines

### Memory Management
- Use pandas efficiently for large datasets
- Implement lazy loading where appropriate
- Clean up temporary files
- Monitor memory usage in notebooks

### Computational Efficiency
- Vectorize operations using numpy/pandas
- Cache expensive calculations
- Use appropriate data types
- Profile performance-critical code

## Security Considerations

### Data Privacy
- No real customer data in code/tests
- Anonymize all example data
- Secure handling of sensitive calculations
- No hardcoded credentials or secrets

### Input Validation
- Validate all user inputs
- Sanitize file uploads
- Handle malformed data gracefully
- Prevent injection attacks

## Error Handling

### Exception Strategy
- Use specific exception types
- Provide meaningful error messages
- Log errors appropriately
- Graceful degradation in UI

### User Experience
- Clear error messages in dashboard
- Validation feedback in real-time
- Recovery suggestions for errors
- Progress indicators for long operations

## Documentation Standards

### Code Documentation
- Module-level docstrings explaining purpose
- Function docstrings with Args/Returns/Raises
- Inline comments for complex logic
- Type hints for all parameters and returns

### User Documentation
- Keep README.md updated
- Document API changes
- Provide usage examples
- Maintain changelog for releases

### Technical Documentation
- Architecture diagrams when helpful
- Database schemas if applicable
- API documentation for integrations
- Deployment instructions

## Agent-Specific Rules

### When Making Changes
1. **Understand context first** - Read related code before modifying
2. **Minimal changes** - Make the smallest change that accomplishes the goal
3. **Test thoroughly** - Run tests and manual verification
4. **Document impact** - Note any breaking changes or dependencies

### Code Review Focus
- Architecture compliance
- Performance implications
- Security considerations
- User experience impact
- Backward compatibility

### Common Pitfalls to Avoid
- Don't put business logic in the dashboard
- Don't commit raw data files
- Don't skip type hints or docstrings
- Don't ignore failing tests
- Don't make breaking changes without clear communication

## Questions and Support
When uncertain about implementation details:
1. Check existing code patterns in the module
2. Refer to this document
3. Look for similar functionality in other modules
4. Ask for clarification in PR comments

Remember: The goal is to build a maintainable, professional-grade system that real estate developers can rely on for critical business decisions.