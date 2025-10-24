import time
import pytest
from pages.pages_mobile.home_mobile import HomeMobile


@pytest.mark.mobile
def test_mobile_popup_title(driver):
    home_page = HomeMobile(driver)
    time.sleep(6)
