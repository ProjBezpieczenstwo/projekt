from flask import request

from services.user_services.teacher_service import TeacherService
from urls.blueprints import api
from urls.decorators import jwt_required, jwt_get_user


@api.route('/teacher/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_teacher_details(teacher_id):
    return TeacherService.get_teacher_details(teacher_id)


@api.route('/teacher-list/<int:page>', methods=['GET'])
@jwt_required()
def get_teacher_list(page):
    return TeacherService.get_teacher_list(page)


@api.route('/teacher-update', methods=['PUT'])
@jwt_required(role='teacher')
@jwt_get_user()
def update_teacher(user):
    data = request.get_json()
    return TeacherService.update_teacher(user, data)
