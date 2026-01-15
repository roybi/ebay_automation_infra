# eBay Automation Testing Framework

A comprehensive Python-based test automation framework for eBay using Playwright, implementing the Page Object Model (POM) design pattern with support for parallel execution and multi-browser testing.

## Features

- **Page Object Model (POM)**: Clean separation of test logic and page interactions
- **Smart Locator Strategy**: Multiple fallback locators for robust element identification
- **Multi-Browser Support**: Test across Chromium, Chrome (Stable/Beta/Dev), Firefox, WebKit, and Edge
- **Parallel Execution**: Run tests concurrently with session isolation
- **Comprehensive Logging**: Playwright API, browser console, and network activity logs
- **Comprehensive Reporting**: HTML reports, Allure reports, and screenshot capture on failures
- **Data-Driven Testing**: JSON-based test data management
- **Retry Mechanism**: Configurable retry logic with exponential backoff
- **Flexible Configuration**: Dataclass-based settings for easy customization

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Node.js and npm (required for Allure reporting)
- Chrome, Firefox, or other browsers (optional for specific browser testing)

## Installation

### 1. Clone the Repository

```bash
cd C:\_Dev\python\ebay_automation_infra
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Package in Development Mode

**This step is required to fix import paths:**

```bash
# Install the package in editable mode
pip install -e .
```

This command installs the package in development mode, which adds the project root to Python's path and allows proper imports of `config`, `pages`, `core`, and `utils` modules.

### 4. Install Playwright Browsers

```bash
# Install all browsers
playwright install

# Or install specific browsers
playwright install chromium
playwright install firefox
playwright install webkit
```

### 5. Install Allure Command-Line Tool (Optional)

For Allure reporting support:

```bash
# Install Allure globally using npm
npm install -g allure-commandline

# Verify installation
allure --version
```

**Note:** The `allure-pytest` Python package is already included in `requirements.txt` and will be installed in step 2.

## Quick Start

### Run All Tests

```bash
# Run all tests (unit + E2E)
pytest tests/ -v

# Run with HTML report
pytest tests/ -v --html=reports/test-report.html --self-contained-html

# Run with Allure reporting
pytest tests/ --alluredir=allure-results -v

# View Allure report
allure serve allure-results
```

### Run Unit Tests Only

```bash
# All unit tests
pytest tests/unit/ -v

# Specific function tests
pytest tests/unit/test_search_items_by_name_under_price.py -v
pytest tests/unit/test_add_items_to_cart.py -v
pytest tests/unit/test_assert_cart_total_not_exceeds.py -v
```

### Run E2E Tests

```bash
# Run E2E tests with visible browser
pytest tests/e2e/ --headed -v

# Run E2E tests in headless mode
pytest tests/e2e/ -v

# Run specific scenario
pytest tests/e2e/test_ebay_shopping_flow.py::TestEbayShoppingFlow::test_complete_shopping_flow_shoes -v
```

### Run Tests with Specific Browser

```bash
# Run on Chromium (default)
pytest tests/e2e/ --browser chromium -v

# Run on Firefox
pytest tests/e2e/ --browser firefox -v

# Run on WebKit (Safari engine)
pytest tests/e2e/ --browser webkit -v
```

## Chrome Version Testing

The framework supports testing on multiple Chrome versions:

| Browser     | Description                      | Channel     |
| ----------- | -------------------------------- | ----------- |
| chromium    | Playwright's bundled Chromium    | (default)   |
| chrome      | Chrome Stable (system-installed) | chrome      |
| chrome-beta | Chrome Beta channel              | chrome-beta |
| chrome-dev  | Chrome Dev channel               | chrome-dev  |
| msedge      | Microsoft Edge (Chromium-based)  | msedge      |

### Running Tests on Different Chrome Versions

**Option 1: Using Convenience Scripts**

Windows:

```bash
# Run E2E tests on Chrome Stable and Chrome Beta
run_multi_chrome_tests.bat

# Specify custom test path
run_multi_chrome_tests.bat tests/e2e/test_ebay_shopping_flow.py
```

**Option 2: Manual Execution**

````bash
# Run on Chrome Stable
pytest tests/e2e/ --browser chromium --browser-channel chrome --headed -v



**Option 3: Generate Separate Reports**

```bash
# Chrome Stable with HTML report
pytest tests/e2e/ --browser chromium --browser-channel chrome -v --html=reports/chrome-stable-report.html --self-contained-html


