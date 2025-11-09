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


def create_default_wishlist(api_client, base_api_url, token, name):
    headers = {"Authorization": f"Bearer {token}"}
    resp = api_client.post(
        f"{base_api_url}/wishlists",
        headers=headers,
        json={"name": name},
    )
    assert resp.status_code == 200, f"Failed to create wishlist: {resp.text}"
    body = resp.json()
    wishlist_id = body.get("id")
    assert wishlist_id is not None, f"Response without wishlist id: {body}"
    return wishlist_id

def add_four_products_on_wishlist(api_client, base_api_url, token, wishlist_id):
    headers = {"Authorization": f"Bearer {token}"}
    url_post = f"{base_api_url}/wishlists/{wishlist_id}/products"

    payload_product1 = {
        "Product": "New Glasses",
        "Price": "99.99",
        "Zipcode": "12345678",
        "delivery_estimate": "12 days",
        "shipping_fee": "29.00"
    }
    post_resp1 = api_client.post(url_post, headers=headers, json=payload_product1)
    assert post_resp1.status_code == 200, post_resp1.text
    product1 = post_resp1.json()

    payload_product2 = {
        "Product": "New Keyboard",
        "Price": "399.99",
        "Zipcode": "38291",
        "delivery_estimate": "1 days",
        "shipping_fee": "8.00"
    }
    post_resp2 = api_client.post(url_post, headers=headers, json=payload_product2)
    assert post_resp2.status_code == 200, post_resp2.text
    product2 = post_resp2.json()

    payload_product3 = {
        "Product": "Apple iPhone",
        "Price": "125.00",
        "Zipcode": "123123123",
        "delivery_estimate": "27 days",
        "shipping_fee": "300.00"
    }
    post_resp3 = api_client.post(url_post, headers=headers, json=payload_product3)
    assert post_resp3.status_code == 200, post_resp3.text
    product3 = post_resp3.json()

    payload_product4 = {
        "Product": "Apple iPhone Turbo",
        "Price": "325.00",
        "Zipcode": "123123123",
        "delivery_estimate": "47 days",
        "shipping_fee": "600.00"
    }
    post_resp4 = api_client.post(url_post, headers=headers, json=payload_product4)
    assert post_resp4.status_code == 200, post_resp4.text
    product4 = post_resp4.json()

    return product1, product2, product3, product4

# # Test Cases for Product Endpoints

# ### Endpoint: POST /wishlists/{wishlist_id}/products

# ### Scenario 21: Successfully Add a Product to a Wishlist
# - **Objective:** Verify that a product can be added to a specific wishlist.
# - **Prerequisites:** User is authenticated and owns a wishlist (e.g., with `id=1`).
# - **Steps:**
#   1. Send a POST request to `/wishlists/1/products` with a valid auth token.
#   2. Provide valid product data in the request body: `{"Product": "New Gadget", "Price": "99.99", "Zipcode": "12345678"}`.
# - **Expected Result:**
#   - The API should respond with a `200 OK` status code.
#   - The response body should contain the created product object, including its new `id` and the `wishlist_id`.
#   - The `is_purchased` field should be `false`.
@pytest.mark.api
def test_product_add_success(api_client, base_api_url, cleanup_users):
    token = get_token_from_new_user(api_client, base_api_url)
    wishlist_id = create_default_wishlist(api_client, base_api_url, token, "Default Wishlist")
    headers = {"Authorization": f"Bearer {token}"}

    # post
    url = f"{base_api_url}/wishlists/{wishlist_id}/products"
    payload = {
        "Product": "New Gadget",
        "Price": "99.99",
        "Zipcode": "12345678",
        "delivery_estimate": "12 days",
        "shipping_fee": "29.00"
    }
    resp = api_client.post(url, headers=headers, json=payload)
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert "id" in body
    assert body.get("wishlist_id") == wishlist_id
    assert body.get("Product") == "New Gadget"
    assert body.get("Price") == "99.99"
    assert body.get("is_purchased") is False


