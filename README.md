# CISC/CMPE 327 – Library Management System (A2)

[![CI](https://github.com/jaineelmodi11/cisc327-library-management-a2-5104/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/jaineelmodi11/cisc327-library-management-a2-5104/actions/workflows/ci.yml)

**Repository:** https://github.com/jaineelmodi11/cisc327-library-management-a2-5104

## Project structure
- `services.py` — core Library business logic (users, books, loans)
- `a1_compat.py` — A1 function-name compatibility layer delegating to `LibraryService`
- `tests/` — unit tests (both human-written and AI-generated)
- `.github/workflows/ci.yml` — GitHub Actions workflow (pytest + coverage)
- `requirements.txt` — test dependencies
- `pytest.ini` — pytest configuration


## A1 → A2 Mapping

This A2 **continues** my A1 library project. The original A1 function names are preserved via `a1_compat.py`, which delegates to the class-based `LibraryService` used in A2.

| A1 function                   | A2 implementation (services.py)                          |
|------------------------------|-----------------------------------------------------------|
| `add_book_to_catalog`        | `add_book` / `register_book`                              |
| `borrow_book_by_patron`      | `checkout_book` (raises on invalid) / `loan_book` (bool)  |
| `return_book_by_patron`      | `return_book`                                             |
| `calculate_late_fee_for_book`| Provided in `a1_compat.py` (simple per-day fee)           |
| `search_books_in_catalog`    | `search_books`                                            |
| `get_patron_status_report`   | `list_active_loans` (+ direct `users`/`books` access)     |

> A2 adds due dates (via a `Loan` object), a per-user active-loan cap, and overdue detection.  
> The `a1_compat.py` module keeps A1-style code working without changes.


## Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
pytest
```

## CI/CD
Every push runs GitHub Actions:
- installs deps,
- runs tests with coverage,
- uploads `coverage.xml` as an artifact.

The badge above shows the latest workflow status.

## Run with coverage locally (optional)
```bash
pytest --cov=. --cov-report=term
```

## Troubleshooting
- If `pytest` can’t find modules, ensure you’re running from the repo root and that `pytest.ini` has `pythonpath = .`.
- If a virtualenv folder shows up in Git, add `.venv/` to `.gitignore`.
