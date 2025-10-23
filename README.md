# Technical activity - Test automation module

The objective of this activity is to consolidate part of the knowledge presented during the test automation module in the QA stage.

* This activity must be completed **INDIVIDUALLY**, without sharing solutions or knowledge.
* The deadline for submission is November 10, 2025, at 8 a.m.
* Submissions must be made as a repository on CESAR's GitHub,
 where the last commit cannot have been made after the final submission date.
  * The history and logs of the Git repository will also be used to assess knowledge and use of Git flow and best practices.
* In addition to the delivery, a day will be set aside during the internship period for the presentation of the resolution.
  * Your test scripts will run in real time during the presentation, so make sure everything is stable and running smoothly.
* Try your best to avoid using LLMs for the development of this project. Keep in mind that there will be questions during your presentation about the technical resolution of your challenge.
* Good development practices (python, pytest, automation, etc.) will be evaluated in the final delivery.
* Remember that this is a **TEST** automation project, so perform tests during the scripts, don't just do screen flows.
* **☢️ Do not include any information about the europa project or information about the europa client in the GitHub repository. For security reasons, create your repository as private.☢️**
---

## Web Flows

### Scenario 1: New User Registration and Password Setup

**Objective:** To validate the complete flow of creating a new account, setting a password, and validating the data.

**Test Steps:**

1.  **Access the website:** Open the browser and go to the Americanas website.
2.  **Navigate to Registration:** Click on the "Login or Sign Up" option.
3.  **Generate Temporary Email:** In a new tab, go to `https://temp-mail.io/` and copy the generated email.
4.  **Enter Email:** Return to the Americanas website, enter the temporary email in the registration field, and click to send the verification code.
5.  **Get Code:** Go back to the `temp-mail` website, open the received email, and copy the verification code.
6.  **Confirm Registration:** Return to the Americanas website and enter the code to finalize the registration.
7.  **Verify Redirect:** Confirm that you have been redirected to the homepage.
8.  **Validate Login:** Check if the new user's email is displayed in the page header.
9.  **Access My Account:** Open the "My Account" menu and confirm that the email in the registration tab is correct.
10. **Start Password Setup:** Navigate to the authentication section and select "Set Password".
11. **Enter Password Code:** Get the new code sent to `temp-mail` and enter it in the corresponding field.
12. **Test Password Rules:**
    *   Try to save a password with less than 8 characters. The "Save" button should be inactive.
    *   Try to save a password without numbers. The "Save" button should be inactive.
    *   Try to save a password without lowercase letters. The "Save" button should be inactive.
    *   Try to save a password without uppercase letters. The "Save" button should be inactive.
13. **Set Valid Password:** Enter a password that meets all criteria and click "Save Password".
14. **Validate success:** Validate that the password was saved successfully (just validate that the sequence of asterisks appeared on the screen).

### Scenario 2: In Progress

---

## Mobile Flows

### Scenario 3: Product Purchase Flow
#### Use the 3 products from wishlist projeto_final as an argument for loop execution
**Objective:** To validate the purchase journey of a product in the application.

**Test Steps:**

1.  **Open App:** Launch the Americanas application.
2.  **Search for Product:** Use the search bar to look for a product from the wishlist.
3.  **Select Product:** Tap on the desired product in the search results.
4.  **Validate Product Page:**
    *   Confirm that the product name and price are correct according to the API response.
    *   Enter an invalid ZIP code, click "Calculate", and verify that an error message is displayed.
    *   Enter the valid ZIP code returned by the API and validate the delivery time and shipping cost.
5.  **Add to Cart:** Tap the "Buy" button.
6.  **Validate Cart Popup:**
    *   In the cart popup, confirm the product name and price again.
    *   Increase the quantity to 2 and check if the quantity field is updated.
    *   Decrease the quantity to 1 and check if the decrease button (`-`) becomes inactive.
    *   Increase the quantity to 2 again.
