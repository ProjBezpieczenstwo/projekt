from flask import request

from services.user_services.lesson_service import LessonService
from urls.blueprints import api
from urls.decorators import jwt_required, jwt_get_user


@api.route('/lesson', methods=['POST'])
@jwt_required(role='student')
@jwt_get_user()
def add_lesson(user):
    data = request.get_json()
    return LessonService.add_lesson(user, data)


@api.route('/lesson', methods=['GET'])
@jwt_required()
@jwt_get_user()
def get_lesson(user):
    status = request.args.get('status')
    return LessonService.get_lesson(user, status)


@api.route('/lesson/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_lesson_by_teacher_id(teacher_id):
    return LessonService.get_lesson_by_teacher_id(teacher_id)


@api.route('/lesson/<int:lesson_id>', methods=['PUT'])
@jwt_required()
@jwt_get_user()
def change_lesson_status(user, lesson_id):
    data = request.get_json()
    return LessonService.change_lesson_status(user, lesson_id, data)
