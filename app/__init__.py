from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

db = SQLAlchemy()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="memory://"
)

def create_app():
    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static")
    )

    app.config.from_object("config.Config")

    db.init_app(app)
    limiter.init_app(app)

    with app.app_context():
        from app.models import User
        db.create_all()

    from app.routes import main
    app.register_blueprint(main)

    return app