7.  **Add and go to cart:** Proceed to the cart finalization screen.
8.  **Validate Cart:**
    *   Confirm the product name and quantity.
    *   Check if the total product value and the order subtotal are double the unit price.
    *   Confirm that the value on the "Proceed to Checkout" button also reflects the total for two units.
    *   Repeat the invalid and valid ZIP code test to ensure shipping calculation consistency.
9.  **Proceed to Checkout:** Tap "Proceed to Checkout".
10. **Validate Redirect:** Check if the login/checkout screen is displayed with the message "Enter your email to continue".


### Scenario 4: In Progress

---

## Mobile and Web Flows

### Scenario 5: Search and View Product from Wishlist
#### Use the 3 products from wishlist projeto_final as an argument for loop execution
**Objective:** To validate the consistency of product display in different modes.

**Test Steps:**

1.  **Access Website/App:** Open the Americanas website or app.
2.  **Search for Product:** Search for a product that exists in your API Wishlist.
3.  **Validate Grid View:** In the grid view, confirm that the product title and price are correct.
4.  **Validate List View:** Switch to the list view and confirm the title and price again.
5.  **Access Product Page:** Click on the product to see its details.
6.  **Validate Details Page:** Confirm for the last time that the product title and price are correct.

### Scenario 6: Login via Password

**Objective:** To validate the login flows for an existing user, both successful and failed.

**Test Steps:**

1.  **Access the website:** Open the browser and go to the Americanas website.
2.  **Navigate to Login:** Click on the "Login or Sign Up" option.
3.  **Enter Correct Credentials:** Fill in the fields with a valid and already registered email and password.
4.  **Perform Login:** Click the "Sign In" button.
5.  **Validate Login:** Confirm the redirect to the homepage and that the user's email is displayed in the header.

### Scenario 7: Login with Incorrect Password

**Test Steps:**

1.  **Access the website:** Open the browser and go to the Americanas website.
2.  **Navigate to Login:** Click on the "Login or Sign Up" option.
3.  **Enter Incorrect Credentials:** Fill in the email field with a valid user and enter an incorrect password.
4.  **Perform Login:** Click the "Sign In" button.
5.  **Validate Error:** Verify that an appropriate error message (e.g., "Invalid email or password") is displayed and the login is not successful.


# Test Cases for Authentication Endpoints

## Endpoint: POST /auth/register

### Scenario 8: Successful User Registration
- **Objective:** Verify that a new user can be created successfully with a valid email and password.
- **Steps:**
  1. Send a POST request to `/auth/register`.
  2. Provide a unique email (e.g., "testuser@example.com") and a strong password (e.g., "password123") in the request body.
- **Expected Result:**
  - The API should respond with a `200 OK` status code.
  - The response body should contain the user's data, including their ID and the email they registered with, but not the password.

### Scenario 9: Registration with an Existing Email
- **Objective:** Ensure the API prevents registration with an email that is already in use.
- **Steps:**
  1. First, register a user with a specific email (e.g., "existinguser@example.com").
  2. Send a second POST request to `/auth/register` using the exact same email.
- **Expected Result:**
  - The API should respond with a `400 Bad Request` status code.
  - The response body should contain an error message indicating that the email is already registered (e.g., "Email already registered").

### Scenario 10: Registration with Invalid Data
- **Objective:** Test the API's validation for invalid input during registration.
- **Steps:**
  1. Send a POST request to `/auth/register` with an invalid email format (e.g., "not-an-email").
  2. Send another request without a password field.
- **Expected Result:**
  - The API should respond with a `422 Unprocessable Entity` status code for both requests.
  - The response body should detail the validation error (e.g., "value is not a valid email address" or "field required").

---

## Endpoint: POST /auth/login

### Scenario 11: Successful Login
- **Objective:** Verify that a registered user can log in with correct credentials.
- **Steps:**
  1. Ensure a user is already registered (e.g., "loginuser@example.com" with password "correct_password").
  2. Send a POST request to `/auth/login` using the registered email as the `username` and the correct password.
