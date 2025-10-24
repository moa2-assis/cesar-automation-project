import time
import pytest
from selenium.webdriver.common.by import By
from pages.pages_web.web_home_page import WebHomePage
from pages.pages_web.web_login_page import WebLoginPage
from pages.pages_web.web_temp_mail_page import WebTempMailPage

# ### Scenario 1: New User Registration and Password Setup

# **Objective:** To validate the complete flow of creating a new account, setting a password, and validating the data.

# **Test Steps:**

# 1.  **Access the website:** Open the browser and go to the Americanas website.
# 2.  **Navigate to Registration:** Click on the "Login or Sign Up" option.
# 3.  **Generate Temporary Email:** In a new tab, go to `https://temp-mail.io/` and copy the generated email.
# 4.  **Enter Email:** Return to the Americanas website, enter the temporary email in the registration field, and click to send the verification code.
# 5.  **Get Code:** Go back to the `temp-mail` website, open the received email, and copy the verification code.
# 6.  **Confirm Registration:** Return to the Americanas website and enter the code to finalize the registration.
# 7.  **Verify Redirect:** Confirm that you have been redirected to the homepage.
# 8.  **Validate Login:** Check if the new user's email is displayed in the page header.
# 9.  **Access My Account:** Open the "My Account" menu and confirm that the email in the registration tab is correct.
# 10. **Start Password Setup:** Navigate to the authentication section and select "Set Password".
# 11. **Enter Password Code:** Get the new code sent to `temp-mail` and enter it in the corresponding field.
# 12. **Test Password Rules:**
#     *   Try to save a password with less than 8 characters. The "Save" button should be inactive.
#     *   Try to save a password without numbers. The "Save" button should be inactive.
#     *   Try to save a password without lowercase letters. The "Save" button should be inactive.
#     *   Try to save a password without uppercase letters. The "Save" button should be inactive.
# 13. **Set Valid Password:** Enter a password that meets all criteria and click "Save Password".
# 14. **Validate success:** Validate that the password was saved successfully (just validate that the sequence of asterisks appeared on the screen).

@pytest.mark.web
def test_web_new_user_registration_password_setup(browser):
    home = WebHomePage(browser)
    login = WebLoginPage(browser)
    temp_mail = WebTempMailPage(browser)

    home.open_americanas()
    home.close_banner_if_present()
    assert home.click_login_link(), "Couldn't click on login link"
    time.sleep(1)
    assert "/login" in browser.current_url.lower() or login.is_visible(By.NAME, "email")

    temp_mail.open_temp_mail_in_new_tab()
    temp_mail_saved = temp_mail.get_temp_email_value()

    time.sleep(1)
    temp_mail.switch_to_main_tab()

    # 4) preenche e envia (ajuste os locators se preciso)
    assert login.type_email(temp_mail_saved), "Email field didnt' receive text."
    assert login.click_submit_email(), "Submit email button not clicked."
    time.sleep(1)

    temp_mail.switch_to_temp_tab()
    time.sleep(3)
    temp_mail.click_refresh_button()
    time.sleep(2)
    temp_mail.wait_subjects_present()
    subject_el = temp_mail.wait_subject_with_phrase("código de acesso", timeout=40)
    temp_token_saved = temp_mail.get_access_code()
    temp_mail.switch_to_main_tab()

    assert login.type_token(temp_token_saved), "Token field didn't receive text."
    assert login.click_submit_token(), "Submit token button not clicked."
    time.sleep(5)

    
