import re
from typing import Optional, Tuple

from playwright.sync_api import Page

from core.base_page import BasePage
from core.smart_locator import SmartLocator
from utils.allure_helper import AllureHelper, allure_step


class CartPage(BasePage):
    """
    eBay Shopping Cart Page object.
    Handles cart interactions and total validation.
    """

    PAGE_URL = "https://cart.ebay.com"
    PAGE_NAME = "CartPage"

    def __init__(self, page: Page):
        super().__init__(page)
        self._define_locators()

    def _define_locators(self) -> None:
        """Define all locators for this page with multiple fallback strategies."""

        # Cart Subtotal

        self.CART_SUBTOTAL = SmartLocator(name="Cart Subtotal")
        # XPath by data-test-id
        self.CART_SUBTOTAL.add_xpath(
            "//span[@data-test-id='SUBTOTAL']", "XPath - data-test-id SUBTOTAL"
        )
        # XPath by class containing subtotal and $
        self.CART_SUBTOTAL.add_xpath(
            "//span[contains(@class, 'subtotal')]//span[contains(text(), '$')]",
            "XPath - subtotal class with $",
        )

        # Cart Total

        self.CART_TOTAL = SmartLocator(name="Cart Total")
        # XPath by data-test-id
        self.CART_TOTAL.add_xpath(
            "//span[@data-test-id='TOTAL']", "XPath - data-test-id TOTAL"
        )
        # XPath by order-total class
        self.CART_TOTAL.add_xpath(
            "//div[contains(@class, 'order-total')]//span[contains(text(), '$')]",
            "XPath - order-total class",
        )

        # Item Count

        self.ITEM_COUNT = SmartLocator(name="Item Count")
        # XPath by data-test-id
        self.ITEM_COUNT.add_xpath(
            "//span[@data-test-id='ITEM_COUNT']", "XPath - data-test-id ITEM_COUNT"
        )
        # XPath by class
        self.ITEM_COUNT.add_xpath(
            "//span[contains(@class, 'item-count')]", "XPath - item-count class"
        )
        # XPath by text pattern (contains 'item')
        self.ITEM_COUNT.add_xpath(
            "//*[contains(text(), 'item') and contains(text(), '(')]",
            "XPath - text with item and (",
        )
        # XPath by header count
        self.ITEM_COUNT.add_xpath(
            "//h1[contains(@class, 'cart-header')]//span", "XPath - cart-header span"
        )
        # CSS by data-test-id
        self.ITEM_COUNT.add_css("span[data-test-id='ITEM_COUNT']", "CSS - data-test-id")
        # CSS by class
        self.ITEM_COUNT.add_css("span.item-count", "CSS - item-count class")

        # Cart Items List

        self.CART_ITEMS = SmartLocator(name="Cart Items")
        # XPath by data-test-id
        self.CART_ITEMS.add_xpath(
            "//*[@data-test-id='CART_ITEM']", "XPath - data-test-id CART_ITEM"
        )
        # XPath by class cart-item
        self.CART_ITEMS.add_xpath(
            "//div[contains(@class, 'cart-item')]", "XPath - cart-item class"
        )
        # XPath by item-details within li
        self.CART_ITEMS.add_xpath(
            "//li[contains(@class, 'item')]//div[contains(@class, 'item-details')]",
            "XPath - item with details",
        )
        # XPath by cart-bucket items
        self.CART_ITEMS.add_xpath(
            "//div[contains(@class, 'cart-bucket')]//div[contains(@class, 'item')]",
            "XPath - cart-bucket item",
        )
        # CSS by data-test-id
        self.CART_ITEMS.add_css("[data-test-id='CART_ITEM']", "CSS - data-test-id")
        # CSS by class
        self.CART_ITEMS.add_css("div.cart-item", "CSS - cart-item class")

        # Individual Item Price (within cart item)

        self.ITEM_PRICE = SmartLocator(name="Item Price")
        # XPath by data-test-id
        self.ITEM_PRICE.add_xpath(
            ".//span[@data-test-id='ITEM_PRICE']", "XPath - data-test-id ITEM_PRICE"
        )
        # XPath by class
        self.ITEM_PRICE.add_xpath(
            ".//span[contains(@class, 'item-price')]//span[contains(text(), '$')]",
            "XPath - item-price class",
        )
        # XPath by text pattern
        self.ITEM_PRICE.add_xpath(
            ".//span[starts-with(normalize-space(text()), '$')]",
            "XPath - starts with $",
        )
        # CSS by data-test-id
        self.ITEM_PRICE.add_css("span[data-test-id='ITEM_PRICE']", "CSS - data-test-id")
        # CSS by class
        self.ITEM_PRICE.add_css("span.item-price span", "CSS - item-price span")

        # Item Title (within cart item)

        self.ITEM_TITLE = SmartLocator(name="Item Title")
        # XPath by data-test-id
        self.ITEM_TITLE.add_xpath(
            ".//span[@data-test-id='ITEM_TITLE']", "XPath - data-test-id ITEM_TITLE"
        )
        # XPath by class
        self.ITEM_TITLE.add_xpath(
            ".//span[contains(@class, 'item-title')]", "XPath - item-title class"
        )
        # XPath by link with title
        self.ITEM_TITLE.add_xpath(
            ".//a[contains(@class, 'item-title')]", "XPath - item-title link"
        )
        # CSS by data-test-id
        self.ITEM_TITLE.add_css("span[data-test-id='ITEM_TITLE']", "CSS - data-test-id")
        # CSS by class
        self.ITEM_TITLE.add_css("span.item-title", "CSS - item-title class")

        # Remove Item Button (within cart item)

        self.REMOVE_ITEM_BUTTON = SmartLocator(name="Remove Item Button")
        # XPath by data-test-id
        self.REMOVE_ITEM_BUTTON.add_xpath(
            ".//button[@data-test-id='REMOVE']", "XPath - data-test-id REMOVE"
        )
        # XPath by text
        self.REMOVE_ITEM_BUTTON.add_xpath(
            ".//button[contains(text(), 'Remove')]", "XPath - text Remove"
        )
        # XPath by aria-label
        self.REMOVE_ITEM_BUTTON.add_xpath(
            ".//button[@aria-label='Remove']", "XPath - aria-label"
        )
        # XPath by class
        self.REMOVE_ITEM_BUTTON.add_xpath(
            ".//button[contains(@class, 'remove')]", "XPath - remove class"
        )
        # CSS by data-test-id
        self.REMOVE_ITEM_BUTTON.add_css(
            "button[data-test-id='REMOVE']", "CSS - data-test-id"
        )
        # CSS by aria-label
        self.REMOVE_ITEM_BUTTON.add_css(
            "button[aria-label='Remove']", "CSS - aria-label"
        )

        # Empty Cart Message

        self.EMPTY_CART = SmartLocator(name="Empty Cart Message")
        # XPath by text content (empty)
        self.EMPTY_CART.add_xpath(
            "//*[contains(text(), 'empty') or contains(text(), 'Empty')]",
            "XPath - text empty",
        )
        # XPath by class
        self.EMPTY_CART.add_xpath(
            "//div[contains(@class, 'empty-cart')]", "XPath - empty-cart class"
        )
        # XPath by no items message
        self.EMPTY_CART.add_xpath(
            "//*[contains(text(), 'no items') or contains(text(), 'No items')]",
            "XPath - no items text",
        )
        # XPath by data-test-id
        self.EMPTY_CART.add_xpath(
            "//*[@data-test-id='EMPTY_CART']", "XPath - data-test-id"
        )
        # CSS by class
        self.EMPTY_CART.add_css("div.empty-cart", "CSS - empty-cart class")
        # CSS by data-test-id
        self.EMPTY_CART.add_css("[data-test-id='EMPTY_CART']", "CSS - data-test-id")

        # -------  Checkout Button

        self.CHECKOUT_BUTTON = SmartLocator(name="Checkout Button")
        # XPath by data-test-id
        self.CHECKOUT_BUTTON.add_xpath(
            "//button[@data-test-id='CHECKOUT_BUTTON']", "XPath - data-test-id"
        )
        # XPath by text content
        self.CHECKOUT_BUTTON.add_xpath(
            "//button[contains(text(), 'Checkout') or contains(text(), 'checkout')]",
            "XPath - text Checkout",
        )
        # XPath by link href
        self.CHECKOUT_BUTTON.add_xpath(
            "//a[contains(@href, 'checkout')]", "XPath - href checkout"
        )
        # XPath by class
        self.CHECKOUT_BUTTON.add_xpath(
            "//button[contains(@class, 'checkout')]", "XPath - checkout class"
        )
        # XPath by call-to-action class
        self.CHECKOUT_BUTTON.add_xpath(
            "//button[contains(@class, 'call-to-action')]",
            "XPath - call-to-action class",
        )
        # CSS by data-test-id
        self.CHECKOUT_BUTTON.add_css(
            "button[data-test-id='CHECKOUT_BUTTON']", "CSS - data-test-id"
        )
        # CSS by href
        self.CHECKOUT_BUTTON.add_css("a[href*='checkout']", "CSS - href checkout")
        # CSS by class
        self.CHECKOUT_BUTTON.add_css("button.checkout-btn", "CSS - checkout-btn class")

        # --------  Continue Shopping Link

        self.CONTINUE_SHOPPING = SmartLocator(name="Continue Shopping")
        # XPath by text
        self.CONTINUE_SHOPPING.add_xpath(
            "//a[contains(text(), 'Continue shopping')]", "XPath - text content"
        )
        # XPath by href to homepage
        self.CONTINUE_SHOPPING.add_xpath(
            "//a[contains(@href, 'ebay.com') and not(contains(@href, 'cart'))]",
            "XPath - homepage href",
        )
        # CSS by text
        self.CONTINUE_SHOPPING.add_css(
            "a[href*='ebay.com']:not([href*='cart'])", "CSS - homepage link"
        )

        # ----------- Quantity Selector (within cart item)
        self.QUANTITY_SELECTOR = SmartLocator(name="Quantity Selector")
        # XPath by data-test-id
        self.QUANTITY_SELECTOR.add_xpath(
            ".//select[@data-test-id='QTY_SELECT']", "XPath - data-test-id"
        )
        # XPath by name
        self.QUANTITY_SELECTOR.add_xpath(
            ".//select[@name='quantity']", "XPath - name quantity"
        )
        # XPath by aria-label
        self.QUANTITY_SELECTOR.add_xpath(
            ".//select[@aria-label='Quantity']", "XPath - aria-label"
        )
        # XPath by class
        self.QUANTITY_SELECTOR.add_xpath(
            ".//select[contains(@class, 'qty')]", "XPath - qty class"
        )
        # CSS by data-test-id
        self.QUANTITY_SELECTOR.add_css(
            "select[data-test-id='QTY_SELECT']", "CSS - data-test-id"
        )
        # CSS by name
        self.QUANTITY_SELECTOR.add_css(
            "select[name='quantity']", "CSS - name attribute"
        )

    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Parse price from text string.
        Returns:
            Float price value or None if parsing fails
        """
        try:
            cleaned = price_text.strip()
            match = re.search(r"[\d,]+\.?\d*", cleaned)
            if match:
                price_str = match.group().replace(",", "")
                return float(price_str)
            return None
        except Exception as e:
            self.logger.warning(f"Failed to parse price '{price_text}': {e}")
            return None

    @allure_step("Navigate to cart")
    def navigate_to_cart(self) -> None:
        """Navigate to the shopping cart page."""
        self.log_action("Navigation", "Going to shopping cart")

        # Try direct cart URL
        cart_urls = [
            "https://cart.ebay.com",
            "https://www.ebay.com/sc/atc",
            "https://www.ebay.com/atc/myatc",
        ]

        for url in cart_urls:
            try:
                self.navigate(url)
                self.wait_for_page_load()

                # Verify we're on cart page
                if (
                    "cart" in self.current_url.lower()
                    or "atc" in self.current_url.lower()
                ):
                    self.logger.info(
                        f"Successfully navigated to cart: {self.current_url}"
                    )
                    return
            except Exception as e:
                self.logger.debug(f"Failed to navigate to {url}: {e}")
                continue

        # Fallback: click cart icon from any page
        try:
            cart_selectors = [
                "xpath=//a[@id='gh-cart-n']",
                "xpath=//a[contains(@href, 'cart')]",
                "css=#gh-cart-n",
                "css=a[href*='cart']",
            ]

            for selector in cart_selectors:
                try:
                    cart_icon = self.page.locator(selector).first
                    if cart_icon.is_visible():
                        cart_icon.click()
                        self.wait_for_page_load()
                        self.logger.info("Navigated to cart via cart icon")
                        return
                except:
                    continue

        except Exception as e:
            self.logger.error(f"Failed to navigate to cart: {e}")

    def is_cart_empty(self) -> bool:
        """Check if cart is empty."""
        try:
            return self.is_element_present(self.EMPTY_CART, timeout=2000)
        except:
            return False

    def get_cart_subtotal(self) -> Optional[float]:
        """
        Get the cart subtotal amount.

        Returns:
            Float subtotal value or None if not found
        """
        try:
            # Try subtotal first
            if self.is_element_present(self.CART_SUBTOTAL, timeout=3000):
                subtotal_text = self.get_text(self.CART_SUBTOTAL)
                subtotal = self._parse_price(subtotal_text)
                if subtotal is not None:
                    self.logger.info(f"Cart subtotal: ${subtotal}")
                    return subtotal

            # Try total as fallback
            if self.is_element_present(self.CART_TOTAL, timeout=3000):
                total_text = self.get_text(self.CART_TOTAL)
                total = self._parse_price(total_text)
                if total is not None:
                    self.logger.info(f"Cart total: ${total}")
                    return total

            # Try to find any price-like element in the summary area
            price_selectors = [
                "xpath=//*[contains(@class, 'subtotal')]//span[contains(text(), '$')]",
                "xpath=//*[contains(@class, 'total')]//span[contains(text(), '$')]",
                "xpath=//span[contains(text(), '$') and ancestor::div[contains(@class, 'summary')]]",
            ]

            for selector in price_selectors:
                try:
                    elements = self.page.locator(selector).all()
                    for elem in elements:
                        text = elem.text_content()
                        if text and "$" in text:
                            price = self._parse_price(text)
                            if price and price > 0:
                                self.logger.info(f"Found price via fallback: ${price}")
                                return price
                except:
                    continue

            self.logger.warning("Could not find cart subtotal/total")
            return None

        except Exception as e:
            self.logger.error(f"Error getting cart subtotal: {e}")
            return None

    def get_cart_item_count(self) -> int:
        """
        Get the number of items in cart.

        Returns:
            Number of items or 0 if not found
        """
        try:
            if self.is_element_present(self.ITEM_COUNT, timeout=2000):
                count_text = self.get_text(self.ITEM_COUNT)
                match = re.search(r"\d+", count_text)
                if match:
                    return int(match.group())

            # Count cart items as fallback
            cart_item_selectors = [
                "xpath=//div[contains(@class, 'cart-item')]",
                "xpath=//*[@data-test-id='CART_ITEM']",
                "css=div.cart-item",
            ]

            for selector in cart_item_selectors:
                try:
                    items = self.page.locator(selector).all()
                    if items:
                        return len(items)
                except:
                    continue

            return 0

        except Exception as e:
            self.logger.warning(f"Error getting cart item count: {e}")
            return 0

    @allure_step("Assert cart total does not exceed budget")
    def assert_cart_total_not_exceeds(
        self, budget_per_item: float, items_count: int
    ) -> Tuple[bool, dict]:
        """

        Validates that the cart total does not exceed the calculated threshold.
        Returns:
            Tuple of (assertion_passed: bool, details: dict)
        """
        self.log_action(
            "assertCartTotalNotExceeds",
            f"Budget per item: ${budget_per_item}, Items: {items_count}",
        )

        # Navigate to cart
        self.navigate_to_cart()
        self.wait_for_page_load()
        self.wait_for_network_idle()

        # Take screenshot of cart page
        self.capture_screenshot("cart_page_before_assertion")

        # Check if cart is empty
        if self.is_cart_empty():
            self.logger.error("Cart is empty!")
            self.capture_screenshot("cart_empty")

            result = {
                "assertion_passed": False,
                "reason": "Cart is empty",
                "expected_max_total": budget_per_item * items_count,
                "actual_total": 0,
                "items_count": 0,
                "cart_url": self.current_url,
            }

            AllureHelper.attach_json(result, "Assertion Result")
            return False, result

        # Get cart subtotal
        cart_total = self.get_cart_subtotal()
        cart_items = self.get_cart_item_count()

        # Calculate threshold
        max_allowed = budget_per_item * items_count

        self.logger.info(f"Cart Total: ${cart_total}")
        self.logger.info(
            f"Maximum Allowed: ${max_allowed} (${budget_per_item} x {items_count})"
        )
        self.logger.info(f"Cart Item Count: {cart_items}")

        # Handle case where total couldn't be found
        if cart_total is None:
            self.logger.error("Could not retrieve cart total!")
            self.capture_screenshot("cart_total_not_found")

            result = {
                "assertion_passed": False,
                "reason": "Could not retrieve cart total",
                "expected_max_total": max_allowed,
                "actual_total": None,
                "items_count": cart_items,
                "cart_url": self.current_url,
            }

            AllureHelper.attach_json(result, "Assertion Result")
            return False, result

        # Perform assertion
        assertion_passed = cart_total <= max_allowed

        result = {
            "assertion_passed": assertion_passed,
            "expected_max_total": max_allowed,
            "actual_total": cart_total,
            "difference": max_allowed - cart_total,
            "items_count": cart_items,
            "budget_per_item": budget_per_item,
            "cart_url": self.current_url,
        }

        if assertion_passed:
            self.logger.info(
                f"ASSERTION PASSED: Cart total ${cart_total} <= "
                f"Max allowed ${max_allowed}"
            )
            result["reason"] = "Cart total is within budget"
            self.capture_screenshot("assertion_passed")
        else:
            self.logger.error(
                f"ASSERTION FAILED: Cart total ${cart_total} > "
                f"Max allowed ${max_allowed}"
            )
            result["reason"] = (
                f"Cart total exceeds budget by ${cart_total - max_allowed:.2f}"
            )
            self.capture_screenshot("assertion_failed")

        # Attach results to Allure
        AllureHelper.attach_json(result, "Cart Assertion Result")

        # Final screenshot
        self.capture_screenshot("cart_page_final")

        return assertion_passed, result

    def remove_item(self, index: int = 0) -> bool:
        """
        Remove an item from cart by index.

        Returns:
            True if removed successfully
        """
        try:
            items = self.page.locator(
                "xpath=//div[contains(@class, 'cart-item')]"
            ).all()
            if index < len(items):
                remove_btn = (
                    items[index]
                    .locator("xpath=.//button[contains(text(), 'Remove')]")
                    .first
                )
                if remove_btn.is_visible():
                    remove_btn.click()
                    self.wait_for_page_load()
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove item: {e}")
            return False


# Standalone function for use outside page object pattern
@allure_step("Assert cart total not exceeds")
def assert_cart_total_not_exceeds(
    page: Page, budget_per_item: float, items_count: int
) -> Tuple[bool, dict]:
    """

    Standalone function to validate cart total.

    Returns:
        Tuple of (assertion_passed: bool, details: dict)
    """
    cart_page = CartPage(page)
    return cart_page.assert_cart_total_not_exceeds(budget_per_item, items_count)
