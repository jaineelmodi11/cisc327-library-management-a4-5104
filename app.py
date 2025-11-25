import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

# Path to the SQLite database inside the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "library.db")


def get_db():
    """Return a connection to the SQLite DB."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist yet."""
    conn = get_db()
    cur = conn.cursor()

    # Simple books table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT NOT NULL,
            copies INTEGER NOT NULL
        )
        """
    )

    # Simple loans table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            patron_id TEXT NOT NULL,
            loan_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
        """
    )

    conn.commit()
    conn.close()


app = Flask(__name__)
# Needed for flash() messages
app.config["SECRET_KEY"] = "dev-secret-change-me"

# Ensure DB exists on startup
init_db()


@app.route("/")
def index():
    return redirect(url_for("list_books"))


@app.route("/books")
def list_books():
    """Show the catalog of books."""
    conn = get_db()
    books = conn.execute(
        "SELECT id, title, author, isbn, copies FROM books ORDER BY id"
    ).fetchall()
    conn.close()
    return render_template("books.html", books=books)


@app.route("/books/add", methods=["GET", "POST"])
def add_book():
    """Add a new book to the catalog via form."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        isbn = request.form.get("isbn", "").strip()
        copies_raw = request.form.get("copies", "").strip()

        if not title or not author or not isbn or not copies_raw:
            flash("All fields are required.", "error")
            return redirect(url_for("add_book"))

        try:
            copies = int(copies_raw)
        except ValueError:
            flash("Copies must be a number.", "error")
            return redirect(url_for("add_book"))

        conn = get_db()
        conn.execute(
            "INSERT INTO books (title, author, isbn, copies) VALUES (?, ?, ?, ?)",
            (title, author, isbn, copies),
        )
        conn.commit()
        conn.close()

        flash(f"Book '{title}' added.", "success")
        return redirect(url_for("list_books"))

    return render_template("add_book.html")


@app.route("/borrow", methods=["GET", "POST"])
def borrow_book():
    """Borrow a book using a patron ID."""
    conn = get_db()

    if request.method == "POST":
        book_id = request.form.get("book_id")
        patron_id = request.form.get("patron_id", "").strip()

        if not book_id or not patron_id:
            flash("Book and patron ID are required.", "error")
            conn.close()
            return redirect(url_for("borrow_book"))

        cur = conn.cursor()
        cur.execute("SELECT copies FROM books WHERE id = ?", (book_id,))
        row = cur.fetchone()

        if row is None:
            flash("Book not found.", "error")
        elif row["copies"] <= 0:
            flash("No copies available for this book.", "error")
        else:
            # Record loan + decrement copies
            cur.execute(
                "INSERT INTO loans (book_id, patron_id) VALUES (?, ?)",
                (book_id, patron_id),
            )
            cur.execute(
                "UPDATE books SET copies = copies - 1 WHERE id = ?",
                (book_id,),
            )
            conn.commit()
            flash(
                f"Book borrowed successfully by patron {patron_id}.",
                "success",
            )

        conn.close()
        return redirect(url_for("list_books"))

    # GET: show borrow form only for books with available copies
    books = conn.execute(
        "SELECT id, title FROM books WHERE copies > 0 ORDER BY title"
    ).fetchall()
    conn.close()
    return render_template("borrow.html", books=books)


if __name__ == "__main__":
    # Local dev: python app.py
    app.run(host="0.0.0.0", port=5000, debug=True)
