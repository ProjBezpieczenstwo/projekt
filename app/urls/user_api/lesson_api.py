from flask import request
from services.user_services.lesson_service import LessonService
from urls.blueprints import api
from urls.decorators import jwt_required, jwt_get_user

@api.route('/lesson', methods=['POST'])
@jwt_required(role='student')
@jwt_get_user()
def add_lesson(user):
    """
    Create a new lesson booking
    ---
    tags:
      - Lesson
    security:
      - JWT: []
    parameters:
      - name: teacher_id
        in: body
        type: integer
        required: true
      - name: subject
        in: body
        type: string
      - name: difficulty
        in: body
        type: string
      - name: date
        in: body
        type: string
        description: "Format: dd/MM/YYYY HH:mm"
    responses:
      201:
        description: Lesson created
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "Lesson created"
      400:
        description: >
          Date must be provided
          OR Date must be in format %d/%m/%Y %H:%M
          OR User has already booked lesson for this date
      404:
        description: Subject not found OR Difficulty not found OR Teacher not found
    """
    data = request.get_json()
    return LessonService.add_lesson(user, data)


@api.route('/lesson', methods=['GET'])
@jwt_required()
@jwt_get_user()
def get_lesson(user):
    """
    Retrieve lessons for the authenticated user, optionally filtered by status
    ---
    tags:
      - Lesson
    security:
      - JWT: []
    parameters:
      - name: status
        in: query
        type: string
        description: "scheduled or completed"
    responses:
      200:
        description: Array of lessons
      400:
        description: Invalid status OR No lessons found
    """
    status = request.args.get('status')
    return LessonService.get_lesson(user, status)


@api.route('/lesson/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_lesson_by_teacher_id(teacher_id):
    """
    List all lessons for a specific teacher
    ---
    tags:
      - Lesson
    security:
      - JWT: []
    parameters:
      - name: teacher_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Array of lesson objects
      404:
        description: Teacher not found
      400:
        description: No lessons found
    """
    return LessonService.get_lesson_by_teacher_id(teacher_id)


@api.route('/lesson/<int:lesson_id>', methods=['PUT'])
@jwt_required()
@jwt_get_user()
def change_lesson_status(user, lesson_id):
    """
    Cancel a lesson (must be >1h before start)
    ---
    tags:
      - Lesson
    security:
      - JWT: []
    parameters:
      - name: lesson_id
        in: path
        type: integer
        required: true
      - name: comment
        in: body
        type: string
        required: true
    responses:
      200:
        description: Lesson cancelled successfully
      400:
        description: No lesson found OR You can not update lesson less than 1 hour before start
    """
    data = request.get_json()
    return LessonService.change_lesson_status(user, lesson_id, data)
