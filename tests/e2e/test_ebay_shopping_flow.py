"""
End-to-End Test: eBay Shopping Flow
Implements the full scenario from NessHomeTest.docx:
1. Identification - Verify eBay homepage
2. Search items by name under price
3. Add items to cart
4. Assert cart total does not exceed budget
"""

import pytest
import allure

from pages import (
    HomePage,
    SearchResultsPage,
    ProductPage,
    CartPage,
    search_items_by_name_under_price,
    add_items_to_cart,
    assert_cart_total_not_exceeds,
)
from utils.data_loader import DataLoader


@pytest.mark.e2e
@allure.epic("eBay E2E Tests")
@allure.feature("Shopping Flow")
class TestEbayShoppingFlow:
    """
    End-to-end test for complete eBay shopping workflow.

    Scenario:
    1. Navigate to eBay homepage
    2. Search for items under a specific price
    3. Add found items to cart
    4. Verify cart total does not exceed budget
    """

    @pytest.fixture
    def test_data(self):
        """Load test data from JSON file."""
        data_loader = DataLoader()
        data = data_loader.load_json("test_data.json")
        return data["test_data"][0]  # Use first test case

    @allure.story("Complete Shopping Flow - Shoes Example")
    @allure.title("Search shoes under $220, add 5 items to cart, validate total")
    @allure.description(
        "Full E2E scenario: Search for shoes under $220, "
        "add up to 5 items to cart, and verify cart total "
        "does not exceed $220 * number_of_items"
    )
    def test_complete_shopping_flow_shoes(self, page, test_data):
        """
        Test the complete shopping flow as per NessHomeTest.docx requirements.

        Steps:
        1. Identification - Verify eBay homepage is loaded
        2. searchItemsByNameUnderPrice("shoes", 220, 5) - Get up to 5 item URLs
        3. addItemsToCart(urls) - Add all items to cart
        4. assertCartTotalNotExceeds(220, urls.length) - Validate cart total
        """
        # Extract test parameters
        search_query = test_data["search_query"]
        max_price = test_data["max_price"]
        limit = test_data["limit"]

        # ============= STEP 1: Identification =============
        with allure.step("Step 1: Verify eBay homepage (identification)"):
            home_page = HomePage(page)
            home_page.navigate()

            # Verify homepage is properly loaded
            identification_passed = home_page.identification()
            assert identification_passed, "eBay homepage identification failed"

            allure.attach(
                str(identification_passed),
                name="Identification Result",
                attachment_type=allure.attachment_type.TEXT
            )

        # ============= STEP 2: Search Items by Name Under Price =============
        with allure.step(f"Step 2: Search for '{search_query}' under ${max_price}"):
            # Perform search
            home_page.search(search_query)

            # Use searchItemsByNameUnderPrice function
            search_results_page = SearchResultsPage(page)
            urls = search_results_page.search_items_by_name_under_price(
                query=search_query,
                max_price=max_price,
                limit=limit
            )

            # Validate search results
            assert len(urls) > 0, f"No items found under ${max_price}"
            assert len(urls) <= limit, f"Found more than {limit} items"

            allure.attach(
                f"Found {len(urls)} items:\n" + "\n".join(urls[:5]),
                name="Search Results",
                attachment_type=allure.attachment_type.TEXT
            )

        # ============= STEP 3: Add Items to Cart =============
        with allure.step(f"Step 3: Add {len(urls)} items to cart"):
            # Use addItemsToCart function
            product_page = ProductPage(page)
            successful_urls, failed_urls = add_items_to_cart(page, urls)

            # Log results
            allure.attach(
                f"Successfully added: {len(successful_urls)}\n"
                f"Failed to add: {len(failed_urls)}",
                name="Add to Cart Summary",
                attachment_type=allure.attachment_type.TEXT
            )

            # We should have at least some items successfully added
            assert len(successful_urls) > 0, "Failed to add any items to cart"

        # ============= STEP 4: Assert Cart Total Not Exceeds =============
        with allure.step(
            f"Step 4: Verify cart total <= ${max_price} * {len(successful_urls)}"
        ):
            # Use assertCartTotalNotExceeds function
            cart_page = CartPage(page)
            assertion_passed, details = cart_page.assert_cart_total_not_exceeds(
                budget_per_item=max_price,
                items_count=len(successful_urls)
            )

            # Attach detailed results
            allure.attach(
                f"Cart Total: ${details.get('actual_total', 'N/A')}\n"
                f"Max Allowed: ${details.get('expected_max_total', 'N/A')}\n"
                f"Items in Cart: {details.get('items_count', 'N/A')}\n"
                f"Assertion: {'PASSED' if assertion_passed else 'FAILED'}\n"
                f"Reason: {details.get('reason', 'N/A')}",
                name="Cart Validation Result",
                attachment_type=allure.attachment_type.TEXT
            )

            # Final assertion
            assert assertion_passed, (
                f"Cart total assertion failed: {details.get('reason', 'Unknown')}"
            )

    @allure.story("Complete Shopping Flow - Laptops Example")
    @allure.title("Search laptops under $500, add items to cart, validate total")
    def test_complete_shopping_flow_laptops(self, page):
        """
        Test shopping flow with different product category (laptops).
        Demonstrates test parameterization and reusability.
        """
        search_query = "laptop"
        max_price = 500
        limit = 5

        # Step 1: Identification
        with allure.step("Verify eBay homepage"):
            home_page = HomePage(page)
            home_page.navigate()
            assert home_page.identification()

        # Step 2: Search
        with allure.step(f"Search for '{search_query}' under ${max_price}"):
            home_page.search(search_query)
            search_results_page = SearchResultsPage(page)
            urls = search_results_page.search_items_by_name_under_price(
                query=search_query, max_price=max_price, limit=limit
            )
            assert len(urls) > 0, f"No items found under ${max_price}"

        # Step 3: Add to cart
        with allure.step(f"Add items to cart"):
            successful_urls, failed_urls = add_items_to_cart(page, urls)
            assert len(successful_urls) > 0, "Failed to add any items"

        # Step 4: Assert cart total
        with allure.step("Verify cart total"):
            assertion_passed, details = assert_cart_total_not_exceeds(
                page, max_price, len(successful_urls)
            )
            assert assertion_passed, f"Cart total validation failed: {details.get('reason')}"

    @allure.story("Standalone Functions Test")
    @allure.title("Test using standalone functions (non-POM approach)")
    def test_using_standalone_functions(self, page):
        """
        Test the E2E flow using standalone functions instead of page objects.
        Demonstrates alternative usage pattern.
        """
        search_query = "headphones"
        max_price = 100
        limit = 5

        # Step 1: Navigate and verify
        with allure.step("Navigate to eBay"):
            home_page = HomePage(page)
            home_page.navigate()
            home_page.search(search_query)

        # Step 2: Search using standalone function
        with allure.step("Search items"):
            urls = search_items_by_name_under_price(page, search_query, max_price, limit)
            assert len(urls) > 0

        # Step 3: Add to cart using standalone function
        with allure.step("Add to cart"):
            successful_urls, failed_urls = add_items_to_cart(page, urls)
            assert len(successful_urls) > 0

        # Step 4: Verify using standalone function
        with allure.step("Verify cart"):
            passed, details = assert_cart_total_not_exceeds(
                page, max_price, len(successful_urls)
            )
            assert passed

    @pytest.mark.smoke
    @allure.story("Quick Smoke Test")
    @allure.title("Smoke test: Search and verify single item")
    def test_smoke_single_item(self, page):
        """
        Quick smoke test: Search for one item, add to cart, verify.
        Faster test for CI/CD pipeline.
        """
        search_query = "phone case"
        max_price = 50
        limit = 1  # Only 1 item for speed

        home_page = HomePage(page)
        home_page.navigate()
        assert home_page.identification()

        home_page.search(search_query)

        search_results_page = SearchResultsPage(page)
        urls = search_results_page.search_items_by_name_under_price(
            search_query, max_price, limit
        )

        if len(urls) > 0:
            successful, failed = add_items_to_cart(page, urls)
            if len(successful) > 0:
                passed, _ = assert_cart_total_not_exceeds(page, max_price, len(successful))
                assert passed


