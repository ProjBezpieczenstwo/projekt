from datetime import datetime

import requests
from flask import jsonify

from models import Lesson, Calendar, db, WeekDay, TempUser
from ..blueprints import api


@api.route('/update-lesson-status', methods=['POST'])
def update_lesson_status():
    current_time = datetime.utcnow()
    lessons_to_update = Lesson.query.filter(
        Lesson.date < current_time,
        Lesson.status == 'scheduled'
    ).all()

    for lesson in lessons_to_update:
        lesson.status = 'completed'

    db.session.commit()
    return jsonify({'message': f'Updated {len(lessons_to_update)} lessons'}), 200


@api.route('/delete-expired-temp-users', methods=['GET'])
def delete_expired_temp_users():
    expiration_time = datetime.utcnow()
    db.session.query(TempUser).filter(TempUser.expired_at < expiration_time).delete()


@api.route('/weekdays/all', methods=['GET'])
def weekdays_all():
    weekdays = WeekDay.query.all()
    weekdays_list = [weekday.to_dict() for weekday in weekdays]
    return jsonify(weekdays=weekdays_list), 200


def clear_calendar(teacher_id):
    db.session.query(Calendar).filter(Calendar.teacher_id == teacher_id).delete()
    db.session.commit()


def update_lesson_status_helper():
    response = requests.post("http://localhost:5000/api/update-lesson-status")
    return response.json(), response.status_code


def delete_expired_temp_users_helper():
    response = requests.get("http://localhost:5000/api/delete-expired")
    return response.json(), response.status_code