# ### Scenario 22: Add a Product to a Non-Existent Wishlist
# - **Objective:** Ensure a product cannot be added to a wishlist that does not exist.
# - **Prerequisites:** User is authenticated.
# - **Steps:**
#   1. Send a POST request to `/wishlists/999/products` (where 999 is a non-existent ID) with a valid auth token and product data.
# - **Expected Result:**
#   - The API should respond with a `404 Not Found` status code.
#   - The response body should contain an error message like "Wishlist not found".
@pytest.mark.api
def test_product_add_nonexistent_wishlist(api_client, base_api_url, cleanup_users):
    token = get_token_from_new_user(api_client, base_api_url)
    wishlist_id = 9382170397
    headers = {"Authorization": f"Bearer {token}"}

    url = f"{base_api_url}/wishlists/{wishlist_id}/products"
    payload = {
        "Product": "New Gadget",
        "Price": "99.99",
        "Zipcode": "12345678",
        "delivery_estimate": "12 days",
        "shipping_fee": "29.00"
    }
    resp = api_client.post(url, headers=headers, json=payload)

    assert resp.status_code == 404, resp.text

    body = resp.json()
    assert body.get('detail') == "Wishlist not found"


# ### Scenario 23: Add a Product to Another User's Wishlist
# - **Objective:** Ensure a user cannot add a product to a wishlist they do not own.
# - **Prerequisites:** Two users exist. User A owns wishlist 1. User B is authenticated.
# - **Steps:**
#   1. User B sends a POST request to `/wishlists/1/products` with their auth token.
# - **Expected Result:**
#   - The API should respond with a `404 Not Found` status code (as the wishlist is not found for that specific user).
@pytest.mark.api
def test_product_add_other_user_wishlist(api_client, base_api_url, cleanup_users):
    token_user1 = get_token_from_new_user(api_client, base_api_url)
    wishlist_id = create_default_wishlist(
        api_client, base_api_url, token_user1, "User 1 wishlist"
    )

    token_user2 = get_token_from_new_user(api_client, base_api_url)
    headers_user2 = {"Authorization": f"Bearer {token_user2}"}
    url = f"{base_api_url}/wishlists/{wishlist_id}/products"
    payload = {
        "Product": "New Gadget",
        "Price": "99.99",
        "Zipcode": "12345678",
        "delivery_estimate": "12 days",
        "shipping_fee": "29.00"
    }
    # post using user 2 token
    resp = api_client.post(url, headers=headers_user2, json=payload)

    assert resp.status_code == 404, resp.text

    body = resp.json()
    assert body.get("detail") == "Wishlist not found"

# ### Scenario 24: Add a Product with Incomplete Data
# - **Objective:** Test validation when required product fields are missing.
# - **Prerequisites:** User is authenticated and owns a wishlist.
# - **Steps:**
#   1. Send a POST request to `/wishlists/1/products` with missing required fields (e.g., `{"Price": "10.00"}`).
# - **Expected Result:**
#   - The API should respond with a `422 Unprocessable Entity` status code.
#   - The response should detail the missing fields.
@pytest.mark.api
def test_product_add_incomplete_data(api_client, base_api_url, cleanup_users):
    token = get_token_from_new_user(api_client, base_api_url)
    wishlist_id = create_default_wishlist(
        api_client, base_api_url, token, "Default Wishlist"
    )
    headers = {"Authorization": f"Bearer {token}"}

    url = f"{base_api_url}/wishlists/{wishlist_id}/products"
    payload = {
        "Product": "New Gadget",
        "Zipcode": "12345678",
        "delivery_estimate": "12 days",
        "shipping_fee": "29.00"
    }
    resp = api_client.post(url, headers=headers, json=payload)
    assert resp.status_code == 422, resp.text

    body = resp.json()
    assert body.get("detail") == "Missing product data"

