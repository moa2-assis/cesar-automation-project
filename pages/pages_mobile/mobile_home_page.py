# pages/pages_mobile/home_mobile.py
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from pages.pages_mobile.mobile_base_page import MobileBasePage
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

class MobileHome(MobileBasePage):
    SEARCH_INPUT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("busque aqui seu produto")')

    def accept_runtime_permissions(
        self, duration: float = 15.0, interval: float = 0.4
    ):
        selectors = [
            'new UiSelector().resourceId("com.android.permissioncontroller:id/permission_allow_foreground_only_button")',
            'new UiSelector().resourceId("com.android.permissioncontroller:id/permission_allow_button")',
        ]

        end = time.time() + duration
        clicks = 0

        while time.time() < end:
            clicked = False
            for sel in selectors:
                try:
                    el = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, sel)
                    el.click()
                    clicks += 1
                    clicked = True
                    # dá um respiro curtinho só quando clicou
                    time.sleep(0.2)
                    break
                except NoSuchElementException:
                    continue
                except Exception:
                    # qualquer outra zica, ignora e tenta de novo
                    pass

            if not clicked:
                time.sleep(interval)

        return clicks

    def is_on_home(self):
        return self.is_visible(*self.SEARCH_INPUT)

    def focus_search(self):
        try:
            el = self.wait_for_visibility(*self.SEARCH_INPUT)
            el.click()
            return True
        except Exception as e:
            print(f"[FOCUS_SEARCH] error focusing field: {e}")
            try:
                self.scroll_screen_down(0.4)
                el = self.find_by_desc_contains("busque")
                el.click()
                return True
            except Exception as e2:
                print(f"[FOCUS_SEARCH] second attempt failed: {e2}")
                return False

    def type_query(self, text):
        try:
            el = self.wait_for_visibility(*self.SEARCH_INPUT)
            el.clear()
            el.send_keys(text)
            return True
        except Exception as e:
            print(f"[TYPE_QUERY] error when typing '{text}': {e}")
            return False

    def submit_search(self):
        try:
            self.press_enter()
            return True
        except Exception as e:
            print(f"[SUBMIT_SEARCH] fail on ENTER: {e}")
            try:
                el = self.find_by_desc_contains("busque")
                el.send_keys("\n")
                return True
            except Exception:
                return False
