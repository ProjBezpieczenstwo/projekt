import os


class Config:
    DB_NAME = os.getenv('db_name')
    DB_USER = os.getenv('db_user')
    DB_PASSWORD = os.getenv('db_password')
    DB_URI = os.getenv('db_uri')
    EMAIL_SERVICE_URL = os.getenv("email_service_uri")
    ADMIN_SECRET = os.getenv("admin_secret")
    SSL_MODE = os.getenv("ssl_mode")
    if SSL_MODE == "require":
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_URI}/{DB_NAME}?sslmode={SSL_MODE}"
    else:
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_URI}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "9f1c2e4b8d7a6e3f9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e")
