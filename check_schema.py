import sqlite3
from app import create_app

# Создаем приложение
app = create_app()

# Получаем путь к базе данных из конфигурации приложения
with app.app_context():
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Проверяем структуру таблицы locations
    cursor.execute("PRAGMA table_info(locations);")
    columns = cursor.fetchall()
    
    print("Структура таблицы locations:")
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}, Default: {col[4]}, Primary Key: {bool(col[5])}")
    
    conn.close()