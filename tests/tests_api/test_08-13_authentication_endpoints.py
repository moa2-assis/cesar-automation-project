import time
import pytest

# helpers
def generate_unique_username(base):
    return f"{base}_{int(time.time()*1000)}"

def generate_unique_email_from_username(username):
    return f"{username}@example.com"

# # Test Cases for Authentication Endpoints

# ### Endpoint: POST /auth/register

# ### Scenario 8: Successful User Registration
# - **Objective:** Verify that a new user can be created successfully with a valid email and password.
# - **Steps:**
#   1. Send a POST request to `/auth/register`.
#   2. Provide a unique email (e.g., "testuser@example.com") and a strong password (e.g., "password123") in the request body.
# - **Expected Result:**
#   - The API should respond with a `200 OK` status code.
#   - The response body should contain the user's data, including their ID and the email they registered with, but not the password.
@pytest.mark.api
def test_register_success(
    api_client, base_api_url, json_data, pytestconfig, cleanup_users
):
    url = f"{base_api_url}/auth/register"
    user = json_data["api"]["user"]

    username = generate_unique_username(user["username"])
    email = generate_unique_email_from_username(username)

    payload = {
        "email": email,
        "password": user["password"],
        "username": username,
    }
    resp = api_client.post(url, json=payload)
    print(resp.json())

    assert resp.status_code == 200, resp.text
    assert "id" in resp.json()
    assert resp.json().get("email") == email
    assert "password" not in resp.json()

# ### Scenario 9: Registration with an Existing Email
# - **Objective:** Ensure the API prevents registration with an email that is already in use.
# - **Steps:**
#   1. First, register a user with a specific email (e.g., "existinguser@example.com").
#   2. Send a second POST request to `/auth/register` using the exact same email.
# - **Expected Result:**
#   - The API should respond with a `400 Bad Request` status code.
#   - The response body should contain an error message indicating that the email is already registered (e.g., "Email already registered").
@pytest.mark.api
def test_register_existing_email(api_client, base_api_url, json_data, cleanup_users):
    url = f"{base_api_url}/auth/register"
    user = json_data["api"]["user"]

    username = generate_unique_username("test_user")
    email = generate_unique_email_from_username(username)

    payload = {
        "email": email,
        "password": user["password"],
        "username": username
    }
    resp = api_client.post(url, json=payload)
    print(resp.json())

    assert resp.status_code == 200, resp.text

    last_created_user = {
        "email": email, 
        "password": user["password"], 
        "username": username
        }

    second_resp = api_client.post(url, json=last_created_user)
    assert second_resp.status_code == 400, resp.text

# ### Scenario 10: Registration with Invalid Data
# - **Objective:** Test the API's validation for invalid input during registration.
# - **Steps:**
#   1. Send a POST request to `/auth/register` with an invalid email format (e.g., "not-an-email").
#   2. Send another request without a password field.
# - **Expected Result:**
#   - The API should respond with a `422 Unprocessable Entity` status code for both requests.
#   - The response body should detail the validation error (e.g., "value is not a valid email address" or "field required").
@pytest.mark.api
def test_register_invalid_data(api_client, base_api_url, json_data, cleanup_users):
    url = f"{base_api_url}/auth/register"
    user = json_data["api"]["user"]

    username = generate_unique_username(user["username"])
    email = generate_unique_email_from_username(username)

    payload_invalid_email = {
        "email": "not_an_email", 
        "password": user["password"], 
        "username": username}
    resp = api_client.post(url, json=payload_invalid_email)
    print(resp.json())

    assert resp.status_code == 422, resp.text
    assert resp.json().get("detail") == "Invalid email format"

    payload_empty_password = {
        "email": email,
        "password": "",
        "username": username,
    }
    second_resp = api_client.post(url, json=payload_empty_password)
    print(second_resp.json())

    assert second_resp.status_code == 422, second_resp.text
    assert second_resp.json().get("detail") == "Missing data"

