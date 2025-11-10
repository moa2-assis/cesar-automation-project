# pages/pages_web/home_web.py
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)

from pages.pages_web.web_base_page import WebBasePage

class WebHomePage(WebBasePage):
    SEARCH_INPUT = (By.ID, "search-input")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    BODY = (By.TAG_NAME, "body")

    HOME_TOP_BANNER_LINK = (By.CSS_SELECTOR, "a[aria-label*='banner de topo']")

    BANNER = (By.ID, "ins-responsive-banner")
    BANNER_CLOSE = (By.CSS_SELECTOR, "#ins-responsive-banner svg.show-element")

    LOGIN_HEADER = (
        By.CSS_SELECTOR,
        "a[class*='ButtonLogin_Container__'][href^='/login']",
    )

    ACCOUNT_HEADER = (
        By.CSS_SELECTOR,
        "div[class*='ButtonLogin_textContainer__'] span"
    )

    def click_login_link(self) -> bool:
        try:
            el = self.wait.until(EC.element_to_be_clickable(self.LOGIN_HEADER))
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", el
            )
            try:
                el.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", el)
            return True
        except Exception:
            return False

    def open_americanas(self):
        self.open("https://www.americanas.com.br/")

    def is_on_homepage(self):
        try:
            self.wait.until(
                EC.presence_of_element_located(self.HOME_TOP_BANNER_LINK)
            )
            return True
        except Exception:
            return False

    def type_query(self, text):
        try:
            self.type(*self.SEARCH_INPUT, text=text)
            return True
        except Exception:
            return False

    def close_banner_if_present(self) -> bool:
        """
        Fecha o banner Insider (id começa com ins-responsive-banner-).
        Retorna True se fechou, False se não encontrou/Não foi necessário.
        """
        try:
            banner = self.wait.until(EC.presence_of_element_located(self.BANNER))
        except Exception:
            return False  # não apareceu

        # tenta clicar no wrapper (filho direto) primeiro
        try:
            wrap = banner.find_element(By.CSS_SELECTOR, ":scope > div[id^='wrap-close-button-']")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", wrap)
            try:
                wrap.click()
                return True
            except Exception:
                self.driver.execute_script("arguments[0].click();", wrap)
                return True
        except Exception:
            pass

        # tenta o botão interno com id dinâmico
        try:
            btn = banner.find_element(By.CSS_SELECTOR, ":scope div[id^='close-button-']")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            try:
                btn.click()
                return True
            except Exception:
                self.driver.execute_script("arguments[0].click();", btn)
                return True
        except Exception:
            pass

        # fallback: o SVG do X
        try:
            svgx = banner.find_element(By.CSS_SELECTOR, ":scope svg.show-element")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", svgx)
            try:
                svgx.click()
                return True
            except Exception:
                self.driver.execute_script("arguments[0].click();", svgx)
                return True
        except Exception:
            pass

    def wait_search_input_visibility(self):
        try:
            americanas_icon = self.wait.until(
                EC.presence_of_element_located(self.SEARCH_INPUT)
            )
            return True
        except Exception:
            return False 

    def get_user_logged_email(self):
        el = self.wait_for_visibility(*self.ACCOUNT_HEADER)
        text = (el.text or "").strip()

        # regex para email
        m = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        return (m.group(0) if m else text.splitlines()[-1]).strip().lower()

    def click_my_account(self):
        el = self.wait_for_visibility(*self.ACCOUNT_HEADER)
        el.click()

    def click_search(self):
        self.click(*self.SEARCH_BUTTON)
