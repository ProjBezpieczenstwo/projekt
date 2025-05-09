from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flasgger import Swagger
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

from config import Config
from models import db
from urls.admin import admin
from urls.api import api, update_lesson_status_helper, delete_expired_temp_users_helper
from urls.auth import auth

app = Flask(__name__)
CORS(app)

try:
    # Load app config
    app.config.from_object(Config)

    # Initialize the app
    db.init_app(app)

    # Try creating tables and start scheduler
    with app.app_context():
        db.create_all()
        back_scheduler = BackgroundScheduler()
        back_scheduler.add_job(func=update_lesson_status_helper, trigger="interval", minutes=30)
        back_scheduler.add_job(func=delete_expired_temp_users_helper, trigger="interval", minutes=30)
        back_scheduler.start()

        from models import WeekDay, DifficultyLevel, Subject

        if WeekDay.query.count() == 0:
            weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for name in weekday_names:
                new_weekday = WeekDay(name=name)
                db.session.add(new_weekday)
            db.session.commit()
            print("Weekdays have been added to the database.")

        if DifficultyLevel.query.count() == 0:
            difficulty_levels = [
                DifficultyLevel(id=1, name="Primary School"),
                DifficultyLevel(id=2, name="Lower Secondary School"),
                DifficultyLevel(id=3, name="Higher Secondary School"),
                DifficultyLevel(id=4, name="Bachelor's"),
                DifficultyLevel(id=5, name="Master's"),
            ]
            db.session.add_all(difficulty_levels)
            db.session.commit()
            print(f"Dodano poziomy nauczania do bazy danych.")

        if Subject.query.count() == 0:
            subjects = [
                Subject(id=1, name="Maths"),
                Subject(id=2, name="Physics"),
                Subject(id=3, name="Biology"),
                Subject(id=4, name="Chemistry"),
                Subject(id=5, name="Geography"),
                Subject(id=6, name="Science"),
                Subject(id=7, name="IT"),
                Subject(id=8, name="English"),
                Subject(id=9, name="Polish"),
                Subject(id=10, name="Spanish"),
                Subject(id=11, name="French"),
                Subject(id=12, name="German"),
                Subject(id=13, name="Italian"),
            ]
            db.session.add_all(subjects)
            db.session.commit()
            print(f"Dodano przedmioty do bazy danych.")

except OperationalError as e:
    print("Database connection failed. Please ensure the database is running and accessible.")
    print(f"Error: {e}")
    exit(1)
except Exception as e:
    print("An unexpected error occurred during app initialization.")
    print(f"Error: {e}")
    exit(1)

jwt = JWTManager(app)

swagger = Swagger(app, template={
    "info": {
        "title": "Korepetycje App API",
        "description": "API created for the Korepetycje App. Made by WZIM students",
        "version": "1.0.0"
    }
})

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(admin, url_prefix="/admin")


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"message": "Page not found"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
