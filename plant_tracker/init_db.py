#!/usr/bin/env python3
"""
Database initialization script that creates tables
"""

import os
from models import db, GrowthPhase

def init_database():
    # Create all tables defined in models
    print("Creating all tables...")
    db.create_all()
    
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
    # When run directly, we need to create an app context
    from app import create_app
    app = create_app()
    with app.app_context():
        init_database()