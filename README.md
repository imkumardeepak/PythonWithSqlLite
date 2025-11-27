# Student Results Dashboard

A lightweight Python web application using Flask and SQLite to display student result statistics on a dashboard.

## Features

- SQLite database for storing student, subject, and result data
- Automatic insertion of dummy student data for demonstration
- Dashboard showing student performance statistics
- Subject-wise performance analysis
- Overall statistics including average, highest, and lowest scores

## Prerequisites

- Python 3.6 or higher

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Run the application:
   ```
   python app.py
   ```

2. Open your web browser and go to `http://127.0.0.1:5000`

## How It Works

- On first run, the application creates an SQLite database with three tables:
  - `students`: Stores student information (name, email)
  - `subjects`: Stores subject names
  - `results`: Stores student scores for each subject
  
- Dummy data is automatically inserted for 10 students across 7 subjects
- The dashboard displays:
  - Overall statistics (average score, highest score, etc.)
  - Student rankings based on average scores
  - Subject performance rankings

## Customization

To add your own data:
1. Modify the `insert_dummy_data()` function in `app.py`
2. Or manually add data to the SQLite database using any SQLite client