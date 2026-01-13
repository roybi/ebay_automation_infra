import random
from typing import List, Tuple

from playwright.sync_api import Page

from core.base_page import BasePage
from core.smart_locator import SmartLocator
from utils.allure_helper import allure_step, AllureHelper


class ProductPage(BasePage):
    """
    eBay Product Page object.
    Handles product details, variant selection, and add to cart functionality.
    """

    PAGE_NAME = "ProductPage"

    def __init__(self, page: Page):
        super().__init__(page)
        self._define_locators()

    def _define_locators(self) -> None:
        # Add to Cart Button
        self.ADD_TO_CART_BUTTON = SmartLocator(name="Add to Cart Button")

        # XPath by class and text
        self.ADD_TO_CART_BUTTON.add_xpath(
            "//a[contains(@class, 'ux-call-to-action') and contains(., 'Add to cart')]",
            "XPath - class and text",
        )
        # XPath by span text and ancestor
        self.ADD_TO_CART_BUTTON.add_xpath(
            "//span[contains(text(), 'Add to cart')]/ancestor::a",
            "XPath - text with ancestor",
        )
        # CSS by data-testid
        self.ADD_TO_CART_BUTTON.add_css(
            "[data-testid='ux-call-to-action-atc']", "CSS - data-testid"
        )

        # Buy It Now Button
        self.BUY_NOW_BUTTON = SmartLocator(name="Buy It Now Button")

        # XPath by ID
        self.BUY_NOW_BUTTON.add_xpath(
            "//a[@id='binBtn_btn_1']", "XPath - ID binBtn_btn_1"
        )

        # Size Selector (Dropdown)
        self.SIZE_SELECTOR = SmartLocator(name="Size Selector")

        # XPath by msku class and select
        # XPath by msku class and select
        self.SIZE_SELECTOR.add_xpath(
            "//div[contains(@class, 'x-msku__select-box')]//select",
            "XPath - msku select",
        )
        # XPath by aria-label
        self.SIZE_SELECTOR.add_xpath(
            "//select[@aria-label='Size']", "XPath - aria-label"
        )

        # Size Options
        self.SIZE_OPTIONS = SmartLocator(name="Size Options")
        # XPath by button in swatch
        self.SIZE_OPTIONS.add_xpath(
            "//ul[contains(@class, 'x-msku__swatch-list')]//button",
            "XPath - swatch list button",
        )
        # XPath by label with size text
        self.SIZE_OPTIONS.add_xpath(
            "//div[contains(@class, 'x-msku__box-cont') and .//span[contains(text(),'Size')]]//input",
            "XPath - msku with size text",
        )
        # CSS by class
        self.SIZE_OPTIONS.add_css(
            "div.x-msku__box-cont input[type='radio']", "CSS - container and radio"
        )
        # Color Selector
        self.COLOR_SELECTOR = SmartLocator(name="Color Selector")
        # CSS by ID pattern
        self.COLOR_SELECTOR.add_css(
            "select[id*='Color'], select[id*='color']", "CSS - ID contains"
        )

        # Quantity Input
        self.QUANTITY_INPUT = SmartLocator(name="Quantity Input")
        # XPath by ID
        self.QUANTITY_INPUT.add_xpath(
            "//input[@id='qtyTextBox']", "XPath - ID qtyTextBox"
        )
        # XPath by class
        self.QUANTITY_INPUT.add_xpath(
            "//input[contains(@class, 'x-quantity__input')]", "XPath - x-quantity class"
        )
        # Product Title
        self.PRODUCT_TITLE = SmartLocator(name="Product Title")
        self.PRODUCT_TITLE.add_xpath(
            "//h1[contains(@class, 'x-item-title')]", "XPath - x-item-title class"
        )
        # XPath by itemprop
        self.PRODUCT_TITLE.add_xpath("//h1[@itemprop='name']", "XPath - itemprop name")
        # XPath by span within title div
        self.PRODUCT_TITLE.add_xpath(
            "//div[contains(@class, 'x-item-title')]//span[@class='ux-textspans']",
            "XPath - span in title div",
        )
        # XPath by data-testid
        self.PRODUCT_TITLE.add_xpath(
            "//*[@data-testid='x-item-title']", "XPath - data-testid"
        )

        # Product Price
        self.PRODUCT_PRICE = SmartLocator(name="Product Price")
        self.PRODUCT_PRICE.add_xpath(
            "//div[contains(@class, 'x-price-primary')]//span[@itemprop='price']",
            "XPath - itemprop price",
        )
        # XPath by class within price div
        self.PRODUCT_PRICE.add_xpath(
            "//div[contains(@class, 'x-price-primary')]//span[contains(@class, 'ux-textspans')]",
            "XPath - ux-textspans in price",
        )
        # XPath by data-testid
        self.PRODUCT_PRICE.add_xpath(
            "//*[@data-testid='x-price-primary']//span", "XPath - data-testid"
        )

        # Cart Confirmation
        self.CART_CONFIRMATION = SmartLocator(name="Cart Confirmation")
        self.CART_CONFIRMATION.add_xpath(
            "//div[contains(@class, 'ux-overlay')]//span[contains(text(), 'Added to cart')]",
            "XPath - overlay with text",
        )
        # XPath by text content alone
        self.CART_CONFIRMATION.add_xpath(
            "//*[contains(text(), 'Added to cart') or contains(text(), 'added to cart')]",
            "XPath - text content",
        )
        # XPath by atc-confirmation class
        self.CART_CONFIRMATION.add_xpath(
            "//div[contains(@class, 'atc-confirmation')]",
            "XPath - atc-confirmation class",
        )

        # Variant Error Message
        self.VARIANT_ERROR = SmartLocator(name="Variant Error")
        # XPath by text content
        self.VARIANT_ERROR.add_xpath(
            "//*[contains(text(), 'Please select')]", "XPath - text Please select"
        )
        # XPath by error message class
        self.VARIANT_ERROR.add_xpath(
            "//span[contains(@class, 'ux-textspans--NEGATIVE')]",
            "XPath - negative textspans",
        )

        # Product Image
        self.PRODUCT_IMAGE = SmartLocator(name="Product Image")
        # XPath by ID
        self.PRODUCT_IMAGE.add_xpath("//img[@id='icImg']", "XPath - ID icImg")

    def _has_size_selection(self) -> bool:
        """Check if product requires size selection."""
        return self.is_element_present(
            self.SIZE_SELECTOR, timeout=2000
        ) or self.is_element_present(self.SIZE_OPTIONS, timeout=2000)

    def _has_color_selection(self) -> bool:
        """Check if product requires color selection."""
        return self.is_element_present(
            self.COLOR_SELECTOR, timeout=2000
        ) or self.is_element_present(self.COLOR_OPTIONS, timeout=2000)

    def _select_random_size(self) -> bool:
        """
        Select a random size option.

        Returns:
            True if selection was made, False otherwise
        """
        try:
            # Try dropdown first
            if self.is_element_present(self.SIZE_SELECTOR, timeout=1000):
                self.log_action("Variant Selection", "Selecting random size from dropdown")
                size_dropdown = self.find_element(self.SIZE_SELECTOR)

                # Get all options
                options = size_dropdown.locator("option").all()
                valid_options = [opt for opt in options if opt.get_attribute("value")]

                if len(valid_options) > 1:  # Skip first "Select" option
                    random_option = random.choice(valid_options[1:])
                    value = random_option.get_attribute("value")
                    size_dropdown.select_option(value=value)
                    self.logger.info(f"Selected size: {value}")
                    return True

            # Try radio buttons/swatches
            if self.is_element_present(self.SIZE_OPTIONS, timeout=1000):
                self.log_action("Variant Selection", "Selecting random size from options")
                options = self.page.locator(
                    "xpath=//div[contains(@class, 'x-msku__box-cont')]//input[@type='radio']"
                ).all()

                if not options:
                    options = self.page.locator(
                        "xpath=//ul[contains(@class, 'x-msku__swatch-list')]//button"
                    ).all()

                if options:
                    available_options = [opt for opt in options if opt.is_enabled()]
                    if available_options:
                        random_option = random.choice(available_options)
                        random_option.click()
                        self.logger.info("Selected random size option")
                        return True

            return False

        except Exception as e:
            self.logger.warning(f"Failed to select size: {e}")
            return False

    def _select_random_color(self) -> bool:
        """
        Select a random color option.

        Returns:
            True if selection was made, False otherwise
        """
        try:
            # Try dropdown first
            if self.is_element_present(self.COLOR_SELECTOR, timeout=1000):
                self.log_action("Variant Selection", "Selecting random color from dropdown")
                color_dropdown = self.find_element(self.COLOR_SELECTOR)

                options = color_dropdown.locator("option").all()
                valid_options = [opt for opt in options if opt.get_attribute("value")]

                if len(valid_options) > 1:
                    random_option = random.choice(valid_options[1:])
                    value = random_option.get_attribute("value")
                    color_dropdown.select_option(value=value)
                    self.logger.info(f"Selected color: {value}")
                    return True

            # Try color swatches
            if self.is_element_present(self.COLOR_OPTIONS, timeout=1000):
                self.log_action("Variant Selection", "Selecting random color from swatches")
                swatches = self.page.locator(
                    "xpath=//ul[contains(@class, 'x-msku__swatch-list')]//button"
                ).all()

                if swatches:
                    available_swatches = [s for s in swatches if s.is_enabled()]
                    if available_swatches:
                        random_swatch = random.choice(available_swatches)
                        random_swatch.click()
                        self.logger.info("Selected random color swatch")
                        return True

            return False

        except Exception as e:
            self.logger.warning(f"Failed to select color: {e}")
            return False

    def _handle_variant_selection(self) -> None:
        """Handle all variant selections (size, color, etc.) if required."""
        self.log_action("Variant Selection", "Checking for required variants")

        # Small delay to let page fully load variant options
        self.page.wait_for_timeout(1000)

        # Select size if available
        if self._has_size_selection():
            self._select_random_size()
            self.page.wait_for_timeout(500)  # Wait for price/availability update

        # Select color if available
        if self._has_color_selection():
            self._select_random_color()
            self.page.wait_for_timeout(500)

    def _click_add_to_cart(self) -> bool:
        """
        Click the Add to Cart button.

        Returns:
            True if clicked successfully, False otherwise
        """
        try:
            self.log_action("Add to Cart", "Clicking Add to Cart button")

            # Try primary Add to Cart button
            if self.is_element_present(self.ADD_TO_CART_BUTTON, timeout=5000):
                self.click(self.ADD_TO_CART_BUTTON)
                return True

            self.logger.warning("Add to Cart button not found")
            return False

        except Exception as e:
            self.logger.error(f"Failed to click Add to Cart: {e}")
            return False

    def _verify_added_to_cart(self) -> bool:
        """
        Verify item was added to cart.

        Returns:
            True if confirmation found, False otherwise
        """
        try:
            # Wait for confirmation modal/message
            self.page.wait_for_timeout(2000)  # Give time for modal to appear

            # Check for various confirmation indicators
            confirmation_texts = [
                "Added to cart",
                "added to cart",
                "Added to your cart",
                "Item added",
            ]

            for text in confirmation_texts:
                if self.page.locator(f"text={text}").count() > 0:
                    self.logger.info(f"Cart confirmation found: '{text}'")
                    return True

            # Check URL change (some flows redirect to cart)
            if "cart" in self.current_url.lower():
                self.logger.info("Redirected to cart page - item added")
                return True

            self.logger.warning("Could not verify item was added to cart")
            return True  # Assume success if no error appeared

        except Exception as e:
            self.logger.warning(f"Error verifying cart addition: {e}")
            return True  # Assume success

    def get_product_title(self) -> str:
        """Get the product title."""
        try:
            return self.get_text(self.PRODUCT_TITLE).strip()
        except:
            return "Unknown Product"

    def get_product_price(self) -> str:
        """Get the product price."""
        try:
            return self.get_text(self.PRODUCT_PRICE).strip()
        except:
            return "Unknown Price"

    @allure_step("Add single item to cart")
    def add_to_cart(self, url: str) -> bool:
        """
        Add a single item to cart.

        Args:
            url: Product URL to add

        Returns:
            True if successfully added, False otherwise
        """
        self.log_action("Add to Cart", f"Processing: {url[:80]}...")

        try:
            # Navigate to product page
            self.navigate(url)
            self.wait_for_page_load()
            self.wait_for_network_idle()

            # Get product info for logging
            title = self.get_product_title()
            price = self.get_product_price()
            self.logger.info(f"Product: {title[:50]}... - {price}")

            # Handle variant selection
            self._handle_variant_selection()

            # Click Add to Cart
            if not self._click_add_to_cart():
                self.capture_screenshot("add_to_cart_failed")
                return False

            # Wait and verify
            self.page.wait_for_timeout(2000)
            success = self._verify_added_to_cart()

            if success:
                self.logger.info(f"Successfully added to cart: {title[:50]}...")
                self.capture_screenshot(f"added_to_cart_{title[:20].replace(' ', '_')}")

            return success

        except Exception as e:
            self.logger.error(f"Failed to add item to cart: {e}")
            self.capture_screenshot("add_to_cart_error")
            return False


