import os


class Config:
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_URI = os.getenv('DB_URI')
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_URI}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '6e48ff4302924803ba0df47c2e307c78'
    EMAIL_SERVICE_URL = os.getenv("EMAIL_SERVICE_URL")
    # JWT_SECRET_KEY = 'your-jwt-secret-key'
