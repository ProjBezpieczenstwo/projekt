import logging
import re
import sys
import uuid

import requests
from flasgger import swag_from
from flask import Blueprint, jsonify, request, current_app
from models import db, Student, Teacher, Subject, DifficultyLevel, TempUser, Admin,AccessCode  # Importuj odpowiednie modele

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
auth = Blueprint('auth', __name__)


def is_valid_email(email: str) -> bool:
    # Regex for an email expression
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


# Registration Endpoint
@auth.route('/register', methods=['POST'])
@swag_from('../swagger_templates/register.yml')
def register():
    data = request.get_json()
    new_user = None

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')  # student or teacher
    logging.info("przed auth_key")
    auth_key = str(uuid.uuid4())
    logging.info("po")
    if not name or not email or not password or not role:
        return jsonify({"message": "Name, email, password, and role are required."}), 400

    if not is_valid_email(email):
        return jsonify({"message": "Invalid email format."}), 400

    if role not in ['student', 'teacher', 'admin']:
        return jsonify({"message": "Role must be either 'student' or 'teacher'."}), 400

    # Sprawdzenie czy e-mail już istnieje
    existing_user = (Student.query.filter_by(email=email).first()
                     or Teacher.query.filter_by(email=email).first()
                     or Admin.query.filter_by(email=email).first())
    if existing_user:
        return jsonify({"message": "Email already in use."}), 400

    existing_user = TempUser.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "Verify your email address."}), 400

    # Tworzenie użytkownika w zależności od roli
    try:
        if role == 'student':
            new_user = TempUser(name=name, email=email, role='student', auth_key=auth_key)
        elif role == 'teacher':
            subject_ids = data.get('subject_ids').strip("{}").split(',')
            difficulty_level_ids = data.get('difficulty_ids').strip("{}").split(',')
            hourly_rate = data.get('hourly_rate')
            teacher_code = data.get('teacher_code')
            codes = [str(n.code) for n in AccessCode.query.all()]
            if str(teacher_code) not in codes:
                return jsonify({'message': 'Invalid teacher code'}), 400
            if not all(Subject.query.filter_by(id=int(s)).first() for s in subject_ids):
                return jsonify({'message': 'Subject not found'}), 404
            if not all(DifficultyLevel.query.filter_by(id=int(s)).first() for s in difficulty_level_ids):
                return jsonify({'message': 'Difficulty level not found'}), 404
            new_user = TempUser(
                name=name,
                email=email,
                subject_ids=subject_ids,
                difficulty_level_ids=difficulty_level_ids,
                hourly_rate=int(hourly_rate),
                role='teacher',
                auth_key=auth_key
            )
            AccessCode.query.filter_by(code=teacher_code).delete()
        elif role == 'admin':
            secret = data.get('secret')
            if int(secret) != 123:
                return jsonify({'message': 'Hackerman do not try to access this'}), 400

            new_user = Admin(name=name, email=email, role='admin')

        if not new_user:
            return jsonify({"message": "Error occurred while creating new user."}), 500
        # Wysłanie e-maila aktywacyjnego
        if role != 'admin':
            email_service_url = current_app.config.get("EMAIL_SERVICE_URL", "http://email_service:5001") + "/send-email"
            email_payload = {"email_receiver": email, "auth_key": auth_key}
            logging.info("przed postem")
            response = requests.post(email_service_url, json=email_payload)
            logging.info("po poscie")
            logging.info(response.status_code)
            logging.info(response.json())
            logging.info(response)
            logging.info(response != 200)
            if response.status_code != 200:
                return jsonify({response.json()}), 500
        try:
            logging.info("po tescie response coda xD")
            new_user.set_password(password)
            logging.info("set password")
            db.session.add(new_user)
            logging.info("new user db")
            db.session.commit()
            logging.info("commit")
        except Exception as e:
            return jsonify({"XD": f"{e}"}), 500
        if role == 'admin':
            return jsonify({"message": "Account created"}), 200
        return jsonify({"message": "Verify your email now!"}), 200

    except Exception as e:
        return jsonify({"message": "Internal server error"}), 500


