def test_register_student(test_client):
    response = test_client.post('/auth/register', json={
        'name': 'Test Student',
        'email': 'student@example.com',
        'password': 'password123',
        'role': 'student'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'Student registered successfully.'


def test_register_teacher(test_client, setup_subjects):
    response = test_client.post('/auth/register', json={
        'name': 'Test Teacher',
        'email': 'teacher@example.com',
        'password': 'password123',
        'role': 'teacher',
        'subject_ids': [1, 2],
        'difficulty_ids': [1],
        'hourly_rate': 50
    })
    assert response.status_code == 201
    assert response.json['message'] == 'Teacher registered successfully.'


def test_login(test_client):
    # Assuming the previous registration tests were successful
    response = test_client.post('/auth/login', json={
        'email': 'student@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json


def test_register_duplicate_email(test_client, setup_users):
    response = test_client.post('/auth/register', json={
        'name': 'Duplicate User',
        'email': 'student@example.com',  # Already exists
        'password': 'password123',
        'role': 'student'
    })
    assert response.status_code == 400
    assert response.json['message'] == 'Email already in use.'


def test_login_invalid_credentials(test_client):
    response = test_client.post('/auth/login', json={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid email or password.'


