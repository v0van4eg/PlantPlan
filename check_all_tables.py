import sqlite3
from app import create_app

# Создаем приложение
app = create_app()

with app.app_context():
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Проверяем список всех таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Таблицы в базе данных:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Если таблица locations существует, проверяем её структуру
    if ('locations',) in tables:
        print("\nСтруктура таблицы locations:")
        cursor.execute("PRAGMA table_info(locations);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}, Default: {col[4]}, Primary Key: {bool(col[5])}")
    else:
        print("\nТаблица locations не найдена!")
    
    conn.close()