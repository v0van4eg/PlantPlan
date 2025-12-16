from app import create_app
from database import db
from models import User, Location, Plant, GrowthPhase, TimelineEvent
from datetime import datetime, timedelta
import hashlib

app = create_app()

with app.app_context():
    # Check if sample data already exists
    if User.query.filter_by(username='sample_user').first() is None:
        # Create a sample user
        sample_user = User(
            username='sample_user',
            email='sample@example.com',
            password_hash=hashlib.sha256('password123'.encode()).hexdigest()
        )
        db.session.add(sample_user)
        db.session.commit()
        print("Created sample user.")
    else:
        sample_user = User.query.filter_by(username='sample_user').first()
        print("Sample user already exists.")

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
    else:
        print("Sample locations already exist.")

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
    else:
        print("Sample plants already exist.")

    # Check if sample timeline events exist
    if TimelineEvent.query.count() == 0:
        # Get the plants
        plants = Plant.query.filter_by(user_id=sample_user.id).all()
        
        if plants:
            # Add growth phases if not exist
            if GrowthPhase.query.count() == 0:
                # Add standard growth phases
                phases = [
                    {'name': 'Прорастание', 'description': 'Seed germinating', 'phase_order': 1},
                    {'name': 'Вегетация', 'description': 'Growth period with leaves and stems', 'phase_order': 2},
                    {'name': 'Цветение', 'description': 'Flowers beginning to form', 'phase_order': 3},
                    {'name': 'Плодоношение', 'description': 'Fruits developing', 'phase_order': 4},
                    {'name': 'Сбор урожая', 'description': 'Ready for harvest', 'phase_order': 5}
                ]
                
                for phase_data in phases:
                    phase = GrowthPhase(**phase_data)
                    db.session.add(phase)
                
                db.session.commit()
                print("Added growth phases to the database.")
            
            # Add sample timeline events for the first plant
            plant = plants[0]
            
            # Add growth phase event
            germination_phase = GrowthPhase.query.filter_by(name='Прорастание').first()
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
    else:
        print("Sample timeline events already exist.")

    print("Sample data initialization completed!")