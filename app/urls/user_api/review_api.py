from flask import request
from services.user_services.review_service import ReviewService
from urls.blueprints import api
from urls.decorators import jwt_required, jwt_get_user

@api.route('/teacher-reviews', methods=['GET'])
@jwt_required()
def get_reviews():
    """
    List all teacher reviews
    ---
    tags:
      - Review
    security:
      - JWT: []
    responses:
      200:
        description: Array of review objects
    """
    return ReviewService.get_reviews()


@api.route('/teacher-reviews/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_reviews_by_id(teacher_id):
    """
    Get all reviews for a specific teacher
    ---
    tags:
      - Review
    security:
      - JWT: []
    parameters:
      - name: teacher_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Array of reviews
      404:
        description: Teacher not found
    """
    return ReviewService.get_reviews_by_teacher_id(teacher_id)


@api.route('/add_review', methods=['POST'])
@jwt_required(role='student')
@jwt_get_user()
def add_review(user):
    """
    Submit a review for a teacher
    ---
    tags:
      - Review
    security:
      - JWT: []
    parameters:
      - name: lesson_id
        in: body
        type: integer
        required: true
      - name: rating
        in: body
        type: integer
        required: true
      - name: comment
        in: body
        type: string
    responses:
      200:
        description: Review created successfully
      400:
        description: Rating must be provided OR Rating must be between values 0 and 5
      404:
        description: Lesson not found
    """
    data = request.get_json()
    return ReviewService.add_review(user, data)


@api.route('/teacher-reviews/<int:teacher_id>', methods=['DELETE'])
@jwt_required(role='student')
@jwt_get_user()
def delete_review(user, teacher_id):
    """
    Delete the authenticated student's review for a teacher
    ---
    tags:
      - Review
    security:
      - JWT: []
    parameters:
      - name: teacher_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Review deleted successfully
      400:
        description: Review does not exist
    """
    return ReviewService.delete_review(user, teacher_id)
