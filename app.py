from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"


def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        source TEXT,
        date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        category TEXT,
        description TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()


create_tables()

@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
        except:
            return "Email already exists"
        finally:
            conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/dashboard")
        else:
            return "Invalid login credentials"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    selected_month = request.args.get("month")

    conn = get_db_connection()

    if selected_month:
        month_pattern = selected_month + "%"

        total_income = conn.execute(
            "SELECT IFNULL(SUM(amount), 0) FROM income WHERE user_id = ? AND date LIKE ?",
            (user_id, month_pattern)
        ).fetchone()[0]

        total_expense = conn.execute(
            "SELECT IFNULL(SUM(amount), 0) FROM expenses WHERE user_id = ? AND date LIKE ?",
            (user_id, month_pattern)
        ).fetchone()[0]

        income = conn.execute(
            "SELECT * FROM income WHERE user_id = ? AND date LIKE ? ORDER BY date DESC",
            (user_id, month_pattern)
        ).fetchall()

        expenses = conn.execute(
            "SELECT * FROM expenses WHERE user_id = ? AND date LIKE ? ORDER BY date DESC",
            (user_id, month_pattern)
        ).fetchall()
        
        category_data = conn.execute(
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE user_id = ? AND date LIKE ?
            GROUP BY category
            """,
            (user_id, month_pattern)
        ).fetchall()
    else:
        total_income = conn.execute(
            "SELECT IFNULL(SUM(amount), 0) FROM income WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]

        total_expense = conn.execute(
            "SELECT IFNULL(SUM(amount), 0) FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]

        income = conn.execute(
            "SELECT * FROM income WHERE user_id = ? ORDER BY date DESC",
            (user_id,)
        ).fetchall()

        expenses = conn.execute(
            "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC",
            (user_id,)
        ).fetchall()
        
        category_data = conn.execute(
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE user_id = ?
            GROUP BY category
            """,
            (user_id,)
        ).fetchall()

    conn.close()

    balance = total_income - total_expense
    
    # Convert category_data to list of dicts for JSON serialization
    category_data_list = [{"category": row["category"], "total": row["total"]} for row in category_data]

    return render_template(
        "dashboard.html",
        username=session["username"],
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        income=income,
        expenses=expenses,
        selected_month=selected_month,
        category_data=category_data_list
    )
    
@app.route("/add-income", methods=["GET", "POST"])
def add_income():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        amount = request.form["amount"]
        source = request.form["source"]
        date = request.form["date"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO income (user_id, amount, source, date) VALUES (?, ?, ?, ?)",
            (session["user_id"], amount, source, date)
        )
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_income.html")
    
@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        description = request.form["description"]
        date = request.form["date"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
            (session["user_id"], amount, category, description, date)
        )
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_expense.html")

@app.route("/delete-expense/<int:expense_id>")
def delete_expense(expense_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    conn.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, session["user_id"])
    )
    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/delete-income/<int:income_id>")
def delete_income(income_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    conn.execute(
        "DELETE FROM income WHERE id = ? AND user_id = ?",
        (income_id, session["user_id"])
    )
    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)