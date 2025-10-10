import pytest
from datetime import date
from services import Library, MAX_ACTIVE_LOANS_PER_USER

def make_lib():
    lib = Library()
    lib.add_user(1, "Alice")
    lib.add_user(2, "Bob")
    lib.add_book(10, "Clean Code", "Martin", copies=2)
    lib.add_book(11, "Refactoring", "Fowler", copies=1)
    return lib

def test_checkout_and_return_flow():
    lib = make_lib()
    lib.checkout_book(1, 10, today=date(2025, 10, 1))
    assert len(lib.list_active_loans(1)) == 1
    lib.return_book(1, 10, return_date=date(2025, 10, 3))
    assert lib.list_active_loans(1) == []
    assert lib.books[10].available_copies == 2  # back on shelf

def test_cannot_checkout_inactive_user_or_book():
    lib = make_lib()
    lib.deactivate_user(1)
    with pytest.raises(ValueError):
        lib.checkout_book(1, 10, today=date(2025, 10, 1))

    # reactivate user to test inactive book
    lib.users[1].is_active = True
    lib.remove_book(11)   # mark inactive (must be fully available)
    with pytest.raises(ValueError):
        lib.checkout_book(1, 11, today=date(2025, 10, 1))

def test_max_active_loans_enforced():
    lib = make_lib()
    # add enough single-copy books to hit the cap
    base = 100
    for i in range(MAX_ACTIVE_LOANS_PER_USER):
        lib.add_book(base + i, f"B{base+i}", "Auth", copies=1)
        lib.checkout_book(1, base + i, today=date(2025, 10, 1))
    assert len(lib.list_active_loans(1)) == MAX_ACTIVE_LOANS_PER_USER

    with pytest.raises(ValueError):
        lib.add_book(base + MAX_ACTIVE_LOANS_PER_USER, "Overflow", "Auth", copies=1)
        lib.checkout_book(1, base + MAX_ACTIVE_LOANS_PER_USER, today=date(2025, 10, 1))

def test_overdue_detection():
    lib = make_lib()
    lib.checkout_book(2, 11, today=date(2025, 9, 1))
    overdue = lib.list_overdue_loans(today=date(2025, 10, 1))
    assert len(overdue) == 1
