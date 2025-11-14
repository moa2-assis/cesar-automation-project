import re
import json
from pathlib import Path
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)

from pages.pages_web.web_base_page import WebBasePage

class WebAccountPage(WebBasePage):
    EMAIL_INFO = (
        By.XPATH,
        "//label[normalize-space()='Email']/following-sibling::div[contains(@class,'vtex-my-account-1-x-dataEntryChildren')]"
    )

    AUTHENTICATION_BUTTON = (
        By.XPATH,
        # isso aqui deu problema pois tem coisa em cima, aí tô pegando o pai
        "//a[contains(@href,'#/authentication') and normalize-space()='Autenticação']",
    )

    SETPASSWORD_BUTTON = (
        By.XPATH,
        "//div[normalize-space()='Definir senha']/parent::button"
    )
    AUTHENTICATION_TITLE = (
        By.XPATH,
        "//div[contains(@class,'vtex-pageHeader__title') and normalize-space()='Autenticação']"
    )
    SAVE_PASSWORD_BUTTON = (
        By.XPATH,
        "//button[.//div[normalize-space()='Salvar senha']]",
    )

    ACCESS_CODE_FIELD = (By.CSS_SELECTOR, "input[type='text']")
    PASSWORD_FIELD = (By.CSS_SELECTOR, "input[type='password']")

    MASKED_PASSWORD = (By.XPATH, "//div[contains(@class,'maskedPassword_content')]")

    def get_user_logged_email(self) -> str:
        el = self.wait_for_visibility(*self.EMAIL_INFO)
        return (el.text or "").strip().lower()

    def click_authentication(self):
        try:
            self.wait_for_visibility(*self.AUTHENTICATION_BUTTON)
            self.click(*self.AUTHENTICATION_BUTTON)
            return True
        except Exception:
            return False

    def click_set_password(self):
        try:
            self.wait_for_visibility(*self.SETPASSWORD_BUTTON)
            self.click(*self.SETPASSWORD_BUTTON)
            return True
        except Exception:
            return False

    def type_access_code(self, access_code: str) -> bool:
        try:
            self.type(*self.ACCESS_CODE_FIELD, text=access_code)
            return True
        except Exception:
            return False

    def is_save_password_enabled(self) -> bool:
        try:
            btn = self.wait_for_visibility(*self.SAVE_PASSWORD_BUTTON)
            # 1) API do Selenium
            enabled_flag = btn.is_enabled()
            # 2) atributo disabled
            has_disabled_attr = (btn.get_attribute("disabled") is not None)
            # 3) classes que indicam desabilitado (pelo seu HTML)
            cls = btn.get_attribute("class") or ""
            looks_disabled = ("bg-disabled" in cls) or ("c-on-disabled" in cls)

            # Habilitado só se:
            return enabled_flag and (not has_disabled_attr) and (not looks_disabled)
        except Exception:
            return False

    def click_save_password(self):
        try:
            self.wait_for_visibility(*self.SAVE_PASSWORD_BUTTON)
            self.wait_clickable(*self.SAVE_PASSWORD_BUTTON).click()
        except Exception:
            return

    def type_password(self, password: str) -> bool:
        try:
            el = self.clear_password_strict()
            el.send_keys(password)
            el.send_keys(Keys.TAB)  # dispara validação
            return True
        except Exception:
            return False

    def clear_password_strict(self):
        el = self.wait_for_visibility(*self.PASSWORD_FIELD)
        try:
            el.clear()
        except Exception:
            pass

        try:
            el.send_keys(Keys.CONTROL, "a"); el.send_keys(Keys.DELETE)
        except Exception:
            try:
                el.send_keys(Keys.COMMAND, "a"); el.send_keys(Keys.DELETE)
            except Exception:
                pass

        try:
            self.driver.execute_script("""
                const el = arguments[0];
                el.value = '';
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
            """, el)
        except Exception:
            pass
        return el

    def get_masked_password(self) -> str:
        try:
            el = self.wait_for_visibility(*self.MASKED_PASSWORD)
            return (el.text or "").strip()
        except Exception:
            return ""

    def default_json_path(self) -> Path:
        root = Path(__file__).resolve().parents[2]
        data_dir = root / "data"
        data_dir.mkdir(exist_ok=True)
        return data_dir / "testing.json"

    # ========== EMAIL ==========

    def save_last_email(self, email: str) -> None:
        path = self.default_json_path()
        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        data["web"]["last_registered_email"] = (email or "").strip()

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_last_email(self) -> str:
        path = self.default_json_path()
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        return (data.get("web", {}).get("last_registered_email") or "").strip()

    # ========== SENHA ==========

    def save_last_password(self, password: str) -> None:
        path = self.default_json_path()
        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        data["web"]["last_registered_password"] = password or ""

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_last_password(self) -> str:
        path = self.default_json_path()
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        return data.get("web", {}).get("last_registered_password") or ""

    def get_incorrect_password(self) -> str:
        return "ThisIsWrongPassword12312"
