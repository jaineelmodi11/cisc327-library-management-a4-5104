import pytest
from services import LibraryService

@pytest.fixture
def lib():
    return LibraryService()

def test_register_book_and_search(lib):
    lib.register_book("978-1", "Intro to AI", "Russell", copies=2)
    lib.register_book("978-2", "AI in Practice", "Ng", copies=1)
    hits = lib.search_books("ai")
    titles = {b["title"] for b in hits}
    assert {"Intro to AI", "AI in Practice"} <= titles

def test_loan_and_return_happy_path(lib):
    uid = lib.add_user("A")
    lib.register_book("978-1", "Intro to AI", "Russell", copies=1)
    assert lib.loan_book(uid, "978-1") is True
    assert lib.return_book(uid, "978-1") is True
    # double return should fail
    assert lib.return_book(uid, "978-1") is False

def test_loan_fails_when_no_copies(lib):
    uid = lib.add_user("A")
    lib.register_book("978-1", "Intro to AI", "Russell", copies=1)
    assert lib.loan_book(uid, "978-1") is True
    assert lib.loan_book(uid, "978-1") is False

def test_loan_requires_valid_user_and_isbn(lib):
    lib.register_book("978-1", "Intro to AI", "Russell", copies=1)
    assert lib.loan_book(999, "978-1") is False
    uid = lib.add_user("A")
    assert lib.loan_book(uid, "NOPE") is False

    
"""
AI tool: ChatGPT (GPT-5 Thinking)
Prompt (initial):
  "Generate pytest test cases for a simple in-memory Library system (users, books, loans) with
   add_user, add_book, checkout_book, return_book, overdue detection (DEFAULT_LOAN_DAYS=14),
   and a max active loans per user of 3. Use from services import Library, DEFAULT_LOAN_DAYS,
   MAX_ACTIVE_LOANS_PER_USER."
Follow-ups:
  - "Add tests for edge cases, inactive user, inactive book, removing a book with outstanding loan."
  - "Use fixed dates for determinism."
"""