# TESTING_QUICKSTART.md

# Pokemon ETL Testing - Quick Start Guide

## Installation

1. **Install test dependencies:**

```bash
pip install -r requirements-test.txt
```

## Running Tests

### Option 1: Using pytest directly

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=data_processing --cov=routers --cov-report=term-missing

# Run specific test file
pytest tests/test_extract.py
pytest tests/test_transform.py
pytest tests/test_load.py
pytest tests/test_etl.py
pytest tests/test_routers.py

# Run verbose
pytest -v

# Run and show print statements
pytest -s
```

### Option 2: Using the test runner script

```bash
# Make the script executable (Unix/Linux/Mac)
chmod +x run_tests.py

# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run with coverage and HTML report
python run_tests.py --coverage --html

# Run specific test file
python run_tests.py --test test_extract.py

# Run verbose
python run_tests.py -v

# Run specific test method
python run_tests.py --method test_successful_extraction

# Stop on first failure
python run_tests.py -x
```

## Test Structure

### 1. **test_extract.py** - Extract Module Tests

Tests for Pokemon data extraction from PokeAPI:

- Valid/invalid Pokemon IDs
- API response handling
- Network error handling
- Evolution chain parsing

**Run:**

```bash
pytest tests/test_extract.py -v
```

### 2. **test_transform.py** - Transform Module Tests

Tests for data transformation logic:

- Data structure validation
- Type conversions
- Missing fields handling
- Stats processing

**Run:**

```bash
pytest tests/test_transform.py -v
```

### 3. **test_load.py** - Load Module Tests

Tests for database operations:

- Database connection
- Table creation
- Data insertion
- Foreign key constraints
- Transaction management

**Run:**

```bash
pytest tests/test_load.py -v
```

### 4. **test_etl.py** - ETL Pipeline Tests

Tests for the complete ETL workflow:

- End-to-end pipeline
- Error handling
- Partial success scenarios
- API rate limiting

**Run:**

```bash
pytest tests/test_etl.py -v
```

### 5. **test_routers.py** - API Endpoint Tests

Tests for FastAPI routes:

- GET /pokemon/ - List Pokemon
- GET /pokemon/filter_pokemons - Filter Pokemon
- POST /pokemon/etl/run-pipeline - Run ETL
- GET /pokemon/analysis - Get analysis data

**Run:**

```bash
pytest tests/test_routers.py -v
```

## Viewing Coverage Reports

### Terminal Report:

```bash
pytest --cov=data_processing --cov=routers --cov-report=term-missing
```

### HTML Report:

```bash
pytest --cov=data_processing --cov=routers --cov-report=html
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Common Test Commands

```bash
# Quick test - just check if everything passes
pytest

# Full test with coverage
pytest --cov --cov-report=term-missing

# Test specific functionality
pytest tests/test_extract.py::TestExtractPokemons::test_successful_extraction

# Test with print output visible
pytest -s tests/test_etl.py

# Test and stop on first failure
pytest -x

# Test with detailed output
pytest -vv

# Test and show slowest tests
pytest --durations=10
```

## Verifying Your Setup

Run this command to verify everything is working:

```bash
pytest tests/ -v --tb=short
```

You should see output like:

```
tests/test_extract.py::TestExtractPokemons::test_invalid_pokemon_id_zero PASSED
tests/test_extract.py::TestExtractPokemons::test_successful_extraction PASSED
tests/test_transform.py::TestTransformPokemons::test_none_input PASSED
...
======================== XX passed in X.XXs =========================
```

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError` when running tests

**Solution:** Make sure you're in the project root directory:

```bash
cd /path/to/your/project
pytest
```

### Database Errors

**Problem:** Database locked or connection errors

**Solution:** Tests use temporary databases. Make sure no other processes are using test databases:

```bash
# Clean up any test databases
rm -f tests/*.db
pytest
```

### Mock Errors

**Problem:** Mocks not working as expected

**Solution:** Verify you're patching the right location:

```python
# Patch where it's USED, not where it's DEFINED
@patch('data_processing.etl.extract_pokemons')  # Correct
@patch('data_processing.extract.extract_pokemons')  # Wrong
```

## Integration with CI/CD

These tests are designed to work with CI/CD pipelines. Example configurations:

### GitHub Actions

```yaml
- name: Run tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov --cov-report=xml
```

### GitLab CI

```yaml
test:
  script:
    - pip install -r requirements-test.txt
    - pytest --cov --cov-report=term
```

## Next Steps

1. Run all tests to verify setup: `pytest -v`
2. Check coverage: `pytest --cov --cov-report=term-missing`
3. Review test output and fix any failures
4. Add tests for any new features you develop
5. Maintain >80% code coverage

## Need Help?

- Check `tests/README.md` for detailed documentation
- Review individual test files for examples
- Check pytest documentation: https://docs.pytest.org/

Happy Testing! 