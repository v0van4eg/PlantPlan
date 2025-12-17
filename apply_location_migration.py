#!/usr/bin/env python3
"""
Script to apply the photo_data column to the locations table in the database
"""

import os
from app import create_app
from models import db, Location

def apply_migration():
    app = create_app()
    
    with app.app_context():
        # Check if the column exists by trying to access it
        try:
            # Try to query the location table to see if photo_data exists
            location = Location.query.first()
            # If we can access photo_data without error, the column exists
            _ = location.photo_data if location else None
            print("Column 'photo_data' already exists in 'locations' table.")
            return
        except Exception as e:
            print(f"Column 'photo_data' does not exist in 'locations' table. Error: {e}")
            
        # Since the column doesn't exist, let's execute raw SQL to add it
        try:
            db.session.execute(db.text("ALTER TABLE locations ADD COLUMN photo_data BYTEA;"))
            db.session.commit()
            print("Successfully added 'photo_data' column to 'locations' table.")
        except Exception as e:
            print(f"Error adding column: {e}")
            db.session.rollback()

if __name__ == "__main__":
    apply_migration()