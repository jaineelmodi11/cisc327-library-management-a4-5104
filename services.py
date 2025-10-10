from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional

DEFAULT_LOAN_DAYS = 14
MAX_ACTIVE_LOANS_PER_USER = 3  # adjust if your A1 spec differs

@dataclass
class Book:
    id: int
    title: str
    author: str
    total_copies: int = 1
    available_copies: int = 1
    is_active: bool = True

@dataclass
class User:
    id: int
    name: str
    is_active: bool = True

@dataclass
class Loan:
    user_id: int
    book_id: int
    due_date: date
    returned_on: Optional[date] = None

@dataclass
class Library:
    users: Dict[int, User] = field(default_factory=dict)
    books: Dict[int, Book] = field(default_factory=dict)
    loans: List[Loan] = field(default_factory=list)

    # --- Users ---
    def register_user(self, user_id: int, name: str) -> User:
        if user_id in self.users:
            raise ValueError("User already exists")
        self.users[user_id] = User(id=user_id, name=name, is_active=True)
        return self.users[user_id]

    def deactivate_user(self, user_id: int) -> None:
        user = self._get_user_or_raise(user_id)
        user.is_active = False

    # --- Books ---
    def add_book(self, book_id: int, title: str, author: str, copies: int = 1) -> Book:
        if copies <= 0:
            raise ValueError("Copies must be positive")
        if book_id in self.books:
            b = self.books[book_id]
            b.total_copies += copies
            b.available_copies += copies
            return b
        self.books[book_id] = Book(
            id=book_id, title=title, author=author,
            total_copies=copies, available_copies=copies, is_active=True
        )
        return self.books[book_id]

    def remove_book(self, book_id: int) -> None:
        b = self._get_book_or_raise(book_id)
        if b.total_copies != b.available_copies:
            raise ValueError("Cannot remove: copies are on loan")
        b.is_active = False

    # --- Circulation ---
    def checkout_book(self, user_id: int, book_id: int, today: Optional[date] = None) -> Loan:
        user = self._get_user_or_raise(user_id)
        book = self._get_book_or_raise(book_id)
        if not user.is_active:
            raise ValueError("Inactive user cannot checkout")
        if not book.is_active:
            raise ValueError("Inactive book cannot be checked out")
        if book.available_copies <= 0:
            raise ValueError("No copies available")
        active_loans = [ln for ln in self.loans if ln.user_id == user_id and ln.returned_on is None]
        if len(active_loans) >= MAX_ACTIVE_LOANS_PER_USER:
            raise ValueError("User loan limit reached")
        # If your A1 forbids borrowing same book twice concurrently, uncomment:
        # if any(ln for ln in active_loans if ln.book_id == book_id):
        #     raise ValueError("User already has this book")

        today = today or date.today()
        due = today + timedelta(days=DEFAULT_LOAN_DAYS)
        loan = Loan(user_id=user_id, book_id=book_id, due_date=due)
        self.loans.append(loan)
        book.available_copies -= 1
        return loan

    def return_book(self, user_id: int, book_id: int, return_date: Optional[date] = None) -> Loan:
        loan = self._get_active_loan_or_raise(user_id, book_id)
        return_date = return_date or date.today()
        loan.returned_on = return_date
        book = self.books[book_id]
        book.available_copies += 1
        return loan

    # --- Queries ---
    def list_active_loans(self, user_id: Optional[int] = None) -> List[Loan]:
        return [ln for ln in self.loans if ln.returned_on is None and (user_id is None or ln.user_id == user_id)]

    def list_overdue_loans(self, today: Optional[date] = None) -> List[Loan]:
        today = today or date.today()
        return [ln for ln in self.loans if ln.returned_on is None and ln.due_date < today]

    # --- Helpers ---
    def _get_user_or_raise(self, user_id: int) -> User:
        try:
            return self.users[user_id]
        except KeyError:
            raise ValueError("User not found")

    def _get_book_or_raise(self, book_id: int) -> Book:
        try:
            return self.books[book_id]
        except KeyError:
            raise ValueError("Book not found")

    def _get_active_loan_or_raise(self, user_id: int, book_id: int) -> Loan:
        for ln in self.loans:
            if ln.user_id == user_id and ln.book_id == book_id and ln.returned_on is None:
                return ln
        raise ValueError("Active loan not found")
