#!/usr/bin/env python3
"""
Script to recreate the database with the correct schema
"""

import os
import sys
from sqlalchemy import create_engine, text
from app import create_app
from models import db

def recreate_database():
    """Drop and recreate all tables with the correct schema"""
    app = create_app()
    
    with app.app_context():
        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        
        # Create all tables with new schema
        print("Creating all tables with new schema...")
        db.create_all()
        
        print("Database recreated with correct schema!")

if __name__ == "__main__":
    recreate_database()