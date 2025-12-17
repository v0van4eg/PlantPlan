from app import app, db

def add_photo_data_column():
    with app.app_context():
        # Выполняем SQL-запрос для добавления столбца
        db.session.execute(db.text("ALTER TABLE locations ADD COLUMN photo_data BYTEA;"))
        db.session.commit()
        print("Столбец photo_data успешно добавлен в таблицу locations")

if __name__ == "__main__":
    add_photo_data_column()