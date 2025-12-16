#!/usr/bin/env python3
"""
Simple script to add missing photo_path column to timeline_events table
using the application's database configuration
"""

import os
from sqlalchemy import create_engine, text

def migrate():
    # Use the same database URL as the application
    database_url = os.environ.get('DATABASE_URL', 'postgresql://plant_tracker_user:plant_tracker_password@db:5432/plant_tracker_db')
    
    print(f"Attempting to connect to database: {database_url}")
    
    try:
        engine = create_engine(database_url)
        
        # Check if the column exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'timeline_events' AND column_name = 'photo_path'
            """)).fetchone()
            
            if result:
                print("Column photo_path already exists in timeline_events table")
                return
            
            print("Column photo_path does not exist. Adding it now...")
            
            # Add the missing column
            conn.execute(text("ALTER TABLE timeline_events ADD COLUMN photo_path VARCHAR(255);"))
            conn.commit()
            print("Successfully added photo_path column to timeline_events table")
            
    except Exception as e:
        print(f"Error connecting to database or adding column: {e}")
        print("Note: This script requires the database to be running and accessible.")

if __name__ == '__main__':
    migrate()