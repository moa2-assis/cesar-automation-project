import time
import pytest
import json

from selenium.webdriver.common.by import By
from pages.pages_web.web_home_page import WebHomePage
from pages.pages_web.web_login_page import WebLoginPage
from pages.pages_web.web_temp_mail_page import WebTempMailPage
from pages.pages_web.web_account_page import WebAccountPage

# ### Scenario 1: New User Registration and Password Setup

# **Objective:** To validate the complete flow of creating a new account, setting a password, and validating the data.

# **Test Steps:**

@pytest.mark.web
def test_web_new_user_registration_password_setup(browser, json_data):
    home = WebHomePage(browser)
    login = WebLoginPage(browser)
    temp_mail = WebTempMailPage(browser)
    account = WebAccountPage(browser)

    # Step 1: **Access the website:** Open the browser and go to the Americanas website.
    home.open_americanas()
    home.close_banner_if_present()

    # Step 2: **Navigate to Registration:** Click on the "Login or Sign Up" option.
    assert home.click_login_link(), "Couldn't click on login link"
    time.sleep(1)
    assert "/login" in browser.current_url.lower() or login.is_visible(By.NAME, "email")

    # Step 3: **Generate Temporary Email:** In a new tab, go to `https://temp-mail.io/` and copy the generated email.
    temp_mail.open_temp_mail_in_new_tab()
    temp_mail_saved = temp_mail.get_temp_email_value()

    time.sleep(1)
    temp_mail.switch_to_main_tab()

    # Step 4: **Enter Email:** Return to the Americanas website, enter the temporary email in the registration field, and click to send the verification code.
    assert login.type_email(temp_mail_saved), "Email field didnt' receive text."
    assert login.click_submit_email(), "Submit email button not clicked."
    time.sleep(1)

    # Step 5: **Get Code:** Go back to the `temp-mail` website, open the received email, and copy the verification code.
    temp_mail.switch_to_temp_tab()
    time.sleep(3)
    temp_mail.click_refresh_button()
    time.sleep(2)
    temp_mail.wait_subjects_present()
    subject_el = temp_mail.wait_subject_with_phrase("código de acesso", timeout=40)
    login_temp_token_saved = temp_mail.get_fresh_access_code()

    # Step 6: **Confirm Registration:** Return to the Americanas website and enter the code to finalize the registration.
    temp_mail.switch_to_main_tab()
    assert login.type_token(login_temp_token_saved), "Token field didn't receive text."
    assert login.click_submit_token(), "Submit token button not clicked."

    # Step 7: **Verify Redirect:** Confirm that you have been redirected to the homepage.
    assert home.wait_search_input_visibility(), f"Search input not found."
    assert "https://www.americanas.com.br/" == browser.current_url.lower(), f"Website isn't at homepage."

    # Step 8: **Validate Login:** Check if the new user's email is displayed in the page header.
    # temp_mail_saved
    home.close_banner_if_present()
    actual_homepage_mail = home.get_user_logged_email()
    assert (
        actual_homepage_mail == temp_mail_saved
    ), f"Expected email in homepage is {temp_mail_saved}, but got {actual_homepage_mail}."

    # Step 9: **Access My Account:** Open the "My Account" menu and confirm that the email in the registration tab is correct.
    home.click_my_account()
    actual_accountpage_mail = account.get_user_logged_email()
    assert (actual_accountpage_mail == temp_mail_saved), f"Expected email in account page is {temp_mail_saved}, but got {actual_accountpage_mail}."

    # Step 10: **Start Password Setup:** Navigate to the authentication section and select "Set Password".
    assert account.click_authentication()
    assert account.click_set_password()

    # Step 11: **Enter Password Code:** Get the new code sent to `temp-mail` and enter it in the corresponding field.
    temp_mail.switch_to_temp_tab()
    temp_mail.click_refresh_button()
    time.sleep(2)
    password_temp_token = temp_mail.get_fresh_access_code()
    temp_mail.switch_to_main_tab()

    account.type_access_code(password_temp_token)

    # Step 12: **Test Password Rules:**
    #     *   Try to save a password with less than 8 characters. The "Save" button should be inactive.
    account.type_password(json_data["web"]["invalid_passwords"]["lessthan8char"])
    time.sleep(1)
    assert not account.is_save_password_enabled()

    #     *   Try to save a password without numbers. The "Save" button should be inactive.
    account.type_password(json_data["web"]["invalid_passwords"]["nonumbers"])
    time.sleep(1)
    assert not account.is_save_password_enabled()

    #     *   Try to save a password without lowercase letters. The "Save" button should be inactive.
    account.type_password(json_data["web"]["invalid_passwords"]["nolowercase"])
    time.sleep(1)
    assert not account.is_save_password_enabled()

    #     *   Try to save a password without uppercase letters. The "Save" button should be inactive.
    account.type_password(json_data["web"]["invalid_passwords"]["nouppercase"])
    time.sleep(1)
    assert not account.is_save_password_enabled()

    # Step 13: **Set Valid Password:** Enter a password that meets all criteria and click "Save Password".
    account.type_password(json_data["web"]["valid_password"])
    time.sleep(1)
    assert account.is_save_password_enabled()
    account.click_save_password()
    time.sleep(3)

    # Step 14: **Validate success:** Validate that the password was saved successfully (just validate that the sequence of asterisks appeared on the screen).
    new_password_masked = account.get_masked_password()
    assert new_password_masked != "", "Masked password text not found!"
    assert set(new_password_masked) == {
        "*"
    }, f"Masked password should only contain asterisks but got: {new_password_masked}"
