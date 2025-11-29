import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import random
import os
import stat

app = Flask(__name__)

# Database setup
DATABASE = 'student_results.db'

def init_db():
    """Initialize the database with tables"""
    # Ensure the database file has proper permissions
    if os.path.exists(DATABASE):
        # Make sure the database file is writable
        os.chmod(DATABASE, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Create subjects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Create results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject_id INTEGER,
            score REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Ensure the database file has proper permissions after creation
    if os.path.exists(DATABASE):
        os.chmod(DATABASE, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)

def insert_dummy_data():
    """Insert dummy student data, subjects, and results for demonstration"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Check if we already have data
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        
        if student_count == 0:
            # Insert dummy students
            students = [
                ('Alice Johnson', 'alice@example.com'),
                ('Bob Smith', 'bob@example.com'),
                ('Charlie Brown', 'charlie@example.com'),
                ('Diana Prince', 'diana@example.com'),
                ('Edward Norton', 'edward@example.com'),
                ('Fiona Gallagher', 'fiona@example.com'),
                ('George Clooney', 'george@example.com'),
                ('Helen Keller', 'helen@example.com'),
                ('Ian Malcolm', 'ian@example.com'),
                ('Julia Roberts', 'julia@example.com')
            ]
            
            cursor.executemany('INSERT INTO students (name, email) VALUES (?, ?)', students)
            
            # Insert subjects
            subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'History', 'Computer Science']
            subject_data = [(subject,) for subject in subjects]
            cursor.executemany('INSERT OR IGNORE INTO subjects (name) VALUES (?)', subject_data)
            
            # Get student IDs and subject IDs
            cursor.execute('SELECT id FROM students')
            student_ids = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT id FROM subjects')
            subject_ids = [row[0] for row in cursor.fetchall()]
            
            # Insert random results for each student in each subject
            results = []
            for student_id in student_ids:
                for subject_id in subject_ids:
                    score = round(random.uniform(50, 100), 2)  # Random score between 50-100
                    results.append((student_id, subject_id, score))
            
            cursor.executemany('INSERT INTO results (student_id, subject_id, score) VALUES (?, ?, ?)', results)
        
        conn.commit()
    finally:
        if conn:
            conn.close()

def get_student_statistics():
    """Get statistics for all students"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Get average scores for each student
        cursor.execute('''
            SELECT s.name, AVG(r.score) as average_score, COUNT(r.id) as subjects_count
            FROM students s
            JOIN results r ON s.id = r.student_id
            GROUP BY s.id, s.name
            ORDER BY average_score DESC
        ''')
        
        student_stats = cursor.fetchall()
        return student_stats
    finally:
        if conn:
            conn.close()

def get_subject_statistics():
    """Get statistics for all subjects"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Get average scores for each subject
        cursor.execute('''
            SELECT sub.name, AVG(r.score) as average_score, COUNT(r.id) as student_count
            FROM subjects sub
            JOIN results r ON sub.id = r.subject_id
            GROUP BY sub.id, sub.name
            ORDER BY average_score DESC
        ''')
        
        subject_stats = cursor.fetchall()
        return subject_stats
    finally:
        if conn:
            conn.close()

def get_overall_statistics():
    """Get overall statistics"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Get overall average score
        cursor.execute('SELECT AVG(score) FROM results')
        overall_avg = cursor.fetchone()[0]
        
        # Get highest and lowest scores
        cursor.execute('SELECT MAX(score), MIN(score) FROM results')
        max_min_scores = cursor.fetchone()
        
        # Get total number of students and results
        cursor.execute('SELECT COUNT(*) FROM students')
        total_students = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM results')
        total_results = cursor.fetchone()[0]
        
        return {
            'average_score': round(overall_avg, 2) if overall_avg else 0,
            'highest_score': max_min_scores[0] if max_min_scores[0] else 0,
            'lowest_score': max_min_scores[1] if max_min_scores[1] else 0,
            'total_students': total_students,
            'total_results': total_results
        }
    finally:
        if conn:
            conn.close()

@app.route('/')
def dashboard():
    """Main dashboard route"""
    # Initialize database and insert dummy data if needed
    init_db()
    insert_dummy_data()
    
    # Get statistics
    student_stats = get_student_statistics()
    subject_stats = get_subject_statistics()
    overall_stats = get_overall_statistics()
    
    return render_template('dashboard.html', 
                          student_stats=student_stats,
                          subject_stats=subject_stats,
                          overall_stats=overall_stats)

# === STUDENT CRUD ROUTES ===

@app.route('/students')
def students_list():
    """Display all students"""
    students = get_all_students()
    return render_template('students.html', students=students)

@app.route('/students/add', methods=['GET', 'POST'])
def add_student_form():
    """Add a new student"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        student_id = add_student(name, email)
        if student_id:
            return redirect(url_for('students_list'))
        else:
            return render_template('add_student.html', error='Email already exists')
    return render_template('add_student.html')

@app.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student_form(student_id):
    """Edit an existing student"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        success = update_student(student_id, name, email)
        if success:
            return redirect(url_for('students_list'))
        else:
            student = get_student_by_id(student_id)
            return render_template('edit_student.html', student=student, error='Email already exists')
    else:
        student = get_student_by_id(student_id)
        if student:
            return render_template('edit_student.html', student=student)
        else:
            return redirect(url_for('students_list'))

@app.route('/students/delete/<int:student_id>', methods=['POST'])
def delete_student_route(student_id):
    """Delete a student"""
    delete_student(student_id)
    return redirect(url_for('students_list'))

# === SUBJECT CRUD ROUTES ===

@app.route('/subjects')
def subjects_list():
    """Display all subjects"""
    subjects = get_all_subjects()
    return render_template('subjects.html', subjects=subjects)

@app.route('/subjects/add', methods=['GET', 'POST'])
def add_subject_form():
    """Add a new subject"""
    if request.method == 'POST':
        name = request.form['name']
        subject_id = add_subject(name)
        if subject_id:
            return redirect(url_for('subjects_list'))
        else:
            return render_template('add_subject.html', error='Subject already exists')
    return render_template('add_subject.html')

@app.route('/subjects/edit/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject_form(subject_id):
    """Edit an existing subject"""
    if request.method == 'POST':
        name = request.form['name']
        success = update_subject(subject_id, name)
        if success:
            return redirect(url_for('subjects_list'))
        else:
            subject = get_subject_by_id(subject_id)
            return render_template('edit_subject.html', subject=subject, error='Subject already exists')
    else:
        subject = get_subject_by_id(subject_id)
        if subject:
            return render_template('edit_subject.html', subject=subject)
        else:
            return redirect(url_for('subjects_list'))

@app.route('/subjects/delete/<int:subject_id>', methods=['POST'])
def delete_subject_route(subject_id):
    """Delete a subject"""
    delete_subject(subject_id)
    return redirect(url_for('subjects_list'))

# === RESULT CRUD ROUTES ===

@app.route('/results')
def results_list():
    """Display all results"""
    results = get_all_results()
    return render_template('results.html', results=results)

def get_all_students():
    """Get all students from the database"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email FROM students ORDER BY name')
        students = cursor.fetchall()
        return students
    finally:
        if conn:
            conn.close()

def get_student_by_id(student_id):
    """Get a specific student by ID"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email FROM students WHERE id = ?', (student_id,))
        student = cursor.fetchone()
        return student
    finally:
        if conn:
            conn.close()

def add_student(name, email):
    """Add a new student to the database"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO students (name, email) VALUES (?, ?)', (name, email))
        student_id = cursor.lastrowid
        conn.commit()
        return student_id
    except sqlite3.IntegrityError:
        return None  # Email already exists
    except sqlite3.OperationalError as e:
        return None  # Database operation failed
    finally:
        if conn:
            conn.close()

def update_student(student_id, name, email):
    """Update an existing student's information"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('UPDATE students SET name = ?, email = ? WHERE id = ?', (name, email, student_id))
        conn.commit()
        success = cursor.rowcount > 0
        return success
    except sqlite3.IntegrityError:
        return False  # Email already exists
    except sqlite3.OperationalError as e:
        return False  # Database operation failed
    finally:
        if conn:
            conn.close()

def delete_student(student_id):
    """Delete a student from the database"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        # First delete related results
        cursor.execute('DELETE FROM results WHERE student_id = ?', (student_id,))
        # Then delete the student
        cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted
    finally:
        if conn:
            conn.close()

# === SUBJECT CRUD FUNCTIONS ===

def get_all_subjects():
    """Get all subjects from the database"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM subjects ORDER BY name')
        subjects = cursor.fetchall()
        return subjects
    finally:
        if conn:
            conn.close()

def get_subject_by_id(subject_id):
    """Get a specific subject by ID"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM subjects WHERE id = ?', (subject_id,))
        subject = cursor.fetchone()
        return subject
    finally:
        if conn:
            conn.close()

def add_subject(name):
    """Add a new subject to the database"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO subjects (name) VALUES (?)', (name,))
        subject_id = cursor.lastrowid
        conn.commit()
        return subject_id
    except sqlite3.IntegrityError:
        return None  # Subject already exists
    finally:
        if conn:
            conn.close()

def update_subject(subject_id, name):
    """Update an existing subject's name"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('UPDATE subjects SET name = ? WHERE id = ?', (name, subject_id))
        conn.commit()
        success = cursor.rowcount > 0
        return success
    except sqlite3.IntegrityError:
        return False  # Subject already exists
    finally:
        if conn:
            conn.close()

def delete_subject(subject_id):
    """Delete a subject from the database"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        # First delete related results
        cursor.execute('DELETE FROM results WHERE subject_id = ?', (subject_id,))
        # Then delete the subject
        cursor.execute('DELETE FROM subjects WHERE id = ?', (subject_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted
    finally:
        if conn:
            conn.close()

# === RESULT CRUD FUNCTIONS ===

def get_all_results():
    """Get all results with student and subject information"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.id, s.name as student_name, sub.name as subject_name, r.score
            FROM results r
            JOIN students s ON r.student_id = s.id
            JOIN subjects sub ON r.subject_id = sub.id
            ORDER BY s.name, sub.name
        ''')
        results = cursor.fetchall()
        return results
    finally:
        if conn:
            conn.close()

def get_result_by_id(result_id):
    """Get a specific result by ID"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.id, r.student_id, r.subject_id, r.score, s.name as student_name, sub.name as subject_name
            FROM results r
            JOIN students s ON r.student_id = s.id
            JOIN subjects sub ON r.subject_id = sub.id
            WHERE r.id = ?
        ''', (result_id,))
        result = cursor.fetchone()
        return result
    finally:
        if conn:
            conn.close()

def add_result(student_id, subject_id, score):
    """Add a new result to the database"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO results (student_id, subject_id, score) VALUES (?, ?, ?)', 
                      (student_id, subject_id, score))
        result_id = cursor.lastrowid
        conn.commit()
        return result_id
    except sqlite3.IntegrityError:
        return None
    finally:
        if conn:
            conn.close()

def update_result(result_id, student_id, subject_id, score):
    """Update an existing result"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('UPDATE results SET student_id = ?, subject_id = ?, score = ? WHERE id = ?', 
                      (student_id, subject_id, score, result_id))
        conn.commit()
        success = cursor.rowcount > 0
        return success
    finally:
        if conn:
            conn.close()

def delete_result(result_id):
    """Delete a result from the database"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM results WHERE id = ?', (result_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted
    finally:
        if conn:
            conn.close()


@app.route('/results/add', methods=['GET', 'POST'])
def add_result_form():
    """Add a new result"""
    if request.method == 'POST':
        student_id = int(request.form['student_id'])
        subject_id = int(request.form['subject_id'])
        score = float(request.form['score'])
        result_id = add_result(student_id, subject_id, score)
        if result_id:
            return redirect(url_for('results_list'))
        else:
            students = get_all_students()
            subjects = get_all_subjects()
            return render_template('add_result.html', students=students, subjects=subjects, error='Error adding result')
    else:
        students = get_all_students()
        subjects = get_all_subjects()
        return render_template('add_result.html', students=students, subjects=subjects)

@app.route('/results/edit/<int:result_id>', methods=['GET', 'POST'])
def edit_result_form(result_id):
    """Edit an existing result"""
    if request.method == 'POST':
        student_id = int(request.form['student_id'])
        subject_id = int(request.form['subject_id'])
        score = float(request.form['score'])
        success = update_result(result_id, student_id, subject_id, score)
        if success:
            return redirect(url_for('results_list'))
        else:
            result = get_result_by_id(result_id)
            students = get_all_students()
            subjects = get_all_subjects()
            return render_template('edit_result.html', result=result, students=students, subjects=subjects, error='Error updating result')
    else:
        result = get_result_by_id(result_id)
        if result:
            students = get_all_students()
            subjects = get_all_subjects()
            return render_template('edit_result.html', result=result, students=students, subjects=subjects)
        else:
            return redirect(url_for('results_list'))

@app.route('/results/delete/<int:result_id>', methods=['POST'])
def delete_result_route(result_id):
    """Delete a result"""
    delete_result(result_id)
    return redirect(url_for('results_list'))

if __name__ == '__main__':
    # Initialize database
    init_db()
    # Insert dummy data
    insert_dummy_data()
    # Run the app
    import os
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5005))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)

