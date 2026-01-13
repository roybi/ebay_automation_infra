# Test Suite Documentation

This directory contains unit tests and end-to-end (E2E) tests for the eBay automation framework.

## Test Structure

```
tests/
├── unit/                              # Unit tests for individual functions
│   ├── test_search_items_by_name_under_price.py
│   ├── test_add_items_to_cart.py
│   └── test_assert_cart_total_not_exceeds.py
├── e2e/                               # End-to-end integration tests
│   └── test_ebay_shopping_flow.py
└── README.md                          # This file
```

## Required Functions - Test Coverage

### 1. `searchItemsByNameUnderPrice` (SearchResultsPage)
**Unit Tests:** `test_search_items_by_name_under_price.py`
- ✓ Price parsing (valid/invalid)
- ✓ Single page results
- ✓ Price filtering
- ✓ Pagination handling
- ✓ Limit enforcement
- ✓ Price filter application
- ✓ Exception handling

### 2. `addItemsToCart` (ProductPage)
**Unit Tests:** `test_add_items_to_cart.py`
- ✓ Single item success/failure
- ✓ Multiple items (all success, partial, all fail)
- ✓ Variant selection (size, color, both, none)
- ✓ Product info extraction
- ✓ Cart verification
- ✓ Exception handling

### 3. `assertCartTotalNotExceeds` (CartPage)
**Unit Tests:** `test_assert_cart_total_not_exceeds.py`
- ✓ Within budget validation
- ✓ Exceeds budget validation
- ✓ Exact budget match
- ✓ Empty cart handling
- ✓ Cart total retrieval
- ✓ Item count extraction
- ✓ Screenshot capture

## Running Tests

### Run All Tests

```bash
# Run all tests (unit + E2E)
pytest tests/

# With verbose output
pytest tests/ -v

# With Allure report
pytest tests/ --alluredir=reports/allure-results
```

### Run Unit Tests Only

```bash
# All unit tests
pytest tests/unit/

# Specific function tests
pytest tests/unit/test_search_items_by_name_under_price.py
pytest tests/unit/test_add_items_to_cart.py
pytest tests/unit/test_assert_cart_total_not_exceeds.py
```

### Run E2E Tests Only

```bash
# All E2E tests
pytest tests/e2e/

# Specific test scenario
pytest tests/e2e/test_ebay_shopping_flow.py::TestEbayShoppingFlow::test_complete_shopping_flow_shoes
```

### Run with Markers

```bash
# Run smoke tests only (quick validation)
pytest -m smoke

# Run E2E tests only
pytest -m e2e

# Run slow tests
pytest -m slow
```

### Parallel Execution

```bash
# Run tests in parallel (4 workers)
pytest tests/ -n 4

# With specific browser
pytest tests/ --browser=chromium

# Multiple browsers (requires pytest-xdist)
pytest tests/ -n 3 --browser=chromium --browser=firefox --browser=webkit
```

## E2E Test Scenarios

### Main Scenario (as per NessHomeTest.docx)

**Test:** `test_complete_shopping_flow_shoes`

**Steps:**
1. **Identification**: Navigate to eBay homepage and verify it's loaded
2. **Search**: `searchItemsByNameUnderPrice("shoes", 220, 5)` → Get up to 5 URLs
3. **Add to Cart**: `addItemsToCart(urls)` → Add all items to cart
4. **Validate**: `assertCartTotalNotExceeds(220, urls.length)` → Verify total ≤ $220 × items

**Expected Result:** All steps pass, cart total does not exceed budget

### Additional Scenarios

- **test_complete_shopping_flow_laptops**: Different product category
- **test_using_standalone_functions**: Using functions without POM
- **test_smoke_single_item**: Quick smoke test with single item
- **test_no_items_found_under_price**: Error handling for empty results
- **test_partial_add_to_cart_success**: Handling partial failures
- **Parameterized tests**: Multiple product/price combinations

## Test Configuration

### Browser Options

