import pytest

# # Test Cases for Authenticated Endpoints - General

# ## Scenario 35: Accessing Endpoint without Authentication Token
# - **Objective:** Verify that all endpoints requiring authentication return a `401 Unauthorized` error when no token is provided.
# - **Endpoints to Test:**
#   - `POST /wishlists`
#   - `GET /wishlists`
#   - `POST /wishlists/{wishlist_id}/products`
#   - `GET /wishlists/{wishlist_id}/products`
#   - `PUT /products/{product_id}`
#   - `DELETE /products/{product_id}`
#   - `PATCH /products/{product_id}/toggle`
# - **Steps:**
#   1. For each endpoint, send a request without the `Authorization` header.
# - **Expected Result:**
#   - The API should respond with a `401 Unauthorized` status code.
#   - The response body should contain a detail message like "Not authenticated".
@pytest.mark.api
def test_protected_endpoints_without_token(api_client, base_api_url):
    # POST wishlists
    url_post_wishlist = f"{base_api_url}/wishlists"
    payload_wishlist = {"name": "Should Not Be Created"}
    resp = api_client.post(url_post_wishlist, json=payload_wishlist)
    assert resp.status_code == 401, resp.text
    body = resp.json()
    assert body.get("detail") == "Not authenticated"

    # GET wishlists
    url_get_wishlists = f"{base_api_url}/wishlists"
    resp = api_client.get(url_get_wishlists)
    assert resp.status_code == 401, resp.text
    body = resp.json()
    assert body.get("detail") == "Not authenticated"

    unexisting_wishlist_id = 32189738
    unexisting_product_id = 95802841

    # POST product
    url_post_product = f"{base_api_url}/wishlists/{unexisting_wishlist_id}/products"
    payload_product = {
        "Product": "Glasses that don't work",
        "Price": "16.00",
        "Zipcode": "1231012",
        "delivery_estimate": "5 days",
        "shipping_fee": "11.00",
    }
    resp = api_client.post(url_post_product, json=payload_product)
    assert resp.status_code == 401, resp.text
    body = resp.json()
    assert body.get("detail") == "Not authenticated"

    # GET product
    url_get_products = f"{base_api_url}/wishlists/{unexisting_wishlist_id}/products"
    resp = api_client.get(url_get_products)
    assert resp.status_code == 401, resp.text
    body = resp.json()
    assert body.get("detail") == "Not authenticated"

    # PUT product
    url_put_product = f"{base_api_url}/products/{unexisting_product_id}"
    payload_update = {
        "Product": "Updated Name for Glasses that don't work",
        "Price": "25.00",
        "delivery_estimate": "3 days",
        "is_purchased": True,
    }
    resp = api_client.put(url_put_product, json=payload_update)
    assert resp.status_code == 401, resp.text
    body = resp.json()
    assert body.get("detail") == "Not authenticated"

    # DELETE product
    url_delete_product = f"{base_api_url}/products/{unexisting_product_id}"
    resp = api_client.delete(url_delete_product)
    assert resp.status_code == 401, resp.text
    body = resp.json()
    assert body.get("detail") == "Not authenticated"

# ## Scenario 36: Accessing Endpoint with an Invalid or Expired Token
# - **Objective:** Verify that all endpoints requiring authentication return a `401 Unauthorized` error when an invalid, malformed, or expired token is provided.
# - **Endpoints to Test:**
#   - `POST /wishlists`
#   - `GET /wishlists`
#   - `POST /wishlists/{wishlist_id}/products`
#   - `GET /wishlists/{wishlist_id}/products`
#   - `PUT /products/{product_id}`
#   - `DELETE /products/{product_id}`
#   - `PATCH /products/{product_id}/toggle` ********
# - **Steps:**
#   1. For each endpoint, send a request with an `Authorization` header containing a token that is either:
#      - A completely invalid string (e.g., "Bearer invalidtoken").
#      - A correctly formatted but expired JWT. ********
#      - A token signed with a different secret key. ********
# - **Expected Result:**
#   - The API should respond with a `401 Unauthorized` status code.
#   - The response body should contain a detail message like "Could not validate credentials" or "Token has expired".
@pytest.mark.api
def test_protected_endpoints_with_invalid_token(api_client, base_api_url):
    invalid_headers = {"Authorization": "Bearer invalidtoken"}

    # POST wishlists
    url_post_wishlist = f"{base_api_url}/wishlists"
    payload_wishlist = {"name": "Wishlist That Shouldn't Be Created"}
    resp = api_client.post(
        url_post_wishlist, headers=invalid_headers, json=payload_wishlist
    )
    assert resp.status_code == 401, resp.text
    body = resp.json()
    assert body.get("detail") == "Could not validate credentials"

    # GET wishlists
    url_get_wishlists = f"{base_api_url}/wishlists"
    resp = api_client.get(url_get_wishlists, headers=invalid_headers)
    assert resp.status_code == 401, resp.text
    body = resp.json()
    assert body.get("detail") == "Could not validate credentials"

    unexisting_wishlist_id = 1
    unexisting_product_id = 1

    # POST product
    url_post_product = f"{base_api_url}/wishlists/{unexisting_wishlist_id}/products"
    payload_product = {
        "Product": "Product That Shouldn't Work",
        "Price": "10.00",
        "Zipcode": "00000000",
        "delivery_estimate": "1 day",
        "shipping_fee": "1.00",
    }
    resp = api_client.post(
        url_post_product, headers=invalid_headers, json=payload_product
    )
    assert resp.status_code == 401, resp.text
    body = resp.json()
    assert body.get("detail") == "Could not validate credentials"

    # GET product
    url_get_products = f"{base_api_url}/wishlists/{unexisting_wishlist_id}/products"
    resp = api_client.get(url_get_products, headers=invalid_headers)
    assert resp.status_code == 401, resp.text
    body = resp.json()
    assert body.get("detail") == "Could not validate credentials"

    # PUT product
    url_put_product = f"{base_api_url}/products/{unexisting_product_id}"
    payload_update = {
        "Product": "Updated Name",
        "Price": "20.00",
        "delivery_estimate": "5 days",
        "is_purchased": True,
    }
    resp = api_client.put(url_put_product, headers=invalid_headers, json=payload_update)
    assert resp.status_code == 401, resp.text
    body = resp.json()
    assert body.get("detail") == "Could not validate credentials"

    # DELETE product
    url_delete_product = f"{base_api_url}/products/{unexisting_product_id}"
    resp = api_client.delete(url_delete_product, headers=invalid_headers)
    assert resp.status_code == 401, resp.text
    body = resp.json()
    assert body.get("detail") == "Could not validate credentials"