- **Expected Result:**
  - The API should respond with a `200 OK` status code.
  - The response body should contain an `access_token` (JWT) and a `token_type` of "bearer".

### Scenario 12: Login with Incorrect Password
- **Objective:** Ensure the API denies access if the password is incorrect.
- **Steps:**
  1. Use the credentials of a registered user (e.g., "loginuser@example.com").
  2. Send a POST request to `/auth/login` with the correct email but an incorrect password (e.g., "wrong_password").
- **Expected Result:**
  - The API should respond with a `401 Unauthorized` status code.
  - The response body should contain an error message like "Incorrect email or password".

### Scenario 13: Login with Non-Existent User
- **Objective:** Ensure the API denies access if the user does not exist.
- **Steps:**
  1. Send a POST request to `/auth/login` with an email that has not been registered (e.g., "nouser@example.com").
- **Expected Result:**
  - The API should respond with a `401 Unauthorized` status code.
  - The response body should contain an error message like "Incorrect email or password".
---

# Test Cases for Wishlist Endpoints

## Endpoint: POST /wishlists

### Scenario 14: Successfully Create a Wishlist
- **Objective:** Verify that an authenticated user can create a new wishlist.
- **Prerequisites:** User must be authenticated (have a valid JWT token).
- **Steps:**
  1. Send a POST request to `/wishlists` with a valid authentication token in the header.
  2. Provide a `name` for the wishlist in the request body (e.g., `{"name": "My Tech Gadgets"}`).
- **Expected Result:**
  - The API should respond with a `200 OK` status code.
  - The response body should contain the newly created wishlist object, including its `id`, `name`, and the `owner_id`.

### Scenario 15: Create a Wishlist with a Duplicate Name
- **Objective:** Verify that a user can't create multiple wishlists with the same name.
- **Prerequisites:** User must be authenticated.
- **Steps:**
  1. Create a wishlist with a specific name (e.g., "Travel Plans").
  2. Send another POST request to `/wishlists` with the same name.
- **Expected Result:**
  - The API should respond with a `409 Conflict` status code.
  - A new wishlist should not be created with a different `id`.

### Scenario 16: Create a Wishlist without Authentication
- **Objective:** Ensure that an unauthenticated user cannot create a wishlist.
- **Steps:**
  1. Send a POST request to `/wishlists` without an authentication token.
- **Expected Result:**
  - The API should respond with a `401 Unauthorized` status code.
  - The response body should contain an error detail like "Not authenticated".

### Scenario 17: Create a Wishlist with Invalid Data
- **Objective:** Test validation when creating a wishlist with no name.
- **Prerequisites:** User must be authenticated.
- **Steps:**
  1. Send a POST request to `/wishlists` with an empty request body `{}`.
- **Expected Result:**
  - The API should respond with a `422 Unprocessable Entity` status code.
  - The response should detail the validation error (e.g., "field required").

---

## Endpoint: GET /wishlists

### Scenario 18: Successfully Retrieve All Wishlists
- **Objective:** Verify that an authenticated user can retrieve all of their wishlists.
- **Prerequisites:** User must be authenticated and have one or more wishlists.
- **Steps:**
  1. Send a GET request to `/wishlists` with a valid authentication token.
- **Expected Result:**
  - The API should respond with a `200 OK` status code.
  - The response body should be a JSON array containing all wishlists owned by the user.

### Scenario 19: Retrieve Wishlists When None Exist
- **Objective:** Verify the response when a user has no wishlists.
- **Prerequisites:** User must be authenticated but have no wishlists created.
- **Steps:**
  1. Send a GET request to `/wishlists` with a valid authentication token.
- **Expected Result:**
  - The API should respond with a `200 OK` status code.
  - The response body should be an empty JSON array `[]`.

### Scenario 20: Retrieve Wishlists without Authentication
- **Objective:** Ensure an unauthenticated user cannot retrieve wishlists.
- **Steps:**
  1. Send a GET request to `/wishlists` without an authentication token.
- **Expected Result:**
  - The API should respond with a `401 Unauthorized` status code.

