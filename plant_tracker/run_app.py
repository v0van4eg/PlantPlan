#!/usr/bin/env python3
"""
Script to run the Plant Tracker application
"""

import time
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from app import app, db

def wait_for_db():
    """Wait for the database to be ready"""
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
    with app.app_context():
        db.create_all()
        
        # Check if growth phases already exist to avoid duplicates
        from models import GrowthPhase
        
        existing_count = GrowthPhase.query.count()
        if existing_count == 0:
            # Add default growth phases
            phases = [
                {'name': 'Seed', 'description': 'Initial seed stage', 'phase_order': 1},
                {'name': 'Germination', 'description': 'Seed germinating', 'phase_order': 2},
                {'name': 'Seedling', 'description': 'Young plant emerging', 'phase_order': 3},
                {'name': 'Vegetative', 'description': 'Growing leaves and roots', 'phase_order': 4},
                {'name': 'Flowering', 'description': 'Developing flowers', 'phase_order': 5},
                {'name': 'Fruiting', 'description': 'Producing fruits', 'phase_order': 6},
                {'name': 'Harvest', 'description': 'Ready for harvest', 'phase_order': 7},
            ]
            
            for phase_data in phases:
                phase = GrowthPhase(**phase_data)
                db.session.add(phase)
            
            db.session.commit()
            print("Added default growth phases to database")

if __name__ == '__main__':
    wait_for_db()
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)