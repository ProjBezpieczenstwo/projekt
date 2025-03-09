from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import Teacher, Student, Review, Lesson, LessonReport, Calendar, Subject, \
    DifficultyLevel


def get_object_or_404(model, object_id, type=int):
    check_data(model,object_id)
    id = parse_data(object_id, type)
    obj = model.query.filter_by(id=id).first()
    if obj is None:
        return jsonify({'error': f'{model.__name__} not found'}), 404
    return obj


def parse_data(data, type):
    try:
        parsed = type(data)
    except ValueError:
        return jsonify({'message': f'{data} must be an {type.__name__}'}), 400
    return parsed


def check_data(model, data):
    if not data:
        return jsonify({'message': f'{model.__name__} id is not provided'}), 400


def get_user_by_jwt():
    user_id = get_jwt_identity()
    return Teacher.query.filter_by(id=user_id).first() or Student.query.filter_by(id=user_id).first()


def jwt_required(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_user_by_jwt()
            if not user:
                return jsonify({'message': 'User not found'}), 401
            if role and getattr(user, 'role', None) != role:
                return jsonify({'message': f'User must be a {role}'}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator

def jwt_get_user():
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(get_user_by_jwt(), *args, **kwargs)
        return wrapper
    return decorator
