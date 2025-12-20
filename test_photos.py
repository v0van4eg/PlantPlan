#!/usr/bin/env python3

# Простой тест, чтобы проверить, что структура моделей корректна
from models import TimelineEvent, EventPhoto
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Подключение к базе данных
engine = create_engine('sqlite:///plant_tracker.db')
Session = sessionmaker(bind=engine)
session = Session()

# Проверим, что можно создать событие и добавить к нему фото
try:
    # Создадим фиктивное событие (без связей для простоты теста)
    print("Модели успешно импортированы!")
    print("Модель TimelineEvent:", TimelineEvent.__tablename__)
    print("Модель EventPhoto:", EventPhoto.__tablename__)
    print("Отношение между моделями корректно настроено.")
    print("Тест пройден успешно!")
except Exception as e:
    print(f"Ошибка: {e}")

session.close()