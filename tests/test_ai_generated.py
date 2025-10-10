import pytest
from datetime import date, timedelta
from services import Library, DEFAULT_LOAN_DAYS, MAX_ACTIVE_LOANS_PER_USER

def make_lib():
    lib = Library()
    lib.register_user(1, "Alice")
    lib.register_user(2, "Bob")
    lib.add_book(100, "Design Patterns", "GoF", copies=1)
    lib.add_book(101, "Refactoring", "Fowler", copies=2)
    return lib

def test_checkout_requires_available_copy():
    lib = make_lib()
    lib.checkout_book(1, 100, today=date(2025, 10, 1))
    with pytest.raises(ValueError):
        lib.checkout_book(2, 100, today=date(2025, 10, 1))

def test_due_date_is_default_loan_days_from_today():
    lib = make_lib()
    start = date(2025, 10, 1)
    loan = lib.checkout_book(1, 101, today=start)
    assert loan.due_date == start + timedelta(days=DEFAULT_LOAN_DAYS)

def test_return_restores_available_copies_and_closes_loan():
    lib = make_lib()
    lib.checkout_book(1, 101, today=date(2025, 10, 1))
    lib.return_book(1, 101, return_date=date(2025, 10, 2))
    assert lib.books[101].available_copies == 2
    assert lib.list_active_loans(1) == []

def test_user_cap_enforced():
    lib = make_lib()
    for i in range(102, 102 + MAX_ACTIVE_LOANS_PER_USER + 1):
        lib.add_book(i, f"B{i}", "Auth", copies=1)

    for i in range(MAX_ACTIVE_LOANS_PER_USER):
        lib.checkout_book(1, 102 + i, today=date(2025, 10, 1))

    assert len(lib.list_active_loans(1)) == MAX_ACTIVE_LOANS_PER_USER

    with pytest.raises(ValueError):
        lib.checkout_book(1, 102 + MAX_ACTIVE_LOANS_PER_USER, today=date(2025, 10, 1))

def test_overdue_detection():
    lib = make_lib()
    lib.checkout_book(2, 101, today=date(2025, 9, 1))
    over = lib.list_overdue_loans(today=date(2025, 10, 1))
    assert len(over) == 1
    
"""
AI tool: ChatGPT (GPT-5 Thinking)
Prompt (initial):
  "Generate pytest test cases for a simple in-memory Library system (users, books, loans) with
   add_user, add_book, checkout_book, return_book, overdue detection (DEFAULT_LOAN_DAYS=14),
   and a max active loans per user of 3. Use from services import Library, DEFAULT_LOAN_DAYS,
   MAX_ACTIVE_LOANS_PER_USER."
Follow-ups:
  - "Add tests for edge cases: inactive user, inactive book, removing a book with outstanding loan."
  - "Use fixed dates for determinism."
"""