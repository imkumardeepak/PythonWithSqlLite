import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import random
import os

app = Flask(__name__)

# Database setup
DATABASE = 'student_results.db'

def init_db():
    """Initialize the database with tables"""
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

def insert_dummy_data():
    """Insert dummy student data, subjects, and results for demonstration"""
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
    conn.close()

def get_student_statistics():
    """Get statistics for all students"""
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
    conn.close()
    return student_stats

def get_subject_statistics():
    """Get statistics for all subjects"""
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
    conn.close()
    return subject_stats

def get_overall_statistics():
    """Get overall statistics"""
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
    
    conn.close()
    
    return {
        'average_score': round(overall_avg, 2) if overall_avg else 0,
        'highest_score': max_min_scores[0] if max_min_scores[0] else 0,
        'lowest_score': max_min_scores[1] if max_min_scores[1] else 0,
        'total_students': total_students,
        'total_results': total_results
    }

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

if __name__ == '__main__':
    # Initialize database
    init_db()
    # Insert dummy data
    insert_dummy_data()
    # Run the app
    import os
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)
