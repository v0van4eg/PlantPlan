#!/usr/bin/env python3
"""
Script to generate sample data for the plant care application.
Creates 5 locations with random names and photos, and 5 plants per location with their own photos.
"""

import os
import sys
import random
import uuid
from datetime import datetime, timedelta

# Add the project root to Python path to import models
sys.path.append('/workspace')

from app import create_app, db
from models import User, Location, Plant


def create_sample_photos(directory, count, prefix):
    """Create dummy photo files in the specified directory."""
    os.makedirs(directory, exist_ok=True)

    photo_filenames = []
    for i in range(count):
        # Create a fake photo filename
        photo_filename = f"{prefix}_{uuid.uuid4().hex[:8]}.jpg"
        photo_path = os.path.join(directory, photo_filename)

        # Create a dummy file (empty file is fine for this purpose)
        with open(photo_path, 'w') as f:
            f.write(f"Dummy photo file for {prefix} {i+1}")

        photo_filenames.append(photo_filename)

    return photo_filenames


def main():
    print("Starting to generate sample data...")

    # Create Flask app and initialize database
    app = create_app()

    with app.app_context():
        # Get the default user from the database (as used in the app)
        user = User.query.filter_by(username='default').first()
        if not user:
            print("Default user not found. Creating a default user...")
            # Create the default user as used in the app
            user = User(
                username="default",
                email="default@example.com",
                password_hash="temp_password_hash"
            )
            db.session.add(user)
            db.session.flush()  # To get the ID without committing

        print(f"Using user: {user.username}")

        # Define some sample location names
        location_names = [
            "Городской сад", "Оранжерея", "Балкон", "Кухня", "Терраса",
            "Подоконник", "Патио", "Садовая беседка", "Зимний сад", "Огород",
            "Веранда", "Лоджия", "Палисадник", "Цветник", "Теплица"
        ]

        # Create photos directory if it doesn't exist
        photos_dir = os.path.join('static', 'photos')
        os.makedirs(photos_dir, exist_ok=True)

        # Randomly select 5 location names
        selected_location_names = random.sample(location_names, 5)

        print("Creating locations...")
        for i, loc_name in enumerate(selected_location_names):
            # Create a photo for the location
            location_photos_dir = os.path.join(photos_dir, "locations")
            location_photo_filenames = create_sample_photos(location_photos_dir, 1, f"location_{i+1}")

            # Create location
            location = Location(
                user_id=user.id,
                name=loc_name,
                description=f"Описание для локации {loc_name}",
                lighting=random.choice(["Солнечное", "Полутень", "Тень"]),
                substrate=random.choice(["Грунт", "Гидропоника", "Кокос", "Перлит"]),
                photo_filename=location_photo_filenames[0]
            )

            db.session.add(location)
            db.session.flush()  # To get the ID before committing

            print(f"Created location: {loc_name}")

            # Create 5 plants for this location
            plant_names = [
                "Роза", "Фикус", "Кактус", "Орхидея", "Сансевиерия",
                "Хлорофитум", "Алоэ", "Каланхоэ", "Монстера", "Папоротник",
                "Герань", "Фиалка", "Драцена", "Толстянка", "Эхмея",
                "Гибискус", "Плющ", "Мирт", "Лавр", "Рута"
            ]

            selected_plant_names = random.sample(plant_names, 5)

            for j, plant_name in enumerate(selected_plant_names):
                # Create a photo for the plant
                plant_photos_dir = os.path.join(photos_dir, "plants")
                plant_photo_filenames = create_sample_photos(plant_photos_dir, 1, f"plant_loc{i+1}_{j+1}")

                # Generate a random planting date in the last year
                days_ago = random.randint(1, 365)
                planted_date = datetime.now() - timedelta(days=days_ago)

                plant = Plant(
                    user_id=user.id,
                    location_id=location.id,
                    name=plant_name,
                    species=f"Вид {plant_name.lower()}",
                    planted_date=planted_date.date(),
                    notes=f"Заметки о растении {plant_name}",
                    photo_filename=plant_photo_filenames[0]
                )

                db.session.add(plant)
                print(f"  Created plant: {plant_name} in {loc_name}")

        # Commit all changes to the database
        db.session.commit()

        print("\nSample data generation completed successfully!")
        print(f"Created 5 locations with 5 plants each (total {5 * 5} plants)")

        # Print summary
        locations_count = Location.query.filter_by(user_id=user.id).count()
        plants_count = Plant.query.filter_by(user_id=user.id).count()

        print(f"\nSummary:")
        print(f"- Locations: {locations_count}")
        print(f"- Plants: {plants_count}")


if __name__ == "__main__":
    main()
