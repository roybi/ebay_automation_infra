# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an eBay automation testing framework using Playwright with a Page Object Model (POM) architecture. The framework's core innovation is the **Smart Locator System** that provides automatic fallback to multiple locator strategies, making tests resilient to UI changes.

## Essential Commands

### Setup & Installation

```bash
# Install dependencies and package in development mode
pip install -r requirements.txt
pip install -e .
playwright install

# Install Allure reporting (optional)
npm install -g allure-commandline
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test types
pytest tests/unit/ -v                    # Unit tests only
pytest tests/e2e/ -v                     # E2E tests only
pytest -m smoke -v                       # Smoke tests only
pytest -m e2e -v                         # E2E marker only

# Run specific test
pytest tests/e2e/test_ebay_shopping_flow.py::TestEbayShoppingFlow::test_complete_shopping_flow_shoes -v

# Run with visible browser (for debugging)
pytest tests/e2e/ --headed -v

# Run on specific browser
pytest tests/e2e/ --browser firefox -v
pytest tests/e2e/ --browser webkit -v

# Run with Allure reporting
pytest tests/ --alluredir=allure-results -v
allure serve allure-results              # View report in browser
```

### Parallel Execution

```bash
# Run tests in parallel (4 workers)
pytest tests/ -n 4 -v

# Run on multiple browsers in parallel
pytest tests/e2e/ -n 3 --browser=chromium --browser=firefox --browser=webkit
```

## Architecture Overview

### Core Framework Components

**Smart Locator System** (`core/smart_locator.py`)
- **Purpose**: Enables automatic fallback between multiple locator strategies
- **Key Pattern**: Each UI element has 3-5 fallback locators (xpath, css, role, text)
- **Resolution**: `SmartLocatorResolver` tries each strategy sequentially until one succeeds
- **Resilience**: Captures screenshots on failure, logs all attempts with timestamps

**Browser Factory** (`core/browser_factory.py`)
- **Purpose**: Creates and manages isolated browser sessions
- **Session Management**: Each test gets a fresh `BrowserSession` (browser + context + page)
- **Multi-Browser**: Supports chromium, firefox, webkit, chrome (stable/beta/dev), edge
- **Logging**: Automatically captures console messages and network activity per session

**Wait Handler** (`core/wait_handler.py`)
- **Purpose**: Smart waiting strategies based on action type
- **Pattern**: `wait_for_element(locator, condition=WaitCondition.VISIBLE)`
- **Smart Wait**: Automatically waits for CLICKABLE before click, EDITABLE before fill
- **Polling**: Configurable polling with custom conditions

**Retry Handler** (`core/retry_handler.py`)
- **Purpose**: Exponential backoff retry mechanism
- **Usage**: Decorator `@retry(max_retries=3)` or context manager
- **Tracking**: Detailed `RetryResult` with attempts, timing, and error history

### Page Object Pattern

**BasePage** (`core/base_page.py`)
- Abstract base class for all page objects
- Integrates SmartLocator, WaitHandler, RetryHandler
- Provides common methods: `click()`, `fill()`, `find_element()`, `capture_screenshot()`

**Page Objects** (`pages/`)
- `HomePage`: Homepage navigation, search, identification
- `SearchResultsPage`: Search results, price filtering, pagination
- `ProductPage`: Product details, add to cart
- `CartPage`: Cart operations, total validation

**Locator Definition Pattern**:
```python
def _define_locators(self):
    self.SEARCH_INPUT = SmartLocator(name="Search Input")
    self.SEARCH_INPUT.add_xpath("//input[@id='gh-ac']", "ID-based")
    self.SEARCH_INPUT.add_xpath("//input[@placeholder='Search for anything']", "Placeholder")
    self.SEARCH_INPUT.add_css("input[type='text'][name='_nkw']", "Name attribute")
```

### Test Organization

**Fixtures** (`conftest.py`)
- `browser_factory` (session-scoped): Single factory for all tests
- `browser_session` (function-scoped): Fresh session per test with auto-cleanup
- `page`, `context`, `browser`: Derived from browser_session
- `screenshot_on_failure` (autouse): Automatic screenshot capture on test failure

**Test Structure**:
```
tests/
  ├── unit/          # Unit tests for individual functions
  └── e2e/           # End-to-end workflow tests
```

**Allure Integration**: All tests use `@allure.epic`, `@allure.feature`, `@allure.story`, `@allure.step` for rich reporting

### Configuration

**Settings Singleton** (`config/settings.py`)
- `BrowserConfig`: Browser launch options, timeouts, viewport
- `WaitConfig`: Timeout values, polling intervals
- `RetryConfig`: Retry counts, backoff multiplier
- `LocatorConfig`: Max locator retries, screenshot on failure
- `ReportConfig`: Allure and HTML report paths
- Access via: `from config.settings import settings`

**Pytest Configuration** (`pytest.ini`)
- Custom markers: `smoke`, `regression`, `e2e`, `slow`, `browser(name)`
- Allure results automatically saved to timestamped directories: `reports/allure-results_YYYYMMDD_HHMMSS/`
- Console and file logging configured

## Key Architectural Patterns

