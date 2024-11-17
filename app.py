import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a more secure key for production

# Function to initialize the database (creates tables based on schema.sql)
def init_db():
    conn = sqlite3.connect('hw13.db')
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())  # Executes the SQL commands to create tables
    conn.commit()
    conn.close()

# Check if the user is logged in
def is_logged_in():
    return 'logged_in' in session and session['logged_in'] == True

# Part II: Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'password':  # Hardcoded credentials
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials, please try again.')
            return redirect(url_for('login'))  # Redirect to login page if credentials are wrong

    return render_template('login.html')

# Root Route - Redirect to login page
@app.route('/')
def index():
    return redirect(url_for('login'))

# Part III: Dashboard Route
@app.route('/dashboard')
def dashboard():
    if not is_logged_in():  # Protect dashboard if user is not logged in
        return redirect(url_for('login'))

    conn = sqlite3.connect('hw13.db')
    cursor = conn.cursor()

    # Fetch students and quizzes
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT * FROM quizzes")
    quizzes = cursor.fetchall()

    conn.close()

    return render_template('dashboard.html', students=students, quizzes=quizzes)

# Part IV: Add Student Route
@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if not is_logged_in():  # Protect add student route
        return redirect(url_for('login'))

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        conn = sqlite3.connect('hw13.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO students (first_name, last_name) VALUES (?, ?)",
                       (first_name, last_name))
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))  # After adding a student, redirect to dashboard

    return render_template('add_student.html')

# Part V: Add Quiz Route
@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if not is_logged_in():  # Protect add quiz route
        return redirect(url_for('login'))

    if request.method == 'POST':
        subject = request.form['subject']
        questions_count = request.form['questions_count']
        date_given = request.form['date_given']

        conn = sqlite3.connect('hw13.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO quizzes (subject, questions_count, date_given) VALUES (?, ?, ?)",
                       (subject, questions_count, date_given))
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))  # After adding a quiz, redirect to dashboard

    return render_template('add_quiz.html')

# Part VI: Student Results Route
@app.route('/student/<int:id>')
def student_results(id):
    if not is_logged_in():  # Protect student results route
        return redirect(url_for('login'))

    conn = sqlite3.connect('hw13.db')
    cursor = conn.cursor()

    # Fetch student quiz results
    cursor.execute("""
        SELECT quizzes.id, quizzes.subject, results.score
        FROM results
        JOIN quizzes ON results.quiz_id = quizzes.id
        WHERE results.student_id = ?
    """, (id,))
    results = cursor.fetchall()

    conn.close()

    if results:
        return render_template('student_results.html', results=results)
    else:
        return "No results"

# Part VII: Add Result Route
@app.route('/results/add', methods=['GET', 'POST'])
def add_result():
    if not is_logged_in():  # Protect add result route
        return redirect(url_for('login'))

    conn = sqlite3.connect('hw13.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, first_name, last_name FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT id, subject FROM quizzes")
    quizzes = cursor.fetchall()

    if request.method == 'POST':
        student_id = request.form['student_id']
        quiz_id = request.form['quiz_id']
        score = request.form['score']

        cursor.execute("""
            INSERT INTO results (student_id, quiz_id, score)
            VALUES (?, ?, ?)
        """, (student_id, quiz_id, score))
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))  # After adding result, redirect to dashboard

    conn.close()

    return render_template('add_result.html', students=students, quizzes=quizzes)

# Logout route to clear session
@app.route('/logout')
def logout():
    session['logged_in'] = False  # Log out the user
    return redirect(url_for('login'))  # Redirect to login page

if __name__ == '__main__':
    # Uncomment the next line to initialize the database (first-time setup)
    init_db()  # Initialize the DB and create tables (only run once, comment after)

    app.run(debug=True)
