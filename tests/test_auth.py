import os
import sys
from models import db, TempUser

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_register_student(test_client):
    response = test_client.post('/auth/register', json={
        'name': 'Test Student',
        'email': 'student@gmail.com',
        'password': 'password123',
        'role': 'student'
    })
    assert response.json['message'] == 'Verify your email now!'
    assert response.status_code == 200


def test_register_teacher(test_client, setup_subjects):
    response = test_client.post('/auth/register', json={
        'name': 'Test Teacher',
        'email': 'korepetycjewzimowskie@gmail.com',
        'password': 'password123',
        'role': 'teacher',
        'subject_ids': '{1, 2}',
        'difficulty_ids': '{1}',
        'hourly_rate': 50,
        'teacher_code': 2137
    })
    assert response.json['message'] == 'Verify your email now!'
    assert response.status_code == 200

def test_login(test_client):
    temp_user = TempUser.query.filter_by(email='student@gmail.com').first()
    assert temp_user is not None, "TempUser not found; did registration fail?"
    confirm_resp = test_client.get(f'/auth/confirm/{temp_user.auth_key}')
    assert confirm_resp.status_code == 201
    assert 'registered successfully.' in confirm_resp.json['message']
    # Assuming the previous registration tests were successful
    response = test_client.post('/auth/login', json={
        'email': 'student@gmail.com',
        'password': 'password123'
    })
    assert 'access_token' in response.json
    assert response.status_code == 200

def test_register_duplicate_email(test_client, setup_users):
    response = test_client.post('/auth/register', json={
        'name': 'Duplicate User',
        'email': 'student@gmail.com',  # Already exists
        'password': 'password123',
        'role': 'student'
    })
    assert response.json['message'] == 'Email already in use.'
    assert response.status_code == 400


def test_login_invalid_credentials(test_client):
    response = test_client.post('/auth/login', json={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    })
    assert response.json['message'] == 'Invalid email or password.'
    assert response.status_code == 401