@pytest.mark.e2e
@allure.epic("eBay E2E Tests")
@allure.feature("Error Handling")
class TestEbayShoppingFlowErrorHandling:
    """Test error handling and edge cases in the shopping flow."""

    @allure.story("Error Handling - Empty Search Results")
    @allure.title("Handle case when no items meet price criteria")
    def test_no_items_found_under_price(self, page):
        """Test behavior when no items are found under the price threshold."""
        search_query = "luxury yacht"
        max_price = 10  # Unrealistically low price
        limit = 5

        home_page = HomePage(page)
        home_page.navigate()
        home_page.search(search_query)

        search_results_page = SearchResultsPage(page)
        urls = search_results_page.search_items_by_name_under_price(
            search_query, max_price, limit
        )

        # Should return empty list or very few results
        assert isinstance(urls, list)
        # Test should handle gracefully, not crash

    @allure.story("Error Handling - Cart Verification with Empty Cart")
    @allure.title("Handle cart validation when cart is empty")
    def test_cart_validation_empty_cart(self, page):
        """Test cart validation when no items were added."""
        cart_page = CartPage(page)
        cart_page.navigate_to_cart()

        # Try to validate empty cart
        passed, details = cart_page.assert_cart_total_not_exceeds(220, 5)

        # Should fail gracefully with proper error message
        assert passed is False
        assert "empty" in details.get("reason", "").lower()

    @allure.story("Error Handling - Partial Success")
    @allure.title("Handle case when only some items are added to cart")
    def test_partial_add_to_cart_success(self, page):
        """
        Test behavior when only some items can be added to cart.
        This can happen due to out-of-stock items or variants not available.
        """
        search_query = "shoes"
        max_price = 220
        limit = 3

        home_page = HomePage(page)
        home_page.navigate()
        home_page.search(search_query)

        search_results_page = SearchResultsPage(page)
        urls = search_results_page.search_items_by_name_under_price(
            search_query, max_price, limit
        )

        if len(urls) > 0:
            successful, failed = add_items_to_cart(page, urls)

            # Should handle partial success gracefully
            total_processed = len(successful) + len(failed)
            assert total_processed == len(urls)

            # If any succeeded, validate cart
            if len(successful) > 0:
                passed, details = assert_cart_total_not_exceeds(
                    page, max_price, len(successful)
                )
                # Assertion should work even with fewer items than expected


