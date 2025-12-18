#!/usr/bin/env python3
"""
Скрипт для миграции старых путей к фото в новую структуру хранения
"""
import os
from models import db, Location, Plant, TimelineEvent
from app import create_app

def migrate_photo_paths():
    app = create_app()
    
    with app.app_context():
        # Миграция фото локаций
        print("Миграция фото локаций...")
        locations = Location.query.all()
        for location in locations:
            if location.photo_filename and not location.photo_filename.startswith('photos/'):
                # Старый формат пути, преобразуем в новый
                if os.path.exists(os.path.join('static', 'photo', location.photo_filename)):
                    # Переместить файл в новую структуру
                    old_path = os.path.join('static', 'photo', location.photo_filename)
                    new_path = os.path.join('static', 'photos', 'locations', location.photo_filename)
                    
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    
                    # Переименовать файл в новое место
                    os.rename(old_path, new_path)
                    
                    # Обновить путь в базе данных
                    location.photo_filename = f"photos/locations/{location.photo_filename}"
                    print(f"  Обновлен путь для локации {location.name}: {location.photo_filename}")
        
        # Миграция фото растений
        print("Миграция фото растений...")
        plants = Plant.query.all()
        for plant in plants:
            if plant.photo_filename and not plant.photo_filename.startswith('photos/'):
                # Старый формат пути, преобразуем в новый
                if os.path.exists(os.path.join('static', 'photo', plant.photo_filename)):
                    # Переместить файл в новую структуру
                    old_path = os.path.join('static', 'photo', plant.photo_filename)
                    new_path = os.path.join('static', 'photos', 'plants', plant.photo_filename)
                    
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    
                    # Переименовать файл в новое место
                    os.rename(old_path, new_path)
                    
                    # Обновить путь в базе данных
                    plant.photo_filename = f"photos/plants/{plant.photo_filename}"
                    print(f"  Обновлен путь для растения {plant.name}: {plant.photo_filename}")
        
        # Миграция фото событий
        print("Миграция фото событий...")
        events = TimelineEvent.query.all()
        for event in events:
            if event.photo_filename and not event.photo_filename.startswith('photos/'):
                # Старый формат пути, преобразуем в новый
                if os.path.exists(os.path.join('static', 'photo', event.photo_filename)):
                    # Переместить файл в новую структуру
                    old_path = os.path.join('static', 'photo', event.photo_filename)
                    new_path = os.path.join('static', 'photos', 'events', event.photo_filename)
                    
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    
                    # Переименовать файл в новое место
                    os.rename(old_path, new_path)
                    
                    # Обновить путь в базе данных
                    event.photo_filename = f"photos/events/{event.photo_filename}"
                    print(f"  Обновлен путь для события {event.title}: {event.photo_filename}")
        
        # Сохранить изменения в базе данных
        db.session.commit()
        print("Миграция завершена!")

if __name__ == "__main__":
    migrate_photo_paths()