---

# Test Cases for Product Endpoints

## Endpoint: POST /wishlists/{wishlist_id}/products

### Scenario 21: Successfully Add a Product to a Wishlist
- **Objective:** Verify that a product can be added to a specific wishlist.
- **Prerequisites:** User is authenticated and owns a wishlist (e.g., with `id=1`).
- **Steps:**
  1. Send a POST request to `/wishlists/1/products` with a valid auth token.
  2. Provide valid product data in the request body: `{"Product": "New Gadget", "Price": "99.99", "Zipcode": "12345678"}`.
- **Expected Result:**
  - The API should respond with a `200 OK` status code.
  - The response body should contain the created product object, including its new `id` and the `wishlist_id`.
  - The `is_purchased` field should be `false`.

### Scenario 22: Add a Product to a Non-Existent Wishlist
- **Objective:** Ensure a product cannot be added to a wishlist that does not exist.
- **Prerequisites:** User is authenticated.
- **Steps:**
  1. Send a POST request to `/wishlists/999/products` (where 999 is a non-existent ID) with a valid auth token and product data.
- **Expected Result:**
  - The API should respond with a `404 Not Found` status code.
  - The response body should contain an error message like "Wishlist not found".

### Scenario 23: Add a Product to Another User's Wishlist
- **Objective:** Ensure a user cannot add a product to a wishlist they do not own.
- **Prerequisites:** Two users exist. User A owns wishlist 1. User B is authenticated.
- **Steps:**
  1. User B sends a POST request to `/wishlists/1/products` with their auth token.
- **Expected Result:**
  - The API should respond with a `404 Not Found` status code (as the wishlist is not found for that specific user).

### Scenario 24: Add a Product with Incomplete Data
- **Objective:** Test validation when required product fields are missing.
- **Prerequisites:** User is authenticated and owns a wishlist.
- **Steps:**
  1. Send a POST request to `/wishlists/1/products` with missing required fields (e.g., `{"Price": "10.00"}`).
- **Expected Result:**
  - The API should respond with a `422 Unprocessable Entity` status code.
  - The response should detail the missing fields.

---

## Endpoint: GET /wishlists/{wishlist_id}/products

### Scenario 25: Successfully Retrieve Products from a Wishlist
- **Objective:** Verify that all products from a specific wishlist can be retrieved.
- **Prerequisites:** User is authenticated and owns a wishlist with products.
- **Steps:**
  1. Send a GET request to `/wishlists/1/products` with a valid auth token.
- **Expected Result:**
  - The API should respond with a `200 OK` status code.
  - The response body should be a JSON array of product objects belonging to that wishlist.

### Scenario 26: Retrieve Products and Filter by Name
- **Objective:** Test filtering products by name.
- **Prerequisites:** User is authenticated and owns a wishlist with a product named "Apple iPhone".
- **Steps:**
  1. Send a GET request to `/wishlists/1/products?Product=iPhone` with a valid auth token.
- **Expected Result:**
  - The API should respond with a `200 OK` status code.
  - The response body should contain only products whose name contains "iPhone".

### Scenario 27: Retrieve Products and Filter by `is_purchased` Status
- **Objective:** Test filtering products by their purchased status.
- **Prerequisites:** User is authenticated and owns a wishlist with purchased and unpurchased items.
- **Steps:**
  1. Send a GET request to `/wishlists/1/products?is_purchased=true`.
- **Expected Result:**
  - The API should respond with a `200 OK` status code.
  - The response body should only contain products that have been marked as purchased.

### Scenario 28: Retrieve Products from Another User's Wishlist
- **Objective:** Ensure a user cannot view products from a wishlist they do not own.
- **Prerequisites:** User A owns wishlist 1. User B is authenticated.
- **Steps:**
  1. User B sends a GET request to `/wishlists/1/products` with their auth token.
- **Expected Result:**
  - The API should respond with a `404 Not Found` status code.

---

## Endpoint: PUT /products/{product_id}

