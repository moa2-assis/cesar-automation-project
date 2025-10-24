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

    def wait_subjects_present(self, timeout: int = 20, refresh_each: int = 4):
        """
        Espera aparecer AO MENOS 1 assunto na lista.
        De tempos em tempos tenta clicar no botão de refresh (se você implementou).
        Retorna a lista de WebElements dos assuntos.
        """
        end = time.time() + timeout
        attempt = 0
        while time.time() < end:
            els = self.driver.find_elements(*self.NEW_MESSAGE_SUBJECTS)
            if els:
                # opcional: filtra só os visíveis
                vis = [e for e in els if e.is_displayed()]
                if vis:
                    return vis
                return els  # se preferir, retorna mesmo não visíveis

            attempt += 1
            if hasattr(self, "click_refresh_button") and (attempt % refresh_each == 0):
                try:
                    self.click_refresh_button()
                except Exception:
                    pass
            time.sleep(0.5)
        raise AssertionError(
            "Nenhum assunto apareceu na caixa de entrada dentro do timeout."
        )

    def wait_subject_with_phrase(
        self, phrase: str = "código de acesso", timeout: int = 30
    ):
        """
        Espera até existir um assunto contendo a frase (case-insensitive).
        Retorna o WebElement do assunto encontrado.
        """
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
        raise AssertionError(f"Não encontrei assunto contendo '{phrase}'.")

    def get_access_code(self, tries: int = 20, pause: float = 1.0) -> str:
        """
        Procura qualquer assunto que contenha 'código de acesso' e retorna os últimos 6 dígitos.
        Tenta algumas vezes, dando refresh de vez em quando.
        """
        self.wait_for_visibility(*self.NEW_MESSAGE_SUBJECTS)
        for i in range(tries):
            els = self.driver.find_elements(*self.NEW_MESSAGE_SUBJECTS)

            for el in els:
                raw = (el.get_attribute("title") or el.text or "").strip()
                s = raw.lower()

                if "código de acesso" in s or "codigo de acesso" in s:
                    # regex
                    m = re.findall(r"\d{6}", raw)
                    if m:
                        return m[-1]

                    # fallback caso dê errado o regex acima
                    digits = "".join(ch for ch in raw if ch.isdigit())
                    if len(digits) >= 6:
                        return digits[-6:]

            if hasattr(self, "click_refresh_button") and (i % 3 == 2):
                try:
                    self.click_refresh_button()
                except Exception:
                    pass

            time.sleep(pause)

        raise AssertionError(
            "No subject with 'código de acesso' containing 6 digits found."
        )

    def open_temp_mail_in_new_tab(self):
        """Abre o temp-mail em NOVA aba (mantém aberta) e troca pra ela."""
        self.main_handle = self.driver.current_window_handle
        self.driver.switch_to.new_window("tab")
        self.driver.get(self.TEMP_URL)
        self.temp_handle = self.driver.current_window_handle

    def click_refresh_button(self):
        try:
            self.wait.until(EC.visibility_of_element_located(self.REFRESH_BUTTON))
        except TimeoutException:
            raise AssertionError("Refresh button not found on page.")

        self.scroll_into_view(*self.REFRESH_BUTTON, block="center")
        el = self.wait.until(EC.element_to_be_clickable(self.REFRESH_BUTTON))
        try:
            el.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", el)
        except Exception as e:
            raise AssertionError(f"Não consegui clicar no refresh: {type(e).__name__}: {e}")

    def get_temp_email_value(self, timeout: int = 20) -> str:
        """
        Espera o input existir e ter um value não-vazio (com '@'), depois retorna o value.
        """
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.EMAIL_INPUT)
        )

        def _value_ready(drv):
            try:
                val = drv.find_element(*self.EMAIL_INPUT).get_attribute("value") or ""
                val = val.strip()
                return val if (val and "@" in val) else False
            except Exception:
                return False

        value = WebDriverWait(self.driver, timeout, poll_frequency=0.5).until(
            _value_ready
        )
        return value

    def switch_to_temp_tab(self):
        """Volta o foco para a aba do temp-mail (sem abrir/fechar nada)."""
        if hasattr(self, "temp_handle"):
            self.driver.switch_to.window(self.temp_handle)

    def switch_to_main_tab(self):
        """Volta o foco para a aba principal (Americanas)."""
        if hasattr(self, "main_handle"):
            self.driver.switch_to.window(self.main_handle)
