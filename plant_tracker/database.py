from flask_sqlalchemy import SQLAlchemy

# Create a single db instance that can be imported by both app and models
db = SQLAlchemy()