# ## Endpoint: GET /wishlists/{wishlist_id}/products


# ### Scenario 25: Successfully Retrieve Products from a Wishlist
# - **Objective:** Verify that all products from a specific wishlist can be retrieved.
# - **Prerequisites:** User is authenticated and owns a wishlist with products.
# - **Steps:**
#   1. Send a GET request to `/wishlists/1/products` with a valid auth token.
# - **Expected Result:**
#   - The API should respond with a `200 OK` status code.
#   - The response body should be a JSON array of product objects belonging to that wishlist.
@pytest.mark.api
def test_product_get_all(api_client, base_api_url, cleanup_users):
    token = get_token_from_new_user(api_client, base_api_url)
    wishlist_id = create_default_wishlist(
        api_client, base_api_url, token, "Default Wishlist"
    )
    headers = {"Authorization": f"Bearer {token}"}

    # post
    url_post = f"{base_api_url}/wishlists/{wishlist_id}/products"
    payload_product1 = {
        "Product": "New Glasses",
        "Price": "99.99",
        "Zipcode": "12345678",
        "delivery_estimate": "12 days",
        "shipping_fee": "29.00"
    }
    post_resp1 = api_client.post(url_post, headers=headers, json=payload_product1)

    payload_product2 = {
        "Product": "New Keyboard",
        "Price": "399.99",
        "Zipcode": "38291",
        "delivery_estimate": "1 days",
        "shipping_fee": "8.00"
    }
    post_resp2 = api_client.post(url_post, headers=headers, json=payload_product2)

    assert post_resp1.status_code == 200, post_resp1.text
    assert post_resp2.status_code == 200, post_resp2.text

    url_get = f"{base_api_url}/wishlists/{wishlist_id}/products"
    get_resp = api_client.get(url_get, headers=headers)
    assert get_resp.status_code == 200, get_resp.text

    body = get_resp.json()
    assert len(body) == 2

    found_names = []
    for product in body:
        product_name = product["Product"]
        found_names.append(product_name)

    assert payload_product1["Product"] in found_names
    assert payload_product2["Product"] in found_names

# ### Scenario 26: Retrieve Products and Filter by Name
# - **Objective:** Test filtering products by name.
# - **Prerequisites:** User is authenticated and owns a wishlist with a product named "Apple iPhone".
# - **Steps:**
#   1. Send a GET request to `/wishlists/1/products?Product=iPhone` with a valid auth token.
# - **Expected Result:**
#   - The API should respond with a `200 OK` status code.
#   - The response body should contain only products whose name contains "iPhone".
@pytest.mark.api
def test_product_get_filter_name(api_client, base_api_url, cleanup_users):
    token = get_token_from_new_user(api_client, base_api_url)
    wishlist_id = create_default_wishlist(
        api_client, base_api_url, token, "Default Wishlist"
    )
    
    headers = {"Authorization": f"Bearer {token}"}

    # post
    url_post = f"{base_api_url}/wishlists/{wishlist_id}/products"
    payload_product1 = {
        "Product": "New Glasses",
        "Price": "99.99",
        "Zipcode": "12345678",
        "delivery_estimate": "12 days",
        "shipping_fee": "29.00"
    }
    post_resp1 = api_client.post(url_post, headers=headers, json=payload_product1)

    payload_product2 = {
        "Product": "New Keyboard",
        "Price": "399.99",
        "Zipcode": "38291",
        "delivery_estimate": "1 days",
        "shipping_fee": "8.00"
    }
    post_resp2 = api_client.post(url_post, headers=headers, json=payload_product2)

    payload_product3 = {
        "Product": "Apple iPhone",
        "Price": "125.00",
        "Zipcode": "123123123",
        "delivery_estimate": "27 days",
        "shipping_fee": "300.00"
    }
    post_resp3 = api_client.post(url_post, headers=headers, json=payload_product3)
    payload_product4 = {
        "Product": "Apple iPhone Turbo",
        "Price": "325.00",
        "Zipcode": "123123123",
        "delivery_estimate": "47 days",
        "shipping_fee": "600.00"
    }
    post_resp4 = api_client.post(url_post, headers=headers, json=payload_product4)

    assert post_resp1.status_code == 200, post_resp1.text
    assert post_resp2.status_code == 200, post_resp2.text
    assert post_resp3.status_code == 200, post_resp3.text
    assert post_resp4.status_code == 200, post_resp4.text

    url_get = f"{base_api_url}/wishlists/{wishlist_id}/products?Product=iPhone"
    get_resp = api_client.get(url_get, headers=headers)

    body = get_resp.json()
    assert len(body) == 2

    for product in body:
        name = product["Product"]
        assert "iPhone" in name, f"Product doesn't have 'iPhone' in its name ({name})"

