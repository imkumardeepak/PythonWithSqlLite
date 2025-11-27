"""
WSGI entry point for the Student Results Dashboard application.
This file is required for running the application with Gunicorn in production.
"""

from app import app

if __name__ == "__main__":
    app.run()