import random
import re

from flasgger import swag_from
import requests
from flask import Blueprint, jsonify, request
from models import db, Student, Teacher, Subject, DifficultyLevel, TempUser, Admin  # Importuj odpowiednie modele

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
    auth_key = random.randint(1111, 9999)

    if not name or not email or not password or not role:
        return jsonify({"message": "Name, email, password, and role are required."}), 400

    if not is_valid_email(email):
        return jsonify({"message": "Invalid email format."}), 400

    if role not in ['student', 'teacher', 'admin']:
        return jsonify({"message": "Role must be either 'student' or 'teacher'."}), 400

    # Check if the email already exists
    existing_user = (Student.query.filter_by(email=email).first()
                     or Teacher.query.filter_by(email=email).first()
                     or Admin.query.filter_by(email=email).first())
    if existing_user:
        return jsonify({"message": "Email already in use."}), 400

    # Create a new user based on the role
    if role == 'student':
        new_user = TempUser(
            name=name,
            email=email,
            role='student',
            auth_key=auth_key
        )
    elif role == 'teacher':

        subject_ids = data.get('subject_ids').replace("{", "").replace("}", "").split(',')
        difficulty_level_ids = data.get('difficulty_ids').replace("{", "").replace("}", "").split(',')
        hourly_rate = data.get('hourly_rate')
        try:
            if subject_ids:
                if not all(Subject.query.filter_by(id=int(s)).first() for s in subject_ids):
                    return jsonify({'message': 'Subject not found'}), 404
            else:
                return jsonify({"message": "Subjects are required."}), 400
        except ValueError:
            return jsonify({'message': 'Subject ids can only contain numbers'}), 400

        try:
            if difficulty_level_ids:
                if not all(DifficultyLevel.query.filter_by(id=int(s)).first() for s in difficulty_level_ids):
                    return jsonify({'message': 'Difficulty level not found'}), 404
            else:
                return jsonify({"message": "Difficulty levels are required."}), 400
        except ValueError:
            return jsonify({'message': 'Difficulty levels ids can only contain numbers'}), 400

        try:
            if hourly_rate:
                hourly_rate = int(hourly_rate)
            else:
                return jsonify({"message": "Hourly rate is required."}), 400
        except ValueError:
            return jsonify({'message': 'Hourly rate can only be an integer'}), 400

        new_user = TempUser(
            name=name,
            email=email,
            subject_ids=subject_ids,
            difficulty_level_ids=difficulty_level_ids,
            hourly_rate=hourly_rate,
            role='teacher',
            auth_key=auth_key
        )
    elif role == 'admin':
        secret = data.get('secret')
        if not secret:
            return jsonify({'message': 'Naaaaah'}), 400
        if secret != 123:
            return jsonify({'message': 'Hackerman do not try to access this'}), 400
        new_user = Admin(
            name=name,
            email=email,
            role='admin'
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Now you can do a magic'}), 201
    if not new_user:
        return jsonify({"message": "Error occurred while creating new user."}), 500

    new_user.set_password(password)

    # Save the new user to the database
    db.session.add(new_user)
    db.session.commit()
    email_service_url = "http://host.docker.internal:5001/send-email"
    email_payload = {
        "email_receiver": email,
        "auth_key": auth_key
    }
    response = requests.post(email_service_url, json=email_payload)
    if response.status_code == 200:
        return jsonify({"message": "Confirm your email."}), 201
    else:
        return jsonify({
            "error": f"Failed to send email: {response.json().get('error', 'Unknown error')}"
        }), 500


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

    # Find the user by email in both Student and Teacher tables

    user = Student.query.filter_by(email=email).first()
    if not user:
        user = Teacher.query.filter_by(email=email).first()

    if user and user.check_password(password):
        # Generate JWT token
        access_token = user.generate_jwt()
        return jsonify({
            "message": "Login successful.",
            "access_token": access_token,
            "role": user.role
        }), 200
    else:
        return jsonify({"message": "Invalid email or password."}), 401


@auth.route('/auth_key', methods=['POST'])
# @swag_from('../swagger_templates/login.yml')
def check_auth_key():
    data = request.get_json()
    email = data.get('email')
    auth_key = data.get('auth_key')
    new_user = None
    if not auth_key:
        return jsonify({"message": "You need to provide auth key."}), 400
    temp_user = TempUser.query.filter_by(email=email).first()
    if temp_user.authKey != auth_key:
        return jsonify({"message": "Wrong auth key."}), 400
    else:
        if temp_user.role == 'student':
            new_user = Student(
                name=temp_user.name,
                email=temp_user.email,
                password=temp_user.password,
                role='student'
            )
        elif temp_user.role == 'teacher':
            new_user = Teacher(
                name=temp_user.name,
                password=temp_user.password,
                email=temp_user.email,
                subject_ids=temp_user.subject_ids,
                difficulty_level_ids=temp_user.difficulty_level_ids,
                hourly_rate=temp_user.hourly_rate,
                role='teacher'
            )
        if not new_user:
            return jsonify({"message": "Error occurred while creating new user."}), 500
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": f"{temp_user.role.capitalize()} registered successfully."}), 201
