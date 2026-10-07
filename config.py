import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-this"
    )

    SQLALCHEMY_DATABASE_URI = "sqlite:///secureauth.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False

    # Session lifetime
    PERMANENT_SESSION_LIFETIME = 1800