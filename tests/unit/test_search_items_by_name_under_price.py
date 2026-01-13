"""
Unit tests for searchItemsByNameUnderPrice function.
Tests the search, filtering, and pagination functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from playwright.sync_api import Page, Locator

from pages.search_results_page import SearchResultsPage, search_items_by_name_under_price


class TestSearchItemsByNameUnderPrice:
    """Unit tests for searchItemsByNameUnderPrice function."""

    @pytest.fixture
    def mock_page(self):
        """Create a mock Playwright Page object."""
        page = Mock(spec=Page)
        page.wait_for_timeout = Mock()
        page.locator = Mock()
        return page

    @pytest.fixture
    def search_page(self, mock_page):
        """Create SearchResultsPage with mocked page."""
        with patch.object(SearchResultsPage, '_define_locators'):
            search_page = SearchResultsPage(mock_page)
            search_page.logger = Mock()
            search_page.log_action = Mock()
            search_page.capture_screenshot = Mock()
            search_page.wait_for_page_load = Mock()
            search_page.wait_for_network_idle = Mock()
            return search_page

    def test_parse_price_valid_price(self, search_page):
        """Test parsing valid price strings."""
        assert search_page._parse_price("$220.00") == 220.0
        assert search_page._parse_price("$1,220.50") == 1220.5
        assert search_page._parse_price("220") == 220.0
        assert search_page._parse_price("$99.99") == 99.99

    def test_parse_price_invalid_price(self, search_page):
        """Test parsing invalid price strings."""
        assert search_page._parse_price("") is None
        assert search_page._parse_price("invalid") is None
        assert search_page._parse_price("$abc") is None

    def test_search_items_no_results(self, search_page, mock_page):
        """Test search when no items meet criteria."""
        # Mock empty results
        mock_items = []
        mock_locator = Mock()
        mock_locator.all.return_value = mock_items
        mock_page.locator.return_value = mock_locator

        search_page.is_element_present = Mock(return_value=False)

        result = search_page.search_items_by_name_under_price("nonexistent", 100, 5)

        assert result == []
        search_page.capture_screenshot.assert_called_once()

    def test_search_items_single_page_enough_results(self, search_page, mock_page):
        """Test search finding enough items on first page."""
        # Create mock items that meet price criteria
        mock_items = []
        for i in range(5):
            item = Mock(spec=Locator)
            price_elem = Mock()
            price_elem.is_visible.return_value = True
            price_elem.text_content.return_value = f"${50 + i * 10}.00"

            link_elem = Mock()
            link_elem.get_attribute.return_value = f"https://ebay.com/item/{i}"

            item.locator.side_effect = lambda xpath, **kw: price_elem if "price" in xpath else link_elem
            mock_items.append(item)

        mock_locator = Mock()
        mock_locator.all.return_value = mock_items
        mock_page.locator.return_value = mock_locator

        search_page.is_element_present = Mock(return_value=False)  # No price filter
        search_page._apply_price_filter = Mock(return_value=False)

        result = search_page.search_items_by_name_under_price("shoes", 220, 5)

        assert len(result) == 5
        assert all(url.startswith("https://ebay.com/item/") for url in result)

    def test_search_items_filters_expensive_items(self, search_page, mock_page):
        """Test that items above max price are filtered out."""
        # Create mock items with varying prices
        mock_items = []
        prices = [50, 150, 250, 100, 300]  # Only first 2 and 4th are under 220

        for i, price in enumerate(prices):
            item = Mock(spec=Locator)
            price_elem = Mock()
            price_elem.is_visible.return_value = True
            price_elem.text_content.return_value = f"${price}.00"

            link_elem = Mock()
            link_elem.get_attribute.return_value = f"https://ebay.com/item/{i}"

            item.locator.side_effect = lambda xpath, price_elem=price_elem, link_elem=link_elem: \
                price_elem if "price" in xpath else link_elem
            mock_items.append(item)

        mock_locator = Mock()
        mock_locator.all.return_value = mock_items
        mock_page.locator.return_value = mock_locator

        search_page.is_element_present = Mock(return_value=False)
        search_page._apply_price_filter = Mock(return_value=False)

        result = search_page.search_items_by_name_under_price("shoes", 220, 5)

        # Should return 3 items (prices 50, 150, 100)
        assert len(result) == 3

    def test_search_items_with_pagination(self, search_page, mock_page):
        """Test search with pagination when first page doesn't have enough items."""
        # First page: 2 items
        # Second page: 3 items
        pages_data = [
            [("50.00", "https://ebay.com/item/1"), ("100.00", "https://ebay.com/item/2")],
            [("75.00", "https://ebay.com/item/3"), ("125.00", "https://ebay.com/item/4"),
             ("90.00", "https://ebay.com/item/5")]
        ]

        page_index = [0]  # Track which page we're on

        def get_items(*args, **kwargs):
            items = []
            for price, url in pages_data[page_index[0]]:
                item = Mock(spec=Locator)
                price_elem = Mock()
                price_elem.is_visible.return_value = True
                price_elem.text_content.return_value = f"${price}"

                link_elem = Mock()
                link_elem.get_attribute.return_value = url

                item.locator.side_effect = lambda xpath, pe=price_elem, le=link_elem: \
                    pe if "price" in xpath else le
                items.append(item)

            mock_loc = Mock()
            mock_loc.all.return_value = items
            return mock_loc

        mock_page.locator.side_effect = get_items

        # Mock pagination
        has_next = [True, False]  # Has next page first time, not second time

        def mock_has_next_page():
            return has_next[page_index[0]]

        def mock_go_to_next():
            if page_index[0] < len(pages_data) - 1:
                page_index[0] += 1
                return True
            return False

        search_page.is_element_present = Mock(return_value=False)
        search_page._apply_price_filter = Mock(return_value=False)
        search_page._has_next_page = Mock(side_effect=mock_has_next_page)
        search_page._go_to_next_page = Mock(side_effect=mock_go_to_next)

        result = search_page.search_items_by_name_under_price("shoes", 220, 5)

        assert len(result) == 5
        assert search_page._go_to_next_page.called

    def test_search_items_stops_at_limit(self, search_page, mock_page):
        """Test that search stops when reaching the requested limit."""
        # Create 10 items but only request 3
        mock_items = []
        for i in range(10):
            item = Mock(spec=Locator)
            price_elem = Mock()
            price_elem.is_visible.return_value = True
            price_elem.text_content.return_value = f"${50 + i * 10}.00"

            link_elem = Mock()
            link_elem.get_attribute.return_value = f"https://ebay.com/item/{i}"

            item.locator.side_effect = lambda xpath, **kw: price_elem if "price" in xpath else link_elem
            mock_items.append(item)

        mock_locator = Mock()
        mock_locator.all.return_value = mock_items
        mock_page.locator.return_value = mock_locator

        search_page.is_element_present = Mock(return_value=False)
        search_page._apply_price_filter = Mock(return_value=False)

        result = search_page.search_items_by_name_under_price("shoes", 220, 3)

        assert len(result) == 3

    def test_search_items_applies_price_filter(self, search_page):
        """Test that price filter is applied when available."""
        search_page.is_element_present = Mock(return_value=True)
        search_page.fill = Mock()
        search_page.click = Mock()
        search_page.wait_for_page_load = Mock()
        search_page.wait_for_network_idle = Mock()

        result = search_page._apply_price_filter(220)

        assert result is True
        search_page.fill.assert_called_once()
        search_page.click.assert_called_once()

    def test_search_items_no_price_filter_available(self, search_page):
        """Test behavior when price filter is not available."""
        search_page.is_element_present = Mock(return_value=False)

        result = search_page._apply_price_filter(220)

        assert result is False

    def test_standalone_function(self, mock_page):
        """Test the standalone function wrapper."""
        with patch('pages.search_results_page.SearchResultsPage') as MockSearchPage:
            mock_instance = Mock()
            mock_instance.search_items_by_name_under_price.return_value = ["url1", "url2"]
            MockSearchPage.return_value = mock_instance

            result = search_items_by_name_under_price(mock_page, "shoes", 220, 5)

            assert result == ["url1", "url2"]
            mock_instance.search_items_by_name_under_price.assert_called_once_with("shoes", 220, 5)

    def test_search_handles_exceptions_gracefully(self, search_page, mock_page):
        """Test that search handles exceptions and returns partial results."""
        # First item succeeds, second raises exception
        item1 = Mock(spec=Locator)
        price_elem1 = Mock()
        price_elem1.is_visible.return_value = True
        price_elem1.text_content.return_value = "$50.00"
        link_elem1 = Mock()
        link_elem1.get_attribute.return_value = "https://ebay.com/item/1"
        item1.locator.side_effect = lambda xpath, **kw: price_elem1 if "price" in xpath else link_elem1

        item2 = Mock(spec=Locator)
        item2.locator.side_effect = Exception("Simulated error")

        mock_locator = Mock()
        mock_locator.all.return_value = [item1, item2]
        mock_page.locator.return_value = mock_locator

        search_page.is_element_present = Mock(return_value=False)
        search_page._apply_price_filter = Mock(return_value=False)

        result = search_page.search_items_by_name_under_price("shoes", 220, 5)

        # Should still return the first item despite second item error
        assert len(result) == 1
        assert result[0] == "https://ebay.com/item/1"
