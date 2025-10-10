# services.py
from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional, Hashable

# ---- Assignment constants ----
DEFAULT_LOAN_DAYS = 14
MAX_ACTIVE_LOANS_PER_USER = 3


@dataclass
class User:
    user_id: int
    name: str
    is_active: bool = True


@dataclass
class Book:
    book_id: Hashable           # supports int IDs or string ISBNs
    title: str
    author: str
    copies: int                 # total copies in the catalog
    available_copies: int       # copies currently on shelf
    is_active: bool = True

    # Alias expected by some tests
    @property
    def total_copies(self) -> int:
        return self.copies


@dataclass
class Loan:
    user_id: int
    book_id: Hashable
    checkout_date: date
    due_date: date


class LibraryService:
    """
    In-memory Library with two compatible APIs:

    A) Human-written tests API (IDs are ints; invalid ops raise ValueError):
       - register_user(user_id, name)  OR register_user(name)
       - add_user(user_id, name)       OR add_user(name)
       - add_book(book_id, title, author, copies=1)
       - checkout_book(user_id, book_id, today=...) -> Loan
       - return_book(user_id, book_id, return_date=...) -> bool
       - list_active_loans(user_id) -> list[(book_id, count)]
       - list_overdue_loans(today=...) -> list[(user_id, book_id)]
       - deactivate_user(user_id)
       - remove_book(book_id)   (only when fully available)
       - public: users: Dict[int, User], books: Dict[Hashable, Book]

    B) AI-generated tests API (string ISBNs; booleans instead of exceptions):
       - register_book(isbn, title, author, copies=1) -> bool
       - loan_book(user_id, isbn) -> bool
       - return_book(user_id, isbn) -> bool
       - search_books(query) -> list of dicts {isbn,title,author,copies,available}
    """

    def __init__(self):
        # public maps (tests access these directly)
        self.users: Dict[int, User] = {}
        self.books: Dict[Hashable, Book] = {}

        self._next_user_id = 1
        # active loans: (user_id, book_id) -> list of loan dates (one per active copy)
        self._loan_dates: Dict[Tuple[int, Hashable], List[date]] = defaultdict(list)

    # ---------- Users ----------
    def add_user(self, *args) -> int:
        """
        add_user(name) -> auto-ID
        add_user(user_id, name) -> explicit ID
        """
        if len(args) == 1:
            name = args[0]
            if not isinstance(name, str) or not name.strip():
                raise ValueError("name must be a non-empty string")
            uid = self._next_user_id
            self.users[uid] = User(uid, name.strip(), True)
            self._next_user_id += 1
            return uid
        elif len(args) == 2:
            uid, name = args
            if not isinstance(uid, int) or uid <= 0:
                raise ValueError("user_id must be a positive int")
            if not isinstance(name, str) or not name.strip():
                raise ValueError("name must be a non-empty string")
            self.users[uid] = User(uid, name.strip(), True)
            self._next_user_id = max(self._next_user_id, uid + 1)
            return uid
        else:
            raise TypeError("add_user expects (name) or (user_id, name)")

    # alias expected by some tests
    def register_user(self, *args) -> int:
        return self.add_user(*args)

    def get_user(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)

    def deactivate_user(self, user_id: int) -> None:
        u = self.users.get(user_id)
        if not u:
            raise ValueError("no such user")
        u.is_active = False

    # ---------- Books ----------
    def add_book(self, book_id: Hashable, title: str, author: str, copies: int = 1) -> bool:
        if copies < 1:
            raise ValueError("copies must be >= 1")
        if book_id in self.books:
            b = self.books[book_id]
            if not b.is_active:
                b.is_active = True
            b.copies += int(copies)
            b.available_copies += int(copies)
            return True
        self.books[book_id] = Book(book_id, title or "", author or "", int(copies), int(copies), True)
        return True

    def remove_book(self, book_id: Hashable) -> None:
        b = self.books.get(book_id)
        if not b:
            raise ValueError("no such book")
        if b.available_copies != b.copies:
            raise ValueError("book has outstanding loans")
        b.is_active = False

    def get_book(self, book_id: Hashable) -> Optional[Book]:
        return self.books.get(book_id)

    # ---------- Loans (human API: raise on invalid; returns Loan) ----------
    def _active_loans_for_user(self, user_id: int) -> int:
        return sum(len(dates) for (uid, _), dates in self._loan_dates.items() if uid == user_id)

    def checkout_book(self, user_id: int, book_id: Hashable, today: Optional[date] = None) -> Loan:
        today = today or date.today()
        u = self.users.get(user_id)
        if not u or not u.is_active:
            raise ValueError("invalid or inactive user")
        b = self.books.get(book_id)
        if not b or not b.is_active:
            raise ValueError("invalid or inactive book")
        if b.available_copies <= 0:
            raise ValueError("no copies available")
        if self._active_loans_for_user(user_id) >= MAX_ACTIVE_LOANS_PER_USER:
            raise ValueError("max active loans reached")

        b.available_copies -= 1
        self._loan_dates[(user_id, book_id)].append(today)
        due = today + timedelta(days=DEFAULT_LOAN_DAYS)
        return Loan(user_id=user_id, book_id=book_id, checkout_date=today, due_date=due)

    def return_book(self, user_id: int, book_id: Hashable, return_date: Optional[date] = None) -> bool:
        key = (user_id, book_id)
        dates = self._loan_dates.get(key)
        if not dates:
            return False
        dates.pop()  # remove one active copy
        self.books[book_id].available_copies += 1
        if not dates:
            self._loan_dates.pop(key, None)
        return True

    def list_active_loans(self, user_id: int) -> List[Tuple[Hashable, int]]:
        """Return [(book_id, count), ...] for user's active loans."""
        out: List[Tuple[Hashable, int]] = []
        for (uid, bid), dates in self._loan_dates.items():
            if uid == user_id and dates:
                out.append((bid, len(dates)))
        return out

    def list_overdue_loans(self, today: Optional[date] = None) -> List[Tuple[int, Hashable]]:
        """Return [(user_id, book_id), ...] where any copy is overdue."""
        today = today or date.today()
        overdue: List[Tuple[int, Hashable]] = []
        for (uid, bid), dates in self._loan_dates.items():
            for d in dates:
                if (today - d) > timedelta(days=DEFAULT_LOAN_DAYS):
                    overdue.append((uid, bid))
                    break
        return overdue

    # ---------- Search ----------
    def search_books(self, query: str):
        """Case-insensitive substring on title/author; returns list of dicts (AI tests format)."""
        q = (str(query) if query is not None else "").lower().strip()
        results = []
        for b in self.books.values():
            if not b.is_active:
                continue
            if q in b.title.lower() or q in b.author.lower():
                results.append(
                    {
                        "isbn": str(b.book_id),   # keep key name 'isbn' for AI tests
                        "title": b.title,
                        "author": b.author,
                        "copies": b.copies,
                        "available": b.available_copies,
                    }
                )
        return results

    # ---------- AI tests compatibility (boolean returns) ----------
    def register_book(self, isbn: str, title: str, author: str, copies: int = 1) -> bool:
        return self.add_book(isbn, title, author, copies)

    def loan_book(self, user_id: int, isbn: Hashable) -> bool:
        u = self.users.get(user_id)
        b = self.books.get(isbn)
        if not u or not b or not b.is_active or b.available_copies <= 0:
            return False
        if self._active_loans_for_user(user_id) >= MAX_ACTIVE_LOANS_PER_USER:
            return False
        b.available_copies -= 1
        self._loan_dates[(user_id, isbn)].append(date.today())
        return True


# Alias used by some tests
Library = LibraryService