```bash
# Run with headed browser (visible)
pytest tests/e2e/ --headed

# Run with slow motion (debugging)
pytest tests/e2e/ --slow-mo=1000

# Specific browser
pytest tests/e2e/ --browser=firefox
```

### Reporting

#### HTML Reports

```bash
# Generate HTML report
pytest tests/ --html=reports/report.html --self-contained-html
```

#### Allure Reports

**Step 1: Run tests with Allure reporting**

```bash
# Generate Allure results
pytest tests/ --alluredir=allure-results -v

# Or run specific tests with Allure
pytest tests/e2e/test_ebay_shopping_flow.py --alluredir=allure-results -v

# Clean previous results before generating new ones
pytest tests/ --alluredir=allure-results --clean-alluredir -v
```

**Note:** Allure results are automatically saved to timestamped directories in `reports/allure-results_YYYYMMDD_HHMMSS/`.

**Step 2: View the Allure report**

**Option 1: Serve with Allure server (Recommended)**

```bash
# Start Allure server - opens automatically in browser
allure serve reports/allure-results_YYYYMMDD_HHMMSS

# Or serve the most recent results
allure serve allure-results

# Server starts on http://127.0.0.1:<random-port>
# Press Ctrl+C to stop the server
```

**Option 2: Generate static HTML report**

```bash
# Generate static HTML report
allure generate reports/allure-results_YYYYMMDD_HHMMSS -o reports/allure-report --clean

# Note: Opening index.html directly may cause CORS issues in browsers
# Use Option 1 (allure serve) instead for best results
```

**Allure Report Features:**
- Interactive dashboard with test statistics
- Test suites organized by @allure.epic, @allure.feature, @allure.story
- Detailed step-by-step execution trace
- Screenshots and attachments
- Timeline view of test execution
- Graphs and trends over time

## Test Data

Test data is loaded from `data/test_data.json`:

```json
{
  "test_data": [
    {
      "search_query": "shoes",
      "max_price": 220,
      "limit": 5
    }
  ]
}
```

## Writing New Tests

### Unit Test Example

```python
import pytest
from unittest.mock import Mock
from pages.your_page import YourPage

class TestYourFunction:
    @pytest.fixture
    def mock_page(self):
        return Mock()

    def test_your_function(self, mock_page):
        # Arrange
        page = YourPage(mock_page)

        # Act
        result = page.your_function()

        # Assert
        assert result is True
```

### E2E Test Example

```python
import pytest
import allure
from pages import HomePage

@pytest.mark.e2e
@allure.feature("Your Feature")
def test_your_scenario(page):
    home_page = HomePage(page)
    home_page.navigate()

    # Your test steps
    assert home_page.identification()
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Run tests with coverage
pytest tests/ --cov=pages --cov=core --cov-report=html

# Run only smoke tests (fast)
pytest -m smoke --headless

# Generate JUnit XML for CI
pytest tests/ --junitxml=reports/junit.xml
```

## Troubleshooting

### Tests Fail to Import

```bash
# Ensure you're in the project root
cd C:\_Dev\python\ebay_automation_infra

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### Tests Timeout

Increase timeout in `pytest.ini`:

```ini
[pytest]
timeout = 600  # 10 minutes
```

### Parallel Execution Issues

Ensure session isolation is working:

```bash
# Run sequentially for debugging
pytest tests/ -n 0
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Use fixtures for setup/teardown
3. **Assertions**: One logical assertion per test
4. **Naming**: Descriptive test names (test_should_do_something_when_condition)
5. **Documentation**: Add docstrings explaining test purpose
6. **Screenshots**: Automatic on failure (configured in conftest.py)

## Coverage Report

Run tests with coverage:

```bash
pytest tests/ --cov=pages --cov=core --cov-report=html
# Open htmlcov/index.html to view coverage
```

## Support

For issues or questions:
- Check logs in `reports/logs/pytest.log`
- Review screenshots in `reports/screenshots/`
- Check Allure report for detailed execution trace
