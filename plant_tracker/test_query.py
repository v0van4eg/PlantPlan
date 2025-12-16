#!/usr/bin/env python3
"""
Test script to verify the exact query that was failing in the original error
"""

from app import create_app
from database import db
from models import TimelineEvent

def test_problematic_query():
    app = create_app()
    
    with app.app_context():
        try:
            # This is the exact query that was failing in the original error:
            # TimelineEvent.query.filter_by(plant_id=plant_id).order_by(TimelineEvent.event_date.desc()).all()
            plant_id = 1  # Using plant_id=1 as in the original error
            timeline_events = TimelineEvent.query.filter_by(plant_id=plant_id).order_by(TimelineEvent.event_date.desc()).all()
            
            print(f"Successfully retrieved {len(timeline_events)} timeline events for plant_id={plant_id}")
            
            for event in timeline_events:
                print(f"Event: {event.title} on {event.event_date}, photo_path: {event.photo_path}")
                
            print("SUCCESS: The problematic query now works correctly!")
            return True
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    test_problematic_query()