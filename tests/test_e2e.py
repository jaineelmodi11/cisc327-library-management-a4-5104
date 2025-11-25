# tests/test_e2e.py
from uuid import uuid4
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5000"


def test_add_and_borrow_book_flow():
    """
    End-to-end user flow:
    1) Add a new book via the web form.
    2) Verify it appears in the catalog.
    3) Navigate to borrow page.
    4) Borrow the book with a patron ID.
    5) Verify the success message appears.
    """
    test_title = f"E2E Test Book {uuid4()}"
    test_author = "Test Author"
    test_isbn = "1234567890"
    test_copies = "10"
    test_patron = "patron-123"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # --- Flow 1: Add book ---
        page.goto(f"{BASE_URL}/books/add")

        page.fill("input[name='title']", test_title)
        page.fill("input[name='author']", test_author)
        page.fill("input[name='isbn']", test_isbn)
        page.fill("input[name='copies']", test_copies)

        page.click("button#submit-add-book")

        # Should redirect to /books
        page.wait_for_url(f"{BASE_URL}/books")
        page.wait_for_selector("#books-table")

        table_text = page.text_content("#books-table")
        assert test_title in table_text
        assert test_author in table_text

        # --- Flow 2: Borrow book ---
        # Go to borrow page using the navbar link
        page.click("a#borrow-book-link")
        page.wait_for_url(f"{BASE_URL}/borrow")

        # Select the book we just added from the dropdown
        page.select_option("select[name='book_id']", label=test_title)
        page.fill("input[name='patron_id']", test_patron)

        page.click("button#submit-borrow")

        # After submit, we redirect back to /books with a success flash message
        page.wait_for_url(f"{BASE_URL}/books")

        body_text = page.text_content("body")
        assert f"Book borrowed successfully by patron {test_patron}." in body_text

        browser.close()