### 1. Smart Locator Resolution Flow
```
find_element(SmartLocator with 4 strategies)
  └─ SmartLocatorResolver.resolve()
      ├─ ATTEMPT 1: xpath "//button[text()='Search']" → Timeout
      ├─ ATTEMPT 2: xpath "//button[@aria-label='Search']" → Timeout
      └─ ATTEMPT 3: css "button[type='submit']" → SUCCESS!
          └─ Return playwright_locator
```

### 2. Test Execution Flow
```
pytest_configure() → browser_factory (session) → browser_session (per test)
  → Create page objects → Execute test steps → Auto screenshot on failure
  → Cleanup session (close page/context/browser)
```

### 3. Session Isolation
Each test receives a completely isolated browser session:
- Fresh browser instance
- New browser context (cookies, storage isolated)
- Clean page object
- Automatic cleanup after test

### 4. Error Handling Layers
1. **Smart Locator**: Multiple strategies with automatic fallback
2. **Wait Handler**: Polling with configurable timeouts
3. **Retry Handler**: Exponential backoff for transient failures
4. **Try/Except**: Graceful degradation in page methods

## Important Implementation Details

### Adding New Page Objects
1. Inherit from `BasePage`
2. Override `_define_locators()` to define all SmartLocators
3. Add 3-5 fallback strategies per locator
4. Use `self.click()`, `self.fill()` from BasePage (includes smart waiting)

### Smart Locator Best Practices
- **Priority order**: ID-based → stable attributes → text → generic selectors
- **Add descriptions**: Each locator should have a description for logs
- **3-5 strategies**: Balance between resilience and resolution time
- **Test fallback**: Intentionally break first locator to test fallback works

### Writing Tests
- Use `@pytest.mark.e2e` for E2E tests, `@pytest.mark.smoke` for smoke tests
- Add Allure decorators: `@allure.epic`, `@allure.feature`, `@allure.story`
- Use `with allure.step("Step description"):` for detailed reporting
- Tests receive `page` fixture (Playwright Page object)
- Create page objects: `home_page = HomePage(page)`

### Debugging Failed Tests
1. Check screenshot in `reports/screenshots/`
2. Review logs:
   - `logs/playwright_*.log` - Playwright API calls
   - `logs/browser_console_*.log` - Browser console messages
   - `logs/browser_network_*.log` - Network requests/responses
3. Run with visible browser: `pytest --headed`
4. Check Allure report for step-by-step execution trace

### Common Test Scenarios

**Three Core Functions** (as per requirements):
1. `searchItemsByNameUnderPrice(query, max_price, limit)` - SearchResultsPage
2. `addItemsToCart(page, urls)` - Standalone function in pages/__init__.py
3. `assertCartTotalNotExceeds(budget_per_item, items_count)` - CartPage

**E2E Flow**:
```python
home_page.navigate() → home_page.search("shoes")
  → search_page.search_items_by_name_under_price("shoes", 220, 5)
  → add_items_to_cart(page, urls)
  → cart_page.assert_cart_total_not_exceeds(220, 5)
```

## File Locations Reference

**Core Framework**:
- `core/base_page.py` - BasePage abstract class
- `core/smart_locator.py` - Smart locator system
- `core/browser_factory.py` - Browser session management
- `core/wait_handler.py` - Wait strategies
- `core/retry_handler.py` - Retry with exponential backoff

**Page Objects**:
- `pages/home_page.py` - eBay homepage
- `pages/search_results_page.py` - Search results and filtering
- `pages/product_page.py` - Product details
- `pages/cart_page.py` - Shopping cart

**Configuration**:
- `config/settings.py` - All framework settings (singleton)
- `conftest.py` - Pytest fixtures and configuration
- `pytest.ini` - Pytest configuration and markers

**Tests**:
- `tests/unit/` - Unit tests for individual functions
- `tests/e2e/test_ebay_shopping_flow.py` - Main E2E test scenarios

**Utilities**:
- `utils/logger.py` - Logging configuration
- `utils/screenshot.py` - Screenshot capture utilities
- `utils/data_loader.py` - JSON test data loading
- `utils/allure_helper.py` - Allure reporting helpers

## Critical Development Notes

### When Modifying Core Framework
- **Never break BasePage API** - all page objects depend on it
- **Smart locators must maintain chainable API** - `.add_xpath().add_css()`
- **Session isolation is critical** - tests must not share state
- **Screenshots on failure are automatic** - don't duplicate in tests

### When Adding Browser Support
- Add to `BROWSER_MATRIX` in `config/settings.py`
- Test with: `pytest --browser new-browser-name`
- Ensure proper cleanup in `BrowserFactory.close_session()`

### Allure Reporting
- Results saved to timestamped directories automatically
- Use `allure serve` not `allure generate` (avoids CORS issues)
- Helper scripts: `generate_allure_report.py`, `open_allure_report.py`
- On Windows with spaces in path, use: `"C:\Users\ROYBIC~1\AppData\Roaming\npm\node_modules\allure-commandline\dist\bin\allure.bat" serve reports/allure-results_*`

### Git Configuration
- Line endings: `git config core.autocrlf true` (Windows)
- Never commit `nul` file (Windows reserved name)
- `.gitignore` excludes all `.md` except `README.md` files

## Test Data

Test data location: `data/test_data.json`
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

Load in tests via fixture:
```python
@pytest.fixture
def test_data(self):
    data_loader = DataLoader()
    data = data_loader.load_json("test_data.json")
    return data["test_data"][0]
```
