# CISC/CMPE 327 – Library Management System (A2)

![CI](https://github.com/jaineelmodi11/cisc327-library-management-a2-5104/actions/workflows/ci.yml/badge.svg)

**Repository:** https://github.com/jaineelmodi11/cisc327-library-management-a2-5104

## Project structure
- `services.py` — core Library business logic (users, books, loans)
- `tests/` — unit tests (both human-written and AI-generated)
- `.github/workflows/ci.yml` — GitHub Actions workflow (pytest + coverage)
- `requirements.txt` — test dependencies
- `pytest.ini` — pytest configuration

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
