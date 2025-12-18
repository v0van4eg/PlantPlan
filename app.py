import base64
import os
import sys
import time
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from init_db import init_database
from models import db


def save_photo(photo_file, folder):
    """Save uploaded photo to local folder and return file path"""
    if photo_file and photo_file.filename != '':
        # Generate unique filename to avoid conflicts
        ext = os.path.splitext(photo_file.filename)[1]
        unique_filename = str(uuid.uuid4()) + ext
        filepath = os.path.join('static/photos', folder, unique_filename)
        
        # Save the file
        photo_file.save(filepath)
        
        return filepath
    return None


def delete_photo(filepath):
    """Delete photo file from disk if it exists"""
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass  # Ignore errors if file doesn't exist or can't be deleted


def binary_to_data_url(binary_data, mime_type='image/jpeg'):
    """Convert binary image data to data URL for HTML display"""
    if binary_data:
        encoded = base64.b64encode(binary_data).decode('utf-8')
        return f"data:{mime_type};base64,{encoded}"
    return None


def wait_for_db(app):
    """Wait for the database to be ready"""
    database_url = app.config['SQLALCHEMY_DATABASE_URI']

    # Only wait for DB if using PostgreSQL
    if database_url.startswith('postgresql'):
        print("Waiting for database...")
        for attempt in range(30):  # Try for up to 30 seconds
            try:
                engine = create_engine(database_url)
                with engine.connect() as conn:
                    print("Database connection established!")
                    break
            except OperationalError as e:
                print(f"Attempt {attempt + 1}: Could not connect to database: {e}")
                time.sleep(1)
        else:
            print("Could not connect to database after 30 attempts. Exiting.")
            sys.exit(1)


