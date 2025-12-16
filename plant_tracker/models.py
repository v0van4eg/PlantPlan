from datetime import datetime
from database import db


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
    photo_path = db.Column(db.String(255))  # Path to stored photo
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
    photo_path = db.Column(db.String(255))  # Path to stored photo for events
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to GrowthPhase is already defined in GrowthPhase class

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