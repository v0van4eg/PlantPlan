#!/usr/bin/env python3

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import User, Location, Plant, GrowthPhase, TimelineEvent, EventPhoto

def update_database():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plant_tracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Инициализация базы данных
    db = SQLAlchemy()
    db.init_app(app)
    
    with app.app_context():
        # Создание всех таблиц
        db.create_all()
        print("Database updated successfully with new tables!")

if __name__ == "__main__":
    update_database()