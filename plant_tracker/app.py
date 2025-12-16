from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from database import db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///plant_tracker.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure upload settings
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Create upload directory if it doesn't exist
    os.makedirs(os.path.join(app.root_path, UPLOAD_FOLDER), exist_ok=True)
    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize db with app
    db.init_app(app)

    # Import models after db initialization to avoid circular imports
    from models import User, Location, Plant, GrowthPhase, TimelineEvent, UserSetting

    def allowed_file(filename):
        """Check if uploaded file has allowed extension"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/')
    def index():
        """Main page now shows plants by default"""
        # Redirect to plants page to show plants by default
        return redirect(url_for('plants'))

    @app.route('/locations')
    def locations():
        """Show all locations for the current user"""
        # In a real app, this would filter by current user
        locations = Location.query.all()
        return render_template('locations.html', locations=locations)

    @app.route('/add_location', methods=['POST'])
    def add_location():
        """Add a new location"""
        name = request.form['name']
        description = request.form.get('description', '')
        
        # In a real app, this would be associated with the current user
        # For now, we'll create it without a user association
        location = Location(
            name=name,
            description=description
        )
        
        db.session.add(location)
        db.session.commit()
        
        flash(f'Location {name} added successfully!', 'success')
        return redirect(url_for('locations'))

    @app.route('/plants')
    def plants():
        """Show all plants for the current user, optionally filtered by location"""
        # Get location filter from query parameters
        location_id = request.args.get('location', type=int)
        
        if location_id:
            # Filter plants by location
            plants = Plant.query.filter_by(location_id=location_id).all()
            # Get the location for display purposes
            location = Location.query.get_or_404(location_id)
            return render_template('plants.html', plants=plants, location=location)
        else:
            # Show all plants without location filter
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
            
            # Handle photo upload
            photo_path = None
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo and photo.filename != '':
                    if allowed_file(photo.filename):
                        filename = secure_filename(photo.filename)
                        # Create unique filename to avoid conflicts
                        base, ext = os.path.splitext(filename)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        unique_filename = f"{base}_{timestamp}{ext}"
                        
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                        photo.save(filepath)
                        photo_path = f"/{os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)}"
                    else:
                        flash('Недопустимый тип файла. Разрешены только JPG, PNG и GIF.', 'warning')
            
            plant = Plant(
                name=name,
                species=species,
                location_id=location_id if location_id else None,
                planted_date=planted_date,
                notes=notes,
                photo_path=photo_path
            )
            
            db.session.add(plant)
            db.session.commit()
            
            flash(f'Plant {name} added successfully!', 'success')
            return redirect(url_for('plants'))
        
        locations = Location.query.all()
        return render_template('add_plant.html', locations=locations)

    @app.route('/edit_plant/<int:plant_id>', methods=['GET', 'POST'])
    def edit_plant(plant_id):
        """Edit an existing plant"""
        plant = Plant.query.get_or_404(plant_id)
        
        if request.method == 'POST':
            plant.name = request.form['name']
            plant.species = request.form['species']
            plant.location_id = request.form.get('location_id') or None
            planted_date_str = request.form.get('planted_date')
            
            if planted_date_str:
                plant.planted_date = datetime.strptime(planted_date_str, '%Y-%m-%d').date()
            else:
                plant.planted_date = None
            
            plant.notes = request.form.get('notes', '')
            
            # Handle photo update
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo and photo.filename != '':
                    if allowed_file(photo.filename):
                        # Remove old photo if it exists
                        if plant.photo_path:
                            old_photo_path = os.path.join(app.root_path, plant.photo_path[1:])  # Remove leading slash
                            if os.path.exists(old_photo_path):
                                os.remove(old_photo_path)
                        
                        filename = secure_filename(photo.filename)
                        # Create unique filename to avoid conflicts
                        base, ext = os.path.splitext(filename)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        unique_filename = f"{base}_{timestamp}{ext}"
                        
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                        photo.save(filepath)
                        plant.photo_path = f"/{os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)}"
                    else:
                        flash('Недопустимый тип файла. Разрешены только JPG, PNG и GIF.', 'warning')
            
            db.session.commit()
            flash(f'Plant {plant.name} updated successfully!', 'success')
            return redirect(url_for('plant_detail', plant_id=plant.id))
        
        locations = Location.query.all()
        return render_template('add_plant.html', plant=plant, locations=locations)

    @app.route('/add_event/<int:plant_id>', methods=['POST'])
    def add_event(plant_id):
        """Add a timeline event for a plant"""
        plant = Plant.query.get_or_404(plant_id)
        
        event_type = request.form['event_type']
        description = request.form.get('description', '')
        event_date_str = request.form['event_date']
        
        # Generate a default title based on event type and date if no description provided
        if description.strip():
            title = description[:50] + "..." if len(description) > 50 else description
        else:
            title = f"{event_type.replace('_', ' ').title()} - {event_date_str}"
        
        event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        
        # Handle different event types
        if event_type == 'growth_phase':
            phase_id = request.form.get('phase_id')
            # Convert to integer if not empty, otherwise keep as None
            try:
                phase_id = int(phase_id) if phase_id and phase_id.strip() != '' else None
            except ValueError:
                # If conversion fails, set to None
                phase_id = None
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
            # Empty string values should remain as empty strings or None if needed
            fertilization_amount = fertilization_amount if fertilization_amount and fertilization_amount.strip() != '' else None
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

    @app.route('/update_plant_photo/<int:plant_id>', methods=['POST'])
    def update_plant_photo(plant_id):
        """Update plant photo"""
        plant = Plant.query.get_or_404(plant_id)
        
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename != '':
                if allowed_file(photo.filename):
                    # Remove old photo if it exists
                    if plant.photo_path:
                        old_photo_path = os.path.join(app.root_path, plant.photo_path[1:])  # Remove leading slash
                        if os.path.exists(old_photo_path):
                            os.remove(old_photo_path)
                    
                    filename = secure_filename(photo.filename)
                    # Create unique filename to avoid conflicts
                    base, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_filename = f"{base}_{timestamp}{ext}"
                    
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    photo.save(filepath)
                    plant.photo_path = f"/{os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)}"
                    
                    db.session.commit()
                    flash('Фото успешно обновлено!', 'success')
                else:
                    flash('Недопустимый тип файла. Разрешены только JPG, PNG и GIF.', 'warning')
        
        return redirect(url_for('plant_detail', plant_id=plant_id))

    @app.route('/api/growth_phases')
    def api_growth_phases():
        """API endpoint to get all growth phases"""
        phases = GrowthPhase.query.order_by(GrowthPhase.phase_order).all()
        phases_data = []
        for phase in phases:
            phases_data.append({
                'id': phase.id,
                'name': phase.name,
                'description': phase.description
            })
        return jsonify(phases_data)

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

    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)