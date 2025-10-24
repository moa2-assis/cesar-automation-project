# pages/pages_mobile/mobile_base_page.py
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage


class MobileBasePage(BasePage):
    """Extensões específicas para Appium/Android."""

    # UiSelector helpers (Android)
    def click_by_text(self, text: str):
        self.click(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')

    def click_by_text_contains(self, substr: str):
        self.click(
            AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{substr}")'
        )

    # Notifications (Android)
    def open_notifications(self):
        self.driver.open_notifications()

    def is_notification_displayed(self, expected_title: str) -> bool:
        try:
            locator = (
                AppiumBy.XPATH,
                f"//*[@resource-id='android:id/title' and @text='{expected_title}']",
            )
            self.wait_for_visibility(*locator)
            return True
        except TimeoutException:
            return False
        finally:
            # fecha a shade se estiver aberta
            try:
                self.driver.back()
            except Exception:
                pass

    def get_notification_text(self, expected_title: str):
        try:
            title_el = self.wait_for_visibility(
                AppiumBy.XPATH,
                f"//*[@resource-id='android:id/title' and @text='{expected_title}']",
            )
            return title_el.find_element(
                AppiumBy.XPATH, "following-sibling::*[@resource-id='android:id/text']"
            ).text
        except Exception:
            return None
        finally:
            try:
                self.driver.back()
            except Exception:
                pass

    # Gestures
    def scroll_screen_down(self, percent: float = 0.8):
        size = self.driver.get_window_size()
        self.driver.execute_script(
            "mobile: scrollGesture",
            {
                "left": 0,
                "top": size["height"] * 0.3,
                "width": size["width"],
                "height": size["height"] * 0.5,
                "direction": "down",
                "percent": percent,
            },
        )
        time.sleep(0.4)

    def scroll_screen_up(self, percent: float = 0.8):
        size = self.driver.get_window_size()
        self.driver.execute_script(
            "mobile: scrollGesture",
            {
                "left": 0,
                "top": size["height"] * 0.3,
                "width": size["width"],
                "height": size["height"] * 0.5,
                "direction": "up",
                "percent": percent,
            },
        )
        time.sleep(0.4)
