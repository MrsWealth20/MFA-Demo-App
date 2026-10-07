import os


class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-this"
    )

    # Use PostgreSQL in production (Render)
    # and SQLite locally for development.
    database_url = os.environ.get(
        "DATABASE_URL",
        "sqlite:///secureauth.db"
    )

    # Render may provide a postgres:// URL.
    # SQLAlchemy expects postgresql://.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    SQLALCHEMY_DATABASE_URI = database_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Local development uses HTTP.
    # Render will use HTTPS.
    SESSION_COOKIE_SECURE = (
        os.environ.get(
            "SESSION_COOKIE_SECURE",
            "False"
        ).lower() == "true"
    )

    # Session lifetime
    PERMANENT_SESSION_LIFETIME = 1800