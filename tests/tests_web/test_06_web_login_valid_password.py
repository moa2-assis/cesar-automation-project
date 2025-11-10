import time
import pytest
import json

from selenium.webdriver.common.by import By
from pages.pages_web.web_home_page import WebHomePage
from pages.pages_web.web_login_page import WebLoginPage
from pages.pages_web.web_temp_mail_page import WebTempMailPage
from pages.pages_web.web_account_page import WebAccountPage

### Scenario 6: Login via Password

# **Objective:** To validate the login flows for an existing user, both successful and failed.

# **Test Steps:**
@pytest.mark.web
def test_web_login_with_valid_password(browser, json_data):
    home = WebHomePage(browser)
    login = WebLoginPage(browser)
    account = WebAccountPage(browser)

    valid_email = account.get_last_email()
    correct_password = account.get_last_password()


    # Step 1: **Access the website:** Open the browser and go to the Americanas website.
    home.open_americanas()
    home.close_banner_if_present()

    # Step 2: **Navigate to Login:** Click on the "Login or Sign Up" option.
    assert home.click_login_link(), "Couldn't click on login link"
    time.sleep(1)
    assert "/login" in browser.current_url.lower() or login.is_visible(By.NAME, "email")

    # Step 3: **Enter Correct Credentials:** Fill in the fields with a valid and already registered email and password.
    login.click_to_login_email_password()
    login.type_email_and_password(valid_email, correct_password)

    # Step 4: **Perform Login:** Click the "Sign In" button.
    login.click_submit_email_password()

    # Step 5: **Validate Login:** Confirm the redirect to the homepage and that the user's email is displayed in the header.
    assert home.wait_search_input_visibility(), f"Search input not found."
    assert home.is_on_homepage(), f"Website isn't at homepage."
    home.close_banner_if_present()
    actual_homepage_mail = home.get_user_logged_email()
    assert (
        actual_homepage_mail == valid_email
    ), f"Expected email in homepage is {valid_email}, but got {actual_homepage_mail}."
