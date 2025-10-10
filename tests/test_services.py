import pytest
from datetime import date, timedelta
from services import Library, DEFAULT_LOAN_DAYS, MAX_ACTIVE_LOANS_PER_USER

@pytest.fixture()
def lib():
    l = Library()
    l.register_user(1, "Alice")
    l.register_user(2, "Bob")
    l.add_book(10, "Clean Code", "Martin", copies=2)
    l.add_book(11, "Refactoring", "Fowler", copies=1)
    return l

def test_register_and_deactivate_user(lib):
    lib.register_user(3, "Carol")
    assert lib.users[3].is_active is True
    lib.deactivate_user(3)
    assert lib.users[3].is_active is False

def test_add_and_remove_book(lib):
    lib.add_book(12, "DDD", "Evans", copies=1)
    assert lib.books[12].total_copies == 1
    lib.checkout_book(1, 12, today=date(2025, 10, 1))
    with pytest.raises(ValueError):
        lib.remove_book(12)
    lib.return_book(1, 12, return_date=date(2025, 10, 2))
    lib.remove_book(12)
    assert lib.books[12].is_active is False

def test_checkout_happy_path_and_due_date(lib):
    start = date(2025, 10, 1)
    loan = lib.checkout_book(1, 10, today=start)
    assert loan.due_date == start + timedelta(days=DEFAULT_LOAN_DAYS)
    assert lib.books[10].available_copies == 1

def test_checkout_exhausts_copies(lib):
    lib.checkout_book(1, 11, today=date(2025, 10, 1))
    with pytest.raises(ValueError):
        lib.checkout_book(2, 11, today=date(2025, 10, 1))

def test_user_loan_limit(lib):
    for b in [10, 11]:
        if lib.books[b].available_copies == 0:
            lib.books[b].available_copies = 1
    lib.add_book(12, "Patterns", "GoF", copies=1)
    lib.add_book(13, "Algorithms", "Sedgewick", copies=1)

    lib.checkout_book(1, 10, today=date(2025, 10, 1))
    lib.checkout_book(1, 11, today=date(2025, 10, 1))
    lib.checkout_book(1, 12, today=date(2025, 10, 1))

    assert len(lib.list_active_loans(1)) == MAX_ACTIVE_LOANS_PER_USER

    with pytest.raises(ValueError):
        lib.checkout_book(1, 13, today=date(2025, 10, 1))

def test_return_and_overdue(lib):
    lib.checkout_book(2, 10, today=date(2025, 9, 1))
    overdue = lib.list_overdue_loans(today=date(2025, 10, 1))
    assert len(overdue) == 1
    lib.return_book(2, 10, return_date=date(2025, 10, 2))
    assert len(lib.list_active_loans(2)) == 0
    assert lib.books[10].available_copies == 2