# ### Scenario 27: Retrieve Products and Filter by `is_purchased` Status
# - **Objective:** Test filtering products by their purchased status.
# - **Prerequisites:** User is authenticated and owns a wishlist with purchased and unpurchased items.
# - **Steps:**
#   1. Send a GET request to `/wishlists/1/products?is_purchased=true`.
# - **Expected Result:**
#   - The API should respond with a `200 OK` status code.
#   - The response body should only contain products that have been marked as purchased.
@pytest.mark.api
def test_product_get_filter_purchased(api_client, base_api_url, cleanup_users):
    token = get_token_from_new_user(api_client, base_api_url)
    wishlist_id = create_default_wishlist(
        api_client, base_api_url, token, "Default Wishlist"
    )
    headers = {"Authorization": f"Bearer {token}"}

    # post
    url_post = f"{base_api_url}/wishlists/{wishlist_id}/products"
    payload_product1 = {
        "Product": "New Glasses",
        "Price": "99.99",
        "Zipcode": "12345678",
        "delivery_estimate": "12 days",
        "shipping_fee": "29.00"
    }
    post_resp1 = api_client.post(url_post, headers=headers, json=payload_product1)
    assert post_resp1.status_code == 200, post_resp1.text
    product1 = post_resp1.json()
    product1_id = product1["id"]

    payload_product2 = {
        "Product": "New Keyboard",
        "Price": "399.99",
        "Zipcode": "38291",
        "delivery_estimate": "1 days",
        "shipping_fee": "8.00"
    }
    post_resp2 = api_client.post(url_post, headers=headers, json=payload_product2)
    assert post_resp2.status_code == 200, post_resp2.text
    product2 = post_resp2.json()
    product2_id = product2["id"]

    payload_product3 = {
        "Product": "Apple iPhone",
        "Price": "125.00",
        "Zipcode": "123123123",
        "delivery_estimate": "27 days",
        "shipping_fee": "300.00"
    }
    post_resp3 = api_client.post(url_post, headers=headers, json=payload_product3)
    assert post_resp3.status_code == 200, post_resp3.text
    product3 = post_resp3.json()
    product3_id = product3["id"]

    payload_product4 = {
        "Product": "Apple iPhone Turbo",
        "Price": "325.00",
        "Zipcode": "123123123",
        "delivery_estimate": "47 days",
        "shipping_fee": "600.00"
    }
    post_resp4 = api_client.post(url_post, headers=headers, json=payload_product4)
    assert post_resp4.status_code == 200, post_resp4.text
    product4 = post_resp4.json()
    product4_id = product4["id"]

    url_put_1 = f"{base_api_url}/products/{product1_id}"
    update1 = {
        "Product": product1["Product"],
        "Price": product1["Price"],
        "delivery_estimate": product1["delivery_estimate"],
        "is_purchased": True
    }
    put_resp1 = api_client.put(url_put_1, headers=headers, json=update1)
    assert put_resp1.status_code == 200

    url_put_2 = f"{base_api_url}/products/{product2_id}"
    update2 = {
        "Product": product2["Product"],
        "Price": product2["Price"],
        "delivery_estimate": product2["delivery_estimate"],
        "is_purchased": True
    }
    put_resp2 = api_client.put(url_put_2, headers=headers, json=update2)
    assert put_resp2.status_code == 200

    url_get = f"{base_api_url}/wishlists/{wishlist_id}/products?is_purchased=true"
    get_resp = api_client.get(url_get, headers=headers)
    assert get_resp.status_code == 200, get_resp.text

    body = get_resp.json()
    assert len(body) == 2

    for product in body:
        is_purchased = product["is_purchased"]
        assert is_purchased == True, f"Product isn't marked as 'purchased' ({is_purchased})"

