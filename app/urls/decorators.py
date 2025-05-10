from functools import wraps

from flask_jwt_extended import verify_jwt_in_request

from helper import get_user_by_jwt


def _get_authenticated_user():
    verify_jwt_in_request()
    user = get_user_by_jwt()
    if not user:
        return None, jsonify({'message': 'User not found'}), 401
    return user, None, None


def jwt_required(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user, error_response, status = _get_authenticated_user()
            if error_response:
                return error_response, status
            if role and getattr(user, 'role', None) != role:
                return jsonify({'message': f'User must be a {role}'}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def jwt_get_user():
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user, error_response, status = _get_authenticated_user()
            if error_response:
                return error_response, status
            return fn(user, *args, **kwargs)

        return wrapper

    return decorator
