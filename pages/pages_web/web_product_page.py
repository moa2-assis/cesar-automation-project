from selenium.webdriver.common.by import By
from pages.pages_web.web_base_page import WebBasePage


class WebProductPage(WebBasePage):
    PRODUCT_TITLE = (By.CSS_SELECTOR, "h1[class^='ProductInfoCenter_title__']")
    PRODUCT_PRICE = (By.CSS_SELECTOR, "div[class^='ProductPrice_productPrice__']")

    def get_product_title(self):
        return self.get_text(*self.PRODUCT_TITLE)

    def get_product_price(self):
        return self.get_text(*self.PRODUCT_PRICE)
