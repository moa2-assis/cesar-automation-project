import re
import time
from typing import List, Optional
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage  # usa teu BasePage original


class MobileBasePage(BasePage):
    def wait_for_visibility(self, by, locator):
        return self.wait.until(
            EC.visibility_of_element_located((by, locator))
        )

    def is_visible(self, by, locator):
        try:
            self.wait_for_visibility(by, locator)
            return True
        except TimeoutException:
            return False

    def find_by_desc(self, text):
        return self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().description("{text}")'
        )

    def find_by_desc_contains(self, text):
        return self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().descriptionContains("{text}")',
        )

    # ações
    def tap(self, by, locator, retries: int = 2):
        for i in range(retries):
            try:
                el = self.wait_for_visibility(by, locator)
                el.click()
                return
            except Exception:
                try:
                    # tenta trazer pra tela e clicar de novo
                    self.scroll_screen_down(0.5)
                except Exception:
                    pass
        raise AssertionError(f"Couldn't click on {locator}")

    def type_text(self, by, locator, text, clear=True):
        el = self.wait_for_visibility(by, locator)
        if clear:
            try:
                el.clear()
            except Exception:
                pass
        el.send_keys(text)

    def press_enter(self):
        self.driver.press_keycode(66)

    def hide_keyboard_safe(self):
        try:
            self.driver.hide_keyboard()
        except Exception:
            pass

    def back_safe(self):
        try:
            self.driver.back()
        except Exception:
            pass

    # scroll e navegação
    def scroll_to(self, by, locator, direction="down", max_swipes=5):
        for _ in range(max_swipes):
            if self.is_visible(by, locator):
                return self.driver.find_element(by, locator)
            self.scroll_screen_down()
        raise AssertionError(
            f"Elemento {locator} não encontrado após {max_swipes} scrolls."
        )

    def scroll_screen_down(self, percent: float = 0.8):
        size = self.driver.get_window_size()
        self.driver.execute_script(
            "mobile: scrollGesture",
            {
                "left": 0,
                "top": size["height"] * 0.3,
                "width": size["width"],
                "height": size["height"] * 0.5,
                "direction": "down",
                "percent": percent,
            },
        )
        time.sleep(0.4)

    def scroll_screen_up(self, percent: float = 0.8):
        size = self.driver.get_window_size()
        self.driver.execute_script(
            "mobile: scrollGesture",
            {
                "left": 0,
                "top": size["height"] * 0.3,
                "width": size["width"],
                "height": size["height"] * 0.5,
                "direction": "up",
                "percent": percent,
            },
        )
        time.sleep(0.4)

    # helpers
    def normalize_price(self, text):
        """Remove símbolos e normaliza preço."""
        return (
            text.replace("R$", "")
            .replace(" ", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )

    def extract_prices_from_text(self, text):
        return re.findall(r"R\$[\s]*[\d\.]+,[\d]{2}", text or "")

    def pick_best_price(self, lines):
        clean_lines = [ln for ln in lines if "R$" in ln]
        if not clean_lines:
            return None
        for ln in clean_lines:
            if "vista" in ln.lower():
                return ln
        return clean_lines[-1]

    def extract_title_from_desc(self, desc):
        lines = [ln.strip() for ln in desc.split("\n") if ln.strip()]
        text_lines = [
            ln for ln in lines if not any(s in ln for s in ["R$", "%", "à vista"])
        ]
        if not text_lines:
            return ""
        return max(text_lines, key=len)
