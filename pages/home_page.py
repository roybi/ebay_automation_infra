from playwright.sync_api import Page

from core.base_page import BasePage
from core.smart_locator import SmartLocator
from utils.allure_helper import allure_step


class HomePage(BasePage):
    """Page object for the Home Page."""

    PAGE_URL = "https://www.ebay.com"
    PAGE_NAME = "HomePage"

    def __init__(self, page: Page):
        super().__init__(page)
        self._define_locators()

    def _define_locators(self):
        """Define locators for the Home Page."""

        # ---- Search Input Field
        self.SEARCH_INPUT = SmartLocator(name="Search Input")
        # XPath by ID

        self.SEARCH_INPUT.add_xpath("//input[@id='gh-ac']", "XPath - ID based")

        # XPath by placeholder
        self.SEARCH_INPUT.add_xpath(
            "//input[@placeholder='Search for anything']", "XPath - placeholder"
        )

        # CSS by attribute
        self.SEARCH_INPUT.add_css(
            "input[type='text'][name='_nkw']", "CSS - attribute selector"
        )

        # --- Search Button
        self.SEARCH_BUTTON = SmartLocator(name="Search Button")
        # XPath by text
        self.SEARCH_BUTTON.add_xpath("//button[text()='Search']", "text")
        # XPath by aria-label
        self.SEARCH_BUTTON.add_xpath("//button[contains(@aria-label, 'Search')]", "aria-label")
        # CSS by type
        self.SEARCH_BUTTON.add_css("button[type='submit']", "type")
        # XPath by class
        self.SEARCH_BUTTON.add_xpath("//button[contains(@class, 'btn')]", "class")
        # XPath fallback
        self.SEARCH_BUTTON.add_xpath("//form[@role='search']//button", "form button")

        # ----- eBay Logo
        self.EBAY_LOGO = SmartLocator(name="eBay Logo")
        # XPath by ID
        self.EBAY_LOGO.add_xpath("//a[@id='gh-la']", "ID")
        # XPath by class
        self.EBAY_LOGO.add_xpath("//a[contains(@class, 'gh-logo')]", "class")
        # CSS by ID
        self.EBAY_LOGO.add_css("a#gh-la", "CSS ID")
        # XPath by aria-label
        self.EBAY_LOGO.add_xpath("//a[@aria-label='eBay Home']", "aria-label")
        # XPath by href
        self.EBAY_LOGO.add_xpath("//a[contains(@href, 'ebay.com')][@class]", "href")

        # Cart Icon
        self.CART_ICON = SmartLocator(name="Cart Icon")
        # XPath by href
        self.CART_ICON.add_xpath("//a[contains(@href, 'cart')]", "href")
        # XPath by aria-label
        self.CART_ICON.add_xpath("//a[contains(@aria-label, 'cart')]", "aria-label")
        # CSS by href
        self.CART_ICON.add_css("a[href*='cart']", "CSS href")
        # XPath by title
        self.CART_ICON.add_xpath("//a[contains(@title, 'cart')]", "title")
        # XPath by any cart link
        self.CART_ICON.add_xpath("//a[contains(., 'cart') or contains(@class, 'cart')]", "any cart")

        # -------Category Dropdown
        self.CATEGORY_DROPDOWN = SmartLocator(name="Category Dropdown")
        # XPath by ID
        self.CATEGORY_DROPDOWN.add_xpath("//select[@id='gh-cat']", "XPath - ID based")
        # CSS by ID
        self.CATEGORY_DROPDOWN.add_css("#gh-cat", "CSS - ID selector")
        # CSS by class
        self.CATEGORY_DROPDOWN.add_css("select.gh-cat__sel", "CSS - class selector")

        # ------- My eBay Link
        self.MY_EBAY_LINK = SmartLocator(name="My eBay Link")
        # XPath by ID
        self.MY_EBAY_LINK.add_xpath("//a[@id='gh-eb-My']", "XPath - ID based")

        # ---- Sign In Link

        # XPath by href
        self.SIGN_IN_LINK = SmartLocator(name="Sign In Link")
        self.SIGN_IN_LINK.add_xpath(
            "//a[contains(@href, 'signin')]", "XPath - href contains"
        )
        # XPath by class and text
        self.SIGN_IN_LINK.add_xpath(
            "//span[contains(@class, 'gh-eb-u')]/a", "XPath - parent class"
        )

    @allure_step("Identification - Verify eBay homepage is loaded")
    def identification(self) -> bool:
        """
        Verifies that the eBay homepage is properly loaded and identified.
        Checks for key elements that confirm we are on the correct page.
        """
        self.log_action("Identification", "Verifying eBay homepage")

        try:
            # Navigate to homepage if not already there
            if "ebay.com" not in self.current_url.lower():
                self.navigate()

            # Wait for page load
            self.wait_for_page_load()

            # Verify key elements are present
            checks = {
                "eBay Logo": self.is_element_visible(self.EBAY_LOGO),
                "Search Input": self.is_element_visible(self.SEARCH_INPUT),
                "Search Button": self.is_element_visible(self.SEARCH_BUTTON),
                "Cart Icon": self.is_element_visible(self.CART_ICON),
            }

            # Log results
            for element_name, is_visible in checks.items():
                status = "FOUND" if is_visible else "NOT FOUND"
                self.logger.info(f"Identification check - {element_name}: {status}")

            # Verify URL
            is_ebay = "ebay.com" in self.current_url.lower()
            self.logger.info(
                f"URL verification: {self.current_url} - {'VALID' if is_ebay else 'INVALID'}"
            )

            # Critical elements: Search Input and Search Button must be present
            critical_elements = checks["Search Input"] and checks["Search Button"]
            all_passed = critical_elements and is_ebay

            # Log if optional elements are missing
            if not checks["eBay Logo"]:
                self.logger.warning("Optional element 'eBay Logo' not found - continuing anyway")
            if not checks["Cart Icon"]:
                self.logger.warning("Optional element 'Cart Icon' not found - continuing anyway")

            if all_passed:
                self.logger.info("Identification: SUCCESS - eBay homepage verified")
                self.capture_screenshot("identification_success")
            else:
                self.logger.error("Identification: FAILED - Some elements not found")
                self.capture_screenshot("identification_failure")

            return all_passed

        except Exception as e:
            self.logger.error(f"Identification failed with error: {str(e)}")
            self.capture_screenshot("identification_error")
            return False

    @allure_step("Perform search")
    def search(self, query: str) -> None:
        """
        Perform a search on eBay.

        """
        self.log_action("Search", f"Searching for: {query}")

        # Clear and fill search input
        self.fill(self.SEARCH_INPUT, query)

        # Click search button
        self.click(self.SEARCH_BUTTON)

        # Wait for results page to load
        self.wait_for_page_load()
        self.wait_for_network_idle()

        self.logger.info(f"Search completed for: {query}")

    @allure_step("Search with category")
    def search_with_category(self, query: str, category: str) -> None:
        """
        Perform a search with specific category selected.

        """
        self.log_action("Search with Category", f"Query: {query}, Category: {category}")

        # Select category first
        if self.is_element_visible(self.CATEGORY_DROPDOWN):
            self.select_option(self.CATEGORY_DROPDOWN, label=category)

        # Perform search
        self.fill(self.SEARCH_INPUT, query)
        self.click(self.SEARCH_BUTTON)

        self.wait_for_page_load()
        self.wait_for_network_idle()

    @allure_step("Navigate to cart")
    def go_to_cart(self) -> None:
        """Navigate to shopping cart."""
        self.log_action("Navigation", "Going to cart")
        self.click(self.CART_ICON)
        self.wait_for_page_load()

    @allure_step("Navigate to My eBay")
    def go_to_my_ebay(self) -> None:
        """Navigate to My eBay page."""
        self.log_action("Navigation", "Going to My eBay")
        self.click(self.MY_EBAY_LINK)
        self.wait_for_page_load()

    def is_user_logged_in(self) -> bool:
        """Check if user is logged in."""
        # If sign in link is visible, user is not logged in
        return not self.is_element_visible(self.SIGN_IN_LINK, timeout=2000)
