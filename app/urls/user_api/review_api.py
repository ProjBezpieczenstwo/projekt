from flask import request

from services.user_services.review_service import ReviewService
from ..blueprints import api
from ..decorators import jwt_required, jwt_get_user


@api.route('/teacher-reviews', methods=['GET'])
@jwt_required()
def get_reviews():
    return ReviewService.get_reviews()


@api.route('/teacher-reviews/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_reviews_by_id(teacher_id):
    return ReviewService.get_reviews_by_teacher_id(teacher_id)


@api.route('/add_review', methods=['POST'])
@jwt_required(role='student')
@jwt_get_user()
def add_review(user):
    data = request.get_json()
    return ReviewService.add_review(user, data)


@api.route('/teacher-reviews/<int:teacher_id>', methods=['DELETE'])
@jwt_required(role='student')
@jwt_get_user()
def delete_review(user, teacher_id):
    return ReviewService.delete_review(user, teacher_id)
