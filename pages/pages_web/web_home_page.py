# pages/pages_web/home_web.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)

from pages.pages_web.web_base_page import WebBasePage
from pages.pages_web.web_login_page import WebLoginPage

class WebHomePage(WebBasePage):
    SEARCH_INPUT = (By.ID, "search-input")
    BODY = (By.TAG_NAME, "body")

    BANNER = (By.ID, "ins-responsive-banner")
    BANNER_CLOSE = (By.CSS_SELECTOR, "#ins-responsive-banner svg.show-element")

    LOGIN_LINK = (
        By.CSS_SELECTOR,
        "a[class*='ButtonLogin_Container__'][href^='/login']",
    )

    def click_login_link(self) -> bool:
        try:
            el = self.wait.until(EC.element_to_be_clickable(self.LOGIN_LINK))
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

    def type_query(self, text: str):
        self.type(*self.SEARCH_INPUT, text=text)

    def try_click_normal_then_js(self, by, locator) -> bool:
        try:
            self.click(by, locator)
            return True
        except Exception:
            try:
                self.js_click(by, locator)
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
