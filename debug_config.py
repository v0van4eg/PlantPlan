from app import create_app

# Создаем приложение
app = create_app()

with app.app_context():
    print("Конфигурация приложения:")
    print(f"DATABASE_URL: {app.config.get('DATABASE_URL', 'Не установлен')}")
    print(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print(f"instance_path: {app.instance_path}")
    print(f"root_path: {app.root_path}")
    
    # Какой путь будет использоваться для базы данных
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        relative_path = db_uri.replace('sqlite:///', '')
        import os
        full_path = os.path.join(app.instance_path, relative_path)
        print(f"Полный путь к базе данных: {full_path}")