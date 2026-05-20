from flask import Flask
from .database import db
import os


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///usuarios.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["DEBUG"] = os.environ.get("DEBUG", "false").lower() == "true"

    db.init_app(app)

    from .routes import usuarios_bp
    app.register_blueprint(usuarios_bp)

    with app.app_context():
        db.create_all()

    return app