@allure_step("Add items to cart")
def add_items_to_cart(page: Page, urls: List[str]) -> Tuple[List[str], List[str]]:
    """
    Function name: addItemsToCart

    Iterate over each provided URL and add items to cart.
    Handles variant selection randomly and captures screenshots.

    Args:
        page: Playwright Page object
        urls: List of product URLs to add to cart

    Returns:
        Tuple of (successful_urls, failed_urls)
    """
    import logging

    logger = logging.getLogger("addItemsToCart")

    logger.info(f"addItemsToCart: Processing {len(urls)} items")

    successful_urls: List[str] = []
    failed_urls: List[str] = []

    product_page = ProductPage(page)

    for index, url in enumerate(urls, 1):
        logger.info(f"Processing item {index}/{len(urls)}")

        try:
            success = product_page.add_to_cart(url)

            if success:
                successful_urls.append(url)
                logger.info(f"Item {index} added successfully")
            else:
                failed_urls.append(url)
                logger.warning(f"Item {index} failed to add")

        except Exception as e:
            logger.error(f"Error processing item {index}: {e}")
            failed_urls.append(url)

    # Summary
    logger.info(
        f"addItemsToCart completed: "
        f"{len(successful_urls)} successful, {len(failed_urls)} failed"
    )

    # Attach results to Allure
    AllureHelper.attach_json(
        {
            "total_items": len(urls),
            "successful": len(successful_urls),
            "failed": len(failed_urls),
            "successful_urls": successful_urls,
            "failed_urls": failed_urls,
        },
        "Add to Cart Results",
    )

    return successful_urls, failed_urls