def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL',
                                                           'postgresql://postgres:password@db:5432/plant_tracker')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Настройки загрузки файлов определены в функции allowed_file()

    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    # Инициализация базы данных приложением
    db.init_app(app)

    # Импорт моделей после инициализации БД для предотвращения циклических импортов
    from models import User, Location, Plant, GrowthPhase, TimelineEvent

    # Добавление функции binary_to_data_url в окружение Jinja2 для использования в шаблонах
    app.jinja_env.globals['binary_to_data_url'] = binary_to_data_url
    
    # Add helper function to convert photo path to URL
    app.jinja_env.globals['get_photo_url'] = lambda photo_path: url_for('static', filename=photo_path) if photo_path else None
    
    # Add helper function to convert multiple photo paths to URLs
    def get_multiple_photo_urls(photo_paths_str):
        if photo_paths_str:
            paths = photo_paths_str.split(',')
            return [url_for('static', filename=path) for path in paths if path.strip()]
        return []
    
    app.jinja_env.globals['get_multiple_photo_urls'] = get_multiple_photo_urls

    @app.route('/')
    def index():
        """Главная страница теперь по умолчанию показывает растения"""
        # Перенаправление на страницу растений для отображения растений по умолчанию
        return redirect(url_for('plants'))

    @app.route('/locations')
    def locations():
        """Показать все локации для текущего пользователя"""
        # Для разработки показываем локации для пользователя по умолчанию
        default_user = User.query.filter_by(username='default').first()
        if default_user:
            locations = Location.query.filter_by(user_id=default_user.id).all()
        else:
            locations = []
        return render_template('locations.html', locations=locations)

    @app.route('/location/<int:location_id>')
    def location_detail(location_id):
        """Показать детали для конкретной локации"""
        location = Location.query.get_or_404(location_id)
        plants = Plant.query.filter_by(location_id=location_id).all()
        return render_template('location_detail.html', location=location, plants=plants)

    @app.route('/add_location', methods=['POST'])
    def add_location():
        """Добавить новую локацию - устаревший метод, теперь обрабатывается в edit_location"""
        # Этот маршрут устарел, так как мы используем маршрут edit_location с location_id=0
        # для добавления новых локаций
        name = request.form['name']
        description = request.form.get('description', '')
        lighting = request.form.get('lighting', '')
        substrate = request.form.get('substrate', '')

        # Обработка загрузки фото
        photo_path = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename != '':
                if allowed_file(photo.filename):
                    photo_path = save_photo(photo, 'locations')
                else:
                    flash('Недопустимый тип файла. Разрешены только JPG, PNG, GIF, WEBP.', 'warning')

        # Получение или создание пользователя по умолчанию для целей разработки
        default_user = User.query.filter_by(username='default').first()
        if not default_user:
            default_user = User(
                username='default',
                email='default@example.com',
                password_hash='temp_password_hash'
            )
            db.session.add(default_user)
            db.session.flush()  # Получение ID пользователя без фиксации

        location = Location(
            user_id=default_user.id,
            name=name,
            description=description,
            lighting=lighting if lighting else None,
            substrate=substrate if substrate else None,
            photo_path=photo_path
        )

        db.session.add(location)
        db.session.commit()

        flash(f'Location {name} added successfully!', 'success')
        return redirect(url_for('locations'))

    @app.route('/edit_location/<int:location_id>', methods=['GET', 'POST'])
    def edit_location(location_id):
        """Редактировать существующую локацию или создать новую, если location_id равен 0"""
        if location_id == 0:
            # Создание новой локации
            location = None
            if request.method == 'POST':
                name = request.form['name']
                description = request.form.get('description', '')
                lighting = request.form.get('lighting', '') or None
                substrate = request.form.get('substrate', '') or None

                # Обработка загрузки фото - чтение бинарных данных
                photo_path = None
                if 'photo' in request.files:
                    photo = request.files['photo']
                    if photo and photo.filename != '':
                        if allowed_file(photo.filename):
                            photo_path = save_photo(photo, 'locations')
                        else:
                            flash('Недопустимый тип файла. Разрешены только JPG, PNG, GIF, WEBP.', 'warning')

                # Получение или создание пользователя по умолчанию для целей разработки
                default_user = User.query.filter_by(username='default').first()
                if not default_user:
                    default_user = User(
                        username='default',
                        email='default@example.com',
                        password_hash='temp_password_hash'
                    )
                    db.session.add(default_user)
                    db.session.flush()  # Получение ID пользователя без фиксации

                new_location = Location(
                    user_id=default_user.id,
                    name=name,
                    description=description,
                    lighting=lighting,
                    substrate=substrate,
                    photo_path=photo_path
                )

                db.session.add(new_location)
                db.session.commit()

                flash(f'Location {name} added successfully!', 'success')
                return redirect(url_for('locations'))

            return render_template('edit_location.html', location=location)
        else:
            # Редактирование существующей локации
            location = Location.query.get_or_404(location_id)

            if request.method == 'POST':
                location.name = request.form['name']
                location.description = request.form.get('description', '')
                location.lighting = request.form.get('lighting', '') or None
                location.substrate = request.form.get('substrate', '') or None

                # Обработка обновления фото
                if 'photo' in request.files:
                    photo = request.files['photo']
                    if photo and photo.filename != '':
                        if allowed_file(photo.filename):
                            # Delete old photo if exists
                            if location.photo_path:
                                delete_photo(location.photo_path)
                            # Save new photo
                            location.photo_path = save_photo(photo, 'locations')
                        else:
                            flash('Недопустимый тип файла. Разрешены только JPG, PNG и GIF.', 'warning')

                db.session.commit()
                flash(f'Location {location.name} updated successfully!', 'success')
                return redirect(url_for('location_detail', location_id=location.id))

            return render_template('edit_location.html', location=location)

    @app.route('/plants')
    def plants():
        """Показать все растения для текущего пользователя, опционально отфильтрованные по локации"""
        # Получение фильтра локации из параметров запроса
        location_id = request.args.get('location', type=int)

        if location_id:
            # Фильтрация растений по локации (убедиться, что она принадлежит пользователю по умолчанию)
            default_user = User.query.filter_by(username='default').first()
            if default_user:
                plants = Plant.query.filter_by(location_id=location_id, user_id=default_user.id).all()
            else:
                plants = []
            # Получение локации для отображения
            location = Location.query.get_or_404(location_id)
            return render_template('plants.html', plants=plants, location=location)
        else:
            # Показать все растения для пользователя по умолчанию без фильтрации по локации
            default_user = User.query.filter_by(username='default').first()
            if default_user:
                plants = Plant.query.filter_by(user_id=default_user.id).all()
            else:
                plants = []
            return render_template('plants.html', plants=plants)

    @app.route('/plant/<int:plant_id>')
    def plant_detail(plant_id):
        """Показать детали для конкретного растения, включая его хронологию"""
        from datetime import date

        plant = Plant.query.get_or_404(plant_id)
        timeline_events = TimelineEvent.query.filter_by(plant_id=plant_id).order_by(
            TimelineEvent.event_date.desc()).all()

        # Получение событий этапов роста и расчет продолжительности
        growth_phase_events = TimelineEvent.query.filter_by(
            plant_id=plant_id,
            event_type='growth_phase'
        ).order_by(TimelineEvent.event_date.asc()).all()

        growth_timeline = []
        for i, event in enumerate(growth_phase_events):
            start_date = event.event_date
            # Нахождение следующего события этапа роста для расчета продолжительности
            if i < len(growth_phase_events) - 1:
                end_date = growth_phase_events[i + 1].event_date
                duration = (end_date - start_date).days
            else:
                # Если это последний этап роста, расчет продолжительности до сегодняшнего дня
                end_date = date.today()
                duration = (end_date - start_date).days

            growth_timeline.append({
                'event': event,
                'start_date': start_date,
                'end_date': end_date,
                'duration_days': duration
            })

        return render_template('plant_detail.html',
                               plant=plant,
                               timeline_events=timeline_events,
                               growth_timeline=growth_timeline)

    @app.route('/add_plant', methods=['GET', 'POST'])
    def add_plant():
        """Добавить новое растение"""
        if request.method == 'POST':
            name = request.form['name']
            species = request.form['species']
            location_id = request.form.get('location_id')
            planted_date_str = request.form.get('planted_date')

            planted_date = None
            if planted_date_str:
                planted_date = datetime.strptime(planted_date_str, '%Y-%m-%d').date()

            notes = request.form.get('notes', '')

            # Обработка загрузки фото - чтение бинарных данных
            photo_path = None
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo and photo.filename != '':
                    if allowed_file(photo.filename):
                        photo_path = save_photo(photo, 'plants')
                    else:
                        flash('Недопустимый тип файла. Разрешены только JPG, PNG, GIF, WEBP.', 'warning')

            # Получение или создание пользователя по умолчанию для целей разработки
            default_user = User.query.filter_by(username='default').first()
            if not default_user:
                default_user = User(
                    username='default',
                    email='default@example.com',
                    password_hash='temp_password_hash'
                )
                db.session.add(default_user)
                db.session.flush()  # Получение ID пользователя без фиксации

            plant = Plant(
                user_id=default_user.id,
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
        """Редактировать существующее растение"""
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

            # Обработка обновления фото
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo and photo.filename != '':
                    if allowed_file(photo.filename):
                        # Delete old photo if exists
                        if plant.photo_path:
                            delete_photo(plant.photo_path)
                        # Save new photo
                        plant.photo_path = save_photo(photo, 'plants')
                    else:
                        flash('Недопустимый тип файла. Разрешены только JPG, PNG и GIF.', 'warning')

            db.session.commit()
            flash(f'Plant {plant.name} updated successfully!', 'success')
            return redirect(url_for('plant_detail', plant_id=plant.id))

        locations = Location.query.all()
        return render_template('add_plant.html', plant=plant, locations=locations)

    @app.route('/add_event/<int:plant_id>', methods=['POST'])
    def add_event(plant_id):
        """Добавить событие в хронологию растения"""
        plant = Plant.query.get_or_404(plant_id)

        event_type = request.form['event_type']
        description = request.form.get('description', '')
        event_date_str = request.form['event_date']

        # Генерация заголовка по умолчанию на основе типа события и даты, если описание не предоставлено
        if description.strip():
            title = description[:50] + "..." if len(description) > 50 else description
        else:
            title = f"{event_type.replace('_', ' ').title()} - {event_date_str}"

        event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()

        # Обработка загрузки фото для заметок - чтение бинарных данных
        photo_paths = []
        if 'note_photo' in request.files:
            photos = request.files.getlist('note_photo')  # Get multiple photos
            for photo in photos:
                if photo and photo.filename != '':
                    if allowed_file(photo.filename):
                        photo_path = save_photo(photo, 'events')
                        if photo_path:
                            photo_paths.append(photo_path)
                    else:
                        flash('Недопустимый тип файла. Разрешены только JPG, PNG и GIF.', 'warning')
        
        # Convert list of photo paths to comma-separated string
        photo_paths_str = ','.join(photo_paths) if photo_paths else None

        # Обработка различных типов событий
        if event_type == 'growth_phase':
            phase_id = request.form.get('phase_id')
            # Преобразование в целое число, если не пустое, иначе оставить как None
            try:
                phase_id = int(phase_id) if phase_id and phase_id.strip() != '' else None
            except ValueError:
                # Если преобразование не удается, установить как None
                phase_id = None
            event = TimelineEvent(
                plant_id=plant_id,
                event_type=event_type,
                title=title,
                event_date=event_date,
                description=description,
                phase_id=phase_id,
                photo_paths=photo_paths_str
            )
        elif event_type == 'fertilization':
            fertilization_type = request.form.get('fertilization_type', '')
            fertilization_amount = request.form.get('fertilization_amount', '')
            # Пустые строковые значения должны оставаться как пустые строки или None, если нужно
            fertilization_amount = fertilization_amount if fertilization_amount and fertilization_amount.strip() != '' else None
            event = TimelineEvent(
                plant_id=plant_id,
                event_type=event_type,
                title=title,
                event_date=event_date,
                description=description,
                fertilization_type=fertilization_type,
                fertilization_amount=fertilization_amount,
                photo_paths=photo_paths_str
            )
        else:
            event = TimelineEvent(
                plant_id=plant_id,
                event_type=event_type,
                title=title,
                event_date=event_date,
                description=description,
                photo_paths=photo_paths_str
            )

        db.session.add(event)
        db.session.commit()

        flash(f'Event added to {plant.name}\'s timeline!', 'success')
        return redirect(url_for('plant_detail', plant_id=plant_id))

    @app.route('/update_plant_photo/<int:plant_id>', methods=['POST'])
    def update_plant_photo(plant_id):
        """Обновить фото растения"""
        plant = Plant.query.get_or_404(plant_id)

        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename != '':
                if allowed_file(photo.filename):
                    # Delete old photo if exists
                    if plant.photo_path:
                        delete_photo(plant.photo_path)
                    # Save new photo
                    plant.photo_path = save_photo(photo, 'plants')

                    db.session.commit()
                    flash('Фото успешно обновлено!', 'success')
                else:
                    flash('Недопустимый тип файла. Разрешены только JPG, PNG и GIF.', 'warning')

        return redirect(url_for('plant_detail', plant_id=plant_id))

    @app.route('/delete_plant_photo/<int:plant_id>', methods=['GET'])
    def delete_plant_photo(plant_id):
        """Удалить фото растения"""
        plant = Plant.query.get_or_404(plant_id)

        if plant.photo_path:
            # Delete photo file from disk
            delete_photo(plant.photo_path)
            # Clear the photo path in database
            plant.photo_path = None
            db.session.commit()
            flash('Фото успешно удалено!', 'success')

        return redirect(url_for('plant_detail', plant_id=plant_id))

    @app.route('/update_location_photo/<int:location_id>', methods=['POST'])
    def update_location_photo(location_id):
        """Обновить фото локации"""
        location = Location.query.get_or_404(location_id)

        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename != '':
                if allowed_file(photo.filename):
                    # Delete old photo if exists
                    if location.photo_path:
                        delete_photo(location.photo_path)
                    # Save new photo
                    location.photo_path = save_photo(photo, 'locations')

                    db.session.commit()
                    flash('Фото успешно обновлено!', 'success')
                else:
                    flash('Недопустимый тип файла. Разрешены только JPG, PNG и GIF.', 'warning')

        return redirect(url_for('location_detail', location_id=location_id))

    @app.route('/delete_location_photo/<int:location_id>', methods=['GET'])
    def delete_location_photo(location_id):
        """Удалить фото локации"""
        location = Location.query.get_or_404(location_id)

        if location.photo_path:
            # Delete photo file from disk
            delete_photo(location.photo_path)
            # Clear the photo path in database
            location.photo_path = None
            db.session.commit()
            flash('Фото успешно удалено!', 'success')

        return redirect(url_for('location_detail', location_id=location_id))

    @app.route('/delete_plant/<int:plant_id>', methods=['POST'])
    def delete_plant(plant_id):
        """Удалить растение"""
        plant = Plant.query.get_or_404(plant_id)
        plant_name = plant.name
        db.session.delete(plant)
        db.session.commit()
        flash(f'Растение \"{plant_name}\" успешно удалено!', 'success')
        return redirect(url_for('plants'))

    @app.route('/delete_location/<int:location_id>', methods=['POST'])
    def delete_location(location_id):
        """Удалить локацию"""
        location = Location.query.get_or_404(location_id)
        location_name = location.name
        # Сначала переместить все растения в этой локации в "Без локации"
        plants_in_location = Plant.query.filter_by(location_id=location_id).all()
        for plant in plants_in_location:
            plant.location_id = None
        db.session.delete(location)
        db.session.commit()
        flash(f'Локация \"{location_name}\" успешно удалена!', 'success')
        return redirect(url_for('locations'))

    @app.route('/api/growth_phases')
    def api_growth_phases():
        """API endpoint для получения всех этапов роста"""
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
        """API endpoint для получения данных хронологии растения в формате JSON"""
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
                'fertilization_amount': event.fertilization_amount,
                'photo_path': event.photo_path
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


# Создание экземпляра приложения
app = create_app()

if __name__ == '__main__':
    # Ожидание готовности базы данных
    wait_for_db(app)
    # Инициализация таблиц базы данных
    with app.app_context():
        init_database()
    # Запуск приложения
    app.run(debug=False, host='0.0.0.0', port=5000)
