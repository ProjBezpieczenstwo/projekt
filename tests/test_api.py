import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from urls.api import update_lesson_status_helper

def test_get_subjects(test_client, login_student):
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.get('/api/subjects', headers=headers)
    assert response.status_code == 200
    assert 'subjects' in response.json


def test_get_teacher_list(test_client, login_student):
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.get('/api/teacher-list', headers=headers)
    assert response.status_code == 200
    assert 'teacher_list' in response.json


def test_get_teacher_list_fail(test_client):
    response = test_client.get('/api/teacher-list')
    assert response.status_code == 401
    assert response.json['msg'] == 'Missing Authorization Header'


def test_get_teacher_list_all(test_client, login_student):
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.get('/api/teacher-list', headers=headers)
    assert response.status_code == 200
    assert 'teacher_list' in response.json


def test_get_teacher_list_all_fail(test_client):
    response = test_client.get('/api/teacher-list')
    assert response.status_code == 401
    assert response.json['msg'] == 'Missing Authorization Header'


def test_get_reviews(test_client, login_teacher):
    headers = {'Authorization': f'Bearer {login_teacher}'}
    response = test_client.get('/api/teacher-reviews', headers=headers)
    assert response.status_code == 200
    assert 'reviews' in response.json


def test_get_reviews_fail(test_client):
    response = test_client.get('/api/teacher-reviews')
    assert response.status_code == 401
    assert response.json['msg'] == 'Missing Authorization Header'


def test_get_reviews_by_id(test_client, login_teacher):
    headers = {'Authorization': f'Bearer {login_teacher}'}
    response = test_client.get('/api/teacher-reviews/2', headers=headers)
    assert response.status_code == 200
    assert 'reviews' in response.json


def test_get_reviews_by_id_fail(test_client):
    response = test_client.get('/api/teacher-reviews/2')
    assert response.status_code == 401
    assert response.json['msg'] == 'Missing Authorization Header'


def test_add_calendar_success(test_client, login_teacher):
    """Test adding a calendar successfully."""
    headers = {'Authorization': f'Bearer {login_teacher}'}
    response = test_client.post('/api/calendar', headers=headers, json={
        'available_from': '08:00',
        'available_until': '16:00',
        'working_days': [1, 2, 3, 4, 5]  # Monday to Friday
    })
    assert response.status_code == 201
    assert response.json['message'] == 'Calendar created'


def test_add_calendar_missing_fields(test_client, login_teacher):
    """Test adding a calendar with missing fields."""
    headers = {'Authorization': f'Bearer {login_teacher}'}
    response = test_client.post('/api/calendar', headers=headers, json={
        'available_from': '08:00'
        # Missing 'available_until' and 'working_days'
    })
    assert response.status_code == 400
    assert response.json['message'] == 'Available dates or hours not provided'


def test_add_calendar_invalid_time_format(test_client, login_teacher):
    """Test adding a calendar with an invalid time format."""
    headers = {'Authorization': f'Bearer {login_teacher}'}
    response = test_client.post('/api/calendar', headers=headers, json={
        'available_from': '8 AM',  # Invalid format
        'available_until': '16:00',
        'working_days': [1, 2, 3, 4, 5]
    })
    assert response.status_code == 400
    assert response.json['message'] == 'Available hours are not in %H:%M format'


def test_add_calendar_invalid_working_days(test_client, login_teacher):
    """Test adding a calendar with invalid working days."""
    headers = {'Authorization': f'Bearer {login_teacher}'}
    response = test_client.post('/api/calendar', headers=headers, json={
        'available_from': '08:00',
        'available_until': '16:00',
        'working_days': [0, 8]  # Invalid days (should be 1-7)
    })
    assert response.status_code == 400
    assert response.json[
               'message'] == 'Wrong value of working days, expected integers between 1 (Monday) and 7 (Sunday)'


def test_add_calendar_unauthorized(test_client):
    """Test adding a calendar without authentication."""
    response = test_client.post('/api/calendar', json={
        'available_from': '08:00',
        'available_until': '16:00',
        'working_days': [1, 2, 3, 4, 5]
    })
    assert response.status_code == 401
    assert response.json['msg'] == 'Missing Authorization Header'


