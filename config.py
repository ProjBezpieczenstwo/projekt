import os


class Config:
    DB_NAME = os.getenv('db-name')
    DB_USER = os.getenv('db-user')
    DB_PASSWORD = os.getenv('db-password')
    DB_URI = os.getenv('db-uri')
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_URI}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '6e48ff4302924803ba0df47c2e307c78'
    EMAIL_SERVICE_URL = os.getenv("email-service-uri")
    # JWT_SECRET_KEY = 'your-jwt-secret-key'
