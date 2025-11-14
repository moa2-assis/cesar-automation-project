import time
import pytest

from pages.pages_web.web_home_page import WebHomePage
from pages.pages_web.web_search_results_page import WebSearchResultsPage
from pages.pages_web.web_product_page import WebProductPage
from utils.api_reader import return_objects_from_wishlist

# ### Scenario 5: Search and View Product from Wishlist
# #### Use the 3 products from wishlist projeto_final as an argument for loop execution
# **Objective:** To validate the consistency of product display in different modes.

# **Test Steps:**

# 1.  **Access Website/App:** Open the Americanas website or app.
# 2.  **Search for Product:** Search for a product that exists in your API Wishlist.
# 3.  **Validate Grid View:** In the grid view, confirm that the product title and price are correct.
# 4.  **Validate List View:** Switch to the list view and confirm the title and price again.
# 5.  **Access Product Page:** Click on the product to see its details.
# 6.  **Validate Details Page:** Confirm for the last time that the product title and price are correct.
@pytest.mark.web
@pytest.mark.parametrize("product_index", [0, 1, 2])
def test_search_view_product_from_wishlist(api_client, base_api_url, browser, product_index):
    home = WebHomePage(browser)
    search = WebSearchResultsPage(browser)
    product = WebProductPage(browser)

    products = return_objects_from_wishlist(api_client, base_api_url)
    assert isinstance(products, list)
    assert len(products) > 0
    product_data = products[product_index]
    expected_name = product_data.get("Product")
    expected_price = search.normalize_price(product_data.get("Price"))

    # 1
    home.open_americanas()
    home.close_banner_if_present()

    # 2
    home.wait_search_input_visibility()
    ok_search = home.type_query(expected_name)
    assert ok_search, f"Couldn't type product name on SEARCH_INPUT"
    time.sleep(1)
    home.click_search()

    # 3
    time.sleep(2)
    if(search.is_empty_search()):
        pytest.fail(f"Product '{expected_name}' didn't show up on the search")

    scroll_success = search.scroll_to_products()
    assert scroll_success, f"Couldn't scroll to product region (GRID_VIEW_BUTTON with start as block)"
    time.sleep(1)
    search.switch_to_grid_view()
    card_grid = search.find_card_by_exact_name(expected_name)
    print(card_grid)
    assert (
        card_grid is not None
    ), f"Product '{expected_name}' didn't show up on the search"
    card_grid_price = search.get_price_from_card(card_grid)
    actual_grid_card_price = search.normalize_price(card_grid_price)
    assert (
        expected_price == actual_grid_card_price
    ), f"Product price didn't match on grid view, API returned {expected_price} and current price is {actual_grid_card_price}"

    # 4
    search.switch_to_list_view()
    time.sleep(2)
    card_list = search.find_card_by_exact_name(expected_name)
    
    assert (
        card_list is not None
    ), f"Product '{expected_name}' didn't show up on the search"
    card_list_price = search.get_price_from_card(card_list)
    actual_list_card_price = home.normalize_price(card_list_price)
    assert (
        expected_price == actual_list_card_price
    ), f"Product price didn't match on list view, API returned {expected_price} and current price is {actual_list_card_price}"

    # 5
    search.click_price_from_card()
    time.sleep(3)

    # 6
    actual_product_title = product.get_product_title()
    assert expected_name == actual_product_title, f"Product name didn't match on product page. Expected is '{expected_name}, but got '{actual_product_title}'"
    time.sleep(1)
    product_price = product.get_product_price()
    actual_product_price = home.normalize_price(product_price)
    assert expected_price == actual_product_price, f"Product price didn't match on product page. Expected is '{expected_price}, but got '{actual_product_price}'"
