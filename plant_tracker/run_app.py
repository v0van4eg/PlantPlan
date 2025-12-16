#!/usr/bin/env python3
"""
Script to run the Plant Tracker application
"""

import time
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from app import create_app
from models import db

def wait_for_db():
    """Wait for the database to be ready"""
    app = create_app()  # Create app to get config
    database_url = app.config['SQLALCHEMY_DATABASE_URI']
    
    # Only wait for DB if using PostgreSQL
    if database_url.startswith('postgresql'):
        print("Waiting for database...")
        for attempt in range(30):  # Try for up to 30 seconds
            try:
                engine = create_engine(database_url)
                with engine.connect() as conn:
                    print("Database connection established!")
                    break
            except OperationalError as e:
                print(f"Attempt {attempt + 1}: Could not connect to database: {e}")
                time.sleep(1)
        else:
            print("Could not connect to database after 30 attempts. Exiting.")
            sys.exit(1)

def init_db():
    """Initialize the database tables"""
    # Import the initialization function from init_db.py
    from init_db import init_database
    init_database()

if __name__ == '__main__':
    wait_for_db()
    init_db()
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=5000)