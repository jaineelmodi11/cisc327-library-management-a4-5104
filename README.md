# CISC/CMPE-327 – Library Management System (Assignment 4)

This repository contains my **Assignment 4 – End-to-End Testing and Application Containerization** for CISC/CMPE-327 (Software Quality Assurance).

It extends the Library Management System from previous labs/assignments by:

- Adding a simple Flask web UI for listing, adding, and borrowing books  
- Implementing a **Playwright + pytest** browser-based end-to-end (E2E) test  
- Containerizing the app with **Docker** and publishing the image to **Docker Hub**

---

## Project Overview

The web app exposes three main pages:

- `GET /books` – Library catalog (list of books)  
- `GET /books/add` – Form to add a new book  
- `GET /borrow` – Form to borrow an existing book by patron ID  

Data is stored in a local **SQLite** database (`library.db`). On startup, `app.py` calls `init_db()` to create the database and required tables if they do not already exist.

The main E2E test lives in:

```text
tests/test_e2e.py
It simulates a real user:

1. Add a new book via the web form  
2. Verify that the book appears in the catalog  
3. Go to the borrow page  
4. Borrow the same book with a patron ID  
5. Verify that a success message appears
```
---

## Setup & Installation

### 1. Clone the repo

```bash
git clone https://github.com/jaineelmodi11/cisc327-library-management-a4-5104.git
cd cisc327-library-management-a4-5104
```

---
### 2. Create virtual environment & install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate        # on macOS / Linux
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Install Playwright browser binaries (one-time)
playwright install
```

## Running the Flask App (without Docker)

Start the app:

```bash
cd cisc327-library-management-a4-5104
source .venv/bin/activate
python app.py
```

Flask will start on port **5000**. You can access:

- Catalog: `http://localhost:5000/books`  
- Add book: `http://localhost:5000/books/add`  
- Borrow book: `http://localhost:5000/borrow`

---

## Running the E2E Tests

**Important:** Before running pytest, start the Flask app in a separate terminal with:

```bash
cd cisc327-library-management-a4-5104
source .venv/bin/activate
python app.py
```

Then, in a second terminal:

```bash
cd cisc327-library-management-a4-5104
source .venv/bin/activate
pytest tests/test_e2e.py -v
```

The main test is:

```text
tests/test_e2e.py::test_add_and_borrow_book_flow
```

It exercises the full add → verify → borrow → verify flow in a real Chromium browser (headless).

---

## Docker Containerization

The app is containerized using the `python:3.11-slim` base image. The `Dockerfile`:

- Sets the working directory to `/app`
- Installs minimal system packages and Python dependencies from `requirements.txt`
- Copies the application source code into the image
- Sets `FLASK_APP=app:app`, `FLASK_RUN_HOST=0.0.0.0`, `FLASK_RUN_PORT=5000`
- Exposes port **5000**
- Runs `flask run` as the container command

### Build the image

```bash
docker build -t library-app .
```

```bash
docker run -p 5000:5000 library-app
```

Then open:

http://localhost:5000/books

You should be able to add and borrow books through the UI running inside the container.

---

## Docker Hub Image

The image is also published to Docker Hub under my account:

```bash
docker tag library-app jaineelmodi1122222/library-app:v1
docker login
docker push jaineelmodi1122222/library-app:v1
```

Anyone with Docker can run:

```bash
docker pull jaineelmodi1122222/library-app:v1
docker run -p 5000:5000 jaineelmodi1122222/library-app:v1
```

and use the app at http://localhost:5000/books without needing Python or Playwright installed locally.
