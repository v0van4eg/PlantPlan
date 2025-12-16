#!/usr/bin/env python3
"""
Test script to connect to the database
"""

import psycopg2
from psycopg2 import sql

try:
    # Try to connect to the database
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="plant_tracker",
        user="plant_user",
        password="plant_password"
    )
    
    print("Connected to database successfully!")
    
    # Create a cursor
    cur = conn.cursor()
    
    # Test query to see if the locations table exists
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'locations';")
    columns = cur.fetchall()
    print("\nColumns in 'locations' table:")
    for col in columns:
        print(f"  {col[0]}: {col[1]}")
    
    # Check if updated_at column exists in locations
    updated_at_exists = any(col[0] == 'updated_at' for col in columns)
    print(f"\nDoes 'updated_at' exist in locations table? {updated_at_exists}")
    
    # Close cursor and connection
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error connecting to database: {str(e)}")
    print("This suggests that the PostgreSQL database is not accessible on localhost:5432")
    print("The database is probably running inside a Docker container.")