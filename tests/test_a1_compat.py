from datetime import date, timedelta
from a1_compat import (
    register_user, add_book_to_catalog, borrow_book_by_patron,
    return_book_by_patron, calculate_late_fee_for_book, search_books_in_catalog
)
from services import DEFAULT_LOAN_DAYS

def test_a1_compat_smoke():
    register_user(1, "Alice")
    add_book_to_catalog("Clean Code", "Martin", 10, total_copies=1)

    loan_info = borrow_book_by_patron(1, 10, today=date(2025, 10, 1))
    assert loan_info["due_date"] == date(2025, 10, 1) + timedelta(days=DEFAULT_LOAN_DAYS)

    hits = search_books_in_catalog("clean")
    assert any(h["title"] == "Clean Code" for h in hits)

    # no fee on same-day
    assert calculate_late_fee_for_book(1, 10, today=date(2025, 10, 1)) == 0.0

    assert return_book_by_patron(1, 10, return_date=date(2025, 10, 3)) is True
