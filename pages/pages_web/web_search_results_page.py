from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.pages_web.web_base_page import WebBasePage


class WebSearchResultsPage(WebBasePage):
    # Botões/toggles de visualização (exemplos!)
    GRID_VIEW_BUTTON = (By.CSS_SELECTOR, "button[title='Forma de exibição em grade']")
    LIST_VIEW_BUTTON = (By.CSS_SELECTOR, "button[title='Forma de exibição horizontal']")
    SEARCH_RESULT_TITLE = (By.XPATH, "//h1[contains(., 'Resultados para:')]")
    PRODUCT_NAME = (By.CSS_SELECTOR, "h3[class^='ProductCard_productName__']")
    PRODUCT_PRICE = (By.CSS_SELECTOR, "p[class^='ProductCard_productPrice__']")
    PRODUCT_CARD = (By.CSS_SELECTOR, "div[data-fs-custom-product-card='true']")
    EMPTY_SEARCH_TITLE = (By.CSS_SELECTOR, "h1[class^=EmptySearchPage_searchTermWrapper__]")

    def switch_to_grid_view(self):
        return self.click(*self.GRID_VIEW_BUTTON)

    def switch_to_list_view(self):
        return self.click(*self.LIST_VIEW_BUTTON)

    def scroll_to_products(self):
        el = self.scroll_into_view(*self.GRID_VIEW_BUTTON, block="start")
        return el is not None

    def find_card_by_exact_name(self, expected_name: str):
        cards = self.find_elements(*self.PRODUCT_CARD)
        for card in cards:
            try:
                name_el = card.find_element(*self.PRODUCT_NAME)
            except NoSuchElementException:
                continue

            name_text = (name_el.text or "").strip()
            if name_text == expected_name:
                return card

        return None

    def get_price_from_card(self, card):
        price_el = card.find_element(*self.PRODUCT_PRICE)
        return (price_el.text or "").strip()

    def click_price_from_card(self):
        self.click(*self.PRODUCT_PRICE)

    def is_empty_search(self) -> bool:
        try:
            self.wait_visible(*self.EMPTY_SEARCH_TITLE)
            return True
        except TimeoutException:
            return False
