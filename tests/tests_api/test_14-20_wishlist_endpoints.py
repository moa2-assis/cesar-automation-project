import time
import pytest

# helpers
def get_token_from_new_user(api_client, base_api_url):
    username = f"test_user_{int(time.time() * 1000)}"
    email = f"{username}@example.com"
    password = "password123"

    reg_url = f"{base_api_url}/auth/register"
    reg_payload = {"username": username, "email": email, "password": password}
    reg_resp = api_client.post(reg_url, json=reg_payload)
    assert reg_resp.status_code == 200, f"Failed to register: {reg_resp.text}"

    login_url = f"{base_api_url}/auth/login"
    login_payload = {"email": email, "password": password}
    login_resp = api_client.post(login_url, json=login_payload)
    assert login_resp.status_code in (200, 201), f"Failed to login: {login_resp.text}"

    token = login_resp.json().get("access_token")
    assert token, "Token not returned by the API"

    # cleanups
    api_client.last_token = token

    return token

# # Test Cases for Wishlist Endpoints

# ### Endpoint: POST /wishlists

# ### Scenario 14: Successfully Create a Wishlist
# - **Objective:** Verify that an authenticated user can create a new wishlist.
# - **Prerequisites:** User must be authenticated (have a valid JWT token).
# - **Steps:**
#   1. Send a POST request to `/wishlists` with a valid authentication token in the header.
#   2. Provide a `name` for the wishlist in the request body (e.g., {"name": "My Tech Gadgets"}).
# - **Expected Result:**
#   - The API should respond with a `200 OK` status code.
#   - The response body should contain the newly created wishlist object, including its `id`, `name`, and the `owner_id`.
@pytest.mark.api
def test_wishlist_create_success(api_client, base_api_url, json_data, cleanup_users):
    login_token = get_token_from_new_user(api_client, base_api_url)
    headers = {"Authorization": f"Bearer {login_token}"}
    url_wishlists = f"{base_api_url}/wishlists"
    payload_wishlists = {
        "name": "Society Sneakers"
    }
    
    wishlist_resp = api_client.post(
        url_wishlists, headers=headers, json=payload_wishlists
    )
    print(wishlist_resp.json())
    assert wishlist_resp.status_code == 200, wishlist_resp.text
    assert "id" in wishlist_resp.json(), "Couldn't find the 'id' field"
    assert "name" in wishlist_resp.json(), "Couldn't find the 'name' field"
    assert "owner_id" in wishlist_resp.json(), "Couldn't find the 'owner_id' field"


# ### Scenario 15: Create a Wishlist with a Duplicate Name
# - **Objective:** Verify that a user can't create multiple wishlists with the same name.
# - **Prerequisites:** User must be authenticated.
# - **Steps:**
#   1. Create a wishlist with a specific name (e.g., "Travel Plans").
#   2. Send another POST request to `/wishlists` with the same name.
# - **Expected Result:**
#   - The API should respond with a `409 Conflict` status code.
#   - A new wishlist should not be created with a different `id`.
@pytest.mark.api
def test_wishlist_create_duplicate_name(
    api_client, base_api_url, json_data, cleanup_users
):
    login_token = get_token_from_new_user(api_client, base_api_url)
    headers = {"Authorization": f"Bearer {login_token}"}
    url_wishlists = f"{base_api_url}/wishlists"
    payload_wishlists = {"name": "Society Sneakers"}

    wishlist_resp = api_client.post(
        url_wishlists, headers=headers, json=payload_wishlists
    )
    print(wishlist_resp.json())
    assert wishlist_resp.status_code == 200, wishlist_resp.text

    duplicate_payload_wishlists = {"name": "Society Sneakers"}
    duplicate_wishlist_resp = api_client.post(
        url_wishlists, headers=headers, json=duplicate_payload_wishlists
    )
    print(duplicate_wishlist_resp.json())
    assert duplicate_wishlist_resp.status_code == 409, wishlist_resp.text


# ### Scenario 16: Create a Wishlist without Authentication
# - **Objective:** Ensure that an unauthenticated user cannot create a wishlist.
# - **Steps:**
#   1. Send a POST request to `/wishlists` without an authentication token.
# - **Expected Result:**
#   - The API should respond with a `401 Unauthorized` status code.
#   - The response body should contain an error detail like "Not authenticated".
@pytest.mark.api
def test_wishlist_create_unauthenticated(
    api_client, base_api_url, json_data, cleanup_users
):
    url_wishlists = f"{base_api_url}/wishlists"
    payload_wishlists = {"name": "Society Sneakers"}

    wishlist_resp = api_client.post(
        url_wishlists, json=payload_wishlists
    )
    print(wishlist_resp.json())
    assert wishlist_resp.status_code == 401, wishlist_resp.text
    assert wishlist_resp.json().get("detail") == "Not authenticated"


