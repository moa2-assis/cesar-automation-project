# pages/pages_mobile/mobile_search_results_page.py
import re
from typing import Optional, Tuple, List

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from pages.pages_mobile.mobile_base_page import MobileBasePage


class MobileSearchResultsPage(MobileBasePage):
    PRODUCT_PRICE = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("{}")')
    
    FILTER_BUTTON = (AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().resourceId('Filtrar')")
    
    def click_grid_list_button(self):
        # parent =
        return 0

    def _get_desc(self, el):
        return (el.get_attribute("contentDescription") or "").strip()

    def _split_lines(self, desc):
        return [ln.strip() for ln in (desc or "").split("\n") if ln.strip()]

    def _is_price_line(self, ln):
        return "R$" in (ln or "")

    def _pick_title_from_desc(self, desc):
        lines = self._split_lines(desc)
        text_lines = [
            ln
            for ln in lines
            if not self._is_price_line(ln)
            and "%" not in ln
            and "à vista" not in ln.lower()
        ]
        if not text_lines:
            return ""
        return max(text_lines, key=len)

    def _extract_all_prices(self, desc):
        # procurar por números em formato de dinheiro tipo “R$ 1.234,56”
        return re.findall(r"R\$[\s]*[\d\.]+,[\d]{2}", desc or "")

    def _pick_best_price_from_desc(self, desc):
        # procura por "à vista"
        for ln in self._split_lines(desc):
            if (
                self._is_price_line(ln)
                and "vista" in ln.lower()
                and not self._looks_like_parcel(ln)
            ):
                return ln
        # senão, último formato de valor válido que não seja de parcelas
        candidates = [
            ln
            for ln in self._split_lines(desc)
            if self._is_price_line(ln) and not self._looks_like_parcel(ln)
        ]
        if candidates:
            return candidates[-1]
        # fallback (regex bruto) em último caso
        all_prices = self._extract_all_prices(desc)
        return all_prices[-1] if all_prices else None

    # ======== API pública ========

    def wait_results_loaded(self):
        try:
            if self.is_empty_search(timeout=2):
                return True
            self.wait_for_visibility(*self.CARD_ANY_PRICE)
            return True
        except TimeoutException:
            return False

    def is_empty_search(self):
        for hint in self.EMPTY_HINTS:
            try:
                locator = (
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiSelector().textContains("{hint}")',
                )
                if self.is_visible(*locator):
                    return True
            except Exception:
                continue
        return False

    def find_card_by_name_contains(self, name_fragment: str, max_scrolls: int = 6):
        frag = (name_fragment or "").strip()
        if not frag:
            return None

        # Primeiro tenta sem scroll
        try:
            return self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().descriptionContains("{frag}")',
            )
        except Exception:
            pass

        # Faz scroll e tenta novamente
        for _ in range(max_scrolls):
            try:
                el = self.driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiSelector().descriptionContains("{frag}")',
                )
                return el
            except NoSuchElementException:
                self.scroll_screen_down(0.7)
            except Exception:
                self.scroll_screen_down(0.7)

        return None

    def get_first_card(self):
        """Retorna o primeiro card com preço na tela (se existir)."""
        try:
            return self.driver.find_element(*self.CARD_ANY_PRICE)
        except Exception:
            return None

    def get_card_title_and_price(self, card_el) -> Tuple[str, Optional[str]]:
        """
        Extrai (title, raw_price_line) de um card.
        - title: texto purificado do possible título
        - raw_price_line: linha bruta contendo 'R$ ...' (pode incluir 'à vista')
        """
        desc = self._get_desc(card_el)
        title = self._pick_title_from_desc(desc)
        price_raw = self._pick_best_price_from_desc(desc)
        return title, price_raw

    def normalize_price_str(self, price_raw: Optional[str]) -> str:
        """Normaliza 'R$ 1.234,56' → '123456' (igual Web)."""
        if not price_raw:
            return ""
        # Reuso do helper do MobileBasePage
        norm = self.normalize_price(price_raw)
        # garantir só dígitos, caso algo escape
        return re.sub(r"\D", "", norm)

    def open_card(self, card_el) -> bool:
        """Abre o produto tocando no card (com fallback por coordenada)."""
        try:
            card_el.click()
            return True
        except Exception:
            try:
                rect = card_el.rect
                x = rect["x"] + rect["width"] // 2
                y = rect["y"] + rect["height"] // 2
                self.driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
                return True
            except Exception:
                return False
