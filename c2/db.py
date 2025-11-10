from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app: Flask) -> None:
    database_uri = "sqlite:///" + "/tmp/c2.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    db.init_app(app)

    with app.app_context():
        # Import all models to register them with SQLAlchemy
        from models import (
            Bot,
        )

        db.create_all()
