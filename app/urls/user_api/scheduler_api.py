from datetime import datetime
import requests
from flask import jsonify

from models import Lesson, Calendar, db, WeekDay, TempUser
from urls.blueprints import api

@api.route('/update-lesson-status', methods=['POST'])
def update_lesson_status():
    """
    Update the status of past lessons to 'completed'
    ---
    tags:
      - Scheduler
    responses:
      200:
        description: Number of lessons updated
        schema:
          type: object
          properties:
            message:
              type: string
          example:
            message: "Updated 5 lessons"
    """
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
    """
    Delete all expired temporary users
    ---
    tags:
      - Scheduler
    responses:
      200:
        description: Expired temp users deleted
        schema:
          type: object
          properties:
            message:
              type: string
          example:
            message: "Deleted 3 expired temp users"
    """
    expiration_time = datetime.utcnow()
    count = db.session.query(TempUser).filter(TempUser.expired_at < expiration_time).delete()
    db.session.commit()
    return jsonify({'message': f'Deleted {count} expired temp users'}), 200



@api.route('/weekdays/all', methods=['GET'])
def weekdays_all():
    """
    List all weekday definitions
    ---
    tags:
      - Scheduler
    responses:
      200:
        description: Array of weekdays
        schema:
          type: object
          properties:
            weekdays:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                example:
                  id: 1
                  name: "Monday"
    """
    weekdays = WeekDay.query.all()
    weekdays_list = [weekday.to_dict() for weekday in weekdays]
    return jsonify(weekdays=weekdays_list), 200


def update_lesson_status_helper():
    response = requests.post("http://localhost:5000/api/update-lesson-status")
    return response.json(), response.status_code


def delete_expired_temp_users_helper():
    response = requests.get("http://localhost:5000/api/delete-expired")
    return response.json(), response.status_code
