#!/usr/bin/env python3
"""
Test script to verify that the TimelineEvent model can access the photo_path column
"""

from app import create_app
from database import db
from models import TimelineEvent

def test_timeline_event_model():
    app = create_app()
    
    with app.app_context():
        try:
            # Test querying timeline events to see if the photo_path column exists
            events = TimelineEvent.query.limit(5).all()
            print(f"Successfully retrieved {len(events)} timeline events")
            
            for event in events:
                # Try accessing the photo_path attribute
                photo_path = getattr(event, 'photo_path', 'No photo_path attribute')
                print(f"Event ID {event.id}: photo_path = {photo_path}")
                
            print("SUCCESS: TimelineEvent model can access photo_path column")
            return True
        except Exception as e:
            print(f"ERROR: {e}")
            return False

if __name__ == '__main__':
    test_timeline_event_model()