### Scenario 29: Successfully Update a Product
- **Objective:** Verify that a product's details can be updated.
- **Prerequisites:** User is authenticated and owns a product (e.g., with `id=1`).
- **Steps:**
  1. Send a PUT request to `/products/1` with a valid auth token.
  2. Provide the fields to be updated in the request body (e.g., `{"Price": "150.00"}`).
- **Expected Result:**
  - The API should respond with a `200 OK` status code.
  - The response body should contain the full product object with the updated price.

### Scenario 30: Update a Product That Doesn't Exist
- **Objective:** Ensure an error is returned when trying to update a non-existent product.
- **Prerequisites:** User is authenticated.
- **Steps:**
  1. Send a PUT request to `/products/999` with an auth token and update data.
- **Expected Result:**
  - The API should respond with a `404 Not Found` status code.

### Scenario 31: Update Another User's Product
- **Objective:** Ensure a user cannot update a product they do not own.
- **Prerequisites:** User A owns product 1. User B is authenticated.
- **Steps:**
  1. User B sends a PUT request to `/products/1` with their auth token.
- **Expected Result:**
  - The API should respond with a `404 Not Found` status code.

---

## Endpoint: DELETE /products/{product_id}

### Scenario 32: Successfully Delete a Product
- **Objective:** Verify that a product can be deleted from a wishlist.
- **Prerequisites:** User is authenticated and owns a product (e.g., with `id=1`).
- **Steps:**
  1. Send a DELETE request to `/products/1` with a valid auth token.
- **Expected Result:**
  - The API should respond with a `204 No Content` status code.

### Scenario 33: Delete a Product That Doesn't Exist
- **Objective:** Ensure an error is returned when trying to delete a non-existent product.
- **Prerequisites:** User is authenticated.
- **Steps:**
  1. Send a DELETE request to `/products/999` with an auth token.
- **Expected Result:**
  - The API should respond with a `404 Not Found` status code.

### Scenario 34: Delete Another User's Product
- **Objective:** Ensure a user cannot delete a product they do not own.
- **Prerequisites:** User A owns product 1. User B is authenticated.
- **Steps:**
  1. User B sends a DELETE request to `/products/1` with their auth token.
- **Expected Result:**
  - The API should respond with a `404 Not Found` status code.

---

# Test Cases for Authenticated Endpoints - General

## Scenario 35: Accessing Endpoint without Authentication Token
- **Objective:** Verify that all endpoints requiring authentication return a `401 Unauthorized` error when no token is provided.
- **Endpoints to Test:**
  - `POST /wishlists`
  - `GET /wishlists`
  - `POST /wishlists/{wishlist_id}/products`
  - `GET /wishlists/{wishlist_id}/products`
  - `PUT /products/{product_id}`
  - `DELETE /products/{product_id}`
  - `PATCH /products/{product_id}/toggle`
- **Steps:**
  1. For each endpoint, send a request without the `Authorization` header.
- **Expected Result:**
  - The API should respond with a `401 Unauthorized` status code.
  - The response body should contain a detail message like "Not authenticated".

## Scenario 36: Accessing Endpoint with an Invalid or Expired Token
- **Objective:** Verify that all endpoints requiring authentication return a `401 Unauthorized` error when an invalid, malformed, or expired token is provided.
- **Endpoints to Test:**
  - `POST /wishlists`
  - `GET /wishlists`
  - `POST /wishlists/{wishlist_id}/products`
  - `GET /wishlists/{wishlist_id}/products`
  - `PUT /products/{product_id}`
  - `DELETE /products/{product_id}`
  - `PATCH /products/{product_id}/toggle`
- **Steps:**
  1. For each endpoint, send a request with an `Authorization` header containing a token that is either:
     - A completely invalid string (e.g., "Bearer invalidtoken").
     - A correctly formatted but expired JWT.
     - A token signed with a different secret key.
- **Expected Result:**
  - The API should respond with a `401 Unauthorized` status code.
  - The response body should contain a detail message like "Could not validate credentials" or "Token has expired".