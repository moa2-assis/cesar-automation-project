# pages/pages_web/web_base_page.py
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class WebBasePage(BasePage):
    """Extensões úteis para web (Selenium)."""

    def open(self, url: str):
        self.driver.get(url)

    def js_click(self, by, locator):
        el = self.wait_clickable(by, locator)
        self.driver.execute_script("arguments[0].click();", el)

    def scroll_into_view(self, by, locator, block: str = "center"):
        """
        block: 'start' | 'center' | 'end' | 'nearest'
        """
        el = self.find_element(by, locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: arguments[1], inline: 'nearest'});",
            el, block
        )
        return el

    def switch_to_tab(self, index: int = 0):
        self.driver.switch_to.window(self.driver.window_handles[index])