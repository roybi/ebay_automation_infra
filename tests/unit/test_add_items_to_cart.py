"""
Unit tests for addItemsToCart function.
Tests adding items to cart with variant selection.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from playwright.sync_api import Page

from pages.product_page import ProductPage, add_items_to_cart


class TestAddItemsToCart:
    """Unit tests for addItemsToCart function."""

    @pytest.fixture
    def mock_page(self):
        """Create a mock Playwright Page object."""
        page = Mock(spec=Page)
        page.wait_for_timeout = Mock()
        page.locator = Mock()
        page.url = "https://www.ebay.com"
        return page

    @pytest.fixture
    def product_page(self, mock_page):
        """Create ProductPage with mocked page."""
        with patch.object(ProductPage, '_define_locators'):
            product_page = ProductPage(mock_page)
            product_page.logger = Mock()
            product_page.log_action = Mock()
            product_page.capture_screenshot = Mock()
            product_page.navigate = Mock()
            product_page.wait_for_page_load = Mock()
            product_page.wait_for_network_idle = Mock()
            return product_page

    def test_add_single_item_success(self, product_page, mock_page):
        """Test successfully adding a single item to cart."""
        url = "https://www.ebay.com/itm/12345"

        product_page.get_product_title = Mock(return_value="Test Product")
        product_page.get_product_price = Mock(return_value="$50.00")
        product_page._handle_variant_selection = Mock()
        product_page._click_add_to_cart = Mock(return_value=True)
        product_page._verify_added_to_cart = Mock(return_value=True)

        result = product_page.add_to_cart(url)

        assert result is True
        product_page.navigate.assert_called_once_with(url)
        product_page._handle_variant_selection.assert_called_once()
        product_page._click_add_to_cart.assert_called_once()
        product_page._verify_added_to_cart.assert_called_once()

    def test_add_single_item_button_not_found(self, product_page, mock_page):
        """Test when add to cart button is not found."""
        url = "https://www.ebay.com/itm/12345"

        product_page.get_product_title = Mock(return_value="Test Product")
        product_page.get_product_price = Mock(return_value="$50.00")
        product_page._handle_variant_selection = Mock()
        product_page._click_add_to_cart = Mock(return_value=False)

        result = product_page.add_to_cart(url)

        assert result is False
        product_page.capture_screenshot.assert_called()

    def test_add_single_item_with_exception(self, product_page, mock_page):
        """Test handling exception during add to cart."""
        url = "https://www.ebay.com/itm/12345"

        product_page.navigate = Mock(side_effect=Exception("Navigation failed"))

        result = product_page.add_to_cart(url)

        assert result is False
        product_page.capture_screenshot.assert_called_with("add_to_cart_error")

    def test_add_multiple_items_all_success(self, mock_page):
        """Test adding multiple items, all succeed."""
        urls = [
            "https://www.ebay.com/itm/1",
            "https://www.ebay.com/itm/2",
            "https://www.ebay.com/itm/3"
        ]

        with patch('pages.product_page.ProductPage') as MockProductPage:
            mock_instance = Mock()
            mock_instance.add_to_cart.return_value = True
            MockProductPage.return_value = mock_instance

            successful, failed = add_items_to_cart(mock_page, urls)

            assert len(successful) == 3
            assert len(failed) == 0
            assert mock_instance.add_to_cart.call_count == 3

    def test_add_multiple_items_some_fail(self, mock_page):
        """Test adding multiple items where some fail."""
        urls = [
            "https://www.ebay.com/itm/1",
            "https://www.ebay.com/itm/2",
            "https://www.ebay.com/itm/3"
        ]

        with patch('pages.product_page.ProductPage') as MockProductPage:
            mock_instance = Mock()
            # First succeeds, second fails, third succeeds
            mock_instance.add_to_cart.side_effect = [True, False, True]
            MockProductPage.return_value = mock_instance

            successful, failed = add_items_to_cart(mock_page, urls)

            assert len(successful) == 2
            assert len(failed) == 1
            assert urls[1] in failed

    def test_add_multiple_items_all_fail(self, mock_page):
        """Test adding multiple items where all fail."""
        urls = [
            "https://www.ebay.com/itm/1",
            "https://www.ebay.com/itm/2"
        ]

        with patch('pages.product_page.ProductPage') as MockProductPage:
            mock_instance = Mock()
            mock_instance.add_to_cart.return_value = False
            MockProductPage.return_value = mock_instance

            successful, failed = add_items_to_cart(mock_page, urls)

            assert len(successful) == 0
            assert len(failed) == 2

    def test_add_multiple_items_with_exceptions(self, mock_page):
        """Test adding items with exceptions during processing."""
        urls = [
            "https://www.ebay.com/itm/1",
            "https://www.ebay.com/itm/2"
        ]

        with patch('pages.product_page.ProductPage') as MockProductPage:
            mock_instance = Mock()
            # First succeeds, second raises exception
            mock_instance.add_to_cart.side_effect = [True, Exception("Error")]
            MockProductPage.return_value = mock_instance

            successful, failed = add_items_to_cart(mock_page, urls)

            assert len(successful) == 1
            assert len(failed) == 1

    def test_add_items_empty_list(self, mock_page):
        """Test adding items with empty URL list."""
        urls = []

        with patch('pages.product_page.ProductPage') as MockProductPage:
            mock_instance = Mock()
            MockProductPage.return_value = mock_instance

            successful, failed = add_items_to_cart(mock_page, urls)

            assert len(successful) == 0
            assert len(failed) == 0
            mock_instance.add_to_cart.assert_not_called()

    def test_variant_selection_has_size(self, product_page, mock_page):
        """Test variant selection when size is available."""
        product_page._has_size_selection = Mock(return_value=True)
        product_page._has_color_selection = Mock(return_value=False)
        product_page._select_random_size = Mock(return_value=True)

        product_page._handle_variant_selection()

        product_page._select_random_size.assert_called_once()
        assert mock_page.wait_for_timeout.called

    def test_variant_selection_has_color(self, product_page, mock_page):
        """Test variant selection when color is available."""
        product_page._has_size_selection = Mock(return_value=False)
        product_page._has_color_selection = Mock(return_value=True)
        product_page._select_random_color = Mock(return_value=True)

        product_page._handle_variant_selection()

        product_page._select_random_color.assert_called_once()

    def test_variant_selection_has_both(self, product_page, mock_page):
        """Test variant selection when both size and color are available."""
        product_page._has_size_selection = Mock(return_value=True)
        product_page._has_color_selection = Mock(return_value=True)
        product_page._select_random_size = Mock(return_value=True)
        product_page._select_random_color = Mock(return_value=True)

        product_page._handle_variant_selection()

        product_page._select_random_size.assert_called_once()
        product_page._select_random_color.assert_called_once()

    def test_variant_selection_none_available(self, product_page, mock_page):
        """Test variant selection when no variants are available."""
        product_page._has_size_selection = Mock(return_value=False)
        product_page._has_color_selection = Mock(return_value=False)

        product_page._handle_variant_selection()

        # Should complete without errors
        product_page.log_action.assert_called()

    def test_get_product_title_success(self, product_page):
        """Test getting product title."""
        product_page.get_text = Mock(return_value="  Test Product  ")

        title = product_page.get_product_title()

        assert title == "Test Product"

    def test_get_product_title_failure(self, product_page):
        """Test getting product title when it fails."""
        product_page.get_text = Mock(side_effect=Exception("Element not found"))

        title = product_page.get_product_title()

        assert title == "Unknown Product"

    def test_get_product_price_success(self, product_page):
        """Test getting product price."""
        product_page.get_text = Mock(return_value="  $50.00  ")

        price = product_page.get_product_price()

        assert price == "$50.00"

    def test_get_product_price_failure(self, product_page):
        """Test getting product price when it fails."""
        product_page.get_text = Mock(side_effect=Exception("Element not found"))

        price = product_page.get_product_price()

        assert price == "Unknown Price"

    def test_verify_added_to_cart_confirmation_found(self, product_page, mock_page):
        """Test cart verification when confirmation is found."""
        mock_locator = Mock()
        mock_locator.count.return_value = 1
        mock_page.locator.return_value = mock_locator

        result = product_page._verify_added_to_cart()

        assert result is True

    def test_verify_added_to_cart_url_changed(self, product_page, mock_page):
        """Test cart verification when URL redirects to cart."""
        mock_locator = Mock()
        mock_locator.count.return_value = 0
        mock_page.locator.return_value = mock_locator

        type(product_page).current_url = property(lambda self: "https://www.ebay.com/cart")

        result = product_page._verify_added_to_cart()

        assert result is True

    def test_verify_added_to_cart_no_confirmation(self, product_page, mock_page):
        """Test cart verification when no confirmation is found."""
        mock_locator = Mock()
        mock_locator.count.return_value = 0
        mock_page.locator.return_value = mock_locator

        type(product_page).current_url = property(lambda self: "https://www.ebay.com/itm/12345")

        result = product_page._verify_added_to_cart()

        # Still returns True (assumes success)
        assert result is True

    def test_click_add_to_cart_success(self, product_page):
        """Test clicking add to cart button successfully."""
        product_page.is_element_present = Mock(return_value=True)
        product_page.click = Mock()

        result = product_page._click_add_to_cart()

        assert result is True
        product_page.click.assert_called_once()

    def test_click_add_to_cart_button_not_found(self, product_page):
        """Test clicking add to cart when button not found."""
        product_page.is_element_present = Mock(return_value=False)

        result = product_page._click_add_to_cart()

        assert result is False
