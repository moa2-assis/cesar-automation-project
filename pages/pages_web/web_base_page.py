from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC


class WebBasePage(BasePage):
    def open(self, url: str):
        self.driver.get(url)

    # helpers
    def wait_clickable(self, by, locator):
        return self.wait.until(
            EC.element_to_be_clickable((by, locator))
        )

    def wait_visible(self, by, locator):
        return self.wait.until(EC.visibility_of_element_located((by, locator)))

    def find_element(self, by, locator):
        return self.driver.find_element(by, locator)

    def find_elements(self, by, locator):
        return self.driver.find_elements(by, locator)

    # ações
    def click(self, by, locator) -> bool:
        # espera ficar clicável
        element = self.wait_clickable(by, locator)

        # tenta click normal
        try:
            element.click()
            return True
        except Exception as e:
            print(f"[CLICK] normal click failed in {by}={locator}: {e}")
            # fallback: JS click
            try:
                self.js_click(element)
                return True
            except Exception as e2:
                print(f"[CLICK] js_click also failed in {by}={locator}: {e2}")
                return False

    def js_click(self, element):
        self.driver.execute_script("arguments[0].click();", element)

    def type(self, by, locator, text: str) -> bool:
        try:
            el = self.wait_visible(by, locator)
            el.clear()
            el.send_keys(text)
            return True
        except Exception as e:
            print(f"[TYPE] error typing in {by}={locator}: {e}")
            return False

    def get_text(self, by, locator) -> str:
        el = self.wait_visible(by, locator)
        return el.text or ""

    def switch_to_tab(self, index: int = 0):
        self.driver.switch_to.window(self.driver.window_handles[index])

    # block: "start" | "center" | "end" | "nearest"
    def scroll_into_view(self, by, locator, block: str = "center"):
        try:
            element = self.wait_visible(by, locator)
        except TimeoutException as e:
            print(f"[SCROLL] element not found to scroll: {by}={locator} -> {e}")
            return None

        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: arguments[1], inline: 'center'});",
                element,
                block,
            )
            return element
        except Exception as e:
            print(f"[SCROLL] error when scrolling to {by}={locator}: {e}")
            return element

    def normalize_price(self, text):
        if text is None:
            return ""
        treated_text = text.strip()
        treated_text = treated_text.replace("R$", "").strip()
        treated_text = treated_text.replace(",", "")
        treated_text = treated_text.replace(".", "")
        return treated_text
