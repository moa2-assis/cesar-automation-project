import time
import pytest
from selenium.webdriver.common.by import By
from pages.pages_web.web_home_page import HomeWeb


@pytest.mark.web
def test_web_open_americanas(browser):
    home_page = HomeWeb(browser)
    home_page.open_americanas()
    time.sleep(2)
    home_page.type_query("oi")
    time.sleep(2)
    assert home_page.is_visible(By.TAG_NAME, "body")
