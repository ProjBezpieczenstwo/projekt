from flask import request
from services.user_services.teacher_service import TeacherService
from urls.blueprints import api
from urls.decorators import jwt_required, jwt_get_user

@api.route('/teacher/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_teacher_details(teacher_id):
    """
    Retrieve a teacher's profile and availability
    ---
    tags:
      - Teacher
    security:
      - JWT: []
    parameters:
      - name: teacher_id
        in: path
        type: integer
        required: true
        description: ID of the teacher
    responses:
      200:
        description: Teacher profile with available hours
        schema:
          type: object
          properties:
            teacher: { type: object }
        example:
          teacher:
            id: 3
            name: "Alice"
            email: "alice@example.com"
            subject_ids: [1,2]
            difficulty_level_ids: [2]
            hourly_rate: 45
            bio: "Physics enthusiast"
            available_hours:
              - id: 5;
                weekday_id: 2;
                available_from: 16;
                available_until: 18
      404:
        description: Teacher not found
    """
    return TeacherService.get_teacher_details(teacher_id)


@api.route('/teacher-list/<int:page>', methods=['GET'])
@jwt_required()
def get_teacher_list(page):
    """
    Paginated listing of teachers (filterable)
    ---
    tags:
      - Teacher
    security:
      - JWT: []
    parameters:
      - name: page
        in: path
        type: integer
        required: true
        description: Page index (0-based)
      - name: subject
        in: query
        type: string
        description: Filter by subject name
      - name: difficulty_id
        in: query
        type: integer
      - name: name
        in: query
        type: string
        description: Partial match on teacher name
    responses:
      200:
        description: Teacher list with total count
        schema:
          type: object
          properties:
            total: { type: integer }
            teacher_list: { type: array }
      404:
        description: Teachers not found
    """
    return TeacherService.get_teacher_list(page)


@api.route('/teacher-update', methods=['PUT'])
@jwt_required(role='teacher')
@jwt_get_user()
def update_teacher(user):
    """
    Update the authenticated teacher's details
    ---
    tags:
      - Teacher
    security:
      - JWT: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            subject_ids:
              type: array
              items: { type: integer }
            difficulty_ids:
              type: array
              items: { type: integer }
            hourly_rate: { type: integer }
          example:
            subject_ids: [1,3]
            difficulty_ids: [2]
            hourly_rate: 50
    responses:
      200:
        description: Teacher details updated
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "Teacher details updated"
      400:
        description: Invalid input
        schema:
          type: object
          properties:
            description: { type: string }
        examples:
          subj_not_numbers:
            value: { error: "Subject ids can only contain numbers" }
          diff_not_numbers:
            value: { error: "Difficulty levels ids can only contain numbers" }
          rate_not_int:
            value: { error: "Hourly rate can only be an integer" }
      404:
        description: Subject not found OR Difficulty level not found
    """
    data = request.get_json()
    return TeacherService.update_teacher(user, data)