# ### Scenario 28: Retrieve Products from Another User's Wishlist
# - **Objective:** Ensure a user cannot view products from a wishlist they do not own.
# - **Prerequisites:** User A owns wishlist 1. User B is authenticated.
# - **Steps:**
#   1. User B sends a GET request to `/wishlists/1/products` with their auth token.
# - **Expected Result:**
#   - The API should respond with a `404 Not Found` status code.
@pytest.mark.api
def test_product_get_other_user(api_client, base_api_url, cleanup_users):
    token_user1 = get_token_from_new_user(api_client, base_api_url)
    wishlist_id_user1 = create_default_wishlist(
        api_client, base_api_url, token_user1, "Default Wishlist"
    )
    headers1 = {"Authorization": f"Bearer {token_user1}"}

    # post
    url_post = f"{base_api_url}/wishlists/{wishlist_id_user1}/products"
    payload_product1 = {
        "Product": "New Glasses",
        "Price": "99.99",
        "Zipcode": "12345678",
        "delivery_estimate": "12 days",
        "shipping_fee": "29.00"
    }
    post_resp1 = api_client.post(url_post, headers=headers1, json=payload_product1)
    assert post_resp1.status_code == 200, post_resp1.text

    payload_product2 = {
        "Product": "New Keyboard",
        "Price": "399.99",
        "Zipcode": "38291",
        "delivery_estimate": "1 days",
        "shipping_fee": "8.00"
    }
    post_resp2 = api_client.post(url_post, headers=headers1, json=payload_product2)
    assert post_resp2.status_code == 200, post_resp2.text

    token_user2 = get_token_from_new_user(api_client, base_api_url)
    headers2 = {"Authorization": f"Bearer {token_user2}"}

    url_get = f"{base_api_url}/wishlists/{wishlist_id_user1}/products"
    get_resp = api_client.get(url_get, headers=headers2)

    assert get_resp.status_code == 404, get_resp.text

# ## Endpoint: PUT /products/{product_id}

# ### Scenario 29: Successfully Update a Product
# - **Objective:** Verify that a product's details can be updated.
# - **Prerequisites:** User is authenticated and owns a product (e.g., with `id=1`).
# - **Steps:**
#   1. Send a PUT request to `/products/1` with a valid auth token.
#   2. Provide the fields to be updated in the request body (e.g., `{"Price": "150.00"}`).
# - **Expected Result:**
#   - The API should respond with a `200 OK` status code.
#   - The response body should contain the full product object with the updated price.
@pytest.mark.api
def test_product_update_success(api_client, base_api_url, cleanup_users):
    token = get_token_from_new_user(api_client, base_api_url)
    wishlist_id = create_default_wishlist(
        api_client, base_api_url, token, "Default Wishlist"
    )
    headers = {"Authorization": f"Bearer {token}"}

    # post
    url_post = f"{base_api_url}/wishlists/{wishlist_id}/products"
    previous_product_name = "New Glasses"
    previous_price = "99.99"
    previous_delivery_estimate = "12 days"
    payload_product1 = {
        "Product": previous_product_name,
        "Price": previous_price,
        "Zipcode": "12345678",
        "delivery_estimate": previous_delivery_estimate,
        "shipping_fee": "29.00"
    }
    post_resp1 = api_client.post(url_post, headers=headers, json=payload_product1)
    assert post_resp1.status_code == 200, post_resp1.text
    product1 = post_resp1.json()
    product1_id = product1["id"]

    url_put_1 = f"{base_api_url}/products/{product1_id}"
    after_product_name = "New Glasses Turbo XL"
    after_price = "129.99"
    after_delivery_estimate = "41 days"
    update_product1 = {
        "Product": after_product_name,
        "Price": after_price,
        "delivery_estimate": after_delivery_estimate
    }
    put_resp1 = api_client.put(url_put_1, headers=headers, json=update_product1)
    assert put_resp1.status_code == 200

    body = put_resp1.json()
    assert body["Product"] == "New Glasses Turbo XL"
    assert body["Price"] == "129.99"
    assert body["delivery_estimate"] == "41 days"

