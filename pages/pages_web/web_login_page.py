# pages/pages_web/web_login_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.pages_web.web_base_page import WebBasePage


class WebLoginPage(WebBasePage):
    EMAIL = (By.NAME, "email")

    SUBMIT_EMAIL_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    TOKEN = (By.NAME, "token")
    SUBMIT_TOKEN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SUBMIT_EMAIL_PASSWORD_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")

    LOGIN_WITH_EMAIL_PASSWORD = (
        By.XPATH,
        "//button[.//span[normalize-space()='Entrar com email e senha']]",
    )

    EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='text']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password']")

    EMAIL_PASSWORD_ERROR_MESSAGE = (By.XPATH, "//div[@role='alert'][contains(., 'Usuário e/ou senha incorretos')]")

    # def wait_loaded(self) -> bool:
    #     try:
    #         self.wait.until(
    #             EC.any_of(
    #                 EC.visibility_of_element_located(self.EMAIL),
    #                 EC.element_to_be_clickable(self.SUBMIT_EMAIL_BUTTON),
    #             )
    #         )
    #         return True
    #     except Exception:
    #         return "/login" in (self.driver.current_url or "").lower()

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
            self.click(*self.SUBMIT_EMAIL_BUTTON)
            return True
        except Exception:
            return False

    def click_submit_token(self) -> bool:
        try:
            self.click(*self.SUBMIT_TOKEN_BUTTON)
            return True
        except Exception:
            return False

    def click_to_login_email_password(self):
        try:
            self.click(*self.LOGIN_WITH_EMAIL_PASSWORD)
            return True
        except Exception:
            return False

    def type_email_and_password(self, email, password):
        try:
            self.type(*self.EMAIL_INPUT, text=email)
            self.type(*self.PASSWORD_INPUT, text=password)
            return True
        except Exception:
            return False

    def click_submit_email_password(self):
        try:
            self.click(*self.SUBMIT_EMAIL_PASSWORD_BUTTON)
            return True
        except Exception:
            return False

    def is_login_error_visible(self):
        try:
            self.wait.until(
                EC.visibility_of_element_located(self.EMAIL_PASSWORD_ERROR_MESSAGE)
            )
            return True
        except Exception:
            return False

    def get_login_error_text(self):
        try:
            return (self.get_text(*self.EMAIL_PASSWORD_ERROR_MESSAGE) or "").strip()
        except Exception:
            return ""
