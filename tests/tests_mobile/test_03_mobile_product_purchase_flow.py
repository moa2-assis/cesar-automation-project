import time
import pytest
from pages.pages_mobile.mobile_home_page import MobileHome
from pages.pages_mobile.mobile_results_page import MobileSearchResultsPage
from utils.api_reader import return_objects_from_wishlist

### Scenario 3: Product Purchase Flow
#### Use the 3 products from wishlist projeto_final as an argument for loop execution
# **Objective:** To validate the purchase journey of a product in the application.

# **Test Steps:**

# 1.  **Open App:** Launch the Americanas application.
# 2.  **Search for Product:** Use the search bar to look for a product from the wishlist.
# 3.  **Select Product:** Tap on the desired product in the search results.
# 4.  **Validate Product Page:**
#     *   Confirm that the product name and price are correct according to the API response.
#     *   Enter an invalid ZIP code, click "Calculate", and verify that an error message is displayed.
#     *   Enter the valid ZIP code returned by the API and validate the delivery time and shipping cost.
# 5.  **Add to Cart:** Tap the "Buy" button.
# 6.  **Validate Cart Popup:**
#     *   In the cart popup, confirm the product name and price again.
#     *   Increase the quantity to 2 and check if the quantity field is updated.
#     *   Decrease the quantity to 1 and check if the decrease button (`-`) becomes inactive.
#     *   Increase the quantity to 2 again.
# 7.  **Add and go to cart:** Proceed to the cart finalization screen.
# 8.  **Validate Cart:**
#     *   Confirm the product name and quantity.
#     *   Check if the total product value and the order subtotal are double the unit price.
#     *   Confirm that the value on the "Proceed to Checkout" button also reflects the total for two units.
#     *   Repeat the invalid and valid ZIP code test to ensure shipping calculation consistency.
# 9.  **Proceed to Checkout:** Tap "Proceed to Checkout".
# 10. **Validate Redirect:** Check if the login/checkout screen is displayed with the message "Enter your email to continue".
@pytest.mark.mobile
@pytest.mark.parametrize("product_index", [0, 1, 2])
def test_mobile_popup_title(driver, api_client, base_api_url, product_index):
    # 1
    home = MobileHome(driver)
    results = MobileSearchResultsPage(driver)
    products = return_objects_from_wishlist(api_client, base_api_url)
    assert isinstance(products, list)
    assert len(products) > 0

    product_data = products[product_index]
    expected_name = product_data.get("Product")
    expected_price = home.normalize_price(product_data.get("Price"))

    home.accept_runtime_permissions(duration=15)

    # 2
    home.is_on_home()
    home.focus_search()
    ok_search = home.type_query(expected_name)
    assert ok_search, f"Couldn't type product name on SEARCH_INPUT"
    home.submit_search()

    time.sleep(5)
