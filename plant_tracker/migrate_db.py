#!/usr/bin/env python3
"""
Migration script to add missing updated_at columns to the database tables
"""

import os
from sqlalchemy import create_engine, text

def migrate_database():
    # Get database URL from environment variable or use default
    database_url = os.environ.get('DATABASE_URL', 'postgresql://plant_user:plant_password@db:5432/plant_tracker')
    
    # For Docker setup, the default URL might be different
    if database_url.startswith('sqlite'):
        print("Using SQLite database, no migration needed")
        return
    
    engine = create_engine(database_url)
    
    # SQL statements to add missing updated_at columns
    migration_statements = [
        # Add updated_at to locations table
        """ALTER TABLE locations ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;""",
        
        # Add updated_at to timeline_events table  
        """ALTER TABLE timeline_events ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;""",
        
        # Add updated_at to user_settings table
        """ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;""",
        
        # Add updated_at to users table (already has it according to schema but adding for safety)
        """ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;""",
        
        # Add updated_at to plants table (already has it according to schema but adding for safety)
        """ALTER TABLE plants ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"""
    ]
    
    try:
        with engine.connect() as conn:
            for statement in migration_statements:
                print(f"Executing: {statement}")
                conn.execute(text(statement))
            
            # Commit the transaction
            conn.commit()
            
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        raise

if __name__ == "__main__":
    migrate_database()