def test_add_calendar_user_not_teacher(test_client, login_student):
    """Test adding a calendar as a student (should fail)."""
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.post('/api/calendar', headers=headers, json={
        'available_from': '08:00',
        'available_until': '16:00',
        'working_days': [1, 2, 3, 4, 5]
    })
    assert response.status_code == 400
    assert response.json['message'] == 'User can not be a student'


def test_add_lesson(test_client, setup_users, login_student):
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.post('/api/lesson', headers=headers, json={
        'teacher_id': 2,
        'subject_id': 1,
        'difficulty_id': 1,
        'date': '15/01/2025 10:00'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'Lesson created'


def test_add_lesson_fail_authorization(test_client):
    response = test_client.post('/api/lesson', json={
        'teacher_id': 2,
        'subject_id': 1,
        'difficulty_id': 1,
        'date': '15/01/2025 10:00'
    })
    assert response.status_code == 401
    assert response.json['msg'] == 'Missing Authorization Header'


def test_add_lesson_fail(test_client, setup_users, login_student):
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.post('/api/lesson', headers=headers, json={
        'teacher_id': 2,
        'subject_id': 1,
        'difficulty_id': 1,
        'date': '15/01/2025 10:00'
    })
    assert response.status_code == 400
    assert response.json['message'] == 'Lesson with this teacher is already booked for this date'


def test_add_lesson_fail_teacher_id(test_client, setup_users, login_student):
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.post('/api/lesson', headers=headers, json={
        'teacher_id': 'a',
        'subject_id': 1,
        'difficulty_id': 1,
        'date': '15/01/2025 10:00'
    })
    assert response.status_code == 400
    assert response.json['message'] == 'Teacher id must be an integer'


def test_add_lesson_fail_teacher(test_client, setup_users, login_student):
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.post('/api/lesson', headers=headers, json={
        'teacher_id': 3,
        'subject_id': 1,
        'difficulty_id': 1,
        'date': '15/01/2025 10:00'
    })
    assert response.status_code == 404
    assert response.json['message'] == 'Teacher not found'


def test_add_lesson_fail_subject(test_client, setup_users, login_student):
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.post('/api/lesson', headers=headers, json={
        'teacher_id': 2,
        'subject_id': 12,
        'difficulty_id': 1,
        'date': '15/01/2025 10:00'
    })
    assert response.status_code == 400
    assert response.json['message'] == 'Teacher does not teach this subject'


def test_add_lesson_fail_difficulty(test_client, setup_users, login_student):
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.post('/api/lesson', headers=headers, json={
        'teacher_id': 2,
        'subject_id': 1,
        'difficulty_id': 4,
        'date': '15/01/2025 10:00'
    })
    assert response.status_code == 400
    assert response.json['message'] == 'Teacher does not teach on this difficulty level'


def test_add_review(test_client, login_student):
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.post('/api/teacher-reviews/2', headers=headers, json={
        'rating': 5,
        'comment': 'Great teacher!'
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Review created successfully.'


def test_add_review_fail(test_client, login_student):
    response = test_client.post('/api/teacher-reviews/2', json={
        'rating': 5,
        'comment': 'Great teacher!'
    })
    assert response.status_code == 401
    assert response.json['msg'] == 'Missing Authorization Header'


def test_delete_review(test_client, login_student):
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.delete('/api/teacher-reviews/2', headers=headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Review deleted successfuly'


def test_delete_review_fail(test_client, login_student):
    response = test_client.delete('/api/teacher-reviews/2')
    assert response.status_code == 401
    assert response.json['msg'] == 'Missing Authorization Header'


def test_get_lessons(test_client, login_student):
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.get('/api/lesson', headers=headers)
    assert response.status_code == 200
    assert 'lesson_list' in response.json


def test_get_lessons_fail(test_client):
    response = test_client.get('/api/lesson')
    assert response.status_code == 401
    assert response.json['msg'] == 'Missing Authorization Header'


def test_add_report(test_client, login_teacher):
    headers = {'Authorization': f'Bearer {login_teacher}'}
    response = test_client.post('/api/report', headers=headers, json={
        'lesson_id': 1,
        'progress_rating': 4,
        'comment': 'Good progress',
        'homework': 'Practice Chapter 3'
    })
    assert response.status_code == 400
    assert response.json['message'] == 'Report cannot be created before the end of the lesson'


def test_add_report_fail(test_client):
    response = test_client.post('/api/report', json={
        'lesson_id': 1,
        'progress_rating': 4,
        'comment': 'Good progress',
        'homework': 'Practice Chapter 3'
    })
    assert response.status_code == 401
    assert response.json['msg'] == 'Missing Authorization Header'


def test_get_report(test_client, login_teacher):
    headers = {'Authorization': f'Bearer {login_teacher}'}
    response = test_client.get('/api/report', headers=headers)
    assert response.status_code == 400
    assert response.json['message'] == 'No reports found'


def test_get_report_fail(test_client):
    response = test_client.get('/api/report')
    assert response.status_code == 401
    assert response.json['msg'] == 'Missing Authorization Header'


def test_add_invoice(test_client, login_student):
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.post('/api/invoice', headers=headers, json={
        'lesson_id': 1
    })
    assert response.status_code == 201
    assert response.json['message'] == 'Invoice created'


def test_update_teacher_success(test_client, login_teacher):
    """Test updating teacher details successfully."""
    headers = {'Authorization': f'Bearer {login_teacher}'}
    response = test_client.put('/api/teacher-update', headers=headers, json={
        'subject_ids': [1],
        'difficulty_ids': [1, 2],
        'hourly_rate': 75
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Teacher details updated'


def test_update_teacher_invalid_subject(test_client, login_teacher):
    """Test updating teacher details with an invalid subject ID."""
    headers = {'Authorization': f'Bearer {login_teacher}'}
    response = test_client.put('/api/teacher-update', headers=headers, json={
        'subject_ids': [999],  # Invalid subject ID
        'difficulty_ids': [1],
        'hourly_rate': 75
    })
    assert response.status_code == 404
    assert response.json['message'] == 'Subject not found'


def test_update_teacher_invalid_difficulty_level(test_client, login_teacher):
    """Test updating teacher details with an invalid difficulty level ID."""
    headers = {'Authorization': f'Bearer {login_teacher}'}
    response = test_client.put('/api/teacher-update', headers=headers, json={
        'subject_ids': [1],
        'difficulty_ids': [999],  # Invalid difficulty level ID
        'hourly_rate': 75
    })
    assert response.status_code == 404
    assert response.json['message'] == 'Difficulty level not found'


def test_update_teacher_invalid_hourly_rate(test_client, login_teacher):
    """Test updating teacher details with an invalid hourly rate."""
    headers = {'Authorization': f'Bearer {login_teacher}'}
    response = test_client.put('/api/teacher-update', headers=headers, json={
        'subject_ids': [1],
        'difficulty_ids': [1],
        'hourly_rate': "invalid_rate"  # Invalid hourly rate
    })
    assert response.status_code == 400
    assert response.json['message'] == 'Hourly rate can only be an integer'


def test_update_teacher_not_teacher_role(test_client, login_student):
    """Test updating teacher details as a student (should fail)."""
    headers = {'Authorization': f'Bearer {login_student}'}
    response = test_client.put('/api/teacher-update', headers=headers, json={
        'subject_ids': [1],
        'difficulty_ids': [1],
        'hourly_rate': 75
    })
    assert response.status_code == 400
    assert response.json['message'] == 'User can not be a student'


def test_update_teacher_no_authentication(test_client):
    """Test updating teacher details without authentication."""
    response = test_client.put('/api/teacher-update', json={
        'subject_ids': [1],
        'difficulty_ids': [1],
        'hourly_rate': 75
    })
    assert response.status_code == 401
    assert response.json['msg'] == 'Missing Authorization Header'


def test_update_lesson_status(test_client):
    response = test_client.post('/api/update-lesson-status')
    assert response.status_code == 200
    assert 'Updated' in response.json['message']


# def test_update_lesson_status_helper(test_client):
#     response_json, response_code = update_lesson_status_helper()
#     assert response_code == 200
#     assert 'Updated' in response_json.json['message']