## Core Test Functions

The framework implements three main test functions as per requirements:

### 1. searchItemsByNameUnderPrice

**Location:** `pages/search_results_page.py`

**Purpose:** Search for items by name and filter by maximum price

# Returns: List of up to 5 product URLs under $220
````

**Features:**

- Price filtering and validation
- Pagination support (up to 5 pages)
- Smart item extraction using XPath
- Price parsing from item listings
- Automatic screenshot capture

### 2. addItemsToCart

**Location:** `pages/product_page.py`

**Purpose:** Add multiple items to shopping cart with variant selection

# Returns: Dict with success status and details for each item

**Features:**

- Bulk item processing
- Automatic variant selection (size, color)
- Cart verification after each addition
- Error handling for unavailable items
- Product info extraction (title, price)

### 3. assertCartTotalNotExceeds

**Location:** `pages/cart_page.py`

**Purpose:** Validate cart total does not exceed budget

# Raises AssertionError if total exceeds $220 × 5 = $1100

**Features:**

- Cart navigation and total extraction
- Budget validation with detailed reporting
- Empty cart detection
- Screenshot capture on assertion failure
- Item count verification

## Standalone Functions

The three core functions are also available as standalone functions (non-POM):

# Use without creating page objects

## Test Execution

### Run Tests with Markers

```bash
# Run smoke tests only
pytest -m smoke -v

# Run E2E tests only
pytest -m e2e -v

# Run regression tests
pytest -m regression -v
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest tests/ -n 4 -v

# Run E2E tests in parallel on multiple browsers
pytest tests/e2e/ -n 3 --browser=chromium --browser=firefox --browser=webkit
```

## Configuration

### Browser Configuration (config/settings.py)

Customize browser settings:

```python
@dataclass
class BrowserConfig:
    name: str                    # Browser name: chromium, firefox, webkit
    headless: bool = False       # Run in headless mode
    slow_mo: int = 0            # Slow down operations (ms)
    viewport_width: int = 1920  # Viewport width
    viewport_height: int = 1080 # Viewport height
    timeout: int = 30000        # Default timeout (ms)
    args: List[str]             # Browser launch arguments
    channel: Optional[str]      # Chrome channel (chrome, chrome-beta, etc.)
    executable_path: Optional[str] # Custom browser path
```

### Wait Configuration

```python
@dataclass
class WaitConfig:
    default_timeout: int = 30000      # Default wait timeout (ms)
    element_load_timeout: int = 15000 # Element load timeout (ms)
    page_load_timeout: int = 60000    # Page load timeout (ms)
    polling_interval: int = 500       # Polling interval (ms)
```

### Retry Configuration

```python
@dataclass
class RetryConfig:
    max_retries: int = 3              # Maximum retry attempts
    initial_delay: float = 1.0        # Initial delay (seconds)
    max_delay: float = 10.0           # Maximum delay (seconds)
    backoff_multiplier: float = 2.0   # Backoff multiplier
```

## Test Data

Test data is stored in `data/test_data.json`:

```json
{
  "test_data": [
    {
      "search_query": "shoes",
      "max_price": 220,
      "limit": 5
    },
    {
      "search_query": "laptop",
      "max_price": 800,
      "limit": 3
    }
  ]
}
```

## Reporting

### HTML Reports

```bash
# Generate HTML report
pytest tests/ --html=reports/report.html --self-contained-html

# View report
# Open reports/report.html in browser
```

### Allure Reports

The framework supports Allure reporting for rich, interactive test reports with detailed test execution history, graphs, and timelines.

#### Prerequisites

Install Allure command-line tool:

```bash
# Using npm (Node.js required)
npm install -g allure-commandline

# Verify installation
allure --version
```

#### Running Tests with Allure

```bash
# Run all tests and generate Allure results
pytest tests/ --alluredir=allure-results -v

# Run specific test class with Allure
pytest tests/e2e/test_ebay_shopping_flow.py::TestEbayShoppingFlow --alluredir=allure-results -v

# Run tests with specific feature
pytest tests/e2e/ -m e2e --alluredir=allure-results -v

# Clean previous results before generating new ones
pytest tests/ --alluredir=allure-results --clean-alluredir -v
```

**Note:** Allure results are automatically saved to timestamped directories in `reports/allure-results_YYYYMMDD_HHMMSS/` to preserve test history.

#### Generating and Viewing Allure Reports

