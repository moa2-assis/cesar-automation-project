# pages/pages_web/web_temp_mail_page.py
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
)
from pages.pages_web.web_base_page import WebBasePage


class WebTempMailPage(WebBasePage):
    TEMP_URL = "https://temp-mail.io/"
    EMAIL_INPUT = (By.ID, "email")
    REFRESH_BUTTON = (By.CSS_SELECTOR, "div.refresh.truncate.w-full")
    NEW_MESSAGE_SUBJECTS = (By.CSS_SELECTOR, "span.message__subject")

    previous_codes = set()

    def wait_subjects_present(self, timeout: int = 20, refresh_each: int = 4):
        end = time.time() + timeout
        attempt = 0
        while time.time() < end:
            els = self.driver.find_elements(*self.NEW_MESSAGE_SUBJECTS)
            if els:
                vis = [e for e in els if e.is_displayed()]
                if vis:
                    return vis
                return els

            attempt += 1
            if attempt % refresh_each == 0:
                try:
                    self.click_refresh_button()
                except AttributeError:
                    pass
            time.sleep(0.5)
        raise AssertionError(
            "No subject came up on inbox during timeout period."
        )

    def wait_subject_with_phrase(
        self, phrase: str = "código de acesso", timeout: int = 30
    ):
        phrase_l = phrase.lower()
        end = time.time() + timeout
        attempt = 0
        while time.time() < end:
            els = self.driver.find_elements(*self.NEW_MESSAGE_SUBJECTS)
            for el in els:
                raw = (el.get_attribute("title") or el.text or "").strip()
                if phrase_l in raw.lower():
                    return el

            attempt += 1
            if hasattr(self, "click_refresh_button") and (attempt % 3 == 0):
                try:
                    self.click_refresh_button()
                except Exception:
                    pass
            time.sleep(0.8)
        raise AssertionError(f"Couldn't find subject with phrase '{phrase}'.")

    def open_temp_mail_in_new_tab(self):
        self.main_handle = self.driver.current_window_handle
        self.driver.switch_to.new_window("tab")
        self.driver.get(self.TEMP_URL)
        self.temp_handle = self.driver.current_window_handle

    def click_refresh_button(self):
        try:
            self.wait.until(EC.visibility_of_element_located(self.REFRESH_BUTTON))
        except TimeoutException:
            raise AssertionError("Refresh button not found on page.")
        self.scroll_into_view(*self.REFRESH_BUTTON)
        el = self.wait.until(EC.element_to_be_clickable(self.REFRESH_BUTTON))
        try:
            el.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", el)
        except Exception as e:
            raise AssertionError(f"Couldn't click refresh button: {type(e).__name__}: {e}")

    def get_temp_email_value(self, timeout: int = 20) -> str:
        self.wait.until(
            EC.presence_of_element_located(self.EMAIL_INPUT)
        )

        def value_ready(drv):
            try:
                v = drv.find_element(*self.EMAIL_INPUT).get_attribute("value") or ""
                v = v.strip()
                return v if (v and "@" in v) else False
            except Exception:
                return False

        value = self.wait.until(value_ready)
        return value

    def switch_to_temp_tab(self):
        if hasattr(self, "temp_handle"):
            self.driver.switch_to.window(self.temp_handle)

    def switch_to_main_tab(self):
        if hasattr(self, "main_handle"):
            self.driver.switch_to.window(self.main_handle)

    def get_fresh_access_code(self, tries: int = 20, pause: float = 1.0):
        self.wait_for_visibility(*self.NEW_MESSAGE_SUBJECTS)
        for i in range(tries):
            els = self.driver.find_elements(*self.NEW_MESSAGE_SUBJECTS)
            for el in els:
                raw = el.text.strip()
                digits = "".join(ch for ch in raw if ch.isdigit())
                if len(digits) >= 6:
                    code = digits[-6:]
                    if code not in self.previous_codes:
                        self.previous_codes.add(code)
                        print(f"[TempMail] Novo código encontrado: {code}")
                        return code

            try:
                self.click_refresh_button()
            except:
                pass

            time.sleep(pause)

        raise AssertionError("Nenhum código novo encontrado.")
