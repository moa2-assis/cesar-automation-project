import time
import pytest
import json

from selenium.webdriver.common.by import By
from pages.pages_web.web_home_page import WebHomePage
from pages.pages_web.web_login_page import WebLoginPage
from pages.pages_web.web_temp_mail_page import WebTempMailPage
from pages.pages_web.web_account_page import WebAccountPage

# ### Scenario 7: Login with Incorrect Password

# **Test Steps:**
@pytest.mark.web
def test_login_with_invalid_password(browser, json_data):
    home = WebHomePage(browser)
    login = WebLoginPage(browser)
    account = WebAccountPage(browser)

    valid_email = account.get_last_email()
    incorrect_password = account.get_incorrect_password()
    expected_login_error_message = json_data["web"]["errors"]["incorrect_password"]

    # Step 1: **Access the website:** Open the browser and go to the Americanas website.
    home.open_americanas()
    home.close_banner_if_present()

    # Step 2: **Navigate to Login:** Click on the "Login or Sign Up" option.
    assert home.click_login_link(), "Couldn't click on login link"
    time.sleep(1)
    assert "/login" in browser.current_url.lower() or login.is_visible(By.NAME, "email")

    # Step 3: **Enter Incorrect Credentials:** Fill in the email field with a valid user and enter an incorrect password.
    login.click_to_login_email_password()
    login.type_email_and_password(valid_email, incorrect_password)

    # Step 4: **Perform Login:** Click the "Sign In" button.
    login.click_submit_email_password()

    # Step 5: **Validate Error:** Verify that an appropriate error message (e.g., "Invalid email or password") is displayed and the login is not successful.
    expected_login_error_message = "Usuário e/ou senha incorretos"
    assert login.is_login_error_visible()
    assert (
        login.get_login_error_text() == expected_login_error_message
    ), f"Expected login error message is {expected_login_error_message}, but got {login.get_login_error_text()}."
