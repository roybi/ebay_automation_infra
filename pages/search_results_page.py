import re
from typing import List, Optional
from playwright.sync_api import Page, Locator

from core.base_page import BasePage
from core.smart_locator import SmartLocator
from utils.allure_helper import allure_step, AllureHelper


class SearchResultsPage(BasePage):
    """
    eBay Search Results Page object.
    Handles search results, filtering, and item extraction.
    """
    
    PAGE_NAME = "SearchResultsPage"
    
    def __init__(self, page: Page):
        super().__init__(page)
        self._define_locators()
    
    def _define_locators(self) -> None:
        self.PRICE_MIN_INPUT = SmartLocator(name="Price Min Input")
        self.PRICE_MIN_INPUT.add_xpath("//input[@aria-label='Minimum value in $']", "aria-label")
        self.PRICE_MIN_INPUT.add_xpath("//input[contains(@class, 'x-price-range__input--min')]", "class")
        self.PRICE_MIN_INPUT.add_xpath("//input[@placeholder='Min']", "placeholder")

        self.PRICE_MAX_INPUT = SmartLocator(name="Price Max Input")
        self.PRICE_MAX_INPUT.add_css("input.x-price-range__input--max", "class")
        self.PRICE_MAX_INPUT.add_css("input[aria-label='Maximum value in $']", "aria-label")
        self.PRICE_MAX_INPUT.add_css("input[name='_udhi']", "name")

        self.PRICE_FILTER_SUBMIT = SmartLocator(name="Price Filter Submit")
        self.PRICE_FILTER_SUBMIT.add_xpath("//button[@aria-label='Submit price range']", "aria-label")

        self.RESULTS_CONTAINER = SmartLocator(name="Results Container")
        self.RESULTS_CONTAINER.add_xpath("//ul[@id='srp-river-results']", "id")
        self.RESULTS_CONTAINER.add_xpath("//ul[@data-view='list']", "data-view")

        self.RESULT_ITEMS = SmartLocator(name="Result Items")
        self.RESULT_ITEMS.add_xpath("//ul[contains(@class, 'srp-results')]/li[contains(@class, 's-item')]", "class")
        self.RESULT_ITEMS.add_xpath("//li[@data-view='mi:1686|iid:1']", "data-view")

        self.ITEM_LINK = SmartLocator(name="Item Link")
        self.ITEM_LINK.add_css("a[href*='/itm/']", "href")
        self.ITEM_LINK.add_xpath(".//a[@data-track='true']", "data-track")

        self.ITEM_PRICE = SmartLocator(name="Item Price")
        self.ITEM_PRICE.add_xpath(".//span[@class='s-item__price']", "class")
        self.ITEM_PRICE.add_xpath(".//span[starts-with(normalize-space(text()), '$')]", "text")

        self.ITEM_TITLE = SmartLocator(name="Item Title")
        self.ITEM_TITLE.add_xpath(".//div[contains(@class, 's-item__title')]//span[@role='heading']", "class")
        self.ITEM_TITLE.add_css("div.s-item__title span", "class")

        self.NEXT_PAGE_BUTTON = SmartLocator(name="Next Page Button")
        self.NEXT_PAGE_BUTTON.add_xpath("//a[contains(@class, 'pagination__next')]", "class")

        self.PREV_PAGE_BUTTON = SmartLocator(name="Previous Page Button")
        self.PREV_PAGE_BUTTON.add_xpath("//a[@type='prev']", "type")
        self.PREV_PAGE_BUTTON.add_css("a.pagination__prev", "class")

        self.RESULTS_COUNT = SmartLocator(name="Results Count")
        self.RESULTS_COUNT.add_xpath("//span[contains(@class, 'srp-controls__count')]", "class")
        self.RESULTS_COUNT.add_xpath("//h1[contains(text(), 'results')]", "text")
        self.RESULTS_COUNT.add_css(".srp-controls__count-heading", "class")

        self.SORT_DROPDOWN = SmartLocator(name="Sort Dropdown")
        self.SORT_DROPDOWN.add_xpath("//button[@aria-label='Sort selector. Best Match selected.']", "aria-label")
        self.SORT_DROPDOWN.add_css("button.srp-controls__sort", "class")

        self.NO_RESULTS = SmartLocator(name="No Results Message")
        self.NO_RESULTS.add_xpath("//div[contains(@class, 'srp-no-results')]", "class")
        self.NO_RESULTS.add_xpath("//*[contains(text(), 'No exact matches found')]", "text")
        self.NO_RESULTS.add_xpath("//h3[contains(text(), 'No results')]", "text")
        
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price from text string."""
        try:
            cleaned = price_text.strip()
            if " to " in cleaned.lower():
                cleaned = cleaned.split(" to ")[0].strip()
            match = re.search(r'[\d,]+\.?\d*', cleaned)
            if match:
                price_str = match.group().replace(',', '')
                return float(price_str)
            return None
        except Exception as e:
            self.logger.warning(f"Failed to parse price '{price_text}': {e}")
            return None
    
    def _is_price_filter_available(self) -> bool:
        """Check if price filter inputs are available."""
        return self.is_element_present(self.PRICE_MAX_INPUT, timeout=3000)
    
    def _apply_price_filter(self, max_price: float, min_price: float = 0) -> bool:
        """Apply price filter."""
        self.log_action("Price Filter", f"Attempting to apply price filter: ${min_price} - ${max_price}")

        if not self._is_price_filter_available():
            self.logger.info("Price filter not available on this page")
            return False

        try:
            if min_price > 0:
                self.fill(self.PRICE_MIN_INPUT, str(int(min_price)))
            self.fill(self.PRICE_MAX_INPUT, str(int(max_price)))
            self.click(self.PRICE_FILTER_SUBMIT)
            self.wait_for_page_load()
            self.wait_for_network_idle()
            self.logger.info(f"Price filter applied: ${min_price} - ${max_price}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to apply price filter: {e}")
            return False
    
    def _is_next_page_available(self) -> bool:
        """Check if next page button is available."""
        return self.is_element_present(self.NEXT_PAGE_BUTTON, timeout=3000)
    
    def _go_to_next_page(self) -> bool:
        """Navigate to next results page."""
        if not self._is_next_page_available():
            self.logger.info("No next page available")
            return False
        try:
            self.log_action("Pagination", "Navigating to next page")
            self.click(self.NEXT_PAGE_BUTTON)
            self.wait_for_page_load()
            self.wait_for_network_idle()
            self.logger.info("Successfully navigated to next page")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to navigate to next page: {e}")
            return False
    
    def _extract_items_from_current_page(self, max_price: float, limit: int, collected_urls: List[str]) -> List[str]:
        """Extract item URLs from current page."""
        urls = []
        remaining = limit - len(collected_urls)

        if remaining <= 0:
            return urls

        try:
            items = self.page.locator("xpath=//li[contains(@class, 's-item')]").all()
            self.logger.info(f"Found {len(items)} items on current page, need {remaining} more")

            for item in items:
                if len(urls) + len(collected_urls) >= limit:
                    break

                try:
                    item_class = item.get_attribute("class") or ""
                    if "s-item__pl-on-bottom" in item_class or "s-item--watch-at-corner" not in item_class:
                        pass

                    price_element = None
                    price_selectors = [
                        "xpath=.//span[contains(@class, 's-item__price')]",
                        "xpath=.//span[@class='s-item__price']",
                        "css=span.s-item__price"
                    ]

                    for selector in price_selectors:
                        try:
                            price_element = item.locator(selector).first
                            if price_element.is_visible():
                                break
                        except:
                            continue

                    if not price_element or not price_element.is_visible():
                        continue

                    price_text = price_element.text_content()
                    price = self._parse_price(price_text)

                    if price is None:
                        self.logger.debug(f"Could not parse price: {price_text}")
                        continue

                    if price > max_price:
                        self.logger.debug(f"Price ${price} exceeds max ${max_price}, skipping")
                        continue

                    link_element = None
                    link_selectors = [
                        "xpath=.//a[contains(@class, 's-item__link')]",
                        "xpath=.//a[contains(@href, '/itm/')]",
                        "css=a.s-item__link",
                        "css=a[href*='/itm/']"
                    ]
                    
                    for selector in link_selectors:
                        try:
                            link_element = item.locator(selector).first
                            if link_element.is_visible():
                                break
                        except:
                            continue
                    
                    if not link_element:
                        continue
                    
                    href = link_element.get_attribute("href")
                    
                    if href and href not in collected_urls and href not in urls:
                        urls.append(href)
                        self.logger.info(f"Collected item: ${price} - {href[:80]}...")
                        
                except Exception as e:
                    self.logger.debug(f"Error processing item: {e}")
                    continue
            
            return urls
            
        except Exception as e:
            self.logger.error(f"Error extracting items: {e}")
            return urls
    
    @allure_step("Search items by name under price")
    def search_items_by_name_under_price(self, query: str, max_price: float, limit: int = 5) -> List[str]:
        """Search items by query under max price."""
        self.log_action("searchItemsByNameUnderPrice", f"Query: '{query}', Max Price: ${max_price}, Limit: {limit}")

        collected_urls: List[str] = []

        try:
            if "ebay.com" not in self.current_url or "/sch/" not in self.current_url:
                from pages.home_page import HomePage
                home = HomePage(self.page)
                home.navigate()
                home.identification()
                home.search(query)

            self.wait_for_page_load()
            self.wait_for_network_idle()

            filter_applied = self._apply_price_filter(max_price)
            if filter_applied:
                self.logger.info("Price filter was applied successfully")
            else:
                self.logger.info("Price filter not available, will filter manually")

            self.capture_screenshot(f"search_results_{query}")

            collected_urls = self._extract_items_from_current_page(max_price, limit, collected_urls)
            self.logger.info(f"Collected {len(collected_urls)} items from first page")

            page_count = 1
            max_pages = 5

            while len(collected_urls) < limit and page_count < max_pages:
                if not self._is_next_page_available():
                    self.logger.info("No more pages available")
                    break

                if not self._go_to_next_page():
                    self.logger.info("Could not navigate to next page")
                    break

                page_count += 1
                self.logger.info(f"Processing page {page_count}")

                new_urls = self._extract_items_from_current_page(max_price, limit, collected_urls)
                collected_urls.extend(new_urls)

                self.logger.info(f"Total collected: {len(collected_urls)} items after page {page_count}")

            self.logger.info(f"searchItemsByNameUnderPrice completed: Found {len(collected_urls)} items for '{query}' under ${max_price}")
            
            # Attach results to Allure report
            AllureHelper.attach_json(
                {
                    "query": query,
                    "max_price": max_price,
                    "limit": limit,
                    "items_found": len(collected_urls),
                    "urls": collected_urls
                },
                "Search Results"
            )
            
            self.capture_screenshot(f"search_complete_{query}")
            
            return collected_urls
            
        except Exception as e:
            self.logger.error(f"searchItemsByNameUnderPrice failed: {e}")
            self.capture_screenshot("search_error")
            AllureHelper.attach_text(str(e), "Error Details")
            return collected_urls  # Return whatever was collected
    
    def get_results_count(self) -> Optional[int]:
        """Get the total number of search results."""
        try:
            if self.is_element_visible(self.RESULTS_COUNT):
                text = self.get_text(self.RESULTS_COUNT)
                match = re.search(r'[\d,]+', text)
                if match:
                    return int(match.group().replace(',', ''))
        except:
            pass
        return None
    
    def has_results(self) -> bool:
        """Check if search returned any results."""
        return not self.is_element_present(self.NO_RESULTS, timeout=2000)


def search_items_by_name_under_price(page: Page, query: str, max_price: float, limit: int = 10) -> List[str]:
    """Search items by query under max price."""
    search_results_page = SearchResultsPage(page)
    return search_results_page.search_items_by_name_under_price(query, max_price, limit)