@pytest.mark.e2e
@pytest.mark.parametrize(
    "query,max_price,limit",
    [
        ("shoes", 220, 5),
        ("laptop", 500, 3),
        ("headphones", 100, 4),
    ],
    ids=["shoes-220", "laptop-500", "headphones-100"]
)
@allure.epic("eBay E2E Tests")
@allure.feature("Parameterized Tests")
class TestParameterizedShoppingFlow:
    """Parameterized E2E tests for different search queries and prices."""

    @allure.story("Parameterized Shopping Flow")
    def test_shopping_flow_parameterized(self, page, query, max_price, limit):
        """
        Parameterized test for shopping flow with different products.

        Args:
            query: Search query
            max_price: Maximum price threshold
            limit: Number of items to search for
        """
        allure.dynamic.title(
            f"E2E Test: {query} under ${max_price} (limit: {limit})"
        )

        # Navigate and search
        home_page = HomePage(page)
        home_page.navigate()
        assert home_page.identification()
        home_page.search(query)

        # Search items
        urls = search_items_by_name_under_price(page, query, max_price, limit)
        assert len(urls) > 0, f"No {query} found under ${max_price}"

        # Add to cart
        successful, failed = add_items_to_cart(page, urls)
        assert len(successful) > 0, f"Failed to add any {query} to cart"

        # Validate cart
        passed, details = assert_cart_total_not_exceeds(page, max_price, len(successful))
        assert passed, f"Cart validation failed for {query}: {details.get('reason')}"
