#!/usr/bin/env python3
"""
Database initialization script that handles schema updates for existing tables
"""

import os
import sys
from sqlalchemy import create_engine, text
from app import create_app
from models import db, User, Location, Plant, GrowthPhase, TimelineEvent, UserSetting

def init_db_with_migrations():
    """Initialize database with proper schema updates"""
    app = create_app()
    
    with app.app_context():
        # Get database URI
        database_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Initializing database: {database_uri}")
        
        # Create tables that don't exist
        db.create_all()
        
        # Now handle schema updates for existing tables
        engine = db.get_engine(app)
        
        # Check and add missing columns to existing tables
        with engine.connect() as conn:
            # Add updated_at to locations table if it doesn't exist
            try:
                result = conn.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'locations' AND column_name = 'updated_at'
                        ) THEN
                            ALTER TABLE locations ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                            RAISE NOTICE 'Added updated_at column to locations table';
                        END IF;
                    END $$;
                """))
                print("Updated locations table schema if needed")
            except Exception as e:
                print(f"Error updating locations table: {e}")
            
            # Add updated_at to timeline_events table if it doesn't exist
            try:
                result = conn.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'timeline_events' AND column_name = 'updated_at'
                        ) THEN
                            ALTER TABLE timeline_events ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                            RAISE NOTICE 'Added updated_at column to timeline_events table';
                        END IF;
                    END $$;
                """))
                print("Updated timeline_events table schema if needed")
            except Exception as e:
                print(f"Error updating timeline_events table: {e}")
            
            # Add updated_at to user_settings table if it doesn't exist
            try:
                result = conn.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'user_settings' AND column_name = 'updated_at'
                        ) THEN
                            ALTER TABLE user_settings ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                            RAISE NOTICE 'Added updated_at column to user_settings table';
                        END IF;
                    END $$;
                """))
                print("Updated user_settings table schema if needed")
            except Exception as e:
                print(f"Error updating user_settings table: {e}")
            
            # Commit the transaction
            conn.commit()
        
        # Add default growth phases if they don't exist
        existing_count = GrowthPhase.query.count()
        if existing_count == 0:
            # Add default growth phases - using the same names as in the SQL schema
            phases_data = [
                {'name': 'Прорастание', 'description': 'Seed germinating', 'phase_order': 1},
                {'name': 'Вегетация', 'description': 'Growth period with leaves and stems', 'phase_order': 2},
                {'name': 'Цветение', 'description': 'Flowers beginning to form', 'phase_order': 3},
                {'name': 'Плодоношение', 'description': 'Fruits developing', 'phase_order': 4},
                {'name': 'Сбор урожая', 'description': 'Ready for harvest', 'phase_order': 5},
            ]
            
            for phase_data in phases_data:
                phase = GrowthPhase(**phase_data)
                db.session.add(phase)
            
            db.session.commit()
            print("Added default growth phases to database")
        else:
            print("Growth phases already exist in database")
        
        print("Database initialization completed successfully!")

if __name__ == "__main__":
    init_db_with_migrations()