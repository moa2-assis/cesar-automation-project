# pages/pages_mobile/home_mobile.py
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from pages.pages_mobile.mobile_base_page import MobileBasePage
from selenium.common.exceptions import TimeoutException
import time

class HomeMobile(MobileBasePage):
    # permission title locator
    PERMISSION_TITLE = 'new UiSelector().resourceId("com.android.permissioncontroller:id/permission_message")'

    # location locators
    PERMISSION_WHILE_USING_APP = 'new UiSelector().resourceId("com.android.permissioncontroller:id/permission_allow_foreground_only_button")'
    PERMISSION_ONLY_THIS_TIME = 'new UiSelector().resourceId("com.android.permissioncontroller:id/permission_allow_one_time_button")'
    PERMISSION_DONT_ALLOW = 'new UiSelector().resourceId("com.android.permissioncontroller:id/permission_deny_button")'

    # send notification locators
    PERMISSION_NOTIFICATION_ALLOW = 'new UiSelector().resourceId("com.android.permissioncontroller:id/permission_allow_button")'
    PERMISSION_NOTIFICATION_DONTALLOW = 'new UiSelector().resourceId("com.android.permissioncontroller:id/permission_deny_button")'

    # localization permission
    def wait_permission_title(self):
        self.wait_for_visibility(AppiumBy.ANDROID_UIAUTOMATOR, self.PERMISSION_TITLE)

    def allow_location_permission_while_using(self):
        self.click(AppiumBy.ANDROID_UIAUTOMATOR, self.PERMISSION_WHILE_USING_APP)
        time.sleep(1)

    # send notification permission
    def allow_notification_permission(self):
        self.click(AppiumBy.ANDROID_UIAUTOMATOR, self.PERMISSION_NOTIFICATION_ALLOW)
        time.sleep(1)