**Option 1: Generate HTML Report (Static)**

```bash
# Generate static HTML report
allure generate reports/allure-results_YYYYMMDD_HHMMSS -o reports/allure-report --clean

# Note: Opening index.html directly may cause CORS issues in browsers
```

**Option 2: Serve Report with Built-in Server (Recommended)**

```bash
# Start Allure server and automatically open report in browser
allure serve reports/allure-results_YYYYMMDD_HHMMSS

# The server will start on http://127.0.0.1:<random-port>
# Report opens automatically in your default browser
# Press Ctrl+C to stop the server
```

#### Helper Scripts

The framework includes helper scripts for easy report generation:

**Python Script:**
```bash
# Generate static report (if allure command has path issues)
python generate_allure_report.py

# Open report in browser
python open_allure_report.py
```

#### Allure Report Features

The Allure report provides:

- **Overview Dashboard**: Test statistics, success rate, and duration
- **Suites**: Test organization by classes and packages
- **Graphs**: Visual charts for test results and trends
- **Timeline**: Chronological view of test execution
- **Behaviors**: Tests grouped by @allure.epic, @allure.feature, @allure.story
- **Packages**: Tests organized by Python package structure
- **Detailed Steps**: Step-by-step execution with @allure.step annotations
- **Attachments**: Screenshots, logs, and test data
- **History**: Test execution trends over time
- **Retries**: Track test retries and flaky tests

#### Allure Decorators in Tests

Tests use Allure decorators for rich reporting:

```python
@allure.epic("eBay E2E Tests")
@allure.feature("Shopping Flow")
@allure.story("Complete Shopping Flow - Shoes Example")
@allure.title("Search shoes under $220, add 5 items to cart, validate total")
def test_complete_shopping_flow_shoes(self, page):
    with allure.step("Step 1: Verify eBay homepage"):
        # Test implementation
        pass
```

### Screenshots

Screenshots are automatically captured on test failures:

- Location: `reports/screenshots/`
- Format: `{test_name}_{timestamp}.png`

### Logs

The framework generates comprehensive logs in the `logs/` directory:

- **playwright\_\*.log**: Playwright API activity and debugging
- **browser*console*\*.log**: Browser console messages (console.log, warnings, errors)
- **browser*network*\*.log**: Network requests and responses (all HTTP activity)
- **framework.log**: Framework-level logs
- **pytest logs**: Test execution logs in `reports/logs/pytest.log`

Each browser session creates separate log files with timestamps for easy tracking. Logs include:

- Console messages with file locations
- Page errors and exceptions
- Network requests (method, URL)
- Network responses (status code, URL)
- Failed requests

## Documentation & Interview Preparation

For comprehensive project documentation and interview preparation, see:

**[Project Guide & Interview Questions](docs/PROJECT_GUIDE_AND_INTERVIEW.md)**

This document includes:
- **How to Read This Project**: Step-by-step learning path through the codebase
- **Architecture Deep Dive**: Detailed diagrams and explanations
- **Key Concepts Explained**: POM, Smart Locator, Fixtures, Core Functions
- **Interview Questions - This Project**: 15+ questions about the framework
- **Interview Questions - Playwright**: 15+ questions about Playwright
- **Interview Questions - General Automation**: Best practices and design patterns

## Project Structure

```
ebay_automation_infra/
├── core/                    # Framework core components
│   ├── base_page.py         # Abstract base class for pages
│   ├── smart_locator.py     # Smart locator with fallback
│   ├── browser_factory.py   # Browser session management
│   ├── wait_handler.py      # Smart waiting strategies
│   └── retry_handler.py     # Retry with exponential backoff
├── pages/                   # Page Object classes
│   ├── home_page.py         # eBay homepage
│   ├── search_results_page.py
│   ├── product_page.py
│   └── cart_page.py
├── tests/                   # Test cases
│   ├── unit/                # Unit tests
│   └── e2e/                 # End-to-end tests
├── config/                  # Configuration
│   └── settings.py          # Framework settings
├── utils/                   # Utilities
├── data/                    # Test data files
├── docs/                    # Documentation
│   └── PROJECT_GUIDE_AND_INTERVIEW.md
├── conftest.py              # Pytest fixtures
└── requirements.txt         # Dependencies
```

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review screenshots in `reports/screenshots/`
- Check Allure report for detailed execution trace
- See `docs/PROJECT_GUIDE_AND_INTERVIEW.md` for troubleshooting
