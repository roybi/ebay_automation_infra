"""
Unit tests for assertCartTotalNotExceeds function.
Tests cart total validation and budget assertion.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from playwright.sync_api import Page

from pages.cart_page import CartPage, assert_cart_total_not_exceeds


class TestAssertCartTotalNotExceeds:
    """Unit tests for assertCartTotalNotExceeds function."""

    @pytest.fixture
    def mock_page(self):
        """Create a mock Playwright Page object."""
        page = Mock(spec=Page)
        page.wait_for_timeout = Mock()
        page.locator = Mock()
        page.url = "https://cart.ebay.com"
        return page

    @pytest.fixture
    def cart_page(self, mock_page):
        """Create CartPage with mocked page."""
        with patch.object(CartPage, '_define_locators'):
            cart_page = CartPage(mock_page)
            cart_page.logger = Mock()
            cart_page.log_action = Mock()
            cart_page.capture_screenshot = Mock()
            cart_page.navigate = Mock()
            cart_page.wait_for_page_load = Mock()
            cart_page.wait_for_network_idle = Mock()
            return cart_page

    def test_parse_price_valid(self, cart_page):
        """Test parsing valid price strings."""
        assert cart_page._parse_price("$220.00") == 220.0
        assert cart_page._parse_price("$1,220.50") == 1220.5
        assert cart_page._parse_price("220") == 220.0
        assert cart_page._parse_price("$99.99") == 99.99

    def test_parse_price_invalid(self, cart_page):
        """Test parsing invalid price strings."""
        assert cart_page._parse_price("") is None
        assert cart_page._parse_price("invalid") is None
        assert cart_page._parse_price("$abc") is None

    def test_assert_cart_total_within_budget(self, cart_page):
        """Test assertion passes when cart total is within budget."""
        cart_page.navigate_to_cart = Mock()
        cart_page.is_cart_empty = Mock(return_value=False)
        cart_page.get_cart_subtotal = Mock(return_value=800.0)
        cart_page.get_cart_item_count = Mock(return_value=4)

        passed, details = cart_page.assert_cart_total_not_exceeds(
            budget_per_item=220.0,
            items_count=4
        )

        assert passed is True
        assert details['assertion_passed'] is True
        assert details['actual_total'] == 800.0
        assert details['expected_max_total'] == 880.0  # 220 * 4
        assert details['items_count'] == 4

    def test_assert_cart_total_exceeds_budget(self, cart_page):
        """Test assertion fails when cart total exceeds budget."""
        cart_page.navigate_to_cart = Mock()
        cart_page.is_cart_empty = Mock(return_value=False)
        cart_page.get_cart_subtotal = Mock(return_value=1000.0)
        cart_page.get_cart_item_count = Mock(return_value=4)

        passed, details = cart_page.assert_cart_total_not_exceeds(
            budget_per_item=220.0,
            items_count=4
        )

        assert passed is False
        assert details['assertion_passed'] is False
        assert details['actual_total'] == 1000.0
        assert details['expected_max_total'] == 880.0
        assert "exceeds budget" in details['reason']

    def test_assert_cart_total_exactly_at_budget(self, cart_page):
        """Test assertion passes when cart total equals budget exactly."""
        cart_page.navigate_to_cart = Mock()
        cart_page.is_cart_empty = Mock(return_value=False)
        cart_page.get_cart_subtotal = Mock(return_value=880.0)
        cart_page.get_cart_item_count = Mock(return_value=4)

        passed, details = cart_page.assert_cart_total_not_exceeds(
            budget_per_item=220.0,
            items_count=4
        )

        assert passed is True
        assert details['assertion_passed'] is True
        assert details['actual_total'] == 880.0
        assert details['expected_max_total'] == 880.0

    def test_assert_cart_is_empty(self, cart_page):
        """Test assertion fails when cart is empty."""
        cart_page.navigate_to_cart = Mock()
        cart_page.is_cart_empty = Mock(return_value=True)

        passed, details = cart_page.assert_cart_total_not_exceeds(
            budget_per_item=220.0,
            items_count=5
        )

        assert passed is False
        assert details['assertion_passed'] is False
        assert details['reason'] == "Cart is empty"
        assert details['actual_total'] == 0

    def test_assert_cart_total_not_found(self, cart_page):
        """Test assertion fails when cart total cannot be retrieved."""
        cart_page.navigate_to_cart = Mock()
        cart_page.is_cart_empty = Mock(return_value=False)
        cart_page.get_cart_subtotal = Mock(return_value=None)
        cart_page.get_cart_item_count = Mock(return_value=4)

        passed, details = cart_page.assert_cart_total_not_exceeds(
            budget_per_item=220.0,
            items_count=4
        )

        assert passed is False
        assert details['assertion_passed'] is False
        assert "Could not retrieve cart total" in details['reason']
        assert details['actual_total'] is None

    def test_get_cart_subtotal_success(self, cart_page):
        """Test getting cart subtotal successfully."""
        cart_page.is_element_present = Mock(return_value=True)
        cart_page.get_text = Mock(return_value="$450.00")

        total = cart_page.get_cart_subtotal()

        assert total == 450.0

    def test_get_cart_subtotal_not_found(self, cart_page, mock_page):
        """Test getting cart subtotal when element not found."""
        cart_page.is_element_present = Mock(return_value=False)
        mock_locator = Mock()
        mock_locator.all.return_value = []
        mock_page.locator.return_value = mock_locator

        total = cart_page.get_cart_subtotal()

        assert total is None

    def test_get_cart_item_count_from_element(self, cart_page):
        """Test getting item count from dedicated element."""
        cart_page.is_element_present = Mock(return_value=True)
        cart_page.get_text = Mock(return_value="5 items")

        count = cart_page.get_cart_item_count()

        assert count == 5

    def test_get_cart_item_count_from_fallback(self, cart_page, mock_page):
        """Test getting item count from fallback method."""
        cart_page.is_element_present = Mock(return_value=False)

        # Mock cart items
        mock_items = [Mock(), Mock(), Mock()]
        mock_locator = Mock()
        mock_locator.all.return_value = mock_items
        mock_page.locator.return_value = mock_locator

        count = cart_page.get_cart_item_count()

        assert count == 3

    def test_get_cart_item_count_no_items(self, cart_page, mock_page):
        """Test getting item count when no items found."""
        cart_page.is_element_present = Mock(return_value=False)
        mock_locator = Mock()
        mock_locator.all.return_value = []
        mock_page.locator.return_value = mock_locator

        count = cart_page.get_cart_item_count()

        assert count == 0

    def test_is_cart_empty_true(self, cart_page):
        """Test checking if cart is empty when it is."""
        cart_page.is_element_present = Mock(return_value=True)

        result = cart_page.is_cart_empty()

        assert result is True

    def test_is_cart_empty_false(self, cart_page):
        """Test checking if cart is empty when it's not."""
        cart_page.is_element_present = Mock(return_value=False)

        result = cart_page.is_cart_empty()

        assert result is False

    def test_navigate_to_cart_direct_url(self, cart_page):
        """Test navigating to cart using direct URL."""
        type(cart_page).current_url = property(lambda self: "https://cart.ebay.com")

        cart_page.navigate_to_cart()

        cart_page.navigate.assert_called()
        cart_page.wait_for_page_load.assert_called()

    def test_standalone_function(self, mock_page):
        """Test the standalone function wrapper."""
        with patch('pages.cart_page.CartPage') as MockCartPage:
            mock_instance = Mock()
            mock_instance.assert_cart_total_not_exceeds.return_value = (True, {"key": "value"})
            MockCartPage.return_value = mock_instance

            passed, details = assert_cart_total_not_exceeds(mock_page, 220.0, 5)

            assert passed is True
            assert details == {"key": "value"}
            mock_instance.assert_cart_total_not_exceeds.assert_called_once_with(220.0, 5)

    def test_assert_captures_screenshots(self, cart_page):
        """Test that assertion captures screenshots at key points."""
        cart_page.navigate_to_cart = Mock()
        cart_page.is_cart_empty = Mock(return_value=False)
        cart_page.get_cart_subtotal = Mock(return_value=800.0)
        cart_page.get_cart_item_count = Mock(return_value=4)

        cart_page.assert_cart_total_not_exceeds(220.0, 4)

        # Should capture multiple screenshots
        assert cart_page.capture_screenshot.call_count >= 2

    def test_assert_with_zero_budget(self, cart_page):
        """Test assertion with zero budget per item."""
        cart_page.navigate_to_cart = Mock()
        cart_page.is_cart_empty = Mock(return_value=False)
        cart_page.get_cart_subtotal = Mock(return_value=100.0)
        cart_page.get_cart_item_count = Mock(return_value=4)

        passed, details = cart_page.assert_cart_total_not_exceeds(0, 4)

        assert passed is False
        assert details['expected_max_total'] == 0

    def test_assert_with_single_item(self, cart_page):
        """Test assertion with single item."""
        cart_page.navigate_to_cart = Mock()
        cart_page.is_cart_empty = Mock(return_value=False)
        cart_page.get_cart_subtotal = Mock(return_value=150.0)
        cart_page.get_cart_item_count = Mock(return_value=1)

        passed, details = cart_page.assert_cart_total_not_exceeds(220.0, 1)

        assert passed is True
        assert details['expected_max_total'] == 220.0

    def test_assert_difference_calculation(self, cart_page):
        """Test that difference is calculated correctly."""
        cart_page.navigate_to_cart = Mock()
        cart_page.is_cart_empty = Mock(return_value=False)
        cart_page.get_cart_subtotal = Mock(return_value=800.0)
        cart_page.get_cart_item_count = Mock(return_value=4)

        passed, details = cart_page.assert_cart_total_not_exceeds(220.0, 4)

        expected_max = 220.0 * 4  # 880.0
        expected_difference = expected_max - 800.0  # 80.0

        assert details['difference'] == expected_difference

    def test_remove_item_success(self, cart_page, mock_page):
        """Test removing an item from cart."""
        mock_items = [Mock(), Mock()]
        mock_remove_btn = Mock()
        mock_remove_btn.is_visible.return_value = True

        mock_items[0].locator.return_value.first = mock_remove_btn

        mock_locator = Mock()
        mock_locator.all.return_value = mock_items
        mock_page.locator.return_value = mock_locator

        result = cart_page.remove_item(0)

        assert result is True
        mock_remove_btn.click.assert_called_once()

    def test_remove_item_index_out_of_range(self, cart_page, mock_page):
        """Test removing item with invalid index."""
        mock_items = [Mock()]
        mock_locator = Mock()
        mock_locator.all.return_value = mock_items
        mock_page.locator.return_value = mock_locator

        result = cart_page.remove_item(5)

        assert result is False

    def test_assert_attaches_to_allure(self, cart_page):
        """Test that assertion results are attached to Allure."""
        with patch('pages.cart_page.AllureHelper') as MockAllureHelper:
            cart_page.navigate_to_cart = Mock()
            cart_page.is_cart_empty = Mock(return_value=False)
            cart_page.get_cart_subtotal = Mock(return_value=800.0)
            cart_page.get_cart_item_count = Mock(return_value=4)

            cart_page.assert_cart_total_not_exceeds(220.0, 4)

            MockAllureHelper.attach_json.assert_called()
