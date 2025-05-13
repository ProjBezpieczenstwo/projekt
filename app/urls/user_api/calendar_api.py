from flask import request
from services.user_services.calendar_service import CalendarService
from urls.blueprints import api
from urls.decorators import jwt_required, jwt_get_user

@api.route('/calendar/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_calendar_for_teacher(teacher_id):
    """
    Get a teacher's calendar availability
    ---
    tags:
      - Calendar
    security:
      - JWT: []
    parameters:
      - name: teacher_id
        in: path
        type: integer
        required: true
        description: Teacher ID
    responses:
      200:
        description: Calendar entries
        schema:
          type: object
          properties:
            calendar: { type: array }
      400:
        description: No calendar found.
    """
    return CalendarService.get_calendar_for_teacher(teacher_id)


@api.route('/calendar', methods=['GET', 'POST'])
@jwt_required(role='teacher')
@jwt_get_user()
def calendar_create(user):
    """
    GET: list calendar entries
    POST: update calendar availability
    ---
    tags:
      - Calendar
    security:
      - JWT: []
    parameters:
      - name: days
        in: body
        required: false
        schema:
          type: array
          items:
            type: object
            properties:
              day: { type: integer }
              available_from: { type: integer }
              available_until: { type: integer }
          example:
            - day: 2;
              available_from: 16;
              available_until: 18
    responses:
      200:
        description: GET successful
      201:
        description: Calendar updated
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "Calendar updated"
      400:
        description: Start time must be before end time for day X OR Invalid time format for day X
      404:
        description: Calendar not found.
    """
    if request.method == 'GET':
        return CalendarService.calendar_create_get(user)
    data = request.get_json()
    return CalendarService.calendar_create_post(user, data)


@api.route('/calendar/pdf', methods=['GET'])
@jwt_required(role='teacher')
@jwt_get_user()
def get_calendar_pdf(user):
    """
    Download the teacher's calendar as a PDF
    ---
    tags:
      - Calendar
    security:
      - JWT: []
    responses:
      200:
        description: PDF file stream
    """
    return CalendarService.get_calendar_pdf(user)
