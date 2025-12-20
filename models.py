from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# This creates a circular import issue when defined in separate file
# So we define it here and import it in app.py
db = SQLAlchemy()

class BaseModel(db.Model):
    """Base model that provides common functionality for all models"""
    __abstract__ = True
    
    # Add created_at and updated_at fields to all models that inherit from this
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(BaseModel):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Relationships
    locations = db.relationship('Location', backref='user', lazy=True, cascade='all, delete-orphan')
    plants = db.relationship('Plant', backref='user', lazy=True, cascade='all, delete-orphan')
    settings = db.relationship('UserSetting', backref='user', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class Location(BaseModel):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    lighting = db.Column(db.String(100))
    substrate = db.Column(db.String(100))
    photo_filename = db.Column(db.String(255))  # Filename for photo stored in static/photo
    
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


class Plant(BaseModel):
    __tablename__ = 'plants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(100))
    planted_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    photo_filename = db.Column(db.String(255))  # Filename for photo stored in static/photo
    
    # Relationship
    timeline_events = db.relationship('TimelineEvent', backref='plant', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Plant {self.name}>'


class TimelineEvent(BaseModel):
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
    photo_filename = db.Column(db.String(255))  # Legacy field for single photo - will be deprecated

    # Relationship to GrowthPhase is already defined in GrowthPhase class
    photos = db.relationship('EventPhoto', backref='timeline_event', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TimelineEvent {self.title} on {self.event_date}>'


class EventPhoto(BaseModel):
    __tablename__ = 'event_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('timeline_events.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # Filename for photo stored in static/photos/events
    
    def __repr__(self):
        return f'<EventPhoto {self.filename} for event {self.event_id}>'


class UserSetting(BaseModel):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    preferred_units = db.Column(db.String(20), default='metric')  # metric/imperial
    notifications_enabled = db.Column(db.Boolean, default=True)
    timezone = db.Column(db.String(50), default='UTC')

    def __repr__(self):
        return f'<UserSetting for user {self.user_id}>'