# eBay Automation Framework - Project Guide & Interview Questions

## Table of Contents
1. [Project Overview](#project-overview)
2. [How to Read This Project](#how-to-read-this-project)
3. [Architecture Deep Dive](#architecture-deep-dive)
4. [Code Reading Order](#code-reading-order)
5. [Key Concepts Explained](#key-concepts-explained)
6. [Interview Questions - This Project](#interview-questions---this-project)
7. [Interview Questions - Playwright](#interview-questions---playwright)
8. [Interview Questions - General Automation](#interview-questions---general-automation)

---

## Project Overview

### What is This Project?
This is an **eBay automation testing framework** built with **Playwright** and **Python**, implementing the **Page Object Model (POM)** pattern. The framework's core innovation is the **Smart Locator System** - a resilient element location mechanism that automatically falls back to alternative locators when the primary one fails.

### Project Purpose
- Automate end-to-end testing of eBay shopping flows
- Demonstrate professional-grade test automation architecture
- Provide a scalable, maintainable test framework

### Key Features
| Feature | Description |
|---------|-------------|
| Smart Locator System | Automatic fallback between multiple locator strategies |
| Page Object Model | Clean separation of test logic and page interactions |
| Multi-Browser Support | Chromium, Firefox, WebKit, Chrome (stable/beta/dev), Edge |
| Session Isolation | Each test gets a completely isolated browser session |
| Allure Reporting | Rich test reports with screenshots and step details |
| Retry Mechanism | Exponential backoff for transient failures |
| Parallel Execution | Support for running tests in parallel |

---

## How to Read This Project

### Step 1: Understand the Folder Structure (5 minutes)

```
ebay_automation_infra/
│
├── core/                    # Framework Foundation (READ FIRST)
│   ├── smart_locator.py     # Smart locator with fallback mechanism
│   ├── base_page.py         # Abstract base class for all pages
│   ├── browser_factory.py   # Browser session management
│   ├── wait_handler.py      # Smart waiting strategies
│   └── retry_handler.py     # Retry with exponential backoff
│
├── pages/                   # Page Objects (READ SECOND)
│   ├── __init__.py          # Exports page objects + standalone functions
│   ├── home_page.py         # eBay homepage interactions
│   ├── search_results_page.py # Search results handling
│   ├── product_page.py      # Product detail page
│   └── cart_page.py         # Shopping cart page
│
├── tests/                   # Test Cases (READ THIRD)
│   ├── e2e/                 # End-to-end test scenarios
│   │   └── test_ebay_shopping_flow.py
│   └── unit/                # Unit tests for functions
│
├── config/                  # Configuration
│   └── settings.py          # All framework settings (singleton)
│
├── utils/                   # Utilities
│   ├── logger.py            # Logging configuration
│   ├── screenshot.py        # Screenshot capture
│   ├── data_loader.py       # Test data loading
│   └── allure_helper.py     # Allure reporting helpers
│
├── conftest.py              # Pytest fixtures & configuration
└── data/                    # Test data files
    └── test_data.json
```

### Step 2: Reading Order - The Learning Path

Follow this exact order to understand the project systematically:

#### Phase 1: Core Framework (Foundation)

**1. `config/settings.py`** - Start here!
- Understand all configuration options
- See browser matrix for multi-browser support
- Learn timeout and retry settings

**2. `core/smart_locator.py`** - The heart of the framework
- Understand `SmartLocator` class and how it holds multiple locator strategies
- Study `SmartLocatorResolver` - the engine that tries locators sequentially
- Key pattern: fallback mechanism for resilience

**3. `core/base_page.py`** - The abstract foundation
- See how `SmartLocator` integrates with page interactions
- Understand `find_element()`, `click()`, `fill()` methods
- Note the integration of wait handler and retry handler

**4. `core/browser_factory.py`** - Session management
- Understand `BrowserSession` dataclass
- See how browser instances are created and isolated
- Learn about session lifecycle and cleanup

**5. `core/wait_handler.py`** - Smart waiting
- Different wait conditions (VISIBLE, CLICKABLE, EDITABLE)
- Smart wait based on action type

#### Phase 2: Page Objects (Implementation)

**6. `pages/home_page.py`** - First page object
- See how locators are defined in `_define_locators()`
- Study the pattern of 3-5 fallback strategies per element
- Understand `identification()` method - verifies page is loaded

**7. `pages/search_results_page.py`** - Main function
- Contains `search_items_by_name_under_price()` function
- See price filtering and URL collection logic

**8. `pages/product_page.py`** - Cart operations
- Contains `add_items_to_cart()` function
- Handles product variants and add-to-cart flow

**9. `pages/cart_page.py`** - Assertions
- Contains `assert_cart_total_not_exceeds()` function
- Cart validation and total calculation

#### Phase 3: Tests & Infrastructure

**10. `conftest.py`** - Pytest configuration
- Understand fixture hierarchy: session → function scope
- See `browser_session` fixture providing isolation
- Learn about screenshot-on-failure mechanism

**11. `tests/e2e/test_ebay_shopping_flow.py`** - Main test
- Complete E2E scenario implementation
- See Allure annotations and step organization
- Understand test parameterization

---

## Architecture Deep Dive

### Smart Locator System - How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    SmartLocator Definition                   │
│                                                              │
│  SEARCH_INPUT = SmartLocator(name="Search Input")           │
│    .add_xpath("//input[@id='gh-ac']")      ─────► Strategy 1│
│    .add_xpath("//input[@placeholder='...']") ───► Strategy 2│
│    .add_css("input[name='_nkw']")          ─────► Strategy 3│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  SmartLocatorResolver                        │
│                                                              │
│  1. Try Strategy 1 (xpath by ID)                            │
│     └─ Timeout? → Move to next strategy                     │
│                                                              │
│  2. Try Strategy 2 (xpath by placeholder)                   │
│     └─ Found? → Return Playwright Locator                   │
│     └─ Timeout? → Move to next strategy                     │
│                                                              │
│  3. Try Strategy 3 (css selector)                           │
│     └─ Found? → Return Playwright Locator                   │
│     └─ Failed? → Capture screenshot, raise error            │
└─────────────────────────────────────────────────────────────┘
```

### Test Execution Flow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│pytest_configure│──►│browser_factory│──►│browser_session│
│(session setup)│    │(session scope)│    │(function scope)│
└──────────────┘    └──────────────┘    └──────────────┘
                                              │
                                              ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Create Page │    │ Execute Test │    │   Cleanup    │
│   Objects    │───►│    Steps     │───►│   Session    │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Session Isolation Diagram

```
Test 1                    Test 2                    Test 3
   │                         │                         │
   ▼                         ▼                         ▼
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│ Browser     │         │ Browser     │         │ Browser     │
│ Instance 1  │         │ Instance 2  │         │ Instance 3  │
├─────────────┤         ├─────────────┤         ├─────────────┤
│ Context 1   │         │ Context 2   │         │ Context 3   │
│ (cookies,   │         │ (cookies,   │         │ (cookies,   │
│  storage)   │         │  storage)   │         │  storage)   │
├─────────────┤         ├─────────────┤         ├─────────────┤
│ Page 1      │         │ Page 2      │         │ Page 3      │
└─────────────┘         └─────────────┘         └─────────────┘

      │                       │                       │
      └───────────────────────┴───────────────────────┘
                              │
                        COMPLETE ISOLATION
                     (No shared state between tests)
```

---

## Key Concepts Explained

### 1. Page Object Model (POM)

**What:** Design pattern that creates an object repository for web elements.

**Why:**
- Reduces code duplication
- Improves maintainability - change locator in one place
- Separates test logic from page structure

**Example in this project:**
```python
# BasePage provides common functionality
class HomePage(BasePage):
    PAGE_URL = "https://www.ebay.com"

    def _define_locators(self):
        self.SEARCH_INPUT = SmartLocator(name="Search Input")
        self.SEARCH_INPUT.add_xpath("//input[@id='gh-ac']")

    def search(self, query: str):
        self.fill(self.SEARCH_INPUT, query)
        self.click(self.SEARCH_BUTTON)
```

### 2. Smart Locator Pattern

**Problem:** UI elements frequently change, breaking tests.

**Solution:** Define multiple locator strategies per element, try them in order.

**Benefits:**
- Tests survive minor UI changes
- Automatic fallback without test code changes
- Detailed logging of which strategy worked

### 3. Fixture Hierarchy

```
session scope (created once)
    │
    └── browser_factory  ──► Single factory for all tests

function scope (created per test)
    │
    ├── browser_session  ──► Fresh browser + context + page
    ├── page             ──► Derived from browser_session
    └── screenshot_on_failure ──► Automatic screenshot on error
```

### 4. Three Core Functions (as per requirements)

| Function | Location | Purpose |
|----------|----------|---------|
| `search_items_by_name_under_price(query, max_price, limit)` | `search_results_page.py` | Find items under price threshold |
| `add_items_to_cart(page, urls)` | `product_page.py` | Add multiple items to cart |
| `assert_cart_total_not_exceeds(budget_per_item, items_count)` | `cart_page.py` | Verify cart total within budget |

---

## Interview Questions - This Project

### Basic Questions

**Q1: Explain the project architecture and the design patterns used.**

**Expected Answer:**
> The project uses the Page Object Model (POM) pattern with a layered architecture:
> - **Core Layer:** Contains `BasePage` (abstract class), `SmartLocator` (element location), `BrowserFactory` (session management), `WaitHandler` and `RetryHandler`
> - **Pages Layer:** Concrete page objects (`HomePage`, `SearchResultsPage`, `ProductPage`, `CartPage`) that inherit from `BasePage`
> - **Tests Layer:** E2E and unit tests using pytest
> - **Config Layer:** Centralized settings using a singleton pattern
>
> The key innovation is the Smart Locator System that provides automatic fallback between multiple locator strategies.

---

**Q2: What is the Smart Locator System and why is it important?**

**Expected Answer:**
> The Smart Locator System is a custom solution for resilient element location. Each `SmartLocator` holds multiple locator strategies (XPath, CSS, text, role, etc.). The `SmartLocatorResolver` tries each strategy sequentially until one succeeds.
>
> **Why it's important:**
> - UI elements change frequently (IDs removed, classes renamed)
> - Instead of tests failing, they automatically try alternative locators
> - Provides detailed logging of which strategy succeeded/failed
> - Captures screenshots on final failure for debugging

---

**Q3: How does session isolation work in this framework?**

**Expected Answer:**
> Session isolation is achieved through the `BrowserFactory` and pytest fixtures:
>
> 1. `browser_factory` fixture is session-scoped - created once for all tests
> 2. `browser_session` fixture is function-scoped - each test gets:
>    - A new browser instance
>    - A new browser context (isolated cookies, storage)
>    - A new page object
> 3. After each test, the session is closed and resources are released
>
> This ensures tests don't share state and can run in parallel without conflicts.

---

**Q4: Walk me through the test execution flow from start to finish.**

**Expected Answer:**
> 1. `pytest_configure()` initializes logging and creates report directories
> 2. `browser_factory` fixture creates the factory (session scope)
> 3. For each test:
>    - `browser_session` fixture creates isolated browser/context/page
>    - Test creates page objects (e.g., `HomePage(page)`)
>    - Page object's `_define_locators()` sets up SmartLocators
>    - Test executes steps using page methods
>    - On failure, `screenshot_on_failure` fixture captures screenshot
>    - Session is closed via `browser_factory.close_session()`
> 4. At session end, `browser_factory.shutdown()` releases all resources

---

**Q5: How would you add a new page object to this framework?**

**Expected Answer:**
> 1. Create a new file in `pages/` directory (e.g., `checkout_page.py`)
> 2. Inherit from `BasePage`
> 3. Define `PAGE_URL` and `PAGE_NAME` class attributes
> 4. Override `_define_locators()` method to define all SmartLocators
> 5. Add 3-5 fallback strategies per locator using chainable methods:
>    ```python
>    self.ELEMENT = SmartLocator(name="Element Name")
>    self.ELEMENT.add_xpath("//primary/xpath")
>    self.ELEMENT.add_css("fallback-css-selector")
>    ```
> 6. Implement page-specific methods using inherited methods like `click()`, `fill()`
> 7. Export the new page from `pages/__init__.py`

---

### Intermediate Questions

**Q6: Explain the retry mechanism in this framework.**

**Expected Answer:**
> The framework has two levels of retry:
>
> 1. **Smart Locator Level:** `SmartLocatorResolver` tries each locator strategy (up to `max_locator_retries` from config)
>
> 2. **Action Level:** `RetryHandler` provides exponential backoff retry:
>    - Configurable `max_retries`, `initial_delay`, `max_delay`
>    - Backoff formula: `delay = min(initial_delay * (backoff_multiplier ^ attempt), max_delay)`
>    - Can be used as decorator `@retry(max_retries=3)` or context manager
>
> This handles both flaky element location and transient action failures.

---

**Q7: How does the framework handle different browsers?**

**Expected Answer:**
> The `BROWSER_MATRIX` in `settings.py` defines configurations for each browser:
> - **Playwright browsers:** chromium, firefox, webkit
> - **Chrome channels:** chrome (stable), chrome-beta, chrome-dev
> - **Edge:** msedge (Chromium-based)
>
> Each config specifies:
> - `headless` mode
> - `viewport` dimensions
> - `timeout` values
> - `channel` for Chrome variants
> - Custom `args` (e.g., `--disable-blink-features=AutomationControlled`)
>
> The `BrowserFactory._get_browser_type()` maps browser names to Playwright browser types.

---

**Q8: What is the difference between `find_element()` and `find_element_safe()`?**

**Expected Answer:**
> | Method | Behavior on Not Found |
> |--------|----------------------|
> | `find_element()` | Raises `ElementNotFoundError` exception |
> | `find_element_safe()` | Returns `None`, doesn't raise exception |
>
> Use `find_element()` when the element must exist - test should fail if missing.
> Use `find_element_safe()` for optional elements or conditional logic.

---

**Q9: How does the framework integrate with Allure reporting?**

**Expected Answer:**
> Allure integration happens at multiple levels:
>
> 1. **Test Decorators:**
>    - `@allure.epic("eBay E2E Tests")` - top-level grouping
>    - `@allure.feature("Shopping Flow")` - feature grouping
>    - `@allure.story("...")` - user story
>    - `@allure.title("...")` - test title
>
> 2. **Step Logging:**
>    - `with allure.step("Step description"):` - marks test steps
>    - `@allure_step` decorator from `utils/allure_helper.py`
>
> 3. **Attachments:**
>    - `allure.attach()` - attach screenshots, text, logs
>    - Automatic screenshot on failure
>
> 4. **Unique Report Directories:**
>    - `settings.REPORT.generate_unique_report_dir` creates timestamped dirs
>    - View with `allure serve reports/allure-results_TIMESTAMP/`

---

**Q10: How would you debug a failing test in this framework?**

**Expected Answer:**
> 1. **Check Screenshots:** Look in `reports/screenshots/` for failure screenshots
>
> 2. **Review Logs:**
>    - `logs/framework.log` - general framework logs
>    - `logs/playwright_*.log` - Playwright API calls
>    - `logs/browser_console_*.log` - Browser console output
>    - `logs/browser_network_*.log` - Network requests/responses
>
> 3. **Run with Visible Browser:**
>    ```bash
>    pytest tests/e2e/test_file.py --headed -v
>    ```
>
> 4. **Check Allure Report:** Step-by-step execution trace with attachments
>
> 5. **Add Debugging:** Use `page.pause()` (Playwright Inspector) or add `self.capture_screenshot("debug")` in page methods

---

### Advanced Questions

**Q11: How would you implement parallel test execution across multiple browsers?**

**Expected Answer:**
> The framework already supports this via pytest-xdist:
>
> ```bash
> # Run 4 parallel workers
> pytest tests/ -n 4
>
> # Run same tests on multiple browsers in parallel
> pytest tests/e2e/ -n 3 --browser=chromium --browser=firefox --browser=webkit
> ```
>
> Session isolation ensures no conflicts:
> - Each worker gets its own `browser_factory` (session scope per worker)
> - Each test gets isolated `browser_session`
> - Allure results merge automatically
>
> For cross-browser matrix testing, use `create_parallel_sessions()` method.

---

**Q12: What are the potential issues with the Smart Locator approach and how would you mitigate them?**

**Expected Answer:**
> **Issues:**
> 1. **Performance:** Trying multiple locators takes longer than single locator
> 2. **False Positives:** Fallback locator might match wrong element
> 3. **Maintenance:** More locators = more to maintain
>
> **Mitigations:**
> 1. **Performance:** Order locators by reliability (most stable first), limit `max_locator_retries`
> 2. **False Positives:** Use specific locators (prefer ID/test-id over generic CSS), add element count validation
> 3. **Maintenance:** Document each locator strategy, run periodic locator audits, prefer 3-5 locators (not more)

---

**Q13: How would you add API testing capability to this framework?**

**Expected Answer:**
> 1. Create `core/api_client.py` with HTTP client wrapper (using `requests` or `httpx`)
> 2. Add `APIConfig` dataclass to settings
> 3. Create `api/` directory for API page objects (similar pattern to UI pages)
> 4. Add fixtures in `conftest.py` for API client:
>    ```python
>    @pytest.fixture
>    def api_client():
>        return APIClient(base_url=settings.API_BASE_URL)
>    ```
> 5. Create hybrid tests that use both UI and API:
>    - API for setup/teardown (faster)
>    - UI for actual user flow verification

---

**Q14: Explain how you would implement data-driven testing in this framework.**

**Expected Answer:**
> The framework already has basic data-driven support:
>
> 1. **JSON Test Data:** `data/test_data.json` loaded via `DataLoader`
> 2. **Pytest Parametrize:** Already used in `TestParameterizedShoppingFlow`:
>    ```python
>    @pytest.mark.parametrize("query,max_price,limit", [
>        ("shoes", 220, 5),
>        ("laptop", 500, 3),
>    ])
>    def test_shopping_flow(self, page, query, max_price, limit):
>        ...
>    ```
>
> To extend:
> - Add more JSON/YAML/CSV data files
> - Create `@pytest.fixture` that loads data based on test name
> - Use `pytest_generate_tests` hook for dynamic test generation

---

**Q15: How does the `WaitHandler` implement "smart wait" and why is it important?**

**Expected Answer:**
> The `WaitHandler.smart_wait()` method selects the appropriate wait condition based on the action type:
>
> | Action | Wait Condition |
> |--------|---------------|
> | click | CLICKABLE (visible + enabled) |
> | fill | EDITABLE (visible + editable) |
> | select | VISIBLE (element visible) |
>
> **Why it's important:**
> - Prevents "element not interactable" errors
> - Waits just long enough (not fixed sleep)
> - Adapts to different element states automatically
> - Improves test reliability without hardcoded waits

---

## Interview Questions - Playwright

### Basic Playwright Questions

**Q16: What is Playwright and how does it differ from Selenium?**

**Expected Answer:**
> | Aspect | Playwright | Selenium |
> |--------|-----------|----------|
> | Architecture | Direct browser protocol (CDP, Firefox Protocol) | WebDriver protocol |
> | Speed | Faster (no intermediate server) | Slower (WebDriver bridge) |
> | Auto-Wait | Built-in auto-waiting | Manual waits required |
> | Browser Support | Chromium, Firefox, WebKit | All browsers via drivers |
> | Language Support | Python, JS/TS, Java, C# | All major languages |
> | Network Interception | Native support | Requires proxy |
> | Mobile Emulation | Built-in | Limited |
> | Trace Viewer | Rich debugging tool | Basic |

---

**Q17: Explain Playwright's auto-waiting mechanism.**

**Expected Answer:**
> Playwright automatically waits for elements before performing actions:
>
> - **Attached:** Element is in the DOM
> - **Visible:** Element has non-empty bounding box and no `visibility:hidden`
> - **Stable:** Element is not animating or animation completed
> - **Receives Events:** Element is not obscured by other elements
> - **Enabled:** Element is not disabled (for input elements)
>
> Example: `page.click("#button")` will automatically wait until button is visible, stable, and enabled.
>
> Custom waits still available:
> ```python
> locator.wait_for(state="visible", timeout=5000)
> page.wait_for_url("**/search*")
> page.wait_for_load_state("networkidle")
> ```

---

**Q18: What are Playwright Locators and how do they differ from ElementHandle?**

**Expected Answer:**
> | Locator | ElementHandle |
> |---------|--------------|
> | Represents a way to find element(s) | Represents a specific DOM element |
> | Re-queries DOM on each action | Holds reference to existing element |
> | Auto-retry if element not found | Fails if element is removed |
> | Recommended approach | Legacy approach |
>
> **Locator example:**
> ```python
> locator = page.locator("#submit-btn")  # Just a query
> locator.click()  # Executes query, then clicks
> ```
>
> **ElementHandle (not recommended):**
> ```python
> element = page.query_selector("#submit-btn")  # Immediate query
> element.click()  # May fail if element was removed
> ```

---

**Q19: How do you handle frames and iframes in Playwright?**

**Expected Answer:**
> ```python
> # Method 1: frame_locator (recommended)
> frame = page.frame_locator("iframe#payment")
> frame.locator("#card-number").fill("1234")
>
> # Method 2: Direct frame access
> frame = page.frame(name="payment-frame")
> frame.click("#submit")
>
> # Method 3: By URL
> frame = page.frame(url="**/payment/**")
>
> # Nested frames
> inner = page.frame_locator("#outer").frame_locator("#inner")
> inner.locator("button").click()
> ```

---

**Q20: What are Playwright contexts and why are they important?**

**Expected Answer:**
> A **Browser Context** is an isolated browser session within a single browser instance:
>
> - **Separate cookies** - contexts don't share cookies
> - **Separate localStorage** - isolated storage
> - **Separate sessions** - different logged-in users
> - **Lightweight** - faster than launching new browser
>
> **Use cases:**
> ```python
> # Multi-user testing
> admin_context = browser.new_context()
> user_context = browser.new_context()
>
> admin_page = admin_context.new_page()
> user_page = user_context.new_page()
>
> # Incognito-like behavior
> context = browser.new_context()  # Fresh, isolated
>
> # Mobile emulation
> context = browser.new_context(
>     viewport={"width": 375, "height": 667},
>     user_agent="Mozilla/5.0 (iPhone...)",
>     has_touch=True
> )
> ```

---

### Intermediate Playwright Questions

**Q21: How does Playwright handle network interception?**

**Expected Answer:**
> ```python
> # Intercept and mock response
> def handle_route(route):
>     if "api/users" in route.request.url:
>         route.fulfill(
>             status=200,
>             body=json.dumps({"name": "Mock User"})
>         )
>     else:
>         route.continue_()
>
> page.route("**/*", handle_route)
>
> # Block resources
> page.route("**/*.{png,jpg,jpeg}", lambda route: route.abort())
>
> # Modify request
> def modify_headers(route):
>     headers = route.request.headers
>     headers["Authorization"] = "Bearer token"
>     route.continue_(headers=headers)
>
> page.route("**/api/**", modify_headers)
>
> # Wait for specific request
> with page.expect_request("**/api/submit") as request_info:
>     page.click("#submit")
> request = request_info.value
> ```

---

**Q22: Explain Playwright's assertion library.**

**Expected Answer:**
> Playwright provides `expect()` with auto-retry:
>
> ```python
> from playwright.sync_api import expect
>
> # Element assertions
> expect(locator).to_be_visible()
> expect(locator).to_be_enabled()
> expect(locator).to_have_text("Hello")
> expect(locator).to_have_value("input value")
> expect(locator).to_have_attribute("href", "/page")
> expect(locator).to_have_class("active")
> expect(locator).to_have_count(5)
>
> # Page assertions
> expect(page).to_have_url("**/dashboard")
> expect(page).to_have_title("Dashboard")
>
> # Negation
> expect(locator).not_to_be_visible()
>
> # Custom timeout
> expect(locator).to_be_visible(timeout=10000)
> ```
>
> **Key difference from pytest assertions:** Playwright assertions auto-retry until condition met or timeout.

---

**Q23: How do you handle file uploads and downloads in Playwright?**

**Expected Answer:**
> **File Upload:**
> ```python
> # Standard file input
> page.set_input_files("input[type=file]", "path/to/file.pdf")
>
> # Multiple files
> page.set_input_files("input[type=file]", ["file1.pdf", "file2.pdf"])
>
> # File chooser for non-standard inputs
> with page.expect_file_chooser() as fc_info:
>     page.click("#upload-btn")
> file_chooser = fc_info.value
> file_chooser.set_files("file.pdf")
> ```
>
> **File Download:**
> ```python
> # Wait for download
> with page.expect_download() as download_info:
>     page.click("#download-btn")
> download = download_info.value
>
> # Save to path
> download.save_as("./downloads/file.pdf")
>
> # Get download path
> path = download.path()
> ```

---

**Q24: What is Playwright's Trace Viewer and how do you use it?**

**Expected Answer:**
> Trace Viewer is a debugging tool that records everything during test execution:
>
> **Recording trace:**
> ```python
> context = browser.new_context()
> context.tracing.start(screenshots=True, snapshots=True, sources=True)
>
> # ... run test ...
>
> context.tracing.stop(path="trace.zip")
> ```
>
> **Viewing trace:**
> ```bash
> playwright show-trace trace.zip
> ```
>
> **What it captures:**
> - DOM snapshots at each action
> - Screenshots timeline
> - Network requests/responses
> - Console logs
> - Source code with action highlights
>
> **With pytest-playwright:**
> ```bash
> pytest --tracing on  # Trace all tests
> pytest --tracing retain-on-failure  # Only failed tests
> ```

---

**Q25: How do you perform visual regression testing with Playwright?**

**Expected Answer:**
> ```python
> # Basic screenshot comparison
> expect(page).to_have_screenshot("homepage.png")
>
> # Element screenshot
> expect(locator).to_have_screenshot("button.png")
>
> # With options
> expect(page).to_have_screenshot(
>     "page.png",
>     full_page=True,
>     mask=[page.locator(".dynamic-element")],  # Ignore dynamic content
>     threshold=0.2,  # Allow 20% difference
>     max_diff_pixel_count=100  # Allow 100 different pixels
> )
>
> # Update baseline
> # pytest --update-snapshots
> ```
>
> **Best practices:**
> - Use `mask` for dynamic content (timestamps, avatars)
> - Set appropriate `threshold` for font rendering differences
> - Run in consistent environment (Docker, CI)

---

### Advanced Playwright Questions

**Q26: How do you handle authentication in Playwright tests?**

**Expected Answer:**
> **Method 1: Storage State (Recommended)**
> ```python
> # Login once, save state
> context = browser.new_context()
> page = context.new_page()
> page.goto("/login")
> page.fill("#username", "user")
> page.fill("#password", "pass")
> page.click("#submit")
> context.storage_state(path="auth.json")
>
> # Reuse in tests
> context = browser.new_context(storage_state="auth.json")
> page = context.new_page()
> page.goto("/dashboard")  # Already logged in!
> ```
>
> **Method 2: HTTP Authentication**
> ```python
> context = browser.new_context(
>     http_credentials={
>         "username": "user",
>         "password": "pass"
>     }
> )
> ```
>
> **Method 3: API Login**
> ```python
> api_context = playwright.request.new_context()
> response = api_context.post("/api/login", data={...})
> cookies = response.cookies()
> context = browser.new_context()
> context.add_cookies(cookies)
> ```

---

**Q27: How do you test applications with multiple windows/tabs?**

**Expected Answer:**
> ```python
> # Wait for new page (popup, new tab)
> with context.expect_page() as page_info:
>     page.click("#open-new-tab")
> new_page = page_info.value
>
> # Wait for new page to load
> new_page.wait_for_load_state()
> new_page.locator("#element").click()
>
> # Get all pages in context
> pages = context.pages
>
> # Handle popup
> with page.expect_popup() as popup_info:
>     page.click("#open-popup")
> popup = popup_info.value
> popup.wait_for_load_state()
>
> # Close popup
> popup.close()
> ```

---

**Q28: How does Playwright handle shadow DOM?**

**Expected Answer:**
> Playwright automatically pierces shadow DOM by default:
>
> ```python
> # This works even if button is inside shadow DOM
> page.locator("button#shadow-button").click()
>
> # CSS engine pierces shadow DOM
> page.locator("css=my-component >> button").click()
>
> # For explicit shadow DOM navigation
> page.locator("my-component").locator("internal:shadow-root").locator("button")
>
> # XPath does NOT pierce shadow DOM
> # Use CSS or built-in locators instead
> ```

---

**Q29: What are Playwright's capabilities for mobile testing?**

**Expected Answer:**
> ```python
> from playwright.sync_api import sync_playwright
>
> with sync_playwright() as p:
>     # Use device preset
>     iphone = p.devices["iPhone 13"]
>     context = p.chromium.launch().new_context(**iphone)
>
>     # Custom mobile config
>     context = p.webkit.launch().new_context(
>         viewport={"width": 375, "height": 812},
>         device_scale_factor=3,
>         is_mobile=True,
>         has_touch=True,
>         user_agent="Mozilla/5.0 (iPhone..."
>     )
>
>     # Geolocation
>     context = browser.new_context(
>         geolocation={"latitude": 37.7749, "longitude": -122.4194},
>         permissions=["geolocation"]
>     )
>
>     # Touch actions
>     page.locator("#element").tap()
>     page.touchscreen.tap(100, 200)
> ```

---

**Q30: How do you implement custom fixtures with pytest-playwright?**

**Expected Answer:**
> ```python
> # conftest.py
> import pytest
> from playwright.sync_api import Page, BrowserContext
>
> # Override default browser
> @pytest.fixture(scope="session")
> def browser_type_launch_args():
>     return {"slow_mo": 100, "headless": True}
>
> # Override default context
> @pytest.fixture
> def context(browser):
>     context = browser.new_context(
>         viewport={"width": 1920, "height": 1080},
>         record_video_dir="videos/"
>     )
>     yield context
>     context.close()
>
> # Custom page fixture
> @pytest.fixture
> def authenticated_page(context) -> Page:
>     page = context.new_page()
>     page.goto("/login")
>     page.fill("#user", "admin")
>     page.fill("#pass", "secret")
>     page.click("#submit")
>     return page
>
> # Page with network mocking
> @pytest.fixture
> def mocked_page(page):
>     page.route("**/api/**", lambda r: r.fulfill(body="{}"))
>     return page
> ```

---

## Interview Questions - General Automation

### Design & Architecture Questions

**Q31: What makes a good test automation framework?**

**Expected Answer:**
> - **Maintainability:** Changes in one place, POM pattern, DRY principle
> - **Reliability:** Smart waits, retry mechanisms, no flaky tests
> - **Scalability:** Parallel execution, cross-browser support
> - **Readability:** Clear test names, self-documenting code, good logging
> - **Reporting:** Rich reports with screenshots, steps, attachments
> - **Reusability:** Shared components, fixtures, utilities
> - **Independence:** Tests don't depend on each other, isolated sessions
> - **Data-Driven:** External test data, parameterization

---

**Q32: How do you handle flaky tests?**

**Expected Answer:**
> 1. **Identify root cause:**
>    - Timing issues → Add proper waits
>    - Race conditions → Synchronize with specific events
>    - External dependencies → Mock/stub them
>    - Shared state → Ensure isolation
>
> 2. **Prevention strategies:**
>    - Never use `sleep()`, use explicit waits
>    - Wait for specific conditions, not arbitrary timeouts
>    - Use retry mechanism for transient failures
>    - Implement proper test isolation
>
> 3. **Detection:**
>    - Run tests multiple times in CI
>    - Track flakiness metrics
>    - Quarantine flaky tests until fixed

---

**Q33: What is your approach to test data management?**

**Expected Answer:**
> 1. **Static Test Data:** JSON/YAML files for fixed data (valid inputs, expected results)
> 2. **Dynamic Data:** Factories/generators for unique data (emails, timestamps)
> 3. **Database Seeding:** Scripts to set up required data before tests
> 4. **Fixtures:** Pytest fixtures for data setup/teardown
> 5. **Isolation:** Each test creates/cleans its own data
> 6. **Environment-Specific:** Different data files per environment
> 7. **Sensitive Data:** Never hardcode credentials, use environment variables

---

**Q34: How do you decide what to automate?**

**Expected Answer:**
> **Automate:**
> - Regression tests (run frequently)
> - Smoke tests (critical paths)
> - Data-driven tests (many variations)
> - Cross-browser/platform tests
> - Performance-critical flows
>
> **Don't Automate:**
> - One-time tests
> - Exploratory testing
> - Tests for features still changing rapidly
> - Tests cheaper to run manually
>
> **ROI Calculation:**
> - Time to automate vs time saved per run
> - How often the test will run
> - Maintenance cost over time

---

**Q35: How do you integrate automation into CI/CD?**

**Expected Answer:**
> ```yaml
> # Example GitHub Actions workflow
> name: E2E Tests
> on: [push, pull_request]
>
> jobs:
>   test:
>     runs-on: ubuntu-latest
>     steps:
>       - uses: actions/checkout@v3
>
>       - name: Setup Python
>         uses: actions/setup-python@v4
>         with:
>           python-version: '3.11'
>
>       - name: Install dependencies
>         run: |
>           pip install -r requirements.txt
>           playwright install --with-deps
>
>       - name: Run tests
>         run: pytest tests/ -v --alluredir=allure-results
>
>       - name: Upload Allure results
>         uses: actions/upload-artifact@v3
>         with:
>           name: allure-results
>           path: allure-results/
> ```
>
> **Best practices:**
> - Run smoke tests on every PR
> - Run full regression nightly
> - Fail build on test failures
> - Publish reports as artifacts

---

## Quick Reference Commands

```bash
# Run all tests
pytest tests/ -v

# Run E2E tests only
pytest tests/e2e/ -v

# Run with visible browser
pytest tests/e2e/ --headed -v

# Run specific browser
pytest tests/e2e/ --browser firefox -v

# Run in parallel
pytest tests/ -n 4 -v

# Generate Allure report
pytest tests/ --alluredir=allure-results
allure serve allure-results

# Debug with Playwright Inspector
PWDEBUG=1 pytest tests/e2e/test_file.py -v
```

---

## Summary

This project demonstrates professional automation framework development with:

1. **Smart Locator System** - Innovative approach to resilient element location
2. **Page Object Model** - Clean separation of concerns
3. **Session Isolation** - Reliable parallel execution
4. **Rich Reporting** - Allure integration with detailed steps
5. **Multi-Browser Support** - Cross-browser testing capability

For interview preparation, focus on:
- Understanding the architectural decisions and trade-offs
- Being able to explain the Smart Locator pattern in detail
- Knowing Playwright specifics vs Selenium
- Having practical debugging and troubleshooting approaches
