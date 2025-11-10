import time
import pytest
from pages.pages_mobile.mobile_home_page import MobileHome
from pages.pages_mobile.mobile_results_page import MobileSearchResultsPage
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
