#!/usr/bin/env python3
"""
Migration script to add photo_path column to timeline_events table
"""

import os
from sqlalchemy import create_engine, text

# Get database URL from environment or use default
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://plant_tracker_user:plant_tracker_password@db:5432/plant_tracker_db')

def migrate():
    engine = create_engine(DATABASE_URL)
    
    # Check if column already exists
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'timeline_events' AND column_name = 'photo_path'
        """))
        
        if result.fetchone():
            print("Column photo_path already exists in timeline_events table")
            return
        
        # Add the photo_path column
        try:
            conn.execute(text("ALTER TABLE timeline_events ADD COLUMN photo_path VARCHAR(255);"))
            conn.commit()
            print("Successfully added photo_path column to timeline_events table")
        except Exception as e:
            print(f"Error adding column: {e}")
            conn.rollback()

if __name__ == '__main__':
    migrate()