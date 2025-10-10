# a1_compat.py
from __future__ import annotations
from datetime import date, timedelta
from typing import Hashable, Dict, Any

from services import LibraryService, DEFAULT_LOAN_DAYS

# Keep a single instance to mimic A1's module-level usage
_LIB = LibraryService()

def register_user(user_id: int, name: str) -> int:
    return _LIB.register_user(user_id, name)

def add_book_to_catalog(title: str, author: str, isbn: Hashable, total_copies: int) -> bool:
    return _LIB.add_book(isbn, title, author, copies=total_copies)

def borrow_book_by_patron(patron_id: int, book_id: Hashable, today: date | None = None) -> Dict[str, Any]:
    loan = _LIB.checkout_book(patron_id, book_id, today=today)
    return {"user_id": patron_id, "book_id": book_id, "due_date": loan.due_date}

def return_book_by_patron(patron_id: int, book_id: Hashable, return_date: date | None = None) -> bool:
    return _LIB.return_book(patron_id, book_id, return_date=return_date)

def calculate_late_fee_for_book(
    patron_id: int, book_id: Hashable, today: date | None = None, per_day: float = 0.25
) -> float:
    """Simple fee: per overdue day * per_day, aggregated; rounded to cents."""
    today = today or date.today()
    dates = _LIB._loan_dates.get((patron_id, book_id), [])  # internal access ok for compat
    fee_cents = 0
    for d in dates:
        overdue_days = (today - (d + timedelta(days=DEFAULT_LOAN_DAYS))).days
        if overdue_days > 0:
            fee_cents += int(round(overdue_days * per_day * 100))
    return round(fee_cents / 100.0, 2)

def search_books_in_catalog(query: str):
    return _LIB.search_books(query)

def get_patron_status_report(patron_id: int) -> Dict[str, Any]:
    user = _LIB.users.get(patron_id)
    loans = _LIB.list_active_loans(patron_id)
    return {
        "is_active": bool(user and user.is_active),
        "active_loans": loans,
        "total_active_loan_count": sum(cnt for _, cnt in loans),
    }
