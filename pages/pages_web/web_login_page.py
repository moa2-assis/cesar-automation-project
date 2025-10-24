# pages/pages_web/web_login_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.pages_web.web_base_page import WebBasePage


class WebLoginPage(WebBasePage):
    EMAIL = (By.NAME, "email")
    SUBMIT_EMAIL_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    TOKEN = (By.NAME, "token")
    SUBMIT_TOKEN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")

    def wait_loaded(self) -> bool:
        try:
            self.wait.until(
                EC.any_of(
                    EC.visibility_of_element_located(self.EMAIL),
                    EC.element_to_be_clickable(self.SUBMIT_EMAIL_BUTTON),
                )
            )
            return True
        except Exception:
            return "/login" in (self.driver.current_url or "").lower()

    def type_email(self, email: str) -> bool:
        try:
            self.type(*self.EMAIL, text=email)
            return True
        except Exception:
            return False

    def type_token(self, token: str) -> bool:
        try:
            self.type(*self.TOKEN, text=token)
            return True
        except Exception:
            return False

    def click_submit_email(self) -> bool:
        try:
            btn = self.wait_clickable(*self.SUBMIT_EMAIL_BUTTON)
            try:
                btn.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", btn)
            return True
        except Exception:
            return False

    def click_submit_token(self) -> bool:
        try:
            btn = self.wait_clickable(*self.SUBMIT_TOKEN_BUTTON)
            try:
                btn.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", btn)
            return True
        except Exception:
            return False
