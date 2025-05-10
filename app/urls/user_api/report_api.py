from flask import request

from services.user_services.report_service import ReportService
from urls.blueprints import api
from urls.decorators import jwt_required, jwt_get_user


@api.route('/report', methods=['POST'])
@jwt_required(role='teacher')
@jwt_get_user()
def add_report(user):
    data = request.get_json()
    return ReportService.add_report(user, data)


@api.route('/report/<int:lesson_id>', methods=['GET'])
@jwt_required()
@jwt_get_user()
def get_report_by_lesson_id(user, lesson_id):
    return ReportService.get_report_by_lesson_id(user, lesson_id)