# Login Endpoint
@auth.route('/login', methods=['POST'])
@swag_from('../swagger_templates/login.yml')
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email, password are required."}), 400

    if not is_valid_email(email):
        return jsonify({"message": "Invalid email format."}), 400

    # Find the user by email in Student, Teacher, or Admin tables
    user = Student.query.filter_by(email=email).first()
    if not user:
        user = Teacher.query.filter_by(email=email).first()
    if not user:
        user = Admin.query.filter_by(email=email).first()

    if user and user.check_password(password):
        # Generate JWT token
        access_token = user.generate_jwt()
        return jsonify({
            "message": "Login successful.",
            "access_token": access_token,
            "role": user.role
        }), 200
    else:
        user = TempUser.query.filter_by(email=email).first()
        if not user:
            return jsonify({"message": "Invalid email or password."}), 401
        return jsonify({"message": "Verify your email."}), 401



@auth.route('/confirm/<auth_key>', methods=['GET'])
# @swag_from('../swagger_templates/login.yml')
def check_auth_key(auth_key):
    new_user = None
    if not auth_key:
        return jsonify({"message": "Bad link."}), 400
    temp_user = TempUser.query.filter_by(auth_key=auth_key).first()
    if not temp_user:
        return jsonify({"message": "Invalid link"}), 400
    if temp_user.role == 'student':
        new_user = Student(
            name=temp_user.name,
            email=temp_user.email,
            password_hash=temp_user.password_hash,
            role='student'
        )
    elif temp_user.role == 'teacher':
        new_user = Teacher(
            name=temp_user.name,
            password_hash=temp_user.password_hash,
            email=temp_user.email,
            subject_ids=temp_user.subject_ids,
            difficulty_level_ids=temp_user.difficulty_level_ids,
            hourly_rate=temp_user.hourly_rate,
            role='teacher'
        )
    if not new_user:
        return jsonify({"message": "Error occurred while creating new user."}), 500
    db.session.delete(temp_user)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"{temp_user.role.capitalize()} registered successfully."}), 201



#TEST REGISTER

@auth.route('/test/register', methods=['POST'])
@swag_from('../swagger_templates/register.yml')
def test_register():
    data = request.get_json()
    new_user = None

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')  # student or teacher
    logging.info("przed auth_key")
    if not name or not email or not password or not role:
        return jsonify({"message": "Name, email, password, and role are required."}), 400

    if not is_valid_email(email):
        return jsonify({"message": "Invalid email format."}), 400

    if role not in ['student', 'teacher', 'admin']:
        return jsonify({"message": "Role must be either 'student' or 'teacher'."}), 400

    # Sprawdzenie czy e-mail już istnieje
    existing_user = (Student.query.filter_by(email=email).first()
                     or Teacher.query.filter_by(email=email).first()
                     or Admin.query.filter_by(email=email).first())
    if existing_user:
        return jsonify({"message": "Email already in use."}), 400


    # Tworzenie użytkownika w zależności od roli
    try:
        if role == 'student':
            new_user = Student(name=name, email=email, role='student')
        elif role == 'teacher':
            subject_ids = data.get('subject_ids').strip("{}").split(',')
            difficulty_level_ids = data.get('difficulty_ids').strip("{}").split(',')
            hourly_rate = data.get('hourly_rate')
            teacher_code = data.get('teacher_code')
            codes = [str(n.code) for n in AccessCode.query.all()]
            if str(teacher_code) not in codes:
                return jsonify({'message': 'Invalid teacher code'}), 400
            if not all(Subject.query.filter_by(id=int(s)).first() for s in subject_ids):
                return jsonify({'message': 'Subject not found'}), 404
            if not all(DifficultyLevel.query.filter_by(id=int(s)).first() for s in difficulty_level_ids):
                return jsonify({'message': 'Difficulty level not found'}), 404
            new_user = Teacher(
                name=name,
                email=email,
                subject_ids=subject_ids,
                difficulty_level_ids=difficulty_level_ids,
                hourly_rate=int(hourly_rate),
                role='teacher'
            )
            AccessCode.query.filter_by(code=teacher_code).delete()
        elif role == 'admin':
            secret = data.get('secret')
            if int(secret) != 123:
                return jsonify({'message': 'Hackerman do not try to access this'}), 400

            new_user = Admin(name=name, email=email, role='admin')

        if not new_user:
            return jsonify({"message": "Error occurred while creating new user."}), 500
        # Wysłanie e-maila aktywacyjnego
        logging.info("po tescie response coda xD")
        new_user.set_password(password)
        logging.info("set password")
        db.session.add(new_user)
        logging.info("new user db")
        db.session.commit()
        logging.info("commit")
        return jsonify({"message": "Account created"}), 200

    except Exception as e:
        return jsonify({"message": "Internal server error"}), 500
