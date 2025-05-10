from flask import request

from services.user_services.calendar_service import CalendarService
from ..blueprints import api
from ..decorators import jwt_required, jwt_get_user


@api.route('/calendar/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_calendar_for_teacher(teacher_id):
    return CalendarService.get_calendar_for_teacher(teacher_id)


@api.route('/calendar', methods=['POST', 'GET'])
@jwt_required(role='teacher')
@jwt_get_user()
def calendar_create(user):
    if request.method == 'GET':
        return CalendarService.calendar_create_get(user)
    else:
        data = request.get_json()
        return CalendarService.calendar_create_post(user, data)


@api.route('/calendar/pdf', methods=['GET'])
@jwt_required(role='teacher')
@jwt_get_user()
def get_calendar_pdf(user):
    return CalendarService.get_calendar_pdf(user)
