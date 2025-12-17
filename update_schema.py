from app import create_app
from models import db, Location
import os

# Создаем приложение
app = create_app()

# Проверим, какая база данных используется
with app.app_context():
    database_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"Используемая база данных: {database_uri}")
    
    # Для SQLite проверим наличие столбца photo_data
    if database_uri.startswith('sqlite'):
        import sqlite3
        db_path = database_uri.replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверим, существует ли столбец photo_data
        cursor.execute("PRAGMA table_info(locations);")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'photo_data' not in columns:
            print("Столбец photo_data отсутствует, добавляем его...")
            try:
                cursor.execute("ALTER TABLE locations ADD COLUMN photo_data BLOB;")
                conn.commit()
                print("Столбец photo_data успешно добавлен!")
            except sqlite3.OperationalError as e:
                print(f"Ошибка при добавлении столбца: {e}")
        else:
            print("Столбец photo_data уже существует")
        
        conn.close()
    else:
        # Для PostgreSQL используем SQLAlchemy
        try:
            # Проверим, существует ли столбец
            inspector = db.inspect()
            columns = [col['name'] for col in inspector.get_columns('locations')]
            
            if 'photo_data' not in columns:
                print("Столбец photo_data отсутствует, добавляем его...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE locations ADD COLUMN photo_data BYTEA;"))
                    conn.commit()
                print("Столбец photo_data успешно добавлен!")
            else:
                print("Столбец photo_data уже существует")
        except Exception as e:
            print(f"Ошибка при работе с PostgreSQL: {e}")

print("Обновление схемы завершено")