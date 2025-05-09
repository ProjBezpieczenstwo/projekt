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
    SECRET_KEY = '6e48ff4302924803ba0df47c2e307c78'
