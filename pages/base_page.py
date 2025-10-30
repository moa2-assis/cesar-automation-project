# pages/base_page.py
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    TimeoutException,
)

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
    def js_click(self, el) -> bool:
        try:
            self.driver.execute_script("arguments[0].click();", el)
            return True
        except Exception:
            return False

    def click(self, by, locator, retries: int = 3, block: str = "center"):
        last_err = None
        for attempt in range(1, retries + 1):
            try:
                el = self.wait_clickable(by, locator)

                # tenta direto
                try:
                    el.click()
                    return True
                except (
                    ElementClickInterceptedException,
                    StaleElementReferenceException,
                ) as e:
                    last_err = e

                # scroll + novo try
                try:
                    el = self.scroll_into_view(by, locator, block=block)
                    time.sleep(0.1)
                    el.click()
                    return True
                except (
                    ElementClickInterceptedException,
                    StaleElementReferenceException,
                ) as e:
                    last_err = e
                except Exception as e:
                    last_err = e
                try:
                    el = self.find_element(by, locator)
                    if self.js_click(el):
                        return True
                except Exception as e:
                    last_err = e

            except (TimeoutException, StaleElementReferenceException) as e:
                last_err = e

            time.sleep(0.2 * attempt)
        if last_err:
            raise last_err
        return False

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
