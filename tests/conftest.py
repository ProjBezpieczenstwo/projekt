import sys
import os
import pytest
from werkzeug.security import generate_password_hash

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app
from models import db, Student, Teacher
from populate_db import populate_subjects, populate_difficulty_levels



@pytest.fixture(scope='module')
def test_client():
    """Set up the Flask test client."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

@pytest.fixture
def setup_users(setup_subjects):
    """Set up mock users for testing."""
    with app.app_context():
        if not Student.query.filter_by(id=1).first():
            # Add a test student
            student = Student(
                id=1,
                name="Test Student",
                email="student@example.com",
                role="student",
                password_hash=generate_password_hash("password123"),
            )
            db.session.add(student)

        if not Teacher.query.filter_by(id=2).first():
            # Add a test teacher
            teacher = Teacher(
                id=2,
                name="Test Teacher",
                email="teacher@example.com",
                role="teacher",
                password_hash=generate_password_hash("password123"),
                subject_ids=[1],
                difficulty_level_ids=[1],
                hourly_rate=50,
            )
            db.session.add(teacher)
            db.session.commit()


@pytest.fixture
def login_student(test_client, setup_users):
    """Log in as a student and return a JWT token."""
    response = test_client.post('/auth/login', json={
        'email': 'student@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json
    return response.json['access_token']

@pytest.fixture
def login_teacher(test_client, setup_users):
    """Log in as a teacher and return a JWT token."""
    response = test_client.post('/auth/login', json={
        'email': 'teacher@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json
    return response.json['access_token']


@pytest.fixture
def setup_subjects():
    populate_subjects()
    populate_difficulty_levels()