# ### Scenario 17: Create a Wishlist with Invalid Data
# - **Objective:** Test validation when creating a wishlist with no name.
# - **Prerequisites:** User must be authenticated.
# - **Steps:**
#   1. Send a POST request to `/wishlists` with an empty request body {}.
# - **Expected Result:**
#   - The API should respond with a `422 Unprocessable Entity` status code.
#   - The response should detail the validation error (e.g., "field required").
@pytest.mark.api
def test_wishlist_create_invalid_data(
    api_client, base_api_url, json_data, cleanup_users
):
    login_token = get_token_from_new_user(api_client, base_api_url)
    headers = {"Authorization": f"Bearer {login_token}"}

    url_wishlists = f"{base_api_url}/wishlists"
    payload_wishlists = {"name": ""}

    wishlist_resp = api_client.post(
        url_wishlists, headers=headers, json=payload_wishlists
    )
    print(wishlist_resp.json())
    assert wishlist_resp.status_code == 422, wishlist_resp.text
    assert wishlist_resp.json().get("detail") == "Missing name"


# --------------------------------------
# ## Endpoint: GET /wishlists
# --------------------------------------


# ### Scenario 18: Successfully Retrieve All Wishlists
# - **Objective:** Verify that an authenticated user can retrieve all of their wishlists.
# - **Prerequisites:** User must be authenticated and have one or more wishlists.
# - **Steps:**
#   1. Send a GET request to `/wishlists` with a valid authentication token.
# - **Expected Result:**
#   - The API should respond with a `200 OK` status code.
#   - The response body should be a JSON array containing all wishlists owned by the user.
@pytest.mark.api
def test_wishlists_get_all_success(api_client, base_api_url, json_data, cleanup_users):
    login_token = get_token_from_new_user(api_client, base_api_url)
    headers = {"Authorization": f"Bearer {login_token}"}
    url_wishlists = f"{base_api_url}/wishlists"
    payload_wishlists1 = {"name": "Society Sneakers"}
    payload_wishlists2 = {"name": "Mountain Shoes"}

    wishlist1_resp = api_client.post(
        url_wishlists, headers=headers, json=payload_wishlists1
    )
    assert wishlist1_resp.status_code == 200, wishlist1_resp.text
    print(wishlist1_resp.json())
    wishlist2_resp = api_client.post(
        url_wishlists, headers=headers, json=payload_wishlists2
    )
    assert wishlist2_resp.status_code == 200, wishlist2_resp.text
    print(wishlist2_resp.json())

    get_resp = api_client.get(url_wishlists, headers=headers)
    wishlists = get_resp.json()
    print(get_resp.json())

    found_names = []
    for item_name in wishlists:
        name = item_name["name"]
        found_names.append(name)

    expected_names = {"Society Sneakers", "Mountain Shoes"}
    for name in expected_names:
        assert name in found_names, f"Wishlist '{name}' not found"


# ### Scenario 19: Retrieve Wishlists When None Exist
# - **Objective:** Verify the response when a user has no wishlists.
# - **Prerequisites:** User must be authenticated but have no wishlists created.
# - **Steps:**
#   1. Send a GET request to `/wishlists` with a valid authentication token.
# - **Expected Result:**
#   - The API should respond with a `200 OK` status code.
#   - The response body should be an empty JSON array [].
@pytest.mark.api
def test_wishlists_get_empty(api_client, base_api_url, json_data, cleanup_users):
    login_token = get_token_from_new_user(api_client, base_api_url)
    headers = {"Authorization": f"Bearer {login_token}"}
    url_wishlists = f"{base_api_url}/wishlists"

    get_resp = api_client.get(url_wishlists, headers=headers)
    wishlists = get_resp.json()
    print(wishlists)
    assert get_resp.status_code == 200, get_resp.text
    assert wishlists == []

# ### Scenario 20: Retrieve Wishlists without Authentication
# - **Objective:** Ensure an unauthenticated user cannot retrieve wishlists.
# - **Steps:**
#   1. Send a GET request to `/wishlists` without an authentication token.
# - **Expected Result:**
#   - The API should respond with a `401 Unauthorized` status code.
@pytest.mark.api
def test_wishlists_get_unauthenticated(
    api_client, base_api_url, json_data, cleanup_users
):
    wrong_login_token = "this_is_definitely_a_wrong_login_token"
    headers = {"Authorization": f"Bearer {wrong_login_token}"}
    url_wishlists = f"{base_api_url}/wishlists"

    get_resp = api_client.get(url_wishlists, headers=headers)
    wishlists = get_resp.json()
    print(wishlists)
    assert get_resp.status_code == 401, get_resp.text
    assert get_resp.json().get("detail") == "Could not validate credentials"
