#!/usr/bin/env python3
"""
Script to run database migrations using the same configuration as the main app
"""

import os
from app import create_app
from models import db, Location, TimelineEvent, UserSetting

def run_migration():
    # Set the DATABASE_URL environment variable - using localhost instead of 'db' hostname
    os.environ['DATABASE_URL'] = 'postgresql://plant_user:plant_password@localhost:5432/plant_tracker'
    
    # Create the Flask app
    app = create_app()
    
    with app.app_context():
        # Get the database URI from app config
        database_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Connecting to database: {database_uri}")
        
        # Execute raw SQL to add missing columns
        try:
            # Add updated_at to locations table
            db.session.execute(db.text("""
                ALTER TABLE locations ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            """))
            
            # Add updated_at to timeline_events table  
            db.session.execute(db.text("""
                ALTER TABLE timeline_events ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            """))
            
            # Add updated_at to user_settings table
            db.session.execute(db.text("""
                ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            """))
            
            # Commit the changes
            db.session.commit()
            
            print("Database migration completed successfully!")
            print("Added 'updated_at' column to locations, timeline_events, and user_settings tables.")
            
        except Exception as e:
            print(f"Error during migration: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    run_migration()