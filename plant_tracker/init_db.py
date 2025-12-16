#!/usr/bin/env python3
"""
Script to initialize the database with tables and sample data
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import hashlib

# Create Flask app instance and configure it
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plant_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db = SQLAlchemy(app)

# Define models inside this script to avoid circular imports
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    locations = db.relationship('Location', backref='user', lazy=True, cascade='all, delete-orphan')
    plants = db.relationship('Plant', backref='user', lazy=True, cascade='all, delete-orphan')
    settings = db.relationship('UserSetting', backref='user', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    plants = db.relationship('Plant', backref='location', lazy=True)

    def __repr__(self):
        return f'<Location {self.name}>'


class GrowthPhase(db.Model):
    __tablename__ = 'growth_phases'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    phase_order = db.Column(db.Integer, default=0, nullable=False)
    
    # Relationship
    timeline_events = db.relationship('TimelineEvent', backref='growth_phase', lazy=True)

    def __repr__(self):
        return f'<GrowthPhase {self.name}>'


class Plant(db.Model):
    __tablename__ = 'plants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(100))
    planted_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    timeline_events = db.relationship('TimelineEvent', backref='plant', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Plant {self.name}>'


class TimelineEvent(db.Model):
    __tablename__ = 'timeline_events'
    
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id', ondelete='CASCADE'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # 'growth_phase', 'fertilization', 'note', 'watering', etc.
    event_date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    phase_id = db.Column(db.Integer, db.ForeignKey('growth_phases.id'), nullable=True)  # for growth phase events
    fertilization_type = db.Column(db.String(100))  # for fertilization events
    fertilization_amount = db.Column(db.String(50))  # quantity of fertilizer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TimelineEvent {self.title} on {self.event_date}>'


class UserSetting(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    preferred_units = db.Column(db.String(20), default='metric')  # metric/imperial
    notifications_enabled = db.Column(db.Boolean, default=True)
    timezone = db.Column(db.String(50), default='UTC')

    def __repr__(self):
        return f'<UserSetting for user {self.user_id}>'


def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if growth phases already exist
        if GrowthPhase.query.count() == 0:
            # Add standard growth phases
            phases = [
                {'name': 'Seed', 'description': 'Initial seed stage', 'phase_order': 1},
                {'name': 'Germination', 'description': 'Seed germinating', 'phase_order': 2},
                {'name': 'Seedling', 'description': 'Young plant with initial leaves', 'phase_order': 3},
                {'name': 'Vegetative', 'description': 'Growth period with leaves and stems', 'phase_order': 4},
                {'name': 'Flowering', 'description': 'Flowers beginning to form', 'phase_order': 5},
                {'name': 'Fruiting', 'description': 'Fruits developing', 'phase_order': 6},
                {'name': 'Harvest', 'description': 'Ready for harvest', 'phase_order': 7}
            ]
            
            for phase_data in phases:
                phase = GrowthPhase(**phase_data)
                db.session.add(phase)
            
            db.session.commit()
            print("Added growth phases to the database.")
        
        # Check if sample user exists
        sample_user = User.query.filter_by(username='sample_user').first()
        if not sample_user:
            # Create a sample user
            sample_user = User(
                username='sample_user',
                email='sample@example.com',
                password_hash=hashlib.sha256('password123'.encode()).hexdigest()
            )
            db.session.add(sample_user)
            db.session.commit()
            print("Created sample user.")
        
        # Check if sample locations exist for the user
        if Location.query.filter_by(user_id=sample_user.id).count() == 0:
            # Create sample locations
            locations = [
                {'name': 'Living Room', 'description': 'Indoor plants near the window'},
                {'name': 'Kitchen Window', 'description': 'Herbs and small plants'},
                {'name': 'Balcony', 'description': 'Outdoor container garden'},
                {'name': 'Greenhouse', 'description': 'Protected growing area'}
            ]
            
            for loc_data in locations:
                location = Location(user_id=sample_user.id, **loc_data)
                db.session.add(location)
            
            db.session.commit()
            print("Added sample locations.")
        
        # Check if sample plants exist for the user
        if Plant.query.filter_by(user_id=sample_user.id).count() == 0:
            # Get locations for the sample user
            locations = Location.query.filter_by(user_id=sample_user.id).all()
            
            # Create sample plants
            plants = [
                {
                    'name': 'Tommy the Tomato',
                    'species': 'Solanum lycopersicum',
                    'location_id': locations[2].id if len(locations) > 2 else None,
                    'planted_date': datetime.now().date() - timedelta(days=30),
                    'notes': 'Cherry tomato plant, needs regular watering and support.'
                },
                {
                    'name': 'Minty',
                    'species': 'Mentha spicata',
                    'location_id': locations[1].id if len(locations) > 1 else None,
                    'planted_date': datetime.now().date() - timedelta(days=60),
                    'notes': 'Spearmint plant, grows very quickly, keep in check.'
                },
                {
                    'name': 'Fernando',
                    'species': 'Nephrolepis exaltata',
                    'location_id': locations[0].id if len(locations) > 0 else None,
                    'planted_date': datetime.now().date() - timedelta(days=90),
                    'notes': 'Boston fern, likes humidity and indirect light.'
                }
            ]
            
            for plant_data in plants:
                plant = Plant(user_id=sample_user.id, **plant_data)
                db.session.add(plant)
            
            db.session.commit()
            print("Added sample plants.")
        
        # Check if sample timeline events exist
        if TimelineEvent.query.count() == 0:
            # Get the plants
            plants = Plant.query.filter_by(user_id=sample_user.id).all()
            
            if plants:
                # Add sample timeline events for the first plant
                plant = plants[0]
                
                # Add growth phase event
                germination_phase = GrowthPhase.query.filter_by(name='Germination').first()
                event1 = TimelineEvent(
                    plant_id=plant.id,
                    event_type='growth_phase',
                    title='First sprout appeared',
                    event_date=datetime.now().date() - timedelta(days=25),
                    description='Small green shoot emerged from soil',
                    phase_id=germination_phase.id
                )
                
                # Add fertilization event
                event2 = TimelineEvent(
                    plant_id=plant.id,
                    event_type='fertilization',
                    title='Applied liquid fertilizer',
                    event_date=datetime.now().date() - timedelta(days=10),
                    description='Used balanced 10-10-10 fertilizer diluted to half strength',
                    fertilization_type='Liquid fertilizer',
                    fertilization_amount='10ml per liter water'
                )
                
                # Add note event
                event3 = TimelineEvent(
                    plant_id=plant.id,
                    event_type='note',
                    title='Started flowering',
                    event_date=datetime.now().date() - timedelta(days=5),
                    description='First flower buds appeared, excited to see tomatoes soon!'
                )
                
                db.session.add_all([event1, event2, event3])
                db.session.commit()
                print("Added sample timeline events.")
        
        print("Database initialization completed!")

if __name__ == '__main__':
    init_database()