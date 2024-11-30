from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_bcrypt import Bcrypt
import sqlite3
from datetime import datetime
from functools import wraps
import time
from time import perf_counter
from sorting_algos import (selection_sort, shell_sort, bucket_sort_with_selection, bucket_sort_with_shell)

app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)

def get_db_connection():
    conn = sqlite3.connect("job_applications.db")  # Ensure this matches the actual path
    conn.row_factory = sqlite3.Row
    return conn


def get_application_count():
    conn = sqlite3.connect("job_applications.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM applications;")
    count = cursor.fetchone()[0]
    conn.close()
    return count

@app.route('/api/application_count', methods=['GET'])
def application_count():
    count = get_application_count()
    return jsonify({'application_count': count})

# Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                         (username, email, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Username or email already exists")
            return redirect(url_for("signup"))
        conn.close()
        flash("Signup successful, please log in.")
        return redirect(url_for("login"))

    return render_template("signup.html")

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        
        if user and bcrypt.check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful!")
            return redirect(url_for("index"))
        else:
            flash("Incorrect email or password.")
    return render_template("login.html")

# Logout Route
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("login"))

# Check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    username = session.get("username")  # Retrieve the username from the session
    
    conn = get_db_connection()
    applications = conn.execute("SELECT * FROM applications WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    
    return render_template("index.html", applications=applications, username=username, filter_type='salary', )

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_application():
    if request.method == "POST":
        title = request.form["title"]
        company = request.form["company"]
        stage = request.form["stage"]
        salary = int(request.form["salary"])
        date_applied = request.form["date_applied"]
        deadline = request.form.get("deadline", None)
        role_type = request.form.get("role_type", None)
        priority = 1 if "priority" in request.form else 0
        user_id = session["user_id"]

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO applications (title, company, stage, salary, date_applied, deadline, role_type, priority, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, company, stage, salary, date_applied, deadline, role_type, priority, user_id))
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add_application.html")


# Route to delete an application by ID
@app.route("/delete/<int:id>", methods=["POST"])
def delete_application(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM applications WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# Route to view applications by filter
algorithm_complexities = {
    "selection": {"time": "O(n²)", "space": "O(1)"},
    "shell": {"time": "O(n log n) - O(n²)", "space": "O(1)"},
    "bucket": {"time": "O(n + k)", "space": "O(n + k)"},
}

filter_key_map = {
    "salary": "salary",
    "date": "date_applied",
    "deadline": "deadline",
    "priority": "priority",
    "stage": "stage"
}

@app.route("/view/<filter_type>")
@login_required
def view_applications(filter_type):
    user_id = session["user_id"]
    username = session.get("username")  # Retrieve the username from the session
    sort_order = request.args.get("order", "asc")  # Default to ascending
    algorithm = request.args.get("algorithm", "selection")  # Default Sorting algorithm
    reverse = sort_order == "desc"
    key = filter_key_map.get(filter_type, "date_applied")  # Default to "date_applied" if no match
    search_query = request.args.get('search', '')
    data_limit = request.args.get("data_limit", "50")

    conn = get_db_connection()

    if data_limit.isdigit():
        limit = int(data_limit)
        applications = conn.execute("SELECT * FROM applications LIMIT ?", (limit,)).fetchall()
    else:
        applications = conn.execute("SELECT * FROM applications").fetchall()

    applications = [dict(app) for app in applications]
    conn.close()


    if search_query:
        applications = [
            app for app in applications
            if search_query.lower() in app['title'].lower() or 
               search_query.lower() in app['company'].lower()
        ]

    # Measure the time taken by the sorting algorithm with higher precision
    start_time = perf_counter()
    


    if algorithm == "selection":
        applications, space_complexity_bytes = selection_sort(applications, key=key, reverse=reverse)
        time_complexity = "O(n^2)"
    elif algorithm == "shell":
        applications, space_complexity_bytes = shell_sort(applications, key=key, reverse=reverse)
        time_complexity = "O(n^1.5) (avg)"
    elif algorithm == "bucket_selection":
        applications, space_complexity_bytes = bucket_sort_with_selection(applications, key=key, reverse=reverse)
        time_complexity = "O(n+k) (bucket) + O(n^2) (selection)"
    elif algorithm == "bucket_shell":
        applications, space_complexity_bytes = bucket_sort_with_shell(applications, key=key, reverse=reverse)
        time_complexity = "O(n+k) (bucket) + O(n^1.5) (shell)"


    # Calculate elapsed time in milliseconds
    elapsed_time_ms = f"{(perf_counter() - start_time):010.6f}"

    # Check if it's an AJAX request and return the appropriate template
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('applications_table.html', applications=applications)

    # Pass time and space complexity as separate variables
    return render_template(
        'view_applications.html',
        applications=applications,
        filter_type=filter_type,
        sort_order=sort_order,
        algorithm=algorithm,
        elapsed_time_ms=elapsed_time_ms,
        time_complexity=time_complexity,
        space_complexity_bytes=space_complexity_bytes,  # Pass space complexity in bytes
        username=username,
        data_limit=data_limit
    )

# Route to update the stage of an application
@app.route("/update_stage/<int:id>", methods=["POST"])
def update_stage(id):
    new_stage = request.form["stage"]
    conn = get_db_connection()
    conn.execute("UPDATE applications SET stage = ? WHERE id = ?", (new_stage, id))
    conn.commit()
    conn.close()
    
    return redirect(url_for("index"))


# Route to search applications by role type
@app.route("/search", methods=["GET", "POST"])
def search():
    applications = None
    if request.method == "POST":
        role_type = request.form["role_type"]
        conn = get_db_connection()
        applications = conn.execute("SELECT * FROM applications WHERE role_type = ?", (role_type,)).fetchall()
        conn.close()
    return render_template("view_applications.html", applications=applications, filter_type="search")



if __name__ == "__main__":
    app.run(debug=True)

    