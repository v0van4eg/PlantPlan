from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///plant_tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy()

# Import models after db initialization to avoid circular imports
from models import User, Location, Plant, GrowthPhase, TimelineEvent, UserSetting

# Initialize db with app
db.init_app(app)


@app.route('/')
def index():
    """Main dashboard page showing all plants for the current user"""
    # For now, we'll just show a simple template
    # In a real app, we would get the current logged-in user
    # and show their plants, locations, etc.
    return render_template('dashboard.html')


@app.route('/locations')
def locations():
    """Show all locations for the current user"""
    # In a real app, this would filter by current user
    locations = Location.query.all()
    return render_template('locations.html', locations=locations)


@app.route('/plants')
def plants():
    """Show all plants for the current user"""
    # In a real app, this would filter by current user
    plants = Plant.query.all()
    return render_template('plants.html', plants=plants)


@app.route('/plant/<int:plant_id>')
def plant_detail(plant_id):
    """Show details for a specific plant, including its timeline"""
    plant = Plant.query.get_or_404(plant_id)
    timeline_events = TimelineEvent.query.filter_by(plant_id=plant_id).order_by(TimelineEvent.event_date.desc()).all()
    
    return render_template('plant_detail.html', plant=plant, timeline_events=timeline_events)


@app.route('/add_plant', methods=['GET', 'POST'])
def add_plant():
    """Add a new plant"""
    if request.method == 'POST':
        name = request.form['name']
        species = request.form['species']
        location_id = request.form.get('location_id')
        planted_date_str = request.form.get('planted_date')
        
        planted_date = None
        if planted_date_str:
            planted_date = datetime.strptime(planted_date_str, '%Y-%m-%d').date()
        
        notes = request.form.get('notes', '')
        
        plant = Plant(
            name=name,
            species=species,
            location_id=location_id if location_id else None,
            planted_date=planted_date,
            notes=notes
        )
        
        db.session.add(plant)
        db.session.commit()
        
        flash(f'Plant {name} added successfully!', 'success')
        return redirect(url_for('plants'))
    
    locations = Location.query.all()
    return render_template('add_plant.html', locations=locations)


@app.route('/add_event/<int:plant_id>', methods=['POST'])
def add_event(plant_id):
    """Add a timeline event for a plant"""
    plant = Plant.query.get_or_404(plant_id)
    
    event_type = request.form['event_type']
    title = request.form['title']
    event_date_str = request.form['event_date']
    description = request.form.get('description', '')
    
    event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
    
    # Handle different event types
    if event_type == 'growth_phase':
        phase_id = request.form.get('phase_id')
        event = TimelineEvent(
            plant_id=plant_id,
            event_type=event_type,
            title=title,
            event_date=event_date,
            description=description,
            phase_id=phase_id
        )
    elif event_type == 'fertilization':
        fertilization_type = request.form.get('fertilization_type', '')
        fertilization_amount = request.form.get('fertilization_amount', '')
        event = TimelineEvent(
            plant_id=plant_id,
            event_type=event_type,
            title=title,
            event_date=event_date,
            description=description,
            fertilization_type=fertilization_type,
            fertilization_amount=fertilization_amount
        )
    else:
        event = TimelineEvent(
            plant_id=plant_id,
            event_type=event_type,
            title=title,
            event_date=event_date,
            description=description
        )
    
    db.session.add(event)
    db.session.commit()
    
    flash(f'Event added to {plant.name}\'s timeline!', 'success')
    return redirect(url_for('plant_detail', plant_id=plant_id))


@app.route('/api/timeline/<int:plant_id>')
def api_timeline(plant_id):
    """API endpoint to get timeline data for a plant in JSON format"""
    plant = Plant.query.get_or_404(plant_id)
    timeline_events = TimelineEvent.query.filter_by(plant_id=plant_id).order_by(TimelineEvent.event_date).all()
    
    events_data = []
    for event in timeline_events:
        event_data = {
            'id': event.id,
            'title': event.title,
            'date': event.event_date.isoformat(),
            'type': event.event_type,
            'description': event.description,
            'phase_name': event.growth_phase.name if event.growth_phase else None,
            'fertilization_type': event.fertilization_type,
            'fertilization_amount': event.fertilization_amount
        }
        events_data.append(event_data)
    
    return jsonify({
        'plant_name': plant.name,
        'events': events_data
    })


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)