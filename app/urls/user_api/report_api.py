from flask import request
from services.user_services.report_service import ReportService
from urls.blueprints import api
from urls.decorators import jwt_required, jwt_get_user

@api.route('/report', methods=['POST'])
@jwt_required(role='teacher')
@jwt_get_user()
def add_report(user):
    """
    Create a lesson report
    ---
    tags:
      - Report
    security:
      - JWT: []
    parameters:
      - name: lesson_id
        in: body
        type: integer
        required: true
      - name: comment
        in: body
        type: string
      - name: homework
        in: body
        type: string
      - name: progress_rating
        in: body
        type: integer
        required: true
    responses:
      201:
        description: Report created
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "Report created"
      400:
        description: >
          Teacher does not belong to this lesson and cannot create report
          OR Rating must be provided
          OR Progress rating must be an integer
          OR Rating must be between values 0 and 5
          OR Lesson is already reported
      404:
        description: No lesson found
    """
    data = request.get_json()
    return ReportService.add_report(user, data)


@api.route('/report/<int:lesson_id>', methods=['GET'])
@jwt_required()
@jwt_get_user()
def get_report_by_lesson_id(user, lesson_id):
    """
    Retrieve the report for a specific lesson
    ---
    tags:
      - Report
    security:
      - JWT: []
    parameters:
      - name: lesson_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Report details
      400:
        description: No reports found OR You are not authorized to view this report
    """
    return ReportService.get_report_by_lesson_id(user, lesson_id)