# ### Scenario 30: Update a Product That Doesn't Exist
# - **Objective:** Ensure an error is returned when trying to update a non-existent product.
# - **Prerequisites:** User is authenticated.
# - **Steps:**
#   1. Send a PUT request to `/products/999` with an auth token and update data.
# - **Expected Result:**
#   - The API should respond with a `404 Not Found` status code.
@pytest.mark.api
def test_product_update_nonexistent(api_client, base_api_url, cleanup_users):
    token = get_token_from_new_user(api_client, base_api_url)
    headers = {"Authorization": f"Bearer {token}"}
    unexisting_product_id = 21839621873698127
    url_put_1 = f"{base_api_url}/products/{unexisting_product_id}"
    product_name = "New Glasses Turbo XL"
    price = "129.99"
    delivery_estimate = "41 days"
    update_product1 = {
        "Product": product_name,
        "Price": price,
        "delivery_estimate": delivery_estimate
    }
    put_resp1 = api_client.put(url_put_1, headers=headers, json=update_product1)
    assert put_resp1.status_code == 404

# ### Scenario 31: Update Another User's Product
# - **Objective:** Ensure a user cannot update a product they do not own.
# - **Prerequisites:** User A owns product 1. User B is authenticated.
# - **Steps:**
#   1. User B sends a PUT request to `/products/1` with their auth token.
# - **Expected Result:**
#   - The API should respond with a `404 Not Found` status code.
@pytest.mark.api
def test_product_update_other_user(api_client, base_api_url, cleanup_users):
    token_user1 = get_token_from_new_user(api_client, base_api_url)
    wishlist_user1_id = create_default_wishlist(
        api_client, base_api_url, token_user1, "Default Wishlist"
    )
    headers1 = {"Authorization": f"Bearer {token_user1}"}

    # post
    url_post = f"{base_api_url}/wishlists/{wishlist_user1_id}/products"
    post_product_name = "New Glasses"
    post_price = "99.99"
    post_delivery_estimate = "12 days"
    payload_product1 = {
        "Product": post_product_name,
        "Price": post_price,
        "Zipcode": "12345678",
        "delivery_estimate": post_delivery_estimate,
        "shipping_fee": "29.00",
    }
    post_resp1 = api_client.post(url_post, headers=headers1, json=payload_product1)
    assert post_resp1.status_code == 200, post_resp1.text
    product1 = post_resp1.json()
    product1_id = product1["id"]

    token_user2 = get_token_from_new_user(api_client, base_api_url)
    headers2 = {"Authorization": f"Bearer {token_user2}"}

    # user 2 trying to update user 1 product
    url_put_user2 = f"{base_api_url}/products/{product1_id}"
    user2_post_product_name = "New Glasses Turbo XL"
    user2_post_price = "129.99"
    user2_post_delivery_estimate = "41 days"
    update_product1 = {
        "Product": user2_post_product_name,
        "Price": user2_post_price,
        "delivery_estimate": user2_post_delivery_estimate,
    }
    put_resp = api_client.put(url_put_user2, headers=headers2, json=update_product1)
    assert put_resp.status_code == 404

