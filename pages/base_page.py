# pages/base_page.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

class BasePage:
    """Base genérica (comum a Appium e Selenium)."""

    def __init__(self, driver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # waits/find
    def find_element(self, by, locator):
        return self.wait.until(EC.presence_of_element_located((by, locator)))

    def wait_for_visibility(self, by, locator):
        return self.wait.until(EC.visibility_of_element_located((by, locator)))

    def wait_clickable(self, by, locator):
        return self.wait.until(EC.element_to_be_clickable((by, locator)))

    # ações básicas
    def click(self, by, locator):
        try:
            self.wait_clickable(by, locator).click()
        except:
            el = self.find_element(by, locator)
            self.driver.execute_script("arguments[0].click();", el)

    def type(self, by, locator, text: str, clear_first: bool = True):
        el = self.wait_for_visibility(by, locator)
        if clear_first:
            el.clear()
        el.send_keys(text)

    def get_text(self, by, locator) -> str:
        return self.find_element(by, locator).text

    def is_visible(self, by, locator) -> bool:
        try:
            self.wait_for_visibility(by, locator)
            return True
        except TimeoutException:
            return False

    def attr(self, by, locator, name: str):
        return self.find_element(by, locator).get_attribute(name)

    def clear_field(self, by, locator):
        """Limpa um input genérico."""
        el = self.wait_for_visibility(by, locator)
        try:
            el.clear()
        except Exception:
            pass
        # garante limpeza (VTEX às vezes ignora clear)
        try:
            el.send_keys(Keys.CONTROL, "a")
            el.send_keys(Keys.DELETE)
        except Exception:
            try:
                el.send_keys(Keys.COMMAND, "a")  # macOS
                el.send_keys(Keys.DELETE)
            except Exception:
                pass
        return el
