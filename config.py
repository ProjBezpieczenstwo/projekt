import os


class Config:
    DB_NAME = os.getenv('db_name')
    DB_USER = os.getenv('db_user')
    DB_PASSWORD = os.getenv('db_password')
    DB_URI = os.getenv('db_uri')
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_URI}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '6e48ff4302924803ba0df47c2e307c78'
    EMAIL_SERVICE_URL = os.getenv("email_service_uri")
    # JWT_SECRET_KEY = 'your-jwt-secret-key'
