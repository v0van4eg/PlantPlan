import sqlite3

# Проверим основной файл базы данных
print("=== Проверка основного файла базы данных (/workspace/plant_tracker.db) ===")
try:
    conn = sqlite3.connect('/workspace/plant_tracker.db')
    cursor = conn.cursor()
    
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
except Exception as e:
    print(f"Ошибка при доступе к основной базе данных: {e}")

print("\n=== Проверка файла базы данных в instance (/workspace/instance/plant_tracker.db) ===")
try:
    conn = sqlite3.connect('/workspace/instance/plant_tracker.db')
    cursor = conn.cursor()
    
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
except Exception as e:
    print(f"Ошибка при доступе к базе данных instance: {e}")