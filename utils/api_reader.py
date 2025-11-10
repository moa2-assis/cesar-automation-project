def login_default_user_token(api_client, base_api_url):
    email = "projeto@example.com"
    password = "Senha123!"

    login_url = f"{base_api_url}/auth/login"
    payload = {
        "email": email,
        "password": password,
    }
    resp = api_client.post(login_url, json=payload)
    assert resp.status_code in (200, 201), f"Failed to login: {resp.text}"

    token = resp.json().get("access_token")
    assert token, "Token not returned by the API"

    return token


def return_objects_from_wishlist(api_client, base_api_url):
    token = login_default_user_token(api_client, base_api_url)
    headers = {"Authorization": f"Bearer {token}"}

    get_wishlist_url = f"{base_api_url}/wishlists"
    wishlist_resp = api_client.get(get_wishlist_url, headers=headers)
    assert wishlist_resp.status_code == 200, wishlist_resp.text

    body = wishlist_resp.json()
    target_id = None
    for wishlist in body:
        if wishlist.get("name") == "projeto_final":
            target_id = wishlist.get("id")
            break

    assert target_id is not None, "Wishlist 'projeto_final' not found"

    get_products_url = f"{base_api_url}/wishlists/{target_id}/products"
    product_resp = api_client.get(get_products_url, headers=headers)
    assert product_resp.status_code == 200, product_resp.text

    return product_resp.json()