# ---

# ## Endpoint: POST /auth/login


# ### Scenario 11: Successful Login
# - **Objective:** Verify that a registered user can log in with correct credentials.
# - **Steps:**
#   1. Ensure a user is already registered (e.g., "loginuser@example.com" with password "correct_password").
#   2. Send a POST request to `/auth/login` using the registered email as the `username` and the correct password.
# - **Expected Result:**
#   - The API should respond with a `200 OK` status code.
#   - The response body should contain an `access_token` (JWT) and a `token_type` of "bearer".
@pytest.mark.api
def test_login_valid_credentials(api_client, base_api_url, json_data, cleanup_users):
    url_register = f"{base_api_url}/auth/register"
    user = json_data["api"]["user"]

    username = generate_unique_username("test_user")
    email = generate_unique_email_from_username(username)

    payload = {"email": email, "password": user["password"], "username": username}
    register_resp = api_client.post(url_register, json=payload)
    print(register_resp.json())

    assert register_resp.status_code == 200, register_resp.text

    last_created_user = {
        "email": email,
        "password": user["password"],
        "username": username,
    }

    payload_login = {
        "email": last_created_user["email"],
        "password": last_created_user["password"]
    }

    url_login = f"{base_api_url}/auth/login"
    login_resp = api_client.post(url_login, json=payload_login)
    print(login_resp.json())

    assert login_resp.status_code in (200, 201), login_resp.text
    assert "access_token" in login_resp.json()
    assert "token_type" in login_resp.json()
    assert login_resp.json().get("token_type") == "bearer"

# ### Scenario 12: Login with Incorrect Password
# - **Objective:** Ensure the API denies access if the password is incorrect.
# - **Steps:**
#   1. Use the credentials of a registered user (e.g., "loginuser@example.com").
#   2. Send a POST request to `/auth/login` with the correct email but an incorrect password (e.g., "wrong_password").
# - **Expected Result:**
#   - The API should respond with a `401 Unauthorized` status code.
#   - The response body should contain an error message like "Incorrect email or password".
@pytest.mark.api
def test_login_incorrect_credentials(
    api_client, base_api_url, json_data, cleanup_users
):
    url_register = f"{base_api_url}/auth/register"
    user = json_data["api"]["user"]

    username = generate_unique_username("test_user")
    email = generate_unique_email_from_username(username)

    payload = {"email": email, "password": user["password"], "username": username}
    register_resp = api_client.post(url_register, json=payload)
    print(register_resp.json())

    assert register_resp.status_code == 200, register_resp.text

    last_created_user = {
        "email": email,
        "password": user["password"],
        "username": username,
    }

    payload_login = {
        "email": last_created_user["email"],
        "password": "this_in_incorrect_password",
    }

    url_login = f"{base_api_url}/auth/login"
    login_resp = api_client.post(url_login, json=payload_login)
    print(login_resp.json())

    assert login_resp.status_code in (400, 401), login_resp.text
    assert login_resp.json().get("detail") == "Incorrect email or password"

# ### Scenario 13: Login with Non-Existent User
# - **Objective:** Ensure the API denies access if the user does not exist.
# - **Steps:**
#   1. Send a POST request to `/auth/login` with an email that has not been registered (e.g., "nouser@example.com").
# - **Expected Result:**
#   - The API should respond with a `401 Unauthorized` status code.
#   - The response body should contain an error message like "Incorrect email or password".
# ---
@pytest.mark.api
def test_login_nonexistent_user(api_client, base_api_url, json_data, cleanup_users):
    
    payload_login = {
        "email": "unregistered_email@for.this.scenario",
        "password": "this_is_a_password"
    }

    url_login = f"{base_api_url}/auth/login"
    login_resp = api_client.post(url_login, json=payload_login)
    print(login_resp.json())

    assert login_resp.status_code in (400, 401), login_resp.text
    assert login_resp.json().get("detail") == "Incorrect email or password"