# ## Endpoint: DELETE /products/{product_id}

# ### Scenario 32: Successfully Delete a Product
# - **Objective:** Verify that a product can be deleted from a wishlist.
# - **Prerequisites:** User is authenticated and owns a product (e.g., with `id=1`).
# - **Steps:**
#   1. Send a DELETE request to `/products/1` with a valid auth token.
# - **Expected Result:**
#   - The API should respond with a `204 No Content` status code.
@pytest.mark.api
def test_product_delete_success(api_client, base_api_url, cleanup_users):
    token = get_token_from_new_user(api_client, base_api_url)
    wishlist_id = create_default_wishlist(
        api_client, base_api_url, token, "Default Wishlist"
    )
    headers = {"Authorization": f"Bearer {token}"}
    product1, product2, product3, product4 = add_four_products_on_wishlist(api_client, base_api_url, token, wishlist_id)
    product1_id = product1["id"]

    # deleting product 1
    url_delete = f"{base_api_url}/products/{product1_id}"
    delete_resp = api_client.delete(url_delete, headers=headers)
    assert delete_resp.status_code == 204, delete_resp.text

    url_get = f"{base_api_url}/wishlists/{wishlist_id}/products"
    get_resp = api_client.get(url_get, headers=headers)
    assert get_resp.status_code == 200, get_resp.text

    body = get_resp.json()
    assert len(body) == 3

    found_names = []
    for product in body:
        product_name = product["Product"]
        found_names.append(product_name)

    assert product1["Product"] not in found_names
    assert product2["Product"] in found_names
    assert product3["Product"] in found_names
    assert product4["Product"] in found_names


# ### Scenario 33: Delete a Product That Doesn't Exist
# - **Objective:** Ensure an error is returned when trying to delete a non-existent product.
# - **Prerequisites:** User is authenticated.
# - **Steps:**
#   1. Send a DELETE request to `/products/999` with an auth token.
# - **Expected Result:**
#   - The API should respond with a `404 Not Found` status code.
@pytest.mark.api
def test_product_delete_nonexistent(api_client, base_api_url, cleanup_users):
    token = get_token_from_new_user(api_client, base_api_url)
    headers = {"Authorization": f"Bearer {token}"}
    unexisting_product_id = 322549382890

    # deleting product that doesn't exist
    url_delete = f"{base_api_url}/products/{unexisting_product_id}"
    delete_resp = api_client.delete(url_delete, headers=headers)
    assert delete_resp.status_code == 404, delete_resp.text


# ### Scenario 34: Delete Another User's Product
# - **Objective:** Ensure a user cannot delete a product they do not own.
# - **Prerequisites:** User A owns product 1. User B is authenticated.
# - **Steps:**1we
#   1. User B sends a DELETE request to `/products/1` with their auth token.
# - **Expected Result:**
#   - The API should respond with a `404 Not Found` status code.
@pytest.mark.api
def test_product_delete_other_user(api_client, base_api_url, cleanup_users):
    token_user1 = get_token_from_new_user(api_client, base_api_url)
    wishlist_id = create_default_wishlist(
        api_client, base_api_url, token_user1, "Default Wishlist"
    )
    product1, product2, product3, product4 = add_four_products_on_wishlist(
        api_client, base_api_url, token_user1, wishlist_id
    )
    user1_product1_id = product1["id"]

    token_user2 = get_token_from_new_user(api_client, base_api_url)
    headers2 = {"Authorization": f"Bearer {token_user2}"}

    # user 2 trying to delete product from user 1 wishlist
    url_delete = f"{base_api_url}/products/{user1_product1_id}"
    delete_resp = api_client.delete(url_delete, headers=headers2)
    assert delete_resp.status_code == 404, delete_resp.text
